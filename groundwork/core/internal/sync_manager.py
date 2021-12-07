from typing import Any, DefaultDict, Dict, Optional, Type

import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from django.db import models, transaction
from django.utils import timezone

from groundwork.core.datasources import SyncedModel
from groundwork.core.internal.collection_util import compact_values


@dataclass
class ModelSyncState:
    resolved_instances: Dict[str, Any] = field(default_factory=dict)


class SyncManager:
    """
    Manages the synchronisation logic for pulling all instances of a remote datasource.

    Due to sometimes needing to recurse through referenced models, a synchronisation session is stateful.
    """

    models: DefaultDict[Type[SyncedModel], ModelSyncState]

    def __init__(self) -> None:
        self.models = defaultdict(ModelSyncState)
        self.sync_time = timezone.now()
        self.ignored_fields = {field.name for field in SyncedModel._meta.get_fields()}

    def sync_model(self, model: Type[SyncedModel]) -> None:
        """
        Pull the result of calling list() on a `SyncedModel`'s datasource into the local database.
        Recursively resolves relationships to other SyncedModels.

        Args:
            model: The model class to sync from its datasource.
        """

        logging.info("Beginning sync of %s…", model._meta.verbose_name)
        start_time = datetime.now()

        # First of all, figure out how to join the remote data to the local data
        model_join_key = model.sync_config.external_id
        resource_join_key = model.sync_config.datasource.identifer

        # Fetch all the models from remote
        resources = model.sync_config.datasource.list()
        model_state = self.models[model]

        # Iterate over the resources and write them into the database
        for resource in resources:

            # We don't want to lock up the database for ages, but also we need a transaction here to ensure that any
            # referenced foreign keys are resolved into the database with this instance.
            #
            # Compromise approach: transaction per instance (and its non-m2m dependencies)
            with transaction.atomic():
                resource_id = getattr(resource, resource_join_key)
                join_query = {model_join_key: resource_id}

                try:
                    instance = model.objects.get(**join_query)

                except model.DoesNotExist:
                    instance = model(**join_query)

                model_state.resolved_instances[resource_id] = instance

                for key, val in self.prepare_resource_attrs_for_save(
                    model, resource
                ).items():
                    setattr(instance, key, val)

                instance.save()

            self.set_resource_m2m(model, resource, instance)

        duration = datetime.now() - start_time
        logging.info("Completed sync of %s in %s", model._meta.verbose_name, duration)

    def resove_embedded_value(self, model: Type[SyncedModel], resource: Any) -> Any:
        """
        Given a resorce object, get or create a model representation for it and return it, updating from the resource
        if needed.

        Args:
            model: The model class to resolve into.
            resource: The resource instance to convert to a model.

        Returns:
            Local model representation of the resource, saved in the database.
        """

        identifier_key = model.sync_config.datasource.identifer
        identifier = getattr(resource, identifier_key)

        model_state = self.models[model]
        model_query = {model.sync_config.external_id: identifier}

        try:
            instance = model.objects.get(**model_query)
        except model.DoesNotExist:
            instance = model()

        model_state.resolved_instances[identifier] = instance

        attrs = self.prepare_resource_attrs_for_save(model, resource)
        for key, val in attrs.items():
            setattr(instance, key, val)

        instance.save()
        return instance

    def resolve_by_external_id(self, model: Type[SyncedModel], id: Any) -> Any:
        """
        Given the external id for an instance of a model class, either:

        - If the instance has already been synced, return it.
        - If the instance has not yet been synced, fetch it from the datasource, save a local copy and return
        that.

        Args:
            model: The model class to resolve into. This model's sync config will be used to fetch the resource if needed.
            id: Identifier used to fetch the resource fron the datasource.

        Returns:
            The local model representation of the resource identified by `id`.
        """

        # Get the current state for the model type in this sync session
        sync_state = self.models[model]

        # If the model has already been referenced elsewhere, return the cached instance we have in memory already.
        if id in sync_state.resolved_instances:
            return sync_state.resolved_instances[id]

        external_id_field = model.sync_config.external_id
        try:
            # If a local copy already exists, add it to the in-memory cache and return it
            instance = model.objects.get(**{external_id_field: id})
            sync_state.resolved_instances[id] = instance

            return instance

        except model.DoesNotExist:
            # If a copy doesn't exist, resolve it from the dtasource. We only resolve enough of its properties
            # to save it in the database – we don't recurse into m2m relationships yet – save that for when this model
            # gets its own top-level sync.

            # Create the model here. Store it in our cache _before_ resolving its attributes in case there are cyclic
            # relationships.

            # Note that this means that this method must be called within a transaction or else saving may throw.
            instance = model()
            sync_state.resolved_instances[id] = instance

            # Fetch the remote referenced data and assign to the model.
            resource = model.sync_config.datasource.get(id)
            for key, val in self.prepare_resource_attrs_for_save(
                model, resource
            ).items():
                setattr(instance, key, val)

            instance.save()

            return instance

    def prepare_resource_attrs_for_save(
        self, model: Type[SyncedModel], resource: Any
    ) -> Dict[str, Any]:
        """
        Given an object returned by the datasource, prepare it for saving to the database.

        The default implementation:
        - Strips from each resource any fields not present in the model.
        - Prepares each attribute by calling `prepare_field_for_save`.
        - Updates the `last_sync_time` attribute with the current date & time.

        Args:
            model: The model class detailing how the attributes of `resource` are to be treated.
            resource: A resource returned by the datasource.

        Returns:
            A dictionary of properties suitable for assigning to an instance of `model`.
        """

        identifier = model.sync_config.datasource.identifer
        properties = dict(
            compact_values(
                (field.name, self.prepare_attr_field_for_save(model, field, resource))
                for field in model._meta.get_fields()
                if field.name not in self.ignored_fields
            )
        )

        properties["last_sync_time"] = self.sync_time
        properties[model.sync_config.external_id] = getattr(resource, identifier)
        return properties

    def set_resource_m2m(
        self, model: Type[SyncedModel], resource: Any, instance: Any
    ) -> None:
        """
        Given an object returned by the datasource and the local model representing it, apply the m2m
        relationships in the resource.

        Args:
            model: The model class detailing how the attributes of `resource` are to be treated.
            resource: A resource returned by the datasource.
            instance: The local model instance to update the m2m relationships of.
        """

        resolved_m2m_values = compact_values(
            (field.name, self.prepare_m2m_field_for_save(model, field, resource))
            for field in model._meta.get_fields()
        )

        for key, values in resolved_m2m_values:
            related_manager = getattr(instance, key)
            related_manager.set(values)

    def prepare_attr_field_for_save(
        self, model: Type[SyncedModel], field: models.Field, resource: Any
    ) -> Optional[Any]:
        """
        Given a value returned by the datasource, convert it into a value suitable for saving locally into the
        field represented by `field`.

        The default implementation returns the value as-is unless the field is a foreign key, in which case the
        value is assumed to be an external identifier and the referenced local instance is returned, fetching it from
        the datasource and saving if needed.

        Many-to-many relationships are ignored and handled separately as then can't be applied to a model before it is
        saved.

        Args:
            model: The model class detailing how the attributes of `resource` are to be treated.
            field: The field descriptor that we wish to update the value of.
            resource: A resource returned by the datasource.

        Returns:
            A value suitable for saving in the slot identified by `field`. Or `None` if no value is suitable.
        """

        resolved_key = self.fetch_urlsource_field_key(model, field.name)
        if resolved_key is None:
            return None

        value = getattr(resource, resolved_key, None)
        if value is None:
            return None

        if field.is_relation and issubclass(field.related_model, SyncedModel):
            if field.many_to_many:
                return None

            if self.is_identifier(value):
                return self.resolve_by_external_id(field.related_model, value)

            return self.resove_embedded_value(field.related_model, value)

        return value

    def prepare_m2m_field_for_save(
        self, model: Type[SyncedModel], field: models.Field, resource: Any
    ) -> Any:
        """
        Given a list of external ids returned by the remote datasource, resolve the external ids into the local model
        (fetching from remote if needed) and return the new list of related values.

        Args:
            model: The model class detailing how the attributes of `resource` are to be treated.
            field: The field descriptor that we wish to update the value of.
            resource: A resource returned by the datasource.

        Returns:
            A list of model instances suitable for assigning to the m2m relationship, or `None` if this is not an m2m
            relationship that we need to update.
        """

        # If these aren't referencing another SyncedModel then we have no idea how to map these onto an external id,
        # so skip.
        if not field.many_to_many or not issubclass(field.related_model, SyncedModel):
            return None

        resolved_key = self.fetch_urlsource_field_key(model, field.name)
        if resolved_key is None:
            return None

        values = getattr(resource, resolved_key, None)
        if values is None:
            return []

        return [
            self.resolve_by_external_id(field.related_model, ref)
            if self.is_identifier(ref)
            else self.resove_embedded_value(field.related_model, ref)
            for ref in values
        ]

    def fetch_urlsource_field_key(
        cls, model: Type[SyncedModel], model_key: str
    ) -> Optional[str]:
        """
        Return the datasource key for a given model key.

        Args:
            model: The model class that the field is being mapped to.
            model_key: The field that we wish to update the value of.

        Returns:
            The key to look up on the resource to assign to the model.
        """

        if model.sync_config.field_map is None:
            return model_key

        return model.sync_config.field_map.get(model_key)

    def is_identifier(self, value: Any) -> bool:
        return (
            isinstance(value, str)
            or isinstance(value, int)
            or isinstance(value, uuid.UUID)
        )

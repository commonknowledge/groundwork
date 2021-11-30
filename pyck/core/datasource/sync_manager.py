from typing import Any, DefaultDict, Dict, Set, Type

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from django.db import models, transaction

from pyck.core.datasource.models import SyncedModel
from pyck.core.internal.collection_util import compact_values


@dataclass
class ModelSyncState:
    resolved_instances: Dict[str, Any] = field(default_factory=dict)


class SyncManager:
    models: DefaultDict[Type[SyncedModel], ModelSyncState]

    def __init__(self) -> None:
        self.models = defaultdict(ModelSyncState)
        self.sync_time = datetime.now()

    def sync_model(self, model: Type[SyncedModel]) -> None:
        """
        Pull the result of calling list() on a `SyncedModel`'s datasource into the local database.
        Recursively resolves relationships to other SyncedModels.
        """

        # First of all, figure out how to join the remote data to the local data
        model_join_key = model.SyncConfig.external_id
        resource_join_key = model.get_datasource_field_key(model_join_key)

        # If the
        if resource_join_key is None:
            resource_join_key = model_join_key

        # Fetch all the models from remote
        resources = model.SyncConfig.datasource.list()
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

    def resolve_by_external_id(self, model: Type[SyncedModel], id: Any) -> Any:
        """
        Given the external id for an instance of a model class, either:

        - If the instance has already been synced, return it.
        - If the instance has not yet been synced, fetch it from the external resource, save a local copy and return
          that.
        """

        # Get the current state for the model type in this sync session
        sync_state = self.models[model]

        # If the model has already been referenced elsewhere, return the cached instance we have in memory already.
        if id in sync_state.resolved_instances:
            return sync_state.resolved_instances[id]

        external_id_field = model.SyncConfig.external_id
        try:
            # If a local copy already exists, add it to the in-memory cache and return it
            instance = model.objects.get(**{external_id_field: id})
            sync_state.resolved_instances[id] = instance

            return instance

        except model.DoesNotExist:
            # If a copy doesn't exist, resolve it from the remote resource. We only resolve enough of its properties
            # to save it in the database – we don't recurse into m2m relationships yet – save that for when this model
            # gets its own top-level sync.

            # Create the model here. Store it in our cache _before_ resolving its attributes in case there are cyclic
            # relationships.

            # Note that this means that this method must be called within a transaction or else saving may throw.
            instance = model()
            sync_state.resolved_instances[id] = instance

            # Fetch the remote referenced data and assign to the model.
            resource = model.SyncConfig.datasource.get(id)
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
        Given an object returned by the external resource, prepare it for saving to the database.

        The default implementation:
        - Strips from each resource item any fields not present in the model
        - Prepares each attribute by calling `prepare_field_for_save`
        - Updates the `last_sync_time` attribute with the current date & time

        Args:
            resource: An object returned by the remote resource.

        Returns:
            A dict of properties suitable for assigning to an instance of this model.
        """

        properties = dict(
            compact_values(
                (field.name, self.prepare_attr_field_for_save(model, field, resource))
                for field in model._meta.get_fields()
            )
        )

        properties["last_sync_time"] = self.sync_time
        return properties

    def set_resource_m2m(
        self, model: Type[SyncedModel], resource: Any, instance: Any
    ) -> None:
        """
        Given an object returned by the external resource and the local model representing it, apply the m2m
        relationships in the resource.

        Args:
            resource: An object returned by the remote resource.
            model: The local copy to update
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
    ) -> Any:
        """
        Given a value returned by the remote resource, convert it into a value suitable for saving locally into the
        field represented by `field`.

        The default implementation returns the value as-is unless the field is a foreign key, in which case the
        value is assumed to be an external identifier and the referenced local instance is returned, fetching it from
        the external resource and saving if needed.
        """

        resolved_key = model.get_datasource_field_key(field.name)
        if resolved_key is None:
            return None

        value = getattr(resource, resolved_key, None)

        if field.is_relation and issubclass(field.related_model, SyncedModel):
            if field.many_to_many:
                return None
            else:
                return self.resolve_by_external_id(field.related_model, value)

        return value

    def prepare_m2m_field_for_save(
        self, model: Type[SyncedModel], field: models.Field, resource: Any
    ) -> Any:
        """
        Given a list of external ids returned by the remote resource, resolve the external ids into the local model
        (fetching from remote if needed) and return the new list of related values
        """

        # If these aren't referencing another SyncedModel then we have no idea how to map these onto an external id,
        # so skip.
        if not field.many_to_many or not issubclass(field.related_model, SyncedModel):
            return None

        resolved_key = model.get_datasource_field_key(field.name)
        if resolved_key is None:
            return None

        values = getattr(resource, resolved_key, None)

        return [
            self.resolve_by_external_id(field.related_model, external_id)
            for external_id in values
        ]

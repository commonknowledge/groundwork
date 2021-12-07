Django ships out of the box with an excellent ORM for modeling data created and managed by our application. This is
useful for several reasons, but mainly:

- Consistent conventions mean less surprises about how different things work.
- The standardised model/queryset format allows the framework to support generic views, forms and other components.

Unfortunately, they don't help so much with external data - either public data that we want to be informed of changes to or data managed by external services.

This gets particuarly tricky when we want to augment the remote data with our own data or there are API limits that
require us to store the data locally and keep it up to date – we often end up writing lots of bug-prone glue code to
manage this.

Groundwork helps here by introducing a lightweight abstraction called a `Datasource`. It might be helpful to
think of these as similar to Django' models and querysets, but for external APIs.

## About datasources

A datasource is a simple interface that defines:

- A method to get objects by ID.
- A method to list (and optionally sort or filter) objects.
- A type that returned objects should be assumed to be instances of.
- A field on that type that provides the object's ID.

You can check out the documentation for the [Datasource](../../api/pyck.core.datasources/#externalresource) class
for more detail on this. For now, we'll look at one thing we can do with them – regularly synchronising data from a
remote service.

## Synchronising data from a remote service

For this example, we'll pull in a list of all the constituencies in the UK using Groundwork's built-in UK parliamentary
datasource. It's not the most interesting example, but works for explaining things.

We'll configure it to update periodically so that changes to UK constituencies are reflected in our local models.

!!! warning

    Just because you _can_ pull in lots of data in from other systems doesn't mean you _should_. Be mindful about any
    personal data that you're pulling in from CRMs, etc. Don't store more than you need, anonymise as necessary and
    ensure that your environment is secure relative to the sensitivity of the data you are storing and your threat
    model.

### Create your model

First, we'll create our model. To make this easier, we'll make the field names in our model match the field names in the datasource. The datasources provided with Groundwork are all documented and have type hints on the objects they return. The UK Parliament datasource is documented [here](../../api/pyck.geo.territories.uk.parliament/).

Some things to note:

- We're subclassing [SyncedModel](../../api/pyck.core.datasources/#syncedmodel). This is needed to register the model with the sync manager.
- We configure where to fetch the data from, how often, and how to map it onto our local model using [SyncConfig](../../api/pyck.core.datasources/#syncconfig).
- We need to store the id used by the remote data source. By default, this is called `external_id`, but you can customize this.
- We need to add the fields we want to save data from in our model. It's absolutely fine to leave out fields that you
  don't want to save.

```python title="app/models.py"
from django.db import models
from pyck.core.datasources import SyncedModel, SyncConfig
from pyck.geo.territories.uk import parliament

class Constituency(SyncedModel):
    # This is where we specify the datasource, along with other options
    # for customizing how synchronization happens.
    sync_config = SyncConfig(
      datasource=parliament.constituencies,
    )

    # This is used to join data returned from the remote API against
    # our local data.
    external_id = models.IntegerField()

    # This will be populated from the remote data.
    name = models.CharField(max_length=256)
```

### Configure a cron process

Groundwork comes with a management command for running background cron processes. Where you run it will depend on your
server setup, but you can launch it by running:

```bash
python manage.py run_cron_tasks
```

This will start a clock process which periodically checks for any pending cron tasks and runs them. It runs until you close it.

For relatively small projects running on a single instance, you might find it convenient to have a launch script that
runs the cron process in the background:

```bash title="run.sh"
python manage.py run_cron_tasks & gunicorn app.wsgi
```

Or on larger installations using an IAAS platform like Heroku, you might want to configure a dedicated box to run the
cron tasks:

```yaml title="Procfile"
web: gunicorn app.wsgi
clock: python manage.py run_cron_tasks
```

In development, you might want to just run all registered cron tasks then exit. You can do this with the `--once` flag.
We'll do that now:

```bash
python manage.py run_cron_tasks --once
```

That's it! You now have a list of UK constituencies saved to your database.

On its own, this isn't very interesting. To make this more useful, the next tutorial will look at relationships.

### Handling relationships

Often, we find ourselves wanting to preserve relationships between resources we're pulling in from remote APIs.

Groundwork's SyncedModel supports following relationships on remote resources and recreating them locally. It will do
this when your model definition has any of:

- A foreign key to another SyncedModel
- A many-many relationship to another SyncedModel
- An inverse relationship to another synced model

And the resource returned by the datasource has a field mapped to the model field where:

- A `str`, `int` or `uuuid` value that can be passed to the datasource's `get` method.
- An embedded instance of the related model's resource type.
- In the case of to-many relationship, a list of either of these.

Let's expand our example to include data about the current MP for the constituencies we just pulled in.

```python title="app/models.py"
from django.db import models
from pyck.core.datasources import SyncedModel, SyncConfig
from pyck.geo.territories.uk import parliament

class Constituency(SyncedModel):
    # This is where we specify the datasource, along with other options
    # for customizing how synchronization happens.
    sync_config = SyncConfig(
      datasource=parliament.constituencies,
    )

    # This is used to join data returned from the remote API against
    # our local data.
    external_id = models.IntegerField()

    # This will be populated from the remote data.
    name = models.CharField(max_length=256)

    # This will be populated from the remote data.
    current_mp = models.ForeignKey('MP',
      null=True,
      on_delete=models.SET_NULL)

class MP(SyncedModel):
    # This is where we specify the datasource, along with other options
    # for customizing how synchronization happens.
    sync_config = SyncConfig(
      datasource=parliament.members,
    )

    # This is used to join data returned from the remote API against
    # our local data.
    external_id = models.IntegerField()

    # This will be populated from the remote data.
    name = models.CharField(max_length=256)

    # This will be populated from the remote data.
    thumbnail_url = models.URLField(null=True)

    # This will be populated from the remote data.
    latest_party = models.ForeignKey('Party',
      null=True,
      on_delete=models.SET_NULL)

class Party(SyncedModel):
    # This is where we specify the datasource, along with other options
    # for customizing how synchronization happens.
    sync_config = SyncConfig(
      datasource=parliament.parties,
    )

    # This is used to join data returned from the remote API against
    # our local data.
    external_id = models.IntegerField()

    # This will be populated from the remote data.
    name = models.CharField(max_length=256)

    # This will be populated from the remote data.
    background_colour = models.CharField(max_length=256)
```

That's it! Generate and run migrations for the new models, run `python manage.py run_cron_tasks --once` again and you
now have the UK's westminster representitives (and their thumbnails) stored in your database.

We used this example not because it's especially interesting politically, but because it uses an open API that doesn't
require configuration. However, the same principles here apply to anything – membership databases, event listings, or
other services specific to your organisation.

## Provided datasources

- [UK Parliament Members & Constituencies](../../api/pyck.geo.territories.uk.parliament/)
- [UK Postcode Geocoding](../../api/pyck.geo.territories.uk.postcodes/)

Forthcoming:

- Action Network
- Airtable
- Google Sheets
- Nationbuilder
- Stripe

## Writing your own datasource

### Adapting an existing client library

Many services provide their own Python client library. If the one you're building a datasource for does, it's better to
simply adapt it in the Datasource interface than reinvent the wheel.

To do this, extend [Datasource](../../api/pyck.core.datasources/#externalresource). You need to implement `get()`
which should get a resource by id and `list()`, which should list resources, optionally filtering them.

Let's do that for a client library for an imaginary service classed _ZapMessage_.

Here we're assuming that its client library has a class for each resource type and that these all have a `get()` and
`filter()` class method to fetch from the API:

```python title="app/datasources/zapmessage.py"
from typing import TypeVar, Iterable, Any

import zapmessage
from django.conf import settings
from pyck.core.datasources import Datasource

# We're using type hints in this example, but feel free to ignore them if
# they're unfamiliar.
ResourceT = typing.TypeVar('ResourceT')

class ZapMessageResource(Datasource[ResourceT]):
  class NotFoundError(Exception):
    pass

  # The Datasource class will set any keyword-args provided to the
  # constructor as instance variables. We add this type hint to document
  # that this is expected.
  resource_type: zapmessage.Resource

  def get(self, id: str) -> ResourceT:
    response = self.resource_type.get(id, api_key=self.api_key)
    if response is None:
      raise ZapMessageResource.NotFoundError(f'not found: {id}')

    return response

  def list(self, **filter: Any) -> Iterable[ResourceT]:
    return self.resource_type.filter(api_key=self.api_key, **filter)

  @property
  def api_key(self):
    return setting.ZAPMESSAGE_API_KEY


messages: Datasource[zapmessage.Message] = ZapMessageResource(
  resource_type=zapmessage.Message
)

senders: Datasource[zapmessage.MessageSender] = ZapMessageResource(
  resource_type=zapmessage.MessageSender
)

categories: Datasource[zapmessage.MessageCategory] = ZapMessageResource(
  resource_type=zapmessage.MessageCategory
)

```

Now we can pass any of these resource endpoints to any API accepting a Datasource.

If the client library is designed well (as this one is), it will probably have consistent conventions for how its
different resources work.

If so, you can probably just define one class adopting the API's overall conventions and customize those using parameters to instances for individual resources.

A real-world example will obviously differ, and may introduce a few inconsistencies that you need to work around but
hopefully this gives you a good starting point!

### Calling a REST API

Let's imagine that _ZapMessage_ didn't provide a Python library and we needed to use its REST API instead.

To do this, we'll need to:

- Define data classes for each resource.
- If we need specify headers or otherwise customize how API calls are made, subclass RestDatasource with our
  customizations.

```python title="app/datasources/zapmessage.py"
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Iterable, Any, Dict

from django.conf import settings
from pyck.core.datasources import RestDatasource

@dataclass
class Message:
  id: str
  sender_id: str
  category_id: str
  timestamp: datetime
  content: str

@dataclass
class MessageSender:
  id: str
  name: str

@dataclass
class MessageSender:
  id: str
  name: str


# We're using type hints in this example, but feel free to ignore them if
# they're unfamiliar.
ResourceT = typing.TypeVar('ResourceT')

class ZapMessageResource(RestDatasource[ResourceT]):
  base_url = 'https://api.zapmessage.io'

  def get_headers(self) -> Dict[str, str]:
    return {
      'Authorization': f'Bearer {settings.ZAPMESSAGE_API_KEY}'
    }

messages: RestDatasource[Message] = ZapMessageResource(
  path='/messages',
  resource_type=Message
)

senders: RestDatasource[MessageSender] = ZapMessageResource(
  path='/senders',
  resource_type=MessageSender
)

categories: RestDatasource[MessageCategory] = ZapMessageResource(
  path='/categories',
  resource_type=MessageCategory
)
```

So far, so good! One additional customization we will often make is to define how list responses are handled.
By default, RestClient's list() call will expect to be returned a list of resources with no pagination.

Here's how we might do that:

```python
class ZapMessageResource(RestDatasource[ResourceT]):
  base_url = 'https://api.zapmessage.io'

  def get_headers(self) -> Dict[str, str]:
    return {
      'Authorization': f'Bearer {settings.ZAPMESSAGE_API_KEY}'
    }

  def paginate(self, **query: Any) -> Iterable[Any]:
    page = 1
    total_pages = None

    while total_pages is None or page <= total_pages>:
      response = self.fetch_url(self.url, query, page=page)
      total_pages = response['total_pages']

      for item in response['items']:
        yield item
```

You can see the full set of options and override points in
[RestClient](../../api/pyck.core.datasources/#restclient)'s API documentation.

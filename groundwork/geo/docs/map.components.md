# Map Components

## Conventions used

### Action bindings

Map components support adding interactivity by marking up your HTML with data attributes. When a component is documented
as supporting _actions_, you may connect a child element to it using the following syntax:

```
data-action="[event trigger]->[action]"
```

Where `[action]` is the documented action and `[event trigger]` is one of:

- For regular DOM elements, a DOM event supported by the element (`click`, `mouseenter`, `mouseleave`, etc)
- For components that document _sent events_, the name of a documented sent event.
- If you use Stimulus to incorporate your own Javascript, an event dispatched by your Stimulus controller.

For example, the `Map` component supports the `map#showPopup` handler which shows a popup on the map. We can connect
an anchor link to it as follows:

```html
<button data-action="click->map-popup#show">Show Popup</button>
```

Multiple action bindings can be attached to the same element by separating them with spaces:

```html
<button data-action="click->map-popup#show click->something-else#do">
  Show Popup
</button>
```

### Event parameters

For both event triggers and actions, we document _Event Parameters_. These allow important contextual information to be
passed between the element that originates an action and the element that receives it.

For example, if we wish to zoom the map to centre on a marker when the marker is clicked, the `click` event needs to
provide an parameter detailing the location to centre on to the `map#fly` action.

We can provide event parameters in several ways:

1. As properties of the event's [`detail`](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent/detail). For
   components that document parameters to _sent events_, they will be provided here. If you dispatch events yourself
   using Javascript, this is how you would provide parameters to the event. Note that the parameters are provided in
   `camelCase` here:

   ```javascript
   someElement.dispatchEvent(
     new CustomEvent("widget", { detail: { flyLocation: [4.53, 52.22] } })
   );
   ```

2. As data attributes of the elemnent that sends the event. This is useful because it allows you to provide event
   parameters to ordinary DOM elements when adding an action binding to them. Note that parameters are provided in
   `kebab-case` here:
   ```html
   <a data-action="click->map#fly" data-fly-location="[4.53,52.22]"></a>
   ```

## Map

Renders a Map onto the page.

=== "Django API"

    ```django
    {% load groundwork_geo %}

    {% map class="my-map-class" center="[4.53,52.22]" zoom=9 %}
    <!-- Map config tags go here -->
    {% endmap %}
    ```

    __Parameters__

    __`element`__
    :   Optional. Return a cache key given the arguments to the function

    __`style`__
    :   Optional. Override the map style on a per-map basis. Defaults to the `MAPBOX_DEFAULT_STYLE` django config.

    __`api_key`__
    :   Optional. Override the map API key on a per-map basis. Defaults to the `MAPBOX_PUBLIC_API_KEY` django config.

    __`center`__
    :   Optional. Initial [lon,lat] location to center the map on.

    __`zoom`__
    :   Optional. Initial zoom value. Defaults to 2.

    __Actions__

    __`map#showPopup`__
    : Shows a Popup at a location on the map. Accepts the following parameters:

        __`mapPopupFeature`__
        : _Required_. Feature to render the popover on. May be any of:

            - A Mapbox [`LngLatLike`](https://docs.mapbox.com/mapbox-gl-js/api/geography/#lnglatlike) object.
            - A GeoJSON Feature or Geometry.
            - A #-reference to either of the above.

        __`mapPopupContent`__
        : _Optional_. Html content to display in the popup. May be any of:

            - An html string.
            - A #-reference to an element whose children should be rendered in the popup.

        __`mapPopupContentProperty`__
        : _Optional_. If a GeoJSON feature is provided as _mapPopupFeature_, the key of a feature property containing
        HTML to render in the popup. Defaults to 'content'.

    __`map#hidePopup`__
    : Hide any popups visible on the map.

    __`map#fly`__
    : 'Fly' the camera to a specific location and zoom. Accepts the following parameters:

        __`mapFlyLocation`__
        : _Optional_. Feature to fly the map to. If not provided, the current location is preserved. May be any of:

            - A Mapbox [`LngLatLike`](https://docs.mapbox.com/mapbox-gl-js/api/geography/#lnglatlike) object.
            - A GeoJSON Feature or Geometry.
            - A #-reference to `<script>` element of type `application/json` containing either of the above.

        __`mapFlyZoom`__
        : _Optional_. Zoom level to fly the map to.

=== "Stimulus API"

    ```html
    <div
        class="my-map-class"
        data-controller="map"
        data-map-api-key-value="..."
        data-map-center-value="[4.53,52.22]"
        data-map-zoom-value="9"
    >
        <!-- Map config tags go here -->
        <div data-map-target="canvas"></div>
    </div>
    ```

    __Values__

    __`api-key`__
    : A valid mapbox public API key

    __`center`__
    : JSON array representing a [lon,lat] pair to initially center the map on.

    __`zoom`__
    : Initial map zoom value. Defaults to 2.

    __`style`__
    : Style for the map. Defaults to `mapbox/streets-v11`.

    __Targets__

    __`canvas`__
    : Required. An element to render the map into.

    __`config`__
    : One or more map config elements. These should have a controller that subclasses MapConfigController

    __Actions__

    __`map#showPopup`__
    : Shows a Popup at a location on the map. Accepts the following parameters:

        __`mapPopupFeature`__
        : _Required_. Feature to render the popover on. May be any of:

            - A Mapbox [`LngLatLike`](https://docs.mapbox.com/mapbox-gl-js/api/geography/#lnglatlike) object.
            - A GeoJSON Feature or Geometry.
            - A #-reference to either of the above.

        __`mapPopupContent`__
        : _Optional_. Html content to display in the popup. May be any of:

            - An html string.
            - A #-reference to an element whose children should be rendered in the popup.

        __`mapPopupContentProperty`__
        : _Optional_. If a GeoJSON feature is provided as _mapPopupFeature_, the key of a feature property containing
        HTML to render in the popup. Defaults to 'content'.

    __`map#hidePopup`__
    : Hide any popups visible on the map.

    __`map#fly`__
    : 'Fly' the camera to a specific location and zoom. Accepts the following parameters:

        __`mapFlyLocation`__
        : _Optional_. Feature to fly the map to. If not provided, the current location is preserved. May be any of:

            - A Mapbox [`LngLatLike`](https://docs.mapbox.com/mapbox-gl-js/api/geography/#lnglatlike) object.
            - A GeoJSON Feature or Geometry.
            - A #-reference to `<script>` element of type `application/json` containing either of the above.

        __`mapFlyZoom`__
        : _Optional_. Zoom level to fly the map to.

## Map source

Adds a datasource to a map.

=== "Django API"

    ```django
    {% load groundwork_geo %}

    {% map %}
        {% map_source id="my_datasource_id" data=my_datasource %}
    {% endmap %}
    ```

    __Parameters__

    __`id`__
    : ID for the datasource made available to layers

    __`data`__
    : JSON object conforming to the [Mapbox source specification](https://docs.mapbox.com/mapbox-gl-js/style-spec/sources/)

=== "Stimulus API"

    ```html
    <div
        data-controller="map"
        data-map-api-key-value="..."
    >
        <div
            data-controller="map-source"
            data-map-target="config"
            data-map-source-id-value="my_datasource_id"
            data-map-source-data-value='{"type": "geojson", "url": "mapbox://mapbox.mapbox-terrain-v2"}'
        >
        </div>
        <div data-map-target="canvas"></div>
    </div>
    ```

    __Parameters__

    __`id`__
    : ID for the datasource made available to layers

    __`data`__
    : JSON object conforming to the [Mapbox source specification](https://docs.mapbox.com/mapbox-gl-js/style-spec/sources/)

## Map layer

Adds a layer to a map.

=== "Django API"

    ```django
    {% load groundwork_geo %}

    {% map %}
        {% map_layer layer=my_layer %}
    {% endmap %}
    ```

    __Parameters__

    __`layer`__
    : JSON object conforming to the [Mapbox layer specification](https://docs.mapbox.com/mapbox-gl-js/style-spec/layers/)

=== "Stimulus API"

    ```html
    <div
        data-controller="map"
        data-map-api-key-value="xxx"
    >
        <div
            data-controller="map-layer"
            data-map-target="config"
            data-map-layer-layer-value='{"id": "terrain-data", "type": "line", "source": "mapbox-terrain", ...}'
        >
        </div>
        <div data-map-target="canvas"></div>
    </div>
    ```

    __Parameters__

    __`layer`__
    : JSON object conforming to the [Mapbox layer specification](https://docs.mapbox.com/mapbox-gl-js/style-spec/layers/)

## Map marker

Adds a marker to a map at a location. Supports custom html markup to define the marker.

!!! note

    Note that this API is intended for displaying a relatively small number of markers on the map. It performs badly with large quantities of data, but trades this off for being relatively simple to use and being easy to add custom
    interactions to. It's better suited to focusing on a relatively small number of locations than allowing someone to
    explore many.

    For displaying large datasets, you should consider clustering your points and fetching on demand (support for this forthcoming!)

=== "Django API"

    ```django
    {% load groundwork_geo %}

    {% map %}
        {% map_marker location="[4.53,52.22]" %}
            <div style="width: 25px; height: 25px; border-radius: 50%; background-color: hotpink;"></div>
        {% endmarker %}
    {% endmap %}
    ```

    __Parameters__

    __`location`__
    : Longitude-latitude array locating the map marker.

    __`children`__
    : HTML markup for the marker. If omitted, the default Mapbox marker is used.

=== "Stimulus API"

    ```html
    <div
        data-controller="map"
        data-map-api-key-value="xxx"
    >
        <div
            data-controller="map-marker"
            data-map-target="config"
            data-map-marker-location-value="[4.53,52.22]"
        >
        </div>
        <div data-map-target="canvas"></div>
    </div>
    ```

    __Parameters__

    __`location`__
    : Longitude-latitude array locating the map marker.

    __`children`__
    : HTML markup for the marker. If omitted, the default Mapbox marker is used.

# Map Components

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

    Any additional arguments are passed to the map as attributes.

=== "Stimulus API"

    ```html
    <div
        class="my-map-class"
        data-controller="map"
        data-map-api-key-value="..."
        data-map-api-center-value="[4.53,52.22]"
        data-map-api-zoom-value="9"
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

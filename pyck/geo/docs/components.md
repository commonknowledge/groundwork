# Map Components

## Map

Renders a mapbox map onto the page.

=== "Django Templates"

    ```django
    {% load ckgeo_tags %}

    {% map class="my-map-class" center="[4.53,52.22]" zoom=9 %}
    <!-- Map config tags go here -->
    {% endmap %}
    ```

    __Parameters__

    `element`
    :   Optional. Return a cache key given the arguments to the function

    `style`
    :   Optional. Override the map style on a per-map basis. Defaults to the `MAPBOX_DEFAULT_STYLE` django config.

    `api_key`
    :   Optional. Override the map api key on a per-map basis. Defaults to the `MAPBOX_PUBLIC_API_KEY` django config.

    `center`
    :   Optional. Initial [lon,lat] location to center the map on.

    `zoom`
    :   Optional. Initial zoom value. Defaults to 2.

    Any additional arguments are passed to the map as attributes.

=== "Stimulus Controller"

    ```html
    <div
        class="my-map-class"
        data-controller="map"
        data-map-api-key-value="xxx"
        data-map-api-center-value="[4.53,52.22]"
        data-map-api-zoom-value="9"
    >
        <!-- Map config tags go here -->
        <div data-map-target="canvas"></div>
    </div>
    ```

    __Required values__

    - `data-map-api-key-value`: A valid mapbox public api key

    __Optional values__

    - `data-map-api-center-value`: JSON array representing a [lon,lat] pair to initially center the map on.
    - `data-map-zoom-value`: Initial map zoom value. Defaults to 2.
    - `data-map-style-value`: Style for the map. Defaults to `mapbox/streets-v11`.

    __Required targets__

    - `data-map-target="canvas"`: An element to render the map into.

    __Optional targets__

    - `data-map-target="config"`: One or more map config elements. These should have a controller that subclasses MapConfigController

## Map source

## Map layer

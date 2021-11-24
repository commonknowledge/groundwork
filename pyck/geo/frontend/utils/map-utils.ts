import { Controller } from "@hotwired/stimulus";
import mapboxgl from "mapbox-gl";
import { resolveablePromise } from "~core/util/promise-utils";

/**
 * Base class for a map config controller.
 *
 * Subclassers should override `connectMap` and `disconnectMap`, and/or implement their own event handlers to configure
 * the mapbox instance with controls, data sources, custom layers, etc.
 */
export class MapConfigController<T = void> extends Controller {
  map?: mapboxgl.Map;
  ready = resolveablePromise();

  initialize() {
    this.element.addEventListener("map:ready", this.handleMapReady, {
      once: true,
    });
  }

  disconnect() {
    if (this.map) {
      this.disconnectMap(this.map);
    }
  }

  connectMap(map: mapboxgl.Map): void | Promise<void> {}
  disconnectMap(map: mapboxgl.Map): void | Promise<void> {}

  private handleMapReady = async (event: any) => {
    const map = event.detail.map;
    this.map = map;
    await this.connectMap(map);
    this.ready.resolve();
  };
}

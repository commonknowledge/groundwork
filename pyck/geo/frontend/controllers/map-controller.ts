import { Controller } from "@hotwired/stimulus";
import mapbox from "mapbox-gl";
import { getReferencedData } from "~core/util/stimulus-utils";

export const MAPBOX_MAP_SYMBOL = Symbol("mapbox-instance");

/**
 * Controller for rendering a mapbox map.
 *
 * Required values:
 *  - `data-map-api-key-value`: A valid mapbox public api key
 *
 * Optional values:
 *  - `data-map-api-center-value`: JSON array representing a [lon,lat] pair to initially center the map on.
 *  - `data-map-zoom-value`: Initial map zoom value. Defaults to 2.
 *  - `data-map-style-value`: Style for the map. Defaults to `mapbox/streets-v11`.
 *
 * Required targets:
 *  - `data-map-target="canvas"`: An element to render the map into.
 *
 * Optional targets:
 *  - `data-map-target="config"`: One or more map config elements. These should have a controller that subclasses MapConfigController
 */
export default class MapController extends Controller {
  static targets = ["canvas", "config"];
  static values = {
    apiKey: String,
    center: String,
    style: String,
    zoom: Number,
  };

  private static cssLoaded = false;

  private apiKeyValue!: string;
  private styleValue!: string;
  private centerValue!: string;
  private zoomValue!: number;

  private canvasTarget!: HTMLElement;
  private configTargets!: HTMLElement[];

  initialize() {
    if (!this.canvasTarget) {
      console.error(
        'No canvas target registered with map controller. Add a child with the attribute `data-map-target="canvas"`'
      );
    }

    const el = this.canvasTarget as any;

    // Install the mapbox instance on the canvas element. Adding it here means that frameworks like turbo can make the
    // canvas persist between loads while recreating controllers so that its configuration can be driven reactively,
    // eg - from the url.
    if (!el[MAPBOX_MAP_SYMBOL]) {
      el[MAPBOX_MAP_SYMBOL] = this.loadMap();
    }

    // Size the canvas element to match the containing element.
    const containerStyle = window.getComputedStyle(this.element);
    if (containerStyle.position === "static") {
      (this.element as HTMLElement).style.position = "relative";
    }

    this.canvasTarget.style.width = "100%";
    this.canvasTarget.style.height = "100%";
  }

  async connect() {
    const mapbox = await this.mapbox;
    if (!mapbox) {
      return;
    }

    // Give any config targets the opportunity to configure the map.
    for (const target of this.configTargets) {
      target.dispatchEvent(
        new CustomEvent("map:ready", {
          bubbles: false,
          detail: { map: mapbox },
        })
      );
    }
  }

  /**
   * Return the mapbox instance attached to the map canvas element.
   */
  get mapbox() {
    const el = this.canvasTarget as any;
    return el[MAPBOX_MAP_SYMBOL] as Promise<mapbox.Map> | undefined;
  }

  /**
   * Parse and return the centre value as a json object.
   */
  private get latLng() {
    return getReferencedData<mapbox.LngLatLike>(this.centerValue) ?? [0, 0];
  }

  /**
   * Initialize the mapbox instance and attach to the dom.
   */
  private loadMap() {
    return new Promise<mapbox.Map | undefined>(async (resolve) => {
      if (!this.apiKeyValue) {
        console.error("Mapbox: No API token defined.");
        return resolve(undefined);
      }

      if (!this.canvasTarget) {
        console.error("Mapbox: No canvas target defined.");
        return resolve(undefined);
      }

      if (!MapController.cssLoaded) {
        await MAPBOX_CSS;
        MapController.cssLoaded = true;
      }

      const map = new mapbox.Map({
        accessToken: this.apiKeyValue,
        container: this.canvasTarget,
        style: this.styleValue || "mapbox://styles/mapbox/streets-v11",
        center: this.latLng,
        zoom: this.zoomValue || 2,
      });

      // Wait for the map to finish loading before resolving.
      map.on("load", () => {
        resolve(map);
      });
    });
  }
}

// Load the mapbox css via dynamic import so that it isn't added to the entry css by bundlers.
const MAPBOX_CSS = import("mapbox-gl/dist/mapbox-gl.css");

import mapboxCSS from "mapbox-gl/dist/mapbox-gl.css";

import { Controller } from "@hotwired/stimulus";
import mapbox from "mapbox-gl";
import { getEventParameters, getReferencedData } from "../../core";
import { createCssLoader } from "../../core/util/css-utils";
import { toFeature, toLngLatLike } from "../utils/geo-utils";

/**
 * @internal
 *
 * Symbol used to attach mapbox instance to dom element.
 */
export const MAPBOX_MAP_SYMBOL = "__mapbox_instance";

export default class MapController extends Controller {
  static targets = ["canvas", "config"];
  static values = {
    apiKey: String,
    center: String,
    style: String,
    zoom: Number,
  };

  private apiKeyValue!: string;
  private styleValue!: string;
  private centerValue!: string;
  private zoomValue!: number;

  private popups = new Set<mapbox.Popup>();
  private map?: mapbox.Map;

  private canvasTarget!: HTMLElement;
  private configTargets!: HTMLElement[];

  initialize() {
    loadCss();

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

    this.canvasTarget.style.opacity = "0";
    this.canvasTarget.style.width = "100%";
    this.canvasTarget.style.height = "100%";
  }

  async connect() {
    const mapbox = await this.mapboxLoader;
    if (!mapbox) {
      return;
    }

    this.map = mapbox;

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
  get mapboxLoader() {
    const el = this.canvasTarget as any;
    return el[MAPBOX_MAP_SYMBOL] as Promise<mapbox.Map> | undefined;
  }

  /**
   * Action. Show a popup at the location described by the event.
   */
  showPopup(event: Event) {
    event.stopPropagation();

    if (!this.map) {
      return;
    }

    let {
      mapPopupFeature,
      mapPopupContent,
      mapPopupContentProperty = "content",
    } = getEventParameters(event, {
      mapPopupFeature: "object",
      mapPopupContent: "html",
      mapPopupContentProperty: "string",
    });

    if (!mapPopupContent) {
      mapPopupContent =
        toFeature(mapPopupFeature)?.properties?.[mapPopupContentProperty];
    }

    const location = toLngLatLike(mapPopupFeature);
    if (!location) {
      console.error(
        "Not adding popup to map because required parameter `mapPopupFeature` is not a valid location"
      );
      return;
    }
    if (!mapPopupContent) {
      console.error(
        "Not adding popup to map because neither mapPopupFeature nor mapPopupContent parameters provide valid html content."
      );
      return;
    }

    const popup = new mapbox.Popup()
      .setLngLat(location)
      .setHTML(mapPopupContent)
      .addTo(this.map);

    this.popups.add(popup);
    return popup;
  }

  /**
   * Action. Hides all popups.
   */
  hidePopup(event: Event) {
    event.stopPropagation();

    for (const popup of this.popups) {
      popup.remove();
    }

    this.popups.clear();
  }

  /**
   * Action. Fly the map to a specific location.
   */
  fly(event: Event) {
    event.stopPropagation();

    const { mapFlyLocation, mapFlyZoom } = getEventParameters(event, {
      mapFlyLocation: toLngLatLike,
      mapFlyZoom: "number",
    });

    if (mapFlyLocation || mapFlyZoom) {
      this.map?.flyTo({
        animate: true,
        center: mapFlyLocation,
        zoom: mapFlyZoom,
      });
    }
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

      const map = new mapbox.Map({
        accessToken: this.apiKeyValue,
        container: this.canvasTarget,
        style: this.styleValue || "mapbox://styles/mapbox/streets-v11",
        center: this.latLng,
        zoom: this.zoomValue || 2,
      });

      // Wait for the map to finish loading before resolving.
      map.on("load", () => {
        map.resize();

        setTimeout(() => {
          this.canvasTarget.style.opacity = "1";
          resolve(map);
        }, 120);
      });
    });
  }
}

const loadCss =
  import.meta.env.MODE !== "bundled" ? createCssLoader(mapboxCSS) : () => {};

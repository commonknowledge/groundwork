import { Feature } from "geojson";
import type { Map } from "mapbox-gl";
import { Popup, MapMouseEvent } from "mapbox-gl";
import { getReferencedData } from "../../core";
import { MapConfigController } from "../utils/map-utils";

export default class MapPopupController extends MapConfigController {
  popup = new Popup();

  show(event: Event | Feature | string) {
    const feature = this.resolve(event);
    if (!feature || !this.map) {
      return;
    }

    if (feature.geometry.type !== "Point") {
      return;
    }

    const contentField = this.resolveContentField(event);
    if (event instanceof Event) {
      event.stopPropagation();
    }

    this.popup.setLngLat(feature.geometry.coordinates as [number, number]);
    this.popup.setHTML(feature.properties?.[contentField]);
    this.popup.addTo(this.map);
  }

  hide() {
    this.popup.remove();
  }

  private resolveContentField(value: Event | Feature | string) {
    if (value instanceof Event && value.target instanceof HTMLElement) {
      if (value.target.dataset.mapPopupContentProperty) {
        return value.target.dataset.mapPopupContentProperty;
      }
    }

    return "content";
  }

  private resolve(value: Event | Feature | string): Feature | undefined {
    if (typeof value === "string") {
      return getReferencedData(value);
    }
    if (value instanceof Event) {
      if (
        value.target instanceof HTMLElement &&
        value.target.dataset.mapPopupContent
      ) {
        return this.resolve(value.target.dataset.mapPopupContent);
      } else {
        return;
      }
    }

    return value;
  }
}

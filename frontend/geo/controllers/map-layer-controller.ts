import type { Map, AnyLayer, MapLayerEventType } from "mapbox-gl";
import { getReferencedData } from "../../core/util/stimulus-utils";
import { MapConfigController } from "../utils/map-utils";

const LAYER_EVENTS: (keyof MapLayerEventType)[] = [
  "click",
  "dblclick",
  "mousedown",
  "mouseup",
  "mousemove",
  "mouseenter",
  "mouseleave",
  "mouseover",
  "mouseout",
  "contextmenu",

  "touchstart",
  "touchend",
  "touchcancel",
];

export default class MapLayerController extends MapConfigController {
  static values = {
    layer: String,
  };

  layerValue!: string;

  connectMap(map: Map) {
    const layer = this.layer;

    if (layer && !map.getLayer(layer.id)) {
      map.addLayer(layer);

      for (const eventType of LAYER_EVENTS) {
        map.on(eventType, layer.id, this.handle);
      }
    }
  }

  disconnectMap(map: Map) {
    const layer = this.layer;

    if (layer) {
      map.removeLayer(layer.id);

      for (const eventType of LAYER_EVENTS) {
        map.off(eventType, layer.id, this.handle);
      }
    }
  }

  get layer() {
    return getReferencedData<AnyLayer>(this.layerValue);
  }

  private handle = <T extends keyof MapLayerEventType>(
    event: MapLayerEventType[T]
  ) => {
    this.dispatch(event.type, {
      detail: event,
    });
  };
}

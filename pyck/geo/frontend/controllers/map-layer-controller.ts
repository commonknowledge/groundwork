import mapboxgl from "mapbox-gl";
import { getReferencedData } from "~core/util/stimulus-utils";
import { MapConfigController } from "../utils/map-utils";

export default class MapLayerController extends MapConfigController {
  static values = {
    layer: String,
  };

  layerValue!: string;

  connectMap(map: mapboxgl.Map) {
    const layer = this.layer;

    if (layer && !map.getLayer(layer.id)) {
      map.addLayer(layer);
    }
  }

  disconnectMap(map: mapboxgl.Map) {
    const layer = this.layer;

    if (layer) {
      map.removeLayer(layer.id);
    }
  }

  get layer() {
    return getReferencedData<mapboxgl.AnyLayer>(this.layerValue);
  }
}

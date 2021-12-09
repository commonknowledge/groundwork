import type { Map, AnySourceData } from "mapbox-gl";
import { getReferencedData } from "../../core/util/stimulus-utils";
import { MapConfigController } from "../utils/map-utils";

export default class MapSourceController extends MapConfigController<AnySourceData> {
  static values = {
    id: String,
    data: String,
  };

  idValue!: string;
  dataValue!: string;

  connectMap(map: Map) {
    const data = this.sourceData;

    if (data && !map.getSource(this.idValue)) {
      map.addSource(this.idValue, data);
    }
  }

  disconnectMap(map: Map) {
    map.removeLayer(this.idValue);
  }

  get sourceData() {
    return getReferencedData<AnySourceData>(this.dataValue);
  }
}

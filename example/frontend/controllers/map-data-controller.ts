import type { Map, MapLayerEventType } from "mapbox-gl";
import { MapConfigController } from "../../../frontend/index.lib";

export default class MapDataController extends MapConfigController {
  static targets = ["eventLog"];
  private readonly eventLogTarget?: HTMLElement;
  static values = {
    mapEvent: { type: String, default: "click" },
  };
  private mapEventValue!: keyof MapLayerEventType;

  connectMap(map: Map) {
    map?.on(this.mapEventValue, (e) => {
      if (!this.eventLogTarget) return;
      this.eventLogTarget.innerHTML = JSON.stringify(e, null, 2);
    });
  }
}

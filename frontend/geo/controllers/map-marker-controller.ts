import type { Map, AnySourceData } from "mapbox-gl";
import mapbox from "mapbox-gl";
import { getReferencedData } from "../../core/util/stimulus-utils";
import { MapConfigController } from "../utils/map-utils";

export default class MapMarkerController extends MapConfigController<AnySourceData> {
  static values = {
    location: String,
  };

  private locationValue!: string;
  marker!: mapbox.Marker;

  initialize() {
    super.initialize();

    const el = this.element.children[0]?.cloneNode() as HTMLElement | undefined;
    this.marker = new mapbox.Marker(el);
  }

  connectMap(map: Map) {
    this.marker.setLngLat(this.latLng).addTo(map);
  }

  disconnectMap(map: Map) {
    this.marker.remove();
  }

  /**
   * Parse and return the centre value as a json object.
   */
  private get latLng() {
    return getReferencedData<mapbox.LngLatLike>(this.locationValue) ?? [0, 0];
  }
}

import { EventEmitter } from "events";
import type { AnySourceImpl, LngLatLike } from "mapbox-gl";

type MockedMethods = Pick<
  mapboxgl.Map,
  | "getContainer"
  | "addLayer"
  | "removeLayer"
  | "getLayer"
  | "addSource"
  | "removeSource"
  | "getSource"
>;

class MockMap extends EventEmitter implements MockedMethods {
  private layers = new Map<string, mapboxgl.AnyLayer>();
  private sources = new Map<string, MockSource>();

  constructor(private options?: mapboxgl.MapboxOptions) {
    super();

    setTimeout(() => {
      this.emit("load");
    });
  }

  getContainer() {
    return this.options?.container as HTMLElement;
  }

  resize() {}

  addLayer(layer: mapboxgl.AnyLayer): mapboxgl.Map {
    this.layers.set(layer.id, layer);
    return this as any;
  }

  removeLayer(id: string): mapboxgl.Map {
    this.layers.delete(id);
    return this as any;
  }

  getLayer(id: string): mapboxgl.AnyLayer {
    return this.layers.get(id)!;
  }

  addSource(id: string, source: mapboxgl.AnySourceData): mapboxgl.Map {
    this.sources.set(id, new MockSource(source.type));
    return this as any;
  }

  removeSource(id: string): mapboxgl.Map {
    this.sources.delete(id);
    return this as any;
  }

  getSource(id: string): mapboxgl.AnySourceImpl {
    return this.sources.get(id) as any;
  }
}

class MockSource {
  constructor(readonly type: string) {}
}

class MockMarker {
  _lngLat?: LngLatLike;

  setLngLat(ll: LngLatLike) {
    this._lngLat = ll;
    return this;
  }

  addTo() {
    return this;
  }

  getLngLat() {
    return this._lngLat;
  }
}

export default { Map: MockMap, Marker: MockMarker };

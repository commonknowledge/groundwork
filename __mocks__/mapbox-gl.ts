import { EventEmitter } from "events";
import type { Popup, LngLatLike } from "mapbox-gl";

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
      this.emit("load", {});
    });
  }

  on(event: string, layerOrListener: any, listener?: any): any {
    if (listener) {
      super.on(event + ":" + layerOrListener, listener);
    } else {
      super.on(event, layerOrListener);
    }
  }

  off(event: string, layerOrListener: any, listener?: any): any {
    if (listener) {
      super.off(event + ":" + layerOrListener, listener);
    } else {
      super.off(event, layerOrListener);
    }
  }

  emit(event: string, layerOrValue: any, value?: any): any {
    if (value) {
      super.emit(event + ":" + layerOrValue, value);
    } else {
      super.emit(event, layerOrValue);
    }
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

class MockPopup implements Partial<Popup> {
  _lngLat: LngLatLike = [0, 0];
  _el = document.createElement("div");

  getElement() {
    return this._el;
  }

  setLngLat(ll: LngLatLike) {
    this._lngLat = ll;
    return this as any;
  }

  getLngLat() {
    return this._lngLat as any;
  }

  setHTML(html: string) {
    this._el.innerHTML = html;
    return this as any;
  }

  addTo() {
    return this as any;
  }

  remove() {
    return this as any;
  }
}

export default { Map: MockMap, Marker: MockMarker, Popup: MockPopup };

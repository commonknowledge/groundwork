import { EventEmitter } from "events";
import mapboxgl, { AnySourceImpl } from "mapbox-gl";

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

export default { Map: MockMap };

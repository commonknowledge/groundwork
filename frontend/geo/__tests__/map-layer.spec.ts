import MapLayerController from "../controllers/map-layer-controller";
import { createConfigFixture } from "../utils/map-test-utils";

test("attaching a layer adds the layer to the map", async () => {
  const someLayer = {
    id: "myLayer",
  };

  const fixture = await createConfigFixture(MapLayerController, {
    values: {
      layer: someLayer,
    },
  });

  expect(fixture.map?.getLayer(someLayer.id)).toEqual(someLayer);
});

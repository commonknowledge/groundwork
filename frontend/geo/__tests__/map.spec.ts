import { createTestFixture } from "../../core/test-utils";
import MapController from "../controllers/map-controller";
import { MapConfigController } from "../";

test("initializes mapbox and binds to canvas", async () => {
  const fixture = await createTestFixture({
    controllers: [MapController],
    html: `
    <div data-testid="map" data-controller="map" data-map-api-key-value="dummy">
      <div data-testid="canvas" data-map-target="canvas"></div>
    </div>
    `,
  });

  const map = fixture.getController(MapController, "map");
  const mapbox = await map.mapbox;

  expect(mapbox?.getContainer()).toBe(fixture.getByTestId("canvas"));
});

test("sets up config controllers", async () => {
  const connectMap = jest.fn();
  class SomeConfigController extends MapConfigController {
    connectMap = connectMap;
  }

  const fixture = await createTestFixture({
    controllers: [MapController, SomeConfigController],
    html: `
    <div data-testid="map" data-controller="map" data-map-api-key-value="dummy">
      <slot data-testid="config" data-map-target="config" data-controller="someconfig">

      <div data-testid="canvas" data-map-target="canvas"></div>
    </div>
    `,
  });

  const map = fixture.getController(MapController, "map");
  const config = fixture.getController(SomeConfigController, "config");
  await config.ready;

  expect(config.map).toBe(await map.mapbox);
  expect(connectMap).toBeCalledWith(await map.mapbox);
});

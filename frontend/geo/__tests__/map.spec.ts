import { createTestFixture, customEvent } from "../../core/test-utils";
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
  const mapbox = await map.mapboxLoader;

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

  expect(config.map).toBe(await map.mapboxLoader);
  expect(connectMap).toBeCalledWith(await map.mapboxLoader);
});

describe("popups", () => {
  test("shows a popup providing content via mapPopupContent", async () => {
    const { map } = await someMap();
    const eventProps = {
      mapPopupFeature: [1, 1],
      mapPopupContent: "<div>Hello</div>",
    };

    const popup = map.showPopup(customEvent(eventProps));

    expect(popup?.getElement().innerHTML).toEqual(eventProps.mapPopupContent);
    expect(popup?.getLngLat()).toEqual(eventProps.mapPopupFeature);
  });

  test("hides popup and discards it when requested", async () => {
    const { map } = await someMap();
    const eventProps = {
      mapPopupFeature: [1, 1],
      mapPopupContent: "<div>Hello</div>",
    };

    const popup = map.showPopup(customEvent(eventProps))!;
    popup.remove = jest.fn();

    map.hidePopup(customEvent({}));
    map.hidePopup(customEvent({}));

    expect(popup.remove).toBeCalledTimes(1);
  });

  test("shows a popup providing content via mapPopupFeature", async () => {
    const { map } = await someMap();
    const eventProps = {
      mapPopupFeature: {
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [1, 1],
        },
        properties: {
          content: "<div>Hello</div>",
        },
      },
    };

    const popup = map.showPopup(customEvent(eventProps));

    expect(popup?.getElement().innerHTML).toEqual(
      eventProps.mapPopupFeature.properties.content
    );
    expect(popup?.getLngLat()).toEqual(
      eventProps.mapPopupFeature.geometry.coordinates
    );
  });

  test("flies to specified location and zoom", async () => {
    const { map } = await someMap();
    const eventProps = {
      mapFlyLocation: [1, 1],
      mapFlyZoom: 10,
    };
    const mapbox = await map.mapboxLoader!;
    mapbox.flyTo = jest.fn();

    map.fly(customEvent(eventProps));

    expect(mapbox.flyTo).toBeCalledWith(
      expect.objectContaining({
        center: eventProps.mapFlyLocation,
        zoom: eventProps.mapFlyZoom,
      })
    );
  });
});

const someMap = async () => {
  const fixture = await createTestFixture({
    controllers: [MapController],
    html: `
    <div data-testid="map" data-controller="map" data-map-api-key-value="dummy">
      <div data-testid="canvas" data-map-target="canvas"></div>
    </div>
    `,
  });

  const map = fixture.getController(MapController, "map");
  await map.mapboxLoader;

  return Object.assign(fixture, {
    map,
  });
};

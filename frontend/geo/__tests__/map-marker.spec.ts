import MapMarkerController from "../controllers/map-marker-controller";
import { createConfigFixture } from "../utils/map-test-utils";

test("sets longitude and latitude on the marker", async () => {
  const fixture = await createConfigFixture(MapMarkerController, {
    values: {
      location: "[11,11]",
    },
  });

  expect(fixture.config.marker.getLngLat()).toEqual([11, 11]);
});

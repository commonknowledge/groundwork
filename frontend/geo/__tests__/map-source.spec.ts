import MapSourceController from "../controllers/map-source-controller";
import { createConfigFixture } from "../utils/map-test-utils";

test("attaching a source adds the source to the map", async () => {
  const someId = "map-source-id";
  const someSource = {
    type: "geojson",
  };

  const fixture = await createConfigFixture(MapSourceController, {
    values: {
      id: someId,
      data: someSource,
    },
  });

  const source = fixture.map?.getSource(someId);

  expect(source?.type).toEqual(someSource.type);
});

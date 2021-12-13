import {
  createTestFixture,
  getTestControllerIdentifier,
} from "../../core/test-utils";

import MapController from "../controllers/map-controller";
import { MapConfigController } from "./map-utils";

/**
 * Utility to set up a
 * @param controller
 */
export const createConfigFixture = async <T extends MapConfigController>(
  controller: new (...args: any[]) => T,
  opts: {
    values?: {};
  } = {}
) => {
  const identifier = getTestControllerIdentifier(controller);
  const attributeString = Object.entries(opts.values ?? {})
    .map(
      ([key, val]) => `data-${identifier}-${key}-value='${serializeVal(val)}'`
    )
    .join(" ");

  const fixture = await createTestFixture({
    controllers: [MapController, controller],
    html: `
    <div data-testid="map" data-controller="map" data-map-api-key-value="dummy">
      <slot data-testid="config" data-map-target="config" data-controller="${identifier}" ${attributeString}>

      <div data-map-target="canvas"></div>
    </div>
    `,
  });

  const map = fixture.getController(MapController, "map");
  const config = fixture.getController(controller, "config");

  await config.ready;

  return Object.assign(fixture, {
    map: await map.mapboxLoader,
    config,
  });
};

const serializeVal = (val: any) => {
  if (val === null || val === undefined) {
    return "";
  }

  if (typeof val === "object") {
    return JSON.stringify(val);
  }

  return val;
};

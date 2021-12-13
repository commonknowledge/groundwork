import { Feature, Point } from "geojson";
import type { LngLatLike } from "mapbox-gl";

export const toLngLatLike = (x: any): LngLatLike | undefined => {
  if (!x) {
    return;
  }

  if ("lat" in x || Array.isArray(x)) {
    return x;
  }

  const geo: Feature | Point = x;
  if (geo.type === "Point") {
    return geo.coordinates as LngLatLike;
  }

  if (geo.type === "Feature" && geo.geometry.type === "Point") {
    return geo.geometry.coordinates as LngLatLike;
  }
};

export const toFeature = (x: any): Feature | undefined => {
  if (!x) {
    return;
  }

  if (x.type === "Feature") {
    return x;
  }
};

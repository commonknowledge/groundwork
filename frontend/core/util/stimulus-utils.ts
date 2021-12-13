import { Dict } from "./types";

/**
 * Implements conventions for passing event parameters to a Stimulus action.
 *
 * @param event Event object. Parameters
 * @param schema Schema object defining how to deserialize the parameters.
 * @returns The deserialized event parameters.
 */
export const getEventParameters = <T extends Dict<SchemaField>>(
  event: Event,
  schema: T
): SchemaType<T> => {
  const props: any = {};

  if (event instanceof CustomEvent) {
    Object.assign(props, event.detail);
  }

  if (event.target instanceof HTMLElement) {
    Object.assign(props, event.target.dataset);
  }

  for (const [key, val] of Object.entries(schema)) {
    props[key] = deserializeValue(props[key], val);
  }

  return props;
};

/**
 * Return either the data represented by a #-reference to a json script
 * or, if a json string the decoded json value.
 *
 * This is useful for passing large JSON objects to the frontend that would be unweildy to
 * do via stimulus's default json value type
 *
 * @param data Either a JSON string or a #-reference to a script element whose inner text is JSON.
 * @returns The decoded json object
 */
export const getReferencedData = <T>(data: string): T | undefined => {
  if (!data) {
    return;
  }

  if (data.startsWith("#")) {
    const json = document.querySelector(data)?.textContent;
    return json ? JSON.parse(json) : undefined;
  }

  return JSON.parse(data);
};

/**
 * Lightweight deserialization of parameters to events defined either in HTML data attributes or detail fields on a
 * CustomEvent.
 *
 * @param val Value to be deserialized.
 * @param type Either the id of a known type or a function that further prepares an object.
 * @returns The deserialized value.
 */
const deserializeValue = (val: any, type: SchemaField): any => {
  if (typeof type === "function") {
    if (typeof val === "string") {
      return type(getReferencedData<any>(val));
    } else {
      return type(val);
    }
  }

  if (type == "number" && typeof val !== "undefined") {
    return Number(val);
  }

  if (type == "string" && typeof val !== "undefined") {
    return String(val);
  }

  if (type == "bool") {
    return JSON.parse(val ?? "false");
  }

  if (type === "object" || type === "array") {
    if (typeof val === "object") {
      return val;
    }

    if (typeof val === "string") {
      return getReferencedData(val);
    }

    return;
  }

  if (type === "html") {
    if (typeof val === "string") {
      if (type.startsWith("#")) {
        return document.querySelector(type)?.innerHTML;
      }

      return val;
    }

    return "";
  }
};

/** Maps deserializable type names to their output type */
type SchemaVal = {
  string: string | undefined;
  number: number | undefined;
  html: string;
  bool: boolean;
  object: any;
  array: any[];
};

/** Possible values for fields in an event parameters schema */
type SchemaField = keyof SchemaVal | ((x: object) => any);

/** Infer the deserialized type from an event parameters */
type SchemaType<S extends Dict<SchemaField>> = {
  [P in keyof S]: S[P] extends keyof SchemaVal
    ? SchemaVal[S[P]]
    : S[P] extends (x: object) => any
    ? ReturnType<S[P]>
    : unknown;
};

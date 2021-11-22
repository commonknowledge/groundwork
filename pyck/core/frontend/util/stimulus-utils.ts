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
    const json = document.querySelector(data)?.innerHTML;
    return json ? JSON.parse(json) : undefined;
  }

  return JSON.parse(data);
};

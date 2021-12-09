/**
 * Load css from string and add to the document's style
 *
 * @param css Result of import "*.css"
 */
export const createCssLoader = (css: string) => {
  let el: HTMLStyleElement | undefined;

  return () => {
    if (el) {
      return;
    }

    el = document.createElement("style");
    el.innerHTML = css as any;
    document.head.appendChild(el);
  };
};

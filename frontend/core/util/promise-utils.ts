export const resolveablePromise = <T = void>() => {
  let doResolve: (x: T) => void;
  const resolve = (x: T) => doResolve(x);

  return Object.assign(
    new Promise<T>((resolve) => {
      doResolve = resolve;
    }),
    { resolve }
  );
};

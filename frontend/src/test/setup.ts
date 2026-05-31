import "@testing-library/jest-dom";

// jsdom lacks ResizeObserver (used by react-medium-image-zoom). Polyfill it.
if (!globalThis.ResizeObserver) {
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
}

// jsdom lacks URL.createObjectURL (used by image preview). Stub it.
if (!globalThis.URL.createObjectURL) {
  globalThis.URL.createObjectURL = () => "blob:mock";
}

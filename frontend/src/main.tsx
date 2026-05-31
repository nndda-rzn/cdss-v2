import "@fontsource-variable/inter";
import "./index.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { ErrorBoundary } from "react-error-boundary";
import { App } from "./App";

const queryClient = new QueryClient();

function RootFallback({ error }: { error: unknown }) {
  const message = error instanceof Error ? error.message : String(error);
  return (
    <div role="alert" className="p-6 max-w-lg mx-auto mt-12 space-y-2">
      <h1 className="text-lg font-semibold">Terjadi kesalahan sistem</h1>
      <p className="text-sm text-muted-foreground">
        Aplikasi mengalami kendala. Coba muat ulang halaman.
      </p>
      <pre className="text-xs bg-muted p-2 rounded overflow-auto">{message}</pre>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary FallbackComponent={RootFallback}>
      <QueryClientProvider client={queryClient}>
        <App />
        {(import.meta as ImportMeta & { env?: { DEV?: boolean } }).env?.DEV ? (
          <ReactQueryDevtools initialIsOpen={false} />
        ) : null}
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>,
);

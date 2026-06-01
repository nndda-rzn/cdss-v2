import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { EcgUploadForm } from "../components/EcgUploadForm";

function renderWithClient(ui: React.ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("EcgUploadForm", () => {
  it("rejects non-image files client-side", async () => {
    // applyAccept: false lets the text/plain file reach the dropzone input so
    // react-dropzone's own accept-filter rejects it (onDropRejected path).
    const user = userEvent.setup({ applyAccept: false });
    renderWithClient(<EcgUploadForm encounterId="1" />);
    const input = screen.getByLabelText(/pilih berkas/i) as HTMLInputElement;
    const bad = new File(["x"], "note.txt", { type: "text/plain" });
    await user.upload(input, bad);
    // Dropzone rejects non-JPEG/PNG before the component's own validation runs.
    expect(await screen.findByText(/ditolak|format harus jpeg atau png/i)).toBeInTheDocument();
  });
});

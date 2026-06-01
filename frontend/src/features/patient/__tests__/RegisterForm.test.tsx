import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { RegisterForm } from "../components/RegisterForm";

vi.mock("../api", () => ({
  registerPatient: vi.fn(),
  patientKeys: { all: ["patients"] },
}));
import { registerPatient } from "../api";

function renderForm() {
  return render(
    <MemoryRouter>
      <RegisterForm />
    </MemoryRouter>,
  );
}

describe("RegisterForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders required fields", () => {
    renderForm();
    expect(screen.getByLabelText(/nama lengkap/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tanggal lahir/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/nik/i)).toBeInTheDocument();
  });

  it("rejects a 15-digit NIK", async () => {
    const user = userEvent.setup();
    renderForm();
    await user.type(screen.getByLabelText(/nama lengkap/i), "Budi Santoso");
    await user.type(screen.getByLabelText(/tanggal lahir/i), "1965-03-12");
    await user.type(screen.getByLabelText(/^nik/i), "320112345678000");
    await user.click(screen.getByLabelText(/pasien menyetujui penggunaan data/i));
    await user.click(screen.getByRole("button", { name: /daftar/i }));
    expect(await screen.findByText(/nik harus 16 digit/i)).toBeInTheDocument();
    expect(registerPatient).not.toHaveBeenCalled();
  });

  it("blocks submit when consent is unchecked", async () => {
    const user = userEvent.setup();
    renderForm();
    await user.type(screen.getByLabelText(/nama lengkap/i), "Budi Santoso");
    await user.type(screen.getByLabelText(/tanggal lahir/i), "1965-03-12");
    await user.click(screen.getByRole("button", { name: /daftar/i }));
    expect(await screen.findByText(/persetujuan penggunaan data wajib/i)).toBeInTheDocument();
    expect(registerPatient).not.toHaveBeenCalled();
  });

  it("shows duplicate dialog when server returns suggestions", async () => {
    vi.mocked(registerPatient).mockResolvedValueOnce({
      action: "confirm",
      duplicates: [
        {
          id: "abc",
          mrn: "MRN-P1-000001",
          name_masked: "B*** S******",
          dob: "1965-03-12",
          gender: "male",
        },
      ],
    });
    const user = userEvent.setup();
    renderForm();
    await user.type(screen.getByLabelText(/nama lengkap/i), "Budi Santoso");
    await user.type(screen.getByLabelText(/tanggal lahir/i), "1965-03-12");
    await user.click(screen.getByLabelText(/pasien menyetujui penggunaan data/i));
    await user.click(screen.getByRole("button", { name: /daftar/i }));
    expect(await screen.findByText(/pasien serupa ditemukan/i)).toBeInTheDocument();
  });
});

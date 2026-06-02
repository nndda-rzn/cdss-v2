import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "../components/LoginForm";

vi.mock("../api", () => ({ login: vi.fn(async () => ({ role: "admin" })) }));
import { login } from "../api";

const PASSWORD_LABEL = /kata sandi|password/i;

describe("LoginForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders email and password fields", () => {
    render(<LoginForm onSuccess={() => {}} />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(PASSWORD_LABEL)).toBeInTheDocument();
  });

  it("calls login on submit", async () => {
    const onSuccess = vi.fn();
    render(<LoginForm onSuccess={onSuccess} />);
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "a@x.id" },
    });
    fireEvent.change(screen.getByLabelText(PASSWORD_LABEL), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByRole("button", { name: /masuk|sign in/i }));
    await waitFor(() =>
      expect(login).toHaveBeenCalledWith({ email: "a@x.id", password: "secret" }),
    );
    await waitFor(() => expect(onSuccess).toHaveBeenCalled());
  });

  it("shows validation error for invalid email", async () => {
    const user = userEvent.setup();
    render(<LoginForm onSuccess={vi.fn()} />);
    await user.type(screen.getByLabelText(/email/i), "not-an-email");
    await user.type(screen.getByLabelText(PASSWORD_LABEL), "pass");
    await user.click(screen.getByRole("button", { name: /masuk|sign in/i }));
    expect(await screen.findByText(/email tidak valid/i)).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });
});

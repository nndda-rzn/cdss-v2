import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { LoginForm } from "./LoginForm";

vi.mock("./api", () => ({ login: vi.fn(async () => undefined) }));
import { login } from "./api";

describe("LoginForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders email and password fields", () => {
    render(<LoginForm onSuccess={() => {}} />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });

  it("calls login on submit", async () => {
    const onSuccess = vi.fn();
    render(<LoginForm onSuccess={onSuccess} />);
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "a@x.id" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "secret" },
    });
    fireEvent.click(screen.getByRole("button", { name: /masuk|login/i }));
    await waitFor(() =>
      expect(login).toHaveBeenCalledWith({ email: "a@x.id", password: "secret" }),
    );
    await waitFor(() => expect(onSuccess).toHaveBeenCalled());
  });
});

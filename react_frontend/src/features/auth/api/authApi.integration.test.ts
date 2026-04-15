import { HttpResponse, http as mswHttp } from "msw";

import { normalizeApiError } from "@/shared/lib/apiError";
import { env } from "@/shared/lib/env";
import { server } from "@/test/setup";

import { registerParty } from "./authApi";

describe("auth api integration", () => {
  it("submits party registration and returns detail", async () => {
    server.use(
      mswHttp.post(`${env.apiBaseUrl}/accounts/auth/register/party/`, async ({ request }) => {
        const body = (await request.json()) as { email?: string };
        if (!body.email) {
          return HttpResponse.json({ detail: "Email is required." }, { status: 400 });
        }
        return HttpResponse.json({ detail: "Registration successful." }, { status: 201 });
      }),
    );

    const response = await registerParty({
      email: "party@example.com",
      password: "Password@123",
      first_name: "Party",
      last_name: "User",
      phone_number: "9876543210",
      date_of_birth: "1995-01-01",
      address: "Address one",
      gender: "U",
    });

    expect(response.detail).toBe("Registration successful.");
  });

  it("normalizes registration API error payload", async () => {
    server.use(
      mswHttp.post(`${env.apiBaseUrl}/accounts/auth/register/party/`, () => {
        return HttpResponse.json({ email: ["A user with this email already exists."] }, { status: 400 });
      }),
    );

    try {
      await registerParty({
        email: "party@example.com",
        password: "Password@123",
        first_name: "Party",
        last_name: "User",
        phone_number: "9876543210",
        date_of_birth: "1995-01-01",
        address: "Address one",
        gender: "U",
      });
      throw new Error("Expected registration to fail");
    } catch (error) {
      const message = normalizeApiError(error, "Registration failed.");
      expect(message).toContain("A user with this email already exists.");
    }
  });
});

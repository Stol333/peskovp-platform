import { timingSafeEqual } from "node:crypto";

import { forbidden, unauthorized } from "@/src/lib/api-response";

function safeCompare(leftRaw: string, rightRaw: string) {
  const left = Buffer.from(leftRaw, "utf8");
  const right = Buffer.from(rightRaw, "utf8");
  if (left.length !== right.length) {
    return false;
  }
  return timingSafeEqual(left, right);
}

function extractAdminToken(request: Request) {
  const authorization = request.headers.get("authorization");
  if (authorization) {
    const [scheme, token] = authorization.trim().split(/\s+/, 2);
    if (scheme?.toLowerCase() === "bearer" && token) {
      return token.trim();
    }
  }
  return request.headers.get("x-admin-auth-token")?.trim() ?? "";
}

export function requireAdminApiAccess(request: Request) {
  const expectedToken = process.env.ADMIN_API_AUTH_TOKEN?.trim();
  if (!expectedToken) {
    return {
      ok: false as const,
      response: unauthorized("Admin API auth is not configured")
    };
  }

  const providedToken = extractAdminToken(request);
  if (!providedToken || !safeCompare(providedToken, expectedToken)) {
    return {
      ok: false as const,
      response: unauthorized("Invalid admin credentials")
    };
  }

  const role = request.headers.get("x-admin-role")?.trim().toLowerCase();
  if (role !== "admin") {
    return {
      ok: false as const,
      response: forbidden("Admin role required")
    };
  }

  return { ok: true as const };
}

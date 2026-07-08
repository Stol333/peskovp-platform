import { NextResponse } from "next/server";

type JsonPayload = Record<string, unknown>;

function json(payload: JsonPayload, status: number, headers?: HeadersInit) {
  return NextResponse.json(payload, {
    status,
    ...(headers ? { headers } : {})
  });
}

export function ok<T extends JsonPayload>(payload: T, status = 200) {
  return json(payload, status);
}

export function badRequest(message: string) {
  return json({ ok: false, error: message }, 400);
}

export function unauthorized(message = "Unauthorized") {
  return json({ ok: false, error: message }, 401);
}
export function forbidden(message = "Forbidden") {
  return json({ ok: false, error: message }, 403);
}

export function conflict(message: string) {
  return json({ ok: false, error: message }, 409);
}

export function serviceUnavailable(message: string) {
  return json({ ok: false, error: message }, 503);
}

export function tooManyRequests(message: string, retryAfterSeconds: number) {
  const safeRetry = Number.isFinite(retryAfterSeconds) && retryAfterSeconds > 0 ? Math.ceil(retryAfterSeconds) : 1;
  return json(
    {
      ok: false,
      error: message,
      retryAfterSeconds: safeRetry
    },
    429,
    { "Retry-After": String(safeRetry) }
  );
}

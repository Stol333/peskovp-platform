import { ok } from "@/src/lib/api-response";

export async function GET() {
  return ok({
    ok: true,
    service: "web",
    endpoint: "health",
    status: "healthy"
  });
}

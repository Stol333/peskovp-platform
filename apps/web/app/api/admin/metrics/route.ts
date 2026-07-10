import { ok } from "@/src/lib/api-response";
import { requireAdminApiAccess } from "@/src/lib/admin-auth";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET(request: Request) {
  const access = requireAdminApiAccess(request);
  if (!access.ok) {
    return access.response;
  }
  return ok({
    ok: true,
    metrics: {
      users: 0,
      activeSubscriptions: 0,
      canaryPercent: 0
    }
  }, 200, { "Cache-Control": "no-store" });
}

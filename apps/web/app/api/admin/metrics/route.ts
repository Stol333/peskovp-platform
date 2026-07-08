import { ok } from "@/src/lib/api-response";
import { requireAdminApiAccess } from "@/src/lib/admin-auth";

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
  });
}

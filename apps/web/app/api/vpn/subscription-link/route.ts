import { ok } from "@/src/lib/api-response";

export async function GET() {
  return ok({
    ok: true,
    link: "masked://subscription-link",
    qrAvailable: true
  });
}

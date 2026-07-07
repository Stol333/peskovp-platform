import { badRequest, conflict, ok } from "@/src/lib/api-response";
import { getPaymentService, resolvePaymentProvider } from "@/src/lib/payment-service";

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as
    | { userId?: string; planId?: string; amount?: number; currency?: string; provider?: string; idempotencyKey?: string }
    | null;
  const amount = typeof body?.amount === "number" ? body.amount : Number.NaN;
  if (!body?.userId || !body?.planId || !body?.currency || !Number.isFinite(amount) || amount <= 0) {
    return badRequest("userId, planId, amount, currency are required and amount must be > 0");
  }
  const idempotencyKey = request.headers.get("x-idempotency-key")?.trim() || body.idempotencyKey?.trim();
  if (!idempotencyKey) {
    return badRequest("x-idempotency-key header is required");
  }

  const paymentService = getPaymentService();
  const result = paymentService.createIntent({
    userId: body.userId,
    planId: body.planId,
    orderId: `ord_${body.userId}_${body.planId}`,
    amount,
    currency: body.currency.toUpperCase(),
    provider: resolvePaymentProvider(body.provider),
    idempotencyKey
  });

  if (result.idempotencyStatus === "conflict") {
    return conflict("idempotency key conflict");
  }
  if (!result.ok || !result.payment) {
    return badRequest(result.error ?? "unable to create payment intent");
  }

  return ok({
    ok: true,
    paymentId: result.payment.paymentId,
    provider: result.payment.provider,
    paymentStatus: result.payment.status,
    idempotencyStatus: result.idempotencyStatus,
    confirmationUrl: result.confirmationUrl ?? null
  }, result.idempotencyStatus === "new" ? 201 : 200);
}

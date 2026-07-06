import { badRequest, conflict, ok, serviceUnavailable, unauthorized } from "@/src/lib/api-response";
import { getPaymentService } from "@/src/lib/payment-service";
import type { PaymentStatus } from "@peskovp/payments";
import { verifyHmacSha256Signature, verifySharedSecret } from "@peskovp/payments";

interface ParsedYooKassaWebhook {
  eventId: string;
  paymentId: string;
  status: PaymentStatus;
  providerChargeId?: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object";
}

function parseJson(raw: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(raw);
    return isRecord(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function asPaymentStatus(value: unknown): PaymentStatus | null {
  if (typeof value !== "string") {
    return null;
  }
  switch (value) {
    case "created":
    case "pending":
    case "succeeded":
    case "canceled":
    case "refunded":
    case "failed":
      return value;
    case "waiting_for_capture":
      return "pending";
    case "cancelled":
      return "canceled";
    default:
      return null;
  }
}

function parseYookassaPayload(payload: Record<string, unknown>): ParsedYooKassaWebhook | null {
  const objectCandidate = payload.object;
  const object = isRecord(objectCandidate) ? objectCandidate : null;
  const metadataCandidate = object ? object.metadata : undefined;
  const metadata = isRecord(metadataCandidate) ? metadataCandidate : null;

  const paymentIdFromMetadata = typeof metadata?.paymentId === "string" ? metadata.paymentId : null;
  const directPaymentId = typeof payload.paymentId === "string" ? payload.paymentId : null;
  const paymentId = paymentIdFromMetadata ?? directPaymentId;

  const providerChargeId = typeof object?.id === "string" ? object.id : undefined;
  const status = asPaymentStatus(object?.status ?? payload.status);
  const eventName = typeof payload.event === "string" ? payload.event : "yookassa.event";
  const eventId =
    providerChargeId ? `${eventName}:${providerChargeId}` : typeof payload.eventId === "string" ? payload.eventId : null;

  if (!paymentId || !status || !eventId) {
    return null;
  }

  return {
    eventId,
    paymentId,
    status,
    ...(providerChargeId ? { providerChargeId } : {})
  };
}

export async function POST(request: Request) {
  const webhookSecret = process.env.PAYMENTS_YOOKASSA_WEBHOOK_SECRET?.trim();
  if (!webhookSecret) {
    return serviceUnavailable("YooKassa webhook is not configured");
  }

  const rawBody = await request.text();
  const sharedSecretHeader = request.headers.get("x-yookassa-webhook-secret");
  const signatureHeader = request.headers.get("x-yookassa-signature");
  const hasValidSharedSecret = verifySharedSecret(sharedSecretHeader, webhookSecret);
  const hasValidHmacSignature = verifyHmacSha256Signature(rawBody, signatureHeader, webhookSecret);
  if (!hasValidSharedSecret && !hasValidHmacSignature) {
    return unauthorized("Invalid YooKassa webhook signature");
  }

  const payload = parseJson(rawBody);
  if (!payload) {
    return badRequest("Invalid YooKassa webhook payload");
  }

  const parsed = parseYookassaPayload(payload);
  if (!parsed) {
    return badRequest("Unable to extract payment event from YooKassa payload");
  }

  const idempotencyKey = request.headers.get("x-idempotency-key")?.trim() || parsed.eventId;
  if (!idempotencyKey) {
    return badRequest("idempotency key is required");
  }

  const result = getPaymentService().processWebhook({
    provider: "yookassa",
    idempotencyKey,
    update: {
      eventId: parsed.eventId,
      paymentId: parsed.paymentId,
      status: parsed.status,
      ...(parsed.providerChargeId ? { providerChargeId: parsed.providerChargeId } : {}),
      rawPayload: payload
    }
  });

  if (result.idempotencyStatus === "conflict") {
    return conflict("idempotency key conflict");
  }
  if (!result.ok || !result.payment) {
    return badRequest(result.error ?? "unable to process YooKassa webhook");
  }
  return ok({
    ok: true,
    provider: "yookassa",
    processed: true,
    paymentId: result.payment.paymentId,
    paymentStatus: result.payment.status,
    idempotencyStatus: result.idempotencyStatus,
    subscriptionActivation: result.subscriptionActivation ?? null
  });
}

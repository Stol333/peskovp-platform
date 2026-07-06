import { badRequest, conflict, ok, serviceUnavailable, unauthorized } from "@/src/lib/api-response";
import { getPaymentService } from "@/src/lib/payment-service";
import type { PaymentStatus } from "@peskovp/payments";
import { verifySharedSecret } from "@peskovp/payments";

interface ParsedTelegramWebhook {
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
    case "successful":
      return "succeeded";
    case "cancelled":
      return "canceled";
    default:
      return null;
  }
}

function parseTelegramPayload(payload: Record<string, unknown>): ParsedTelegramWebhook | null {
  const directPaymentId = typeof payload.paymentId === "string" ? payload.paymentId : null;
  const directStatus = asPaymentStatus(payload.status);
  const directEventId = typeof payload.eventId === "string" ? payload.eventId : null;
  const directChargeId = typeof payload.telegramChargeId === "string" ? payload.telegramChargeId : undefined;
  if (directPaymentId && directStatus && directEventId) {
    return {
      eventId: directEventId,
      paymentId: directPaymentId,
      status: directStatus,
      ...(directChargeId ? { providerChargeId: directChargeId } : {})
    };
  }

  const messageCandidate = payload.message;
  const message = isRecord(messageCandidate) ? messageCandidate : null;
  const successfulPaymentCandidate = message ? message.successful_payment : undefined;
  const successfulPayment = isRecord(successfulPaymentCandidate) ? successfulPaymentCandidate : null;
  const invoicePayload = typeof successfulPayment?.invoice_payload === "string" ? successfulPayment.invoice_payload : null;
  const chargeId = typeof successfulPayment?.telegram_payment_charge_id === "string" ? successfulPayment.telegram_payment_charge_id : undefined;
  const updateId = typeof payload.update_id === "number" ? String(payload.update_id) : null;

  if (invoicePayload && updateId) {
    return {
      eventId: `telegram-update:${updateId}`,
      paymentId: invoicePayload,
      status: "succeeded",
      ...(chargeId ? { providerChargeId: chargeId } : {})
    };
  }

  const preCheckoutCandidate = payload.pre_checkout_query;
  const preCheckout = isRecord(preCheckoutCandidate) ? preCheckoutCandidate : null;
  const preCheckoutInvoicePayload =
    preCheckout && typeof preCheckout.invoice_payload === "string" ? preCheckout.invoice_payload : null;
  const preCheckoutId = preCheckout && typeof preCheckout.id === "string" ? preCheckout.id : null;
  if (preCheckoutInvoicePayload && preCheckoutId) {
    return {
      eventId: `telegram-precheckout:${preCheckoutId}`,
      paymentId: preCheckoutInvoicePayload,
      status: "pending"
    };
  }

  return null;
}

export async function POST(request: Request) {
  const webhookSecret = process.env.PAYMENTS_TELEGRAM_WEBHOOK_SECRET?.trim();
  if (!webhookSecret) {
    return serviceUnavailable("Telegram payments webhook is not configured");
  }
  const incomingSecret = request.headers.get("x-payments-webhook-secret");
  if (!verifySharedSecret(incomingSecret, webhookSecret)) {
    return unauthorized("Invalid Telegram payments webhook secret");
  }

  const rawBody = await request.text();
  const payload = parseJson(rawBody);
  if (!payload) {
    return badRequest("Invalid Telegram payments payload");
  }

  const parsed = parseTelegramPayload(payload);
  if (!parsed) {
    return badRequest("Unable to extract payment event from Telegram payload");
  }

  const idempotencyKey = request.headers.get("x-idempotency-key")?.trim() || parsed.eventId;
  if (!idempotencyKey) {
    return badRequest("idempotency key is required");
  }

  const result = getPaymentService().processWebhook({
    provider: "telegram_stars",
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
    return badRequest(result.error ?? "unable to process Telegram payment webhook");
  }
  return ok({
    ok: true,
    provider: "telegram_stars",
    processed: true,
    paymentId: result.payment.paymentId,
    paymentStatus: result.payment.status,
    idempotencyStatus: result.idempotencyStatus,
    subscriptionActivation: result.subscriptionActivation ?? null
  });
}

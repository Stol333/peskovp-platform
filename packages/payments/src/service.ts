import { randomUUID } from "node:crypto";
import { InMemoryIdempotencyStore } from "./idempotency.js";
import { buildManualConfirmationUrl } from "./manual-provider.js";
import { canTransitionPaymentStatus } from "./state-machine.js";
import type {
  CreatePaymentIntentInput,
  IdempotencyStatus,
  PaymentIntentResult,
  PaymentRecord,
  PaymentServiceOptions,
  PaymentWebhookResult,
  ProcessPaymentWebhookInput
} from "./types.js";

function nowIso() {
  return new Date().toISOString();
}

function toIntentFingerprint(input: CreatePaymentIntentInput) {
  return JSON.stringify({
    orderId: input.orderId,
    userId: input.userId,
    planId: input.planId,
    amount: input.amount,
    currency: input.currency,
    provider: input.provider
  });
}

function toWebhookFingerprint(input: ProcessPaymentWebhookInput) {
  return JSON.stringify({
    provider: input.provider,
    eventId: input.update.eventId,
    paymentId: input.update.paymentId,
    status: input.update.status,
    providerChargeId: input.update.providerChargeId
  });
}

function withIdempotencyStatus<T extends object>(
  value: T,
  idempotencyStatus: IdempotencyStatus
): T & { idempotencyStatus: IdempotencyStatus } {
  return {
    ...value,
    idempotencyStatus
  };
}

export class PaymentService {
  private readonly payments = new Map<string, PaymentRecord>();
  private readonly intentStore = new InMemoryIdempotencyStore<Omit<PaymentIntentResult, "idempotencyStatus">>();
  private readonly webhookStore = new InMemoryIdempotencyStore<Omit<PaymentWebhookResult, "idempotencyStatus">>();
  private readonly options: PaymentServiceOptions;

  constructor(options?: PaymentServiceOptions) {
    this.options = options ?? {};
  }

  createIntent(input: CreatePaymentIntentInput): PaymentIntentResult {
    const fingerprint = toIntentFingerprint(input);
    const execution = this.intentStore.execute(input.idempotencyKey, fingerprint, () => {
      const createdAt = nowIso();
      const paymentId = `pay_${randomUUID().replace(/-/g, "").slice(0, 24)}`;
      const payment: PaymentRecord = {
        paymentId,
        orderId: input.orderId,
        userId: input.userId,
        planId: input.planId,
        provider: input.provider,
        amount: input.amount,
        currency: input.currency.toUpperCase(),
        status: "created",
        idempotencyKey: input.idempotencyKey,
        createdAtIso: createdAt,
        updatedAtIso: createdAt
      };
      this.payments.set(payment.paymentId, payment);
      this.emitAudit({
        event: "payment_intent_created",
        provider: payment.provider,
        paymentId: payment.paymentId,
        status: payment.status,
        idempotencyStatus: "new"
      });
      return {
        ok: true,
        payment,
        confirmationUrl: buildManualConfirmationUrl(payment.paymentId)
      };
    });

    if (execution.kind === "conflict") {
      return {
        ok: false,
        idempotencyStatus: "conflict",
        error: "idempotency_key_conflict"
      };
    }

    const idempotencyStatus: IdempotencyStatus = execution.kind === "new" ? "new" : "replay";
    return withIdempotencyStatus(execution.value, idempotencyStatus);
  }

  processWebhook(input: ProcessPaymentWebhookInput): PaymentWebhookResult {
    const fingerprint = toWebhookFingerprint(input);
    const execution = this.webhookStore.execute(input.idempotencyKey, fingerprint, () => {
      const current = this.payments.get(input.update.paymentId);
      if (!current) {
        return {
          ok: false,
          error: "payment_not_found"
        };
      }
      if (current.provider !== input.provider) {
        return {
          ok: false,
          error: "provider_mismatch"
        };
      }
      if (!canTransitionPaymentStatus(current.status, input.update.status)) {
        return {
          ok: false,
          error: `invalid_status_transition:${current.status}->${input.update.status}`
        };
      }

      const updated: PaymentRecord = {
        ...current,
        status: input.update.status,
        updatedAtIso: nowIso(),
        ...(input.update.providerChargeId !== undefined ? { providerChargeId: input.update.providerChargeId } : {})
      };

      let subscriptionActivation: PaymentWebhookResult["subscriptionActivation"] | undefined;
      if (updated.status === "succeeded") {
        const subscriptionId = this.options.activateSubscription?.(updated) ?? `sub_${updated.paymentId}`;
        if (subscriptionId !== null) {
          updated.subscriptionId = subscriptionId;
        } else {
          delete updated.subscriptionId;
        }
        subscriptionActivation = {
          activated: subscriptionId !== null,
          subscriptionId
        };
      }

      this.payments.set(updated.paymentId, updated);
      this.emitAudit({
        event: "payment_webhook_processed",
        provider: updated.provider,
        paymentId: updated.paymentId,
        status: updated.status,
        idempotencyStatus: "new",
        eventId: input.update.eventId
      });
      return {
        ok: true,
        payment: updated,
        ...(subscriptionActivation !== undefined ? { subscriptionActivation } : {})
      };
    });

    if (execution.kind === "conflict") {
      return {
        ok: false,
        idempotencyStatus: "conflict",
        error: "idempotency_key_conflict"
      };
    }

    const idempotencyStatus: IdempotencyStatus = execution.kind === "new" ? "new" : "replay";
    return withIdempotencyStatus(execution.value, idempotencyStatus);
  }

  getPayment(paymentId: string) {
    return this.payments.get(paymentId);
  }

  private emitAudit(event: {
    event: "payment_intent_created" | "payment_webhook_processed";
    provider: PaymentRecord["provider"];
    paymentId: string;
    status: PaymentRecord["status"];
    idempotencyStatus: IdempotencyStatus;
    eventId?: string;
  }) {
    this.options.onAuditEvent?.(event);
  }
}

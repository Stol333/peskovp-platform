export type PaymentProviderName = "manual" | "telegram_stars" | "yookassa" | "cloudpayments";

export type PaymentStatus = "created" | "pending" | "succeeded" | "canceled" | "refunded" | "failed";

export type IdempotencyStatus = "new" | "replay" | "conflict";

export interface PaymentRecord {
  paymentId: string;
  orderId: string;
  userId: string;
  planId: string;
  provider: PaymentProviderName;
  amount: number;
  currency: string;
  status: PaymentStatus;
  idempotencyKey: string;
  providerChargeId?: string;
  createdAtIso: string;
  updatedAtIso: string;
  subscriptionId?: string;
}

export interface CreatePaymentIntentInput {
  orderId: string;
  userId: string;
  planId: string;
  amount: number;
  currency: string;
  provider: PaymentProviderName;
  idempotencyKey: string;
}

export interface PaymentIntentResult {
  ok: boolean;
  idempotencyStatus: IdempotencyStatus;
  payment?: PaymentRecord;
  confirmationUrl?: string;
  error?: string;
}

export interface ProcessPaymentWebhookInput {
  provider: PaymentProviderName;
  idempotencyKey: string;
  update: {
    eventId: string;
    paymentId: string;
    status: PaymentStatus;
    providerChargeId?: string;
    rawPayload: unknown;
  };
}

export interface PaymentWebhookResult {
  ok: boolean;
  idempotencyStatus: IdempotencyStatus;
  payment?: PaymentRecord;
  subscriptionActivation?: {
    activated: boolean;
    subscriptionId: string | null;
  };
  error?: string;
}

export interface PaymentAuditEvent {
  event: "payment_intent_created" | "payment_webhook_processed";
  provider: PaymentProviderName;
  paymentId: string;
  status: PaymentStatus;
  idempotencyStatus: IdempotencyStatus;
  eventId?: string;
}

export interface PaymentServiceOptions {
  onAuditEvent?: (event: PaymentAuditEvent) => void;
  activateSubscription?: (payment: PaymentRecord) => string | null;
}

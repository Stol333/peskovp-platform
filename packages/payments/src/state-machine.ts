import type { PaymentStatus } from "./types.js";

const ALLOWED_TRANSITIONS: Record<PaymentStatus, PaymentStatus[]> = {
  created: ["pending", "succeeded", "canceled", "failed"],
  pending: ["succeeded", "canceled", "failed", "refunded"],
  succeeded: ["refunded"],
  canceled: [],
  refunded: [],
  failed: []
};

export function canTransitionPaymentStatus(from: PaymentStatus, to: PaymentStatus) {
  if (from === to) {
    return true;
  }
  return ALLOWED_TRANSITIONS[from].includes(to);
}

export function getAllowedTransitions(from: PaymentStatus) {
  return [...ALLOWED_TRANSITIONS[from]];
}

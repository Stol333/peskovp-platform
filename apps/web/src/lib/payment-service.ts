import { PaymentService, type PaymentAuditEvent, type PaymentProviderName } from "@peskovp/payments";

const KNOWN_PAYMENT_PROVIDERS = new Set<PaymentProviderName>(["manual", "telegram_stars", "yookassa", "cloudpayments"]);

const globalState = globalThis as typeof globalThis & {
  __peskovpPaymentService?: PaymentService;
};

function createPaymentService() {
  return new PaymentService({
    onAuditEvent(event: PaymentAuditEvent) {
      console.info("payments.audit", JSON.stringify(event));
    }
  });
}

export function getPaymentService() {
  if (!globalState.__peskovpPaymentService) {
    globalState.__peskovpPaymentService = createPaymentService();
  }
  return globalState.__peskovpPaymentService;
}

export function resolvePaymentProvider(value: unknown): PaymentProviderName {
  if (typeof value === "string") {
    const normalized = value.trim().toLowerCase() as PaymentProviderName;
    if (KNOWN_PAYMENT_PROVIDERS.has(normalized)) {
      return normalized;
    }
  }
  const envProvider = process.env.PAYMENT_PROVIDER?.trim().toLowerCase() as PaymentProviderName | undefined;
  if (envProvider && KNOWN_PAYMENT_PROVIDERS.has(envProvider)) {
    return envProvider;
  }
  return "manual";
}

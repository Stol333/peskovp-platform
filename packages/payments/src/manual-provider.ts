export function buildManualConfirmationUrl(paymentId: string) {
  return `/dashboard/payments/${paymentId}`;
}

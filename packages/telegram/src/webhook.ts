import { timingSafeEqual } from "node:crypto";

export function verifyTelegramWebhookSecret(receivedSecret: string | null, expectedSecret: string | undefined) {
  const expected = expectedSecret?.trim();
  if (!expected) {
    return false;
  }
  if (!receivedSecret) {
    return false;
  }
  const left = Buffer.from(receivedSecret, "utf8");
  const right = Buffer.from(expected, "utf8");
  if (left.length !== right.length) {
    return false;
  }
  return timingSafeEqual(left, right);
}

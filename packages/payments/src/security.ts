import { createHmac, timingSafeEqual } from "node:crypto";

function safeCompareUtf8(leftRaw: string, rightRaw: string) {
  const left = Buffer.from(leftRaw, "utf8");
  const right = Buffer.from(rightRaw, "utf8");
  if (left.length !== right.length) {
    return false;
  }
  return timingSafeEqual(left, right);
}

function parseSignature(signatureRaw: string | null): Buffer | null {
  if (!signatureRaw) {
    return null;
  }
  const normalized = signatureRaw.trim().replace(/^sha256=/i, "");
  if (!normalized) {
    return null;
  }
  if (/^[0-9a-f]+$/i.test(normalized) && normalized.length % 2 === 0) {
    return Buffer.from(normalized, "hex");
  }
  return Buffer.from(normalized, "base64");
}

export function verifySharedSecret(receivedSecret: string | null, expectedSecret: string | undefined) {
  const expected = expectedSecret?.trim();
  if (!expected || !receivedSecret) {
    return false;
  }
  return safeCompareUtf8(receivedSecret, expected);
}

export function verifyHmacSha256Signature(payloadRaw: string, receivedSignature: string | null, secret: string | undefined) {
  const signingSecret = secret?.trim();
  if (!signingSecret || !receivedSignature) {
    return false;
  }
  const calculated = createHmac("sha256", signingSecret).update(payloadRaw).digest();
  const incoming = parseSignature(receivedSignature);
  if (!incoming || incoming.length !== calculated.length) {
    return false;
  }
  return timingSafeEqual(incoming, calculated);
}

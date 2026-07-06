import { createHmac, timingSafeEqual } from "node:crypto";
import type { TelegramInitDataValidationResult, TelegramWebAppUser, VerifyTelegramInitDataInput } from "./types.js";

const TELEGRAM_WEB_APP_SECRET = "WebAppData";
const DEFAULT_MAX_AGE_SECONDS = 300;
const CLOCK_SKEW_SECONDS = 30;

function isHexHash(value: string) {
  return /^[0-9a-f]{64}$/i.test(value);
}

function safeCompareHex(expectedHex: string, incomingHex: string): boolean {
  if (!isHexHash(expectedHex) || !isHexHash(incomingHex)) {
    return false;
  }
  const expected = Buffer.from(expectedHex, "hex");
  const incoming = Buffer.from(incomingHex, "hex");
  if (expected.length !== incoming.length) {
    return false;
  }
  return timingSafeEqual(expected, incoming);
}

function parseTelegramUser(rawUser: string | null): TelegramWebAppUser | undefined {
  if (!rawUser) {
    return undefined;
  }
  try {
    const parsed = JSON.parse(rawUser) as TelegramWebAppUser;
    if (typeof parsed.id !== "number") {
      return undefined;
    }
    return parsed;
  } catch {
    return undefined;
  }
}

export function buildDataCheckString(params: URLSearchParams) {
  return [...params.entries()]
    .filter(([key]) => key !== "hash")
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([key, value]) => `${key}=${value}`)
    .join("\n");
}

export function calculateTelegramInitDataHash(initData: string, botToken: string) {
  const params = new URLSearchParams(initData);
  const dataCheckString = buildDataCheckString(params);
  const secretKey = createHmac("sha256", TELEGRAM_WEB_APP_SECRET).update(botToken).digest();
  const calculatedHash = createHmac("sha256", secretKey).update(dataCheckString).digest("hex");
  return {
    params,
    dataCheckString,
    calculatedHash
  };
}

export function verifyTelegramInitData(input: VerifyTelegramInitDataInput): TelegramInitDataValidationResult {
  const botToken = input.botToken.trim();
  const initData = input.initData.trim();
  const maxAgeSeconds = input.maxAgeSeconds && input.maxAgeSeconds > 0 ? input.maxAgeSeconds : DEFAULT_MAX_AGE_SECONDS;
  const nowDate = input.now ?? new Date();
  const nowUnix = Math.floor(nowDate.getTime() / 1000);

  const { params, calculatedHash } = calculateTelegramInitDataHash(initData, botToken);
  const incomingHash = params.get("hash");
  if (!incomingHash) {
    return {
      isValid: false,
      reason: "missing_hash"
    };
  }
  if (!isHexHash(incomingHash)) {
    return {
      isValid: false,
      reason: "invalid_hash_format"
    };
  }
  if (!safeCompareHex(calculatedHash, incomingHash)) {
    return {
      isValid: false,
      reason: "invalid_signature"
    };
  }

  const authDateRaw = params.get("auth_date");
  if (!authDateRaw) {
    return {
      isValid: false,
      reason: "missing_auth_date"
    };
  }
  const authDateUnix = Number.parseInt(authDateRaw, 10);
  if (!Number.isFinite(authDateUnix) || authDateUnix <= 0) {
    return {
      isValid: false,
      reason: "invalid_auth_date"
    };
  }
  if (authDateUnix > nowUnix + CLOCK_SKEW_SECONDS) {
    return {
      isValid: false,
      reason: "future_auth_date"
    };
  }
  if (nowUnix - authDateUnix > maxAgeSeconds) {
    return {
      isValid: false,
      reason: "expired_auth_date"
    };
  }

  const authDateIso = new Date(authDateUnix * 1000).toISOString();
  const queryId = params.get("query_id");
  const user = parseTelegramUser(params.get("user"));
  return {
    isValid: true,
    authDateUnix,
    authDateIso,
    ...(queryId !== null ? { queryId } : {}),
    ...(user !== undefined ? { user } : {})
  };
}

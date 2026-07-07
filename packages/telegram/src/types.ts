export interface TelegramWebAppUser {
  id: number;
  is_bot?: boolean;
  first_name?: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  allows_write_to_pm?: boolean;
}

export type TelegramInitDataFailureReason =
  | "missing_hash"
  | "invalid_hash_format"
  | "missing_auth_date"
  | "invalid_auth_date"
  | "future_auth_date"
  | "expired_auth_date"
  | "invalid_signature";

export interface VerifyTelegramInitDataInput {
  initData: string;
  botToken: string;
  maxAgeSeconds?: number;
  now?: Date;
}

export interface TelegramInitDataValidationResult {
  isValid: boolean;
  reason?: TelegramInitDataFailureReason;
  user?: TelegramWebAppUser;
  queryId?: string;
  authDateUnix?: number;
  authDateIso?: string;
}

export interface SanitizedTelegramUser {
  idMasked: string;
  username?: string;
  languageCode?: string;
}

export interface RateLimiterOptions {
  limit: number;
  windowSeconds: number;
  maxKeys?: number;
}

export interface RateLimitDecision {
  allowed: boolean;
  remaining: number;
  retryAfterSeconds: number;
  limit: number;
  windowSeconds: number;
}

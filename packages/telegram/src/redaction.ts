import type { SanitizedTelegramUser, TelegramWebAppUser } from "./types.js";

function maskValue(value: string) {
  if (value.length <= 6) {
    return "***";
  }
  return `${value.slice(0, 3)}***${value.slice(-3)}`;
}

export function redactInitDataForLogs(initData: string) {
  const params = new URLSearchParams(initData);
  const redacted = new URLSearchParams(params);
  if (redacted.has("hash")) {
    redacted.set("hash", "***");
  }
  if (redacted.has("signature")) {
    redacted.set("signature", "***");
  }
  if (redacted.has("user")) {
    redacted.set("user", "***");
  }
  return redacted.toString();
}

export function sanitizeTelegramUser(user: TelegramWebAppUser | undefined): SanitizedTelegramUser | null {
  if (!user) {
    return null;
  }
  return {
    idMasked: maskValue(String(user.id)),
    ...(user.username !== undefined ? { username: user.username } : {}),
    ...(user.language_code !== undefined ? { languageCode: user.language_code } : {})
  };
}

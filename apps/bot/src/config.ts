import { z } from "zod";

export type BotRunMode = "polling" | "webhook";

export interface BotRuntimeConfig {
  botToken: string;
  miniAppUrl?: string;
  runMode: BotRunMode;
  webhookUrl?: string;
  webhookSecret?: string;
  rateLimitPerMinute: number;
}

const BOT_CONFIG_SCHEMA = z
  .object({
    TELEGRAM_BOT_TOKEN: z.string().min(10),
    TELEGRAM_MINI_APP_URL: z.string().url().optional(),
    BOT_RUN_MODE: z.enum(["polling", "webhook"]).default("polling"),
    TELEGRAM_WEBHOOK_URL: z.string().url().optional(),
    TELEGRAM_WEBHOOK_SECRET: z.string().min(8).optional(),
    TELEGRAM_BOT_RATE_LIMIT_PER_MINUTE: z.coerce.number().int().positive().default(30)
  })
  .superRefine((value, context) => {
    if (value.BOT_RUN_MODE === "webhook" && !value.TELEGRAM_WEBHOOK_URL) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: "TELEGRAM_WEBHOOK_URL is required when BOT_RUN_MODE=webhook"
      });
    }
    if (value.BOT_RUN_MODE === "webhook" && !value.TELEGRAM_WEBHOOK_SECRET) {
      context.addIssue({
        code: z.ZodIssueCode.custom,
        message: "TELEGRAM_WEBHOOK_SECRET is required when BOT_RUN_MODE=webhook"
      });
    }
  });

export type BotConfigLoadResult =
  | {
      ok: true;
      config: BotRuntimeConfig;
    }
  | {
      ok: false;
      errors: string[];
    };

export function loadBotRuntimeConfig(env: NodeJS.ProcessEnv = process.env): BotConfigLoadResult {
  const parsed = BOT_CONFIG_SCHEMA.safeParse(env);
  if (!parsed.success) {
    return {
      ok: false,
      errors: parsed.error.issues.map((issue) => issue.message)
    };
  }
  const config: BotRuntimeConfig = {
    botToken: parsed.data.TELEGRAM_BOT_TOKEN,
    runMode: parsed.data.BOT_RUN_MODE,
    rateLimitPerMinute: parsed.data.TELEGRAM_BOT_RATE_LIMIT_PER_MINUTE,
    ...(parsed.data.TELEGRAM_MINI_APP_URL ? { miniAppUrl: parsed.data.TELEGRAM_MINI_APP_URL } : {}),
    ...(parsed.data.TELEGRAM_WEBHOOK_URL ? { webhookUrl: parsed.data.TELEGRAM_WEBHOOK_URL } : {}),
    ...(parsed.data.TELEGRAM_WEBHOOK_SECRET ? { webhookSecret: parsed.data.TELEGRAM_WEBHOOK_SECRET } : {})
  };
  return {
    ok: true,
    config
  };
}

import { Bot } from "grammy";
import { registerCoreCommands } from "./commands.js";
import { loadBotRuntimeConfig } from "./config.js";
import { logBotEvent } from "./logger.js";

async function bootstrap() {
  const configResult = loadBotRuntimeConfig();
  if (!configResult.ok) {
    logBotEvent("error", "config.invalid", {
      errors: configResult.errors
    });
    process.exitCode = 1;
    return;
  }

  const config = configResult.config;
  const bot = new Bot(config.botToken);
  registerCoreCommands(bot, config);

  if (config.runMode === "webhook") {
    if (!config.webhookUrl || !config.webhookSecret) {
      logBotEvent("error", "config.webhook_fields_missing");
      process.exitCode = 1;
      return;
    }

    await bot.api.setWebhook(config.webhookUrl, {
      secret_token: config.webhookSecret
    });
    await bot.init();
    logBotEvent("info", "bot.webhook_mode_enabled", {
      webhookUrl: config.webhookUrl
    });
    return;
  }

  await bot.start({
    onStart: () => {
      logBotEvent("info", "bot.polling_started");
    }
  });
}

void bootstrap();

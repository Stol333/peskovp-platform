import type { RateLimitDecision, RateLimiterOptions } from "./types.js";

interface InternalBucket {
  hits: number;
  windowStartUnixMs: number;
}

const DEFAULT_MAX_KEYS = 20_000;

export class InMemoryRateLimiter {
  private readonly buckets = new Map<string, InternalBucket>();
  private readonly limit: number;
  private readonly windowSeconds: number;
  private readonly maxKeys: number;

  constructor(options: RateLimiterOptions) {
    this.limit = Math.max(1, Math.floor(options.limit));
    this.windowSeconds = Math.max(1, Math.floor(options.windowSeconds));
    this.maxKeys = Math.max(100, Math.floor(options.maxKeys ?? DEFAULT_MAX_KEYS));
  }

  consume(key: string, nowUnixMs = Date.now()): RateLimitDecision {
    this.pruneIfNeeded(nowUnixMs);
    const normalizedKey = key || "anonymous";
    const windowMs = this.windowSeconds * 1000;
    const existing = this.buckets.get(normalizedKey);
    if (!existing || nowUnixMs - existing.windowStartUnixMs >= windowMs) {
      this.buckets.set(normalizedKey, {
        hits: 1,
        windowStartUnixMs: nowUnixMs
      });
      return {
        allowed: true,
        remaining: this.limit - 1,
        retryAfterSeconds: 0,
        limit: this.limit,
        windowSeconds: this.windowSeconds
      };
    }

    existing.hits += 1;
    const remaining = this.limit - existing.hits;
    if (remaining >= 0) {
      return {
        allowed: true,
        remaining,
        retryAfterSeconds: 0,
        limit: this.limit,
        windowSeconds: this.windowSeconds
      };
    }

    const elapsedMs = nowUnixMs - existing.windowStartUnixMs;
    const retryAfterSeconds = Math.ceil((windowMs - elapsedMs) / 1000);
    return {
      allowed: false,
      remaining: 0,
      retryAfterSeconds: Math.max(1, retryAfterSeconds),
      limit: this.limit,
      windowSeconds: this.windowSeconds
    };
  }

  private pruneIfNeeded(nowUnixMs: number) {
    if (this.buckets.size <= this.maxKeys) {
      return;
    }
    const expirationCutoffMs = nowUnixMs - this.windowSeconds * 1000 * 2;
    for (const [key, bucket] of this.buckets.entries()) {
      if (bucket.windowStartUnixMs < expirationCutoffMs) {
        this.buckets.delete(key);
      }
      if (this.buckets.size <= this.maxKeys) {
        return;
      }
    }
  }
}

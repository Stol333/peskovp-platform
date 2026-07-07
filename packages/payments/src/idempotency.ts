export type IdempotencyExecution<T> =
  | {
      kind: "new";
      value: T;
    }
  | {
      kind: "replay";
      value: T;
    }
  | {
      kind: "conflict";
      value: null;
    };

interface StoredIdempotencyEntry<T> {
  fingerprint: string;
  value: T;
  createdAtUnixMs: number;
}

const DEFAULT_MAX_ENTRIES = 20_000;

export class InMemoryIdempotencyStore<T> {
  private readonly entries = new Map<string, StoredIdempotencyEntry<T>>();
  private readonly maxEntries: number;

  constructor(maxEntries = DEFAULT_MAX_ENTRIES) {
    this.maxEntries = Math.max(100, Math.floor(maxEntries));
  }

  execute(key: string, fingerprint: string, create: () => T): IdempotencyExecution<T> {
    if (!key) {
      const value = create();
      return {
        kind: "new",
        value
      };
    }

    const existing = this.entries.get(key);
    if (existing) {
      if (existing.fingerprint === fingerprint) {
        return {
          kind: "replay",
          value: existing.value
        };
      }
      return {
        kind: "conflict",
        value: null
      };
    }

    const value = create();
    this.entries.set(key, {
      fingerprint,
      value,
      createdAtUnixMs: Date.now()
    });
    this.pruneIfNeeded();
    return {
      kind: "new",
      value
    };
  }

  private pruneIfNeeded() {
    if (this.entries.size <= this.maxEntries) {
      return;
    }
    const sortedEntries = [...this.entries.entries()].sort((left, right) => left[1].createdAtUnixMs - right[1].createdAtUnixMs);
    const overflow = sortedEntries.length - this.maxEntries;
    for (let index = 0; index < overflow; index += 1) {
      const key = sortedEntries[index]?.[0];
      if (key) {
        this.entries.delete(key);
      }
    }
  }
}

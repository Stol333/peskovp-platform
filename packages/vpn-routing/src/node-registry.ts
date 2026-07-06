import { readFileSync } from "node:fs";
import type { NodeDescriptor, NodeRole } from "./types.js";

const VALID_ROLES: ReadonlySet<NodeRole> = new Set(["main", "rf", "backup"]);

export class NodeRegistry {
  private readonly nodes: NodeDescriptor[];
  private readonly index: Map<string, NodeDescriptor>;

  constructor(nodes: NodeDescriptor[]) {
    this.nodes = nodes;
    this.index = new Map(nodes.map((node) => [node.nodeId, node]));
    if (this.index.size !== this.nodes.length) {
      throw new Error("Duplicate nodeId detected in registry.");
    }
  }

  static fromObject(payload: unknown): NodeRegistry {
    if (!payload || typeof payload !== "object") {
      throw new Error("Registry payload must be an object.");
    }

    const maybeNodes = (payload as { nodes?: unknown }).nodes;
    if (!Array.isArray(maybeNodes)) {
      throw new Error("Registry payload must contain array field 'nodes'.");
    }

    const nodes = maybeNodes
      .map((raw) => NodeRegistry.parseNode(raw))
      .filter((node): node is NodeDescriptor => node !== null);

    return new NodeRegistry(nodes);
  }

  static fromJsonFile(path: string): NodeRegistry {
    const content = readFileSync(path, "utf8");
    return NodeRegistry.fromObject(JSON.parse(content) as unknown);
  }

  private static parseNode(raw: unknown): NodeDescriptor | null {
    if (!raw || typeof raw !== "object") {
      return null;
    }
    const item = raw as Record<string, unknown>;
    const nodeId = String(item.node_id ?? item.nodeId ?? "").trim();
    if (!nodeId) {
      throw new Error("nodeId/node_id is required for each node.");
    }

    const roleRaw = String(item.role ?? "backup").trim().toLowerCase();
    const role = VALID_ROLES.has(roleRaw as NodeRole) ? (roleRaw as NodeRole) : "backup";
    const region = String(item.region ?? "unknown").trim() || "unknown";
    const domain = String(item.domain ?? "").trim();
    const port = Number(item.port ?? 0);
    const transport = String(item.transport ?? "tcp").trim() || "tcp";
    const active = item.active === undefined ? true : Boolean(item.active);

    const rawHealth = item.health;
    let health: NodeDescriptor["health"];
    if (rawHealth && typeof rawHealth === "object") {
      const h = rawHealth as Record<string, unknown>;
      health = {
        latencyMs: Number(h.latency_ms ?? h.latencyMs ?? 0),
        errorRate: Number(h.error_rate ?? h.errorRate ?? 0),
        uptimeRatio: Number(h.uptime_ratio ?? h.uptimeRatio ?? 1),
        loadRatio: Number(h.load_ratio ?? h.loadRatio ?? 0),
        lastUpdatedUtc: String(h.last_updated_utc ?? h.lastUpdatedUtc ?? "")
      };
    }

    return {
      nodeId,
      role,
      region,
      domain,
      port,
      transport,
      active,
      ...(health !== undefined ? { health } : {})
    };
  }

  toObject(): { nodes: Array<Record<string, unknown>> } {
    return {
      nodes: this.nodes.map((node) => ({
        node_id: node.nodeId,
        role: node.role,
        region: node.region,
        domain: node.domain,
        port: node.port,
        transport: node.transport,
        active: node.active,
        health: node.health
          ? {
              latency_ms: node.health.latencyMs,
              error_rate: node.health.errorRate,
              uptime_ratio: node.health.uptimeRatio,
              load_ratio: node.health.loadRatio,
              last_updated_utc: node.health.lastUpdatedUtc
            }
          : undefined
      }))
    };
  }

  listNodes(): NodeDescriptor[] {
    return [...this.nodes];
  }

  getNode(nodeId: string): NodeDescriptor | undefined {
    return this.index.get(nodeId);
  }

  listActive(filters?: { role?: NodeRole; region?: string }): NodeDescriptor[] {
    return this.nodes.filter((node) => {
      if (!node.active) {
        return false;
      }
      if (filters?.role && node.role !== filters.role) {
        return false;
      }
      if (filters?.region && node.region !== filters.region) {
        return false;
      }
      return true;
    });
  }
}

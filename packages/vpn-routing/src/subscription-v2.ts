import type { CanaryDecision } from "./canary.js";
import type { SubscriptionProfile } from "./types.js";
type ProfileCatalog = {
  legacy: SubscriptionProfile;
  v2_auto: SubscriptionProfile;
  lte_safe: SubscriptionProfile;
  ru_direct: SubscriptionProfile;
  rf_gateway: SubscriptionProfile;
  v2_premium: SubscriptionProfile;
  canary: SubscriptionProfile;
};

export class SubscriptionProfileCatalog {
  private readonly profiles: ProfileCatalog = {
    legacy: {
      profileId: "legacy",
      displayName: "Legacy Stable",
      transports: ["vless_reality_main", "hy2_main"],
      includeLegacy: true,
      metadata: { tier: "stable" }
    },
    v2_auto: {
      profileId: "v2_auto",
      displayName: "V2 Auto",
      transports: ["vless_rf_tcp", "vless_rf_grpc", "vless_rf_xhttp"],
      includeLegacy: true,
      metadata: { tier: "v2" }
    },
    lte_safe: {
      profileId: "lte_safe",
      displayName: "LTE Safe",
      transports: ["vless_rf_tcp"],
      includeLegacy: true,
      metadata: { tier: "v2_safe" }
    },
    ru_direct: {
      profileId: "ru_direct",
      displayName: "RU Direct + Proxy Mix",
      transports: ["vless_rf_tcp", "vless_rf_grpc"],
      includeLegacy: true,
      directDomains: ["ru", "su", "xn--p1ai", "yandex.ru", "vk.com"],
      blockedProtocols: ["bittorrent"],
      metadata: { tier: "v2_policy" }
    },
    rf_gateway: {
      profileId: "rf_gateway",
      displayName: "RF Gateway",
      transports: ["vless_rf_tcp", "hy2_rf"],
      includeLegacy: false,
      metadata: { tier: "rf_only" }
    },
    v2_premium: {
      profileId: "v2_premium",
      displayName: "V2 Premium",
      transports: ["vless_rf_tcp", "vless_rf_grpc", "vless_rf_xhttp", "hy2_rf"],
      includeLegacy: true,
      metadata: { tier: "premium" }
    },
    canary: {
      profileId: "canary",
      displayName: "V2 Canary",
      transports: ["vless_rf_tcp", "vless_rf_grpc", "hy2_rf"],
      includeLegacy: true,
      blockedProtocols: ["bittorrent"],
      metadata: { tier: "canary" }
    }
  };

  get(profileId: string): SubscriptionProfile | undefined {
    if (profileId in this.profiles) {
      return this.profiles[profileId as keyof ProfileCatalog];
    }
    return undefined;
  }

  listAll(): SubscriptionProfile[] {
    return Object.values(this.profiles);
  }

  pickForDecision(decision: CanaryDecision): SubscriptionProfile[] {
    const legacy = this.profiles.legacy;
    if (decision.lane === "legacy") {
      return [legacy];
    }
    return [this.profiles.canary, this.profiles.v2_auto, this.profiles.lte_safe, this.profiles.ru_direct, this.profiles.v2_premium, legacy];
  }
}

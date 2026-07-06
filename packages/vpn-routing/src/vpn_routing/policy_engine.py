from __future__ import annotations

from dataclasses import dataclass

from .models import PolicyDecision


@dataclass(slots=True, frozen=True)
class PolicyConfig:
    direct_domain_suffixes: tuple[str, ...] = ("ru", "su", "xn--p1ai")
    direct_domains: tuple[str, ...] = ("yandex.ru", "vk.com", "avito.ru", "gosuslugi.ru")
    blocked_protocols: tuple[str, ...] = ("bittorrent",)
    blocked_udp_ports: tuple[int, ...] = (443,)


class RoutingPolicyEngine:
    def __init__(self, config: PolicyConfig | None = None) -> None:
        self._config = config or PolicyConfig()

    def decide(
        self,
        *,
        domain: str | None = None,
        protocol: str | None = None,
        transport: str | None = None,
        udp_port: int | None = None,
    ) -> PolicyDecision:
        normalized_domain = _normalize_domain(domain)
        normalized_protocol = str(protocol or "").strip().lower()
        normalized_transport = str(transport or "").strip().lower()

        if normalized_protocol in self._config.blocked_protocols:
            return PolicyDecision(lane="block", reason="Blocked protocol", matched_rule=normalized_protocol)

        if normalized_transport == "udp" and udp_port in self._config.blocked_udp_ports:
            return PolicyDecision(lane="block", reason="Blocked UDP port policy", matched_rule=f"udp:{udp_port}")

        if normalized_domain in self._config.direct_domains:
            return PolicyDecision(lane="direct", reason="Direct domain allowlist", matched_rule=normalized_domain)

        for suffix in self._config.direct_domain_suffixes:
            if normalized_domain.endswith(f".{suffix}") or normalized_domain == suffix:
                return PolicyDecision(lane="direct", reason="Direct suffix policy", matched_rule=suffix)

        return PolicyDecision(lane="proxy", reason="Default proxy lane", matched_rule=None)


def _normalize_domain(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().lower().rstrip(".")


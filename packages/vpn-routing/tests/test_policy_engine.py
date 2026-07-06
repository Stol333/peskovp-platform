from __future__ import annotations

from vpn_routing.policy_engine import RoutingPolicyEngine


def test_policy_direct_for_ru_domain() -> None:
    engine = RoutingPolicyEngine()
    decision = engine.decide(domain="video.yandex.ru", transport="tcp")
    assert decision.lane == "direct"


def test_policy_blocks_bittorrent_protocol() -> None:
    engine = RoutingPolicyEngine()
    decision = engine.decide(domain="example.org", protocol="bittorrent", transport="udp", udp_port=51413)
    assert decision.lane == "block"


def test_policy_default_proxy_lane() -> None:
    engine = RoutingPolicyEngine()
    decision = engine.decide(domain="example.com", transport="tcp")
    assert decision.lane == "proxy"


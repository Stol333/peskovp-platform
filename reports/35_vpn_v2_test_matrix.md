# 35 VPN V2 Test Matrix
## Scope
Валидация V2 routing/API contour и регрессия существующих модулей после выполнения V6 implementation steps.

## Команды
- Unit/regression:
  - `python -m pytest C:\Users\dgafa\packages\vpn-routing\tests C:\Users\dgafa\apps\api\tests C:\Users\dgafa\services\ai-module\tests C:\Users\dgafa\integrations\vpn\tests`
- Syntax/compile:
  - `python -m compileall C:\Users\dgafa\packages\vpn-routing\src C:\Users\dgafa\apps\api\src C:\Users\dgafa\services\ai-module\src C:\Users\dgafa\integrations\vpn\src`
- Canary distribution simulation:
  - `python -` (script using `CanaryRolloutManager`, 1000 synthetic users, rollout=5%).
- API V2 smoke-check:
  - `python -` (script calling `VPNV2Service.preview_subscription(...)`).

## Results
- Pytest summary:
  - `20 passed in 0.12s`.
- Compile summary:
  - `compileall` completed без ошибок.
- Canary cohort simulation:
  - `CANARY_V2=45`, `CANARY_LEGACY=955`, `CANARY_PERCENT_REAL=4.50`.
- API preview smoke:
  - `POLICY_LANE=direct`;
  - `CANARY_LANE=v2_canary`;
  - `PROFILE_COUNT=5`;
  - `PROFILES=canary,v2_auto,lte_safe,ru_direct,legacy`.

## Gate checks
- Routing module tests: `PASS`.
- API contour tests: `PASS`.
- Existing AI/VPN regressions: `PASS`.
- Syntax checks: `PASS`.
- Mass subscription switch: `NOT EXECUTED` (as required).

## Conclusion
Кодовый V2 baseline готов к controlled canary use-case, rollback-invariants соблюдены.


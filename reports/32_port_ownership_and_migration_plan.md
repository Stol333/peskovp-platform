# 32 Port Ownership and Migration Plan
## Цель
Определить контролируемую модель владения портами между MAIN и RF без поломки legacy-клиентов и сервисов панели/подписки.

## Current ownership (verified)
### MAIN (`91.202.0.193`)
- `22/tcp`: SSH (must keep).
- `80/tcp`, `443/tcp`: host nginx edge (must keep).
- `8443/tcp`: xray/x-ui inbound (legacy production).
- `443/udp`, `2443/udp`, `3443/udp`: HY2 services (legacy production).
- `127.0.0.1:10443`: xray loopback.
- `127.0.0.1:18080`: `peskovp-sub`.

### RF (`138.16.181.33`)
- `22/tcp`: SSH.
- VPN data-plane порты пока не заняты.

## Target ownership model
- MAIN:
  - остаётся control-plane + legacy edge;
  - не публикуем новые compose сервисы на public `80/443`;
  - не трогаем legacy inbound до завершения V2 canary.
- RF:
  - принимает V2 data-plane транспорта;
  - публикует только явно нужные canary порты;
  - домены `ru.peskovp.com` и `relay-ru.peskovp.com` закрепляются за RF.

## Candidate V2 ports on RF
- Stable first:
  - `443/tcp` (или альтернативный high TCP порт при конфликте) для VLESS Reality canary.
- Optional phased transports:
  - `8443/tcp` для gRPC/xHTTP canary.
  - `2443/udp` и/или `3443/udp` для HY2 canary (после отдельного тест-гейта).

## Migration phases
### Phase A — Canary only
- Добавить скрытый V2 subscription endpoint для admin/test users.
- Публиковать только RF canary профили.
- Legacy массовую подписку не менять.

### Phase B — Partial rollout
- Перевести `1% -> 5% -> 25%` новых пользователей на V2 profile preset.
- Существующих пользователей переводить только opt-in.
- На каждом шаге фиксировать success/error/rollback signal.

### Phase C — Controlled default
- V2 по умолчанию только для новых пользователей при стабильном SLO.
- Legacy профили остаются доступны как fallback.

### Phase D — Port reclaim
- Освобождение legacy-портов только после устойчивости V2.
- По одному порту за итерацию, с обязательным rollback window.

## Port-by-port migration matrix (text form)
- `MAIN 8443/tcp`:
  - current: legacy VLESS/x-ui.
  - target: keep until V2 stable.
  - method: no change in canary window.
  - rollback: N/A (unchanged).
- `MAIN 443/2443/3443 udp`:
  - current: legacy HY2 services.
  - target: gradual deprecation after V2 adoption.
  - method: disable one legacy exposure per step, monitor, then continue.
  - rollback: instant service re-enable + UFW rule restore.
- `RF 443/tcp`, `RF 8443/tcp`, `RF 2443/3443 udp`:
  - current: free for V2.
  - target: controlled canary exposure.
  - method: enable minimal set first, then extend.
  - rollback: close UFW rule + stop related service + DNS fallback if needed.

## Safety rules
- Любой шаг migration выполняется только после:
  - backup snapshot,
  - config syntax check,
  - smoke-check subscription profile,
  - rollback command rehearsal.
- Hard stop:
  - регрессия `panel/sub/legacy subscription`,
  - ошибка `nginx -t`/`xray -test`,
  - рост fail-rate выше canary threshold.


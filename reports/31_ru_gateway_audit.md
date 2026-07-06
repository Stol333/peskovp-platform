# 31 RU Gateway Audit (MAIN + RF, read-only)
## Scope
Read-only срез состояния MAIN (`91.202.0.193`) и RF gateway (`138.16.181.33`) перед V2 canary.

## Команды
- MAIN audit:
  - `C:\Windows\System32\OpenSSH\ssh.exe -i C:\Users\dgafa\.ssh\spain_new ... root@91.202.0.193 '<read-only bundle>'`
- RF audit:
  - `C:\Windows\System32\OpenSSH\ssh.exe -i C:\Users\dgafa\.ssh\id_ed25519_138_16_181_33_ru ... root@138.16.181.33 '<read-only bundle>'`
- DNS baseline:
  - `Resolve-DnsName` для `app/api/admin/panel/sub/www/ru/relay-ru`.

## MAIN: подтверждённое состояние
- Host: `peskovp-vpn-01`.
- OS: `Ubuntu 24.04.4 LTS`.
- Active services:
  - `nginx`, `x-ui`, `peskovp-sub`, `peskovp-hy2`, `peskovp-hy2-obfs`, `peskovp-hy2-advanced`, `fail2ban`, `ssh`, `docker`, `containerd`.
- Критичные порты (listen ownership):
  - TCP: `22`, `80`, `443`, `8443`;
  - UDP: `443`, `2443`, `3443`;
  - loopback: `127.0.0.1:10443`, `127.0.0.1:18080`.
- UFW:
  - status `active`,
  - defaults: `deny incoming`, `allow outgoing`,
  - allow/limit: `22/tcp LIMIT`, `80/tcp`, `443/tcp`, `8443/tcp`, `443/2443/3443 udp`.
- x-ui DB:
  - path: `/etc/x-ui/x-ui.db`,
  - `inbounds=2`,
  - `client_traffics=5`.

## RF: подтверждённое состояние
- Host: `v3179705.hosted-by-vdsina.ru`.
- OS: `Ubuntu 24.04.4 LTS`.
- Active services:
  - `ssh`, `docker`, `containerd`.
- Inactive services:
  - `nginx`, `x-ui`, `fail2ban`, `xray`, `hysteria-server`, `hysteria`.
- Порты:
  - public: `22/tcp`,
  - local resolver: `127.0.0.53:53`, `127.0.0.54:53`,
  - local containerd: `127.0.0.1:46785`.
- Firewall:
  - UFW `inactive`,
  - iptables baseline: `INPUT ACCEPT`, `FORWARD DROP`, `OUTPUT ACCEPT` + docker chains.
- Docker:
  - `Docker 29.1.3`,
  - `docker compose` plugin отсутствует (`unknown command`).

## DNS baseline
- MAIN-dомены:
  - `app.peskovp.com`, `api.peskovp.com`, `admin.peskovp.com`, `panel.peskovp.com`, `sub.peskovp.com`, `www.peskovp.com` -> `91.202.0.193`.
- RF-домены:
  - `ru.peskovp.com`, `relay-ru.peskovp.com` -> `138.16.181.33`.

## Вывод
- MAIN остаётся production edge/control-plane и не должен терять текущий портовый ownership.
- RF готов как выделенный data-plane gateway для V2 canary (после controlled bootstrap и firewall hardening).


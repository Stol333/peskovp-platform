param(
    [string]$MainHost = "91.202.0.193",
    [string]$MainUser = "root",
    [string]$MainKeyPath = "$HOME\.ssh\spain_new",
    [string]$RfHost = "138.16.181.33",
    [string]$RfUser = "root",
    [string]$RfKeyPath = "$HOME\.ssh\id_ed25519_138_16_181_33_ru",
    [string]$SshBinary = "",
    [string]$ArtifactsRoot = "",
    [string]$GraceConfirmationPath = "",
    [int]$SshConnectTimeoutSec = 12
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $true

function Invoke-RemoteReadOnlySnapshot {
    param(
        [Parameter(Mandatory = $true)][string]$RemoteHost,
        [Parameter(Mandatory = $true)][string]$User,
        [Parameter(Mandatory = $true)][string]$KeyPath,
        [Parameter(Mandatory = $true)][string]$ScriptText,
        [Parameter(Mandatory = $true)][string]$RawOutputPath,
        [Parameter(Mandatory = $true)][int]$ConnectTimeoutSec
    )

    $target = "$User@$RemoteHost"
    $normalizedScript = $ScriptText -replace "`r`n", "`n" -replace "`r", "`n"
    $outputLines = $normalizedScript | & $SshBinary -i $KeyPath -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=$ConnectTimeoutSec $target "bash -s --"
    Set-Content -Path $RawOutputPath -Value $outputLines -Encoding utf8
    return $outputLines
}

function Convert-KeyValueLinesToMap {
    param([string[]]$Lines)

    $map = [ordered]@{}
    foreach ($line in $Lines) {
        if ($line -match "^[A-Za-z0-9_]+=") {
            $separatorIndex = $line.IndexOf("=")
            if ($separatorIndex -gt 0) {
                $key = $line.Substring(0, $separatorIndex)
                $value = $line.Substring($separatorIndex + 1).Trim()
                $map[$key] = $value
            }
        }
    }
    return $map
}

function Get-IntOrDefault {
    param(
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Map,
        [Parameter(Mandatory = $true)][string]$Key,
        [int]$Default = -1
    )

    if (-not $Map.Contains($Key)) {
        return $Default
    }

    $rawValue = [string]$Map[$Key]
    $parsedValue = 0
    if ([int]::TryParse($rawValue, [ref]$parsedValue)) {
        return $parsedValue
    }
    return $Default
}

function Get-GraceConfirmationState {
    param(
        [Parameter(Mandatory = $true)][string]$ConfirmationPath
    )

    $result = [ordered]@{
        status = "manual_confirmation_required"
        confirmed = $false
        details = $null
    }

    if (-not (Test-Path -LiteralPath $ConfirmationPath)) {
        return $result
    }

    try {
        $confirmationRaw = Get-Content -Path $ConfirmationPath -Raw -Encoding utf8
        $confirmation = $confirmationRaw | ConvertFrom-Json -AsHashtable
        $status = [string]$confirmation["grace_period_completed"]
        if ($status -eq "confirmed") {
            $result.status = "confirmed"
            $result.confirmed = $true
        }
        $result.details = $confirmation
        return $result
    } catch {
        $result.status = "manual_confirmation_required"
        $result.confirmed = $false
        $result.details = [ordered]@{
            parse_error = $_.Exception.Message
            path = $ConfirmationPath
        }
        return $result
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
if ([string]::IsNullOrWhiteSpace($SshBinary)) {
    $sshCommand = Get-Command ssh -ErrorAction SilentlyContinue
    if ($null -ne $sshCommand) {
        $SshBinary = $sshCommand.Source
    } elseif (Test-Path "C:\Windows\System32\OpenSSH\ssh.exe") {
        $SshBinary = "C:\Windows\System32\OpenSSH\ssh.exe"
    } else {
        throw "SSH executable не найден. Установите OpenSSH client или передайте -SshBinary."
    }
}
if ([string]::IsNullOrWhiteSpace($ArtifactsRoot)) {
    $ArtifactsRoot = Join-Path $repoRoot "artifacts/phase25_monitoring"
}
if ([string]::IsNullOrWhiteSpace($GraceConfirmationPath)) {
    $GraceConfirmationPath = Join-Path $ArtifactsRoot "grace_period_confirmation.json"
}

$timestampUtc = [DateTime]::UtcNow
$snapshotId = $timestampUtc.ToString("yyyyMMdd-HHmmss")
$snapshotDir = Join-Path $ArtifactsRoot $snapshotId

New-Item -Path $snapshotDir -ItemType Directory -Force | Out-Null

$mainRawPath = Join-Path $snapshotDir "main_snapshot_raw.txt"
$rfRawPath = Join-Path $snapshotDir "rf_snapshot_raw.txt"
$summaryPath = Join-Path $snapshotDir "phase25_monitoring_summary.json"
$latestPath = Join-Path $ArtifactsRoot "latest_phase25_monitoring_summary.json"

$mainScript = @'
set -eu
echo "SNAPSHOT_TS_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "HOSTNAME=$(hostname)"

ENV_FILE="/root/peskovp-platform/docker/env/prod.env.phase22"
vpn_canary_percent="$(grep -E '^VPN_V2_CANARY_PERCENT=' "$ENV_FILE" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"
[ -n "$vpn_canary_percent" ] || vpn_canary_percent="unknown"
echo "VPN_V2_CANARY_PERCENT=$vpn_canary_percent"

vpn_write_enabled="$(grep -E '^VPN_WRITE_ENABLED=' "$ENV_FILE" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"
[ -n "$vpn_write_enabled" ] || vpn_write_enabled="unknown"
echo "VPN_WRITE_ENABLED=$vpn_write_enabled"

vpn_dry_run="$(grep -E '^VPN_PROVISIONING_DRY_RUN=' "$ENV_FILE" 2>/dev/null | tail -n1 | cut -d= -f2 || true)"
[ -n "$vpn_dry_run" ] || vpn_dry_run="unknown"
echo "VPN_PROVISIONING_DRY_RUN=$vpn_dry_run"

echo "ESTAB_TCP_8443=$(ss -tan state established '( sport = :8443 )' | awk 'NR>1 {c++} END {print c+0}')"
echo "ESTAB_TCP_443=$(ss -tan state established '( sport = :443 )' | awk 'NR>1 {c++} END {print c+0}')"
echo "UDP_LISTEN_443_2443_3443=$(ss -uan '( sport = :443 or sport = :2443 or sport = :3443 )' | awk 'NR>1 {c++} END {print c+0}')"
echo "HY2_LOG_LINES_60M=$(journalctl -u peskovp-hy2 -u peskovp-hy2-obfs -u peskovp-hy2-advanced --since '-60 min' --no-pager 2>/dev/null | wc -l | tr -d ' ')"
echo "HY2_ERR_LINES_60M=$(journalctl -u peskovp-hy2 -u peskovp-hy2-obfs -u peskovp-hy2-advanced --since '-60 min' -p err --no-pager 2>/dev/null | wc -l | tr -d ' ')"

echo "SERVICE_NGINX=$(systemctl is-active nginx 2>/dev/null || echo unknown)"
echo "SERVICE_X_UI=$(systemctl is-active x-ui 2>/dev/null || echo unknown)"
echo "SERVICE_PESKOVP_SUB=$(systemctl is-active peskovp-sub 2>/dev/null || echo unknown)"
echo "SERVICE_PESKOVP_HY2=$(systemctl is-active peskovp-hy2 2>/dev/null || echo unknown)"
echo "SERVICE_PESKOVP_HY2_OBFS=$(systemctl is-active peskovp-hy2-obfs 2>/dev/null || echo unknown)"
echo "SERVICE_PESKOVP_HY2_ADVANCED=$(systemctl is-active peskovp-hy2-advanced 2>/dev/null || echo unknown)"
route_app_code="$(curl -k -sS -o /dev/null -w '%{http_code}' --max-time 8 https://app.peskovp.com || true)"
[ -n "$route_app_code" ] || route_app_code="000"
echo "ROUTE_APP_CODE=$route_app_code"

route_admin_code="$(curl -k -sS -o /dev/null -w '%{http_code}' --max-time 8 https://admin.peskovp.com || true)"
[ -n "$route_admin_code" ] || route_admin_code="000"
echo "ROUTE_ADMIN_CODE=$route_admin_code"

route_api_health_code="$(curl -k -sS -o /dev/null -w '%{http_code}' --max-time 8 https://api.peskovp.com/api/health || true)"
[ -n "$route_api_health_code" ] || route_api_health_code="000"
echo "ROUTE_API_HEALTH_CODE=$route_api_health_code"

route_panel_code="$(curl -k -sS -o /dev/null -w '%{http_code}' --max-time 8 https://panel.peskovp.com || true)"
[ -n "$route_panel_code" ] || route_panel_code="000"
echo "ROUTE_PANEL_CODE=$route_panel_code"

route_sub_code="$(curl -k -sS -o /dev/null -w '%{http_code}' --max-time 8 https://sub.peskovp.com || true)"
[ -n "$route_sub_code" ] || route_sub_code="000"
echo "ROUTE_SUB_CODE=$route_sub_code"

route_www_code="$(curl -k -sS -o /dev/null -w '%{http_code}' --max-time 8 https://www.peskovp.com || true)"
[ -n "$route_www_code" ] || route_www_code="000"
echo "ROUTE_WWW_CODE=$route_www_code"

api_health_json="$(curl -sS --max-time 8 http://127.0.0.1:18081/health 2>/dev/null || curl -sS --max-time 8 http://127.0.0.1:18080/health 2>/dev/null || true)"
echo "API_HEALTH_JSON_B64=$(printf '%s' "$api_health_json" | base64 | tr -d '\n')"

vpn_health_json="$(curl -sS --max-time 8 http://127.0.0.1:3100/api/vpn/health 2>/dev/null || true)"
echo "VPN_HEALTH_JSON_B64=$(printf '%s' "$vpn_health_json" | base64 | tr -d '\n')"
'@

$rfScript = @'
set -eu
echo "SNAPSHOT_TS_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "HOSTNAME=$(hostname)"

echo "XRAY_ACTIVE=$(systemctl is-active xray 2>/dev/null || echo unknown)"
xray_test="fail"
xray run -test -config /usr/local/etc/xray/config.json >/dev/null 2>&1 && xray_test="ok" || true
if [ "$xray_test" != "ok" ]; then
  /usr/local/x-ui/bin/xray run -test -config /usr/local/etc/xray/config.json >/dev/null 2>&1 && xray_test="ok" || true
fi
echo "XRAY_CONFIG_TEST=$xray_test"

echo "LISTEN_TCP_443=$(ss -tln '( sport = :443 )' | awk 'NR>1 {c++} END {print c+0}')"
echo "LISTEN_TCP_2087=$(ss -tln '( sport = :2087 )' | awk 'NR>1 {c++} END {print c+0}')"
echo "LISTEN_TCP_2084=$(ss -tln '( sport = :2084 )' | awk 'NR>1 {c++} END {print c+0}')"

echo "UFW_STATUS=$(ufw status 2>/dev/null | head -n1 | awk '{print $2}')"
echo "UFW_RULE_443=$(ufw status numbered 2>/dev/null | grep -c '443/tcp')"
echo "UFW_RULE_2087=$(ufw status numbered 2>/dev/null | grep -c '2087/tcp')"
echo "UFW_RULE_2084=$(ufw status numbered 2>/dev/null | grep -c '2084/tcp')"

echo "XRAY_ERR_LINES_60M=$(journalctl -u xray --since '-60 min' -p err --no-pager 2>/dev/null | wc -l | tr -d ' ')"
'@

Write-Host "Collecting PHASE 25 monitoring snapshot from MAIN ($MainHost) and RF ($RfHost)..." -ForegroundColor Cyan

$mainRawLines = Invoke-RemoteReadOnlySnapshot -RemoteHost $MainHost -User $MainUser -KeyPath $MainKeyPath -ScriptText $mainScript -RawOutputPath $mainRawPath -ConnectTimeoutSec $SshConnectTimeoutSec
$rfRawLines = Invoke-RemoteReadOnlySnapshot -RemoteHost $RfHost -User $RfUser -KeyPath $RfKeyPath -ScriptText $rfScript -RawOutputPath $rfRawPath -ConnectTimeoutSec $SshConnectTimeoutSec

$mainMap = Convert-KeyValueLinesToMap -Lines $mainRawLines
$rfMap = Convert-KeyValueLinesToMap -Lines $rfRawLines

$estab8443 = Get-IntOrDefault -Map $mainMap -Key "ESTAB_TCP_8443"
$hy2Logs60m = Get-IntOrDefault -Map $mainMap -Key "HY2_LOG_LINES_60M"
$hy2Err60m = Get-IntOrDefault -Map $mainMap -Key "HY2_ERR_LINES_60M"

$legacyEndpointQuiet = $estab8443 -ge 0 -and $estab8443 -le 5
$legacyLogVolumeLow = $hy2Logs60m -ge 0 -and $hy2Logs60m -le 50
$legacyErrorLow = $hy2Err60m -ge 0 -and $hy2Err60m -le 1

$mainServicesOk = $true
foreach ($serviceKey in @(
    "SERVICE_NGINX",
    "SERVICE_X_UI",
    "SERVICE_PESKOVP_SUB",
    "SERVICE_PESKOVP_HY2",
    "SERVICE_PESKOVP_HY2_OBFS",
    "SERVICE_PESKOVP_HY2_ADVANCED"
)) {
    $serviceValue = [string]$mainMap[$serviceKey]
    if ([string]::IsNullOrWhiteSpace($serviceValue) -or $serviceValue -ne "active") {
        $mainServicesOk = $false
        break
    }
}

$rfHealthOk = $rfMap["XRAY_ACTIVE"] -eq "active" -and $rfMap["XRAY_CONFIG_TEST"] -eq "ok"
$routeRegressionOk = $true
$routeExpectations = [ordered]@{
    "ROUTE_APP_CODE" = "200"
    "ROUTE_ADMIN_CODE" = "200"
    "ROUTE_API_HEALTH_CODE" = "200"
    "ROUTE_PANEL_CODE" = "404"
    "ROUTE_SUB_CODE" = "404"
    "ROUTE_WWW_CODE" = "403"
}
foreach ($routeKey in $routeExpectations.Keys) {
    $routeValue = [string]$mainMap[$routeKey]
    if ([string]::IsNullOrWhiteSpace($routeValue) -or $routeValue -ne $routeExpectations[$routeKey]) {
        $routeRegressionOk = $false
        break
    }
}

$unblockWithoutGracePeriod = $legacyEndpointQuiet -and $legacyLogVolumeLow -and $legacyErrorLow -and $mainServicesOk -and $rfHealthOk -and $routeRegressionOk
$graceConfirmationState = Get-GraceConfirmationState -ConfirmationPath $GraceConfirmationPath
$phase25UnblockCandidate = $unblockWithoutGracePeriod -and [bool]$graceConfirmationState["confirmed"]

$summary = [ordered]@{
    snapshot_id = $snapshotId
    generated_at_utc = $timestampUtc.ToString("o")
    targets = [ordered]@{
        main_host = $MainHost
        rf_host = $RfHost
    }
    phase25 = [ordered]@{
        gate = "PHASE_25_BLOCKED"
        grace_period_completed = [string]$graceConfirmationState["status"]
        grace_period_confirmation_path = $GraceConfirmationPath
        grace_period_confirmation_loaded = [bool]$graceConfirmationState["confirmed"]
    }
    metrics = [ordered]@{
        main = $mainMap
        rf = $rfMap
    }
    derived = [ordered]@{
        legacy_endpoint_quiet = $legacyEndpointQuiet
        legacy_log_volume_low = $legacyLogVolumeLow
        legacy_error_low = $legacyErrorLow
        main_services_ok = $mainServicesOk
        rf_health_ok = $rfHealthOk
        route_regression_ok = $routeRegressionOk
        unblock_candidate_without_grace_period = $unblockWithoutGracePeriod
        phase25_unblock_candidate = $phase25UnblockCandidate
    }
    monitoring_policy = [ordered]@{
        cadence_minutes = 30
        required_stable_window_hours = 24
        target_conditions = @(
            "ESTAB_TCP_8443 <= 5 на протяжении окна наблюдения",
            "HY2_LOG_LINES_60M <= 50 и HY2_ERR_LINES_60M <= 1 на протяжении окна",
            "MAIN и RF service/route проверки без регрессии",
            "Подтверждено завершение legacy grace period"
        )
    }
}

$summaryJson = $summary | ConvertTo-Json -Depth 8
Set-Content -Path $summaryPath -Value $summaryJson -Encoding utf8
Set-Content -Path $latestPath -Value $summaryJson -Encoding utf8

Write-Host "PHASE 25 monitoring snapshot created." -ForegroundColor Green
Write-Host "Snapshot directory: $snapshotDir"
Write-Host "Summary JSON: $summaryPath"

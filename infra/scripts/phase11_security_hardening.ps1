param(
    [string]$RemoteHost,
    [string]$RemoteUser = "root",
    [string]$SshKeyPath,
    [string]$LocalArtifactsDir = "C:\Users\dgafa\artifacts\phase11",
    [int]$SshConnectTimeoutSec = 20
)

$ErrorActionPreference = "Stop"

function Write-Phase11 {
    param([string]$Message)
    Write-Host "[PHASE11] $Message"
}

function Test-RequiredCommand {
    param([string]$CommandName)
    $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Required command '$CommandName' was not found in PATH."
    }
}

function Resolve-OpenSshCommand {
    param(
        [string]$CommandName,
        [string]$FallbackPath
    )
    $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    if (Test-Path -LiteralPath $FallbackPath) {
        return $FallbackPath
    }
    throw "Required command '$CommandName' was not found in PATH and fallback path '$FallbackPath' is missing."
}

if ([string]::IsNullOrWhiteSpace($RemoteHost)) {
    throw "RemoteHost is required."
}
if ([string]::IsNullOrWhiteSpace($SshKeyPath)) {
    throw "SshKeyPath is required."
}
if (-not (Test-Path -LiteralPath $SshKeyPath)) {
    throw "SshKeyPath does not exist: $SshKeyPath"
}

$sshCommand = Resolve-OpenSshCommand -CommandName "ssh" -FallbackPath "C:\Windows\System32\OpenSSH\ssh.exe"
$scpCommand = Resolve-OpenSshCommand -CommandName "scp" -FallbackPath "C:\Windows\System32\OpenSSH\scp.exe"

$commonSshOptions = @(
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=$SshConnectTimeoutSec",
    "-o", "ServerAliveInterval=15",
    "-o", "ServerAliveCountMax=3",
    "-o", "StrictHostKeyChecking=accept-new"
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir = Join-Path $LocalArtifactsDir $timestamp
$logsDir = Join-Path $runDir "logs"
$manifestsDir = Join-Path $runDir "manifests"
New-Item -ItemType Directory -Path $runDir -Force | Out-Null
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
New-Item -ItemType Directory -Path $manifestsDir -Force | Out-Null

$remoteScript = @'
set -u

TS="$(date +%Y%m%d-%H%M%S)"
RUN_BASE="/root/backups/peskovp-phase11-hardening-${TS}"
mkdir -p "${RUN_BASE}/"{backup,precheck,postcheck}

SSHD_BIN="$(command -v sshd 2>/dev/null || true)"
if [ -z "${SSHD_BIN}" ] && [ -x /usr/sbin/sshd ]; then
  SSHD_BIN="/usr/sbin/sshd"
fi

# Precheck snapshot
date -Is > "${RUN_BASE}/precheck/start-utc.txt"
uname -a > "${RUN_BASE}/precheck/uname.txt" 2>&1 || true
cat /etc/os-release > "${RUN_BASE}/precheck/os-release.txt" 2>&1 || true
nginx -t > "${RUN_BASE}/precheck/nginx-test-before.txt" 2>&1 || true
if [ -n "${SSHD_BIN}" ]; then
  "${SSHD_BIN}" -t > "${RUN_BASE}/precheck/sshd-test-before.txt" 2>&1 || true
fi
ufw status verbose > "${RUN_BASE}/precheck/ufw-before.txt" 2>&1 || true
fail2ban-client status > "${RUN_BASE}/precheck/fail2ban-before.txt" 2>&1 || true
systemctl is-active nginx > "${RUN_BASE}/precheck/nginx-active-before.txt" 2>&1 || true
systemctl is-active fail2ban > "${RUN_BASE}/precheck/fail2ban-active-before.txt" 2>&1 || true
(systemctl is-active ssh || systemctl is-active sshd) > "${RUN_BASE}/precheck/ssh-active-before.txt" 2>&1 || true

# Backup config before changes
cp -a /etc/ssh/sshd_config "${RUN_BASE}/backup/sshd_config.bak" 2>/dev/null || true
cp -a /etc/ssh/sshd_config.d "${RUN_BASE}/backup/sshd_config.d.bak" 2>/dev/null || true
cp -a /etc/fail2ban "${RUN_BASE}/backup/fail2ban.bak" 2>/dev/null || true
cp -a /etc/nginx/nginx.conf "${RUN_BASE}/backup/nginx.conf.bak" 2>/dev/null || true
cp -a /etc/nginx/conf.d "${RUN_BASE}/backup/nginx-conf.d.bak" 2>/dev/null || true
cp -a /etc/nginx/sites-enabled "${RUN_BASE}/backup/nginx-sites-enabled.bak" 2>/dev/null || true
cp -a /etc/ufw "${RUN_BASE}/backup/ufw.bak" 2>/dev/null || true

HARDEN_FAIL=0

# SSH hardening include
mkdir -p /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/99-peskovp-hardening.conf <<'EOF_SSH'
# PESKOVP Phase 11 hardening
PermitEmptyPasswords no
MaxAuthTries 4
LoginGraceTime 30
MaxStartups 10:30:60
ClientAliveInterval 300
ClientAliveCountMax 2
EOF_SSH

if [ -n "${SSHD_BIN}" ]; then
  if ! "${SSHD_BIN}" -t > "${RUN_BASE}/postcheck/sshd-test-after.txt" 2>&1; then
    HARDEN_FAIL=1
  else
    (systemctl reload ssh || systemctl reload sshd) > "${RUN_BASE}/postcheck/ssh-reload.txt" 2>&1 || HARDEN_FAIL=1
  fi
else
  echo "sshd binary not found" > "${RUN_BASE}/postcheck/sshd-test-after.txt"
  HARDEN_FAIL=1
fi

# Fail2ban hardening for SSH
mkdir -p /etc/fail2ban/jail.d
cat > /etc/fail2ban/jail.d/10-peskovp-sshd.local <<'EOF_F2B'
[sshd]
enabled = true
mode = aggressive
findtime = 10m
maxretry = 5
bantime = 1h
ignoreip = 127.0.0.1/8 ::1
EOF_F2B

if command -v fail2ban-client >/dev/null 2>&1; then
  fail2ban-client -t > "${RUN_BASE}/postcheck/fail2ban-config-test.txt" 2>&1 || HARDEN_FAIL=1
fi
systemctl restart fail2ban > "${RUN_BASE}/postcheck/fail2ban-restart.txt" 2>&1 || HARDEN_FAIL=1
fail2ban-client status > "${RUN_BASE}/postcheck/fail2ban-after.txt" 2>&1 || true
fail2ban-client status sshd > "${RUN_BASE}/postcheck/fail2ban-sshd-after.txt" 2>&1 || true

# Nginx hardening include (http context via conf.d)
mkdir -p /etc/nginx/conf.d
cat > /etc/nginx/conf.d/zz-peskovp-hardening.conf <<'EOF_NGINX'
server_tokens off;
client_max_body_size 2m;
client_body_timeout 15s;
client_header_timeout 15s;
keepalive_timeout 30s;
send_timeout 30s;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
EOF_NGINX

if ! nginx -t > "${RUN_BASE}/postcheck/nginx-test-after.txt" 2>&1; then
  HARDEN_FAIL=1
else
  systemctl reload nginx > "${RUN_BASE}/postcheck/nginx-reload.txt" 2>&1 || HARDEN_FAIL=1
fi

# UFW SSH throttling (safe additive)
ufw status verbose > "${RUN_BASE}/postcheck/ufw-before-limit.txt" 2>&1 || true
if ! grep -Eq '^22/tcp\s+LIMIT' "${RUN_BASE}/postcheck/ufw-before-limit.txt"; then
  ufw limit 22/tcp > "${RUN_BASE}/postcheck/ufw-limit-22.txt" 2>&1 || true
fi
ufw status verbose > "${RUN_BASE}/postcheck/ufw-after.txt" 2>&1 || true

# Final checks
SSH_ACTIVE="$(systemctl is-active ssh 2>/dev/null || true)"
SSHD_ACTIVE="$(systemctl is-active sshd 2>/dev/null || true)"
NGINX_ACTIVE="$(systemctl is-active nginx 2>/dev/null || true)"
F2B_ACTIVE="$(systemctl is-active fail2ban 2>/dev/null || true)"
echo "ssh=${SSH_ACTIVE}" > "${RUN_BASE}/postcheck/services-active-after.txt"
echo "sshd=${SSHD_ACTIVE}" >> "${RUN_BASE}/postcheck/services-active-after.txt"
echo "nginx=${NGINX_ACTIVE}" >> "${RUN_BASE}/postcheck/services-active-after.txt"
echo "fail2ban=${F2B_ACTIVE}" >> "${RUN_BASE}/postcheck/services-active-after.txt"

CRIT_FAIL=0
if [ "${HARDEN_FAIL}" -ne 0 ]; then
  CRIT_FAIL=1
fi
if [ "${NGINX_ACTIVE}" != "active" ]; then
  CRIT_FAIL=1
fi
if [ "${F2B_ACTIVE}" != "active" ]; then
  CRIT_FAIL=1
fi
if [ "${SSH_ACTIVE}" != "active" ] && [ "${SSHD_ACTIVE}" != "active" ]; then
  CRIT_FAIL=1
fi
if ! nginx -t > /dev/null 2>&1; then
  CRIT_FAIL=1
fi
if [ -n "${SSHD_BIN}" ] && ! "${SSHD_BIN}" -t > /dev/null 2>&1; then
  CRIT_FAIL=1
fi

if [ "${CRIT_FAIL}" -eq 0 ]; then
  RESULT="PASS"
  EXIT_CODE=0
else
  RESULT="FAIL"
  EXIT_CODE=61
fi

echo "PHASE11_RESULT=${RESULT}" > "${RUN_BASE}/RESULT.txt"
echo "PHASE11_EXIT_CODE=${EXIT_CODE}" >> "${RUN_BASE}/RESULT.txt"
echo "PHASE11_RUN_BASE=${RUN_BASE}" >> "${RUN_BASE}/RESULT.txt"

echo "PHASE11_RUN_BASE=${RUN_BASE}"
echo "PHASE11_RESULT=${RESULT}"
echo "PHASE11_EXIT_CODE=${EXIT_CODE}"
exit ${EXIT_CODE}
'@

$remoteScriptNormalized = ($remoteScript -replace "`r`n", "`n") -replace "`r", "`n"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$localRemoteScriptPath = Join-Path $runDir "run_phase11_remote_hardening.sh"
[System.IO.File]::WriteAllText($localRemoteScriptPath, $remoteScriptNormalized, $utf8NoBom)

$remoteTmpScript = "/tmp/peskovp_phase11_hardening_${timestamp}.sh"
$uploadLog = Join-Path $logsDir "scp_upload.log"
$remoteExecLog = Join-Path $logsDir "ssh_remote_exec.log"
$downloadLog = Join-Path $logsDir "scp_download.log"
$cleanupLog = Join-Path $logsDir "ssh_cleanup.log"

Write-Phase11 "Uploading remote hardening script..."
& $scpCommand @commonSshOptions -i $SshKeyPath $localRemoteScriptPath "${RemoteUser}@${RemoteHost}:$remoteTmpScript" 2>&1 | Tee-Object -FilePath $uploadLog | Out-Null

Write-Phase11 "Executing remote Phase 11 hardening..."
$remoteExecOutput = & $sshCommand @commonSshOptions -i $SshKeyPath "$RemoteUser@$RemoteHost" "bash $remoteTmpScript" 2>&1 | Tee-Object -FilePath $remoteExecLog
$sshExitCode = $LASTEXITCODE

$remoteBaseLine = $remoteExecOutput | Where-Object { $_ -like "PHASE11_RUN_BASE=*" } | Select-Object -Last 1
$remoteResultLine = $remoteExecOutput | Where-Object { $_ -like "PHASE11_RESULT=*" } | Select-Object -Last 1
$remoteExitLine = $remoteExecOutput | Where-Object { $_ -like "PHASE11_EXIT_CODE=*" } | Select-Object -Last 1

if ([string]::IsNullOrWhiteSpace($remoteBaseLine)) {
    throw "Could not determine PHASE11_RUN_BASE from remote output."
}
$remoteBasePath = $remoteBaseLine -replace "^PHASE11_RUN_BASE=", ""
$phase11Result = if ([string]::IsNullOrWhiteSpace($remoteResultLine)) { "UNKNOWN" } else { $remoteResultLine -replace "^PHASE11_RESULT=", "" }
$phase11ExitCode = if ([string]::IsNullOrWhiteSpace($remoteExitLine)) { "-1" } else { $remoteExitLine -replace "^PHASE11_EXIT_CODE=", "" }

$downloadTarget = Join-Path $runDir "server_phase11"
New-Item -ItemType Directory -Path $downloadTarget -Force | Out-Null

Write-Phase11 "Downloading Phase 11 artifacts..."
& $scpCommand @commonSshOptions -i $SshKeyPath -r "${RemoteUser}@${RemoteHost}:$remoteBasePath" $downloadTarget 2>&1 | Tee-Object -FilePath $downloadLog | Out-Null

Write-Phase11 "Cleaning up temporary remote script..."
& $sshCommand @commonSshOptions -i $SshKeyPath "$RemoteUser@$RemoteHost" "rm -f $remoteTmpScript" 2>&1 | Tee-Object -FilePath $cleanupLog | Out-Null

$summary = [ordered]@{
    completed_at_utc     = (Get-Date).ToUniversalTime().ToString("o")
    remote_host          = $RemoteHost
    remote_user          = $RemoteUser
    remote_run_base      = $remoteBasePath
    phase11_result       = $phase11Result
    phase11_exit_code    = $phase11ExitCode
    ssh_process_exit     = $sshExitCode
    local_download_path  = $downloadTarget
    logs_directory       = $logsDir
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $manifestsDir "phase11_apply_summary.json") -Encoding UTF8

Write-Phase11 "Remote run base: $remoteBasePath"
Write-Phase11 "Result: $phase11Result (remote exit $phase11ExitCode, ssh exit $sshExitCode)"
Write-Phase11 "Local artifacts: $downloadTarget"

if ($phase11Result -ne "PASS") {
    throw "Phase 11 hardening failed on remote side. See artifacts in $downloadTarget"
}

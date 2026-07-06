
param(
    [switch]$InstallNodeIfMissing,
    [string]$NodeWingetId = "OpenJS.NodeJS.LTS",
    [string]$PnpmVersion = "9.12.3"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$PSNativeCommandUseErrorActionPreference = $true

function Test-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Action
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
Push-Location $repoRoot
try {
    if (-not (Test-Command "node")) {
        if (-not $InstallNodeIfMissing) {
            throw "Node.js не найден. Запустите скрипт с -InstallNodeIfMissing или установите Node.js LTS вручную."
        }
        if (-not (Test-Command "winget")) {
            throw "Node.js не найден, а winget недоступен. Установите Node.js LTS вручную."
        }
        Invoke-Step -Name "Install Node.js LTS via winget" -Action {
            winget install --id $NodeWingetId -e --silent --accept-package-agreements --accept-source-agreements
        }
    }

    if (-not (Test-Command "corepack")) {
        throw "corepack недоступен. Проверьте установку Node.js LTS."
    }

    Invoke-Step -Name "Enable Corepack" -Action { corepack enable }
    Invoke-Step -Name "Activate pnpm $PnpmVersion" -Action { corepack prepare "pnpm@$PnpmVersion" --activate }

    Invoke-Step -Name "Version check (node/npm/pnpm)" -Action {
        node --version
        npm --version
        pnpm --version
    }

    Invoke-Step -Name "pnpm install" -Action { pnpm install }
    Invoke-Step -Name "pnpm lint" -Action { pnpm lint }
    Invoke-Step -Name "pnpm prettier check" -Action { pnpm exec prettier --check . }
    Invoke-Step -Name "pnpm typecheck" -Action { pnpm typecheck }
    Invoke-Step -Name "pnpm build" -Action { pnpm build }
    Invoke-Step -Name "pnpm db build" -Action { pnpm --filter @peskovp/db build }

    Invoke-Step -Name "Python tests: vpn-routing" -Action { python -m pytest C:/Users/dgafa/packages/vpn-routing/tests -q }
    Invoke-Step -Name "Python tests: apps/api" -Action { python -m pytest C:/Users/dgafa/apps/api/tests -q }
    Invoke-Step -Name "Python tests: integrations/vpn" -Action { python -m pytest C:/Users/dgafa/integrations/vpn/tests -q }
    Invoke-Step -Name "Python tests: ai-module" -Action { python -m pytest C:/Users/dgafa/services/ai-module/tests -q }

    Invoke-Step -Name "Python compileall checks" -Action {
        python -m compileall C:/Users/dgafa/packages/vpn-routing/src C:/Users/dgafa/apps/api/src C:/Users/dgafa/integrations/vpn/src C:/Users/dgafa/services/ai-module/src
    }

    Invoke-Step -Name "Docker compose config check" -Action {
        docker compose -f C:/Users/dgafa/docker/docker-compose.prod.yml --env-file C:/Users/dgafa/docker/env/prod.env.example config
    }

    Write-Host "PHASE 17 verify sequence completed." -ForegroundColor Green
}
finally {
    Pop-Location
}

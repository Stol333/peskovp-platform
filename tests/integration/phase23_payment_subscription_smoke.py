from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


JsonObject = dict[str, Any]


@dataclass(slots=True)
class HttpResult:
    status: int
    body_text: str
    body_json: Any | None
    headers: dict[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PHASE 23 CI smoke for payment -> webhook/idempotency -> subscription link flow."
    )
    parser.add_argument("--base-url", required=True, help="Base URL of running web app, e.g. http://127.0.0.1:3100")
    parser.add_argument("--webhook-secret", required=True, help="Expected Telegram payments webhook secret")
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts/phase23_ci",
        help="Directory where request/response artifacts will be saved",
    )
    parser.add_argument(
        "--wait-timeout-seconds",
        type=int,
        default=240,
        help="Max wait time for health checks",
    )
    parser.add_argument(
        "--wait-interval-seconds",
        type=int,
        default=4,
        help="Polling interval for health/ready checks",
    )
    return parser.parse_args()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def http_json(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: JsonObject | None = None,
    timeout_seconds: int = 15,
) -> HttpResult:
    request_headers: dict[str, str] = {"accept": "application/json"}
    payload_bytes: bytes | None = None

    if body is not None:
        payload_bytes = json.dumps(body).encode("utf-8")
        request_headers["content-type"] = "application/json"
    if headers:
        request_headers.update(headers)

    request = Request(url=url, method=method.upper(), data=payload_bytes, headers=request_headers)

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
            parsed = _parse_json(raw)
            return HttpResult(
                status=response.getcode(),
                body_text=raw,
                body_json=parsed,
                headers={k.lower(): v for k, v in response.headers.items()},
            )
    except HTTPError as error:
        raw = error.read().decode("utf-8")
        parsed = _parse_json(raw)
        return HttpResult(
            status=error.code,
            body_text=raw,
            body_json=parsed,
            headers={k.lower(): v for k, v in error.headers.items()},
        )
    except URLError as error:
        raise RuntimeError(f"HTTP request failed for {method.upper()} {url}: {error}") from error


def _parse_json(raw: str) -> Any | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def as_object(value: Any, message: str) -> JsonObject:
    expect(isinstance(value, dict), message)
    return value


def run_step(
    *,
    artifacts_dir: Path,
    name: str,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: JsonObject | None = None,
    expected_status: int | None = None,
) -> HttpResult:
    result = http_json(method, url, headers=headers, body=body)
    write_json(
        artifacts_dir / f"{name}.json",
        {
            "step": name,
            "request": {
                "method": method.upper(),
                "url": url,
                "headers": headers or {},
                "body": body,
            },
            "response": {
                "status": result.status,
                "headers": result.headers,
                "body_text": result.body_text,
                "body_json": result.body_json,
            },
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
    )

    if expected_status is not None:
        expect(
            result.status == expected_status,
            f"{name}: expected HTTP {expected_status}, got {result.status}. Body: {result.body_text}",
        )
    return result


def wait_until(
    *,
    artifacts_dir: Path,
    name: str,
    method: str,
    url: str,
    predicate: Callable[[HttpResult], bool],
    timeout_seconds: int,
    interval_seconds: int,
) -> HttpResult:
    deadline = time.monotonic() + timeout_seconds
    attempt = 0
    last_result: HttpResult | None = None

    while time.monotonic() < deadline:
        attempt += 1
        step_name = f"{name}_attempt_{attempt:02d}"
        result = run_step(
            artifacts_dir=artifacts_dir,
            name=step_name,
            method=method,
            url=url,
        )
        last_result = result
        if predicate(result):
            print(f"[wait] {name} passed on attempt {attempt}")
            return result
        print(f"[wait] {name} attempt {attempt}: status={result.status}, waiting {interval_seconds}s")
        time.sleep(interval_seconds)

    details = "no response captured"
    if last_result is not None:
        details = f"last_status={last_result.status} last_body={last_result.body_text}"
    raise TimeoutError(f"{name} did not satisfy predicate in {timeout_seconds}s: {details}")


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    print(f"[start] PHASE 23 integration smoke against {base_url}")

    health_url = f"{base_url}/api/health"
    create_url = f"{base_url}/api/payments/create"
    webhook_url = f"{base_url}/api/payments/webhook/telegram"
    subscription_url = f"{base_url}/api/vpn/subscription-link"

    wait_until(
        artifacts_dir=artifacts_dir,
        name="wait_web_health",
        method="GET",
        url=health_url,
        timeout_seconds=args.wait_timeout_seconds,
        interval_seconds=args.wait_interval_seconds,
        predicate=lambda result: result.status == 200
        and isinstance(result.body_json, dict)
        and result.body_json.get("ok") is True
        and result.body_json.get("status") == "healthy",
    )


    create_body = {
        "userId": "phase23-ci-user",
        "planId": "phase23-monthly",
        "amount": 499,
        "currency": "RUB",
        "provider": "telegram_stars",
    }

    create_1 = run_step(
        artifacts_dir=artifacts_dir,
        name="create_intent_new",
        method="POST",
        url=create_url,
        headers={"x-idempotency-key": "phase23-ci-create-1"},
        body=create_body,
        expected_status=201,
    )
    create_1_json = as_object(create_1.body_json, "create_intent_new: response must be JSON object")
    expect(create_1_json.get("ok") is True, "create_intent_new: ok must be true")
    expect(create_1_json.get("idempotencyStatus") == "new", "create_intent_new: idempotencyStatus must be 'new'")
    payment_id_1 = create_1_json.get("paymentId")
    expect(isinstance(payment_id_1, str) and payment_id_1, "create_intent_new: paymentId must be non-empty string")

    create_1_replay = run_step(
        artifacts_dir=artifacts_dir,
        name="create_intent_replay",
        method="POST",
        url=create_url,
        headers={"x-idempotency-key": "phase23-ci-create-1"},
        body=create_body,
        expected_status=200,
    )
    create_1_replay_json = as_object(create_1_replay.body_json, "create_intent_replay: response must be JSON object")
    expect(
        create_1_replay_json.get("idempotencyStatus") == "replay",
        "create_intent_replay: idempotencyStatus must be 'replay'",
    )
    expect(
        create_1_replay_json.get("paymentId") == payment_id_1,
        "create_intent_replay: paymentId must match original request",
    )

    webhook_headers_ok = {
        "x-idempotency-key": "phase23-ci-webhook-success-1",
        "x-payments-webhook-secret": args.webhook_secret,
    }
    webhook_body_success_1 = {
        "eventId": "phase23-ci-event-success-1",
        "paymentId": payment_id_1,
        "status": "succeeded",
        "telegramChargeId": "ci_charge_success_1",
    }
    webhook_success_1 = run_step(
        artifacts_dir=artifacts_dir,
        name="webhook_succeeded_new",
        method="POST",
        url=webhook_url,
        headers=webhook_headers_ok,
        body=webhook_body_success_1,
        expected_status=200,
    )
    webhook_success_1_json = as_object(webhook_success_1.body_json, "webhook_succeeded_new: response must be JSON object")
    expect(
        webhook_success_1_json.get("paymentStatus") == "succeeded",
        "webhook_succeeded_new: paymentStatus must be 'succeeded'",
    )
    expect(
        webhook_success_1_json.get("idempotencyStatus") == "new",
        "webhook_succeeded_new: idempotencyStatus must be 'new'",
    )
    activation_1 = webhook_success_1_json.get("subscriptionActivation")
    activation_1_obj = as_object(activation_1, "webhook_succeeded_new: subscriptionActivation must be object")
    expect(
        activation_1_obj.get("activated") is True,
        "webhook_succeeded_new: subscriptionActivation.activated must be true",
    )

    webhook_success_1_replay = run_step(
        artifacts_dir=artifacts_dir,
        name="webhook_succeeded_replay",
        method="POST",
        url=webhook_url,
        headers=webhook_headers_ok,
        body=webhook_body_success_1,
        expected_status=200,
    )
    webhook_success_1_replay_json = as_object(
        webhook_success_1_replay.body_json, "webhook_succeeded_replay: response must be JSON object"
    )
    expect(
        webhook_success_1_replay_json.get("idempotencyStatus") == "replay",
        "webhook_succeeded_replay: idempotencyStatus must be 'replay'",
    )

    create_2 = run_step(
        artifacts_dir=artifacts_dir,
        name="create_intent_second_new",
        method="POST",
        url=create_url,
        headers={"x-idempotency-key": "phase23-ci-create-2"},
        body={**create_body, "planId": "phase23-quarterly"},
        expected_status=201,
    )
    create_2_json = as_object(create_2.body_json, "create_intent_second_new: response must be JSON object")
    payment_id_2 = create_2_json.get("paymentId")
    expect(isinstance(payment_id_2, str) and payment_id_2, "create_intent_second_new: paymentId must be non-empty string")

    webhook_failed_2 = run_step(
        artifacts_dir=artifacts_dir,
        name="webhook_failed_new",
        method="POST",
        url=webhook_url,
        headers={
            "x-idempotency-key": "phase23-ci-webhook-failed-2",
            "x-payments-webhook-secret": args.webhook_secret,
        },
        body={
            "eventId": "phase23-ci-event-failed-2",
            "paymentId": payment_id_2,
            "status": "failed",
            "telegramChargeId": "ci_charge_failed_2",
        },
        expected_status=200,
    )
    webhook_failed_2_json = as_object(webhook_failed_2.body_json, "webhook_failed_new: response must be JSON object")
    expect(webhook_failed_2_json.get("paymentStatus") == "failed", "webhook_failed_new: paymentStatus must be 'failed'")
    expect(
        webhook_failed_2_json.get("subscriptionActivation") is None,
        "webhook_failed_new: subscriptionActivation must be null for failed payment",
    )

    run_step(
        artifacts_dir=artifacts_dir,
        name="webhook_invalid_secret",
        method="POST",
        url=webhook_url,
        headers={
            "x-idempotency-key": "phase23-ci-webhook-invalid-secret",
            "x-payments-webhook-secret": "ci-phase23-invalid-secret",
        },
        body={
            "eventId": "phase23-ci-event-invalid-secret",
            "paymentId": payment_id_2,
            "status": "succeeded",
        },
        expected_status=401,
    )

    create_3 = run_step(
        artifacts_dir=artifacts_dir,
        name="create_intent_renew_new",
        method="POST",
        url=create_url,
        headers={"x-idempotency-key": "phase23-ci-create-3-renew"},
        body={**create_body},
        expected_status=201,
    )
    create_3_json = as_object(create_3.body_json, "create_intent_renew_new: response must be JSON object")
    payment_id_3 = create_3_json.get("paymentId")
    expect(isinstance(payment_id_3, str) and payment_id_3, "create_intent_renew_new: paymentId must be non-empty string")

    webhook_renew = run_step(
        artifacts_dir=artifacts_dir,
        name="webhook_renew_succeeded_new",
        method="POST",
        url=webhook_url,
        headers={
            "x-idempotency-key": "phase23-ci-webhook-renew-3",
            "x-payments-webhook-secret": args.webhook_secret,
        },
        body={
            "eventId": "phase23-ci-event-renew-3",
            "paymentId": payment_id_3,
            "status": "succeeded",
            "telegramChargeId": "ci_charge_renew_3",
        },
        expected_status=200,
    )
    webhook_renew_json = as_object(webhook_renew.body_json, "webhook_renew_succeeded_new: response must be JSON object")
    activation_renew = as_object(
        webhook_renew_json.get("subscriptionActivation"),
        "webhook_renew_succeeded_new: subscriptionActivation must be object",
    )
    expect(
        activation_renew.get("activated") is True,
        "webhook_renew_succeeded_new: subscriptionActivation.activated must be true",
    )

    subscription_link = run_step(
        artifacts_dir=artifacts_dir,
        name="subscription_link_check",
        method="GET",
        url=subscription_url,
        expected_status=200,
    )
    subscription_link_json = as_object(subscription_link.body_json, "subscription_link_check: response must be JSON object")
    expect(subscription_link_json.get("ok") is True, "subscription_link_check: ok must be true")
    expect(subscription_link_json.get("qrAvailable") is True, "subscription_link_check: qrAvailable must be true")
    expect(
        isinstance(subscription_link_json.get("link"), str) and bool(subscription_link_json.get("link")),
        "subscription_link_check: link must be non-empty string",
    )

    summary = {
        "status": "passed",
        "flow": "phase23_ci_payment_subscription_smoke",
        "paymentIds": {
            "primary": payment_id_1,
            "failed_case": payment_id_2,
            "renew_case": payment_id_3,
        },
        "checks": [
            "health_ok",
            "create_intent_new_and_replay",
            "webhook_succeeded_new_and_replay",
            "webhook_failed_no_activation",
            "invalid_secret_401",
            "renew_succeeded_activation",
            "subscription_link_qr_available",
        ],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    write_json(artifacts_dir / "summary.json", summary)
    print("[done] PHASE23_CI_SMOKE_PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"[error] PHASE23_CI_SMOKE_FAIL: {error}", file=sys.stderr)
        raise

#!/usr/bin/env python3
"""Fail-closed required-check guard for the Phase 11 aggregate validator."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd()
FIXTURE_PATH = Path("zigux/tests/fixtures/phase11_validate_checks.json")

REQUIRED_CHECKS = (
    ("phase11-validation-self-test", ("python", "scripts/zigux/validate-phase11.py", "--self-test")),
    ("phase11-validate-manifest-roster-self-test", ("python", "scripts/zigux/check-phase11-validate-manifest-roster.py", "--self-test")),
    ("phase11-validate-manifest-roster", ("python", "scripts/zigux/check-phase11-validate-manifest-roster.py")),
    ("phase11-validate-check-roster-self-test", ("python", "scripts/zigux/check-phase11-validate-check-roster.py", "--self-test")),
    ("phase11-validate-check-roster", ("python", "scripts/zigux/check-phase11-validate-check-roster.py")),
    ("phase11-validate-route-alignment-self-test", ("python", "scripts/zigux/check-phase11-validate-route-alignment.py", "--self-test")),
    ("phase11-validate-route-alignment", ("python", "scripts/zigux/check-phase11-validate-route-alignment.py")),
    ("phase11-shared-tooling-manifest-self-test", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py", "--self-test")),
    ("phase11-shared-tooling-manifest", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py")),
    ("phase11-build-inventory-self-test", ("python", "scripts/zigux/check-phase11-build-inventory.py", "--self-test")),
    ("phase11-build-inventory", ("python", "scripts/zigux/check-phase11-build-inventory.py")),
    ("phase11-focused-direct-build-replays-self-test", ("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py", "--self-test")),
    ("phase11-focused-direct-build-replays", ("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py")),
    ("phase11-shared-replay-contract-counts-self-test", ("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py", "--self-test")),
    ("phase11-shared-replay-contract-counts", ("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py")),
    ("phase11-matrix-gap-survey-self-test", ("python", "scripts/zigux/check-phase11-matrix-gap-survey.py", "--self-test")),
    ("phase11-matrix-gap-survey", ("python", "scripts/zigux/check-phase11-matrix-gap-survey.py")),
    ("phase11-validation-matrix-gap-survey-self-test", ("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py", "--self-test")),
    ("phase11-validation-matrix-gap-survey", ("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py")),
    ("phase11-watchdog-lifecycle-parity-gap-self-test", ("python", "scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py", "--self-test")),
    ("phase11-watchdog-lifecycle-parity-gap", ("python", "scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py")),
    ("phase11-header-boundary-packet-self-test", ("python", "scripts/zigux/check-phase11-header-boundary-packet.py", "--self-test")),
    ("phase11-header-boundary-packet", ("python", "scripts/zigux/check-phase11-header-boundary-packet.py")),
    ("phase11-hvc-cleanup-current-head-self-test", ("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py", "--self-test")),
    ("phase11-hvc-cleanup-current-head", ("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py")),
    ("phase11-hvc-cleanup-prerequisite-packet-self-test", ("python", "scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py", "--self-test")),
    ("phase11-hvc-cleanup-prerequisite-packet", ("python", "scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py")),
    ("phase11-hvc-targetless-unregister-witness-self-test", ("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test")),
    ("phase11-hvc-targetless-unregister-witness", ("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py")),
    ("phase11-hvc-current-head-manifest-self-test", ("python", "scripts/zigux/check-phase11-hvc-current-head-manifest.py", "--self-test")),
    ("phase11-hvc-current-head-manifest", ("python", "scripts/zigux/check-phase11-hvc-current-head-manifest.py")),
    ("phase11-dw-wdt-teardown-packet-self-test", ("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py", "--self-test")),
    ("phase11-dw-wdt-teardown-packet", ("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py")),
    ("phase11-dw-wdt-verify-alignment-self-test", ("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py", "--self-test")),
    ("phase11-dw-wdt-verify-alignment", ("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py")),
    ("phase11-dw-wdt-build-route-self-test", ("python", "scripts/zigux/check-phase11-dw-wdt-build-route.py", "--self-test")),
    ("phase11-dw-wdt-build-route", ("python", "scripts/zigux/check-phase11-dw-wdt-build-route.py")),
)


class CheckError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CheckError(f"missing required fixture: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {path}")
    return value


def fixture_check_map(fixture: dict[str, object]) -> dict[str, tuple[str, ...]]:
    exact_checks = fixture.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise CheckError(f"expected exact_checks list in {FIXTURE_PATH}")

    checks: dict[str, tuple[str, ...]] = {}
    for item in exact_checks:
        if not isinstance(item, dict):
            raise CheckError(f"expected object entries in {FIXTURE_PATH}")
        name = item.get("name")
        command = item.get("command")
        if not isinstance(name, str):
            raise CheckError(f"expected string check name in {FIXTURE_PATH}")
        if name in checks:
            raise CheckError(f"duplicate check name in {FIXTURE_PATH}: {name}")
        if not isinstance(command, list) or any(not isinstance(part, str) for part in command):
            raise CheckError(f"expected string-list command for {name} in {FIXTURE_PATH}")
        checks[name] = tuple(command)
    return checks


def run_check(root: Path) -> int:
    checks = fixture_check_map(read_json(root / FIXTURE_PATH))
    for name, command in REQUIRED_CHECKS:
        actual = checks.get(name)
        if actual is None:
            raise CheckError(f"missing required Phase 11 validate check: {name}")
        if actual != command:
            raise CheckError(
                f"command mismatch for {name}: expected {' '.join(command)}, got {' '.join(actual)}"
            )
    return len(checks)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_payload(*, omit: str | None = None, wrong_command: str | None = None) -> dict[str, object]:
    exact_checks = []
    for name, command in REQUIRED_CHECKS:
        if name == omit:
            continue
        row_command = list(command)
        if name == wrong_command:
            row_command = ["python", "scripts/zigux/wrong.py"]
        exact_checks.append({"name": name, "command": row_command})
    exact_checks.append({"name": "phase11-extra-zig-build", "command": ["zig", "build", "test"]})
    return {"exact_checks": exact_checks}


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_required_validate_checks_"))
    try:
        passing = tmpdir / "passing"
        write(passing / FIXTURE_PATH, json.dumps(fixture_payload(), indent=2) + "\n")
        check_count = run_check(passing)
        case_count = 1

        missing = tmpdir / "missing"
        write(
            missing / FIXTURE_PATH,
            json.dumps(fixture_payload(omit="phase11-hvc-current-head-manifest"), indent=2) + "\n",
        )
        expect_failure(missing, "phase11-hvc-current-head-manifest")
        case_count += 1

        wrong_command = tmpdir / "wrong_command"
        write(
            wrong_command / FIXTURE_PATH,
            json.dumps(
                fixture_payload(wrong_command="phase11-shared-tooling-manifest"),
                indent=2,
            )
            + "\n",
        )
        expect_failure(wrong_command, "command mismatch for phase11-shared-tooling-manifest")
        case_count += 1

        duplicate = tmpdir / "duplicate"
        payload = fixture_payload()
        payload["exact_checks"].append(payload["exact_checks"][0])
        write(duplicate / FIXTURE_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(duplicate, "duplicate check name")
        case_count += 1

        malformed = tmpdir / "malformed"
        write(malformed / FIXTURE_PATH, "[]\n")
        expect_failure(malformed, "expected object")
        case_count += 1

        print("PHASE11_REQUIRED_VALIDATE_CHECKS_SELF_TEST=pass")
        print(f"PHASE11_REQUIRED_VALIDATE_CHECKS_SELF_TEST_CASE_COUNT={case_count}")
        print(f"PHASE11_REQUIRED_VALIDATE_CHECKS_REQUIRED_COUNT={len(REQUIRED_CHECKS)}")
        print(f"PHASE11_REQUIRED_VALIDATE_CHECKS_FIXTURE_CHECK_COUNT={check_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        check_count = run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_REQUIRED_VALIDATE_CHECKS=fail: {exc}")
        return 1

    print("PHASE11_REQUIRED_VALIDATE_CHECKS=pass")
    print(f"PHASE11_REQUIRED_VALIDATE_CHECKS_REQUIRED_COUNT={len(REQUIRED_CHECKS)}")
    print(f"PHASE11_REQUIRED_VALIDATE_CHECKS_FIXTURE_CHECK_COUNT={check_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

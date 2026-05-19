#!/usr/bin/env python3
"""Guard the rematerialized Phase 2 direct cross-route packet."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
MAKEFILE = ROOT / "zigux" / "Makefile"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
ROUTE = "make -C zigux phase2-cross"
SHA256_HEX_DIGEST_LENGTH = 64

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

EXPECTED_FIXTURE_PHASE = "Phase 2"
EXPECTED_FIXTURE_STATUS = "active"
EXPECTED_FIXTURE_FIELDS = frozenset(
    {"phase", "status", "route", "archive_target_scope", "cross_targets"}
)
EXPECTED_CROSS_TARGET_FIELDS = frozenset(
    {"target", "review_status", "validation_mode", "route"}
)
EXPECTED_CROSS_TARGETS = {
    "x86_64-linux": {
        "review_status": "pinned bootstrap archive",
        "validation_mode": "archive_required",
    },
    "aarch64-linux": {
        "review_status": "route contract only",
        "validation_mode": "route_contract_only",
    },
}
EXPECTED_CROSS_TARGET_ORDER = tuple(EXPECTED_CROSS_TARGETS)
ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")
EXPECTED_ISSUE_CODES = (
    "MISSING_MAKEFILE_LINE",
    "DUPLICATE_MAKEFILE_LINE",
    "ARCHIVE_HASH_SCOPE_MISMATCH",
    "ARCHIVE_HASH_SCOPE_ORDER_MISMATCH",
    "INVALID_FIXTURE_SHAPE",
    "UNEXPECTED_FIXTURE_FIELD",
    "INVALID_FIXTURE_FIELD",
    "INVALID_FIXTURE_ARCHIVE_SCOPE_ENTRY",
    "DUPLICATE_FIXTURE_ARCHIVE_SCOPE",
    "ARCHIVE_SCOPE_MISMATCH",
    "ARCHIVE_SCOPE_ORDER_MISMATCH",
    "INVALID_CROSS_TARGET_ENTRY",
    "UNEXPECTED_CROSS_TARGET_FIELD",
    "DUPLICATE_CROSS_TARGET",
    "UNEXPECTED_CROSS_TARGET",
    "INVALID_CROSS_TARGET_ROUTE",
    "INVALID_CROSS_TARGET_REVIEW_STATUS",
    "INVALID_CROSS_TARGET_MODE",
    "INVALID_CROSS_TARGET_EXPECTED_MODE",
    "CROSS_TARGET_SET_MISMATCH",
    "CROSS_TARGET_ORDER_MISMATCH",
    "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH",
    "ARCHIVE_REQUIRED_TARGET_ORDER_MISMATCH",
)

EXPECTED_SELF_TEST_CASE_COUNT = 35


class DuplicateJsonKeyError(ValueError):
    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.key = key


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path), object_pairs_hook=load_json_object)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    except DuplicateJsonKeyError as exc:
        raise SystemExit(f"duplicate json key in required file: {path}: {exc.key}") from exc


def load_json_object(pairs: list[tuple[object, object]]) -> dict[object, object]:
    payload: dict[object, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateJsonKeyError(str(key))
        payload[key] = value
    return payload


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def format_expected_actual(expected: list[str] | tuple[str, ...], actual: list[str]) -> str:
    return f"expected={','.join(expected)};actual={','.join(actual)}"


def load_toolchain_policy(root: Path) -> tuple[Path, dict[str, object]]:
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    payload = read_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")
    return policy_path, payload


def is_canonical_sha256(value: str) -> bool:
    return (
        len(value) == SHA256_HEX_DIGEST_LENGTH
        and all(character in "0123456789abcdef" for character in value)
    )


def load_archive_target_scope(root: Path) -> list[str]:
    policy_path, payload = load_toolchain_policy(root)
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")
    normalized: list[str] = []
    seen: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")
        target = value.strip()
        if target != value:
            raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")
        if target in seen:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {policy_path}: {target}")
        seen.add(target)
        normalized.append(target)
    return normalized


def load_archive_sha256_targets(root: Path) -> list[str]:
    policy_path, payload = load_toolchain_policy(root)
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in required file: {policy_path}")

    normalized: list[str] = []
    seen: set[str] = set()
    for key, value in archive_sha256.items():
        if not isinstance(key, str) or not key.strip():
            raise SystemExit(f"invalid archive_sha256 key in required file: {policy_path}")
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"invalid archive_sha256 value in required file: {policy_path}: {key}")
        target = key.strip()
        if target != key:
            raise SystemExit(f"invalid archive_sha256 key in required file: {policy_path}")
        if value != value.strip() or not is_canonical_sha256(value):
            raise SystemExit(f"invalid archive_sha256 value in required file: {policy_path}: {key}")
        if target in seen:
            raise SystemExit(f"duplicate archive_sha256 key in required file: {policy_path}: {target}")
        seen.add(target)
        normalized.append(target)
    return normalized


def normalize_fixture_archive_scope(fixture_scope: object) -> tuple[list[str] | None, list[tuple[str, str]]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(fixture_scope, list) or not fixture_scope:
        return None, [("INVALID_FIXTURE_FIELD", "archive_target_scope")]

    normalized: list[str] = []
    seen: set[str] = set()
    for index, value in enumerate(fixture_scope):
        if not isinstance(value, str) or not value.strip():
            issues.append(("INVALID_FIXTURE_ARCHIVE_SCOPE_ENTRY", f"index={index}"))
            continue
        target = value.strip()
        if target != value:
            issues.append(("INVALID_FIXTURE_ARCHIVE_SCOPE_ENTRY", f"index={index}"))
            continue
        if target in seen:
            issues.append(("DUPLICATE_FIXTURE_ARCHIVE_SCOPE", target))
            continue
        seen.add(target)
        normalized.append(target)
    if issues:
        return None, issues
    return normalized, []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    fixture = read_json(resolve_path(root, FIXTURE))
    archive_target_scope = load_archive_target_scope(root)
    archive_sha256_targets = load_archive_sha256_targets(root)

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    if set(archive_sha256_targets) != set(archive_target_scope):
        issues.append(
            (
                "ARCHIVE_HASH_SCOPE_MISMATCH",
                format_expected_actual(archive_target_scope, archive_sha256_targets),
            )
        )
    elif archive_sha256_targets != archive_target_scope:
        issues.append(
            (
                "ARCHIVE_HASH_SCOPE_ORDER_MISMATCH",
                format_expected_actual(archive_target_scope, archive_sha256_targets),
            )
        )

    if not isinstance(fixture, dict):
        issues.append(("INVALID_FIXTURE_SHAPE", "root"))
        return issues

    for field in sorted(set(fixture) - EXPECTED_FIXTURE_FIELDS):
        issues.append(("UNEXPECTED_FIXTURE_FIELD", field))

    if fixture.get("phase") != EXPECTED_FIXTURE_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != EXPECTED_FIXTURE_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))

    fixture_scope, fixture_scope_issues = normalize_fixture_archive_scope(
        fixture.get("archive_target_scope")
    )
    issues.extend(fixture_scope_issues)
    if fixture_scope is not None:
        if set(fixture_scope) != set(archive_target_scope):
            issues.append(
                (
                    "ARCHIVE_SCOPE_MISMATCH",
                    format_expected_actual(archive_target_scope, fixture_scope),
                )
            )
        elif fixture_scope != archive_target_scope:
            issues.append(
                (
                    "ARCHIVE_SCOPE_ORDER_MISMATCH",
                    format_expected_actual(archive_target_scope, fixture_scope),
                )
            )

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    seen_targets: set[str] = set()
    target_order: list[str] = []
    archive_required_target_order: list[str] = []
    archive_required_targets: set[str] = set()
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}"))
            continue
        raw_target = entry.get("target")
        entry_label = (
            raw_target
            if isinstance(raw_target, str) and raw_target.strip() and raw_target == raw_target.strip()
            else f"index={index}"
        )
        for field in sorted(set(entry) - EXPECTED_CROSS_TARGET_FIELDS):
            issues.append(("UNEXPECTED_CROSS_TARGET_FIELD", f"{entry_label}:{field}"))

        target = raw_target
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not isinstance(target, str) or not target.strip() or target != target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}:target"))
            continue
        if target in seen_targets:
            issues.append(("DUPLICATE_CROSS_TARGET", target))
        seen_targets.add(target)
        target_order.append(target)

        expected_entry = EXPECTED_CROSS_TARGETS.get(target)
        if expected_entry is None:
            issues.append(("UNEXPECTED_CROSS_TARGET", target))

        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))

        if not isinstance(review_status, str) or not review_status.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        elif review_status != review_status.strip() or (
            expected_entry is not None and review_status != expected_entry["review_status"]
        ):
            issues.append(("INVALID_CROSS_TARGET_REVIEW_STATUS", f"{target}:{review_status}"))

        if validation_mode not in ALLOWED_VALIDATION_MODES:
            issues.append(("INVALID_CROSS_TARGET_MODE", target))
            continue
        if expected_entry is not None and validation_mode != expected_entry["validation_mode"]:
            issues.append(("INVALID_CROSS_TARGET_EXPECTED_MODE", target))
        if validation_mode == "archive_required":
            archive_required_targets.add(target)
            archive_required_target_order.append(target)

    if seen_targets != set(EXPECTED_CROSS_TARGETS):
        issues.append(
            (
                "CROSS_TARGET_SET_MISMATCH",
                format_expected_actual(list(EXPECTED_CROSS_TARGET_ORDER), target_order),
            )
        )
    if target_order != list(EXPECTED_CROSS_TARGET_ORDER):
        issues.append(
            (
                "CROSS_TARGET_ORDER_MISMATCH",
                format_expected_actual(list(EXPECTED_CROSS_TARGET_ORDER), target_order),
            )
        )

    if archive_required_targets != set(archive_target_scope):
        issues.append(
            (
                "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH",
                format_expected_actual(archive_target_scope, archive_required_target_order),
            )
        )
    if archive_required_target_order != archive_target_scope:
        issues.append(
            (
                "ARCHIVE_REQUIRED_TARGET_ORDER_MISMATCH",
                format_expected_actual(archive_target_scope, archive_required_target_order),
            )
        )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    unexpected_codes = sorted(set(grouped) - set(EXPECTED_ISSUE_CODES))
    if unexpected_codes:
        raise AssertionError(f"unexpected issue codes missing from EXPECTED_ISSUE_CODES: {unexpected_codes}")

    print("PHASE2_DIRECT_CROSS_ROUTE=fail")
    for code in EXPECTED_ISSUE_CODES:
        values = grouped.get(code)
        if not values:
            continue
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, FIXTURE),
        json.dumps(
            {
                "phase": "Phase 2",
                "status": "active",
                "route": ROUTE,
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_route_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "x86_64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate archive_target_scope entry" in str(exc)
        else:
            raise AssertionError("duplicate policy archive_target_scope did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = [" x86_64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid archive_target_scope" in str(exc)
        else:
            raise AssertionError("whitespace policy archive_target_scope did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text(
            """{
  "phase": "Phase 2",
  "phase": "Phase 2",
  "channel": "0.17.0-dev.87+9b177a7d2",
  "minimum_version": "0.17.0-dev.87+9b177a7d2",
  "archive_sha256": {
    "x86_64-linux": "3333333333333333333333333333333333333333333333333333333333333333"
  },
  "upgrade_policy": {
    "channel_minimum_lockstep": true,
    "archive_target_scope": [
      "x86_64-linux"
    ],
    "required_make_routes": [
      "phase2-toolchain",
      "phase2-validate"
    ]
  }
}
""",
            encoding="utf-8",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate json key" in str(exc)
        else:
            raise AssertionError("duplicate policy json key did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_sha256"]["aarch64-linux"] = "4" * 64
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "ARCHIVE_HASH_SCOPE_MISMATCH",
            "expected=x86_64-linux;actual=x86_64-linux,aarch64-linux",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        del payload["archive_sha256"]["x86_64-linux"]
        payload["archive_sha256"]["aarch64-linux"] = "4" * 64
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert (
            "ARCHIVE_HASH_SCOPE_MISMATCH",
            "expected=x86_64-linux;actual=aarch64-linux",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_sha256"] = {" x86_64-linux": "3" * 64}
        try:
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid archive_sha256 key" in str(exc)
        else:
            raise AssertionError("whitespace archive_sha256 key did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_sha256"]["x86_64-linux"] = "3" * 63
        try:
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid archive_sha256 value" in str(exc)
        else:
            raise AssertionError("short archive_sha256 value did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_sha256"]["x86_64-linux"] = ("A" * 63) + " "
        try:
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid archive_sha256 value" in str(exc)
        else:
            raise AssertionError("whitespace-padded archive_sha256 value did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "aarch64-linux"]
        payload["archive_sha256"] = {
            "x86_64-linux": "3" * 64,
            "aarch64-linux": "4" * 64,
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux", "x86_64-linux"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "ARCHIVE_SCOPE_ORDER_MISMATCH",
            "expected=x86_64-linux,aarch64-linux;actual=aarch64-linux,x86_64-linux",
        ) in issues
        assert (
            "ARCHIVE_SCOPE_MISMATCH",
            "expected=x86_64-linux,aarch64-linux;actual=aarch64-linux,x86_64-linux",
        ) not in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "aarch64-linux"]
        payload["archive_sha256"] = {
            "aarch64-linux": "4" * 64,
            "x86_64-linux": "3" * 64,
        }
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "ARCHIVE_HASH_SCOPE_ORDER_MISMATCH",
            "expected=x86_64-linux,aarch64-linux;actual=aarch64-linux,x86_64-linux",
        ) in issues
        assert (
            "ARCHIVE_HASH_SCOPE_MISMATCH",
            "expected=x86_64-linux,aarch64-linux;actual=aarch64-linux,x86_64-linux",
        ) not in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        path.write_text(
            """{
  "phase": "Phase 2",
  "status": "active",
  "route": "make -C zigux phase2-cross",
  "archive_target_scope": [
    "x86_64-linux"
  ],
  "cross_targets": [
    {
      "target": "x86_64-linux",
      "review_status": "pinned bootstrap archive",
      "validation_mode": "archive_required",
      "validation_mode": "archive_required",
      "route": "make -C zigux phase2-cross"
    },
    {
      "target": "aarch64-linux",
      "review_status": "route contract only",
      "validation_mode": "route_contract_only",
      "route": "make -C zigux phase2-cross"
    }
  ]
}
""",
            encoding="utf-8",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate json key" in str(exc)
        else:
            raise AssertionError("duplicate fixture json key did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["unexpected"] = True
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_FIXTURE_FIELD", "unexpected") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["x86_64-linux", "x86_64-linux"]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_FIXTURE_ARCHIVE_SCOPE", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = [" x86_64-linux"]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_ARCHIVE_SCOPE_ENTRY", "index=0") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert (
            "ARCHIVE_SCOPE_MISMATCH",
            "expected=x86_64-linux;actual=aarch64-linux",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][0]["validation_mode"] = "route_contract_only"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("INVALID_CROSS_TARGET_EXPECTED_MODE", "x86_64-linux") in issues
        assert (
            "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH",
            "expected=x86_64-linux;actual=",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["review_status"] = "fresh archive"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_REVIEW_STATUS", "aarch64-linux:fresh archive") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["review_status"] = "route contract only "
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert (
            "INVALID_CROSS_TARGET_REVIEW_STATUS",
            "aarch64-linux:route contract only ",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["unexpected"] = True
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_CROSS_TARGET_FIELD", "aarch64-linux:unexpected") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["target"] = " aarch64-linux"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "index=1:target") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["target"] = "riscv64-linux"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNEXPECTED_CROSS_TARGET", "riscv64-linux") in issues
        assert (
            "CROSS_TARGET_SET_MISMATCH",
            "expected=x86_64-linux,aarch64-linux;actual=x86_64-linux,riscv64-linux",
        ) in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"] = [fixture["cross_targets"][1], fixture["cross_targets"][0]]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "CROSS_TARGET_ORDER_MISMATCH",
            "expected=x86_64-linux,aarch64-linux;actual=aarch64-linux,x86_64-linux",
        ) in issues
        assert (
            "ARCHIVE_REQUIRED_TARGET_ORDER_MISMATCH",
            "expected=x86_64-linux;actual=x86_64-linux",
        ) not in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"] = [
            fixture["cross_targets"][1],
            {
                "target": "x86_64-linux",
                "review_status": "pinned bootstrap archive",
                "validation_mode": "archive_required",
                "route": ROUTE,
            },
        ]
        fixture["archive_target_scope"] = ["x86_64-linux"]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert (
            "CROSS_TARGET_ORDER_MISMATCH",
            "expected=x86_64-linux,aarch64-linux;actual=aarch64-linux,x86_64-linux",
        ) in issues
        assert (
            "ARCHIVE_REQUIRED_TARGET_ORDER_MISMATCH",
            "expected=x86_64-linux;actual=x86_64-linux",
        ) not in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"].append(dict(fixture["cross_targets"][0]))
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("DUPLICATE_CROSS_TARGET", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["route"] = "make -C zigux phase2"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["review_status"] = ""
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "aarch64-linux:review_status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = "unexpected_mode"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_MODE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            exit_code = emit_issues(
                [
                    (
                        "CROSS_TARGET_ORDER_MISMATCH",
                        "expected=x86_64-linux,aarch64-linux;actual=aarch64-linux,x86_64-linux",
                    ),
                    ("ARCHIVE_SCOPE_MISMATCH", "expected=x86_64-linux;actual=aarch64-linux"),
                    ("MISSING_MAKEFILE_LINE", "phase2-cross:"),
                ]
            )
        assert exit_code == 1
        assert capture.getvalue().splitlines() == [
            "PHASE2_DIRECT_CROSS_ROUTE=fail",
            "MISSING_MAKEFILE_LINE_START",
            "phase2-cross:",
            "MISSING_MAKEFILE_LINE_END",
            "ARCHIVE_SCOPE_MISMATCH_START",
            "expected=x86_64-linux;actual=aarch64-linux",
            "ARCHIVE_SCOPE_MISMATCH_END",
            "CROSS_TARGET_ORDER_MISMATCH_START",
            "expected=x86_64-linux,aarch64-linux;actual=aarch64-linux,x86_64-linux",
            "CROSS_TARGET_ORDER_MISMATCH_END",
        ]
        checks_run += 1

        for primary_path in (TOOLCHAIN_POLICY, MAKEFILE, FIXTURE):
            build_self_test_root(root)
            resolve_path(root, primary_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
            else:
                raise AssertionError(f"missing primary file did not abort: {primary_path}")
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST=pass")
    print(f"PHASE2_DIRECT_CROSS_ROUTE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the rematerialized Phase 2 direct cross-route packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    fixture = read_json(resolve_path(args.root.resolve(), FIXTURE))
    assert isinstance(fixture, dict)
    cross_targets = fixture.get("cross_targets")
    assert isinstance(cross_targets, list)
    print("PHASE2_DIRECT_CROSS_ROUTE=pass")
    print(f"PHASE2_DIRECT_CROSS_ROUTE_TARGET_COUNT={len(cross_targets)}")
    print(f"PHASE2_DIRECT_CROSS_ROUTE_ARCHIVE_SCOPE_COUNT={len(load_archive_target_scope(args.root.resolve()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

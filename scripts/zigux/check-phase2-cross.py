#!/usr/bin/env python3
"""Guard the rematerialized Phase 2 direct cross-route packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
MAKEFILE = ROOT / "zigux" / "Makefile"
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
ROUTE = "make -C zigux phase2-cross"

MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

EXPECTED_FIXTURE_PHASE = "Phase 2"
EXPECTED_FIXTURE_STATUS = "active"
SUPPORTED_CROSS_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_REVIEW_STATUS_BY_TARGET = {
    "x86_64-linux": "pinned bootstrap archive",
    "aarch64-linux": "route contract only",
}
ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")
EXPECTED_FIXTURE_FIELDS = {
    "phase",
    "status",
    "route",
    "archive_target_scope",
    "cross_targets",
}
EXPECTED_CROSS_TARGET_FIELDS = {
    "target",
    "review_status",
    "validation_mode",
    "route",
}

EXPECTED_SELF_TEST_CASE_COUNT = 37


class DuplicateJsonKeyError(ValueError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path), object_pairs_hook=reject_duplicate_object_pairs)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    except DuplicateJsonKeyError as exc:
        raise SystemExit(f"duplicate json key in required file: {path}: {exc}") from exc


def reject_duplicate_object_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
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


def format_expected_actual(expected: list[str], actual: list[str]) -> str:
    return f"expected={','.join(expected)};actual={','.join(actual)}"


def load_archive_sha256_targets(root: Path) -> list[str]:
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    payload = read_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")
    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise SystemExit(f"invalid archive_sha256 in required file: {policy_path}")

    normalized: list[str] = []
    seen_targets: set[str] = set()
    for key, value in archive_sha256.items():
        if not isinstance(key, str) or not key or key != key.strip():
            raise SystemExit(f"invalid archive_sha256 key in required file: {policy_path}")
        if not isinstance(value, str) or not value or value != value.strip():
            raise SystemExit(f"invalid archive_sha256 value in required file: {policy_path}: {key}")
        target = key
        if target in seen_targets:
            raise SystemExit(f"duplicate archive_sha256 key in required file: {policy_path}: {target}")
        normalized.append(target)
        seen_targets.add(target)
    return normalized


def load_archive_target_scope(root: Path) -> list[str]:
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    payload = read_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")
    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")
    normalized: list[str] = []
    seen_targets: set[str] = set()
    for value in archive_target_scope:
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")
        target = value
        if target in seen_targets:
            raise SystemExit(f"duplicate archive_target_scope entry in required file: {policy_path}")
        if target not in SUPPORTED_CROSS_TARGETS:
            raise SystemExit("unsupported archive_target_scope targets in required file: " + target)
        normalized.append(target)
        seen_targets.add(target)
    return normalized


def collect_fixture_scope_issues(
    fixture_scope: object, archive_target_scope: list[str]
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(fixture_scope, list) or not fixture_scope:
        return [("INVALID_FIXTURE_FIELD", "archive_target_scope")]

    normalized_scope: list[str] = []
    seen_targets: set[str] = set()
    for index, value in enumerate(fixture_scope):
        if not isinstance(value, str) or not value.strip():
            issues.append(("INVALID_FIXTURE_ARCHIVE_SCOPE_ENTRY", f"index={index}"))
            continue
        if value != value.strip():
            issues.append(("WHITESPACE_PADDED_FIXTURE_ARCHIVE_SCOPE", f"index={index}:{value}"))
            continue
        if value in seen_targets:
            issues.append(("DUPLICATE_FIXTURE_ARCHIVE_SCOPE_TARGET", value))
            continue
        if value not in SUPPORTED_CROSS_TARGETS:
            issues.append(("UNSUPPORTED_FIXTURE_ARCHIVE_SCOPE_TARGET", value))
        normalized_scope.append(value)
        seen_targets.add(value)

    if normalized_scope != archive_target_scope:
        issues.append(("ARCHIVE_SCOPE_MISMATCH", ",".join(archive_target_scope)))
    return issues


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

    for key in fixture:
        if key not in EXPECTED_FIXTURE_FIELDS:
            issues.append(("UNEXPECTED_FIXTURE_FIELD", key))

    if fixture.get("phase") != EXPECTED_FIXTURE_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if fixture.get("status") != EXPECTED_FIXTURE_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if fixture.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))

    issues.extend(collect_fixture_scope_issues(fixture.get("archive_target_scope"), archive_target_scope))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    seen_targets: set[str] = set()
    target_order: list[str] = []
    archive_required_targets: set[str] = set()
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}"))
            continue
        for key in entry:
            if key not in EXPECTED_CROSS_TARGET_FIELDS:
                issues.append(("UNEXPECTED_CROSS_TARGET_FIELD", f"{index}:{key}"))

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not isinstance(target, str) or not target.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}:target"))
            continue
        if target != target.strip():
            issues.append(("WHITESPACE_PADDED_CROSS_TARGET", f"index={index}:{target}"))
            continue
        if target in seen_targets:
            issues.append(("DUPLICATE_CROSS_TARGET", target))
        seen_targets.add(target)
        target_order.append(target)

        if target not in SUPPORTED_CROSS_TARGETS:
            issues.append(("UNSUPPORTED_CROSS_TARGET", target))
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        expected_review_status = EXPECTED_REVIEW_STATUS_BY_TARGET.get(target)
        if not isinstance(review_status, str) or not review_status.strip():
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        elif review_status != review_status.strip():
            issues.append(("WHITESPACE_PADDED_CROSS_TARGET_REVIEW_STATUS", target))
        elif expected_review_status is not None and review_status != expected_review_status:
            issues.append(("INVALID_CROSS_TARGET_REVIEW_STATUS", f"{target}:{review_status}"))
        if not isinstance(validation_mode, str) or not validation_mode:
            issues.append(("INVALID_CROSS_TARGET_MODE", target))
            continue
        if validation_mode != validation_mode.strip():
            issues.append(("WHITESPACE_PADDED_CROSS_TARGET_MODE", target))
            continue
        if validation_mode not in ALLOWED_VALIDATION_MODES:
            issues.append(("INVALID_CROSS_TARGET_MODE", target))
            continue
        if validation_mode == "archive_required":
            archive_required_targets.add(target)

    if seen_targets != set(SUPPORTED_CROSS_TARGETS):
        issues.append(("CROSS_TARGET_SET_MISMATCH", ",".join(sorted(seen_targets))))
    if target_order != list(SUPPORTED_CROSS_TARGETS):
        issues.append(("CROSS_TARGET_ORDER_MISMATCH", ",".join(target_order)))

    if archive_required_targets != set(archive_target_scope):
        issues.append(("ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", ",".join(sorted(archive_required_targets))))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_DIRECT_CROSS_ROUTE=fail")
    for code, values in grouped.items():
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


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
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
            path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), marker, "# removed"), encoding="utf-8")
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in MAKEFILE_LINES:
            build_self_test_root(root)
            path = resolve_path(root, MAKEFILE)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        path.write_text(
            """{
  "phase": "Phase 2",
  "channel": "0.17.0-dev.87+9b177a7d2",
  "minimum_version": "0.17.0-dev.87+9b177a7d2",
  "archive_sha256": {"x86_64-linux": "%s"},
  "upgrade_policy": {
    "archive_target_scope": ["x86_64-linux"],
    "archive_target_scope": ["aarch64-linux"]
  }
}
""" % ("3" * 64),
            encoding="utf-8",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate json key in required file" in str(exc)
            assert "archive_target_scope" in str(exc)
        else:
            raise AssertionError("duplicate policy json key did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = [" x86_64-linux "]
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid archive_target_scope" in str(exc)
        else:
            raise AssertionError("whitespace-padded archive_target_scope entry did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "x86_64-linux"]
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate archive_target_scope entry" in str(exc)
        else:
            raise AssertionError("duplicate archive_target_scope entry did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["archive_sha256"] = {" x86_64-linux ": "3" * 64}
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid archive_sha256 key" in str(exc)
        else:
            raise AssertionError("whitespace-padded archive_sha256 key did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["archive_sha256"] = {"x86_64-linux": f" {'3' * 64} "}
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid archive_sha256 value" in str(exc)
        else:
            raise AssertionError("whitespace-padded archive_sha256 value did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        path.write_text(
            """{
  "phase": "Phase 2",
  "status": "active",
  "route": "make -C zigux phase2-cross",
  "archive_target_scope": ["x86_64-linux"],
  "cross_targets": [
    {
      "target": "x86_64-linux",
      "review_status": "pinned bootstrap archive",
      "validation_mode": "archive_required",
      "route": "make -C zigux phase2-cross",
      "route": "make -C zigux phase2"
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
            assert "duplicate json key in required file" in str(exc)
            assert "route" in str(exc)
        else:
            raise AssertionError("duplicate fixture json key did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        del policy["archive_sha256"]["x86_64-linux"]
        policy["archive_sha256"]["aarch64-linux"] = "4" * 64
        policy["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        fixture_path = resolve_path(root, FIXTURE)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture["cross_targets"][0]["validation_mode"] = "route_contract_only"
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["archive_sha256"]["riscv64-linux"] = "5" * 64
        policy["upgrade_policy"]["archive_target_scope"] = ["riscv64-linux"]
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "unsupported archive_target_scope targets" in str(exc)
        else:
            raise AssertionError("unsupported archive_target_scope targets did not abort")
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["archive_sha256"]["aarch64-linux"] = "4" * 64
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert (
            "ARCHIVE_HASH_SCOPE_MISMATCH",
            "expected=x86_64-linux;actual=x86_64-linux,aarch64-linux",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(path.read_text(encoding="utf-8"))
        del policy["archive_sha256"]["x86_64-linux"]
        policy["archive_sha256"]["aarch64-linux"] = "4" * 64
        path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        assert (
            "ARCHIVE_HASH_SCOPE_MISMATCH",
            "expected=x86_64-linux;actual=aarch64-linux",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = [" x86_64-linux "]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("WHITESPACE_PADDED_FIXTURE_ARCHIVE_SCOPE", "index=0: x86_64-linux ") in issues
        assert ("ARCHIVE_SCOPE_MISMATCH", "x86_64-linux") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("ARCHIVE_SCOPE_MISMATCH", "x86_64-linux") in collect_issues(root)
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
        fixture["cross_targets"][0]["unexpected"] = True
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_CROSS_TARGET_FIELD", "0:unexpected") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][0]["validation_mode"] = "route_contract_only"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", "") in collect_issues(root)
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
        fixture["cross_targets"][0]["review_status"] = " pinned bootstrap archive "
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("WHITESPACE_PADDED_CROSS_TARGET_REVIEW_STATUS", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][0]["review_status"] = "route contract only"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert (
            "INVALID_CROSS_TARGET_REVIEW_STATUS",
            "x86_64-linux:route contract only",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["review_status"] = "pinned bootstrap archive"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert (
            "INVALID_CROSS_TARGET_REVIEW_STATUS",
            "aarch64-linux:pinned bootstrap archive",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = " route_contract_only "
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("WHITESPACE_PADDED_CROSS_TARGET_MODE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = "unexpected_mode"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_MODE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"] = fixture["cross_targets"][:1]
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("CROSS_TARGET_SET_MISMATCH", "x86_64-linux") in collect_issues(root)
        assert ("CROSS_TARGET_ORDER_MISMATCH", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][0]["target"] = " x86_64-linux "
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("WHITESPACE_PADDED_CROSS_TARGET", "index=0: x86_64-linux ") in issues
        assert ("CROSS_TARGET_SET_MISMATCH", "aarch64-linux") in issues
        assert ("CROSS_TARGET_ORDER_MISMATCH", "aarch64-linux") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"][0]["target"] = "riscv64-linux"
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNSUPPORTED_CROSS_TARGET", "riscv64-linux") in issues
        assert ("CROSS_TARGET_SET_MISMATCH", "aarch64-linux,riscv64-linux") in issues
        assert ("CROSS_TARGET_ORDER_MISMATCH", "riscv64-linux,aarch64-linux") in issues
        assert ("ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", "riscv64-linux") in issues
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, FIXTURE)
        fixture = json.loads(path.read_text(encoding="utf-8"))
        fixture["cross_targets"].reverse()
        path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("CROSS_TARGET_ORDER_MISMATCH", "aarch64-linux,x86_64-linux") in issues
        assert ("CROSS_TARGET_SET_MISMATCH", "aarch64-linux,x86_64-linux") not in issues
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

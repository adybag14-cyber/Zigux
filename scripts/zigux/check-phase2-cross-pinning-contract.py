#!/usr/bin/env python3
"""Guard the Phase 2 cross packet through the toolchain pinning surfaces."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
TOOLCHAIN_PINNING = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py"
TOOLCHAIN_PIN_SCOPE = ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py"
CROSS_FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_ROUTE = "make -C zigux phase2-cross"
SUPPORTED_TARGETS = ("x86_64-linux", "aarch64-linux")
EXPECTED_REQUIRED_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")
ALLOWED_VALIDATION_MODES = ("archive_required", "route_contract_only")

BOOTSTRAP_NOTE_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`make -C zigux phase2-cross`",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-cross",
)

MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)

TOOLCHAIN_PINNING_MARKERS = (
    'ROOT / "scripts" / "zigux" / "check-phase2-cross.py",',
    'ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",',
    'ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",',
    '"required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],',
)

TOOLCHAIN_PIN_SCOPE_MARKERS = (
    '"`scripts/zigux/check-phase2-cross.py`",',
    '"`scripts/zigux/check-phase2-cross-selftest-alignment.py`",',
    '"`make -C zigux phase2-cross`",',
    'EXPECTED_REQUIRED_ROUTES = ["phase2-toolchain", "phase2-validate", "phase2-cross"]',
)


class DuplicateJsonKeyError(ValueError):
    pass


def reject_duplicate_object_pairs(pairs: list[tuple[object, object]]) -> dict[object, object]:
    payload: dict[object, object] = {}
    for key, value in pairs:
        if key in payload:
            raise DuplicateJsonKeyError(str(key))
        payload[key] = value
    return payload


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def is_strict_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def load_policy_scope(root: Path) -> list[str]:
    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    payload = read_json(policy_path)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid policy payload in required file: {policy_path}")

    if payload.get("phase") != EXPECTED_PHASE:
        raise SystemExit(f"invalid phase in required file: {policy_path}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")

    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_ROUTES):
        raise SystemExit(f"invalid required_make_routes in required file: {policy_path}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_target_scope, list) or not archive_target_scope:
        raise SystemExit(f"invalid archive_target_scope in required file: {policy_path}")

    normalized: list[str] = []
    seen_targets: set[str] = set()
    for value in archive_target_scope:
        if not is_strict_non_empty_string(value):
            raise SystemExit(f"invalid archive_target_scope entry in required file: {policy_path}")
        if value in seen_targets:
            raise SystemExit(
                f"duplicate archive_target_scope entry in required file: {policy_path}: {value}"
            )
        if value not in SUPPORTED_TARGETS:
            raise SystemExit(f"unsupported archive_target_scope target in required file: {policy_path}: {value}")
        seen_targets.add(value)
        normalized.append(value)
    return normalized


def collect_fixture_issues(root: Path) -> list[tuple[str, str]]:
    fixture_path = resolve_path(root, CROSS_FIXTURE)
    payload = read_json(fixture_path)
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_FIXTURE_SHAPE", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != EXPECTED_ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))

    policy_scope = load_policy_scope(root)
    fixture_scope = payload.get("archive_target_scope")
    if fixture_scope != policy_scope:
        issues.append(("ARCHIVE_SCOPE_MISMATCH", repr(fixture_scope)))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list) or not cross_targets:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    seen_targets: set[str] = set()
    target_order: list[str] = []
    archive_required_targets: set[str] = set()
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}:{type(entry).__name__}"))
            continue

        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")

        if not is_strict_non_empty_string(target):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}:target"))
            continue
        if target in seen_targets:
            issues.append(("DUPLICATE_CROSS_TARGET", target))
        seen_targets.add(target)
        target_order.append(target)

        if target not in SUPPORTED_TARGETS:
            issues.append(("UNSUPPORTED_CROSS_TARGET", target))
        if route != EXPECTED_ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if not is_strict_non_empty_string(review_status):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if validation_mode not in ALLOWED_VALIDATION_MODES:
            issues.append(("INVALID_CROSS_TARGET_MODE", f"{target}:{validation_mode!r}"))
            continue
        if validation_mode == "archive_required":
            archive_required_targets.add(target)

    if target_order != list(SUPPORTED_TARGETS):
        issues.append(("TARGET_ORDER_MISMATCH", repr(target_order)))
    if archive_required_targets != set(policy_scope):
        issues.append(("ARCHIVE_REQUIRED_TARGET_SET_MISMATCH", repr(sorted(archive_required_targets))))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, BOOTSTRAP_NOTES)),
            BOOTSTRAP_NOTE_MARKERS,
            "MISSING_BOOTSTRAP_NOTE_MARKERS",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, WORKFLOW)),
            WORKFLOW_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )
    issues.extend(
        collect_exact_line_issues(
            read_text(resolve_path(root, MAKEFILE)),
            MAKEFILE_LINES,
            "MISSING_MAKEFILE_LINE",
            "DUPLICATE_MAKEFILE_LINE",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TOOLCHAIN_PINNING)),
            TOOLCHAIN_PINNING_MARKERS,
            "MISSING_TOOLCHAIN_PINNING_MARKERS",
        )
    )
    issues.extend(
        collect_missing_markers(
            read_text(resolve_path(root, TOOLCHAIN_PIN_SCOPE)),
            TOOLCHAIN_PIN_SCOPE_MARKERS,
            "MISSING_TOOLCHAIN_PIN_SCOPE_MARKERS",
        )
    )
    issues.extend(collect_fixture_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_PINNING_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    write_text(resolve_path(root, BOOTSTRAP_NOTES), "\n".join(["# notes", *BOOTSTRAP_NOTE_MARKERS]) + "\n")
    write_text(resolve_path(root, WORKFLOW), "\n".join(["name: zigux-bootstrap", *WORKFLOW_LINES]) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(MAKEFILE_LINES) + "\n")
    write_text(resolve_path(root, TOOLCHAIN_PINNING), "\n".join(["# pinning", *TOOLCHAIN_PINNING_MARKERS]) + "\n")
    write_text(resolve_path(root, TOOLCHAIN_PIN_SCOPE), "\n".join(["# pin-scope", *TOOLCHAIN_PIN_SCOPE_MARKERS]) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(EXPECTED_REQUIRED_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve_path(root, CROSS_FIXTURE),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
                "route": EXPECTED_ROUTE,
                "archive_target_scope": ["x86_64-linux"],
                "cross_targets": [
                    {
                        "target": "x86_64-linux",
                        "review_status": "pinned bootstrap archive",
                        "validation_mode": "archive_required",
                        "route": EXPECTED_ROUTE,
                    },
                    {
                        "target": "aarch64-linux",
                        "review_status": "route contract only",
                        "validation_mode": "route_contract_only",
                        "route": EXPECTED_ROUTE,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
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
    expected_case_count = (
        1
        + len(BOOTSTRAP_NOTE_MARKERS)
        + len(WORKFLOW_LINES)
        + len(WORKFLOW_LINES)
        + len(MAKEFILE_LINES)
        + len(MAKEFILE_LINES)
        + len(TOOLCHAIN_PINNING_MARKERS)
        + len(TOOLCHAIN_PIN_SCOPE_MARKERS)
        + 14
        + 7
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_pinning_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in BOOTSTRAP_NOTE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, BOOTSTRAP_NOTES)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_BOOTSTRAP_NOTE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 scripts/zigux/other.py"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_LINES:
            build_self_test_root(root)
            path = resolve_path(root, WORKFLOW)
            path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
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

        for marker in TOOLCHAIN_PINNING_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TOOLCHAIN_PINNING)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TOOLCHAIN_PINNING_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        for marker in TOOLCHAIN_PIN_SCOPE_MARKERS:
            build_self_test_root(root)
            path = resolve_path(root, TOOLCHAIN_PIN_SCOPE)
            path.write_text(replace_once(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            assert ("MISSING_TOOLCHAIN_PIN_SCOPE_MARKERS", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["phase"] = "Phase X"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "phase") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["status"] = "blocked"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["route"] = "make -C zigux phase2"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "route") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_target_scope"] = ["aarch64-linux"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("ARCHIVE_SCOPE_MISMATCH", "['aarch64-linux']") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][1]["validation_mode"] = "archive_required"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert any(code == "ARCHIVE_REQUIRED_TARGET_SET_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"].append(dict(payload["cross_targets"][0]))
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_CROSS_TARGET", "x86_64-linux") in issues
        assert any(code == "TARGET_ORDER_MISMATCH" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["target"] = "riscv64-linux"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("UNSUPPORTED_CROSS_TARGET", "riscv64-linux") in issues
        assert any(code == "TARGET_ORDER_MISMATCH" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["route"] = "make -C zigux phase2-toolchain"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "x86_64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"][0]["review_status"] = ""
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "x86_64-linux:review_status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve_path(root, CROSS_FIXTURE)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["cross_targets"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "cross_targets") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing phase2-cross route did not abort")

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "x86_64-linux"]
        policy_path.write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate archive_target_scope entry" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate archive scope did not abort")

        build_self_test_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid policy json did not abort")

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_FIXTURE)
        fixture_path.write_text("{\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid json in required file" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("invalid fixture json did not abort")

        for path in (
            BOOTSTRAP_NOTES,
            WORKFLOW,
            MAKEFILE,
            TOOLCHAIN_POLICY,
            TOOLCHAIN_PINNING,
            TOOLCHAIN_PIN_SCOPE,
            CROSS_FIXTURE,
        ):
            build_self_test_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    assert checks_run == expected_case_count
    print("PHASE2_CROSS_PINNING_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_PINNING_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 cross packet stays aligned through the toolchain pinning surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    policy_scope = load_policy_scope(args.root.resolve())
    print("PHASE2_CROSS_PINNING_CONTRACT=pass")
    print(f"PHASE2_CROSS_PINNING_CONTRACT_SCOPE_COUNT={len(policy_scope)}")
    print(f"PHASE2_CROSS_PINNING_CONTRACT_TARGET_COUNT={len(SUPPORTED_TARGETS)}")
    print(f"PHASE2_CROSS_PINNING_CONTRACT_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

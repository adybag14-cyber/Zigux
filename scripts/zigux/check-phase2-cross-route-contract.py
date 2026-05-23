#!/usr/bin/env python3
"""Guard the Phase 2 cross-route contract across policy, note, and Makefile."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
PHASE2_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
MAKEFILE = ROOT / "zigux" / "Makefile"
CROSS_TARGETS = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"

ROUTE = "make -C zigux phase2-cross"
EXPECTED_PHASE = "Phase 2"
EXPECTED_STATUS = "active"
EXPECTED_REQUIRED_MAKE_ROUTES = (
    "phase2-toolchain",
    "phase2-validate",
    "phase2-cross",
)
EXPECTED_ARCHIVE_SCOPE = ("x86_64-linux",)
EXPECTED_CROSS_TARGETS = (
    ("x86_64-linux", "archive_required"),
    ("aarch64-linux", "route_contract_only"),
)

REQUIRED_NOTE_MARKERS = (
    "`phase2-toolchain`, `phase2-validate`, and `phase2-cross` as the required Linux-style make routes",
    "`zigux/tests/fixtures/phase2_cross_targets.json` keeps the rematerialized direct cross-route packet explicit",
    "`make -C zigux phase2-cross`",
)
REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
)

EXPECTED_SELF_TEST_CASE_COUNT = 18


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def no_duplicate_object_pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path), object_pairs_hook=no_duplicate_object_pairs_hook)
    except ValueError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


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


def load_policy_contract(root: Path) -> dict[str, object]:
    payload = read_json(resolve_path(root, TOOLCHAIN_POLICY))
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")
    if payload.get("phase") != EXPECTED_PHASE:
        raise SystemExit(f"invalid phase in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {resolve_path(root, TOOLCHAIN_POLICY)}")

    archive_target_scope = upgrade_policy.get("archive_target_scope")
    if archive_target_scope != list(EXPECTED_ARCHIVE_SCOPE):
        raise SystemExit(
            f"invalid archive_target_scope in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )

    required_make_routes = upgrade_policy.get("required_make_routes")
    if required_make_routes != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise SystemExit(
            f"invalid required_make_routes in required file: {resolve_path(root, TOOLCHAIN_POLICY)}"
        )

    return {
        "archive_target_scope": list(EXPECTED_ARCHIVE_SCOPE),
        "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
    }


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    policy = load_policy_contract(root)

    notes_text = read_text(resolve_path(root, PHASE2_NOTES))
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in notes_text:
            issues.append(("MISSING_NOTE_MARKER", marker))

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    payload = read_json(resolve_path(root, CROSS_TARGETS))
    if not isinstance(payload, dict):
        issues.append(("INVALID_FIXTURE_SHAPE", type(payload).__name__))
        return issues

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_FIXTURE_FIELD", "phase"))
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(("INVALID_FIXTURE_FIELD", "status"))
    if payload.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_FIELD", "route"))
    if payload.get("archive_target_scope") != policy["archive_target_scope"]:
        issues.append(("INVALID_FIXTURE_FIELD", "archive_target_scope"))

    cross_targets = payload.get("cross_targets")
    if not isinstance(cross_targets, list):
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
        return issues

    actual_targets: list[tuple[str, str]] = []
    for index, entry in enumerate(cross_targets):
        if not isinstance(entry, dict):
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}"))
            continue
        if tuple(entry.keys()) != ("target", "review_status", "validation_mode", "route"):
            issues.append(("UNEXPECTED_CROSS_TARGET_KEYS", f"index={index}:{','.join(entry.keys())}"))
        target = entry.get("target")
        review_status = entry.get("review_status")
        validation_mode = entry.get("validation_mode")
        route = entry.get("route")
        if not isinstance(target, str) or not target:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"index={index}:target"))
            continue
        if not isinstance(review_status, str) or not review_status:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:review_status"))
        if route != ROUTE:
            issues.append(("INVALID_CROSS_TARGET_ROUTE", target))
        if not isinstance(validation_mode, str) or not validation_mode:
            issues.append(("INVALID_CROSS_TARGET_ENTRY", f"{target}:validation_mode"))
            continue
        actual_targets.append((target, validation_mode))

    if tuple(actual_targets) != EXPECTED_CROSS_TARGETS:
        issues.append(
            (
                "INVALID_CROSS_TARGET_MATRIX",
                json.dumps(actual_targets, ensure_ascii=True),
            )
        )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CROSS_ROUTE_CONTRACT=fail")
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
                "phase": EXPECTED_PHASE,
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": list(EXPECTED_ARCHIVE_SCOPE),
                    "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(resolve_path(root, PHASE2_NOTES), "\n".join(REQUIRED_NOTE_MARKERS) + "\n")
    write_text(resolve_path(root, MAKEFILE), "\n".join(REQUIRED_MAKEFILE_LINES) + "\n")
    write_text(
        resolve_path(root, CROSS_TARGETS),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "status": EXPECTED_STATUS,
                "route": ROUTE,
                "archive_target_scope": list(EXPECTED_ARCHIVE_SCOPE),
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
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_route_contract_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        notes_path = resolve_path(root, PHASE2_NOTES)
        notes_path.write_text(notes_path.read_text(encoding="utf-8").replace(REQUIRED_NOTE_MARKERS[1], ""), encoding="utf-8")
        assert ("MISSING_NOTE_MARKER", REQUIRED_NOTE_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_MAKEFILE_LINES[:3]:
            build_self_test_root(root)
            makefile_path = resolve_path(root, MAKEFILE)
            makefile_path.write_text(
                replace_exact_line(makefile_path.read_text(encoding="utf-8"), marker, "# removed"),
                encoding="utf-8",
            )
            assert ("MISSING_MAKEFILE_LINE", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0]),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_MAKEFILE_LINE",
            f"{REQUIRED_MAKEFILE_LINES[0]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        toolchain_path = resolve_path(root, TOOLCHAIN_POLICY)
        toolchain = json.loads(toolchain_path.read_text(encoding="utf-8"))
        toolchain["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        toolchain_path.write_text(json.dumps(toolchain, indent=2) + "\n", encoding="utf-8")
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "invalid required_make_routes" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("required_make_routes drift did not abort")

        build_self_test_root(root)
        toolchain_path = resolve_path(root, TOOLCHAIN_POLICY)
        toolchain_path.write_text(
            '{\n  "phase": "Phase 2",\n  "phase": "Phase 2"\n}\n',
            encoding="utf-8",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate key" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate policy key did not abort")

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_TARGETS)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["archive_target_scope"] = ["aarch64-linux"]
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_FIXTURE_FIELD", "archive_target_scope") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_TARGETS)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["route"] = "make -C zigux phase2"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ROUTE", "aarch64-linux") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_TARGETS)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["review_status"] = ""
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_ENTRY", "aarch64-linux:review_status") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_TARGETS)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["validation_mode"] = "archive_required"
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_CROSS_TARGET_MATRIX", '[["x86_64-linux", "archive_required"], ["aarch64-linux", "archive_required"]]') in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_TARGETS)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][0]["extra"] = True
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        assert ("UNEXPECTED_CROSS_TARGET_KEYS", "index=0:target,review_status,validation_mode,route,extra") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture_path = resolve_path(root, CROSS_TARGETS)
        fixture_path.write_text(
            '{\n  "phase": "Phase 2",\n  "phase": "Phase 2",\n  "status": "active"\n}\n',
            encoding="utf-8",
        )
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "duplicate key" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("duplicate fixture key did not abort")

        for primary_path in (TOOLCHAIN_POLICY, PHASE2_NOTES, MAKEFILE, CROSS_TARGETS):
            build_self_test_root(root)
            resolve_path(root, primary_path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
            else:
                raise AssertionError(f"missing required file did not abort: {primary_path}")
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_ROUTE_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 cross-route contract stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_ROUTE_CONTRACT=pass")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_TARGET_COUNT={len(EXPECTED_CROSS_TARGETS)}")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_ARCHIVE_SCOPE_COUNT={len(EXPECTED_ARCHIVE_SCOPE)}")
    print(f"PHASE2_CROSS_ROUTE_CONTRACT_REQUIRED_ROUTE_COUNT={len(EXPECTED_REQUIRED_MAKE_ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

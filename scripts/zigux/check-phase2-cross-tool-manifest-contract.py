#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
FIXTURE = Path("zigux/tests/fixtures/phase2_cross_targets.json")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
BOOTSTRAP_NOTE = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")

ROUTE = "make -C zigux phase2-cross"
REQUIRED_MAKE_ROUTE = "phase2-cross"
REQUIRED_CHECKERS = (
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
)
REQUIRED_MANIFEST_CROSS_SUPPORT = (
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
REQUIRED_NOTE_MARKERS = (
    "direct cross-route checker",
    "phase2_cross_targets fixture",
    "phase2-cross",
)
REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: make -C zigux phase2-cross",
)
REQUIRED_MAKEFILE_LINES = (
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
)
EXPECTED_SELF_TEST_CASE_COUNT = 20


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


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


def load_manifest(root: Path) -> dict:
    payload = read_json(root / MANIFEST)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {root / MANIFEST}")
    return payload


def load_policy(root: Path) -> dict:
    payload = read_json(root / POLICY)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {root / POLICY}")
    return payload


def load_fixture(root: Path) -> dict:
    payload = read_json(root / FIXTURE)
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {root / FIXTURE}")
    return payload


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    manifest = load_manifest(root)
    policy = load_policy(root)
    fixture = load_fixture(root)
    makefile_text = read_text(root / MAKEFILE)
    workflow_text = read_text(root / WORKFLOW)
    bootstrap_note_text = read_text(root / BOOTSTRAP_NOTE)
    scripts_readme_text = read_text(root / SCRIPTS_README)
    tests_readme_text = read_text(root / TESTS_README)

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_FIELD", "present_surfaces"))
        return issues

    cross_route_support = present_surfaces.get("cross_route_support")
    if cross_route_support != list(REQUIRED_MANIFEST_CROSS_SUPPORT):
        issues.append(("INVALID_MANIFEST_FIELD", "cross_route_support"))

    checkers = present_surfaces.get("checkers")
    if not isinstance(checkers, list):
        issues.append(("INVALID_MANIFEST_FIELD", "checkers"))
    else:
        for checker in REQUIRED_CHECKERS:
            count = checkers.count(checker)
            if count == 0:
                issues.append(("MISSING_CHECKER_ENTRY", checker))
            elif count != 1:
                issues.append(("DUPLICATE_CHECKER_ENTRY", f"{checker}:count={count}"))

    make_wrappers = present_surfaces.get("make_wrappers")
    if not isinstance(make_wrappers, list) or ROUTE not in make_wrappers:
        issues.append(("MISSING_MANIFEST_ROUTE", ROUTE))

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY_FIELD", "upgrade_policy"))
    else:
        required_make_routes = upgrade_policy.get("required_make_routes")
        if not isinstance(required_make_routes, list) or REQUIRED_MAKE_ROUTE not in required_make_routes:
            issues.append(("MISSING_POLICY_ROUTE", REQUIRED_MAKE_ROUTE))

    if fixture.get("route") != ROUTE:
        issues.append(("INVALID_FIXTURE_ROUTE", ROUTE))

    cross_targets = fixture.get("cross_targets")
    if not isinstance(cross_targets, list) or len(cross_targets) < 2:
        issues.append(("INVALID_FIXTURE_FIELD", "cross_targets"))
    else:
        for target in cross_targets:
            if not isinstance(target, dict) or target.get("route") != ROUTE:
                issues.append(("INVALID_CROSS_TARGET_ROUTE", ROUTE))
                break

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in bootstrap_note_text:
            issues.append(("MISSING_BOOTSTRAP_NOTE_MARKER", marker))
        if marker not in scripts_readme_text:
            issues.append(("MISSING_SCRIPTS_README_MARKER", marker))
        if marker not in tests_readme_text:
            issues.append(("MISSING_TESTS_README_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
        "workflow": ".github/workflows/zigux-bootstrap.yml",
        "present_surfaces": {
            "checkers": [
                "scripts/zigux/check-zig-toolchain.py",
                *REQUIRED_CHECKERS,
            ],
            "cross_route_support": list(REQUIRED_MANIFEST_CROSS_SUPPORT),
            "make_wrappers": [
                "zigux/Makefile",
                "make -C zigux phase2-toolchain",
                ROUTE,
            ],
        },
        "repo_reality_gaps": [],
        "notes": ["placeholder"],
    }
    policy = {
        "phase": "Phase 2",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "minimum_version": "0.17.0-dev.87+9b177a7d2",
        "archive_sha256": {"x86_64-linux": "3" * 64},
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": ["x86_64-linux"],
            "required_make_routes": ["phase2-toolchain", "phase2-validate", REQUIRED_MAKE_ROUTE],
        },
    }
    fixture = {
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
    }
    makefile_text = "\n".join(
        (
            "PYTHON ?= python3",
            "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
            "",
            *REQUIRED_MAKEFILE_LINES,
        )
    ) + "\n"
    workflow_text = "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES)) + "\n"
    note_text = (
        "This packet keeps the direct cross-route checker, phase2_cross_targets fixture, "
        "and phase2-cross route explicit.\n"
    )

    write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
    write_text(root / POLICY, json.dumps(policy, indent=2) + "\n")
    write_text(root / FIXTURE, json.dumps(fixture, indent=2) + "\n")
    write_text(root / MAKEFILE, makefile_text)
    write_text(root / WORKFLOW, workflow_text)
    write_text(root / BOOTSTRAP_NOTE, note_text)
    write_text(root / SCRIPTS_README, note_text)
    write_text(root / TESTS_README, note_text)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_cross_tool_manifest_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        manifest_path = root / MANIFEST
        policy_path = root / POLICY
        fixture_path = root / FIXTURE
        makefile_path = root / MAKEFILE
        workflow_path = root / WORKFLOW

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["cross_route_support"] = ["scripts/zigux/check-phase2-cross.py"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("INVALID_MANIFEST_FIELD", "cross_route_support") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["checkers"].remove(REQUIRED_CHECKERS[0])
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_CHECKER_ENTRY", REQUIRED_CHECKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["checkers"].append(REQUIRED_CHECKERS[0])
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("DUPLICATE_CHECKER_ENTRY", f"{REQUIRED_CHECKERS[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["present_surfaces"]["make_wrappers"].remove(ROUTE)
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_MANIFEST_ROUTE", ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate"]
        write_text(policy_path, json.dumps(policy, indent=2) + "\n")
        assert ("MISSING_POLICY_ROUTE", REQUIRED_MAKE_ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["route"] = "make -C zigux phase2"
        write_text(fixture_path, json.dumps(fixture, indent=2) + "\n")
        assert ("INVALID_FIXTURE_ROUTE", ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["cross_targets"][1]["route"] = "make -C zigux phase2"
        write_text(fixture_path, json.dumps(fixture, indent=2) + "\n")
        assert ("INVALID_CROSS_TARGET_ROUTE", ROUTE) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0], "# removed"),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path.write_text(
            duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[1]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_MAKEFILE_LINE", f"{REQUIRED_MAKEFILE_LINES[1]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "run: python3 other.py"),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[-1]),
            encoding="utf-8",
        )
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[-1]}:count=2") in collect_issues(root)
        checks_run += 1

        for rel in (BOOTSTRAP_NOTE, SCRIPTS_README, TESTS_README):
            build_self_test_root(root)
            path = root / rel
            path.write_text("phase2-cross only\n", encoding="utf-8")
            expected_code = {
                BOOTSTRAP_NOTE: "MISSING_BOOTSTRAP_NOTE_MARKER",
                SCRIPTS_README: "MISSING_SCRIPTS_README_MARKER",
                TESTS_README: "MISSING_TESTS_README_MARKER",
            }[rel]
            assert (expected_code, "direct cross-route checker") in collect_issues(root)
            checks_run += 1

        for rel in (MANIFEST, POLICY, FIXTURE, MAKEFILE, WORKFLOW):
            build_self_test_root(root)
            (root / rel).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {rel}")

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 tool manifest aligned with the current cross-route packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CROSS_TOOL_MANIFEST_CONTRACT=pass")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_CHECKER_COUNT={len(REQUIRED_CHECKERS)}")
    print(f"PHASE2_CROSS_TOOL_MANIFEST_CONTRACT_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

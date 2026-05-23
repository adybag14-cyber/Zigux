#!/usr/bin/env python3
"""Guard the current Lane 03 Phase 2 toolchain make-route bundle."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE = Path("zigux/Makefile")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")

REQUIRED_PATHS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
)

REQUIRED_MAKE_ROUTE = "phase2-toolchain"
REQUIRED_POLICY_ROUTES = ("phase2-toolchain", "phase2-validate", "phase2-cross")
REQUIRED_WORKFLOW_LINE = "run: make -C zigux phase2-toolchain"
PHONY_MARKER = ".PHONY: phase1-route-summary phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2"

REQUIRED_TARGET_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel": "0.17.0-dev.87+9b177a7d2",
    "minimum_version": "0.17.0-dev.87+9b177a7d2",
    "archive_sha256": {
        "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
    },
    "upgrade_policy": {
        "channel_minimum_lockstep": True,
        "archive_target_scope": ["x86_64-linux"],
        "required_make_routes": list(REQUIRED_POLICY_ROUTES),
    },
}


def resolve_path(root: Path, rel: Path | str) -> Path:
    return root / Path(rel)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def extract_target_block(makefile_text: str, target: str) -> list[str] | None:
    lines = makefile_text.splitlines()
    start = None
    prefix = f"{target}:"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            start = index
            break
    if start is None:
        return None

    block: list[str] = []
    for line in lines[start + 1 :]:
        if not line.startswith("\t"):
            break
        block.append(line.strip())
    return block


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def remove_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    policy_path = resolve_path(root, POLICY)
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        return [("INVALID_POLICY_JSON", exc.msg)]

    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]

    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))

    if payload.get("channel") != EXPECTED_POLICY["channel"]:
        issues.append(("POLICY_CHANNEL_MISMATCH", repr(payload.get("channel"))))

    if payload.get("minimum_version") != EXPECTED_POLICY["minimum_version"]:
        issues.append(("POLICY_MINIMUM_VERSION_MISMATCH", repr(payload.get("minimum_version"))))

    if payload.get("archive_sha256") != EXPECTED_POLICY["archive_sha256"]:
        issues.append(("POLICY_ARCHIVE_SHA256_MISMATCH", repr(payload.get("archive_sha256"))))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade_policy.get("channel_minimum_lockstep"))))

    if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["upgrade_policy"]["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(upgrade_policy.get("archive_target_scope"))))

    if upgrade_policy.get("required_make_routes") != list(REQUIRED_POLICY_ROUTES):
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", repr(upgrade_policy.get("required_make_routes"))))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    makefile_text = read_text(resolve_path(root, MAKEFILE))

    for rel in REQUIRED_PATHS:
        if not resolve_path(root, rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    issues.extend(collect_policy_issues(root))

    phony_count = count_exact_lines(makefile_text, PHONY_MARKER)
    if phony_count == 0:
        issues.append(("MISSING_PHONY_MARKER", PHONY_MARKER))
    elif phony_count != 1:
        issues.append(("DUPLICATE_PHONY_MARKER", f"{PHONY_MARKER}:count={phony_count}"))

    workflow_count = count_exact_lines(workflow_text, REQUIRED_WORKFLOW_LINE)
    if workflow_count == 0:
        issues.append(("MISSING_WORKFLOW_ROUTE_LINE", REQUIRED_WORKFLOW_LINE))
    elif workflow_count != 1:
        issues.append(("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{REQUIRED_WORKFLOW_LINE}:count={workflow_count}"))

    block = extract_target_block(makefile_text, REQUIRED_MAKE_ROUTE)
    if block is None:
        issues.append(("MISSING_TARGET_BLOCK", f"{REQUIRED_MAKE_ROUTE}:"))
        return issues

    if len(block) != len(REQUIRED_TARGET_LINES):
        issues.append(("TARGET_BLOCK_LINE_COUNT_MISMATCH", f"actual={len(block)}:expected={len(REQUIRED_TARGET_LINES)}"))

    for marker in REQUIRED_TARGET_LINES:
        count = block.count(marker)
        if count == 0:
            issues.append(("MISSING_TARGET_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_TARGET_LINE", f"{marker}:count={count}"))

    for expected, actual in zip(REQUIRED_TARGET_LINES, block):
        if expected != actual:
            issues.append(("TARGET_LINE_ORDER_MISMATCH", f"expected={expected}::actual={actual}"))
            break

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("LANE03_PHASE2_TOOLCHAIN_ROUTE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        write_text(resolve_path(root, rel), "present\n")

    write_text(resolve_path(root, POLICY), json.dumps(EXPECTED_POLICY, indent=2) + "\n")

    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Run current Phase 2 toolchain make route",
                f"        {REQUIRED_WORKFLOW_LINE}",
            )
        )
        + "\n",
    )

    makefile_lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "ZIGUX_ROOT := ..",
        "",
        PHONY_MARKER,
        "",
        "phase2-toolchain:",
    ]
    makefile_lines.extend(f"\t{line}" for line in REQUIRED_TARGET_LINES)
    makefile_lines.extend(
        (
            "",
            "phase2-tools:",
            "\t@true",
        )
    )
    write_text(resolve_path(root, MAKEFILE), "\n".join(makefile_lines) + "\n")


def run_self_test() -> int:
    checks = 0
    expected_checks = 13

    with tempfile.TemporaryDirectory(prefix="lane03_phase2_toolchain_route_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(remove_exact_line(read_text(workflow_path), REQUIRED_WORKFLOW_LINE), encoding="utf-8")
        assert ("MISSING_WORKFLOW_ROUTE_LINE", REQUIRED_WORKFLOW_LINE) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(duplicate_exact_line(read_text(workflow_path), REQUIRED_WORKFLOW_LINE), encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_ROUTE_LINE", f"{REQUIRED_WORKFLOW_LINE}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(remove_exact_line(read_text(makefile_path), PHONY_MARKER), encoding="utf-8")
        assert ("MISSING_PHONY_MARKER", PHONY_MARKER) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        marker = REQUIRED_TARGET_LINES[3]
        makefile_path.write_text(remove_exact_line(read_text(makefile_path), marker), encoding="utf-8")
        assert ("MISSING_TARGET_LINE", marker) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        marker = REQUIRED_TARGET_LINES[0]
        makefile_path.write_text(duplicate_exact_line(read_text(makefile_path), marker), encoding="utf-8")
        issues = collect_issues(root)
        assert ("DUPLICATE_TARGET_LINE", f"{marker}:count=2") in issues
        assert any(code == "TARGET_BLOCK_LINE_COUNT_MISMATCH" for code, _ in issues)
        checks += 1

        build_sample_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        lines = read_text(makefile_path).splitlines()
        first_index = lines.index(f"\t{REQUIRED_TARGET_LINES[0]}")
        second_index = lines.index(f"\t{REQUIRED_TARGET_LINES[1]}")
        lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
        makefile_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert any(code == "TARGET_LINE_ORDER_MISMATCH" for code, _ in collect_issues(root))
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, POLICY)
        payload = json.loads(read_text(policy_path))
        payload["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-cross"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", "['phase2-toolchain', 'phase2-cross']") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, POLICY)
        payload = json.loads(read_text(policy_path))
        payload["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", "['aarch64-linux']") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, POLICY)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        assert ("INVALID_POLICY_JSON", "Expecting property name enclosed in double quotes") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy_path = resolve_path(root, POLICY)
        policy_path.write_text("[]\n", encoding="utf-8")
        assert ("INVALID_POLICY_PAYLOAD", "list") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        resolve_path(root, REQUIRED_PATHS[0]).unlink()
        assert ("MISSING_REQUIRED_PATH", REQUIRED_PATHS[0]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        resolve_path(root, MAKEFILE).unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks += 1
        else:
            raise AssertionError("missing Makefile did not abort")

    assert checks == expected_checks
    print("LANE03_PHASE2_TOOLCHAIN_ROUTE_SELF_TEST=pass")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Lane 03 phase2-toolchain route keeps its returned toolchain bundle explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a focused current-like sample root for replay and exit",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_PHASE2_TOOLCHAIN_ROUTE=pass")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_WORKFLOW_LINE_COUNT=1")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_TARGET_LINE_COUNT={len(REQUIRED_TARGET_LINES)}")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

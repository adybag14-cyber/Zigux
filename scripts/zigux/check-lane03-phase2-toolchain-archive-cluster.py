#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = "zigux/Makefile"
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
POLICY = "scripts/zigux/zig-toolchain-policy.json"
TARGET_HEADER = "phase2-toolchain:"
WORKFLOW_ROUTE = "run: make -C zigux phase2-toolchain"

REQUIRED_PATHS = (
    MAKEFILE,
    WORKFLOW,
    POLICY,
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


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def extract_target_block(makefile_text: str, header: str = TARGET_HEADER) -> list[str]:
    lines = makefile_text.splitlines()
    start_index: int | None = None
    for index, line in enumerate(lines):
        if line.startswith(header):
            start_index = index + 1
            break
    if start_index is None:
        raise ValueError(f"missing Makefile target {header}")

    block: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("\t"):
            block.append(line.strip())
            continue
        if not line.strip():
            if block:
                break
            continue
        if block:
            break
    return block


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    makefile_text = read_text(root, MAKEFILE)
    workflow_text = read_text(root, WORKFLOW)
    policy_text = read_text(root, POLICY)

    try:
        target_block = extract_target_block(makefile_text)
    except ValueError as exc:
        issues.append(("MISSING_TARGET", str(exc)))
        target_block = []

    for marker in REQUIRED_TARGET_LINES:
        count = target_block.count(marker)
        if count == 0:
            issues.append(("MISSING_TARGET_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_TARGET_LINE", f"{marker}:count={count}"))

    if target_block:
        positions = [target_block.index(marker) for marker in REQUIRED_TARGET_LINES if marker in target_block]
        if positions != sorted(positions):
            issues.append(("OUT_OF_ORDER_TARGET_CLUSTER", TARGET_HEADER))

    workflow_count = count_exact_lines(workflow_text, WORKFLOW_ROUTE)
    if workflow_count == 0:
        issues.append(("MISSING_WORKFLOW_ROUTE", WORKFLOW_ROUTE))
    elif workflow_count != 1:
        issues.append(("DUPLICATE_WORKFLOW_ROUTE", f"{WORKFLOW_ROUTE}:count={workflow_count}"))

    try:
        policy = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
        policy = None

    if isinstance(policy, dict):
        upgrade_policy = policy.get("upgrade_policy")
        if not isinstance(upgrade_policy, dict):
            issues.append(("INVALID_UPGRADE_POLICY", POLICY))
        else:
            required_make_routes = upgrade_policy.get("required_make_routes")
            if not isinstance(required_make_routes, list) or not required_make_routes:
                issues.append(("INVALID_REQUIRED_MAKE_ROUTES", POLICY))
            else:
                if "phase2-toolchain" not in required_make_routes:
                    issues.append(("MISSING_POLICY_ROUTE", "phase2-toolchain"))
                if len(required_make_routes) != len(set(required_make_routes)):
                    issues.append(("DUPLICATE_POLICY_ROUTE", "required_make_routes"))

            archive_target_scope = upgrade_policy.get("archive_target_scope")
            if not isinstance(archive_target_scope, list) or len(archive_target_scope) != 1:
                issues.append(("INVALID_ARCHIVE_TARGET_SCOPE", POLICY))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, detail in issues:
        grouped.setdefault(code, []).append(detail)

    print("LANE03_PHASE2_TOOLCHAIN_ARCHIVE_CLUSTER=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        if rel in {MAKEFILE, WORKFLOW, POLICY}:
            continue
        write_text(root, rel, "present\n")

    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "",
                ".PHONY: phase2-toolchain",
                "",
                "phase2-toolchain:",
                *[f"\t{line}" for line in REQUIRED_TARGET_LINES],
                "",
                "phase2-tools:",
                "\t@true",
            )
        )
        + "\n",
    )
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Run current Phase 2 toolchain make route",
                f"        {WORKFLOW_ROUTE}",
            )
        )
        + "\n",
    )
    write_text(
        root,
        POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": [
                        "phase2-toolchain",
                        "phase2-validate",
                        "phase2-cross",
                    ],
                },
            },
            indent=2,
        )
        + "\n",
    )


def remove_first_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_first_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def swap_adjacent_target_lines(text: str, first_marker: str, second_marker: str) -> str:
    lines = text.splitlines()
    first_index = None
    second_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == first_marker and first_index is None:
            first_index = index
        if stripped == second_marker and second_index is None:
            second_index = index
    if first_index is None or second_index is None:
        raise AssertionError("target markers not found")
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    checks = 0

    with tempfile.TemporaryDirectory(prefix="zigux_lane03_archive_cluster_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        (root / "scripts/zigux/stage-pinned-zig-archive.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/stage-pinned-zig-archive.py") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, remove_first_line(read_text(root, MAKEFILE), REQUIRED_TARGET_LINES[10]))
        assert ("MISSING_TARGET_LINE", REQUIRED_TARGET_LINES[10]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, duplicate_first_line(read_text(root, MAKEFILE), REQUIRED_TARGET_LINES[8]))
        assert ("DUPLICATE_TARGET_LINE", f"{REQUIRED_TARGET_LINES[8]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            swap_adjacent_target_lines(read_text(root, MAKEFILE), REQUIRED_TARGET_LINES[6], REQUIRED_TARGET_LINES[7]),
        )
        assert ("OUT_OF_ORDER_TARGET_CLUSTER", TARGET_HEADER) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, remove_first_line(read_text(root, WORKFLOW), WORKFLOW_ROUTE))
        assert ("MISSING_WORKFLOW_ROUTE", WORKFLOW_ROUTE) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_first_line(read_text(root, WORKFLOW), WORKFLOW_ROUTE))
        assert ("DUPLICATE_WORKFLOW_ROUTE", f"{WORKFLOW_ROUTE}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(root, POLICY))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-validate", "phase2-cross"]
        write_text(root, POLICY, json.dumps(policy, indent=2) + "\n")
        assert ("MISSING_POLICY_ROUTE", "phase2-toolchain") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(root, POLICY))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-toolchain"]
        write_text(root, POLICY, json.dumps(policy, indent=2) + "\n")
        assert ("DUPLICATE_POLICY_ROUTE", "required_make_routes") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(root, POLICY))
        policy["upgrade_policy"]["archive_target_scope"] = ["x86_64-linux", "aarch64-linux"]
        write_text(root, POLICY, json.dumps(policy, indent=2) + "\n")
        assert ("INVALID_ARCHIVE_TARGET_SCOPE", POLICY) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, POLICY, "{not-json}\n")
        assert collect_issues(root)[0][0] == "INVALID_POLICY_JSON"
        checks += 1

    print("LANE03_PHASE2_TOOLCHAIN_ARCHIVE_CLUSTER_SELF_TEST=pass")
    print(f"LANE03_PHASE2_TOOLCHAIN_ARCHIVE_CLUSTER_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 03 phase2-toolchain archive cluster across the Makefile, workflow, and pinned policy."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--write-sample-root", type=Path, help="write a current-like sample root and exit")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract tests")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    root = args.root.resolve()
    issues = collect_issues(root)
    if issues:
        return emit_issues(issues)

    print("LANE03_PHASE2_TOOLCHAIN_ARCHIVE_CLUSTER=pass")
    print(f"LANE03_PHASE2_TOOLCHAIN_ARCHIVE_CLUSTER_TARGET_LINE_COUNT={len(REQUIRED_TARGET_LINES)}")
    print("LANE03_PHASE2_TOOLCHAIN_ARCHIVE_CLUSTER_WORKFLOW_ROUTE_COUNT=1")
    print(f"LANE03_PHASE2_TOOLCHAIN_ARCHIVE_CLUSTER_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

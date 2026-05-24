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
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
)

EXPECTED_POLICY_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-validate",
    "phase2-cross",
)

EXPECTED_PHASE2_TOOLCHAIN_LINES = (
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

EXPECTED_PHASE2_TOOLS_LINES = (
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
)

EXPECTED_WORKFLOW_CLUSTER = (
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: make -C zigux phase2-toolchain",
    "run: make -C zigux phase2-tools",
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
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


def parse_make_target_block(text: str, target: str) -> list[str] | None:
    lines = text.splitlines()
    header = f"{target}:"
    start_index: int | None = None
    for index, line in enumerate(lines):
        if line.startswith(header):
            start_index = index + 1
            break
    if start_index is None:
        return None

    commands: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("\t"):
            commands.append(line.strip())
            continue
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            break
        break
    return commands


def contains_contiguous_run_cluster(text: str, cluster: tuple[str, ...]) -> bool:
    stripped = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("run:")
    ]
    width = len(cluster)
    for index in range(len(stripped) - width + 1):
        if tuple(stripped[index : index + width]) == cluster:
            return True
    return False


def check_target_commands(
    issues: list[tuple[str, str]],
    target_name: str,
    commands: list[str] | None,
    expected_lines: tuple[str, ...],
) -> None:
    if commands is None:
        issues.append(("MISSING_MAKE_TARGET", target_name))
        return
    if commands != list(expected_lines):
        issues.append((f"{target_name.upper().replace('-', '_')}_COMMAND_MISMATCH", f"count={len(commands)}"))
    for marker in expected_lines:
        count = commands.count(marker)
        if count == 0:
            issues.append((f"MISSING_{target_name.upper().replace('-', '_')}_LINE", marker))
        elif count != 1:
            issues.append(
                (f"DUPLICATE_{target_name.upper().replace('-', '_')}_LINE", f"{marker}:count={count}")
            )


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    makefile_text = read_text(root, MAKEFILE)
    workflow_text = read_text(root, WORKFLOW)
    policy_text = read_text(root, POLICY)

    try:
        policy = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
        return issues

    required_make_routes = policy.get("upgrade_policy", {}).get("required_make_routes")
    if required_make_routes != list(EXPECTED_POLICY_ROUTES):
        issues.append(
            (
                "POLICY_ROUTE_MISMATCH",
                ",".join(required_make_routes) if isinstance(required_make_routes, list) else repr(required_make_routes),
            )
        )

    check_target_commands(
        issues,
        "phase2-toolchain",
        parse_make_target_block(makefile_text, "phase2-toolchain"),
        EXPECTED_PHASE2_TOOLCHAIN_LINES,
    )
    check_target_commands(
        issues,
        "phase2-tools",
        parse_make_target_block(makefile_text, "phase2-tools"),
        EXPECTED_PHASE2_TOOLS_LINES,
    )

    for marker in EXPECTED_WORKFLOW_CLUSTER:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    if not contains_contiguous_run_cluster(workflow_text, EXPECTED_WORKFLOW_CLUSTER):
        issues.append(("WORKFLOW_CLUSTER_MISMATCH", "phase2 toolchain/tools workflow cluster is not contiguous"))

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
                "phase2-toolchain:",
                *[f"\t{line}" for line in EXPECTED_PHASE2_TOOLCHAIN_LINES],
                "",
                "phase2-tools:",
                *[f"\t{line}" for line in EXPECTED_PHASE2_TOOLS_LINES],
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
                "      - name: Self-test current Phase 2 toolchain pinning checker",
                "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
                "      - name: Check current Phase 2 toolchain pinning packet",
                "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
                "      - name: Self-test current Phase 2 toolchain pin-scope checker",
                "        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
                "      - name: Check current Phase 2 toolchain pin-scope packet",
                "        run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
                "      - name: Run current Phase 2 toolchain make route",
                "        run: make -C zigux phase2-toolchain",
                "      - name: Run current Phase 2 tools make route",
                "        run: make -C zigux phase2-tools",
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
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": list(EXPECTED_POLICY_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0

    with tempfile.TemporaryDirectory(prefix="zigux_lane03_phase2_toolchain_route_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        (root / "scripts/zigux/install-zig.py").unlink()
        assert ("MISSING_REQUIRED_PATH", "scripts/zigux/install-zig.py") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(root, POLICY))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-validate", "phase2-cross"]
        write_text(root, POLICY, json.dumps(policy, indent=2) + "\n")
        assert ("POLICY_ROUTE_MISMATCH", "phase2-toolchain,phase2-validate,phase2-cross") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_exact_line(
                read_text(root, MAKEFILE),
                EXPECTED_PHASE2_TOOLCHAIN_LINES[3],
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --not-self-test",
            ),
        )
        issues = collect_issues(root)
        assert ("PHASE2_TOOLCHAIN_COMMAND_MISMATCH", f"count={len(EXPECTED_PHASE2_TOOLCHAIN_LINES)}") in issues
        assert ("MISSING_PHASE2_TOOLCHAIN_LINE", EXPECTED_PHASE2_TOOLCHAIN_LINES[3]) in issues
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            replace_exact_line(
                read_text(root, MAKEFILE),
                EXPECTED_PHASE2_TOOLS_LINES[2],
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py --wrong",
            ),
        )
        issues = collect_issues(root)
        assert ("PHASE2_TOOLS_COMMAND_MISMATCH", f"count={len(EXPECTED_PHASE2_TOOLS_LINES)}") in issues
        assert ("MISSING_PHASE2_TOOLS_LINE", EXPECTED_PHASE2_TOOLS_LINES[2]) in issues
        checks += 1

        build_sample_root(root)
        write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), EXPECTED_PHASE2_TOOLS_LINES[-1]))
        assert (
            "DUPLICATE_PHASE2_TOOLS_LINE",
            f"{EXPECTED_PHASE2_TOOLS_LINES[-1]}:count=2",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            replace_exact_line(
                read_text(root, WORKFLOW),
                EXPECTED_WORKFLOW_CLUSTER[5],
                "        run: make -C zigux phase2-tools-missing",
            ),
        )
        issues = collect_issues(root)
        assert ("MISSING_WORKFLOW_LINE", EXPECTED_WORKFLOW_CLUSTER[5]) in issues
        assert ("WORKFLOW_CLUSTER_MISMATCH", "phase2 toolchain/tools workflow cluster is not contiguous") in issues
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), EXPECTED_WORKFLOW_CLUSTER[5]))
        assert (
            "DUPLICATE_WORKFLOW_LINE",
            f"{EXPECTED_WORKFLOW_CLUSTER[5]}:count=2",
        ) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW,
            read_text(root, WORKFLOW).replace(
                "\n      - name: Run current Phase 2 toolchain make route\n        run: make -C zigux phase2-toolchain"
                "\n      - name: Run current Phase 2 tools make route\n        run: make -C zigux phase2-tools",
                "\n      - name: Run current Phase 2 tools make route\n        run: make -C zigux phase2-tools"
                "\n      - name: Run current Phase 2 toolchain make route\n        run: make -C zigux phase2-toolchain",
                1,
            ),
        )
        assert ("WORKFLOW_CLUSTER_MISMATCH", "phase2 toolchain/tools workflow cluster is not contiguous") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE,
            read_text(root, MAKEFILE).replace("phase2-tools:\n", "phase2-tools-disabled:\n", 1),
        )
        assert ("MISSING_MAKE_TARGET", "phase2-tools") in collect_issues(root)
        checks += 1

    print("LANE03_PHASE2_TOOLCHAIN_ROUTE_SELF_TEST=pass")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Zigux Phase 2 toolchain/tool routes packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a focused current-like sample root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print("LANE03_PHASE2_TOOLCHAIN_ROUTE_SAMPLE_ROOT=pass")
        print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_SAMPLE_ROOT_PATH={args.write_sample_root.resolve()}")
        return 0

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("LANE03_PHASE2_TOOLCHAIN_ROUTE=pass")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_TOOLCHAIN_TARGET_LINE_COUNT={len(EXPECTED_PHASE2_TOOLCHAIN_LINES)}")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_TOOLS_TARGET_LINE_COUNT={len(EXPECTED_PHASE2_TOOLS_LINES)}")
    print(f"LANE03_PHASE2_TOOLCHAIN_ROUTE_WORKFLOW_LINE_COUNT={len(EXPECTED_WORKFLOW_CLUSTER)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
MAKEFILE_ROUTE = "phase2-toolchain:"

WORKFLOW_PREVIOUS_STEP = "- name: Check current Lane 05 install-zig archive verification packet"
WORKFLOW_NEXT_STEP = "- name: Self-test current Phase 2 toolchain pinning checker"
MAKEFILE_PREVIOUS_LINE = "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py"
MAKEFILE_NEXT_LINE = "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test"

WORKFLOW_PACKET = [
    (
        "- name: Self-test current Zig installer helper",
        "run: python3 scripts/zigux/install-zig.py --self-test",
    ),
    (
        "- name: Self-test current staged pinned Zig archive helper",
        "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    ),
    (
        "- name: Self-test current Lane 05 stage helper contract checker",
        "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    ),
    (
        "- name: Check current Lane 05 stage helper contract packet",
        "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    ),
    (
        "- name: Self-test current Lane 05 stage helper selftest checker",
        "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    ),
    (
        "- name: Check current Lane 05 stage helper selftest packet",
        "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    ),
]

MAKEFILE_PACKET = [
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"lane05 stage-helper makefile packet missing required file: {path}") from exc


def require_exact_line(text: str, line: str, label: str) -> None:
    expected = line.strip()
    count = sum(1 for current in text.splitlines() if current.strip() == expected)
    if count != 1:
        raise SystemExit(
            "lane05 stage-helper makefile packet expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(
            f"lane05 stage-helper makefile packet missing {label}: {marker}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            "lane05 stage-helper makefile packet missing ordered markers for "
            f"{label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 stage-helper makefile packet expected "
            f"{label} `{earlier}` before `{later}`"
        )


def require_line_order(text: str, earlier: str, later: str, label: str) -> None:
    normalized = [line.strip() for line in text.splitlines()]
    earlier_expected = earlier.strip()
    later_expected = later.strip()
    try:
        earlier_index = normalized.index(earlier_expected)
    except ValueError as exc:
        raise SystemExit(
            f"lane05 stage-helper makefile packet missing earlier line for {label}: {earlier}"
        ) from exc
    try:
        later_index = normalized.index(later_expected)
    except ValueError as exc:
        raise SystemExit(
            f"lane05 stage-helper makefile packet missing later line for {label}: {later}"
        ) from exc
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 stage-helper makefile packet expected "
            f"{label} `{earlier}` before `{later}`"
        )


def extract_makefile_route(makefile_text: str, route: str) -> str:
    lines = makefile_text.splitlines()
    route_index = None
    for index, line in enumerate(lines):
        if line.startswith(route):
            route_index = index
            break
    if route_index is None:
        raise SystemExit(
            f"lane05 stage-helper makefile packet missing route header: {route}"
        )

    collected = [lines[route_index]]
    for line in lines[route_index + 1 :]:
        if line.startswith("\t"):
            collected.append(line)
            continue
        if not line.strip():
            break
        if not line.startswith("\t"):
            break
    return "\n".join(collected) + "\n"


def check_workflow(workflow_text: str) -> int:
    require_marker(workflow_text, WORKFLOW_PREVIOUS_STEP, "workflow anchor")
    require_marker(workflow_text, WORKFLOW_NEXT_STEP, "workflow anchor")
    require_order(
        workflow_text,
        WORKFLOW_PREVIOUS_STEP,
        WORKFLOW_PACKET[0][0],
        "workflow packet start",
    )
    require_order(
        workflow_text,
        WORKFLOW_PACKET[-1][0],
        WORKFLOW_NEXT_STEP,
        "workflow packet end",
    )

    previous_step = WORKFLOW_PREVIOUS_STEP
    for step, command in WORKFLOW_PACKET:
        require_exact_line(workflow_text, step, "workflow step")
        require_exact_line(workflow_text, f"        {command}", "workflow command")
        require_line_order(workflow_text, previous_step, step, "workflow order")
        previous_step = step

    return len(WORKFLOW_PACKET)


def check_makefile(makefile_text: str) -> int:
    route_text = extract_makefile_route(makefile_text, MAKEFILE_ROUTE)
    require_marker(route_text, MAKEFILE_PREVIOUS_LINE, "makefile anchor")
    require_marker(route_text, MAKEFILE_NEXT_LINE, "makefile anchor")
    require_order(
        route_text,
        MAKEFILE_PREVIOUS_LINE,
        MAKEFILE_PACKET[0],
        "makefile packet start",
    )
    require_order(
        route_text,
        MAKEFILE_PACKET[-1],
        MAKEFILE_NEXT_LINE,
        "makefile packet end",
    )

    previous_line = MAKEFILE_PREVIOUS_LINE
    for line in MAKEFILE_PACKET:
        require_exact_line(route_text, line, "makefile route")
        require_line_order(route_text, previous_line, line, "makefile order")
        previous_line = line

    return len(MAKEFILE_PACKET)


def check_root(root: Path) -> tuple[int, int]:
    workflow_text = read_text(root / WORKFLOW_PATH)
    makefile_text = read_text(root / MAKEFILE_PATH)
    workflow_count = check_workflow(workflow_text)
    makefile_count = check_makefile(makefile_text)
    return workflow_count, makefile_count


def write_sample_root(root: Path) -> None:
    (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)

    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Check current Lane 05 install-zig archive verification packet",
        "        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
        "      - name: Self-test current Zig installer helper",
        "        run: python3 scripts/zigux/install-zig.py --self-test",
        "      - name: Self-test current staged pinned Zig archive helper",
        "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
        "      - name: Self-test current Lane 05 stage helper contract checker",
        "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
        "      - name: Check current Lane 05 stage helper contract packet",
        "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
        "      - name: Self-test current Lane 05 stage helper selftest checker",
        "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
        "      - name: Check current Lane 05 stage helper selftest packet",
        "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
        "      - name: Self-test current Phase 2 toolchain pinning checker",
        "        run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    ]
    (root / WORKFLOW_PATH).write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")

    makefile_lines = [
        "PYTHON ?= python3",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "",
        "phase2-toolchain:",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-first-archive-workflow.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-local-archive-readme.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-install-zig-archive-verification.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
        "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    ]
    (root / MAKEFILE_PATH).write_text("\n".join(makefile_lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_sample_root(root)
        workflow_count, makefile_count = check_root(root)
        case_count = 1

        workflow_path = root / WORKFLOW_PATH
        makefile_path = root / MAKEFILE_PATH

        broken_workflow = workflow_path.read_text(encoding="utf-8").replace(
            "      - name: Self-test current staged pinned Zig archive helper\n"
            "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n",
            "",
            1,
        )
        workflow_path.write_text(broken_workflow, encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert WORKFLOW_PACKET[1][0] in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing workflow stage helper step failure")
        write_sample_root(root)

        broken_workflow = workflow_path.read_text(encoding="utf-8").replace(
            "      - name: Check current Lane 05 stage helper contract packet\n"
            "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py\n",
            "      - name: Check current Lane 05 stage helper contract packet\n"
            "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py\n",
            1,
        )
        workflow_path.write_text(broken_workflow, encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "check-lane05-stage-helper-contract.py" in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected wrong workflow command failure")
        write_sample_root(root)

        broken_makefile = makefile_path.read_text(encoding="utf-8").replace(
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py\n",
            "",
            1,
        )
        makefile_path.write_text(broken_makefile, encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "check-lane05-stage-helper-contract.py" in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing makefile contract line failure")
        write_sample_root(root)

        broken_makefile = makefile_path.read_text(encoding="utf-8").replace(
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test\n"
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py\n",
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py\n"
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test\n",
            1,
        )
        makefile_path.write_text(broken_makefile, encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "makefile order" in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected reordered makefile packet failure")
        write_sample_root(root)

        duplicate_workflow = workflow_path.read_text(encoding="utf-8").replace(
            "      - name: Self-test current Zig installer helper\n",
            "      - name: Self-test current Zig installer helper\n"
            "      - name: Self-test current Zig installer helper\n",
            1,
        )
        workflow_path.write_text(duplicate_workflow, encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert WORKFLOW_PACKET[0][0] in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected duplicate workflow step failure")
        write_sample_root(root)

        broken_makefile = makefile_path.read_text(encoding="utf-8").replace(
            "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test\n",
            "",
            1,
        )
        makefile_path.write_text(broken_makefile, encoding="utf-8")
        try:
            check_root(root)
        except SystemExit as exc:
            assert MAKEFILE_NEXT_LINE in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing makefile next anchor failure")

    print("LANE05_STAGE_HELPER_MAKEFILE_PACKET_SELF_TEST=pass")
    print(f"LANE05_STAGE_HELPER_MAKEFILE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    print(f"LANE05_STAGE_HELPER_MAKEFILE_PACKET_SELF_TEST_WORKFLOW_STEP_COUNT={workflow_count}")
    print(f"LANE05_STAGE_HELPER_MAKEFILE_PACKET_SELF_TEST_MAKEFILE_LINE_COUNT={makefile_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Lane 05 staged pinned-archive helper packet stays aligned "
            "between the bootstrap workflow and phase2-toolchain."
        )
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root containing the workflow and Makefile paths.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like sample root and exit.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    workflow_count, makefile_count = check_root(args.root)
    print("LANE05_STAGE_HELPER_MAKEFILE_PACKET=pass")
    print(f"LANE05_STAGE_HELPER_MAKEFILE_PACKET_WORKFLOW_STEP_COUNT={workflow_count}")
    print(f"LANE05_STAGE_HELPER_MAKEFILE_PACKET_MAKEFILE_LINE_COUNT={makefile_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

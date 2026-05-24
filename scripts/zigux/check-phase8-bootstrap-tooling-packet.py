#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
DOCS_README = Path("Documentation/zigux/README.md")
SCRIPTS_README = Path("scripts/zigux/README.md")
TESTS_README = Path("zigux/tests/README.md")
MAKEFILE = Path("zigux/Makefile")
VALIDATOR = Path("scripts/zigux/validate-phase8.py")
EXEC_CMD_HELPER = Path("tools/lib/subcmd/exec-cmd.zig")
EXEC_CMD_TEST = Path("zigux/tests/phase8_exec_cmd.zig")
EXEC_CMD_BUILD = Path("zigux/tests/phase8_exec_cmd_only_build.zig")
LIBBPF_SEGMENTS_BUILD = Path("zigux/tests/phase8_libbpf_segments_only_build.zig")
PERF_BUFFER_POLL_HELPER = Path("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig")
PERF_BUFFER_POLL_TEST = Path("zigux/tests/phase8_perf_buffer_poll.zig")
PHASE8_BUILD = Path("zigux/tests/phase8_build.zig")

WORKFLOW_LINES = (
    "run: make -C zigux phase8-validate",
    "run: make -C zigux phase8-exec-cmd-test",
    "run: make -C zigux phase8-libbpf-segments-test",
    "run: make -C zigux phase8-test",
)

BOUNDARY_LINES = (
    "run: make -C zigux phase6-perf",
    "run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
)

REQUIRED_FILES = (
    WORKFLOW,
    DOCS_README,
    SCRIPTS_README,
    TESTS_README,
    MAKEFILE,
    VALIDATOR,
    EXEC_CMD_HELPER,
    EXEC_CMD_TEST,
    EXEC_CMD_BUILD,
    LIBBPF_SEGMENTS_BUILD,
    PERF_BUFFER_POLL_HELPER,
    PERF_BUFFER_POLL_TEST,
    PHASE8_BUILD,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    DOCS_README: (
        "Phase 8 notes",
        "scripts/zigux/validate-phase8.py",
        "tools/lib/subcmd/exec-cmd.zig",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    ),
    SCRIPTS_README: (
        "## Phase 8",
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "scripts/zigux/validate-phase8.py",
        "zigux/tests/phase8_exec_cmd.zig",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    ),
    TESTS_README: (
        "## Phase 8 tooling packet",
        "`scripts/zigux/validate-phase8.py`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_perf_buffer_poll.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-test`",
    ),
    MAKEFILE: (
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "phase8-exec-cmd-test:",
        "phase8-libbpf-segments-test:",
        "phase8-test:",
        "phase8: phase8-validate",
    ),
    VALIDATOR: (
        "EXEC_CMD_PACKET_CHECKER = Path(\"scripts/zigux/check-phase8-exec-cmd-packet.py\")",
        "Path(\".github/workflows/zigux-bootstrap.yml\"): (",
        "\"Validate Phase 8 tooling routes\",",
        "\"Run focused Phase 8 exec-cmd tests\",",
        "\"Run Phase 8 tooling tests\",",
        "Path(\"zigux/Makefile\"): (",
        "\"phase8-libbpf-segments-test:\",",
    ),
    EXEC_CMD_HELPER: (
        "pub fn buildDeferredExeclCall",
        "pub fn buildDeferredExecvCall",
    ),
    EXEC_CMD_TEST: (
        "test \"phase8 exec-cmd packet keeps execl and execv call plans explicit\"",
    ),
    EXEC_CMD_BUILD: (
        "phase8-exec-cmd-test",
    ),
    LIBBPF_SEGMENTS_BUILD: (
        "phase8-libbpf-segments-test",
    ),
    PERF_BUFFER_POLL_HELPER: (
        "pub fn classifyWaitMode",
        "pub fn summarizePollPlan",
    ),
    PERF_BUFFER_POLL_TEST: (
        "test \"phase8 perf_buffer_poll packet keeps wait classification and summaries explicit\"",
    ),
    PHASE8_BUILD: (
        "../../tools/lib/subcmd/exec-cmd.zig",
        "phase8_exec_cmd.zig",
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "phase8_perf_buffer_poll.zig",
    ),
}


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
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


def swap_exact_lines(text: str, left_marker: str, right_marker: str) -> str:
    lines = text.splitlines()
    left_index = None
    right_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == left_marker and left_index is None:
            left_index = index
        if stripped == right_marker and right_index is None:
            right_index = index
    if left_index is None:
        raise AssertionError(f"left marker line not found: {left_marker}")
    if right_index is None:
        raise AssertionError(f"right marker line not found: {right_marker}")
    lines[left_index], lines[right_index] = lines[right_index], lines[left_index]
    return "\n".join(lines) + "\n"


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", str(rel)))

    workflow = read_text(root, WORKFLOW)
    lines = workflow.splitlines()
    step_positions: list[int] = []
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
            continue
        if count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))
            continue
        step_positions.append(next(i for i, line in enumerate(lines) if line.strip() == marker))

    for marker in BOUNDARY_LINES:
        count = count_exact_lines(workflow, marker)
        if count == 0:
            issues.append(("MISSING_BOUNDARY_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_BOUNDARY_LINE", f"{marker}:count={count}"))

    if len(step_positions) == len(WORKFLOW_LINES):
        if step_positions != sorted(step_positions):
            issues.append(("MISORDERED_WORKFLOW_PACKET", "phase8-bootstrap-tooling"))
        else:
            contiguous = all(step_positions[i] + 2 == step_positions[i + 1] for i in range(len(step_positions) - 1))
            if not contiguous:
                issues.append(("NONCONTIGUOUS_WORKFLOW_PACKET", "phase8-bootstrap-tooling"))
            phase6_idx = next((i for i, line in enumerate(lines) if line.strip() == BOUNDARY_LINES[0]), None)
            phase9_idx = next((i for i, line in enumerate(lines) if line.strip() == BOUNDARY_LINES[1]), None)
            if phase6_idx is not None and phase6_idx >= step_positions[0]:
                issues.append(("BROKEN_PREVIOUS_BOUNDARY", BOUNDARY_LINES[0]))
            if phase9_idx is not None and phase9_idx <= step_positions[-1]:
                issues.append(("BROKEN_NEXT_BOUNDARY", BOUNDARY_LINES[1]))

    for rel, markers in FILE_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            if marker not in text:
                issues.append(("MISSING_FILE_MARKER", f"{rel}:{marker}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE8_BOOTSTRAP_TOOLING_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root,
        WORKFLOW,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Run current Phase 6 shared perf route",
                "        run: make -C zigux phase6-perf",
                "      - name: Validate Phase 8 tooling routes",
                "        run: make -C zigux phase8-validate",
                "      - name: Run focused Phase 8 exec-cmd tests",
                "        run: make -C zigux phase8-exec-cmd-test",
                "      - name: Run focused Phase 8 libbpf segment tests",
                "        run: make -C zigux phase8-libbpf-segments-test",
                "      - name: Run Phase 8 tooling tests",
                "        run: make -C zigux phase8-test",
                "      - name: Self-test current Phase 9 review-checklist boundaries checker",
                "        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
            )
        )
        + "\n",
    )
    write_text(
        root,
        DOCS_README,
        "\n".join(
            (
                "# Zigux Documentation This directory is the product documentation root for Zigux.",
                "Phase 8 notes",
                "scripts/zigux/validate-phase8.py",
                "tools/lib/subcmd/exec-cmd.zig",
                "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
            )
        )
        + "\n",
    )
    write_text(
        root,
        SCRIPTS_README,
        "\n".join(
            (
                "# scripts/zigux",
                "## Phase 8",
                "scripts/zigux/check-phase8-tests-readme-alignment.py",
                "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
                "scripts/zigux/validate-phase8.py",
                "zigux/tests/phase8_exec_cmd.zig",
                "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
            )
        )
        + "\n",
    )
    write_text(
        root,
        TESTS_README,
        "\n".join(
            (
                "# zigux/tests",
                "## Phase 8 tooling packet",
                "`scripts/zigux/validate-phase8.py`",
                "`zigux/tests/phase8_exec_cmd.zig`",
                "`zigux/tests/phase8_perf_buffer_poll.zig`",
                "`make -C zigux phase8-exec-cmd-test`",
                "`make -C zigux phase8-test`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "phase8-validate:",
                "\tpython3 scripts/zigux/validate-phase8.py",
                "\tpython3 scripts/zigux/check-phase8-libbpf-segment-gate.py",
                "phase8-exec-cmd-test:",
                "\tzig build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all",
                "phase8-libbpf-segments-test:",
                "\tzig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
                "phase8-test:",
                "\tzig build test --build-file zigux/tests/phase8_build.zig --summary all",
                "phase8: phase8-validate phase8-exec-cmd-test phase8-libbpf-segments-test phase8-test",
            )
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATOR,
        "\n".join(
            (
                'EXEC_CMD_PACKET_CHECKER = Path("scripts/zigux/check-phase8-exec-cmd-packet.py")',
                'Path(".github/workflows/zigux-bootstrap.yml"): (',
                '    "Validate Phase 8 tooling routes",',
                '    "Run focused Phase 8 exec-cmd tests",',
                '    "Run Phase 8 tooling tests",',
                '),',
                'Path("zigux/Makefile"): (',
                '    "phase8-libbpf-segments-test:",',
                '),',
            )
        )
        + "\n",
    )
    write_text(
        root,
        EXEC_CMD_HELPER,
        "\n".join(
            (
                "pub fn buildDeferredExeclCall() void {}",
                "pub fn buildDeferredExecvCall() void {}",
            )
        )
        + "\n",
    )
    write_text(
        root,
        EXEC_CMD_TEST,
        'test "phase8 exec-cmd packet keeps execl and execv call plans explicit" {}\n',
    )
    write_text(root, EXEC_CMD_BUILD, 'const step_name = "phase8-exec-cmd-test";\n')
    write_text(root, LIBBPF_SEGMENTS_BUILD, 'const step_name = "phase8-libbpf-segments-test";\n')
    write_text(
        root,
        PERF_BUFFER_POLL_HELPER,
        "\n".join(
            (
                "pub fn classifyWaitMode() void {}",
                "pub fn summarizePollPlan() void {}",
            )
        )
        + "\n",
    )
    write_text(
        root,
        PERF_BUFFER_POLL_TEST,
        'test "phase8 perf_buffer_poll packet keeps wait classification and summaries explicit" {}\n',
    )
    write_text(
        root,
        PHASE8_BUILD,
        "\n".join(
            (
                "../../tools/lib/subcmd/exec-cmd.zig",
                "phase8_exec_cmd.zig",
                "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
                "phase8_perf_buffer_poll.zig",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_bootstrap_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert collect_issues(root) == []
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), WORKFLOW_LINES[1], "        run: make -C zigux phase8-help-test"))
        assert ("MISSING_WORKFLOW_LINE", WORKFLOW_LINES[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), WORKFLOW_LINES[2]))
        assert ("DUPLICATE_WORKFLOW_LINE", f"{WORKFLOW_LINES[2]}:count=2") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, swap_exact_lines(read_text(root, WORKFLOW), WORKFLOW_LINES[0], WORKFLOW_LINES[3]))
        assert ("MISORDERED_WORKFLOW_PACKET", "phase8-bootstrap-tooling") in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, WORKFLOW, read_text(root, WORKFLOW).replace(BOUNDARY_LINES[1] + "\n", "", 1))
        assert ("MISSING_BOUNDARY_LINE", BOUNDARY_LINES[1]) in collect_issues(root)
        checks += 1

        build_sample_root(root)
        write_text(root, TESTS_README, read_text(root, TESTS_README).replace("`make -C zigux phase8-test`\n", "", 1))
        issues = collect_issues(root)
        assert any(code == "MISSING_FILE_MARKER" and value.startswith(f"{TESTS_README}:") for code, value in issues)
        checks += 1

    print("PHASE8_BOOTSTRAP_TOOLING_PACKET_SELF_TEST=pass")
    print(f"PHASE8_BOOTSTRAP_TOOLING_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guard the live Phase 8 bootstrap tooling packet across the workflow, validator, wrapper routes, and reminder surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in contract checks")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        default=None,
        help="write a minimal passing sample root for replay",
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

    print("PHASE8_BOOTSTRAP_TOOLING_PACKET=pass")
    print(f"PHASE8_BOOTSTRAP_TOOLING_PACKET_WORKFLOW_STEP_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE8_BOOTSTRAP_TOOLING_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "samples/zigux/README.md").exists() and (candidate / "zigux/tests/phase9_build.zig").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SAMPLES_README_PATH = "samples/zigux/README.md"
EXEC_CMD_PATH = "tools/lib/subcmd/exec-cmd.zig"
HELP_PATH = "tools/lib/subcmd/help.zig"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
RUNTIME_LOADER_CONTRACT_PATH = "zigux/kernel/runtime_loader_contract.zig"
RUNTIME_LOADER_ALLOCATOR_INIT_FLOW_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"

RUNTIME_LOADER_PACKET_PATHS = [
    RUNTIME_LOADER_PATH,
    RUNTIME_LOADER_CONTRACT_PATH,
    RUNTIME_LOADER_ALLOCATOR_INIT_FLOW_PATH,
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
]

FORBIDDEN_RUNTIME_CONTROL_MARKERS = [
    "command_name:",
    ".command_name =",
    "argv_policy:",
    ".argv_policy =",
    "activation_env:",
    ".activation_env =",
    "exec_path_env:",
    ".exec_path_env =",
    '"PERF_EXEC_PATH"',
    '"PATH"',
    '"LINES"',
    '"COLUMNS"',
]

SAMPLES_README_BOUNDARY_MARKER = (
    "keep the older command and environment control boundary explicit too: "
    "`tools/lib/subcmd/exec-cmd.zig` still owns the deferred `command_name`, exec-path, "
    "`PERF_EXEC_PATH`, and `PATH` tooling cues, while `tools/lib/subcmd/help.zig` still owns "
    "the `LINES` and `COLUMNS` terminal-formatting cues; the Phase 9 loader packet remains a "
    "metadata-only handoff and should not be read as shipped runtime command or environment "
    "activation control on current `master`"
)

EXEC_CMD_REQUIRED_MARKERS = [
    '"PERF_EXEC_PATH"',
    '"PATH"',
]

HELP_REQUIRED_MARKERS = [
    '"LINES"',
    '"COLUMNS"',
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_contains(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def ensure_absent(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            failures.append(f"{label}_forbidden:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    required_paths = [
        SAMPLES_README_PATH,
        EXEC_CMD_PATH,
        HELP_PATH,
        *RUNTIME_LOADER_PACKET_PATHS,
    ]
    for rel_path in required_paths:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    samples_readme = read_text(root, SAMPLES_README_PATH)
    exec_cmd = read_text(root, EXEC_CMD_PATH)
    help_text = read_text(root, HELP_PATH)

    ensure_contains(failures, "samples_readme", samples_readme, [SAMPLES_README_BOUNDARY_MARKER])
    ensure_contains(failures, "exec_cmd", exec_cmd, EXEC_CMD_REQUIRED_MARKERS)
    ensure_contains(failures, "help", help_text, HELP_REQUIRED_MARKERS)

    for rel_path in RUNTIME_LOADER_PACKET_PATHS:
        ensure_absent(failures, rel_path, read_text(root, rel_path), FORBIDDEN_RUNTIME_CONTROL_MARKERS)

    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(root / SAMPLES_README_PATH, "# samples/zigux\n" + SAMPLES_README_BOUNDARY_MARKER + "\n")
    write_text(root / EXEC_CMD_PATH, "const path_name = \"PATH\";\nconst perf_name = \"PERF_EXEC_PATH\";\n")
    write_text(root / HELP_PATH, "const rows_name = \"LINES\";\nconst cols_name = \"COLUMNS\";\n")
    for rel_path in RUNTIME_LOADER_PACKET_PATHS:
        write_text(root / rel_path, "// runtime-loader packet placeholder\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-runtime-loader-control-boundary-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        write_fixture_tree(base)
        samples_readme_path = base / SAMPLES_README_PATH
        samples_readme_path.write_text("# samples/zigux\n", encoding="utf-8")
        expect_failure(base, f"samples_readme:{SAMPLES_README_BOUNDARY_MARKER}")

        write_fixture_tree(base)
        exec_cmd_path = base / EXEC_CMD_PATH
        exec_cmd_path.write_text("const perf_name = \"PERF_EXEC_PATH\";\n", encoding="utf-8")
        expect_failure(base, 'exec_cmd:"PATH"')

        write_fixture_tree(base)
        help_path = base / HELP_PATH
        help_path.write_text("const rows_name = \"LINES\";\n", encoding="utf-8")
        expect_failure(base, 'help:"COLUMNS"')

        write_fixture_tree(base)
        bitmap_loader_path = base / "samples/zigux/runtime_bitmap_loader.zig"
        bitmap_loader_path.write_text("command_name:\n", encoding="utf-8")
        expect_failure(base, "samples/zigux/runtime_bitmap_loader.zig_forbidden:command_name:")

        write_fixture_tree(base)
        allocator_init_flow_path = base / RUNTIME_LOADER_ALLOCATOR_INIT_FLOW_PATH
        allocator_init_flow_path.write_text('const leaked = "PATH"\n', encoding="utf-8")
        expect_failure(base, 'zigux/tests/runtime_loader_allocator_init_flow.zig_forbidden:"PATH"')

        print("PHASE9_RUNTIME_LOADER_CONTROL_BOUNDARY_SELF_TEST=pass")
        print("PHASE9_RUNTIME_LOADER_CONTROL_BOUNDARY_SELF_TEST_CASE_COUNT=5")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that Phase 9 runtime-loader packet files keep command and environment "
            "controls out of the shared loader handoff while Phase 8 tooling retains ownership "
            "of those surfaces."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the repository root inferred from this script.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE9_RUNTIME_LOADER_CONTROL_BOUNDARY=fail")
        print("PHASE9_RUNTIME_LOADER_CONTROL_BOUNDARY_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE9_RUNTIME_LOADER_CONTROL_BOUNDARY_FAILURES_END")
        return 1

    print("PHASE9_RUNTIME_LOADER_CONTROL_BOUNDARY=pass")
    print(
        "PHASE9_RUNTIME_LOADER_CONTROL_BOUNDARY_CHECKED_PATHS="
        f"{len(RUNTIME_LOADER_PACKET_PATHS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

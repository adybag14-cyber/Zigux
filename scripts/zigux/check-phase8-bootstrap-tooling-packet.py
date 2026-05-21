#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


PACKET_NAME = "PHASE8_BOOTSTRAP_TOOLING_PACKET"
SELF_TEST_NAME = f"{PACKET_NAME}_SELF_TEST"

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BEFORE_STEP = "Run current Phase 6 shared perf route"
PACKET_STEPS = (
    "Validate Phase 8 tooling routes",
    "Run focused Phase 8 exec-cmd tests",
    "Run Phase 8 tooling tests",
)
AFTER_STEP = "Self-test current Phase 9 review-checklist boundaries checker"

REQUIRED_PATHS = (
    WORKFLOW_PATH,
    Path("scripts/zigux/validate-phase8.py"),
    Path("zigux/Makefile"),
    Path("Documentation/zigux/README.md"),
    Path("scripts/zigux/README.md"),
    Path("zigux/tests/README.md"),
    Path("zigux/tests/phase8_exec_cmd.zig"),
    Path("zigux/tests/phase8_exec_cmd_only_build.zig"),
    Path("zigux/tests/phase8_build.zig"),
    Path("tools/lib/subcmd/exec-cmd.zig"),
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    WORKFLOW_PATH: (
        BEFORE_STEP,
        *PACKET_STEPS,
        AFTER_STEP,
    ),
    Path("scripts/zigux/validate-phase8.py"): (
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "zigux/tests/phase8_exec_cmd.zig",
        "zigux/tests/phase8_exec_cmd_only_build.zig",
        "tools/lib/subcmd/exec-cmd.zig",
    ),
    Path("zigux/Makefile"): (
        "phase8-validate:",
        "scripts/zigux/validate-phase8.py",
        "phase8-exec-cmd-test:",
        "phase8-test:",
        "phase8: phase8-validate phase8-exec-cmd-test",
    ),
    Path("Documentation/zigux/README.md"): (
        "Phase 8 notes",
        "scripts/zigux/validate-phase8.py",
        "tools/lib/subcmd/exec-cmd.zig",
        "Documentation/zigux/phase8-file-path-handle-bridge-slice.md",
    ),
    Path("scripts/zigux/README.md"): (
        "## Phase 8",
        "scripts/zigux/check-phase8-tests-readme-alignment.py",
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "scripts/zigux/validate-phase8.py",
        "tools/lib/subcmd/exec-cmd.zig",
    ),
    Path("zigux/tests/README.md"): (
        "## Phase 8 review packet",
        "`scripts/zigux/validate-phase8.py`",
        "`zigux/tests/phase8_exec_cmd.zig`",
        "`zigux/tests/phase8_exec_cmd_only_build.zig`",
        "`make -C zigux phase8-exec-cmd-test`",
        "`make -C zigux phase8-test`",
    ),
    Path("zigux/tests/phase8_exec_cmd.zig"): (
        'test "phase8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit" {',
        "scripts/zigux/validate-phase8.py",
        "tools/lib/subcmd/exec-cmd.zig",
        "Run focused Phase 8 exec-cmd tests",
    ),
    Path("zigux/tests/phase8_exec_cmd_only_build.zig"): (
        "phase8_exec_cmd.zig",
        "phase8_exec_cmd",
        "Run the phase 8 exec-cmd review witness tests.",
    ),
    Path("zigux/tests/phase8_build.zig"): (
        "phase8_exec_cmd",
        "phase8_file_path_handle_bridge",
        "phase8_perf_buffer_poll",
    ),
    Path("tools/lib/subcmd/exec-cmd.zig"): (
        "pub fn",
        "test ",
    ),
}


class PacketError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PacketError(f"missing required path: {path.as_posix()}") from exc


def ensure_required_paths(root: Path) -> None:
    for relative_path in REQUIRED_PATHS:
        if not (root / relative_path).is_file():
            raise PacketError(f"missing required path: {relative_path.as_posix()}")


def ensure_markers(root: Path) -> None:
    for relative_path, markers in FILE_MARKERS.items():
        content = read_text(root / relative_path)
        for marker in markers:
            if marker not in content:
                raise PacketError(
                    f"missing marker in {relative_path.as_posix()}: {marker}"
                )


def parse_workflow_steps(content: str) -> list[str]:
    steps: list[str] = []
    prefix = "      - name:"
    for line in content.splitlines():
        if line.startswith(prefix):
            steps.append(line[len(prefix) :].strip())
    return steps


def ensure_unique_step(steps: list[str], step: str) -> int:
    count = steps.count(step)
    if count == 0:
        raise PacketError(f"missing workflow step: {step}")
    if count > 1:
        raise PacketError(f"duplicate workflow step: {step}")
    return steps.index(step)


def ensure_workflow_packet(root: Path) -> None:
    steps = parse_workflow_steps(read_text(root / WORKFLOW_PATH))
    ordered_steps = (BEFORE_STEP, *PACKET_STEPS, AFTER_STEP)
    indices = [ensure_unique_step(steps, step) for step in ordered_steps]
    if indices != sorted(indices):
        raise PacketError("workflow packet order drifted")
    for left, right in zip(indices, indices[1:]):
        if right != left + 1:
            raise PacketError("workflow packet is no longer contiguous")


def validate(root: Path) -> None:
    ensure_required_paths(root)
    ensure_markers(root)
    ensure_workflow_packet(root)


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Run current Phase 6 shared perf route
        run: make -C zigux phase6-perf
      - name: Validate Phase 8 tooling routes
        run: make -C zigux phase8-validate
      - name: Run focused Phase 8 exec-cmd tests
        run: make -C zigux phase8-exec-cmd-test
      - name: Run Phase 8 tooling tests
        run: make -C zigux phase8-test
      - name: Self-test current Phase 9 review-checklist boundaries checker
        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test
"""

    validate_phase8 = """#!/usr/bin/env python3
REQUIRED_FILES = (
    Path("scripts/zigux/check-phase8-tests-readme-alignment.py"),
    Path("scripts/zigux/check-phase8-perf-buffer-poll-gate.py"),
    Path("zigux/tests/phase8_exec_cmd.zig"),
    Path("zigux/tests/phase8_exec_cmd_only_build.zig"),
    Path("tools/lib/subcmd/exec-cmd.zig"),
)
"""

    makefile = """phase8-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase8.py

phase8-exec-cmd-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all

phase8-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase8_build.zig --summary all

phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test
"""

    docs_readme = """# Zigux Documentation
Phase 8 notes
- scripts/zigux/validate-phase8.py
- tools/lib/subcmd/exec-cmd.zig
- Documentation/zigux/phase8-file-path-handle-bridge-slice.md
"""

    scripts_readme = """# scripts/zigux
## Phase 8
- scripts/zigux/check-phase8-tests-readme-alignment.py
- scripts/zigux/check-phase8-perf-buffer-poll-gate.py
- scripts/zigux/validate-phase8.py
- tools/lib/subcmd/exec-cmd.zig
"""

    tests_readme = """# zigux/tests
## Phase 8 review packet
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `make -C zigux phase8-exec-cmd-test`
- `make -C zigux phase8-test`
"""

    phase8_exec_cmd = """test "phase8 exec-cmd review witness keeps the surviving shared reminder surfaces explicit" {
    _ = "scripts/zigux/validate-phase8.py";
    _ = "tools/lib/subcmd/exec-cmd.zig";
    _ = "Run focused Phase 8 exec-cmd tests";
}
"""

    phase8_exec_cmd_build = """const target = "phase8_exec_cmd.zig";
const step_name = "phase8_exec_cmd";
const message = "Run the phase 8 exec-cmd review witness tests.";
"""

    phase8_build = """const a = "phase8_exec_cmd";
const b = "phase8_file_path_handle_bridge";
const c = "phase8_perf_buffer_poll";
"""

    exec_cmd = """pub fn execCmd() void {}
test "exec-cmd placeholder" {}
"""

    write_file(root, WORKFLOW_PATH, workflow)
    write_file(root, Path("scripts/zigux/validate-phase8.py"), validate_phase8)
    write_file(root, Path("zigux/Makefile"), makefile)
    write_file(root, Path("Documentation/zigux/README.md"), docs_readme)
    write_file(root, Path("scripts/zigux/README.md"), scripts_readme)
    write_file(root, Path("zigux/tests/README.md"), tests_readme)
    write_file(root, Path("zigux/tests/phase8_exec_cmd.zig"), phase8_exec_cmd)
    write_file(
        root,
        Path("zigux/tests/phase8_exec_cmd_only_build.zig"),
        phase8_exec_cmd_build,
    )
    write_file(root, Path("zigux/tests/phase8_build.zig"), phase8_build)
    write_file(root, Path("tools/lib/subcmd/exec-cmd.zig"), exec_cmd)


def expect_failure(mutator) -> None:
    with tempfile.TemporaryDirectory(prefix="phase8-bootstrap-tooling-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        mutator(root)
        try:
            validate(root)
        except PacketError:
            return
        raise AssertionError("expected PacketError")


def run_self_test() -> None:
    cases = 0

    with tempfile.TemporaryDirectory(prefix="phase8-bootstrap-tooling-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        validate(root)
        cases += 1

    def remove_validate_step(root: Path) -> None:
        path = root / WORKFLOW_PATH
        content = path.read_text(encoding="utf-8").replace(
            "      - name: Validate Phase 8 tooling routes\n"
            "        run: make -C zigux phase8-validate\n",
            "",
        )
        path.write_text(content, encoding="utf-8")

    expect_failure(remove_validate_step)
    cases += 1

    def reorder_exec_step(root: Path) -> None:
        path = root / WORKFLOW_PATH
        content = path.read_text(encoding="utf-8")
        old = (
            "      - name: Validate Phase 8 tooling routes\n"
            "        run: make -C zigux phase8-validate\n"
            "      - name: Run focused Phase 8 exec-cmd tests\n"
            "        run: make -C zigux phase8-exec-cmd-test\n"
        )
        new = (
            "      - name: Run focused Phase 8 exec-cmd tests\n"
            "        run: make -C zigux phase8-exec-cmd-test\n"
            "      - name: Validate Phase 8 tooling routes\n"
            "        run: make -C zigux phase8-validate\n"
        )
        path.write_text(content.replace(old, new), encoding="utf-8")

    expect_failure(reorder_exec_step)
    cases += 1

    def duplicate_tooling_step(root: Path) -> None:
        path = root / WORKFLOW_PATH
        content = path.read_text(encoding="utf-8")
        marker = (
            "      - name: Run Phase 8 tooling tests\n"
            "        run: make -C zigux phase8-test\n"
        )
        path.write_text(content.replace(marker, marker + marker), encoding="utf-8")

    expect_failure(duplicate_tooling_step)
    cases += 1

    def remove_makefile_marker(root: Path) -> None:
        path = root / Path("zigux/Makefile")
        content = path.read_text(encoding="utf-8").replace("phase8-test:\n", "")
        path.write_text(content, encoding="utf-8")

    expect_failure(remove_makefile_marker)
    cases += 1

    def remove_tests_anchor(root: Path) -> None:
        path = root / Path("zigux/tests/README.md")
        content = path.read_text(encoding="utf-8").replace(
            "- `make -C zigux phase8-test`\n",
            "",
        )
        path.write_text(content, encoding="utf-8")

    expect_failure(remove_tests_anchor)
    cases += 1

    print(f"{SELF_TEST_NAME}=pass")
    print(f"{SELF_TEST_NAME}_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    root = args.root if args.root is not None else Path(__file__).resolve().parents[2]
    try:
        validate(root)
    except PacketError as exc:
        print(f"{PACKET_NAME}=fail")
        print(f"{PACKET_NAME}_REASON={exc}")
        return 1

    print(f"{PACKET_NAME}=pass")
    print(f"{PACKET_NAME}_WORKFLOW_STEP_COUNT={len(PACKET_STEPS)}")
    print(f"{PACKET_NAME}_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase8-file-path-handle-bridge-packet.py"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"
SLICE_PATH = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"
SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
MAKEFILE_PATH = "zigux/Makefile"
TESTS_README_PATH = "zigux/tests/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
PACKET_HELPER_PATH = "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"
PACKET_BUILD_PATH = "zigux/tests/phase8_build.zig"
PACKET_TEST_PATH = "zigux/tests/phase8_file_path_handle_bridge.zig"
PACKET_ONLY_BUILD_PATH = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    SEQUENCING_PATH,
    SLICE_PATH,
    SURVEY_PATH,
    MAKEFILE_PATH,
    TESTS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    PACKET_HELPER_PATH,
    PACKET_BUILD_PATH,
    PACKET_TEST_PATH,
    PACKET_ONLY_BUILD_PATH,
)

REQUIRED_MARKERS = {
    SEQUENCING_PATH: (
        "### 3. Libbpf helper lane",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "Keep follow-up in this lane limited to helper-local truthfulness, compile or behavior proof, or narrowly scoped reminder-surface repair.",
    ),
    SLICE_PATH: (
        "PHASE8_SLICE=libbpf-file-path-handle-bridge",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "zigux/tests/phase8_build.zig",
        "make -C zigux phase8-validate",
        "python3 scripts/zigux/validate-phase8.py --self-test",
        "python3 scripts/zigux/validate-phase8.py",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all",
        "make -C zigux phase8-test",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
        "make -C zigux phase8",
        "mapReuseObservationFromFdinfo()",
        "resolveReusePinnedMapAttempt()",
        "planTokenPreparation()",
        "no direct procfs reads",
        "no live bpffs opens",
        "no `bpf_obj_get()` reopen flow",
        "no token materialization or capability handoff",
    ),
    SURVEY_PATH: (
        "The same shared Phase 8 boundary packet also keeps the queued file, path, and",
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge.zig",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig",
        "make -C zigux phase8-file-path-handle-bridge-test",
        "mapReuseObservationFromFdinfo()",
        "resolveReusePinnedMapAttempt()",
        "planTokenPreparation()",
        "does not claim token materialization or capability handoff,",
        "map reopen or bpffs compatibility closure, or fd close or ownership semantics.",
    ),
    MAKEFILE_PATH: (
        "phase8-validate:",
        "phase8-file-path-handle-bridge-test:",
        "zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all",
    ),
    TESTS_README_PATH: (
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge.zig`",
        "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
        "`make -C zigux phase8-file-path-handle-bridge-test`",
    ),
    PACKET_HELPER_PATH: (
        "pub fn buildProcFdinfoPath(",
        "pub fn parseFdinfoMapInfo(",
        "pub fn mapReuseObservationFromFdinfo(",
        "pub fn resolveReusePinnedMapAttempt(",
        "pub fn planTokenPreparation(",
    ),
    PACKET_TEST_PATH: (
        'test "phase 8 file-path-handle bridge docs keep the planning-only resource boundary explicit" {',
        'test "phase 8 file-path-handle bridge helper keeps reuse planning smaller than reopen flow" {',
        'test "resolveReusePinnedMapAttempt returns a ready attempt only for compatible pinned-path reuse plans" {',
        'test "planTokenPreparation keeps token readiness gated on the reuse plan" {',
    ),
    PACKET_ONLY_BUILD_PATH: (
        "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        "phase8_file_path_handle_bridge.zig",
        "phase8-file-path-handle-bridge-tests",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"missing-marker:{rel_path}:{marker}")
    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root, rel_path, "\n".join(markers) + "\n")
    if PACKET_BUILD_PATH not in REQUIRED_MARKERS:
        write_text(root, PACKET_BUILD_PATH, "// fixture\n")


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")
    (root / rel_path).write_text(text.replace(marker, "", 1), encoding="utf-8")
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{rel_path}:{marker}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_file_path_handle_bridge_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            (SLICE_PATH, "make -C zigux phase8-file-path-handle-bridge-test"),
            (SLICE_PATH, "planTokenPreparation()"),
            (SURVEY_PATH, "resolveReusePinnedMapAttempt()"),
            (SEQUENCING_PATH, "`zigux/tests/phase8_file_path_handle_bridge.zig`"),
            (MAKEFILE_PATH, "phase8-file-path-handle-bridge-test:"),
            (TESTS_README_PATH, "`make -C zigux phase8-file-path-handle-bridge-test`"),
            (REVIEW_CHECKLIST_PATH, "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`"),
            (PACKET_HELPER_PATH, "pub fn resolveReusePinnedMapAttempt("),
            (PACKET_TEST_PATH, 'test "planTokenPreparation keeps token readiness gated on the reuse plan" {'),
            (PACKET_ONLY_BUILD_PATH, "phase8-file-path-handle-bridge-tests"),
        )
        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
            cases += 1

        missing_file_cases = (
            PACKET_HELPER_PATH,
            PACKET_TEST_PATH,
            PACKET_ONLY_BUILD_PATH,
        )
        for rel_path in missing_file_cases:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            (case_root / rel_path).unlink()
            result = run_validator(case_root)
            expected = f"missing-file:{rel_path}"
            output = result.stdout.strip() or result.stderr.strip() or "no_output"
            if result.returncode == 0 or expected not in output:
                raise SystemExit(f"self-test-mismatch:{expected}:{output}")
            cases += 1

    print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET_SELF_TEST=pass")
    print(f"PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET=fail")
        print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET_PROBLEMS_END")
        return 1

    print("PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET=pass")
    print(f"PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET_ROOT={root}")
    print(f"PHASE8_FILE_PATH_HANDLE_BRIDGE_PACKET_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in REQUIRED_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
BRIDGE_BOUNDARY_SURVEY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
MAKEFILE_PATH = "zigux/Makefile"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"
BRIDGE_TEST_PATH = "zigux/tests/phase8_file_path_handle_bridge.zig"
BOUNDARY_GUARD_PATH = "zigux/tests/phase8_file_path_handle_boundary_guard.zig"
LIBBPF_SEGMENTS_TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"
LIBBPF_SEGMENTS_BUILD_PATH = "zigux/tests/phase8_libbpf_segments_only_build.zig"
MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
PERF_BUFFER_POLL_VERIFY_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig"
READY_BUFFER_ATTEMPT_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig"
READY_BUFFER_FD_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig"
READY_BUFFER_WINDOW_VERIFY_PATH = "tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    VALIDATOR_PATH,
    SURVEY_PATH,
    BRIDGE_BOUNDARY_SURVEY_PATH,
    DOCS_README_PATH,
    TESTS_README_PATH,
    MAKEFILE_PATH,
    PHASE8_BUILD_PATH,
    BRIDGE_TEST_PATH,
    BOUNDARY_GUARD_PATH,
    LIBBPF_SEGMENTS_TEST_PATH,
    LIBBPF_SEGMENTS_BUILD_PATH,
    MANIFEST_PATH,
    PERF_BUFFER_POLL_VERIFY_PATH,
    READY_BUFFER_ATTEMPT_VERIFY_PATH,
    READY_BUFFER_FD_VERIFY_PATH,
    READY_BUFFER_WINDOW_VERIFY_PATH,
)

REQUIRED_MARKERS = {
    VALIDATOR_PATH: (
        'LIBBPF_SHARD_ROUTES_CHECKER = Path("scripts/zigux/check-phase8-libbpf-shard-routes.py")',
        "LIBBPF_SHARD_ROUTES_CHECKER,",
    ),
    SURVEY_PATH: (
        "Current helper-plus-build packet",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/type_names.zig`",
        "`tools/lib/bpf/zigux_segments/pin_path.zig`",
        "`tools/lib/bpf/zigux_segments/manifest.json`",
        "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`",
        "`zigux/tests/phase8_build.zig`",
        "`zigux/tests/phase8_verify_routing_gap.zig`",
        "`zigux/tests/phase8_verify_routing_gap_only_build.zig`",
        "Current authenticated tree readback in this runtime is narrower than some older Phase 8 reminder surfaces:",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig` now keeps wait classification, poll summary, execution summary, and impossible-summary fail-closed outputs explicit beside that same stable-output helper packet.",
        "`zigux/tests/phase8_build.zig` still wires the current libbpf helper-first shard packet.",
        "The directly readable verifier packet now also keeps dedicated stable-output witnesses for cpu-mask parse, string-backed summary, reader-backed summary, auto-count, and fail-closed outputs, logging env/version/error outputs, perf-buffer wait-classification, poll-summary, execution-summary, and impossible-summary fail-closed outputs, pin-path map/program output and validation wrappers, online-CPU route CPU-index and buffer-FD wrappers, ready-buffer attempt wrappers, ready-buffer FD wrappers, ready-buffer window mapped-size and lookup-return wrappers, and type-name lookup plus formatter wrappers explicit beside the aggregate `verify.zig` replay surface.",
        "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`",
        "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`",
        "Current repo-facing reminder surfaces already keep the bridge helper, the focused bridge build shard, the focused libbpf-segment shard, and the shared Phase 8 build replay explicit on `master`, while that same checker packet already keeps the landed `tools/lib/bpf/zigux_segments/logging_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `tools/lib/bpf/zigux_segments/pin_path_verify.zig`, `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` helper-local evidence, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, and `tools/lib/bpf/zigux_segments/type_names_verify.zig` explicit.",
    ),
    BRIDGE_BOUNDARY_SURVEY_PATH: (
        "deferred `perf-buffer-online-cpu-routing` packet",
        "`/sys/devices/system/cpu/online`",
        "`libbpf_num_possible_cpus()`",
        "online CPU filtering",
        "`perf_event_open()` setup",
        "`PERF_EVENT_IOC_ENABLE` enablement",
        "epoll-backed perf FD registration",
    ),
    DOCS_README_PATH: (
        "Phase 8 notes",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
        "`scripts/zigux/validate-phase8.py`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
    ),
    TESTS_README_PATH: (
        "## Phase 8 review packet",
        "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
        "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
        "`tools/lib/bpf/zigux_segments/verify.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "`zigux/tests/phase8_libbpf_segments.zig`",
        "`zigux/tests/phase8_libbpf_segments_only_build.zig`",
        "`make -C zigux phase8-libbpf-segments-test`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-test`",
    ),
    MAKEFILE_PATH: (
        "phase8-libbpf-segments-test:",
        "zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
        "phase8-perf-buffer-poll-test:",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "phase8-test:",
        "zigux/tests/phase8_build.zig --summary all",
    ),
    PHASE8_BUILD_PATH: (
        "../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig",
        "../../tools/lib/bpf/zigux_segments/verify.zig",
        "phase8_libbpf_segments.zig",
        "phase8_verify_routing_gap.zig",
        "phase8-perf-buffer-ready-window-tests",
        "phase8-libbpf-segment-verify-tests",
        "phase8-libbpf-segment-compatibility-tests",
        "phase8-verify-routing-gap-tests",
        "Run the shared Phase 8 tooling tests.",
    ),
    BRIDGE_TEST_PATH: (
        "phase 8 file-path handle bridge proof keeps the manifest-backed helper and deferred bridge split explicit",
        "\\\"slug\\\\\\\": \\\\\\\"fdinfo-map-info-helpers\\\\\\\", \\\\\\\"status\\\\\\\": \\\\\\\"starter_landed\\\\\\\"",
        "\\\"slug\\\\\\\": \\\\\\\"map-reuse-compatibility\\\\\\\", \\\\\\\"status\\\\\\\": \\\\\\\"starter_landed\\\\\\\"",
        "\\\"slug\\\\\\\": \\\\\\\"file-path-and-handle-bridge\\\\\\\", \\\\\\\"status\\\\\\\": \\\\\\\"deferred_high_risk\\\\\\\", \\\\\\\"kind\\\\\\\": \\\\\\\"resource_boundary\\\\\\\"",
    ),
    BOUNDARY_GUARD_PATH: (
        "phase 8 file-path-handle boundary guard keeps landed helper slices distinct from the deferred bridge",
        "\\\"slug\\\\\\\": \\\\\\\"file-path-and-handle-bridge\\\\\\\"",
        "\\\"kind\\\\\\\": \\\\\\\"resource_boundary\\\\\\\"",
        "planTokenPreparation",
        "isMapReuseCompatible",
    ),
    LIBBPF_SEGMENTS_TEST_PATH: (
        'test "phase 8 libbpf-segment compatibility witness keeps the focused verify-routing replay visible" {',
        'test "phase 8 libbpf-segment compatibility witness keeps the shared no-timer poll boundary explicit" {',
        'test "phase 8 libbpf-segment compatibility witness keeps the mixed-source bridge packet visible" {',
    ),
    LIBBPF_SEGMENTS_BUILD_PATH: (
        'b.path("../../tools/lib/bpf/zigux_segments/verify.zig")',
        '"phase8-libbpf-segment-verify-tests"',
        '"Run focused Phase 8 libbpf segment verify build"',
    ),
    MANIFEST_PATH: (
        '\\"slug\\": \\"fdinfo-map-info-helpers\\", \\"status\\": \\"starter_landed\\"',
        '\\"slug\\": \\"map-reuse-compatibility\\", \\"status\\": \\"starter_landed\\"',
        '\\"slug\\": \\"file-path-and-handle-bridge\\", \\"status\\": \\"deferred_high_risk\\", \\"kind\\": \\"resource_boundary\\"',
        "direct procfs reads and descriptor ownership flow",
        "token creation, bpffs reopen flow, and other fd-handle bridge side effects",
    ),
    PERF_BUFFER_POLL_VERIFY_PATH: (
        "phase8 perf-buffer poll helper entrypoints stay explicit",
        "summarizePollExecutionResultFromWaitResult",
        "phase8 perf-buffer poll rejects impossible hand-built summaries and mismatched ready waits",
    ),
    READY_BUFFER_ATTEMPT_VERIFY_PATH: (
        "phase8 ready-buffer attempt helper entrypoints stay explicit",
        "resolveReadyBufferAttemptLookupReturn",
        "phase8 ready-buffer attempt helpers keep errno-shaped outputs stable",
    ),
    READY_BUFFER_FD_VERIFY_PATH: (
        "phase8 ready-buffer fd helper entrypoints stay explicit",
        "resolveReadyBufferFdAtAttempt",
        "phase8 ready-buffer fd helpers keep errno-shaped outputs stable",
    ),
    READY_BUFFER_WINDOW_VERIFY_PATH: (
        "phase8 ready-buffer window helper entrypoints stay explicit",
        "resolveReadyBufferWindowMappedSizeReturnAtAttempt",
        "phase8 ready-buffer window helpers keep lookup-return outputs stable",
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


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")

    (root / rel_path).write_text(text.replace(marker, ""), encoding="utf-8")
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{expected}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_libbpf_shard_routes_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                case_root = Path(tmp) / f"case_{cases}"
                shutil.copytree(baseline_root, case_root)
                assert_missing_case(case_root, rel_path, marker)
                cases += 1

        for rel_path in REQUIRED_FILES[1:]:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            (case_root / rel_path).unlink()
            result = run_validator(case_root)
            expected = f"missing-file:{rel_path}"
            output = result.stdout.strip() or result.stderr.strip() or "no_output"
            if result.returncode == 0:
                raise SystemExit(f"self-test-unexpected-pass:{expected}")
            if expected not in output:
                raise SystemExit(f"self-test-mismatch:{expected}:{output}")
            cases += 1

        missing_script_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_script_root)
        (missing_script_root / SCRIPT_PATH).unlink()
        missing_result = run_validator(missing_script_root)
        missing_output = (
            missing_result.stdout.strip() or missing_result.stderr.strip() or "no_output"
        )
        if missing_result.returncode == 0 or "can't open file" not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTES_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_LIBBPF_SHARD_ROUTES=fail")
        print("PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_LIBBPF_SHARD_ROUTES_PROBLEMS_END")
        return 1

    print("PHASE8_LIBBPF_SHARD_ROUTES=pass")
    print(f"PHASE8_LIBBPF_SHARD_ROUTES_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

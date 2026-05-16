#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase8-online-cpu-routing-packet.py"
SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
BOUNDARY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"
MANIFEST_PATH = "tools/lib/bpf/zigux_segments/manifest.json"
HELPER_PATH = "tools/lib/bpf/zigux_segments/online_cpu_routing.zig"
TEST_PATH = "zigux/tests/phase8_libbpf_segments.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    SURVEY_PATH,
    BOUNDARY_PATH,
    SEQUENCING_PATH,
    MANIFEST_PATH,
    HELPER_PATH,
    TEST_PATH,
)

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`",
        "advanceOnlineCpuCursor()",
        "summarizeNextOnlineCpuRoute()",
        "summarizeOnlineCpuRouting()",
        "broader timeout-sensitive routing behavior",
    ),
    BOUNDARY_PATH: (
        "deferred `perf-buffer-online-cpu-routing` packet",
        "`/sys/devices/system/cpu/online`",
        "`perf_event_open()`",
        "epoll-backed perf FD registration",
        "broader timeout-sensitive routing behavior",
    ),
    SEQUENCING_PATH: (
        "### 3. Libbpf helper lane",
        "`tools/lib/bpf/zigux_segments/manifest.json` still records the helper-first landed slices around logging, pin-path helpers, cpu-mask parsing, type-name helpers, file-path helper-adjacent reviewability, and perf-buffer poll bookkeeping",
        "the same manifest still keeps `perf-buffer-online-cpu-routing` deferred as the interrupt-routing boundary",
    ),
    MANIFEST_PATH: (
        '"slug": "perf-buffer-online-cpu-routing"',
        '"status": "deferred_high_risk"',
        '"kind": "interrupt_routing"',
        '"zigux_destination": "tools/lib/bpf/zigux_segments/online_cpu_routing.zig"',
    ),
    HELPER_PATH: (
        "pub fn advanceOnlineCpuCursor(",
        "pub fn summarizeNextOnlineCpuRoute(",
        "pub fn summarizeOnlineCpuRouting(",
        'test "summarizeOnlineCpuRouting reports the first routed online CPU whose fd slot is empty" {',
    ),
    TEST_PATH: (
        'test "phase 8 libbpf survey keeps routing helper and perf-buffer boundary explicit" {',
        '"tools/lib/bpf/zigux_segments/online_cpu_routing.zig"',
        '"advanceOnlineCpuCursor()"',
        '"summarizeNextOnlineCpuRoute()"',
        '"summarizeOnlineCpuRouting()"',
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
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_online_cpu_routing_packet_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            (SURVEY_PATH, "`tools/lib/bpf/zigux_segments/online_cpu_routing.zig`"),
            (SURVEY_PATH, "summarizeOnlineCpuRouting()"),
            (BOUNDARY_PATH, "`perf_event_open()`"),
            (BOUNDARY_PATH, "broader timeout-sensitive routing behavior"),
            (SEQUENCING_PATH, "the same manifest still keeps `perf-buffer-online-cpu-routing` deferred as the interrupt-routing boundary"),
            (MANIFEST_PATH, '"kind": "interrupt_routing"'),
            (HELPER_PATH, "pub fn summarizeOnlineCpuRouting("),
            (HELPER_PATH, 'test "summarizeOnlineCpuRouting reports the first routed online CPU whose fd slot is empty" {'),
            (TEST_PATH, 'test "phase 8 libbpf survey keeps routing helper and perf-buffer boundary explicit" {'),
            (TEST_PATH, '"summarizeNextOnlineCpuRoute()"'),
        )
        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
            cases += 1

        missing_file_root = Path(tmp) / f"case_{cases}"
        shutil.copytree(baseline_root, missing_file_root)
        (missing_file_root / HELPER_PATH).unlink()
        missing_result = run_validator(missing_file_root)
        missing_output = missing_result.stdout.strip() or missing_result.stderr.strip() or "no_output"
        expected = f"missing-file:{HELPER_PATH}"
        if missing_result.returncode == 0 or expected not in missing_output:
            raise SystemExit(f"self-test-missing-file-mismatch:{missing_output}")
        cases += 1

    print("PHASE8_ONLINE_CPU_ROUTING_PACKET_SELF_TEST=pass")
    print(f"PHASE8_ONLINE_CPU_ROUTING_PACKET_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_ONLINE_CPU_ROUTING_PACKET=fail")
        print("PHASE8_ONLINE_CPU_ROUTING_PACKET_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_ONLINE_CPU_ROUTING_PACKET_PROBLEMS_END")
        return 1

    print("PHASE8_ONLINE_CPU_ROUTING_PACKET=pass")
    print(f"PHASE8_ONLINE_CPU_ROUTING_PACKET_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

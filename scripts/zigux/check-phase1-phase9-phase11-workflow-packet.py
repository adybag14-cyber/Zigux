#!/usr/bin/env python3
"""Guard the current Lane 17 Phase 1 Phase 9/11 workflow packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
CHECKER_REL = Path("scripts/zigux/check-phase1-phase9-phase11-workflow-packet.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    MAKEFILE_REL,
    CHECKER_REL,
)

MARKERS = {
    WORKFLOW_REL: (
        "      - name: Self-test current Phase 9 build-only surface checker",
        "        run: python3 scripts/zigux/check-phase9-build-only-surface.py --self-test",
        "      - name: Check current Phase 9 build-only surface packet",
        "        run: python3 scripts/zigux/check-phase9-build-only-surface.py",
        "      - name: Self-test current Phase 9 trace-events runtime packet checker",
        "        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
        "      - name: Check current Phase 9 trace-events runtime packet",
        "        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
        "      - name: Run current Phase 9 shared loader command-environment boundary guard tests",
        "        run: zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig",
        "      - name: Run current Phase 9 shared loader allocator-init-flow packet",
        "        run: zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
        "      - name: Run current Phase 9 trace-events runtime sample tests",
        "        run: zig test samples/zigux/runtime_trace_events.zig",
        "      - name: Run current Phase 9 registration reentry companion tests",
        "        run: zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        "      - name: Validate current Phase 11 support bundle",
        "        run: make -C zigux phase11-validate",
    ),
    MAKEFILE_REL: (
        "phase9-runtime-loader-command-env-boundary-guard-test:",
        "phase9-runtime-loader-shared-test:",
        "phase9-runtime-trace-events-test:",
        "phase9-first-loadable-runtime-module-parity-test:",
        "phase9-test: phase9-runtime-atomic64-test phase9-runtime-bitmap-test phase9-runtime-loader-shared-test phase9-runtime-trace-events-test phase9-first-loadable-runtime-module-parity-test",
        "phase11-validate:",
        "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    ),
}


def load_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def write_text(root: Path, relative: Path, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_once(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            failures.append(f"missing_file:{relative.as_posix()}")
        elif not path.is_file():
            failures.append(f"non_file_path:{relative.as_posix()}")
    if failures:
        return failures

    for relative, markers in MARKERS.items():
        text = load_text(root, relative)
        for marker in markers:
            failures.extend(require_once(text, f"{relative.as_posix()}:{marker}", marker))

    return failures


def sample_text(relative: Path) -> str:
    lines = list(MARKERS.get(relative, ()))
    if relative == WORKFLOW_REL:
        return "name: zigux-bootstrap\n\njobs:\n  bootstrap:\n    runs-on: ubuntu-latest\n    steps:\n" + "\n".join(lines) + "\n"
    return "\n".join(lines) + ("\n" if lines else "")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    for relative in REQUIRED_FILES:
        write_text(root, relative, sample_text(relative))


def rewrite_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"missing sample marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-phase9-phase11-workflow-packet-") as tmpdir:
        root = Path(tmpdir)

        write_sample_root(root)
        if collect_failures(root):
            print("self-test:baseline_failed")
            return 1
        case_count += 1

        sample_root = root / "sample-root"
        write_sample_root(sample_root)
        if collect_failures(sample_root):
            print("self-test:written_sample_failed")
            return 1
        case_count += 1

        broken_root = root / "missing_checker"
        write_sample_root(broken_root)
        (broken_root / CHECKER_REL).unlink()
        failures = collect_failures(broken_root)
        if f"missing_file:{CHECKER_REL.as_posix()}" not in failures:
            print("self-test:missing_checker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_phase9_workflow_marker"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            WORKFLOW_REL,
            rewrite_once(load_text(broken_root, WORKFLOW_REL), MARKERS[WORKFLOW_REL][9] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{WORKFLOW_REL.as_posix()}:{MARKERS[WORKFLOW_REL][9]}") for item in failures):
            print("self-test:missing_phase9_workflow_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "duplicate_phase11_workflow_marker"
        write_sample_root(broken_root)
        workflow_text = load_text(broken_root, WORKFLOW_REL)
        duplicate = workflow_text.replace(
            MARKERS[WORKFLOW_REL][16],
            MARKERS[WORKFLOW_REL][16] + "\n" + MARKERS[WORKFLOW_REL][16],
            1,
        )
        write_text(broken_root, WORKFLOW_REL, duplicate)
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{WORKFLOW_REL.as_posix()}:{MARKERS[WORKFLOW_REL][16]}") for item in failures):
            print("self-test:duplicate_phase11_workflow_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_phase9_makefile_marker"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            MAKEFILE_REL,
            rewrite_once(load_text(broken_root, MAKEFILE_REL), MARKERS[MAKEFILE_REL][4] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{MAKEFILE_REL.as_posix()}:{MARKERS[MAKEFILE_REL][4]}") for item in failures):
            print("self-test:missing_phase9_makefile_marker_not_detected")
            return 1
        case_count += 1

        broken_root = root / "missing_phase11_makefile_marker"
        write_sample_root(broken_root)
        write_text(
            broken_root,
            MAKEFILE_REL,
            rewrite_once(load_text(broken_root, MAKEFILE_REL), MARKERS[MAKEFILE_REL][8] + "\n"),
        )
        failures = collect_failures(broken_root)
        if not any(item.startswith(f"{MAKEFILE_REL.as_posix()}:{MARKERS[MAKEFILE_REL][8]}") for item in failures):
            print("self-test:missing_phase11_makefile_marker_not_detected")
            return 1
        case_count += 1

    print("PHASE1_PHASE9_PHASE11_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_PHASE9_PHASE11_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE1_PHASE9_PHASE11_WORKFLOW_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root.resolve())
    if failures:
        print("PHASE1_PHASE9_PHASE11_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_PHASE9_PHASE11_WORKFLOW_PACKET=pass")
    print(f"PHASE1_PHASE9_PHASE11_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_PHASE9_PHASE11_WORKFLOW_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
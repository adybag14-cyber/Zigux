#!/usr/bin/env python3
"""Guard the current Phase 1 closure reminder packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

CLOSURE_NOTE_REL = "Documentation/zigux/phase1-closure.md"
MAKEFILE_REL = "zigux/Makefile"

DIRECT_PACKET_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
)

BROADER_COMPANION_GAPS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

REQUIRED_CLOSURE_LINES = (
    "- `PHASE1_STATUS=parked`",
    "- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`",
    "- `PHASE1_HELPER_COUNT=13`",
    "- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
)

FORBIDDEN_MAKEFILE_LINES = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    want = marker.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in DIRECT_PACKET_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_direct_packet_file:{relative_path}")

    if not (root / MAKEFILE_REL).is_file():
        failures.append(f"missing_makefile:{MAKEFILE_REL}")

    for relative_path in BROADER_COMPANION_GAPS:
        if (root / relative_path).exists():
            failures.append(f"unexpected_broader_companion_presence:{relative_path}")

    if failures:
        return failures

    closure_text = read_text(root, CLOSURE_NOTE_REL)
    for marker in REQUIRED_CLOSURE_LINES:
        count = count_exact_line(closure_text, marker)
        if count != 1:
            failures.append(f"closure_line_count:{marker}:expected=1:actual={count}")

    makefile_text = read_text(root, MAKEFILE_REL)
    route_summary_count = count_exact_line(makefile_text, "phase1-route-summary:")
    if route_summary_count != 1:
        failures.append(
            "makefile_phase1_route_summary:expected=1:"
            f"actual={route_summary_count}"
        )

    for marker in FORBIDDEN_MAKEFILE_LINES:
        count = count_exact_line(makefile_text, marker)
        if count != 0:
            failures.append(f"makefile_forbidden_line:{marker}:expected=0:actual={count}")

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in DIRECT_PACKET_FILES:
        if relative_path == CLOSURE_NOTE_REL:
            write_text(root, relative_path, "\n".join(REQUIRED_CLOSURE_LINES) + "\n")
        else:
            write_text(root, relative_path, f"placeholder for {relative_path}\n")
    write_text(root, MAKEFILE_REL, "phase1-route-summary:\n")


def remove_exact_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return
    raise ValueError(f"missing marker {marker!r} in {relative_path}")


def duplicate_exact_line(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing marker {marker!r} in {relative_path}")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [("success", None)]

    for relative_path in DIRECT_PACKET_FILES:
        cases.append((f"missing_direct_packet:{relative_path}", ("remove_file", relative_path)))
    cases.append(("missing_makefile", ("remove_file", MAKEFILE_REL)))
    for relative_path in BROADER_COMPANION_GAPS:
        cases.append((f"unexpected_gap_presence:{relative_path}", ("add_file", relative_path)))
    for marker in REQUIRED_CLOSURE_LINES:
        cases.append((f"missing_line:{marker}", ("remove_line", CLOSURE_NOTE_REL, marker)))
        cases.append((f"duplicate_line:{marker}", ("duplicate_line", CLOSURE_NOTE_REL, marker)))
    cases.append(("missing_route_summary", ("remove_line", MAKEFILE_REL, "phase1-route-summary:")))
    for marker in FORBIDDEN_MAKEFILE_LINES:
        cases.append((f"forbidden_makefile:{marker}", ("add_line", MAKEFILE_REL, marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "remove_file":
                    (root / mutation[1]).unlink()
                elif kind == "add_file":
                    write_text(root, mutation[1], "unexpected broader companion\n")
                elif kind == "remove_line":
                    remove_exact_line(root, mutation[1], mutation[2])
                elif kind == "duplicate_line":
                    duplicate_exact_line(root, mutation[1], mutation[2])
                elif kind == "add_line":
                    path = root / mutation[1]
                    text = path.read_text(encoding="utf-8")
                    path.write_text(text + mutation[2] + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a current-like sample root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        build_sample_repo(args.write_sample_root)
        print(f"PHASE1_CLOSURE_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_PACKET=pass")
    print(f"PHASE1_CLOSURE_PACKET_DIRECT_FILE_COUNT={len(DIRECT_PACKET_FILES)}")
    print(f"PHASE1_CLOSURE_PACKET_BROADER_COMPANION_GAP_COUNT={len(BROADER_COMPANION_GAPS)}")
    print(f"PHASE1_CLOSURE_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_CLOSURE_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

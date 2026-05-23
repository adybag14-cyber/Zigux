#!/usr/bin/env python3
"""Guard the current broader Phase 1 gap packet across closure and reminder surfaces."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
)

EXPECTED_GAP_PATHS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

EXPECTED_GAP_PACKET = ",".join(EXPECTED_GAP_PATHS)

EXACT_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        f"`PHASE1_CURRENT_GAP_PACKET={EXPECTED_GAP_PACKET}`",
        "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.",
        "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them.",
    ),
    "scripts/zigux/README.md": (
        "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    ),
    "zigux/tests/README.md": (
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    ),
    "Documentation/zigux/README.md": (
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    ),
}

FORBIDDEN_WORKFLOW_FRAGMENTS = (
    "python3 scripts/zigux/validate-phase1.py --self-test",
    "python3 scripts/zigux/validate-phase1.py",
    "python3 scripts/zigux/check-phase1-parity.py --self-test",
    "python3 scripts/zigux/check-phase1-parity.py",
    "zig build test --build-file zigux/tests/build.zig",
    "zig build bench --build-file zigux/tests/build.zig",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [path for path in REQUIRED_FILES if not (root / path).is_file()]


def collect_marker_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, markers in EXACT_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                failures.append(
                    f"marker:{relative_path}:expected=1:actual={count}:{marker}"
                )
    return failures


def collect_gap_path_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in EXPECTED_GAP_PATHS:
        if (root / relative_path).exists():
            failures.append(f"gap_path_present:{relative_path}")
    return failures


def collect_workflow_failures(root: Path) -> list[str]:
    failures: list[str] = []
    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    for fragment in FORBIDDEN_WORKFLOW_FRAGMENTS:
        count = workflow.count(fragment)
        if count != 0:
            failures.append(
                f"forbidden_workflow_fragment:expected=0:actual={count}:{fragment}"
            )
    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path}" for path in collect_missing_files(root)]
    if failures:
        return failures
    failures.extend(collect_marker_failures(root))
    failures.extend(collect_gap_path_failures(root))
    failures.extend(collect_workflow_failures(root))
    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    for relative_path, markers in EXACT_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")
    write_text(root, ".github/workflows/zigux-bootstrap.yml", "# no historical phase1 replay routes\n")


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_add_gap_path(root: Path, relative_path: str) -> None:
    write_text(root, relative_path, "# rematerialized unexpectedly\n")


def mutate_add_workflow_fragment(root: Path, fragment: str) -> None:
    target = root / ".github/workflows/zigux-bootstrap.yml"
    text = target.read_text(encoding="utf-8")
    target.write_text(text + fragment + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, str, str] | tuple[str, str] | None]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("remove_file", relative_path)))
    for relative_path, markers in EXACT_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove_marker", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path}", ("duplicate_marker", relative_path, marker)))
    for relative_path in EXPECTED_GAP_PATHS:
        cases.append((f"gap_path_present:{relative_path}", ("add_gap_path", relative_path)))
    for fragment in FORBIDDEN_WORKFLOW_FRAGMENTS:
        cases.append((f"forbidden_workflow:{fragment}", ("add_workflow_fragment", fragment)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-gap-packet-") as tmpdir:
            root = Path(tmpdir)
            write_sample_root(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "remove_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove_marker":
                    mutate_remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate_marker":
                    mutate_duplicate_marker(root, mutation[1], mutation[2])
                elif kind == "add_gap_path":
                    mutate_add_gap_path(root, mutation[1])
                elif kind == "add_workflow_fragment":
                    mutate_add_workflow_fragment(root, mutation[1])
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

    print("PHASE1_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_GAP_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", help="write a synthetic current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root:
        sample_root = Path(args.write_sample_root).resolve()
        if sample_root.exists():
            shutil.rmtree(sample_root)
        write_sample_root(sample_root)
        print(f"PHASE1_GAP_PACKET_SAMPLE_ROOT={sample_root}")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_GAP_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_GAP_PACKET=pass")
    print(f"PHASE1_GAP_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_GAP_PACKET_GAP_PATH_COUNT={len(EXPECTED_GAP_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

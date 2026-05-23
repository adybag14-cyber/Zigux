#!/usr/bin/env python3
"""Guard the current Phase 1 broader-companion wording across reminder surfaces."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

BROADER_COMPANION_FILES = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "## Broader Closure Companions",
        "- `scripts/zigux/validate-phase1.py`",
        "- `scripts/zigux/check-phase1-parity.py`",
        "- `zigux/tests/phase1_helpers.zig`",
        "- `zigux/tests/phase1_bench.zig`",
        "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
        "- `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them.",
    ),
    "Documentation/zigux/review-checklist.md": (
        "while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    "scripts/zigux/README.md": (
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    ),
    "zigux/tests/README.md": (
        "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "Tests-root reviewer prompt:",
        "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
    ),
}

FORBIDDEN_FRAGMENTS = (
    "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "so treat those installer-backed, older validator-first, parity, and replay routes as active current-`master` reminder evidence",
    "so keep those paths framed as active tests-root proof inside this direct-readback reminder packet",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).exists()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:marker:{marker}:expected=1:actual={count}")
    return issues


def collect_forbidden_fragments(text: str, label: str) -> list[str]:
    issues: list[str] = []
    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(f"{label}:forbidden:{fragment}:actual={count}")
    return issues


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if failures:
        return failures

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        failures.extend(collect_exact_markers(text, relative_path, markers))
        failures.extend(collect_forbidden_fragments(text, relative_path))
    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path, markers in MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")


def write_sample_root(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    build_sample_repo(destination)


def mutate_remove_file(root: Path, relative_path: str) -> None:
    (root / relative_path).unlink()


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_append_forbidden(root: Path, relative_path: str, fragment: str) -> None:
    path = root / relative_path
    path.write_text(path.read_text(encoding="utf-8") + fragment + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("remove_file", relative_path)))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append((f"remove_marker:{relative_path}", ("remove_marker", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path}", ("duplicate_marker", relative_path, marker)))
    for fragment in FORBIDDEN_FRAGMENTS:
        cases.append(("forbidden_fragment", ("forbidden_fragment", "zigux/tests/README.md", fragment)))

    for name, payload in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if payload is not None:
                mode = payload[0]
                if mode == "remove_file":
                    mutate_remove_file(root, payload[1])
                elif mode == "remove_marker":
                    mutate_remove_marker(root, payload[1], payload[2])
                elif mode == "duplicate_marker":
                    mutate_duplicate_marker(root, payload[1], payload[2])
                elif mode == "forbidden_fragment":
                    mutate_append_forbidden(root, payload[1], payload[2])

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

    print("PHASE1_BROADER_COMPANION_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BROADER_COMPANION_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", "--repo-root", dest="repo_root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic checker coverage")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample packet root to the given directory and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print(f"PHASE1_BROADER_COMPANION_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    root = repo_root(args.repo_root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_BROADER_COMPANION_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BROADER_COMPANION_PACKET=pass")
    print(f"PHASE1_BROADER_COMPANION_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BROADER_COMPANION_PACKET_GAP_COUNT={len(BROADER_COMPANION_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

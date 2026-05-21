#!/usr/bin/env python3
"""Guard the current parked Phase 1 bench-gap packet across reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
TESTS_README_REL = Path("zigux/tests/README.md")

PARKED_GAP_FILES = (
    Path("scripts/zigux/validate-phase1.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_bench.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
)

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    BENCH_CHECKER_REL,
    TESTS_README_REL,
)

EXACT_MARKERS = {
    DOCS_ROOT_REL: (
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12.",
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    ),
    PHASE1_CLOSURE_REL: (
        "- `scripts/zigux/validate-phase1.py`",
        "- `scripts/zigux/check-phase1-parity.py`",
        "- `zigux/tests/phase1_helpers.zig`",
        "- `zigux/tests/phase1_bench.zig`",
        "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
        "- `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
    ),
    REVIEW_CHECKLIST_REL: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    SCRIPTS_README_REL: (
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
        "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    ),
    BENCH_CHECKER_REL: (
        'EXPECTATIONS = ROOT / "zigux" / "tests" / "fixtures" / "phase1_bench_expectations.json"',
        'PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS',
        'PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS',
        'PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM',
        'PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM',
    ),
    TESTS_README_REL: (
        "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
}

FORBIDDEN_FRAGMENTS = {
    DOCS_ROOT_REL: (
        "treat the bench checker itself as a repo-reality gap here",
    ),
    PHASE1_CLOSURE_REL: (
        "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_absent(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 0 else [f"{label}:forbidden:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_required_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path in PARKED_GAP_FILES:
        if (root / relative_path).exists():
            failures.append(f"unexpected_present_gap_file:{relative_path.as_posix()}")

    for relative_path, markers in EXACT_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_occurrence(
                    text,
                    f"{relative_path.as_posix()}:marker",
                    marker,
                )
            )

    for relative_path, fragments in FORBIDDEN_FRAGMENTS.items():
        text = read_text(root, relative_path)
        for fragment in fragments:
            failures.extend(
                require_absent(
                    text,
                    f"{relative_path.as_posix()}:fragment",
                    fragment,
                )
            )

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        content = "\n".join(EXACT_MARKERS.get(relative_path, ())) + "\n"
        write_text(root, relative_path, content)


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def add_gap_file(root: Path, relative_path: Path) -> None:
    write_text(root, relative_path, "unexpected\n")


def add_forbidden_fragment(root: Path, relative_path: Path, fragment: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + fragment + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("baseline", None)]
    for relative_path, markers in EXACT_MARKERS.items():
        for marker in markers:
            cases.append(
                (
                    f"missing_{relative_path.name}_{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: remove_marker(
                        root, relative_path, marker
                    ),
                )
            )
            cases.append(
                (
                    f"duplicate_{relative_path.name}_{abs(hash(marker))}",
                    lambda root, relative_path=relative_path, marker=marker: duplicate_marker(
                        root, relative_path, marker
                    ),
                )
            )
    for relative_path in PARKED_GAP_FILES:
        cases.append(
            (
                f"gap_present_{relative_path.name}",
                lambda root, relative_path=relative_path: add_gap_file(root, relative_path),
            )
        )
    for relative_path, fragments in FORBIDDEN_FRAGMENTS.items():
        for fragment in fragments:
            cases.append(
                (
                    f"forbidden_{relative_path.name}_{abs(hash(fragment))}",
                    lambda root, relative_path=relative_path, fragment=fragment: add_forbidden_fragment(
                        root, relative_path, fragment
                    ),
                )
            )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bench-gap-selftest-") as tmp:
            root = Path(tmp)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-bench-gap-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-bench-gap-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BENCH_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_GAP_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample repo root and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.write_sample_root:
        build_sample_repo(Path(args.write_sample_root).resolve())
        print(f"PHASE1_BENCH_GAP_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BENCH_GAP_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BENCH_GAP_PACKET=pass")
    print(f"PHASE1_BENCH_GAP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BENCH_GAP_PACKET_GAP_FILE_COUNT={len(PARKED_GAP_FILES)}")
    print(
        "PHASE1_BENCH_GAP_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Guard the current Phase 1 historical gap packet against reminder-surface drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
)

REQUIRED_EXACT_LINES = {
    DOCS_ROOT_REL: {
        "historical_gap_warning": "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
        "gap_alignment": "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    },
    PHASE1_CLOSURE_REL: {
        "gap_packet": "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "narrow_packet_summary": "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them. The already-landed shared tests-root smoke route plus the shipped bench checker and shared reminder checker remain the narrower packet that current `master` can support directly.",
    },
    REVIEW_CHECKLIST_REL: {
        "phase1_question": "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `zigux/Makefile` explicit as the adjacent Phase 1 route-summary evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    },
    SCRIPTS_README_REL: {
        "historical_gap_warning": "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
        "bench_checker_present": "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    },
    TESTS_README_REL: {
        "historical_gap_warning": "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "followthrough_alignment": "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    },
}

REQUIRED_SINGLE_OCCURRENCE_FRAGMENTS = {
    DOCS_ROOT_REL: {
        "validate_phase1_py": "`scripts/zigux/validate-phase1.py`",
        "check_phase1_parity_py": "`scripts/zigux/check-phase1-parity.py`",
        "phase1_bench_zig": "`zigux/tests/phase1_bench.zig`",
        "phase1_bench_expectations_json": "`zigux/tests/fixtures/phase1_bench_expectations.json`",
        "phase1_helpers_c_harness_c": "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "zig_build_test": "`zig build test --build-file zigux/tests/build.zig`",
        "zig_build_bench": "`zig build bench --build-file zigux/tests/build.zig`",
        "make_phase1_validate": "`make -C zigux phase1-validate`",
        "make_phase1_test": "`make -C zigux phase1-test`",
        "make_phase1_bench": "`make -C zigux phase1-bench`",
        "make_phase1": "`make -C zigux phase1`",
    },
    PHASE1_CLOSURE_REL: {
        "validate_phase1_py": "`scripts/zigux/validate-phase1.py`",
        "check_phase1_parity_py": "`scripts/zigux/check-phase1-parity.py`",
        "phase1_bench_zig": "`zigux/tests/phase1_bench.zig`",
        "phase1_bench_expectations_json": "`zigux/tests/fixtures/phase1_bench_expectations.json`",
        "phase1_helpers_c_harness_c": "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "make_phase1_validate": "`make -C zigux phase1-validate`",
        "make_phase1_test": "`make -C zigux phase1-test`",
        "make_phase1_bench": "`make -C zigux phase1-bench`",
        "make_phase1": "`make -C zigux phase1`",
    },
    SCRIPTS_README_REL: {
        "validate_phase1_py": "`scripts/zigux/validate-phase1.py`",
        "check_phase1_parity_py": "`scripts/zigux/check-phase1-parity.py`",
        "phase1_bench_zig": "`zigux/tests/phase1_bench.zig`",
        "phase1_bench_expectations_json": "`zigux/tests/fixtures/phase1_bench_expectations.json`",
        "phase1_helpers_c_harness_c": "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    },
    TESTS_README_REL: {
        "validate_phase1_py": "`scripts/zigux/validate-phase1.py`",
        "check_phase1_parity_py": "`scripts/zigux/check-phase1-parity.py`",
        "phase1_bench_zig": "`zigux/tests/phase1_bench.zig`",
        "phase1_bench_expectations_json": "`zigux/tests/fixtures/phase1_bench_expectations.json`",
        "phase1_helpers_c_harness_c": "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    },
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current in text.splitlines() if current.strip() == expected)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_fragment_count(text: str, label: str, fragment: str, expected_count: int = 1) -> list[str]:
    count = text.count(fragment)
    return [] if count == expected_count else [f"{label}:expected={expected_count}:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        text = load_text(root, relative_path)
        for label, line in labels.items():
            failures.extend(
                require_exact_line(text, f"{relative_path.as_posix()}:{label}", line)
            )
        for label, fragment in REQUIRED_SINGLE_OCCURRENCE_FRAGMENTS.get(relative_path, {}).items():
            failures.extend(
                require_fragment_count(
                    text,
                    f"{relative_path.as_posix()}:{label}",
                    fragment,
                )
            )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_text(relative_path: Path) -> str:
    labels = REQUIRED_EXACT_LINES.get(relative_path, {})
    fragments = REQUIRED_SINGLE_OCCURRENCE_FRAGMENTS.get(relative_path, {})
    lines = ["# sample", ""]
    lines.extend(labels.values())
    lines.extend(
        fragment
        for fragment in fragments.values()
        if not any(fragment in line for line in labels.values())
    )
    return "\n".join(lines) + "\n"


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_file(root, relative_path, sample_text(relative_path))


def mutate_remove(root: Path, relative_path: Path, needle: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(needle + "\n", "", 1), encoding="utf-8")


def mutate_duplicate(root: Path, relative_path: Path, needle: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(needle, needle + "\n" + needle, 1), encoding="utf-8")


def mutate_append(root: Path, relative_path: Path, needle: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + needle + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, Path | None, str | None, str, list[str], str]] = [
        ("success", None, None, "none", [], "exact"),
        (
            "missing_phase1_closure",
            PHASE1_CLOSURE_REL,
            None,
            "missing_file",
            [f"missing_file:{PHASE1_CLOSURE_REL.as_posix()}"],
            "exact",
        ),
    ]

    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        for label, line in labels.items():
            cases.append(
                (
                    f"missing_{relative_path.name}_{label}",
                    relative_path,
                    line,
                    "remove",
                    [f"{relative_path.as_posix()}:{label}:expected=1:actual=0"],
                    "contains",
                )
            )
            cases.append(
                (
                    f"duplicate_{relative_path.name}_{label}",
                    relative_path,
                    line,
                    "duplicate",
                    [f"{relative_path.as_posix()}:{label}:expected=1:actual=2"],
                    "contains",
                )
            )

    for relative_path, labels in REQUIRED_SINGLE_OCCURRENCE_FRAGMENTS.items():
        for label, fragment in labels.items():
            cases.append(
                (
                    f"duplicate_fragment_{relative_path.name}_{label}",
                    relative_path,
                    fragment,
                    "append",
                    [f"{relative_path.as_posix()}:{label}:expected=1:actual=2"],
                    "exact",
                )
            )

    for name, relative_path, needle, operation, expected_failures, expectation_mode in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-gap-packet-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if relative_path and operation == "missing_file":
                (root / relative_path).unlink()
            elif relative_path and needle and operation == "remove":
                mutate_remove(root, relative_path, needle)
            elif relative_path and needle and operation == "duplicate":
                mutate_duplicate(root, relative_path, needle)
            elif relative_path and needle and operation == "append":
                mutate_append(root, relative_path, needle)

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
                continue

            if expectation_mode == "exact" and failures != expected_failures:
                print(f"self-test:{name}:unexpected_failures")
                print(f"expected={expected_failures!r}")
                print(f"actual={failures!r}")
                return 1
            if expectation_mode == "contains" and not all(
                failure in failures for failure in expected_failures
            ):
                print(f"self-test:{name}:missing_expected_failures")
                print(f"expected_subset={expected_failures!r}")
                print(f"actual={failures!r}")
                return 1

    print("PHASE1_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_GAP_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_GAP_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_GAP_PACKET=pass")
    print(f"PHASE1_GAP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_GAP_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_EXACT_LINES.values())}"
    )
    print(
        "PHASE1_GAP_PACKET_REQUIRED_FRAGMENT_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_SINGLE_OCCURRENCE_FRAGMENTS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

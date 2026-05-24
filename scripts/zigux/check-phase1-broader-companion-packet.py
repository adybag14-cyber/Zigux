#!/usr/bin/env python3
"""Guard the current Phase 1 broader-companion wording across live reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

MARKERS = {
    "Documentation/zigux/README.md": (
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "## Broader Closure Companions",
        "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.",
        "- `scripts/zigux/validate-phase1.py`",
        "- `scripts/zigux/check-phase1-parity.py`",
        "- `zigux/tests/phase1_helpers.zig`",
        "- `zigux/tests/phase1_bench.zig`",
        "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
        "- `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them. The already-landed shared tests-root smoke route plus the shipped bench checker and shared reminder checker remain the narrower packet that current `master` can support directly.",
    ),
    "scripts/zigux/README.md": (
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
    ),
    "zigux/tests/README.md": (
        "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
    ),
}

FORBIDDEN_FRAGMENTS = {
    "Documentation/zigux/phase1-closure.md": (
        "## Broader Current Reminder Packet Proof",
        "`PHASE1_CURRENT_REMINDER_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    ),
    "zigux/tests/README.md": (
        "keep those paths framed as active tests-root proof inside this direct-readback reminder packet",
    ),
}


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
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_forbidden_fragments(text: str, label: str, fragments: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    for fragment in fragments:
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
        failures.extend(
            collect_forbidden_fragments(
                text,
                relative_path,
                FORBIDDEN_FRAGMENTS.get(relative_path, ()),
            )
        )
    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        markers = MARKERS.get(relative_path, ())
        write_text(root, relative_path, "\n".join(markers) + ("\n" if markers else ""))


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_append_fragment(root: Path, relative_path: str, fragment: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + fragment + "\n", encoding="utf-8")


def write_sample_root(root: Path) -> None:
    build_sample_repo(root)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1

    def make_missing_file_case(relative_path: str):
        return (
            f"missing_file_{relative_path.replace('/', '_').replace('.', '_')}",
            lambda root, relative_path=relative_path: (root / relative_path).unlink(),
        )

    def make_marker_case(relative_path: str, marker: str, mutation: str):
        mutator = mutate_remove_marker if mutation == "remove" else mutate_duplicate_marker
        return (
            f"{mutation}_{relative_path.replace('/', '_').replace('.', '_')}_{abs(hash(marker))}",
            lambda root, relative_path=relative_path, marker=marker, mutator=mutator: mutator(
                root, relative_path, marker
            ),
        )

    def make_forbidden_fragment_case(relative_path: str, fragment: str):
        return (
            f"forbidden_{relative_path.replace('/', '_').replace('.', '_')}_{abs(hash(fragment))}",
            lambda root, relative_path=relative_path, fragment=fragment: mutate_append_fragment(
                root, relative_path, fragment
            ),
        )

    cases: list[tuple[str, object]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append(make_missing_file_case(relative_path))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append(make_marker_case(relative_path, marker, "remove"))
            cases.append(make_marker_case(relative_path, marker, "duplicate"))
    for relative_path, fragments in FORBIDDEN_FRAGMENTS.items():
        for fragment in fragments:
            cases.append(make_forbidden_fragment_case(relative_path, fragment))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
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
    parser.add_argument(
        "--root",
        "--repo-root",
        dest="repo_root",
        help="override the repository root used for checks",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the guard against synthetic positive and negative cases",
    )
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample repository tree to the given path",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        write_sample_root(destination)
        print(f"PHASE1_BROADER_COMPANION_PACKET_SAMPLE_ROOT={destination}")
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
    print(
        "PHASE1_BROADER_COMPANION_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

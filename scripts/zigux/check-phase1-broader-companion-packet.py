#!/usr/bin/env python3
"""Guard the current Phase 1 broader-companion packet across reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
)

COMPANION_PATHS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

MARKERS = {
    "Documentation/zigux/README.md": (
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12.",
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "## Broader Closure Companions",
        "- `scripts/zigux/validate-phase1.py`",
        "- `scripts/zigux/check-phase1-parity.py`",
        "- `zigux/tests/phase1_helpers.zig`",
        "- `zigux/tests/phase1_bench.zig`",
        "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
        "- `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them. The already-landed shared tests-root smoke route plus the shipped bench checker and shared reminder checker remain the narrower packet that current `master` can support directly.",
    ),
    "Documentation/zigux/review-checklist.md": (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    "scripts/zigux/README.md": (
        "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
    ),
    "zigux/tests/README.md": (
        "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    ),
}

FORBIDDEN_FRAGMENTS = (
    "`scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c` still agree on the current closed-helper reminder packet",
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
            issues.append(f"{label}:{marker}:expected=1:actual={count}")
    return issues


def collect_forbidden_fragments(text: str, label: str) -> list[str]:
    issues: list[str] = []
    for fragment in FORBIDDEN_FRAGMENTS:
        count = text.count(fragment)
        if count != 0:
            issues.append(f"{label}:forbidden:{fragment}:actual={count}")
    return issues


def collect_missing_markers(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        issues.extend(collect_exact_markers(text, relative_path, markers))
        issues.extend(collect_forbidden_fragments(text, relative_path))
    return issues


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


def write_sample_root(destination: Path) -> None:
    build_sample_repo(destination)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        issues = collect_missing_markers(root)
        if issues:
            print("self-test:success:unexpected_failures")
            for item in issues:
                print(item)
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
    for fragment in FORBIDDEN_FRAGMENTS:
        cases.append(make_forbidden_fragment_case("Documentation/zigux/review-checklist.md", fragment))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            issues = collect_missing_markers(root)
            if name == "success":
                if issues:
                    print("self-test:success:unexpected_failures")
                    for item in issues:
                        print(item)
                    return 1
            elif not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BROADER_COMPANION_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BROADER_COMPANION_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    print(f"PHASE1_BROADER_COMPANION_PACKET_COMPANION_COUNT={len(COMPANION_PATHS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        help="write a minimal current-like sample repository root and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        write_sample_root(destination)
        print(f"PHASE1_BROADER_COMPANION_PACKET_SAMPLE_ROOT={destination}")
        return 0

    issues = collect_missing_markers(repo_root(args.root))
    if issues:
        print("PHASE1_BROADER_COMPANION_PACKET=fail")
        for item in issues:
            print(item)
        return 1

    print("PHASE1_BROADER_COMPANION_PACKET=pass")
    print(f"PHASE1_BROADER_COMPANION_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BROADER_COMPANION_PACKET_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in MARKERS.values())}")
    print(f"PHASE1_BROADER_COMPANION_PACKET_COMPANION_COUNT={len(COMPANION_PATHS)}")
    print("PHASE1_BROADER_COMPANION_PACKET_COMPANIONS=" + ",".join(COMPANION_PATHS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

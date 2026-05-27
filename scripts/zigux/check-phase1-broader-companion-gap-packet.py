#!/usr/bin/env python3
"""Guard the current broader Phase 1 companion-gap packet across reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

SURFACE_FILES = (
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/phase1-closure.md"),
    Path("scripts/zigux/README.md"),
    Path("zigux/tests/README.md"),
    Path("zigux/Makefile"),
)

EXPECTED_MISSING_FILES = (
    Path("scripts/zigux/validate-phase1.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("zigux/tests/phase1_bench.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
)

REQUIRED_MARKERS = {
    Path("Documentation/zigux/README.md"): (
        "keep the live owner map, the restored closure note and closure validator, the adjacent route-summary guard, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
        "* the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
    ),
    Path("Documentation/zigux/phase1-closure.md"): (
        "## Broader Closure Companions",
        "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/phase1_helpers_c_harness.c`",
        "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
    ),
    Path("scripts/zigux/README.md"): (
        "`scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
        "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
        "`zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
    ),
    Path("zigux/tests/README.md"): (
        "  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    ),
}

FORBIDDEN_MARKERS = {
    Path("Documentation/zigux/README.md"): (
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12.",
    ),
    Path("zigux/tests/README.md"): (
        "  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in SURFACE_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")

    for relative_path in EXPECTED_MISSING_FILES:
        if (root / relative_path).exists():
            failures.append(f"expected_missing_file_present:{relative_path.as_posix()}")

    for relative_path, markers in REQUIRED_MARKERS.items():
        target = root / relative_path
        if not target.is_file():
            continue
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                failures.append(
                    f"{relative_path.as_posix()}:expected_once:{marker}:actual_count={count}"
                )

        for marker in FORBIDDEN_MARKERS.get(relative_path, ()):
            count = text.count(marker)
            if count != 0:
                failures.append(
                    f"{relative_path.as_posix()}:forbidden:{marker}:actual_count={count}"
                )

    return failures


def make_fixture_tree(root: Path) -> None:
    for relative_path in SURFACE_FILES:
        if relative_path == Path("zigux/Makefile"):
            write_text(
                root / relative_path,
                "\n".join(
                    (
                        "phase1-route-summary:",
                        "phase2-toolchain:",
                        "phase3-validate:",
                        "phase4-validate:",
                        "phase6-validate:",
                        "phase8-validate:",
                        "phase10-validate:",
                        "phase12-validate:",
                        "phase14-validate:",
                    )
                )
                + "\n",
            )
            continue

        content = "\n".join(REQUIRED_MARKERS[relative_path]) + "\n"
        write_text(root / relative_path, content)


def replace_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise ValueError(f"missing expected marker: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    checks_run = 0

    with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-gap-") as tmpdir:
        root = Path(tmpdir)
        make_fixture_tree(root)
        if failures := collect_failures(root):
            print("phase1-broader-companion-gap:self-test:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1
        checks_run += 1

    cases = (
        (
            "missing_surface_file",
            lambda root: (root / Path("scripts/zigux/README.md")).unlink(),
        ),
        (
            "missing_marker",
            lambda root: write_text(
                root / Path("Documentation/zigux/phase1-closure.md"),
                replace_once(
                    read_text(root, Path("Documentation/zigux/phase1-closure.md")),
                    REQUIRED_MARKERS[Path("Documentation/zigux/phase1-closure.md")][1] + "\n",
                ),
            ),
        ),
        (
            "duplicate_marker",
            lambda root: write_text(
                root / Path("zigux/tests/README.md"),
                replace_once(
                    read_text(root, Path("zigux/tests/README.md")),
                    REQUIRED_MARKERS[Path("zigux/tests/README.md")][2],
                    REQUIRED_MARKERS[Path("zigux/tests/README.md")][2]
                    + "\n"
                    + REQUIRED_MARKERS[Path("zigux/tests/README.md")][2],
                ),
            ),
        ),
        (
            "forbidden_old_tests_wording",
            lambda root: write_text(
                root / Path("zigux/tests/README.md"),
                read_text(root, Path("zigux/tests/README.md"))
                + FORBIDDEN_MARKERS[Path("zigux/tests/README.md")][0]
                + "\n",
            ),
        ),
        (
            "unexpected_gap_file_present",
            lambda root: write_text(
                root / Path("scripts/zigux/check-phase1-parity.py"),
                "restored unexpectedly\n",
            ),
        ),
        (
            "missing_makefile",
            lambda root: (root / Path("zigux/Makefile")).unlink(),
        ),
    )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(
            prefix=f"phase1-broader-companion-gap-{name}-"
        ) as tmpdir:
            root = Path(tmpdir)
            make_fixture_tree(root)
            mutate(root)
            if not collect_failures(root):
                print(f"phase1-broader-companion-gap:{name}:expected_failure")
                return 1
            checks_run += 1

    print("PHASE1_BROADER_COMPANION_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BROADER_COMPANION_GAP_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def write_sample_root(destination: Path) -> None:
    make_fixture_tree(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument(
        "--self-test", action="store_true", help="run the built-in checker self-test"
    )
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample tree to the given directory and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BROADER_COMPANION_GAP_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BROADER_COMPANION_GAP_PACKET=pass")
    print(f"PHASE1_BROADER_COMPANION_GAP_PACKET_SURFACE_FILE_COUNT={len(SURFACE_FILES)}")
    print(
        f"PHASE1_BROADER_COMPANION_GAP_PACKET_EXPECTED_MISSING_COUNT={len(EXPECTED_MISSING_FILES)}"
    )
    print(
        "PHASE1_BROADER_COMPANION_GAP_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

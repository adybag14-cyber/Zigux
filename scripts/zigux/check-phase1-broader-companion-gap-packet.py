#!/usr/bin/env python3
"""Guard the current broader Phase 1 companion-gap packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    DOCS_README_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
)

GAP_FILES = (
    Path("scripts/zigux/validate-phase1.py"),
    Path("scripts/zigux/check-phase1-parity.py"),
    Path("zigux/tests/phase1_helpers.zig"),
    Path("zigux/tests/phase1_bench.zig"),
    Path("zigux/tests/fixtures/phase1_bench_expectations.json"),
    Path("zigux/tests/fixtures/phase1_helpers_c_harness.c"),
)

EXPECTED_GAP_PACKET = (
    "scripts/zigux/validate-phase1.py,"
    "scripts/zigux/check-phase1-parity.py,"
    "zigux/tests/phase1_helpers.zig,"
    "zigux/tests/phase1_bench.zig,"
    "zigux/tests/fixtures/phase1_bench_expectations.json,"
    "zigux/tests/fixtures/phase1_helpers_c_harness.c"
)

EXPECTED_CLOSURE_ROUTE_SPLIT = (
    "It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, "
    "`make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as "
    "current repo evidence while those older Phase 1 wrapper names remain historical packet "
    "members rather than active closure proof."
)

EXPECTED_DOCS_BROADER_GAP_LIST = (
    "`scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, "
    "`zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, "
    "`zigux/tests/fixtures/phase1_bench_expectations.json`, "
    "`zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file "
    "zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, "
    "`make -C zigux phase1-validate`, `make -C zigux phase1-test`, "
    "`make -C zigux phase1-bench`, and `make -C zigux phase1`"
)

EXPECTED_SCRIPTS_MAKEFILE_EVIDENCE = (
    "`zigux/Makefile` is current repo evidence again from the scripts root too, because its live "
    "body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded "
    "returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, "
    "Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned "
    "here while the older Phase 1 wrapper names stay historical reminder vocabulary"
)

EXPECTED_TESTS_MAKEFILE_EVIDENCE = (
    "current `master` does materialize `zigux/Makefile` again, and its live body now exposes the "
    "shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and "
    "`phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 "
    "route families, so treat the returned file as current repo evidence while the older Phase 1 "
    "wrapper names remain historical packet members rather than active tests-root proof"
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "## Broader Closure Companions",
        "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.",
        f"`PHASE1_CURRENT_GAP_PACKET={EXPECTED_GAP_PACKET}`",
        EXPECTED_CLOSURE_ROUTE_SPLIT,
    ),
    DOCS_README_REL: (
        EXPECTED_DOCS_BROADER_GAP_LIST,
        "treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members",
    ),
    SCRIPTS_README_REL: (
        "`scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "treat those installer-backed, older validator-first, parity, and replay routes as historical packet members",
        EXPECTED_SCRIPTS_MAKEFILE_EVIDENCE,
    ),
    TESTS_README_REL: (
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet",
        "`scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
        EXPECTED_TESTS_MAKEFILE_EVIDENCE,
    ),
}

FORBIDDEN_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "`PHASE1_CURRENT_GAP_PACKET=scripts/zigux/install-zig.py`",
        "those older Phase 1 wrapper names remain active closure proof",
    ),
    DOCS_README_REL: (
        "treat those installer-backed, older validator-first, bench-route, and replay routes as direct current-master evidence",
    ),
    SCRIPTS_README_REL: (
        "treat those installer-backed, older validator-first, parity, and replay routes as direct current-`master` reminder evidence",
        "older Phase 1 wrapper names stay live current-`master` reminder evidence",
    ),
    TESTS_README_REL: (
        "keep those paths framed as active tests-root proof inside this direct-readback reminder packet",
        "older Phase 1 wrapper names remain active tests-root proof",
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    for path, markers in REQUIRED_MARKERS.items():
        text = load_text(root, path)
        for marker in markers:
            failures.extend(require_exact_occurrence(text, f"{path.as_posix()}:marker", marker))
        for marker in FORBIDDEN_MARKERS.get(path, ()):
            count = text.count(marker)
            if count:
                failures.append(f"{path.as_posix()}:forbidden_marker:actual_count={count}:{marker}")

    for gap_path in GAP_FILES:
        if (root / gap_path).exists():
            failures.append(f"unexpected_materialized_gap:{gap_path.as_posix()}")

    return failures


def sample_phase1_closure() -> str:
    return "\n".join(
        (
            "# Phase 1 Closure",
            "",
            "## Broader Closure Companions",
            "",
            "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.",
            "",
            "- `scripts/zigux/validate-phase1.py`",
            "- `scripts/zigux/check-phase1-parity.py`",
            "- `zigux/tests/phase1_helpers.zig`",
            "- `zigux/tests/phase1_bench.zig`",
            "- `zigux/tests/fixtures/phase1_bench_expectations.json`",
            "- `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
            "",
            f"- `PHASE1_CURRENT_GAP_PACKET={EXPECTED_GAP_PACKET}`",
            "",
            EXPECTED_CLOSURE_ROUTE_SPLIT,
            "",
        )
    )


def sample_docs_readme() -> str:
    return "\n".join(
        (
            "# Zigux Documentation",
            "",
            "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.",
            "",
        )
    )


def sample_scripts_readme() -> str:
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence",
            "",
            f"- {EXPECTED_SCRIPTS_MAKEFILE_EVIDENCE}",
            "",
        )
    )


def sample_tests_readme() -> str:
    return "\n".join(
        (
            "# zigux/tests",
            "",
            f"  * {EXPECTED_TESTS_MAKEFILE_EVIDENCE}",
            f"  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
            "",
        )
    )


SAMPLE_FILES = {
    PHASE1_CLOSURE_REL: sample_phase1_closure,
    DOCS_README_REL: sample_docs_readme,
    SCRIPTS_README_REL: sample_scripts_readme,
    TESTS_README_REL: sample_tests_readme,
}


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for relative_path, builder in SAMPLE_FILES.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(builder(), encoding="utf-8")


def run_self_test() -> None:
    cases = (
        ("baseline", None),
        (
            "missing_closure_route_split",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_ROUTE_SPLIT + "\n", "", 1),
            ),
        ),
        (
            "missing_docs_route_gap",
            lambda root: write_text(
                root / DOCS_README_REL,
                load_text(root, DOCS_README_REL).replace(EXPECTED_DOCS_BROADER_GAP_LIST, "drifted route gap"),
            ),
        ),
        (
            "missing_scripts_makefile_evidence",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL).replace(EXPECTED_SCRIPTS_MAKEFILE_EVIDENCE, "drifted makefile evidence"),
            ),
        ),
        (
            "missing_tests_makefile_evidence",
            lambda root: write_text(
                root / TESTS_README_REL,
                load_text(root, TESTS_README_REL).replace(EXPECTED_TESTS_MAKEFILE_EVIDENCE, "drifted tests makefile evidence"),
            ),
        ),
        (
            "forbidden_scripts_current_master_evidence",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL)
                + "older Phase 1 wrapper names stay live current-`master` reminder evidence\n",
            ),
        ),
        (
            "unexpected_materialized_gap",
            lambda root: write_text(root / GAP_FILES[0], "unexpected current tree body\n"),
        ),
    )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-broader-companion-gap-") as tmpdir:
            sample_root = Path(tmpdir) / "sample"
            write_sample_root(sample_root)
            if mutate is not None:
                mutate(sample_root)
            failures = collect_failures(sample_root)
            if name == "baseline":
                if failures:
                    raise SystemExit("\n".join((f"self-test baseline failed:", *failures)))
            elif not failures:
                raise SystemExit(f"self-test case unexpectedly passed: {name}")

    print("PHASE1_BROADER_COMPANION_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BROADER_COMPANION_GAP_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-test")
    parser.add_argument("--write-sample-root", help="Write a synthetic current-like root and exit")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    root = repo_root(args.root)
    failures = collect_failures(root)
    if failures:
        print("PHASE1_BROADER_COMPANION_GAP_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BROADER_COMPANION_GAP_PACKET=pass")
    print(f"PHASE1_BROADER_COMPANION_GAP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BROADER_COMPANION_GAP_PACKET_GAP_FILE_COUNT={len(GAP_FILES)}")
    print(
        "PHASE1_BROADER_COMPANION_GAP_PACKET_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

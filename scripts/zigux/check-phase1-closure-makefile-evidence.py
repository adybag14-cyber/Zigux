#!/usr/bin/env python3
"""Guard the current Phase 1 closure-side Makefile evidence packet."""

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
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
TESTS_README_REL = Path("zigux/tests/README.md")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    VALIDATOR_REL,
    TESTS_README_REL,
    MAKEFILE_REL,
)

EXPECTED_MARKERS = {
    DOCS_ROOT_REL: (
        "* repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, older validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence, while `zigux/Makefile` is current repo evidence again because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane route families across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14.",
    ),
    PHASE1_CLOSURE_REL: (
        "Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.",
    ),
    REVIEW_CHECKLIST_REL: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `zigux/Makefile` explicit as current repo evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    SCRIPTS_README_REL: (
        "- `scripts/zigux/check-phase1-route-summary-counts.py`, `make -C zigux phase1-route-summary`, and `.github/workflows/zigux-bootstrap.yml` keep the adjacent Phase 1 route-summary guard explicit beside the narrower reminder packet, so scripts-root follow-through can verify the returned non-Phase-1 Makefile route inventory without promoting the older Phase 1 wrappers back into shipped proof",
        "- `zigux/Makefile` is current repo evidence again from the scripts root too, because its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded returned `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so keep that returned route summary aligned here while the older Phase 1 wrapper names stay historical reminder vocabulary",
    ),
    VALIDATOR_REL: (
        '    "phase3-validate:",',
        '    "phase4-validate:",',
        '    "phase6-validate:",',
        '    "phase8-validate:",',
        '    "phase10-validate:",',
        '    "phase12-validate:",',
        '    "phase12-smoke:",',
        '    "phase12-test:",',
        '    "phase12: phase12-validate phase12-smoke phase12-test",',
        '    "phase14-validate:",',
    ),
    TESTS_README_REL: (
        "* current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    ),
    MAKEFILE_REL: (
        "phase1-route-summary:",
        "phase2-toolchain:",
        "phase2-tools:",
        "phase2-kconfig:",
        "phase2-cross:",
        "phase2-genksyms:",
        "phase2-fixdep:",
        "phase2-validate:",
        "phase2: phase2-validate",
        "phase3-validate:",
        "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
        "phase4-validate:",
        "phase6-validate:",
        "phase8-validate:",
        "phase10-validate:",
        "phase12-validate:",
        "phase12-smoke:",
        "phase12-test:",
        "phase12: phase12-validate phase12-smoke phase12-test",
        "phase14-validate",
    ),
}

FORBIDDEN_MARKERS = {
    MAKEFILE_REL: (
        "phase1-validate:",
        "phase1-test:",
        "phase1-bench:",
        "phase1:",
    ),
}


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{needle}"]


def require_absent(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 0 else [f"{label}:forbidden_actual_count={count}:{needle}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    for relative_path, markers in EXPECTED_MARKERS.items():
        text = load_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_occurrence(
                    text,
                    f"{relative_path.as_posix()}:required",
                    marker,
                )
            )

    for relative_path, markers in FORBIDDEN_MARKERS.items():
        text = load_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_absent(
                    text,
                    f"{relative_path.as_posix()}:forbidden",
                    marker,
                )
            )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_tree(root: Path) -> None:
    for relative_path, markers in EXPECTED_MARKERS.items():
        write_text(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [
        ("baseline", None),
        ("missing_docs_marker", lambda root: write_text(root / DOCS_ROOT_REL, "")),
        (
            "missing_closure_marker",
            lambda root: write_text(root / PHASE1_CLOSURE_REL, ""),
        ),
        (
            "missing_review_checklist_marker",
            lambda root: write_text(root / REVIEW_CHECKLIST_REL, ""),
        ),
        (
            "missing_scripts_route_inventory_line",
            lambda root: write_text(root / SCRIPTS_README_REL, EXPECTED_MARKERS[SCRIPTS_README_REL][1] + "\n"),
        ),
        (
            "missing_validator_phase14_marker",
            lambda root: write_text(
                root / VALIDATOR_REL,
                "\n".join(EXPECTED_MARKERS[VALIDATOR_REL][:-1]) + "\n",
            ),
        ),
        (
            "missing_tests_marker",
            lambda root: write_text(root / TESTS_README_REL, ""),
        ),
        (
            "missing_makefile_phase12_aggregate",
            lambda root: write_text(
                root / MAKEFILE_REL,
                "\n".join(
                    marker for marker in EXPECTED_MARKERS[MAKEFILE_REL] if marker != "phase12"
                    and marker != "phase12: phase12-validate phase12-smoke phase12-test"
                )
                + "\n",
            ),
        ),
        (
            "forbidden_phase1_validate_route",
            lambda root: write_text(
                root / MAKEFILE_REL,
                load_text(root, MAKEFILE_REL) + "phase1-validate:\n",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-makefile-evidence-") as tmp:
            root = Path(tmp)
            make_fixture_tree(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-closure-makefile-evidence-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-closure-makefile-evidence-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_CLOSURE_MAKEFILE_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_MAKEFILE_EVIDENCE_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_CLOSURE_MAKEFILE_EVIDENCE=pass")
    print("PHASE1_CLOSURE_MAKEFILE_EVIDENCE_MODE=current-master-safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

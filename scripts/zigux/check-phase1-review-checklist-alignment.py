#!/usr/bin/env python3
"""Guard the current Phase 1 review-checklist alignment packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_README_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    MAKEFILE_REL,
)

EXPECTED_REMINDER_PACKET = (
    "Documentation/zigux/phase1-closure.md,"
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md,"
    "Documentation/zigux/README.md,"
    "Documentation/zigux/review-checklist.md,"
    "scripts/zigux/README.md,"
    "scripts/zigux/check-phase1-string-review-packet.py,"
    "scripts/zigux/check-phase1-direct-owner-markers.py,"
    "scripts/zigux/check-phase1-bench.py,"
    "scripts/zigux/check-phase1-shared-reminder-packet.py,"
    "scripts/zigux/validate-phase1-closure.py,"
    "zigux/tests/README.md,"
    "zigux/tests/build.zig,"
    "zigux/tests/phase1_host_tools_smoke.zig,"
    ".github/workflows/zigux-bootstrap.yml,"
    "zigux/tests/fixtures/phase1_helper_manifest.json"
)

EXPECTED_CHECKLIST_PHASE1 = (
    "if the change touches the shared Phase 1 host-tools closure packet, do "
    "`Documentation/zigux/phase1-closure.md`, "
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, "
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, "
    "`scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, "
    "`scripts/zigux/check-phase1-string-review-packet.py`, "
    "`scripts/zigux/check-phase1-direct-owner-markers.py`, "
    "`scripts/zigux/check-phase1-bench.py`, "
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, "
    "`zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, "
    "`.github/workflows/zigux-bootstrap.yml`, "
    "`zigux/tests/fixtures/phase1_helper_manifest.json`, and "
    "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree "
    "on the current closed-helper reminder packet, keep `zigux/Makefile` explicit as "
    "current repo evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, "
    "Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, "
    "parity, bench-route, and replay names stay framed as historical packet members "
    "until current `master` materializes them again?"
)

EXPECTED_DOCS_PACKET = (
    "the current docs-root Phase 1 reminder packet should stay parked on the live "
    "owner-map, restored closure-side, string-review, direct-owner, and bench guards"
)

EXPECTED_SCRIPTS_PACKET = (
    "`scripts/zigux/check-phase1-string-review-packet.py`, "
    "`scripts/zigux/check-phase1-direct-owner-markers.py`, "
    "`scripts/zigux/check-phase1-bench.py`, "
    "`scripts/zigux/check-phase1-shared-reminder-packet.py`, and "
    "`scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, "
    "direct-owner, bench, shared-reminder, and closure-validator packet explicit "
    "from the scripts root"
)

EXPECTED_SCRIPTS_MAKEFILE_EVIDENCE = (
    "`zigux/Makefile` is current repo evidence again from the scripts root too, "
    "because its live body now exposes the shipped Phase 2 toolchain and kbuild "
    "wrappers together with the bounded returned `phase3-validate` and `phase3` "
    "routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and "
    "Phase 14 route families, so keep that returned route summary aligned here "
    "while the older Phase 1 wrapper names stay historical reminder vocabulary"
)

EXPECTED_TESTS_PACKET = "current direct-readback Phase 1 reminder packet:"

EXPECTED_TESTS_MAKEFILE_EVIDENCE = (
    "current `master` does materialize `zigux/Makefile` again, and its live body now "
    "exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded "
    "`phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, "
    "Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as "
    "current repo evidence while the older Phase 1 wrapper names remain historical "
    "packet members rather than active tests-root proof"
)

EXPECTED_TESTS_GAP = (
    "broader Phase 1 closure companions stay outside the narrow direct-readback packet"
)

EXPECTED_CLOSURE_REMINDER = (
    f"`PHASE1_CURRENT_REMINDER_PACKET={EXPECTED_REMINDER_PACKET}`"
)
EXPECTED_CLOSURE_VALIDATOR = (
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`"
)
EXPECTED_CLOSURE_ROUTE_SUMMARY = (
    "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`"
)

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_REL: (EXPECTED_CHECKLIST_PHASE1,),
    DOCS_README_REL: (EXPECTED_DOCS_PACKET,),
    SCRIPTS_README_REL: (EXPECTED_SCRIPTS_PACKET, EXPECTED_SCRIPTS_MAKEFILE_EVIDENCE),
    TESTS_README_REL: (
        EXPECTED_TESTS_PACKET,
        EXPECTED_TESTS_MAKEFILE_EVIDENCE,
        EXPECTED_TESTS_GAP,
    ),
    PHASE1_CLOSURE_REL: (
        EXPECTED_CLOSURE_REMINDER,
        EXPECTED_CLOSURE_VALIDATOR,
        EXPECTED_CLOSURE_ROUTE_SUMMARY,
    ),
}

REQUIRED_MAKEFILE_MARKERS = (
    "phase2-toolchain:",
    "phase2-tools:",
    "phase2-kconfig:",
    "phase2-cross:",
    "phase2-genksyms:",
    "phase3-validate:",
    "phase3:",
    "phase4-validate:",
    "phase6-validate:",
    "phase8-validate:",
    "phase10-validate:",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12:",
    "phase14-validate:",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase1-validate:",
    "phase1-test:",
    "phase1-bench:",
    "phase1:",
)


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

    makefile_text = load_text(root, MAKEFILE_REL)
    for marker in REQUIRED_MAKEFILE_MARKERS:
        failures.extend(require_exact_occurrence(makefile_text, "zigux/Makefile:marker", marker))
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        count = makefile_text.count(marker)
        if count:
            failures.append(f"zigux/Makefile:forbidden_marker:actual_count={count}:{marker}")

    return failures


def sample_phase1_closure() -> str:
    return "\n".join(
        (
            "# Phase 1 Closure",
            "",
            f"- {EXPECTED_CLOSURE_REMINDER}",
            f"- {EXPECTED_CLOSURE_VALIDATOR}",
            f"- {EXPECTED_CLOSURE_ROUTE_SUMMARY}",
            "",
        )
    )


def sample_docs_readme() -> str:
    return "\n".join(
        (
            "# Zigux Documentation",
            "",
            f"* {EXPECTED_DOCS_PACKET}",
            "",
        )
    )


def sample_review_checklist() -> str:
    return "\n".join(
        (
            "# Zigux Review Checklist",
            "",
            "## Validation",
            f"  * {EXPECTED_CHECKLIST_PHASE1}",
            "",
        )
    )


def sample_scripts_readme() -> str:
    return "\n".join(
        (
            "# scripts/zigux",
            "",
            "## Phase 1",
            f"- {EXPECTED_SCRIPTS_PACKET}",
            f"- {EXPECTED_SCRIPTS_MAKEFILE_EVIDENCE}",
            "",
        )
    )


def sample_tests_readme() -> str:
    return "\n".join(
        (
            "# zigux/tests",
            "",
            "## Phase 1 host-tools review packet",
            f"  * {EXPECTED_TESTS_PACKET}",
            f"  * {EXPECTED_TESTS_MAKEFILE_EVIDENCE}",
            f"  * {EXPECTED_TESTS_GAP}: placeholder",
            "",
        )
    )


def sample_makefile() -> str:
    return "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n"


SAMPLE_FILES = {
    PHASE1_CLOSURE_REL: sample_phase1_closure,
    DOCS_README_REL: sample_docs_readme,
    REVIEW_CHECKLIST_REL: sample_review_checklist,
    SCRIPTS_README_REL: sample_scripts_readme,
    TESTS_README_REL: sample_tests_readme,
    MAKEFILE_REL: sample_makefile,
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
            "missing_checklist_phase1",
            lambda root: write_text(
                root / REVIEW_CHECKLIST_REL,
                load_text(root, REVIEW_CHECKLIST_REL).replace(EXPECTED_CHECKLIST_PHASE1, "drifted checklist packet"),
            ),
        ),
        (
            "missing_closure_validator_marker",
            lambda root: write_text(
                root / PHASE1_CLOSURE_REL,
                load_text(root, PHASE1_CLOSURE_REL).replace(EXPECTED_CLOSURE_VALIDATOR, "drifted closure validator"),
            ),
        ),
        (
            "missing_scripts_makefile_evidence",
            lambda root: write_text(
                root / SCRIPTS_README_REL,
                load_text(root, SCRIPTS_README_REL).replace(EXPECTED_SCRIPTS_MAKEFILE_EVIDENCE, "drifted scripts evidence"),
            ),
        ),
        (
            "missing_tests_gap_marker",
            lambda root: write_text(
                root / TESTS_README_REL,
                load_text(root, TESTS_README_REL).replace(EXPECTED_TESTS_GAP, "drifted tests gap"),
            ),
        ),
        (
            "missing_docs_packet",
            lambda root: write_text(
                root / DOCS_README_REL,
                load_text(root, DOCS_README_REL).replace(EXPECTED_DOCS_PACKET, "drifted docs packet"),
            ),
        ),
        (
            "forbidden_phase1_makefile_route",
            lambda root: write_text(
                root / MAKEFILE_REL,
                load_text(root, MAKEFILE_REL) + "phase1-validate:\n",
            ),
        ),
    )

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-review-checklist-packet-") as tmpdir:
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

    print("PHASE1_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")


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
        print("PHASE1_REVIEW_CHECKLIST_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_REVIEW_CHECKLIST_ALIGNMENT=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_REVIEW_CHECKLIST_ALIGNMENT_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print(
        "PHASE1_REVIEW_CHECKLIST_ALIGNMENT_REQUIRED_MAKEFILE_MARKER_COUNT="
        f"{len(REQUIRED_MAKEFILE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

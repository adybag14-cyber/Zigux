#!/usr/bin/env python3
"""Guard the current-head Phase 4 validation-lane sequencing packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SEQUENCING_NOTE = Path("Documentation/zigux/phase4-validation-lane-sequencing.md")
REVERSIBLE_NOTE = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
REPO_WARNING = Path("scripts/zigux/check-phase4-repo-reality-warning.py")
PERF_PACKET = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")

EXPECTED_SELF_TEST_CASES = 11

SEQUENCING_MARKERS = (
    "current direct-readback shared handoff:",
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase4-repo-reality-warning.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "historical broader shared exact-readback and owner-map packet until a same-family lane rereads or republishes it:",
    "`scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "the dedicated perf lane owns only the landed packet for:",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
    "Keep the Validation and Perf Team decision-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane",
    "Current shared reminder ownership is narrower than that historical label: `P4-L24` now covers the matrix-side remaining-gap reminder around `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py`, while the live `P4-L19` reminder lane covers only the review-checklist wording that mirrors that same checker.",
    "If the drift is limited to the matrix-side or review-checklist reminder surfaces around `scripts/zigux/check-phase4-remaining-gap-matrix.py`, keep it in the live `P4-L24` matrix reminder lane or the live `P4-L19` checklist reminder lane before reopening either parked starter-gap packet.",
    "Keep dedicated local perf checker maintenance in that same dedicated perf packet.",
    "Do not use the shared exact-readback lane to change local-only perf limits or starter-gap packet-local replay wording.",
    "Do not use the parked starter-gap lanes to imply that either Zig starter has landed while the current measurable state is still the dedicated parked survey packet.",
    "reopen the dedicated perf lane only for one checker, manifest, survey, benchmark-command, acceptable-limit, or local-only policy truthfulness repair",
)

REVERSIBLE_MARKERS = (
    "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
    "The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run",
    "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence.",
)

REPO_WARNING_MARKERS = (
    'EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16',
    'EXPECTED_PIN_SELF_TEST_CASES = 14',
    'PERF_BASELINE_CHECKER = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")',
    'REMAINING_GAP_PACKET = (',
    '"scripts/zigux/validate-phase4.py",',
    '"zigux/tests/phase4_build.zig",',
)

PERF_PACKET_MARKERS = (
    'EXPECTED_SELF_TEST_CASES = 13',
    '"decision_owner": "Validation and Perf Team"',
    '"ABI and Runtime Team"',
    '"Shared Subsystems Pod"',
    '"linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey"',
    '"shared_ci_perf_promotion_status": "pending"',
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def read(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.is_file():
        raise RuntimeError(f"missing required file: {rel.as_posix()}")
    return path.read_text(encoding="utf-8")


def write(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require(text: str, markers: tuple[str, ...], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise RuntimeError(f"{label} is missing required fragments: {missing}")


def check(root: Path) -> None:
    require(read(root, SEQUENCING_NOTE), SEQUENCING_MARKERS, SEQUENCING_NOTE.as_posix())
    require(read(root, REVERSIBLE_NOTE), REVERSIBLE_MARKERS, REVERSIBLE_NOTE.as_posix())
    require(read(root, REPO_WARNING), REPO_WARNING_MARKERS, REPO_WARNING.as_posix())
    require(read(root, PERF_PACKET), PERF_PACKET_MARKERS, PERF_PACKET.as_posix())


def build_fixture_tree(root: Path) -> None:
    write(
        root,
        SEQUENCING_NOTE,
        "\n".join(
            [
                "# Phase 4 Validation Lane Sequencing",
                "",
                "Current `master` still exposes this sequencing note and the narrower shared-versus-adjacent owner split, but nearby runs should treat `Documentation/zigux/phase4-reversible-delivery-evidence.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, and `scripts/zigux/check-phase4-reversible-delivery-pins.py` as the current direct-readback handoff before reopening older broader Phase 4 companions.",
                "",
                "- current direct-readback shared handoff:",
                "  - `Documentation/zigux/phase4-reversible-delivery-evidence.md`",
                "  - `Documentation/zigux/review-checklist.md`",
                "  - `zigux/tests/README.md`",
                "  - `scripts/zigux/check-phase4-repo-reality-warning.py`",
                "  - `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
                "- historical broader shared exact-readback and owner-map packet until a same-family lane rereads or republishes it:",
                "  - `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
                "  - `scripts/zigux/validate-phase4.py`",
                "  - `zigux/tests/phase4_build.zig`",
                "- the dedicated perf lane owns only the landed packet for:",
                "  - `scripts/zigux/check-phase4-perf-baseline-packet.py`",
                "  - `zigux/tests/phase4_perf_baseline_manifest.json`",
                "  - `zigux/tests/phase4_perf_baseline_survey.zig`",
                "Keep the Validation and Perf Team decision-owner cue in the dedicated local-only perf packet, but leave the current cross-family coordination-owner split with the ABI and Runtime Team plus Shared Subsystems Pod in the shared exact-readback lane because that wording spans both landed rollback gates.",
                "Current shared reminder ownership is narrower than that historical label: `P4-L24` now covers the matrix-side remaining-gap reminder around `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py`, while the live `P4-L19` reminder lane covers only the review-checklist wording that mirrors that same checker.",
                "If the drift is limited to the matrix-side or review-checklist reminder surfaces around `scripts/zigux/check-phase4-remaining-gap-matrix.py`, keep it in the live `P4-L24` matrix reminder lane or the live `P4-L19` checklist reminder lane before reopening either parked starter-gap packet.",
                "Keep dedicated local perf checker maintenance in that same dedicated perf packet.",
                "Do not use the shared exact-readback lane to change local-only perf limits or starter-gap packet-local replay wording.",
                "Do not use the parked starter-gap lanes to imply that either Zig starter has landed while the current measurable state is still the dedicated parked survey packet.",
                "reopen the dedicated perf lane only for one checker, manifest, survey, benchmark-command, acceptable-limit, or local-only policy truthfulness repair",
                "",
            ]
        ),
    )
    write(
        root,
        REVERSIBLE_NOTE,
        "\n".join(
            [
                "# Phase 4 Reversible Delivery Evidence",
                "",
                "Current direct readback in this run confirmed this note, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase4-repo-reality-warning.py`, `scripts/zigux/check-phase4-reversible-delivery-pins.py`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` on current `master`.",
                "The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run",
                "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence.",
                "",
            ]
        ),
    )
    write(
        root,
        REPO_WARNING,
        "\n".join(
            [
                'EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16',
                'EXPECTED_PIN_SELF_TEST_CASES = 14',
                'PERF_BASELINE_CHECKER = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")',
                'REMAINING_GAP_PACKET = (',
                '    "scripts/zigux/validate-phase4.py",',
                '    "zigux/tests/phase4_build.zig",',
                ')',
                "",
            ]
        ),
    )
    write(
        root,
        PERF_PACKET,
        "\n".join(
            [
                'EXPECTED_SELF_TEST_CASES = 13',
                '"decision_owner": "Validation and Perf Team"',
                '"ABI and Runtime Team"',
                '"Shared Subsystems Pod"',
                '"linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey"',
                '"shared_ci_perf_promotion_status": "pending"',
                "",
            ]
        ),
    )


def expect_failure(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"missing replacement target in fixture: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    try:
        check(root)
    except RuntimeError:
        return
    raise AssertionError(f"expected drift to fail for {rel.as_posix()}: {old!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase4-validation-lane-sequencing-") as tmp:
        root = Path(tmp)
        build_fixture_tree(root)
        check(root)
        cases = 1

        drift_cases = (
            (
                SEQUENCING_NOTE,
                "current direct-readback shared handoff:",
                "current historical handoff:",
            ),
            (
                SEQUENCING_NOTE,
                "the dedicated perf lane owns only the landed packet for:",
                "the shared lane owns the perf packet too:",
            ),
            (
                SEQUENCING_NOTE,
                "Current shared reminder ownership is narrower than that historical label: `P4-L24` now covers the matrix-side remaining-gap reminder around `Documentation/zigux/phase4-validation-matrix.md` plus `scripts/zigux/check-phase4-remaining-gap-matrix.py`, while the live `P4-L19` reminder lane covers only the review-checklist wording that mirrors that same checker.",
                "Current shared reminder ownership is the same as the historical label.",
            ),
            (
                SEQUENCING_NOTE,
                "Keep dedicated local perf checker maintenance in that same dedicated perf packet.",
                "Keep dedicated local perf checker maintenance in the shared exact-readback lane.",
            ),
            (
                REVERSIBLE_NOTE,
                "The broader Phase 4 checker, validator, build, and bitmap replay companions are still repo-reality gaps in this run",
                "The broader Phase 4 companions are all directly readable again.",
            ),
            (
                REVERSIBLE_NOTE,
                "Current direct contents reads for `zigux/tests/atomic64_diff.zig` and `zigux/tests/runtime_atomic64_diff.zig` now return on current `master`, so keep that roadmap-backed differential-gate pair explicit as direct current-head evidence.",
                "The atomic64 pair is no longer current-head evidence.",
            ),
            (
                REPO_WARNING,
                'EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 16',
                'EXPECTED_REPO_REALITY_WARNING_SELF_TEST_CASES = 12',
            ),
            (
                REPO_WARNING,
                'EXPECTED_PIN_SELF_TEST_CASES = 14',
                'EXPECTED_PIN_SELF_TEST_CASES = 8',
            ),
            (
                PERF_PACKET,
                '"decision_owner": "Validation and Perf Team"',
                '"decision_owner": "ABI and Runtime Team"',
            ),
            (
                PERF_PACKET,
                '"linux_style_wrapper": "make -C zigux phase4-perf-baseline-survey"',
                '"linux_style_wrapper": "make -C zigux phase4-test"',
            ),
        )

        for rel, old, new in drift_cases:
            build_fixture_tree(root)
            expect_failure(root, rel, old, new)
            cases += 1

        if cases != EXPECTED_SELF_TEST_CASES:
            print("PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST=fail")
            print(f"expected {EXPECTED_SELF_TEST_CASES} self-test cases, saw {cases}")
            return 1

    print("PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST=pass")
    print(f"PHASE4_VALIDATION_LANE_SEQUENCING_SELF_TEST_CASES={EXPECTED_SELF_TEST_CASES}")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    try:
        check(args.root.resolve())
    except RuntimeError as exc:
        print(f"PHASE4_VALIDATION_LANE_SEQUENCING_CHECK=fail: {exc}")
        return 1
    print("PHASE4_VALIDATION_LANE_SEQUENCING_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

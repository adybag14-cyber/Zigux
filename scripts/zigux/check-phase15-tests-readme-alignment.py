#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

TESTS_README_PATH = Path("zigux/tests/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")
VALIDATOR_REL = "scripts/zigux/validate-phase15.py"

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
    VALIDATOR_REL,
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_build.zig",
)

REQUIRED_MARKERS = (
    "Phase 15 governance packet",
    "Keep the current bounded Phase 15 governance reminder explicit through",
    "Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `scripts/zigux/check-phase15-shared-summary-gap.py` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.",
    "Keep the directly readable tests-root Phase 15 governance packet explicit through",
    "Current `master` does materialize `zigux/tests/phase15_architecture_council_review_process_build.zig`, so keep that focused build-file replay in the directly readable governance packet instead of undercounting the Architecture Council review-process evidence.",
    "Current `master` does materialize `zigux/tests/phase15_handoff_next_steps_manifest.json`, so keep that handoff-specific manifest in the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
    "Current `master` does materialize `zigux/tests/phase15_handoff_next_steps.zig`, so keep that focused handoff-specific replay in the directly readable governance packet instead of carrying the handoff packet as manifest-only inventory.",
    "Current `master` does materialize `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`, so keep that focused lane-sequencing manifest-plus-replay pair in the directly readable governance packet instead of leaving the Architecture Council maintenance route undercounted.",
    "Current `master` does materialize `zigux/tests/phase15_parity_scorecard.json`, so keep that machine-readable parity scorecard companion explicit beside `zigux/tests/phase15_parity_scorecard.zig` in the directly readable governance packet instead of carrying the scorecard as replay-only evidence.",
    "Current `master` now directly materializes `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep that focused lane-owner replay in the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
    "Current `master` now directly materializes `scripts/zigux/validate-phase15.py`, so keep that validator-first maintenance gate explicit beside the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
    "Current `master` does materialize `zigux/tests/phase15_build.zig`, so keep that shared Phase 15 governance build companion explicit beside the directly readable governance packet instead of carrying it as a broader dedicated-build repo-reality gap.",
    "Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names in the same blocked-route bucket until direct readback proves they have returned.",
    "without implying any Architecture Council approval for a freeze-map status change?",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    readme = _read(root / TESTS_README_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in readme:
            failures.append(f"tests_readme:missing:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in readme:
            failures.append(f"tests_readme:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    if not (root / MAKEFILE_PATH).exists():
        failures.append(f"repo:missing_present_path:{MAKEFILE_PATH}")

    return failures


def _sample_readme() -> str:
    direct = "\n".join(f"- `{rel}`" for rel in DIRECT_PACKET_PATHS)
    return f"""# zigux/tests

## Phase 15 governance packet

Keep the current bounded Phase 15 governance reminder explicit through {", ".join(f"`{rel}`" for rel in DIRECT_PACKET_PATHS[:14])}, and `zigux/tests/README.md`.
Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `scripts/zigux/check-phase15-shared-summary-gap.py` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.

Keep the directly readable tests-root Phase 15 governance packet explicit through:
{direct}

Current `master` does materialize `zigux/tests/phase15_architecture_council_review_process_build.zig`, so keep that focused build-file replay in the directly readable governance packet instead of undercounting the Architecture Council review-process evidence.

Current `master` does materialize `zigux/tests/phase15_handoff_next_steps_manifest.json`, so keep that handoff-specific manifest in the directly readable governance packet instead of carrying it as a broader repo-reality gap.

Current `master` does materialize `zigux/tests/phase15_handoff_next_steps.zig`, so keep that focused handoff-specific replay in the directly readable governance packet instead of carrying the handoff packet as manifest-only inventory.

Current `master` does materialize `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`, so keep that focused lane-sequencing manifest-plus-replay pair in the directly readable governance packet instead of leaving the Architecture Council maintenance route undercounted.

Current `master` does materialize `zigux/tests/phase15_parity_scorecard.json`, so keep that machine-readable parity scorecard companion explicit beside `zigux/tests/phase15_parity_scorecard.zig` in the directly readable governance packet instead of carrying the scorecard as replay-only evidence.

Current `master` now directly materializes `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep that focused lane-owner replay in the directly readable governance packet instead of carrying it as a broader repo-reality gap.

Current `master` now directly materializes `scripts/zigux/validate-phase15.py`, so keep that validator-first maintenance gate explicit beside the directly readable governance packet instead of carrying it as a broader repo-reality gap.

Current `master` does materialize `zigux/tests/phase15_build.zig`, so keep that shared Phase 15 governance build companion explicit beside the directly readable governance packet instead of carrying it as a broader dedicated-build repo-reality gap.

Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`, so keep those route names in the same blocked-route bucket until direct readback proves they have returned.

Tests-root reviewer prompt:
- Does the bounded Phase 15 reminder keep the directly readable governance packet, the returned review-process build replay, the returned readiness and handoff survey packet members, the returned focused handoff replay, the shared-summary gap note, the active-governance replay entrypoints, the returned validator-first maintenance gate, the shared governance build companion, and the still-missing route-level surfaces aligned without promoting blocked governance wrappers or deeper-core status changes into current tests-root evidence without implying any Architecture Council approval for a freeze-map status change?
"""


def _seed(root: Path) -> None:
    _write(root / TESTS_README_PATH, _sample_readme())
    for rel in DIRECT_PACKET_PATHS:
        _write(root / rel, "present\n")
    _write(root / MAKEFILE_PATH, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_tests_readme_alignment_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_checker_root = root / "missing_checker"
        _seed(missing_checker_root)
        _write(
            missing_checker_root / TESTS_README_PATH,
            _sample_readme().replace("`scripts/zigux/check-phase15-tests-readme-alignment.py`, ", "", 1),
        )
        failures = collect_failures(missing_checker_root)
        expected = [
            "tests_readme:missing:Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `scripts/zigux/check-phase15-shared-summary-gap.py` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-checker failure: {failures}")

        missing_study_only_checker_root = root / "missing_study_only_checker"
        _seed(missing_study_only_checker_root)
        _write(
            missing_study_only_checker_root / TESTS_README_PATH,
            _sample_readme().replace(
                "`scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, ", "", 1
            ),
        )
        failures = collect_failures(missing_study_only_checker_root)
        expected = [
            "tests_readme:missing:Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `scripts/zigux/check-phase15-shared-summary-gap.py` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-study-only-checker failure: {failures}")

        missing_handoff_note_checker_root = root / "missing_handoff_note_checker"
        _seed(missing_handoff_note_checker_root)
        _write(
            missing_handoff_note_checker_root / TESTS_README_PATH,
            _sample_readme().replace("`scripts/zigux/check-phase15-handoff-note-alignment.py`, ", "", 1),
        )
        failures = collect_failures(missing_handoff_note_checker_root)
        expected = [
            "tests_readme:missing:Keep `scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `scripts/zigux/check-phase15-tests-readme-alignment.py`, `scripts/zigux/check-phase15-review-checklist-study-only-alignment.py`, `scripts/zigux/check-phase15-review-process-handoff.py`, `scripts/zigux/check-phase15-handoff-note-alignment.py`, and `scripts/zigux/check-phase15-shared-summary-gap.py` explicit as the shipped reminder guards so the tests-root summary stays in maintenance-mode truthfulness work instead of implying Architecture Council approval or direct deep-core port-readiness.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-handoff-note-checker failure: {failures}")

        missing_direct_root = root / "missing_direct"
        _seed(missing_direct_root)
        (missing_direct_root / "zigux/tests/phase15_parity_scorecard.zig").unlink()
        failures = collect_failures(missing_direct_root)
        expected = ["repo:missing_direct_path:zigux/tests/phase15_parity_scorecard.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct failure: {failures}")

        missing_build_replay_root = root / "missing_build_replay_marker"
        _seed(missing_build_replay_root)
        _write(
            missing_build_replay_root / TESTS_README_PATH,
            _sample_readme().replace(
                "Current `master` does materialize `zigux/tests/phase15_architecture_council_review_process_build.zig`, so keep that focused build-file replay in the directly readable governance packet instead of undercounting the Architecture Council review-process evidence.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_build_replay_root)
        expected = [
            "tests_readme:missing:Current `master` does materialize `zigux/tests/phase15_architecture_council_review_process_build.zig`, so keep that focused build-file replay in the directly readable governance packet instead of undercounting the Architecture Council review-process evidence.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-build-replay failure: {failures}")

        missing_handoff_manifest_root = root / "missing_handoff_manifest_marker"
        _seed(missing_handoff_manifest_root)
        _write(
            missing_handoff_manifest_root / TESTS_README_PATH,
            _sample_readme().replace(
                "Current `master` does materialize `zigux/tests/phase15_handoff_next_steps_manifest.json`, so keep that handoff-specific manifest in the directly readable governance packet instead of carrying it as a broader repo-reality gap.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_handoff_manifest_root)
        expected = [
            "tests_readme:missing:Current `master` does materialize `zigux/tests/phase15_handoff_next_steps_manifest.json`, so keep that handoff-specific manifest in the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-handoff-manifest failure: {failures}")

        missing_handoff_replay_root = root / "missing_handoff_replay_marker"
        _seed(missing_handoff_replay_root)
        _write(
            missing_handoff_replay_root / TESTS_README_PATH,
            _sample_readme().replace(
                "Current `master` does materialize `zigux/tests/phase15_handoff_next_steps.zig`, so keep that focused handoff-specific replay in the directly readable governance packet instead of carrying the handoff packet as manifest-only inventory.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_handoff_replay_root)
        expected = [
            "tests_readme:missing:Current `master` does materialize `zigux/tests/phase15_handoff_next_steps.zig`, so keep that focused handoff-specific replay in the directly readable governance packet instead of carrying the handoff packet as manifest-only inventory.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-handoff-replay failure: {failures}")

        missing_lane_sequencing_packet_root = root / "missing_lane_sequencing_packet_marker"
        _seed(missing_lane_sequencing_packet_root)
        _write(
            missing_lane_sequencing_packet_root / TESTS_README_PATH,
            _sample_readme().replace(
                "Current `master` does materialize `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`, so keep that focused lane-sequencing manifest-plus-replay pair in the directly readable governance packet instead of leaving the Architecture Council maintenance route undercounted.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_lane_sequencing_packet_root)
        expected = [
            "tests_readme:missing:Current `master` does materialize `zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`, so keep that focused lane-sequencing manifest-plus-replay pair in the directly readable governance packet instead of leaving the Architecture Council maintenance route undercounted.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-lane-sequencing-packet failure: {failures}")

        missing_parity_scorecard_json_root = root / "missing_parity_scorecard_json_marker"
        _seed(missing_parity_scorecard_json_root)
        _write(
            missing_parity_scorecard_json_root / TESTS_README_PATH,
            _sample_readme().replace(
                "Current `master` does materialize `zigux/tests/phase15_parity_scorecard.json`, so keep that machine-readable parity scorecard companion explicit beside `zigux/tests/phase15_parity_scorecard.zig` in the directly readable governance packet instead of carrying the scorecard as replay-only evidence.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_parity_scorecard_json_root)
        expected = [
            "tests_readme:missing:Current `master` does materialize `zigux/tests/phase15_parity_scorecard.json`, so keep that machine-readable parity scorecard companion explicit beside `zigux/tests/phase15_parity_scorecard.zig` in the directly readable governance packet instead of carrying the scorecard as replay-only evidence.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-parity-scorecard-json failure: {failures}")

        missing_lane_owner_root = root / "missing_lane_owner_marker"
        _seed(missing_lane_owner_root)
        _write(
            missing_lane_owner_root / TESTS_README_PATH,
            _sample_readme().replace(
                "Current `master` now directly materializes `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep that focused lane-owner replay in the directly readable governance packet instead of carrying it as a broader repo-reality gap.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_lane_owner_root)
        expected = [
            "tests_readme:missing:Current `master` now directly materializes `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`, so keep that focused lane-owner replay in the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-lane-owner failure: {failures}")

        missing_validator_root = root / "missing_validator_marker"
        _seed(missing_validator_root)
        _write(
            missing_validator_root / TESTS_README_PATH,
            _sample_readme().replace(
                "Current `master` now directly materializes `scripts/zigux/validate-phase15.py`, so keep that validator-first maintenance gate explicit beside the directly readable governance packet instead of carrying it as a broader repo-reality gap.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_validator_root)
        expected = [
            "tests_readme:missing:Current `master` now directly materializes `scripts/zigux/validate-phase15.py`, so keep that validator-first maintenance gate explicit beside the directly readable governance packet instead of carrying it as a broader repo-reality gap.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-validator failure: {failures}")

        missing_build_companion_root = root / "missing_build_companion_marker"
        _seed(missing_build_companion_root)
        _write(
            missing_build_companion_root / TESTS_README_PATH,
            _sample_readme().replace(
                "Current `master` does materialize `zigux/tests/phase15_build.zig`, so keep that shared Phase 15 governance build companion explicit beside the directly readable governance packet instead of carrying it as a broader dedicated-build repo-reality gap.\n\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_build_companion_root)
        expected = [
            "tests_readme:missing:Current `master` does materialize `zigux/tests/phase15_build.zig`, so keep that shared Phase 15 governance build companion explicit beside the directly readable governance packet instead of carrying it as a broader dedicated-build repo-reality gap.",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-build-companion failure: {failures}")

        missing_direct_build_root = root / "missing_direct_build"
        _seed(missing_direct_build_root)
        (missing_direct_build_root / "zigux/tests/phase15_build.zig").unlink()
        failures = collect_failures(missing_direct_build_root)
        expected = ["repo:missing_direct_path:zigux/tests/phase15_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct-build failure: {failures}")

        missing_makefile_root = root / "missing_makefile"
        _seed(missing_makefile_root)
        (missing_makefile_root / MAKEFILE_PATH).unlink()
        failures = collect_failures(missing_makefile_root)
        expected = ["repo:missing_present_path:zigux/Makefile"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-makefile failure: {failures}")

    print("PHASE15_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    print("PHASE15_TESTS_README_ALIGNMENT_SELF_TEST_CASES=12")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 tests-root reminder stays aligned with the current governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE15_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
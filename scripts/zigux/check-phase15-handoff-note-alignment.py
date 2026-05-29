#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")
CHECKER_PATH = Path("scripts/zigux/check-phase15-handoff-note-alignment.py")

EXPECTED_LANE_KEY = "P15-L12"
EXPECTED_PHASE = "Phase 15"
RETIRED_MISSING_REPLAY_MARKER = (
    "no dedicated handoff-specific Zig replay is directly materialized on current `master`"
)
REQUIRED_BOUNDARY_MARKERS = (
    "keep the four freeze-in-C anchors parked",
    "keep the two roadmap study-only anchors parked",
    "treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence",
    "do not treat any direct Zig deep-core bridge as a next-phase commitment while the current blocker posture remains unchanged",
)
REQUIRED_FREEZE_IN_C_PATHS = (
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
)
REQUIRED_STUDY_ONLY_PATHS = (
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
)
MANIFEST_MARKER_GROUPS = (
    ("required_markers", "required marker"),
    ("checker_group_markers", "checker-group marker"),
    ("handoff_rule_markers", "handoff-rule marker"),
    ("roadmap_alignment_markers", "roadmap-alignment marker"),
    ("pending_next_step_markers", "pending-next-step marker"),
    ("next_bounded_future_target_markers", "next-bounded future-target marker"),
    ("missing_route_markers", "missing-route marker"),
)

SAMPLE_MANIFEST: dict[str, Any] = {
    "lane_key": "P15-L12",
    "phase": "Phase 15",
    "surveyed_commit": "current-master-readback-2026-05-27",
    "handoff_note": HANDOFF_NOTE_PATH.as_posix(),
    "checker": CHECKER_PATH.as_posix(),
    "present_paths": [
        "Documentation/zigux/freeze-map.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/phase15_handoff_next_steps_manifest.json",
        "zigux/tests/phase15_handoff_next_steps.zig",
        "scripts/zigux/check-phase15-handoff-note-alignment.py",
        "scripts/zigux/validate-phase15.py",
    ],
    "still_missing_paths": [],
    "required_markers": [
        "PHASE15_STATUS=handoff_next_steps_survey_landed",
        "PHASE15_LANE_KEY=P15-L12",
        "PHASE15_PROVENANCE_MODE=dated_master_readback",
        "an Architecture Council approval workflow implementation",
        "a direct port-readiness decision for any Phase 15 anchor",
    ],
    "checker_group_markers": [
        "one focused docs-readme checker",
        "the focused handoff-note checker",
    ],
    "handoff_rule_markers": [
        "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",
        "if dedicated `phase15*` wrapper routes or a dedicated shared-CI route are published later, reread this note together with those new direct paths before presenting them as current evidence here",
    ],
    "roadmap_alignment_markers": [
        "The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.",
        "These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.",
    ],
    "pending_next_step_markers": [
        "compare the live Phase 15 governance packet against the roadmap first and use the bootstrap ledger only as early-tranche context, because the ledger does not own later-lane status",
        "tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet",
    ],
    "next_bounded_future_target_markers": [
        "reread `Documentation/zigux/review-checklist.md` together with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the current directly materialized governance packet whenever the shared Architecture Council prompts drift",
        "if future work touches `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, keep it study-only unless a smaller-than-boundary seam is explicitly recorded in the governance packet",
    ],
    "missing_route_markers": [
        "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
        "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`",
    ],
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest() -> str:
    return json.dumps(SAMPLE_MANIFEST, indent=2) + "\n"


def _marker_lines(markers: list[str], *, ordered: bool = False) -> str:
    if ordered:
        return "\n".join(f"{index + 1}. {marker}" for index, marker in enumerate(markers))
    return "\n".join(f"- {marker}" for marker in markers)


def _path_lines(paths: list[str]) -> str:
    return "\n".join(f"- `{repo_path}`" for repo_path in paths) or "- none"


def _sample_handoff_note() -> str:
    manifest = SAMPLE_MANIFEST
    boundary_markers = "\n".join(f"- {marker}" for marker in REQUIRED_BOUNDARY_MARKERS)
    freeze_paths = "\n".join(f"- `{repo_path}`" for repo_path in REQUIRED_FREEZE_IN_C_PATHS)
    study_only_paths = "\n".join(f"- `{repo_path}`" for repo_path in REQUIRED_STUDY_ONLY_PATHS)

    return f"""# Phase 15 Handoff Next Steps Survey

- `PHASE15_STATUS=handoff_next_steps_survey_landed`
- `PHASE15_LANE_KEY=P15-L12`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `{manifest['surveyed_commit']}`

## Current handed-off packet on current master

{_path_lines(manifest['present_paths'])}

## Required markers

{_marker_lines(manifest['required_markers'])}

## Checker group markers

{_marker_lines(manifest['checker_group_markers'])}

## Roadmap alignment

{_marker_lines(manifest['roadmap_alignment_markers'])}

## Current governance posture to preserve

{freeze_paths}
{study_only_paths}
{boundary_markers}

## Roadmap-backed open handoff gaps

{_marker_lines(manifest['missing_route_markers'])}

## Pending next-step order

{_marker_lines(manifest['pending_next_step_markers'], ordered=True)}

## Next bounded future targets

{_marker_lines(manifest['next_bounded_future_target_markers'], ordered=True)}

## Handoff rules

{_marker_lines(manifest['handoff_rule_markers'])}

## Still-missing broader paths

{_path_lines(manifest['still_missing_paths'])}
"""


def collect_failures(root: Path) -> list[str]:
    handoff_note = _read_text(root / HANDOFF_NOTE_PATH)
    manifest = _read_manifest(root / MANIFEST_PATH)
    failures: list[str] = []

    if manifest["lane_key"] != EXPECTED_LANE_KEY:
        failures.append(f"handoff manifest lane key drifted from {EXPECTED_LANE_KEY}: {manifest['lane_key']}")
    if manifest["phase"] != EXPECTED_PHASE:
        failures.append(f"handoff manifest phase drifted from {EXPECTED_PHASE}: {manifest['phase']}")
    if manifest["handoff_note"] != HANDOFF_NOTE_PATH.as_posix():
        failures.append(f"handoff manifest note path drifted from {HANDOFF_NOTE_PATH.as_posix()}: {manifest['handoff_note']}")
    if manifest["checker"] != CHECKER_PATH.as_posix():
        failures.append(f"handoff manifest checker path drifted from {CHECKER_PATH.as_posix()}: {manifest['checker']}")
    if manifest["surveyed_commit"] not in handoff_note:
        failures.append("handoff note is missing the manifest surveyed_commit marker")
    if f"`{manifest['checker']}`" not in handoff_note:
        failures.append("handoff note is missing the focused handoff-note checker path")
    if RETIRED_MISSING_REPLAY_MARKER in handoff_note:
        failures.append("handoff note still frames the focused handoff replay as missing")

    for key, label in MANIFEST_MARKER_GROUPS:
        for marker in manifest[key]:
            if marker not in handoff_note:
                failures.append(f"handoff note is missing {label}: {marker}")

    for marker in REQUIRED_BOUNDARY_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff note is missing boundary marker: {marker}")

    for repo_path in manifest["present_paths"]:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing present-path marker: {marker}")
        if not (root / repo_path).exists():
            failures.append(f"handoff note claims present path missing from repo: {marker}")

    for repo_path in manifest["still_missing_paths"]:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing gap-path marker: {marker}")
        if (root / repo_path).exists():
            failures.append(f"handoff note still frames shipped path as missing gap: {marker}")

    for repo_path in REQUIRED_FREEZE_IN_C_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing freeze-in-c path marker: {marker}")

    for repo_path in REQUIRED_STUDY_ONLY_PATHS:
        marker = f"`{repo_path}`"
        if marker not in handoff_note:
            failures.append(f"handoff note is missing study-only path marker: {marker}")

    return failures


def _seed_present_paths(root: Path, manifest: dict[str, Any]) -> None:
    for repo_path in manifest["present_paths"]:
        if repo_path == MANIFEST_PATH.as_posix():
            continue
        _write(root / repo_path, "# fixture\n")


def _expect_failures(root: Path, expected: list[str], label: str) -> None:
    failures = collect_failures(root)
    if failures != expected:
        raise AssertionError(f"unexpected {label} failure: {failures}")


def _fixture(root: Path, note_text: str, manifest_text: str | None = None) -> Path:
    _write(root / HANDOFF_NOTE_PATH, note_text)
    _write(root / MANIFEST_PATH, manifest_text or _sample_manifest())
    manifest = _read_manifest(root / MANIFEST_PATH)
    _seed_present_paths(root, manifest)
    return root


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_handoff_note_") as tmp_dir:
        root = Path(tmp_dir)
        _fixture(root, _sample_handoff_note())
        _expect_failures(root, [], "baseline")

        _expect_failures(
            _fixture(
                root / "missing_boundary",
                _sample_handoff_note().replace(
                    "- treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence\n",
                    "",
                    1,
                ),
            ),
            ["handoff note is missing boundary marker: treat broader docs-root, checklist, scripts-root, tests-root, and dedicated-build Phase 15 wording drift as truthfulness gaps, not as already-landed evidence"],
            "missing-boundary",
        )

        _expect_failures(
            _fixture(
                root / "missing_next_bounded_future_target",
                _sample_handoff_note().replace(
                    "1. reread `Documentation/zigux/review-checklist.md` together with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the current directly materialized governance packet whenever the shared Architecture Council prompts drift\n",
                    "",
                    1,
                ),
            ),
            ["handoff note is missing next-bounded future-target marker: reread `Documentation/zigux/review-checklist.md` together with `Documentation/zigux/phase15-shared-summary-gap.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, and the current directly materialized governance packet whenever the shared Architecture Council prompts drift"],
            "missing-next-bounded-future-target",
        )

        mutated = _sample_manifest().replace('"lane_key": "P15-L12"', '"lane_key": "P15-L99"', 1)
        mutated = mutated.replace('"phase": "Phase 15"', '"phase": "Phase 15 drift"', 1)
        mutated = mutated.replace(f'"handoff_note": "{HANDOFF_NOTE_PATH.as_posix()}"', '"handoff_note": "Documentation/zigux/phase15-handoff-next-step-survey.md"', 1)
        mutated = mutated.replace(f'"checker": "{CHECKER_PATH.as_posix()}"', '"checker": "scripts/zigux/check-phase15-handoff-alignment.py"', 1)
        _expect_failures(
            _fixture(root / "identity_drift", _sample_handoff_note(), mutated),
            [
                "handoff manifest lane key drifted from P15-L12: P15-L99",
                "handoff manifest phase drifted from Phase 15: Phase 15 drift",
                "handoff manifest note path drifted from Documentation/zigux/phase15-handoff-next-steps-survey.md: Documentation/zigux/phase15-handoff-next-step-survey.md",
                "handoff manifest checker path drifted from scripts/zigux/check-phase15-handoff-note-alignment.py: scripts/zigux/check-phase15-handoff-alignment.py",
                "handoff note is missing the focused handoff-note checker path",
            ],
            "identity-drift",
        )

        _expect_failures(
            _fixture(
                root / "missing_route_marker",
                _sample_handoff_note().replace(
                    "- no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`\n",
                    "",
                    1,
                ),
            ),
            ["handoff note is missing missing-route marker: no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`"],
            "missing-route-marker",
        )

        _expect_failures(
            _fixture(
                root / "retired_gap",
                _sample_handoff_note() + "\n- no dedicated handoff-specific Zig replay is directly materialized on current `master`\n",
            ),
            ["handoff note still frames the focused handoff replay as missing"],
            "retired-gap",
        )

    print("PHASE15_HANDOFF_NOTE_ALIGNMENT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that the Phase 15 handoff note stays aligned with the current governance packet and dedicated handoff manifest.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root containing Documentation/zigux, scripts/zigux, and zigux/tests")
    parser.add_argument("--self-test", action="store_true", help="exercise the checker against synthetic repo fixtures")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE15_HANDOFF_NOTE_ALIGNMENT_FAILURE={failure}")
        return 1

    print("PHASE15_HANDOFF_NOTE_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

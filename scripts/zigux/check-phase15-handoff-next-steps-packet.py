#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase15_handoff_next_steps_manifest.json")

EXPECTED_LANE_KEY = "P15-L12"
EXPECTED_PHASE = "Phase 15"
EXPECTED_SURVEYED_COMMIT = "current-master-readback-2026-05-27"
EXPECTED_CHECKER = "scripts/zigux/check-phase15-handoff-note-alignment.py"

EXPECTED_PRESENT_PATHS = [
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-deep-core-blocker-survey.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-architecture-council-decision-index.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "zigux-alpha/README.md",
    "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md",
    "zigux/tests/phase15_freeze_map_governance.zig",
    "zigux/tests/phase15_parity_scorecard.json",
    "zigux/tests/phase15_parity_scorecard.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
    "zigux/tests/phase15_architecture_council_review_process.zig",
    "zigux/tests/phase15_architecture_council_review_process_build.zig",
    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
    "zigux/tests/phase15_governance_lane_sequencing.zig",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_indefinite_c_policy.json",
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-review-checklist-study-only-alignment.py",
    "scripts/zigux/check-phase15-readiness-gate-packet.py",
    "scripts/zigux/check-phase15-tests-readme-alignment.py",
    "scripts/zigux/check-phase15-architecture-council-packet.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
    "scripts/zigux/check-phase15-handoff-note-alignment.py",
    "scripts/zigux/validate-phase15.py",
]

EXPECTED_REQUIRED_MARKERS = [
    "PHASE15_STATUS=handoff_next_steps_survey_landed",
    "PHASE15_LANE_KEY=P15-L12",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "The dedicated governance-lane sequencing manifest `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, the focused governance-lane sequencing Zig replay `zigux/tests/phase15_governance_lane_sequencing.zig`, the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json`, and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`",
    "The focused freeze-map governance replay `zigux/tests/phase15_freeze_map_governance.zig`, the focused parity-scorecard machine-readable companion `zigux/tests/phase15_parity_scorecard.json`, and the focused parity-scorecard Zig replay `zigux/tests/phase15_parity_scorecard.zig` are also directly materialized on current `master`.",
    "The dedicated deep-core blocker survey `Documentation/zigux/phase15-deep-core-blocker-survey.md` is also directly materialized on current `master` and keeps the roadmap-versus-current-master blocker crosswalk explicit beside the broader handoff packet.",
    "Treat this note together with `zigux/tests/phase15_governance_lane_sequencing_manifest.json`, `zigux/tests/phase15_governance_lane_sequencing.zig`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, `zigux/tests/phase15_handoff_next_steps.zig`, and `zigux/tests/phase15_build.zig` as the handoff-specific source of truth while the blocked route bodies and shared-CI route remain gap-tracked.",
    "The dedicated validator `scripts/zigux/validate-phase15.py`, the dedicated Architecture Council packet checker `scripts/zigux/check-phase15-architecture-council-packet.py`, and shared build companion `zigux/tests/phase15_build.zig` are directly materialized on current `master`, but they do not by themselves land the broader dedicated `phase15*` wrapper routes or shared-CI route.",
    "an Architecture Council approval workflow implementation",
    "a direct port-readiness decision for any Phase 15 anchor",
]

EXPECTED_CHECKER_GROUP_MARKERS = [
    "one focused docs-readme checker",
    "one focused scripts-readme checker",
    "one focused review-process checker",
    "one focused review-checklist study-only checker",
    "one focused readiness-packet checker",
    "one focused tests-readme checker",
    "one focused Architecture Council packet checker",
    "the shared-summary gap checker",
    "the focused handoff-note checker",
]

EXPECTED_HANDOFF_RULE_MARKERS = [
    "if docs-root, checklist, tests-root, or scripts-root Phase 15 reminder wording drifts",
    "if dedicated `phase15*` wrapper routes or a dedicated shared-CI route are published later, reread this note together with those new direct paths before presenting them as current evidence here",
]

EXPECTED_ROADMAP_ALIGNMENT_MARKERS = [
    "The roadmap-required Phase 15 governance features are already materialized on current `master`: the freeze map, the Architecture Council review process, the parity scorecard, and the policy for code that remains in C indefinitely all have directly readable owner notes in the current packet.",
    "`zigux-alpha/README.md` and `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md` keep the bootstrap boundary explicit: the ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so later-lane Phase 15 status still has to be confirmed in the live product docs, current repo tree, and active lane notes.",
    "These are handoff and reminder-surface gaps, not missing ownership of the roadmap's four required governance features.",
]

EXPECTED_PENDING_NEXT_STEP_MARKERS = [
    "compare the live Phase 15 governance packet against the roadmap first and use the bootstrap ledger only as early-tranche context, because the ledger does not own later-lane status",
    "tighten the smallest shared reminder surface first if docs-root, checklist, scripts-root, or tests-root wording drifts away from the directly materialized governance packet",
    "reread this handoff note together with any newly landed dedicated `phase15*` wrapper or shared-CI route recovery before treating that broader replay surface as current evidence here",
    "revisit freeze-map or parity-scorecard status only if an owning governance packet changes or a deep-core blocker disposition actually moves",
]

EXPECTED_MISSING_ROUTE_MARKERS = [
    "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`",
    "no dedicated shared-CI Phase 15 validate, test, or aggregate route is materialized in `.github/workflows/zigux-bootstrap.yml` on current `master`",
]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _placeholder_for(path: str) -> str:
    if path.endswith(".py"):
        return "#!/usr/bin/env python3\n"
    if path.endswith(".json"):
        return "{}\n"
    if path.endswith(".md"):
        return f"# Placeholder for {path}\n"
    if path.endswith(".zig"):
        return 'const std = @import("std");\n\ntest "placeholder" {\n    try std.testing.expect(true);\n}\n'
    return "\n"


def _expected_manifest() -> dict[str, object]:
    return {
        "lane_key": EXPECTED_LANE_KEY,
        "phase": EXPECTED_PHASE,
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "handoff_note": str(HANDOFF_NOTE_PATH),
        "checker": EXPECTED_CHECKER,
        "present_paths": EXPECTED_PRESENT_PATHS,
        "still_missing_paths": [],
        "required_markers": EXPECTED_REQUIRED_MARKERS,
        "checker_group_markers": EXPECTED_CHECKER_GROUP_MARKERS,
        "handoff_rule_markers": EXPECTED_HANDOFF_RULE_MARKERS,
        "roadmap_alignment_markers": EXPECTED_ROADMAP_ALIGNMENT_MARKERS,
        "pending_next_step_markers": EXPECTED_PENDING_NEXT_STEP_MARKERS,
        "missing_route_markers": EXPECTED_MISSING_ROUTE_MARKERS,
    }


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    note_path = root / HANDOFF_NOTE_PATH
    manifest_path = root / MANIFEST_PATH

    if not note_path.exists():
        failures.append(f"missing_required_path:{HANDOFF_NOTE_PATH}")
    if not manifest_path.exists():
        failures.append(f"missing_required_path:{MANIFEST_PATH}")
    if failures:
        return failures

    note = _read_text(note_path)
    manifest = json.loads(_read_text(manifest_path))
    expected = _expected_manifest()

    for key in (
        "lane_key",
        "phase",
        "surveyed_commit",
        "handoff_note",
        "checker",
        "present_paths",
        "still_missing_paths",
        "required_markers",
        "checker_group_markers",
        "handoff_rule_markers",
        "roadmap_alignment_markers",
        "pending_next_step_markers",
        "missing_route_markers",
    ):
        if manifest.get(key) != expected[key]:
            failures.append(f"manifest_mismatch:{key}")

    for path in EXPECTED_PRESENT_PATHS:
        if not (root / path).exists():
            failures.append(f"missing_present_path:{path}")

    for marker_group in (
        EXPECTED_REQUIRED_MARKERS,
        EXPECTED_CHECKER_GROUP_MARKERS,
        EXPECTED_HANDOFF_RULE_MARKERS,
        EXPECTED_ROADMAP_ALIGNMENT_MARKERS,
        EXPECTED_PENDING_NEXT_STEP_MARKERS,
        EXPECTED_MISSING_ROUTE_MARKERS,
    ):
        for marker in marker_group:
            if marker not in note:
                failures.append(f"missing_note_marker:{marker}")

    for path in EXPECTED_PRESENT_PATHS:
        if path not in note:
            failures.append(f"missing_note_path:{path}")

    return failures


def _sample_note() -> str:
    lines = [
        "# Phase 15 Handoff Next Steps Survey",
        "",
        "## Status",
        "",
        "- `PHASE15_STATUS=handoff_next_steps_survey_landed`",
        "- `PHASE15_LANE_KEY=P15-L12`",
        "- `PHASE15_PROVENANCE_MODE=dated_master_readback`",
        f"- surveyed against dated current-master readback marker `{EXPECTED_SURVEYED_COMMIT}`",
        "",
        "## Packet",
        "",
    ]
    for marker in EXPECTED_REQUIRED_MARKERS:
        lines.append(f"- {marker}")
    lines.append("")
    lines.append("## Present paths")
    lines.append("")
    for path in EXPECTED_PRESENT_PATHS:
        lines.append(f"- `{path}`")
    lines.append("")
    lines.append("## Checker group")
    lines.append("")
    for marker in EXPECTED_CHECKER_GROUP_MARKERS:
        lines.append(f"- {marker}")
    lines.append("")
    lines.append("## Handoff rules")
    lines.append("")
    for marker in EXPECTED_HANDOFF_RULE_MARKERS:
        lines.append(f"- {marker}")
    lines.append("")
    lines.append("## Roadmap alignment")
    lines.append("")
    for marker in EXPECTED_ROADMAP_ALIGNMENT_MARKERS:
        lines.append(f"- {marker}")
    lines.append("")
    lines.append("## Pending next steps")
    lines.append("")
    for marker in EXPECTED_PENDING_NEXT_STEP_MARKERS:
        lines.append(f"- {marker}")
    lines.append("")
    lines.append("## Missing routes")
    lines.append("")
    for marker in EXPECTED_MISSING_ROUTE_MARKERS:
        lines.append(f"- {marker}")
    lines.append("")
    return "\n".join(lines) + "\n"


def write_sample_root(root: Path) -> None:
    _write_text(root / HANDOFF_NOTE_PATH, _sample_note())
    _write_text(root / MANIFEST_PATH, json.dumps(_expected_manifest(), indent=2) + "\n")
    for path in EXPECTED_PRESENT_PATHS:
        if path == str(MANIFEST_PATH):
            continue
        _write_text(root / path, _placeholder_for(path))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase15_handoff_packet_") as tmp_dir:
        base = Path(tmp_dir)

        passing_root = base / "passing"
        write_sample_root(passing_root)
        failures = collect_failures(passing_root)
        if failures:
            raise AssertionError(f"sample root should pass: {failures}")

        lane_root = base / "lane"
        write_sample_root(lane_root)
        manifest = json.loads(_read_text(lane_root / MANIFEST_PATH))
        manifest["lane_key"] = "P15-L99"
        _write_text(lane_root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        failures = collect_failures(lane_root)
        if failures != ["manifest_mismatch:lane_key"]:
            raise AssertionError(f"unexpected lane mismatch result: {failures}")

        missing_path_root = base / "missing_path"
        write_sample_root(missing_path_root)
        (missing_path_root / "zigux/tests/phase15_build.zig").unlink()
        failures = collect_failures(missing_path_root)
        if failures != ["missing_present_path:zigux/tests/phase15_build.zig"]:
            raise AssertionError(f"unexpected missing path result: {failures}")

        missing_marker_root = base / "missing_marker"
        write_sample_root(missing_marker_root)
        note = _read_text(missing_marker_root / HANDOFF_NOTE_PATH)
        marker = EXPECTED_REQUIRED_MARKERS[3]
        _write_text(
            missing_marker_root / HANDOFF_NOTE_PATH,
            note.replace(f"- {marker}\n", "", 1),
        )
        failures = collect_failures(missing_marker_root)
        if failures != [f"missing_note_marker:{marker}"]:
            raise AssertionError(f"unexpected missing marker result: {failures}")

        missing_note_path_root = base / "missing_note_path"
        write_sample_root(missing_note_path_root)
        note = _read_text(missing_note_path_root / HANDOFF_NOTE_PATH)
        path = EXPECTED_PRESENT_PATHS[0]
        _write_text(missing_note_path_root / HANDOFF_NOTE_PATH, note.replace(f"- `{path}`\n", "", 1))
        failures = collect_failures(missing_note_path_root)
        if failures != [f"missing_note_path:{path}"]:
            raise AssertionError(f"unexpected missing note path result: {failures}")

    print("PHASE15_HANDOFF_NEXT_STEPS_PACKET_SELF_TEST=pass")
    print("PHASE15_HANDOFF_NEXT_STEPS_PACKET_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 15 handoff next-steps packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a passing sample root for focused packet replay",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE15_HANDOFF_NEXT_STEPS_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        print("PHASE15_HANDOFF_NEXT_STEPS_PACKET=fail")
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_HANDOFF_NEXT_STEPS_PACKET=pass")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_PACKET_PRESENT_PATH_COUNT={len(EXPECTED_PRESENT_PATHS)}")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_PACKET_REQUIRED_MARKER_COUNT={len(EXPECTED_REQUIRED_MARKERS)}")
    print(f"PHASE15_HANDOFF_NEXT_STEPS_PACKET_PENDING_STEP_COUNT={len(EXPECTED_PENDING_NEXT_STEP_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

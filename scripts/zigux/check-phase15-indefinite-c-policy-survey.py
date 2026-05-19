#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

SURVEY_REL = "Documentation/zigux/phase15-indefinite-c-policy-survey.md"
POLICY_REL = "Documentation/zigux/phase15-indefinite-c-policy.md"
POLICY_JSON_REL = "zigux/tests/phase15_indefinite_c_policy.json"
POLICY_ZIG_REL = "zigux/tests/phase15_indefinite_c_policy.zig"
BLOCKER_EVIDENCE_REL = "zigux/tests/phase15_indefinite_c_blocker_evidence.zig"
LANE_ALIGNMENT_REL = "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig"
FREEZE_MAP_REL = "Documentation/zigux/freeze-map.md"
LANE_NOTE_REL = "Documentation/zigux/phase15-governance-lane-sequencing.md"
HANDOFF_REL = "Documentation/zigux/phase15-handoff-next-steps-survey.md"
READINESS_REL = "Documentation/zigux/phase15-readiness-gate-survey.md"
DOCS_README_REL = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"
TESTS_README_REL = "zigux/tests/README.md"
VALIDATOR_REL = "scripts/zigux/validate-phase15.py"

REQUIRED_FILES = (
    SURVEY_REL,
    POLICY_REL,
    POLICY_JSON_REL,
    POLICY_ZIG_REL,
    BLOCKER_EVIDENCE_REL,
    LANE_ALIGNMENT_REL,
    FREEZE_MAP_REL,
    LANE_NOTE_REL,
    HANDOFF_REL,
    READINESS_REL,
    DOCS_README_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    VALIDATOR_REL,
)

SURVEY_MARKERS = (
    "PHASE15_LANE_KEY=P15-L13",
    "PHASE15_STATUS=indefinite_c_policy_survey",
    "The roadmap says Phase 15 must include a policy for code that remains in C indefinitely.",
    "The current same-lane gap is not a missing indefinite-C policy packet.",
    "the roadmap-required indefinite-C policy packet is landed",
    "no Architecture Council approval is recorded for a freeze-map status change",
    "every freeze-in-C anchor remains blocked from a direct Zigux port claim",
    "phase15-deep-core-status-change-blocker",
    "Keep this packet parked unless one of the named reopen triggers fires or the deep-core blocker posture changes.",
)

POLICY_MARKERS = (
    "PHASE15_STATUS=indefinite_c_policy_packet_landed",
    "PHASE15_LANE_KEY=P15-L16",
    "policy for code that remains in C indefinitely",
    "There is no silent exception path around the indefinite-C policy.",
    "The only allowed exception is an Architecture Council reopen request",
    "narrower_followup_answers_blocker",
    "evidence_packet_stale_or_contradictory",
    "ownership_or_validation_changed",
)

FREEZE_MAP_MARKERS = (
    "the existing C implementation remains the product source of truth for every freeze-in-C anchor",
    "there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review",
)

LANE_NOTE_MARKERS = (
    "- `indefinite-c-policy`: owns `Documentation/zigux/phase15-indefinite-c-policy.md`, `zigux/tests/phase15_indefinite_c_policy.json`, `zigux/tests/phase15_indefinite_c_policy.zig`, `zigux/tests/phase15_indefinite_c_blocker_evidence.zig`, and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "route stay-in-C policy fields, exception posture, blocker-evidence replay, and lane-owner-alignment maintenance to `indefinite-c-policy` only",
)

HANDOFF_MARKERS = (
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "the broader Phase 15 governance family now includes `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard-survey.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`",
)

READINESS_MARKERS = (
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "the remaining blocker is still `phase15-deep-core-status-change-blocker`",
)

DOCS_README_MARKERS = (
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "keep the current parked governance packet reviewable without implying any Architecture Council approval for a freeze-map status change.",
)

REVIEW_CHECKLIST_MARKERS = (
    "indefinite-C policy link or non-applicability note",
)

SCRIPTS_README_MARKERS = ()

TESTS_README_MARKERS = (
    "zigux/tests/phase15_indefinite_c_policy.zig",
    "zigux/tests/phase15_indefinite_c_blocker_evidence.zig",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
)

VALIDATOR_MARKERS = (
    POLICY_JSON_REL,
    POLICY_ZIG_REL,
    BLOCKER_EVIDENCE_REL,
    LANE_ALIGNMENT_REL,
)

EXPECTED_ANCHORS = [
    "kernel/sched/core.c",
    "mm/page_alloc.c",
    "kernel/rcu/tree.c",
    "net/core/skbuff.c",
]

EXPECTED_REQUIREMENT_IDS = [
    "indefinite-c-source-of-truth",
    "indefinite-c-recordkeeping",
    "indefinite-c-allowed-work",
    "indefinite-c-exception-path",
    "indefinite-c-reopen-gate",
    "indefinite-c-reopen-trigger-catalog",
]

EXPECTED_GAP_IDS = [
    "phase15-indefinite-c-policy-note",
    "phase15-indefinite-c-policy-manifest",
    "phase15-indefinite-c-policy-test",
    "phase15-build-gate-indefinite-c-policy",
    "phase15-indefinite-c-field-sync-followup",
    "phase15-indefinite-c-roadmap-continuity-survey",
    "phase15-indefinite-c-dated-readback-provenance-refresh",
    "phase15-indefinite-c-maintenance-handoff",
    "phase15-deep-core-status-change-blocker",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _require_markers(name: str, source: str, markers: tuple[str, ...], issues: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            issues.append(f"{name}:missing:{marker}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    survey = _read(root / SURVEY_REL)
    policy = _read(root / POLICY_REL)
    freeze_map = _read(root / FREEZE_MAP_REL)
    lane_note = _read(root / LANE_NOTE_REL)
    handoff = _read(root / HANDOFF_REL)
    readiness = _read(root / READINESS_REL)
    docs_readme = _read(root / DOCS_README_REL)
    review_checklist = _read(root / REVIEW_CHECKLIST_REL)
    scripts_readme = _read(root / SCRIPTS_README_REL)
    tests_readme = _read(root / TESTS_README_REL)
    validator = _read(root / VALIDATOR_REL)

    _require_markers("survey", survey, SURVEY_MARKERS, issues)
    _require_markers("policy", policy, POLICY_MARKERS, issues)
    _require_markers("freeze_map", freeze_map, FREEZE_MAP_MARKERS, issues)
    _require_markers("lane_note", lane_note, LANE_NOTE_MARKERS, issues)
    _require_markers("handoff", handoff, HANDOFF_MARKERS, issues)
    _require_markers("readiness", readiness, READINESS_MARKERS, issues)
    _require_markers("docs_readme", docs_readme, DOCS_README_MARKERS, issues)
    _require_markers("review_checklist", review_checklist, REVIEW_CHECKLIST_MARKERS, issues)
    _require_markers("scripts_readme", scripts_readme, SCRIPTS_README_MARKERS, issues)
    _require_markers("tests_readme", tests_readme, TESTS_README_MARKERS, issues)
    _require_markers("validator", validator, VALIDATOR_MARKERS, issues)

    manifest = json.loads(_read(root / POLICY_JSON_REL))
    if manifest.get("lane_key") != "P15-L16":
        issues.append("policy_json:lane_key")
    if manifest.get("roadmap_requirement") != "policy for code that remains in C indefinitely":
        issues.append("policy_json:roadmap_requirement")
    if manifest.get("surveyed_commit") != "current-master-readback-2026-05-14":
        issues.append("policy_json:surveyed_commit")
    if manifest.get("anchors") != EXPECTED_ANCHORS:
        issues.append("policy_json:anchors")

    requirement_ids = [item.get("id") for item in manifest.get("indefinite_c_requirements", [])]
    if requirement_ids != EXPECTED_REQUIREMENT_IDS:
        issues.append("policy_json:indefinite_c_requirements")

    gap_ids = [item.get("id") for item in manifest.get("gaps", [])]
    if gap_ids != EXPECTED_GAP_IDS:
        issues.append("policy_json:gaps")

    supporting = manifest.get("supporting_artifacts", [])
    for rel in (
        FREEZE_MAP_REL,
        REVIEW_CHECKLIST_REL,
        "Documentation/zigux/phase15-architecture-council-review-process.md",
        "Documentation/zigux/phase15-parity-scorecard.md",
        LANE_NOTE_REL,
        BLOCKER_EVIDENCE_REL,
        LANE_ALIGNMENT_REL,
        "zigux/tests/phase15_build.zig",
    ):
        if rel not in supporting:
            issues.append(f"policy_json:supporting_artifacts:{rel}")

    maintenance = manifest.get("maintenance_handoff", {})
    replays = maintenance.get("replay_before_trusting", [])
    for replay in (
        f"zig test {POLICY_ZIG_REL}",
        f"zig test {BLOCKER_EVIDENCE_REL}",
        f"zig test {LANE_ALIGNMENT_REL}",
        "zig build test --build-file zigux/tests/phase15_build.zig",
    ):
        if replay not in replays:
            issues.append(f"policy_json:maintenance_handoff:{replay}")

    return issues


def _seed(root: Path) -> None:
    _write(root / SURVEY_REL, "\n".join(SURVEY_MARKERS) + "\n")
    _write(root / POLICY_REL, "\n".join(POLICY_MARKERS) + "\n")
    _write(root / FREEZE_MAP_REL, "\n".join(FREEZE_MAP_MARKERS) + "\n")
    _write(root / LANE_NOTE_REL, "\n".join(LANE_NOTE_MARKERS) + "\n")
    _write(root / HANDOFF_REL, "\n".join(HANDOFF_MARKERS) + "\n")
    _write(root / READINESS_REL, "\n".join(READINESS_MARKERS) + "\n")
    _write(root / DOCS_README_REL, "\n".join(DOCS_README_MARKERS) + "\n")
    _write(root / REVIEW_CHECKLIST_REL, "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
    _write(root / SCRIPTS_README_REL, "\n".join(SCRIPTS_README_MARKERS) + "\n")
    _write(root / TESTS_README_REL, "\n".join(TESTS_README_MARKERS) + "\n")
    _write(root / VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS) + "\n")
    _write(root / POLICY_ZIG_REL, "// policy zig\n")
    _write(root / BLOCKER_EVIDENCE_REL, "// blocker evidence\n")
    _write(root / LANE_ALIGNMENT_REL, "// lane owner alignment\n")
    _write(
        root / POLICY_JSON_REL,
        json.dumps(
            {
                "lane_key": "P15-L16",
                "roadmap_requirement": "policy for code that remains in C indefinitely",
                "surveyed_commit": "current-master-readback-2026-05-14",
                "anchors": EXPECTED_ANCHORS,
                "supporting_artifacts": [
                    FREEZE_MAP_REL,
                    REVIEW_CHECKLIST_REL,
                    "Documentation/zigux/phase15-architecture-council-review-process.md",
                    "Documentation/zigux/phase15-parity-scorecard.md",
                    LANE_NOTE_REL,
                    BLOCKER_EVIDENCE_REL,
                    LANE_ALIGNMENT_REL,
                    "zigux/tests/phase15_build.zig",
                ],
                "indefinite_c_requirements": [{"id": req_id} for req_id in EXPECTED_REQUIREMENT_IDS],
                "maintenance_handoff": {
                    "replay_before_trusting": [
                        f"zig test {POLICY_ZIG_REL}",
                        f"zig test {BLOCKER_EVIDENCE_REL}",
                        f"zig test {LANE_ALIGNMENT_REL}",
                        "zig build test --build-file zigux/tests/phase15_build.zig",
                    ]
                },
                "gaps": [{"id": gap_id} for gap_id in EXPECTED_GAP_IDS],
            },
            indent=2,
        )
        + "\n",
    )


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase15-indefinite-c-policy-survey-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_indefinite_c_policy_survey_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        path = root / SURVEY_REL
        _write(path, _read(path).replace("phase15-deep-core-status-change-blocker\n", "", 1))
        _assert_only(
            validate(root),
            ["survey:missing:phase15-deep-core-status-change-blocker"],
            "survey_missing_blocker",
        )
        _seed(root)
        case_count += 1

        manifest = json.loads(_read(root / POLICY_JSON_REL))
        manifest["lane_key"] = "P15-L99"
        _write(root / POLICY_JSON_REL, json.dumps(manifest, indent=2) + "\n")
        _assert_only(validate(root), ["policy_json:lane_key"], "manifest_wrong_lane")
        _seed(root)
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace("Documentation/zigux/phase15-indefinite-c-policy.md\n", "", 1))
        _assert_only(
            validate(root),
            ["docs_readme:missing:Documentation/zigux/phase15-indefinite-c-policy.md"],
            "docs_missing_policy",
        )
        _seed(root)
        case_count += 1

        path = root / VALIDATOR_REL
        _write(path, _read(path).replace(f"{LANE_ALIGNMENT_REL}\n", "", 1))
        _assert_only(
            validate(root),
            [f"validator:missing:{LANE_ALIGNMENT_REL}"],
            "validator_missing_lane_alignment",
        )
        _seed(root)
        case_count += 1

    print("PHASE15_INDEFINITE_C_POLICY_SURVEY_SELF_TEST=pass")
    print(f"PHASE15_INDEFINITE_C_POLICY_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 15 indefinite-C policy survey aligned with the landed stay-in-C packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE15_INDEFINITE_C_POLICY_SURVEY=fail")
        print("PHASE15_INDEFINITE_C_POLICY_SURVEY_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE15_INDEFINITE_C_POLICY_SURVEY_ISSUES_END")
        return 1

    print("PHASE15_INDEFINITE_C_POLICY_SURVEY=pass")
    print(f"PHASE15_INDEFINITE_C_POLICY_SURVEY_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE15_INDEFINITE_C_POLICY_SURVEY_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in (SURVEY_MARKERS, POLICY_MARKERS, FREEZE_MAP_MARKERS, LANE_NOTE_MARKERS, HANDOFF_MARKERS, READINESS_MARKERS, DOCS_README_MARKERS, REVIEW_CHECKLIST_MARKERS, SCRIPTS_README_MARKERS, TESTS_README_MARKERS, VALIDATOR_MARKERS))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

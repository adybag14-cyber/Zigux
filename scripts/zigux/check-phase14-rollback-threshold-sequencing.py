#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

FILES = [
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
]

REVIEW_CHECKLIST_MARKER = (
    "if the change touches the shared Phase 14 smoke packet, do the same shared smoke "
    "manifest, release-boundary note, and survey packet still keep the sequencing split "
    "explicit so only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` are treated as "
    "bounded-internal same-phase follow-up lanes while `net/core/skbuff.c` and "
    "`kernel/rcu/tree.c` stay governance-blocked under the Phase 15 freeze packet?"
)

SURVEY_NOTE_MARKER = (
    "the shared smoke packet now also keeps the sequencing split explicit: only the "
    "bounded-internal `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` anchors remain "
    "eligible for same-phase bounded follow-up, while `net/core/skbuff.c` and "
    "`kernel/rcu/tree.c` stay governance-blocked under the Phase 15 freeze packet and must "
    "not be treated as bounded-internal next steps."
)

RELEASE_BOUNDARY_MARKER = (
    "bounded-internal sequencing guard: only `kernel/workqueue.c` and "
    "`kernel/trace/ring_buffer.c` remain eligible for same-phase bounded follow-up inside "
    "the current Phase 14 study packet, while `net/core/skbuff.c` and `kernel/rcu/tree.c` "
    "stay governed by the Phase 15 freeze-in-C packet and are not bounded-internal next-step lanes"
)

SUMMARY_KEYS = [
    "review_checklist_has_rollback_threshold_prompt",
    "review_checklist_has_return_to_blocked_trigger_prompt",
    "review_checklist_has_phase14_bounded_internal_sequencing_prompt",
    "smoke_note_records_rollback_threshold",
    "smoke_note_records_return_to_blocked_triggers",
    "smoke_note_records_bounded_internal_sequencing_split",
    "release_boundary_note_records_bounded_internal_sequencing_split",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_exact_line(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == f"- {marker}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    required_paths = [root / path for path in FILES]
    missing_paths = [str(path) for path in required_paths if not path.exists()]
    for path in missing_paths:
        issues.append(f"missing:{path}")
    if issues:
        return issues

    review_checklist = read(root / "Documentation/zigux/review-checklist.md")
    survey_note = read(root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md")
    release_boundary = read(root / "Documentation/zigux/phase14-release-boundary-survey.md")
    manifest = json.loads(read(root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"))

    if REVIEW_CHECKLIST_MARKER not in review_checklist:
        issues.append("review_checklist:sequencing_prompt")
    if count_exact_line(survey_note, SURVEY_NOTE_MARKER) != 1:
        issues.append("survey_note:sequencing_split_line")
    if count_exact_line(release_boundary, RELEASE_BOUNDARY_MARKER) != 1:
        issues.append("release_boundary:sequencing_guard_line")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        issues.append("manifest:survey_summary")
        return issues

    for key in SUMMARY_KEYS:
        if summary.get(key) is not True:
            issues.append(f"manifest:survey_summary:{key}")

    rollback_threshold = manifest.get("rollback_threshold")
    if not isinstance(rollback_threshold, dict):
        issues.append("manifest:rollback_threshold")
    else:
        triggers = rollback_threshold.get("rollback_triggers")
        if not isinstance(triggers, list) or len(triggers) != 4:
            issues.append("manifest:rollback_threshold:rollback_triggers")
        else:
            for item in triggers:
                if not isinstance(item, str) or item not in survey_note:
                    issues.append(f"survey_note:rollback_trigger:{item}")

    return issues


def run_self_test() -> int:
    fixture_root = ROOT / "_phase14_checker_fixture"
    fixture_root.mkdir(exist_ok=True)
    (fixture_root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (fixture_root / "zigux/tests").mkdir(parents=True, exist_ok=True)

    survey_summary = {key: True for key in SUMMARY_KEYS}
    survey_summary.update(
        {
            "review_checklist_has_fallback_path_prompt": True,
            "smoke_note_records_fallback_path": True,
            "scripts_readme_records_return_to_blocked_triggers": True,
        }
    )
    manifest = {
        "survey_summary": survey_summary,
        "rollback_threshold": {
            "rollback_triggers": [
                "any shared smoke packet edit that drops the named validation gate or rollback owner",
                "missing fallback path or study-only stay-in-C wording in the shared manifest, survey note, review checklist, `Documentation/zigux/README.md`, or `scripts/zigux/README.md`",
                "any anchor-local manifest refresh that changes a quoted surveyed commit or lane key without refreshing the shared smoke packet",
                "loss of the dedicated docs-root smoke checker, the docs-root summary, the focused `phase14-smoke` replay contract, or the validator-backed `make -C zigux phase14-validate` entrypoint from the shared packet",
            ]
        },
    }
    review_checklist = f"# Checklist\n- {REVIEW_CHECKLIST_MARKER}\n"
    survey_note = "\n".join(
        [
            "# Survey",
            f"- {SURVEY_NOTE_MARKER}",
            "- any shared smoke packet edit that drops the named validation gate or rollback owner",
            "- missing fallback path or study-only stay-in-C wording in the shared manifest, survey note, review checklist, `Documentation/zigux/README.md`, or `scripts/zigux/README.md`",
            "- any anchor-local manifest refresh that changes a quoted surveyed commit or lane key without refreshing the shared smoke packet",
            "- loss of the dedicated docs-root smoke checker, the docs-root summary, the focused `phase14-smoke` replay contract, or the validator-backed `make -C zigux phase14-validate` entrypoint from the shared packet",
        ]
    )
    release_boundary = f"# Release\n- {RELEASE_BOUNDARY_MARKER}\n"

    (fixture_root / "Documentation/zigux/review-checklist.md").write_text(review_checklist, encoding="utf-8")
    (fixture_root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md").write_text(survey_note, encoding="utf-8")
    (fixture_root / "Documentation/zigux/phase14-release-boundary-survey.md").write_text(release_boundary, encoding="utf-8")
    (fixture_root / "zigux/tests/phase14_end_to_end_smoke_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    good = validate(fixture_root)

    bad_checklist = fixture_root / "Documentation/zigux/review-checklist.md"
    bad_checklist.write_text("# Checklist\n", encoding="utf-8")
    missing_prompt = validate(fixture_root)
    bad_checklist.write_text(review_checklist, encoding="utf-8")

    bad_survey = fixture_root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
    bad_survey.write_text("# Survey\n", encoding="utf-8")
    missing_survey_line = validate(fixture_root)
    bad_survey.write_text(survey_note, encoding="utf-8")

    bad_release = fixture_root / "Documentation/zigux/phase14-release-boundary-survey.md"
    bad_release.write_text("# Release\n", encoding="utf-8")
    missing_release_line = validate(fixture_root)
    bad_release.write_text(release_boundary, encoding="utf-8")

    bad_manifest = fixture_root / "zigux/tests/phase14_end_to_end_smoke_manifest.json"
    broken_manifest = dict(manifest)
    broken_manifest["survey_summary"] = dict(survey_summary)
    broken_manifest["survey_summary"]["smoke_note_records_bounded_internal_sequencing_split"] = False
    bad_manifest.write_text(json.dumps(broken_manifest, indent=2) + "\n", encoding="utf-8")
    bad_summary_flag = validate(fixture_root)

    broken_manifest = dict(manifest)
    broken_manifest["rollback_threshold"] = {
        "rollback_triggers": manifest["rollback_threshold"]["rollback_triggers"][:3]
    }
    bad_manifest.write_text(json.dumps(broken_manifest, indent=2) + "\n", encoding="utf-8")
    bad_trigger_count = validate(fixture_root)

    broken_manifest = dict(manifest)
    bad_manifest.write_text(json.dumps(broken_manifest, indent=2) + "\n", encoding="utf-8")
    bad_survey.write_text(
        "\n".join(
            [
                "# Survey",
                f"- {SURVEY_NOTE_MARKER}",
                "- any shared smoke packet edit that drops the named validation gate or rollback owner",
            ]
        ),
        encoding="utf-8",
    )
    missing_trigger_text = validate(fixture_root)

    if (
        good
        or not missing_prompt
        or not missing_survey_line
        or not missing_release_line
        or not bad_summary_flag
        or not bad_trigger_count
        or not missing_trigger_text
    ):
        print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=fail")
        return 1

    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass")
    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST_CASE_COUNT=6")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING=fail")
        print("ISSUES_START")
        for issue in issues:
            print(issue)
        print("ISSUES_END")
        return 1

    print("PHASE14_ROLLBACK_THRESHOLD_SEQUENCING=pass")
    print(f"PHASE14_ROLLBACK_THRESHOLD_SUMMARY_KEY_COUNT={len(SUMMARY_KEYS)}")
    print("PHASE14_ROLLBACK_TRIGGER_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

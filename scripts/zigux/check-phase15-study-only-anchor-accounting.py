#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
LANE_SEQ_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")
HANDOFF_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
PARITY_SCORECARD_PATH = Path("Documentation/zigux/phase15-parity-scorecard.md")

STATUS_MARKERS = (
    "PHASE15_STATUS=study_only_accounting_slice_landed",
    "PHASE15_LANE_KEY=P15-L05",
    "PHASE15_SLICE=study-only-anchor-accounting",
    "PHASE15_PROVENANCE_MODE=dated_master_readback",
    "current-master-readback-2026-05-25",
)

ANCHORS = (
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
)

STUDY_ONLY_REQUIRED_MARKERS = (
    "tracked outside the freeze-in-C scorecard and outside blocked status-change rows",
    "keep the two study-only anchors explicit beside the freeze map, the Phase 15 freeze-map governance note, the parity scorecard, the governance-lane sequencing note, the handoff-next-steps survey, the shared-summary gap note, and the landed validator-first maintenance gate",
    "the current Phase 15 parity scorecard still records `study-only anchors tracked outside this scorecard: 2`",
    "the current Phase 15 governance-lane sequencing note keeps the study-only inventory explicitly parked behind the owner packets and the remaining dedicated-build gap",
    "the current Phase 15 handoff-next-steps survey keeps the same two study-only anchors parked beside the existing governance packet",
    "the current Phase 15 shared-summary gap note and landed tests-root governance reminder keep docs-root, checklist, scripts-root, tests-root, and validator-first wording drift framed as truthfulness follow-through rather than study-only status-change evidence",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
)

FREEZE_MAP_REQUIRED_MARKERS = (
    "## Study / Boundary Only",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture",
    "must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

REVIEW_CHECKLIST_REQUIRED_MARKERS = (
    "if a shared reminder surface summarizes the study-only freeze-map anchors",
    "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
)

LANE_SEQ_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows",
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves",
)

HANDOFF_REQUIRED_MARKERS = (
    "keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
)

SHARED_GAP_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "the checklist-specific study-only anchor summary boundary",
)

PARITY_SCORECARD_REQUIRED_MARKERS = (
    "study-only anchors tracked outside this scorecard: `2`",
    "study-only anchors remain outside this scorecard until a lane asks for a status-bucket review",
)

FORBIDDEN_MARKERS = (
    "an Architecture Council approval for any study-only anchor to leave its current posture",
    "a direct Zigux bridge for `kernel/workqueue.c`",
    "a direct Zigux bridge for `kernel/trace/ring_buffer.c`",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ensure_present(source: str, markers: tuple[str, ...], label: str, failures: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            failures.append(f"{label}:missing:{marker}")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required_paths = (
        STUDY_ONLY_PATH,
        FREEZE_MAP_PATH,
        REVIEW_CHECKLIST_PATH,
        LANE_SEQ_PATH,
        HANDOFF_PATH,
        SHARED_GAP_PATH,
        PARITY_SCORECARD_PATH,
    )
    for rel in required_paths:
        if not (root / rel).exists():
            failures.append(f"missing_required_path:{rel}")
    if failures:
        return failures

    study_only = _read(root / STUDY_ONLY_PATH)
    freeze_map = _read(root / FREEZE_MAP_PATH)
    review_checklist = _read(root / REVIEW_CHECKLIST_PATH)
    lane_seq = _read(root / LANE_SEQ_PATH)
    handoff = _read(root / HANDOFF_PATH)
    shared_gap = _read(root / SHARED_GAP_PATH)
    parity_scorecard = _read(root / PARITY_SCORECARD_PATH)

    _ensure_present(study_only, STATUS_MARKERS, "study_only", failures)
    _ensure_present(study_only, ANCHORS, "study_only", failures)
    _ensure_present(study_only, STUDY_ONLY_REQUIRED_MARKERS, "study_only", failures)
    _ensure_present(freeze_map, FREEZE_MAP_REQUIRED_MARKERS, "freeze_map", failures)
    _ensure_present(review_checklist, REVIEW_CHECKLIST_REQUIRED_MARKERS, "review_checklist", failures)
    _ensure_present(lane_seq, LANE_SEQ_REQUIRED_MARKERS, "lane_seq", failures)
    _ensure_present(handoff, HANDOFF_REQUIRED_MARKERS, "handoff", failures)
    _ensure_present(shared_gap, SHARED_GAP_REQUIRED_MARKERS, "shared_gap", failures)
    _ensure_present(parity_scorecard, PARITY_SCORECARD_REQUIRED_MARKERS, "parity_scorecard", failures)

    for marker in FORBIDDEN_MARKERS:
        if marker in study_only:
            failures.append(f"study_only:unexpected:{marker}")

    return failures


def _sample_study_only() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

- `PHASE15_STATUS=study_only_accounting_slice_landed`
- `PHASE15_LANE_KEY=P15-L05`
- `PHASE15_SLICE=study-only-anchor-accounting`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-25`
- scope: keep the two study-only anchors explicit beside the freeze map, the Phase 15 freeze-map governance note, the parity scorecard, the governance-lane sequencing note, the handoff-next-steps survey, the shared-summary gap note, and the landed validator-first maintenance gate

- the current Phase 15 parity scorecard still records `study-only anchors tracked outside this scorecard: 2`
- the current Phase 15 governance-lane sequencing note keeps the study-only inventory explicitly parked behind the owner packets and the remaining dedicated-build gap
- the current Phase 15 handoff-next-steps survey keeps the same two study-only anchors parked beside the existing governance packet
- the current Phase 15 shared-summary gap note and landed tests-root governance reminder keep docs-root, checklist, scripts-root, tests-root, and validator-first wording drift framed as truthfulness follow-through rather than study-only status-change evidence

### `kernel/workqueue.c`
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows

### `kernel/trace/ring_buffer.c`
- current Phase 15 role: tracked outside the freeze-in-C scorecard and outside blocked status-change rows

- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

- shared reminder surfaces that summarize freeze posture
- must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
"""


def _sample_lane_seq() -> str:
    return """# Phase 15 Governance Lane Sequencing

- `Documentation/zigux/phase15-study-only-anchor-accounting.md` owns the explicit two-anchor study-only inventory that stays outside the freeze-in-C scorecard and blocked status-change rows
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves
"""


def _sample_handoff() -> str:
    return """# Phase 15 Handoff Next Steps Survey

- keep the two roadmap study-only anchors parked: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`
- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
"""


def _sample_shared_gap() -> str:
    return """# Phase 15 Shared Summary Gap

- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- the checklist-specific study-only anchor summary boundary
"""


def _sample_parity_scorecard() -> str:
    return """# Phase 15 Parity Scorecard

- study-only anchors tracked outside this scorecard: `2`
- study-only anchors remain outside this scorecard until a lane asks for a status-bucket review
"""


def _seed_repo(root: Path) -> None:
    _write(root / STUDY_ONLY_PATH, _sample_study_only())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / LANE_SEQ_PATH, _sample_lane_seq())
    _write(root / HANDOFF_PATH, _sample_handoff())
    _write(root / SHARED_GAP_PATH, _sample_shared_gap())
    _write(root / PARITY_SCORECARD_PATH, _sample_parity_scorecard())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase15_study_only_accounting_") as tmp_dir:
        root = Path(tmp_dir)

        baseline = root / "baseline"
        _seed_repo(baseline)
        failures = collect_failures(baseline)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        missing_anchor = root / "missing_anchor"
        _seed_repo(missing_anchor)
        _write(
            missing_anchor / STUDY_ONLY_PATH,
            _sample_study_only().replace("### `kernel/trace/ring_buffer.c`\n", "", 1),
        )
        failures = collect_failures(missing_anchor)
        expected = ["study_only:missing:`kernel/trace/ring_buffer.c`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-anchor failure: {failures}")
        case_count += 1

        missing_freeze_route = root / "missing_freeze_route"
        _seed_repo(missing_freeze_route)
        _write(
            missing_freeze_route / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "- must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`\n",
                "",
                1,
            ),
        )
        failures = collect_failures(missing_freeze_route)
        expected = [
            "freeze_map:missing:must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-freeze-route failure: {failures}")
        case_count += 1

        missing_review_prompt = root / "missing_review_prompt"
        _seed_repo(missing_review_prompt)
        _write(
            missing_review_prompt / REVIEW_CHECKLIST_PATH,
            "# Zigux Review Checklist\n\n",
        )
        failures = collect_failures(missing_review_prompt)
        expected = [
            "review_checklist:missing:if a shared reminder surface summarizes the study-only freeze-map anchors",
            "review_checklist:missing:`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
            "review_checklist:missing:`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-review-prompt failure: {failures}")
        case_count += 1

        unexpected_bridge = root / "unexpected_bridge"
        _seed_repo(unexpected_bridge)
        _write(
            unexpected_bridge / STUDY_ONLY_PATH,
            _sample_study_only() + "- a direct Zigux bridge for `kernel/workqueue.c`\n",
        )
        failures = collect_failures(unexpected_bridge)
        expected = ["study_only:unexpected:a direct Zigux bridge for `kernel/workqueue.c`"]
        if failures != expected:
            raise AssertionError(f"unexpected bridge failure: {failures}")
        case_count += 1

    print("PHASE15_STUDY_ONLY_ACCOUNTING_SELF_TEST=pass")
    print(f"PHASE15_STUDY_ONLY_ACCOUNTING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 study-only anchor accounting note stays aligned with the freeze-boundary governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--self-test", action="store_true", help="run synthetic fixture checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("PHASE15_STUDY_ONLY_ACCOUNTING=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

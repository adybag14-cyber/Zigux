#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DOCS_README_PATH = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")

CORE_PHASE15_SURFACES = (
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
)

DOCS_README_MARKERS = CORE_PHASE15_SURFACES + (
    "Phase 15 notes",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-architecture-council-packet.py`",
    "`scripts/zigux/validate-phase15.py`",
    "the current docs-root Phase 15 reminder packet should stay parked on",
    "keep the shared reminder surfaces explicit here too: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
)

REVIEW_CHECKLIST_MARKERS = (
    "if a freeze-map anchor is entering Architecture Council status review or recording a stay-in-C closeout",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "`Documentation/zigux/phase15-indefinite-c-policy.md`",
    "if a shared reminder surface summarizes the study-only freeze-map anchors",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context",
)

FREEZE_MAP_MARKERS = (
    "shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`",
    "must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "shared Phase 15 handoff and gap notes, especially `Documentation/zigux/phase15-handoff-next-steps-survey.md` and `Documentation/zigux/phase15-shared-summary-gap.md`",
    "study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c`",
)

FORBIDDEN_DOCS_README_MARKERS = (
    "still stops at Phase 14 on current `master`",
    "active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _missing(label: str, body: str, markers: tuple[str, ...]) -> list[str]:
    return [f"{label}:missing:{marker}" for marker in markers if marker not in body]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for rel in (DOCS_README_PATH, REVIEW_CHECKLIST_PATH, FREEZE_MAP_PATH):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures

    docs_readme = _read(root / DOCS_README_PATH)
    review_checklist = _read(root / REVIEW_CHECKLIST_PATH)
    freeze_map = _read(root / FREEZE_MAP_PATH)

    failures.extend(_missing("docs_readme", docs_readme, DOCS_README_MARKERS))
    failures.extend(_missing("review_checklist", review_checklist, REVIEW_CHECKLIST_MARKERS))
    failures.extend(_missing("freeze_map", freeze_map, FREEZE_MAP_MARKERS))

    for marker in FORBIDDEN_DOCS_README_MARKERS:
        if marker in docs_readme:
            failures.append(f"docs_readme:forbidden_stale_gap_marker:{marker}")

    for anchor in ("`kernel/workqueue.c`", "`kernel/trace/ring_buffer.c`"):
        if anchor not in docs_readme:
            failures.append(f"docs_readme:missing_study_anchor:{anchor}")
        if anchor not in review_checklist:
            failures.append(f"review_checklist:missing_study_anchor:{anchor}")
        if anchor not in freeze_map:
            failures.append(f"freeze_map:missing_study_anchor:{anchor}")

    return failures


def _sample_docs_readme() -> str:
    surfaces = "\n".join(f"- {surface}" for surface in CORE_PHASE15_SURFACES)
    return f"""# Zigux Documentation

Phase 15 notes
{surfaces}
- `scripts/zigux/check-phase15-docs-readme-alignment.py`
- `scripts/zigux/check-phase15-architecture-council-packet.py`
- `scripts/zigux/validate-phase15.py`

* the current docs-root Phase 15 reminder packet should stay parked on these surfaces.
* if shared reminders mention `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`, keep them study-only.
* keep the shared reminder surfaces explicit here too: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.
"""


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

* if a freeze-map anchor is entering Architecture Council status review or recording a stay-in-C closeout, keep `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-architecture-council-decision-record-template.md`, and `Documentation/zigux/phase15-indefinite-c-policy.md` explicit.
* if a shared reminder surface summarizes the study-only freeze-map anchors, route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context.
"""


def _sample_freeze_map() -> str:
    return """# Zigux Freeze Map

- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`.
- shared Phase 15 handoff and gap notes, especially `Documentation/zigux/phase15-handoff-next-steps-survey.md` and `Documentation/zigux/phase15-shared-summary-gap.md`, must keep landed governance evidence aligned.
- study-only anchor maintenance must stay aligned with `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only.
"""


def _seed(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())
    _write(root / FREEZE_MAP_PATH, _sample_freeze_map())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_triad_") as tmp_dir:
        root = Path(tmp_dir)

        good = root / "good"
        _seed(good)
        failures = collect_failures(good)
        if failures:
            raise AssertionError(f"good fixture should pass: {failures}")
        case_count += 1

        stale_docs = root / "stale_docs"
        _seed(stale_docs)
        _write(
            stale_docs / DOCS_README_PATH,
            _sample_docs_readme()
            + "\nactive shared-summary gap source until a dedicated Phase 15 docs-root reminder lands\n",
        )
        failures = collect_failures(stale_docs)
        expected = [
            "docs_readme:forbidden_stale_gap_marker:active shared-summary gap source until a dedicated Phase 15 docs-root reminder lands"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected stale-docs failures: {failures}")
        case_count += 1

        missing_surface = root / "missing_surface"
        _seed(missing_surface)
        _write(
            missing_surface / DOCS_README_PATH,
            _sample_docs_readme().replace(
                "- `Documentation/zigux/phase15-parity-scorecard.md`\n", "", 1
            ),
        )
        failures = collect_failures(missing_surface)
        expected = [
            "docs_readme:missing:`Documentation/zigux/phase15-parity-scorecard.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-surface failures: {failures}")
        case_count += 1

        checklist_anchor = root / "checklist_anchor"
        _seed(checklist_anchor)
        _write(
            checklist_anchor / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("`kernel/trace/ring_buffer.c`", "trace ring buffer", 1),
        )
        failures = collect_failures(checklist_anchor)
        expected = [
            "review_checklist:missing:`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context",
            "review_checklist:missing_study_anchor:`kernel/trace/ring_buffer.c`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected checklist-anchor failures: {failures}")
        case_count += 1

        freeze_handoff = root / "freeze_handoff"
        _seed(freeze_handoff)
        _write(
            freeze_handoff / FREEZE_MAP_PATH,
            _sample_freeze_map().replace(
                "- shared Phase 15 handoff and gap notes, especially `Documentation/zigux/phase15-handoff-next-steps-survey.md` and `Documentation/zigux/phase15-shared-summary-gap.md`, must keep landed governance evidence aligned.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(freeze_handoff)
        expected = [
            "freeze_map:missing:shared Phase 15 handoff and gap notes, especially `Documentation/zigux/phase15-handoff-next-steps-survey.md` and `Documentation/zigux/phase15-shared-summary-gap.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-handoff failures: {failures}")
        case_count += 1

    print("PHASE15_SHARED_REMINDER_TRIAD_SELF_TEST=pass")
    print(f"PHASE15_SHARED_REMINDER_TRIAD_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Phase 15 docs-root, review-checklist, and freeze-map reminder alignment."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 shared reminder triad check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

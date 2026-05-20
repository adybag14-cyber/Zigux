#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


PLAN_PATH = Path("Documentation/zigux/phase11-bcm2835-wdt-validation-plan.md")
SURVEY_PATH = Path("Documentation/zigux/phase11-bcm2835-wdt-survey.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md")
MANIFEST_PATH = Path("zigux/tests/phase11_bcm2835_wdt_manifest.json")

PLAN_MARKERS = [
    "PHASE11_BCM2835_WDT_VALIDATION_PLAN_STATUS=plan_landed",
    "archival packet identity remains `P11-L08`",
    "drivers/watchdog/bcm2835_wdt.zig",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "zigux/tests/phase11_bcm2835_wdt.zig",
    "zigux/tests/phase11_bcm2835_wdt_survey.zig",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "Documentation/zigux/phase11-bcm2835-wdt-teardown-note.md",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "live platform registration",
    "PM-base plumbing",
    "watchdog-core lifecycle wiring",
    "shared poweroff-handler coordination",
    "hardware-backed execution",
    "phase11-bcm2835-wdt-live-platform-registration",
]

SURVEY_MARKERS = [
    "PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed",
    "explicit validation plan",
]

MATRIX_MARKERS = [
    "PHASE11_BCM2835_WDT_STATUS=survey_gate_truthful",
    "explicit validation plan",
]

BLOCKED_GAP_ID = "phase11-bcm2835-wdt-live-platform-registration"


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    return path.read_text(encoding="utf-8")


def expect_contains(label: str, text: str, marker: str) -> None:
    if marker not in text:
        raise SystemExit(f"{label} missing marker: {marker}")


def validate_root(root: Path) -> None:
    plan = read_text(root, PLAN_PATH)
    survey = read_text(root, SURVEY_PATH)
    matrix = read_text(root, MATRIX_PATH)
    manifest = json.loads(read_text(root, MANIFEST_PATH))

    for marker in PLAN_MARKERS:
        expect_contains("validation plan", plan, marker)
    for marker in SURVEY_MARKERS:
        expect_contains("survey note", survey, marker)
    for marker in MATRIX_MARKERS:
        expect_contains("validation matrix", matrix, marker)

    lane_key = manifest.get("lane_key")
    if lane_key != "P11-L08":
        raise SystemExit(f"manifest lane_key mismatch: expected P11-L08, got {lane_key!r}")

    blocked_gap = None
    for gap in manifest.get("gaps", []):
        if gap.get("id") == BLOCKED_GAP_ID:
            blocked_gap = gap
            break
    if blocked_gap is None:
        raise SystemExit(f"manifest missing blocked gap: {BLOCKED_GAP_ID}")
    if blocked_gap.get("status") != "blocked_on_driver_scaffold":
        raise SystemExit(
            "manifest blocked gap status drifted: "
            f"expected blocked_on_driver_scaffold, got {blocked_gap.get('status')!r}"
        )
    why_now = blocked_gap.get("why_now", "")
    expect_contains("manifest blocked gap", why_now, "explicit hardware-validation plan")
    expect_contains("manifest blocked gap", why_now, "PM base")

    print("PHASE11_BCM2835_VALIDATION_PLAN=pass")
    print(f"PHASE11_BCM2835_VALIDATION_PLAN_REQUIRED_MARKER_COUNT={len(PLAN_MARKERS)}")
    print("PHASE11_BCM2835_VALIDATION_PLAN_BLOCKED_SURFACE_COUNT=5")


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_file(
        root / PLAN_PATH,
        Path(__file__).resolve().parents[2].joinpath(PLAN_PATH).read_text(encoding="utf-8"),
    )
    write_file(
        root / SURVEY_PATH,
        """# Phase 11 BCM2835 Watchdog Survey
## Status
* `PHASE11_BCM2835_WDT_SURVEY_STATUS=survey_gate_landed`
## Next Bounded Step
The next honest same-lane follow-through is no longer another reminder-surface add. Keep future bcm2835 work inside a later driver-local or explicit validation plan step.
""",
    )
    write_file(
        root / MATRIX_PATH,
        """# Phase 11 BCM2835 Watchdog Validation Matrix
## Status
- `PHASE11_BCM2835_WDT_STATUS=survey_gate_truthful`
## Next Blocked Step
The next honest bcm2835-only follow-through is one explicit validation plan for any future platform-registration or PM-base work.
""",
    )
    write_file(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P11-L08",
                "gaps": [
                    {
                        "id": BLOCKED_GAP_ID,
                        "status": "blocked_on_driver_scaffold",
                        "why_now": (
                            "Live platform-driver registration, PM base plumbing, watchdog-core "
                            "lifecycle wiring, and shared poweroff-handler coordination remain "
                            "blocked until the lane carries an explicit hardware-validation plan "
                            "for behavior wider than the current handoff and poweroff summaries."
                        ),
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> None:
    cases = [
        "sample root passes",
        "missing plan status fails",
        "missing lane key fails",
        "missing blocked gap fails",
        "wrong blocked status fails",
        "missing PM base wording fails",
        "missing survey marker fails",
        "missing matrix marker fails",
    ]

    tempdir = Path(tempfile.mkdtemp(prefix="phase11-bcm2835-validation-plan-"))
    try:
        sample_root = tempdir / "sample"
        write_sample_root(sample_root)
        validate_root(sample_root)

        broken_plan = tempdir / "broken-plan"
        shutil.copytree(sample_root, broken_plan)
        write_file((broken_plan / PLAN_PATH), read_text(broken_plan, PLAN_PATH).replace("plan_landed", "missing"))
        expect_failure(broken_plan)

        broken_lane = tempdir / "broken-lane"
        shutil.copytree(sample_root, broken_lane)
        manifest = json.loads(read_text(broken_lane, MANIFEST_PATH))
        manifest["lane_key"] = "P11-L12"
        write_file(broken_lane / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(broken_lane)

        broken_gap = tempdir / "broken-gap"
        shutil.copytree(sample_root, broken_gap)
        manifest = json.loads(read_text(broken_gap, MANIFEST_PATH))
        manifest["gaps"] = []
        write_file(broken_gap / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(broken_gap)

        broken_status = tempdir / "broken-status"
        shutil.copytree(sample_root, broken_status)
        manifest = json.loads(read_text(broken_status, MANIFEST_PATH))
        manifest["gaps"][0]["status"] = "starter_landed"
        write_file(broken_status / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(broken_status)

        broken_pm = tempdir / "broken-pm"
        shutil.copytree(sample_root, broken_pm)
        manifest = json.loads(read_text(broken_pm, MANIFEST_PATH))
        manifest["gaps"][0]["why_now"] = manifest["gaps"][0]["why_now"].replace("PM base", "memory map")
        write_file(broken_pm / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(broken_pm)

        broken_survey = tempdir / "broken-survey"
        shutil.copytree(sample_root, broken_survey)
        write_file(
            broken_survey / SURVEY_PATH,
            read_text(broken_survey, SURVEY_PATH).replace("explicit validation plan", "future note"),
        )
        expect_failure(broken_survey)

        broken_matrix = tempdir / "broken-matrix"
        shutil.copytree(sample_root, broken_matrix)
        write_file(
            broken_matrix / MATRIX_PATH,
            read_text(broken_matrix, MATRIX_PATH).replace("explicit validation plan", "future note"),
        )
        expect_failure(broken_matrix)

        print("PHASE11_BCM2835_VALIDATION_PLAN_SELF_TEST=pass")
        print(f"PHASE11_BCM2835_VALIDATION_PLAN_SELF_TEST_CASE_COUNT={len(cases)}")
    finally:
        shutil.rmtree(tempdir)


def expect_failure(root: Path) -> None:
    try:
        validate_root(root)
    except SystemExit:
        return
    raise SystemExit(f"expected failure for {root}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return
    if args.self_test:
        run_self_test()
        return
    validate_root(args.root)


if __name__ == "__main__":
    main()

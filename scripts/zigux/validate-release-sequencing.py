#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "scripts/zigux/validate-release-sequencing.py",
    "Documentation/zigux/release-sequencing-plan.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
]

DOC_MARKERS = [
    "## Current release sequence",
    "Release train A: foundations already closed",
    "Release train E: release discipline and governance packet",
    "RELEASE_PLAN_FOUNDATION_PHASES=phase1_closed,phase2_closed",
    "RELEASE_PLAN_ACTIVE_RELEASE_PACKET=phase13_release_discipline",
    "RELEASE_PLAN_ACTIVE_SMOKE_PACKET=phase14_stay_in_c_smoke",
    "RELEASE_PLAN_PARKED_GOVERNANCE_PACKET=phase15_maintenance_mode",
    "Refresh this release-sequencing packet only when one of these changes happens:",
]

PHASE_MARKERS = {
    "Documentation/zigux/phase1-closure.md": ["PHASE1_STATUS=closed"],
    "Documentation/zigux/phase2-closure.md": ["PHASE2_STATUS=closed"],
    "Documentation/zigux/phase13-release-notes-survey.md": ["PHASE13_STATUS=active"],
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": ["PHASE14_STATUS=active"],
    "Documentation/zigux/phase15-readiness-gate-survey.md": ["PHASE15_STATUS=readiness_gate_survey_landed"],
    "Documentation/zigux/phase15-handoff-next-steps-survey.md": ["PHASE15_STATUS=handoff_next_steps_survey_landed"],
}


def require_markers(name: str, source: str, markers: list[str], missing: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")


def run(root: Path) -> int:
    missing: list[str] = []
    missing_files = [path for path in FILES if not (root / path).exists()]
    if missing_files:
        print("RELEASE_SEQUENCING_VALIDATION=fail")
        print("MISSING_RELEASE_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_RELEASE_FILES_END")
        return 1

    require_markers(
        "release_doc",
        (root / "Documentation/zigux/release-sequencing-plan.md").read_text(encoding="utf-8"),
        DOC_MARKERS,
        missing,
    )

    for path, markers in PHASE_MARKERS.items():
        require_markers(path, (root / path).read_text(encoding="utf-8"), markers, missing)

    if missing:
        print("RELEASE_SEQUENCING_VALIDATION=fail")
        print("RELEASE_SEQUENCING_MISSING_START")
        for item in missing:
            print(item)
        print("RELEASE_SEQUENCING_MISSING_END")
        return 1

    print("RELEASE_SEQUENCING_VALIDATION=pass")
    print(f"RELEASE_SEQUENCING_REQUIRED_FILE_COUNT={len(FILES)}")
    print(
        "RELEASE_SEQUENCING_REQUIRED_MARKER_COUNT="
        + str(
            len(DOC_MARKERS)
            + sum(len(markers) for markers in PHASE_MARKERS.values())
        )
    )
    print("RELEASE_SEQUENCING_CURRENT_CLOSED_PHASES=phase1,phase2")
    print("RELEASE_SEQUENCING_CURRENT_ACTIVE_PM_PACKET=phase13,phase14,phase15")
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        for rel in FILES:
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if rel == "scripts/zigux/validate-release-sequencing.py":
                target.write_text("# self-presence marker\n", encoding="utf-8")
            elif rel == "Documentation/zigux/release-sequencing-plan.md":
                target.write_text("\n".join(DOC_MARKERS), encoding="utf-8")
            else:
                target.write_text("\n".join(PHASE_MARKERS[rel]), encoding="utf-8")
        code = run(root)
        if code == 0:
            print("RELEASE_SEQUENCING_SELF_TEST=pass")
        return code


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(run_self_test())
    sys.exit(run(ROOT))

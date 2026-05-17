#!/usr/bin/env python3

"""Guard the current Phase 15 readiness-route exactness posture.

This checker keeps one bounded Architecture Council truthfulness note aligned
with the current blocked-route readiness packet on master. It should fail once
the missing route companions land or the parked reminder wording drifts.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE_REL = "Documentation/zigux/phase15-readiness-route-exactness-gap.md"
SURVEY_REL = "Documentation/zigux/phase15-readiness-gate-survey.md"
MANIFEST_REL = "zigux/tests/phase15_readiness_gate_manifest.json"
VALIDATOR_REL = "scripts/zigux/validate-phase15.py"
MAKEFILE_REL = "zigux/Makefile"

EXPECTED_MANIFEST_CHECKERS = [
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
]

NOTE_MARKERS = [
    "current `master` no longer materializes the shared `phase15-validate` route",
    "`zigux/Makefile` and `scripts/zigux/validate-phase15.py` still return missing",
    "`zigux/tests/phase15_readiness_gate_manifest.json` now carries the",
    "four-checker inventory",
    "`Documentation/zigux/phase15-readiness-gate-survey.md` already treats",
    "blocked route vocabulary rather than a directly",
    "replayable shipped route",
    "scripts/zigux/check-phase15-readiness-route-exactness.py",
]

SURVEY_MARKERS = [
    "- `scripts/zigux/validate-phase15.py`",
    "- `zigux/Makefile`",
    "- `make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path",
    "- `make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path",
    "- `make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path",
]


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in (NOTE_REL, SURVEY_REL, MANIFEST_REL):
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    for rel in (VALIDATOR_REL, MAKEFILE_REL):
        if (root / rel).exists():
            issues.append(f"unexpected_present:{rel}")

    note_text = _read(root, NOTE_REL)
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"note:missing:{marker}")

    survey_text = _read(root, SURVEY_REL)
    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            issues.append(f"survey:missing:{marker}")

    manifest = json.loads(_read(root, MANIFEST_REL))
    if manifest.get("phase15_validate_checkers") != EXPECTED_MANIFEST_CHECKERS:
        issues.append(
            "manifest:phase15_validate_checkers no longer matches the blocked-route readiness packet"
        )

    return issues


def _seed(root: Path) -> None:
    _write(
        root,
        NOTE_REL,
        "\n".join(
            [
                "# note",
                "current `master` no longer materializes the shared `phase15-validate` route",
                "`zigux/Makefile` and `scripts/zigux/validate-phase15.py` still return missing",
                "`zigux/tests/phase15_readiness_gate_manifest.json` now carries the",
                "four-checker inventory",
                "`Documentation/zigux/phase15-readiness-gate-survey.md` already treats",
                "blocked route vocabulary rather than a directly",
                "replayable shipped route",
                "scripts/zigux/check-phase15-readiness-route-exactness.py",
                "",
            ]
        ),
    )
    _write(
        root,
        SURVEY_REL,
        "\n".join(
            [
                "# survey",
                "- `scripts/zigux/validate-phase15.py`",
                "- `zigux/Makefile`",
                "- `make -C zigux phase15-validate` remains blocked route vocabulary rather than a directly readable shipped replay path",
                "- `make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path",
                "- `make -C zigux phase15` remains blocked route vocabulary rather than a directly readable shipped replay path",
                "",
            ]
        ),
    )
    _write(
        root,
        MANIFEST_REL,
        json.dumps(
            {"phase15_validate_checkers": EXPECTED_MANIFEST_CHECKERS},
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase15_readiness_route_") as tmp_dir:
        base = Path(tmp_dir)

        root = base / "baseline"
        _seed(root)
        case_count += 1
        baseline = validate(root)
        if baseline:
            raise SystemExit(
                f"phase15-readiness-route-exactness-self-test:baseline:{baseline}"
            )

        root = base / "validator_present"
        _seed(root)
        case_count += 1
        _write(root, VALIDATOR_REL, "# present\n")
        issues = validate(root)
        expected = [f"unexpected_present:{VALIDATOR_REL}"]
        if issues != expected:
            raise SystemExit(
                f"phase15-readiness-route-exactness-self-test:validator-present:{issues}"
            )

        root = base / "makefile_present"
        _seed(root)
        case_count += 1
        _write(root, MAKEFILE_REL, "phase15-validate:\n")
        issues = validate(root)
        expected = [f"unexpected_present:{MAKEFILE_REL}"]
        if issues != expected:
            raise SystemExit(
                f"phase15-readiness-route-exactness-self-test:makefile-present:{issues}"
            )

        root = base / "manifest_mismatch"
        _seed(root)
        case_count += 1
        manifest = json.loads(_read(root, MANIFEST_REL))
        manifest["phase15_validate_checkers"] = EXPECTED_MANIFEST_CHECKERS[:-1]
        _write(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        expected = [
            "manifest:phase15_validate_checkers no longer matches the blocked-route readiness packet"
        ]
        if issues != expected:
            raise SystemExit(
                f"phase15-readiness-route-exactness-self-test:manifest:{issues}"
            )

        root = base / "note_marker_missing"
        _seed(root)
        case_count += 1
        note_text = _read(root, NOTE_REL).replace(
            "replayable shipped route\n",
            "",
            1,
        )
        _write(root, NOTE_REL, note_text)
        issues = validate(root)
        expected = ["note:missing:replayable shipped route"]
        if issues != expected:
            raise SystemExit(
                f"phase15-readiness-route-exactness-self-test:note:{issues}"
            )

        root = base / "survey_marker_missing"
        _seed(root)
        case_count += 1
        survey_text = _read(root, SURVEY_REL).replace(
            "- `make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path\n",
            "",
            1,
        )
        _write(root, SURVEY_REL, survey_text)
        issues = validate(root)
        expected = [
            "survey:missing:- `make -C zigux phase15-test` remains blocked route vocabulary rather than a directly readable shipped replay path"
        ]
        if issues != expected:
            raise SystemExit(
                f"phase15-readiness-route-exactness-self-test:survey:{issues}"
            )

    print("PHASE15_READINESS_ROUTE_EXACTNESS_SELF_TEST=pass")
    print(f"PHASE15_READINESS_ROUTE_EXACTNESS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 15 blocked-route readiness posture."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE15_READINESS_ROUTE_EXACTNESS=fail")
        print("PHASE15_READINESS_ROUTE_EXACTNESS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE15_READINESS_ROUTE_EXACTNESS_ISSUES_END")
        return 1

    print("PHASE15_READINESS_ROUTE_EXACTNESS=pass")
    print("PHASE15_READINESS_ROUTE_EXACTNESS_MODE=blocked_route_posture_matches_note")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

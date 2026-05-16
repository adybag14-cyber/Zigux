#!/usr/bin/env python3

"""Guard the current Phase 15 readiness-route exactness gap.

This checker intentionally models the current mismatch between the shipped
`phase15-validate` route, the validator-side readiness inventory, and the
machine-readable readiness manifest. It should fail once those packets are
repaired so the gap note can be updated or retired.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAKEFILE_REL = "zigux/Makefile"
VALIDATE_REL = "scripts/zigux/validate-phase15.py"
MANIFEST_REL = "zigux/tests/phase15_readiness_gate_manifest.json"
NOTE_REL = "Documentation/zigux/phase15-readiness-route-exactness-gap.md"

MAKE_ROUTE_CHECKERS = [
    "scripts/zigux/check-phase15-docs-readme-alignment.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
]

VALIDATOR_READINESS_CHECKERS = [
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-shared-summary-gap.py",
]

MANIFEST_READINESS_CHECKERS = [
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "scripts/zigux/check-phase15-review-process-handoff.py",
]

NOTE_MARKERS = [
    "Make route: four checkers",
    "validator readiness inventory: three checkers, missing only the docs",
    "readiness manifest: two checkers, missing the docs alignment checker and the",
    "shared-summary gap checker",
    "scripts/zigux/check-phase15-readiness-route-exactness.py",
]


def _read(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _extract_make_route(text: str) -> list[str] | None:
    match = re.search(r"phase15-validate:\n(?P<body>.*?)(?:\nphase15-test:|\Z)", text, re.S)
    if not match:
        return None

    found: list[str] = []
    for checker in MAKE_ROUTE_CHECKERS:
        if f"{checker} --self-test" in match.group("body") and re.search(
            rf"{re.escape(checker)}(?!\s*--self-test)",
            match.group("body"),
        ):
            found.append(checker)
    return found


def _extract_list(text: str, name: str) -> list[str] | None:
    match = re.search(rf"{re.escape(name)}\s*=\s*\[(?P<body>.*?)\]", text, re.S)
    if not match:
        return None
    return re.findall(r'"([^"]+)"', match.group("body"))


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in (MAKEFILE_REL, VALIDATE_REL, MANIFEST_REL, NOTE_REL):
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    note_text = _read(root, NOTE_REL)
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"note:missing:{marker}")

    makefile_text = _read(root, MAKEFILE_REL)
    make_route = _extract_make_route(makefile_text)
    if make_route is None:
        issues.append("makefile:phase15_validate_route_missing")
    elif make_route != MAKE_ROUTE_CHECKERS:
        issues.append(f"makefile:route={make_route}")

    validate_text = _read(root, VALIDATE_REL)
    make_markers = _extract_list(validate_text, "MAKE_MARKERS")
    if make_markers is None:
        issues.append("validate_phase15:make_markers_missing")
    else:
        for checker in MAKE_ROUTE_CHECKERS:
            if checker not in make_markers:
                issues.append(f"validate_phase15:make_markers_missing:{checker}")

    readiness_checkers = _extract_list(validate_text, "READINESS_CHECKERS")
    if readiness_checkers is None:
        issues.append("validate_phase15:readiness_checkers_missing")
    elif readiness_checkers != VALIDATOR_READINESS_CHECKERS:
        issues.append(f"validate_phase15:readiness_checkers={readiness_checkers}")

    manifest = json.loads(_read(root, MANIFEST_REL))
    manifest_checkers = manifest.get("phase15_validate_checkers")
    if manifest_checkers != MANIFEST_READINESS_CHECKERS:
        issues.append(f"readiness_manifest:phase15_validate_checkers={manifest_checkers}")

    return issues


def _seed(root: Path) -> None:
    _write(
        root,
        NOTE_REL,
        "\n".join(
            [
                "# note",
                "Make route: four checkers",
                "validator readiness inventory: three checkers, missing only the docs",
                "readiness manifest: two checkers, missing the docs alignment checker and the",
                "shared-summary gap checker",
                "scripts/zigux/check-phase15-readiness-route-exactness.py",
                "",
            ]
        ),
    )
    _write(
        root,
        MAKEFILE_REL,
        "\n".join(
            [
                "phase15-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-docs-readme-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-docs-readme-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-scripts-readme-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-review-process-handoff.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-shared-summary-gap.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-shared-summary-gap.py",
                "phase15-test:",
                "",
            ]
        ),
    )
    _write(
        root,
        VALIDATE_REL,
        "\n".join(
            [
                "MAKE_MARKERS = [",
                '  "scripts/zigux/check-phase15-docs-readme-alignment.py --self-test",',
                '  "scripts/zigux/check-phase15-docs-readme-alignment.py",',
                '  "scripts/zigux/check-phase15-scripts-readme-alignment.py --self-test",',
                '  "scripts/zigux/check-phase15-scripts-readme-alignment.py",',
                '  "scripts/zigux/check-phase15-review-process-handoff.py --self-test",',
                '  "scripts/zigux/check-phase15-review-process-handoff.py",',
                '  "scripts/zigux/check-phase15-shared-summary-gap.py --self-test",',
                '  "scripts/zigux/check-phase15-shared-summary-gap.py",',
                "]",
                "READINESS_CHECKERS = [",
                '  "scripts/zigux/check-phase15-scripts-readme-alignment.py",',
                '  "scripts/zigux/check-phase15-review-process-handoff.py",',
                '  "scripts/zigux/check-phase15-shared-summary-gap.py",',
                "]",
                "",
            ]
        ),
    )
    _write(
        root,
        MANIFEST_REL,
        json.dumps(
            {
                "phase15_validate_checkers": MANIFEST_READINESS_CHECKERS,
            },
            indent=2,
        )
        + "\n",
    )


def _assert_result(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(
            f"phase15-readiness-route-exactness-self-test:{label}:got={actual}:want={expected}"
        )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase15_readiness_route_") as tmp_dir:
        root = Path(tmp_dir)

        _seed(root)
        case_count += 1
        _assert_result(validate(root), [], "baseline")

        _seed(root)
        case_count += 1
        text = _read(root, VALIDATE_REL).replace(
            '\n'.join(
                [
                    "READINESS_CHECKERS = [",
                    '  "scripts/zigux/check-phase15-scripts-readme-alignment.py",',
                    '  "scripts/zigux/check-phase15-review-process-handoff.py",',
                    '  "scripts/zigux/check-phase15-shared-summary-gap.py",',
                    "]",
                ]
            ),
            '\n'.join(
                [
                    "READINESS_CHECKERS = [",
                    '  "scripts/zigux/check-phase15-docs-readme-alignment.py",',
                    '  "scripts/zigux/check-phase15-scripts-readme-alignment.py",',
                    '  "scripts/zigux/check-phase15-review-process-handoff.py",',
                    '  "scripts/zigux/check-phase15-shared-summary-gap.py",',
                    "]",
                ]
            ),
            1,
        )
        _write(root, VALIDATE_REL, text)
        issues = validate(root)
        if not any(item.startswith("validate_phase15:readiness_checkers=") for item in issues):
            raise SystemExit(
                "phase15-readiness-route-exactness-self-test:validator_repaired_route_drift_not_detected"
            )

        _seed(root)
        case_count += 1
        manifest = json.loads(_read(root, MANIFEST_REL))
        manifest["phase15_validate_checkers"] = MAKE_ROUTE_CHECKERS
        _write(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        issues = validate(root)
        if not any(item.startswith("readiness_manifest:phase15_validate_checkers=") for item in issues):
            raise SystemExit(
                "phase15-readiness-route-exactness-self-test:manifest_repair_not_detected"
            )

        _seed(root)
        case_count += 1
        broken_make = _read(root, MAKEFILE_REL).replace(
            "scripts/zigux/check-phase15-docs-readme-alignment.py --self-test\n"
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase15-docs-readme-alignment.py\n",
            "",
            1,
        )
        _write(root, MAKEFILE_REL, broken_make)
        issues = validate(root)
        if not any(item.startswith("makefile:route=") for item in issues):
            raise SystemExit(
                "phase15-readiness-route-exactness-self-test:make_route_regression_not_detected"
            )

    print("PHASE15_READINESS_ROUTE_EXACTNESS_SELF_TEST=pass")
    print(f"PHASE15_READINESS_ROUTE_EXACTNESS_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 15 readiness-route exactness gap."
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
    print("PHASE15_READINESS_ROUTE_EXACTNESS_MODE=current_gap_matches_note")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

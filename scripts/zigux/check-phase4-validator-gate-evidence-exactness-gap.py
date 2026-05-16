#!/usr/bin/env python3
"""PHASE4_CHECK_PACKET=validator_gate_evidence_exactness_gap

Fail-closed checker for the bounded Phase 4 validator exactness gap note.
This intentionally stays validator-local: it documents and guards the known
prefix-only mismatch without reopening the broader shared gate packet.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

VALIDATOR_PATH = Path("scripts/zigux/validate-phase4.py")
GATE_EVIDENCE_PATH = Path("Documentation/zigux/phase4-gate-evidence.md")
GAP_NOTE_PATH = Path("Documentation/zigux/phase4-validator-gate-evidence-exactness-gap.md")

PREFIX_ONLY_VALIDATOR_MARKERS = [
    '"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",',
    '"PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",',
    '"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",',
    '"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",',
]

FORBIDDEN_EXACT_VALIDATOR_MARKERS = [
    'f"PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}"',
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES_LINE,",
    'f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}"',
    'f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT}"',
]

GATE_EVIDENCE_MARKERS = [
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",
    "shared_validator_reruns_gate_evidence_check_drift",
]

NOTE_MARKERS = [
    "`PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`",
    "`PHASE4_VALIDATOR_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`",
    "`PHASE4_GATE_EVIDENCE_BLOB_SHA=8f604959c5250433c5fca14b20d7ff75341c8d33`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`",
    "`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`",
    "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=`",
    "`shared_validator_reruns_gate_evidence_check_drift`",
    "`scripts/zigux/validate-phase4.py`",
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`scripts/zigux/check-phase4-validator-gate-evidence-exactness-gap.py`",
]


def _read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def check(root: Path) -> list[str]:
    errors: list[str] = []

    for rel in [VALIDATOR_PATH, GATE_EVIDENCE_PATH, GAP_NOTE_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing file: {rel.as_posix()}")
    if errors:
        return errors

    validator = _read_text(root, VALIDATOR_PATH)
    gate_evidence = _read_text(root, GATE_EVIDENCE_PATH)
    gap_note = _read_text(root, GAP_NOTE_PATH)

    for marker in PREFIX_ONLY_VALIDATOR_MARKERS:
        if marker not in validator:
            errors.append(f"missing validator prefix-only marker in {VALIDATOR_PATH.as_posix()}: {marker}")

    for marker in FORBIDDEN_EXACT_VALIDATOR_MARKERS:
        if marker in validator:
            errors.append(
                "validator exactness rewrite appears landed and the gap note must be removed or narrowed: "
                + marker
            )

    for marker in GATE_EVIDENCE_MARKERS:
        if marker not in gate_evidence:
            errors.append(
                f"missing gate-evidence exactness marker in {GATE_EVIDENCE_PATH.as_posix()}: {marker}"
            )

    for marker in NOTE_MARKERS:
        if marker not in gap_note:
            errors.append(f"missing gap-note marker in {GAP_NOTE_PATH.as_posix()}: {marker}")

    return errors


def _write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _validator_fixture() -> str:
    return """#!/usr/bin/env python3
REQUIRED_GATE_EVIDENCE_MARKERS = [
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
    "PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",
    "PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=",
]
"""


def _gate_evidence_fixture() -> str:
    return """# Phase 4 Gate Evidence

- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`
- `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=baseline_round_trip,shared_validator_reruns_gate_evidence_check_drift`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`
- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`
"""


def _gap_note_fixture() -> str:
    return """# Phase 4 Validator Gate-Evidence Exactness Gap

- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP=present`
- `PHASE4_VALIDATOR_BLOB_SHA=694ad85743612aa0a595cd1752dd03c1013603ab`
- `PHASE4_GATE_EVIDENCE_BLOB_SHA=8f604959c5250433c5fca14b20d7ff75341c8d33`

`PHASE4_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`
`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`
`PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_SELF_TEST_CASE_COUNT=34`
`PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=`
`shared_validator_reruns_gate_evidence_check_drift`
`scripts/zigux/validate-phase4.py`
`Documentation/zigux/phase4-gate-evidence.md`
`scripts/zigux/check-phase4-validator-gate-evidence-exactness-gap.py`
"""


def run_self_test() -> int:
    cases = 4
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root, VALIDATOR_PATH, _validator_fixture())
        _write(root, GATE_EVIDENCE_PATH, _gate_evidence_fixture())
        _write(root, GAP_NOTE_PATH, _gap_note_fixture())
        if check(root):
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=fail")
            for error in check(root):
                print(error)
            return 1

        _write(
            root,
            VALIDATOR_PATH,
            _validator_fixture().replace(
                '"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=",\n',
                'f"PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT={PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT}"\n',
            ),
        )
        if not check(root):
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=fail")
            print("expected exact validator marker drift to fail")
            return 1

        _write(root, VALIDATOR_PATH, _validator_fixture())
        _write(
            root,
            GATE_EVIDENCE_PATH,
            _gate_evidence_fixture().replace(
                "- `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=19`\n",
                "",
            ),
        )
        if not check(root):
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=fail")
            print("expected missing gate-evidence marker to fail")
            return 1

        _write(root, GATE_EVIDENCE_PATH, _gate_evidence_fixture())
        _write(
            root,
            GAP_NOTE_PATH,
            _gap_note_fixture().replace(
                "`PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=`\n",
                "",
            ),
        )
        if not check(root):
            print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=fail")
            print("expected missing gap-note marker to fail")
            return 1

    print("PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST=pass")
    print(f"PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GAP_SELF_TEST_CASES={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    errors = check(Path.cwd())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

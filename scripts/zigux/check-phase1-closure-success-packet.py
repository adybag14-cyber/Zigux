#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase1-closure.py")
CLOSURE_NOTE_PATH = Path("Documentation/zigux/phase1-closure.md")

REQUIRED_WORKFLOW_MARKERS = (
    "      - name: Self-test current Phase 1 closure validator\n"
    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "      - name: Check current Phase 1 closure packet\n"
    "        run: python3 scripts/zigux/validate-phase1-closure.py",
)

REQUIRED_VALIDATOR_MARKERS = (
    "def main() -> int:",
    'parser = argparse.ArgumentParser(description=__doc__)',
    "failures = collect_failures(repo_root(args.root))",
    'print("PHASE1_CLOSURE_VALIDATION=pass")',
    'print("PHASE1_CLOSURE_MODE=current-master-safe")',
    "return 0",
)

REQUIRED_CLOSURE_NOTE_MARKERS = (
    "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`",
    "`PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_root(root: Path) -> tuple[str, object]:
    workflow_file = root / WORKFLOW_PATH
    validator_file = root / VALIDATOR_PATH
    closure_note_file = root / CLOSURE_NOTE_PATH

    missing_files = [
        str(path)
        for path in (workflow_file, validator_file, closure_note_file)
        if not path.is_file()
    ]
    if missing_files:
        return ("missing_files", missing_files)

    workflow_text = read_text(workflow_file)
    validator_text = read_text(validator_file)
    closure_note_text = read_text(closure_note_file)

    missing_workflow = [
        marker for marker in REQUIRED_WORKFLOW_MARKERS if marker not in workflow_text
    ]
    if missing_workflow:
        return ("missing_workflow_markers", missing_workflow)

    missing_validator = [
        marker for marker in REQUIRED_VALIDATOR_MARKERS if marker not in validator_text
    ]
    if missing_validator:
        return ("missing_validator_markers", missing_validator)

    missing_closure_note = [
        marker
        for marker in REQUIRED_CLOSURE_NOTE_MARKERS
        if marker not in closure_note_text
    ]
    if missing_closure_note:
        return ("missing_closure_note_markers", missing_closure_note)

    return (
        "pass",
        {
            "workflow_marker_count": len(REQUIRED_WORKFLOW_MARKERS),
            "validator_marker_count": len(REQUIRED_VALIDATOR_MARKERS),
            "closure_note_marker_count": len(REQUIRED_CLOSURE_NOTE_MARKERS),
        },
    )


def write_sample_root(root: Path) -> None:
    (root / WORKFLOW_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / VALIDATOR_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / CLOSURE_NOTE_PATH.parent).mkdir(parents=True, exist_ok=True)

    workflow_text = """name: zigux-bootstrap
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 1 closure validator
        run: python3 scripts/zigux/validate-phase1-closure.py --self-test
      - name: Check current Phase 1 closure packet
        run: python3 scripts/zigux/validate-phase1-closure.py
"""

    validator_text = """#!/usr/bin/env python3
from __future__ import annotations
import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()
    failures = collect_failures(repo_root(args.root))
    if failures:
        return 1
    print("PHASE1_CLOSURE_VALIDATION=pass")
    print("PHASE1_CLOSURE_MODE=current-master-safe")
    return 0
"""

    closure_note_text = """# Phase 1 Closure

- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`
- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`
"""

    (root / WORKFLOW_PATH).write_text(workflow_text, encoding="utf-8")
    (root / VALIDATOR_PATH).write_text(validator_text, encoding="utf-8")
    (root / CLOSURE_NOTE_PATH).write_text(closure_note_text, encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane16-phase1-closure-success-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        kind, payload = validate_root(root)
        assert kind == "pass", (kind, payload)
        assert payload == {
            "workflow_marker_count": len(REQUIRED_WORKFLOW_MARKERS),
            "validator_marker_count": len(REQUIRED_VALIDATOR_MARKERS),
            "closure_note_marker_count": len(REQUIRED_CLOSURE_NOTE_MARKERS),
        }
        case_count += 1

        workflow_text = read_text(root / WORKFLOW_PATH).replace(
            "      - name: Check current Phase 1 closure packet\n"
            "        run: python3 scripts/zigux/validate-phase1-closure.py\n",
            "      - name: Check current Phase 1 closure packet\n"
            "        run: python3 scripts/zigux/check-phase1-bench.py\n",
            1,
        )
        (root / WORKFLOW_PATH).write_text(workflow_text, encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "missing_workflow_markers", (kind, payload)
        assert payload == [
            "      - name: Check current Phase 1 closure packet\n"
            "        run: python3 scripts/zigux/validate-phase1-closure.py"
        ]
        case_count += 1

        write_sample_root(root)
        validator_text = read_text(root / VALIDATOR_PATH).replace(
            '    print("PHASE1_CLOSURE_VALIDATION=pass")\n',
            "",
            1,
        )
        (root / VALIDATOR_PATH).write_text(validator_text, encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "missing_validator_markers", (kind, payload)
        assert payload == ['print("PHASE1_CLOSURE_VALIDATION=pass")']
        case_count += 1

        write_sample_root(root)
        validator_text = read_text(root / VALIDATOR_PATH).replace(
            "current-master-safe",
            "missing_current_master",
            1,
        )
        (root / VALIDATOR_PATH).write_text(validator_text, encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "missing_validator_markers", (kind, payload)
        assert payload == ['print("PHASE1_CLOSURE_MODE=current-master-safe")']
        case_count += 1

        write_sample_root(root)
        closure_note_text = read_text(root / CLOSURE_NOTE_PATH).replace(
            "`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`\n",
            "`PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`\n",
            1,
        )
        (root / CLOSURE_NOTE_PATH).write_text(closure_note_text, encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "missing_closure_note_markers", (kind, payload)
        assert payload == ["`PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`"]
        case_count += 1

        write_sample_root(root)
        (root / CLOSURE_NOTE_PATH).unlink()
        kind, payload = validate_root(root)
        assert kind == "missing_files", (kind, payload)
        assert payload == [str(root / CLOSURE_NOTE_PATH)]
        case_count += 1

    print("PHASE1_CLOSURE_SUCCESS_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_SUCCESS_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shipped Phase 1 closure validator keeps its success packet explicit."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    kind, payload = validate_root(args.root)
    if kind != "pass":
        print("PHASE1_CLOSURE_SUCCESS_PACKET=fail")
        print(f"PHASE1_CLOSURE_SUCCESS_PACKET_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_CLOSURE_SUCCESS_PACKET=pass")
    print("PHASE1_CLOSURE_SUCCESS_PACKET_REQUIRED_FILE_COUNT=3")
    print(
        f"PHASE1_CLOSURE_SUCCESS_PACKET_WORKFLOW_MARKER_COUNT={payload['workflow_marker_count']}"
    )
    print(
        f"PHASE1_CLOSURE_SUCCESS_PACKET_VALIDATOR_MARKER_COUNT={payload['validator_marker_count']}"
    )
    print(
        "PHASE1_CLOSURE_SUCCESS_PACKET_CLOSURE_NOTE_MARKER_COUNT="
        f"{payload['closure_note_marker_count']}"
    )
    print(
        "PHASE1_CLOSURE_SUCCESS_PACKET_REQUIRED_MARKER_COUNT="
        f"{payload['workflow_marker_count'] + payload['validator_marker_count'] + payload['closure_note_marker_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

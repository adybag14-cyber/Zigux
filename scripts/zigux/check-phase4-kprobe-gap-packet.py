#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE_REL = Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md")
MANIFEST_REL = Path("zigux/tests/phase4_kprobe_example_manifest.json")
SURVEY_REL = Path("zigux/tests/phase4_kprobe_example_survey.zig")
FILES = [NOTE_REL, MANIFEST_REL, SURVEY_REL]
NOTE_MARKERS = [
    "PHASE4_KPROBE_STATUS=parked_gap_packet_landed",
    "PHASE4_KPROBE_LANE_KEY=P4-L19",
    "PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c",
    "PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey",
    "PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig",
    "PHASE4_KPROBE_OWNER=Validation and Perf Team",
    "PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team",
    "Current `master` still does not ship `samples/zigux/kprobe_example.zig`.",
    "The same packet also keeps its reversible-delivery evidence string pinned in the paired manifest",
]
MANIFEST_MARKERS = [
    '"lane_key": "P4-L19"',
    '"phase": "Phase 4"',
    '"owner": "Validation and Perf Team"',
    '"rollback_owner": "Validation and Perf Team"',
    '"anchor": "samples/kprobes/kprobe_example.c"',
    '"current_replay": "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m"',
    '"isolated_survey_replay": "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig"',
    '"shared_build_replay": "phase4-kprobe-example-survey-tests"',
    '"phase4_gate_evidence_present": true',
    '"local_lab_replay"',
    'make -C zigux phase4-kprobe-example-survey',
]
SURVEY_MARKERS = [
    'test "phase4 kprobe survey keeps the parked gap packet explicit" {',
    'test "phase4 kprobe survey keeps reversible-delivery evidence explicit" {',
    'test "phase4 kprobe survey keeps the bounded next step explicit" {',
    'make -C zigux phase4-kprobe-example-survey',
    'zig test zigux/tests/phase4_kprobe_example_survey.zig',
    'Validation and Perf Team',
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def collect_missing(text: str, prefix: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        if marker not in text:
            missing.append(f"{prefix}:{marker}")
    return missing


def validate_root(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in FILES:
        if not (root / rel).exists():
            failures.append(f"file:{rel.as_posix()}")
    if failures:
        return failures

    failures.extend(collect_missing(read_text(root, NOTE_REL), "note", NOTE_MARKERS))
    failures.extend(
        collect_missing(read_text(root, MANIFEST_REL), "manifest", MANIFEST_MARKERS)
    )
    failures.extend(collect_missing(read_text(root, SURVEY_REL), "survey", SURVEY_MARKERS))
    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise AssertionError(old)
    return text.replace(old, new, 1)


def write_fixture_tree(root: Path) -> None:
    write_text(root / NOTE_REL, "\n".join(NOTE_MARKERS) + "\n")
    write_text(root / MANIFEST_REL, "\n".join(MANIFEST_MARKERS) + "\n")
    write_text(root / SURVEY_REL, "\n".join(SURVEY_MARKERS) + "\n")


def expect_failure(
    root: Path,
    description: str,
    *,
    exact_failure: str,
) -> bool:
    failures = validate_root(root)
    if exact_failure not in failures:
        print("PHASE4_KPROBE_GAP_PACKET_SELF_TEST=fail")
        print(f"expected {description} failure: {exact_failure}")
        print("\n".join(failures))
        return False
    return True


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_kprobe_gap_packet_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)
        failures = validate_root(root)
        if failures:
            print("PHASE4_KPROBE_GAP_PACKET_SELF_TEST=fail")
            print("\n".join(failures))
            return 1
        case_count += 1

        note_path = root / NOTE_REL
        original_note = read_text(root, NOTE_REL)
        note_path.write_text(
            replace_once(
                original_note,
                "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
                "PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux broken-phase4-kprobe-example-survey",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "note local replay drift",
            exact_failure="note:PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey",
        ):
            return 1
        case_count += 1
        note_path.write_text(original_note, encoding="utf-8")

        manifest_path = root / MANIFEST_REL
        original_manifest = read_text(root, MANIFEST_REL)
        manifest_path.write_text(
            replace_once(original_manifest, '"local_lab_replay"', '"local_replay"'),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "manifest local lab replay drift",
            exact_failure='manifest:"local_lab_replay"',
        ):
            return 1
        case_count += 1
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_path = root / SURVEY_REL
        original_survey = read_text(root, SURVEY_REL)
        survey_path.write_text(
            replace_once(
                original_survey,
                'test "phase4 kprobe survey keeps the bounded next step explicit" {',
                'test "phase4 kprobe survey drifted next step" {',
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "survey next-step drift",
            exact_failure='survey:test "phase4 kprobe survey keeps the bounded next step explicit" {',
        ):
            return 1
        case_count += 1

    print("PHASE4_KPROBE_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE4_KPROBE_GAP_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 4 kprobe parked-gap packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in synthetic drift tests in a temporary workspace.",
    )
    parser.add_argument(
        "--root",
        default=str(ROOT),
        help="Repository root to validate. Defaults to the checker's inferred repo root.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(Path(args.root))
    if failures:
        print("PHASE4_KPROBE_GAP_PACKET=fail")
        print("MISSING_PHASE4_KPROBE_GAP_PACKET_MARKERS_START")
        for failure in failures:
            print(failure)
        print("MISSING_PHASE4_KPROBE_GAP_PACKET_MARKERS_END")
        return 1

    print("PHASE4_KPROBE_GAP_PACKET=pass")
    print(f"PHASE4_KPROBE_GAP_PACKET_FILE_COUNT={len(FILES)}")
    print(
        "PHASE4_KPROBE_GAP_PACKET_MARKER_COUNT="
        f"{len(NOTE_MARKERS) + len(MANIFEST_MARKERS) + len(SURVEY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

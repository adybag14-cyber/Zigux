#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
NOTE_PATH = Path("Documentation/zigux/phase4-kprobe-sample-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase4_kprobe_sample_manifest.json")

EXPECTED_MANIFEST = {
    "lane_key": "P4-L20",
    "phase": "Phase 4",
    "survey_scope": "matrix_only_kprobe_sample_gap",
    "c_anchor_path": "samples/kprobes/kprobe_example.c",
    "zig_target_path": "samples/zigux/kprobe_example.zig",
    "zig_target_present": False,
    "current_replay_command": "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "survey_owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
    "threshold_posture": "reviewability_only_no_perf_threshold",
    "next_bounded_step": "land one bounded manifest-backed or starter-backed follow-up that keeps the same anchor, replay command, and rollback ownership explicit if the Zig sample lands or this matrix row changes",
}

REQUIRED_NOTE_LINES = [
    "- `PHASE4_KPROBE_SURVEY_SCOPE=matrix_only_kprobe_sample_gap`",
    "- `PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c`",
    "- `PHASE4_KPROBE_ZIG_TARGET=samples/zigux/kprobe_example.zig`",
    "- `PHASE4_KPROBE_ZIG_STARTER_PRESENT=false`",
    "- `PHASE4_KPROBE_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`",
    "- `PHASE4_KPROBE_SURVEY_OWNER=Validation and Perf Team`",
    "- `PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team`",
    "- `PHASE4_KPROBE_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold`",
]

REQUIRED_NOTE_MARKERS = [
    "## Exact Survey",
    "## Next Step",
    "current `master` still ships `samples/kprobes/kprobe_example.c` and does not ship `samples/zigux/kprobe_example.zig`",
    "this packet keeps the current C anchor, current replay command, survey owner, rollback owner, and no-threshold posture reviewable without claiming a shipped Zig starter",
    "no hard timing threshold is approved for this matrix-only sample gap while the Zig starter remains absent",
]


def _read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def validate_root(root: Path) -> list[str]:
    failures: list[str] = []
    note_file = root / NOTE_PATH
    manifest_file = root / MANIFEST_PATH
    c_anchor = root / EXPECTED_MANIFEST["c_anchor_path"]
    zig_target = root / EXPECTED_MANIFEST["zig_target_path"]

    if not note_file.exists():
        return [f"missing_file:{NOTE_PATH}"]
    if not manifest_file.exists():
        return [f"missing_file:{MANIFEST_PATH}"]
    if not c_anchor.exists():
        failures.append(f"missing_c_anchor:{EXPECTED_MANIFEST['c_anchor_path']}")

    try:
        manifest = json.loads(_read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        return [f"invalid_manifest_json:{exc.msg}"]

    for key, expected in EXPECTED_MANIFEST.items():
        actual = manifest.get(key)
        if actual != expected:
            failures.append(f"manifest:{key}:{actual!r}:{expected!r}")

    if manifest.get("zig_target_present") != zig_target.exists():
        failures.append(
            "manifest:zig_target_present_vs_repo:"
            f"{manifest.get('zig_target_present')!r}:{zig_target.exists()!r}"
        )

    note_text = _read_text(root, NOTE_PATH)
    for line in REQUIRED_NOTE_LINES:
        count = note_text.count(line)
        if count != 1:
            failures.append(f"note_line_exact_once:{line}:{count}")
    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            failures.append(f"note_marker:{marker}")

    return failures


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _fixture_note() -> str:
    return """# Phase 4 Kprobe Sample Survey

This note records the bounded matrix-only survey for the still-absent Phase 4 `kprobe_example` Zig starter.

## Status
- `PHASE4_KPROBE_SURVEY_SCOPE=matrix_only_kprobe_sample_gap`
- `PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c`
- `PHASE4_KPROBE_ZIG_TARGET=samples/zigux/kprobe_example.zig`
- `PHASE4_KPROBE_ZIG_STARTER_PRESENT=false`
- `PHASE4_KPROBE_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `PHASE4_KPROBE_SURVEY_OWNER=Validation and Perf Team`
- `PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_KPROBE_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold`

## Exact Survey
- current `master` still ships `samples/kprobes/kprobe_example.c` and does not ship `samples/zigux/kprobe_example.zig`
- this packet keeps the current C anchor, current replay command, survey owner, rollback owner, and no-threshold posture reviewable without claiming a shipped Zig starter
- no hard timing threshold is approved for this matrix-only sample gap while the Zig starter remains absent

## Next Step
- land one bounded manifest-backed or starter-backed follow-up that keeps the same anchor, replay command, and rollback ownership explicit if the Zig sample lands or this matrix row changes
"""


def _fixture_manifest() -> str:
    return json.dumps(EXPECTED_MANIFEST, indent=2) + "\n"


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_kprobe_survey_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / NOTE_PATH, _fixture_note())
        _write(root / MANIFEST_PATH, _fixture_manifest())
        _write(root / EXPECTED_MANIFEST["c_anchor_path"], "// fixture c anchor\n")

        assert validate_root(root) == []

        _write(
            root / NOTE_PATH,
            _fixture_note().replace(
                "- `PHASE4_KPROBE_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`\n",
                "",
                1,
            ),
        )
        assert validate_root(root) == [
            "note_line_exact_once:- `PHASE4_KPROBE_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`:0"
        ]

        _write(root / NOTE_PATH, _fixture_note())
        mutated = EXPECTED_MANIFEST | {"zig_target_present": True}
        _write(root / MANIFEST_PATH, json.dumps(mutated, indent=2) + "\n")
        assert validate_root(root) == [
            "manifest:zig_target_present:True:False",
            "manifest:zig_target_present_vs_repo:True:False",
        ]

        _write(root / MANIFEST_PATH, _fixture_manifest())
        _write(root / EXPECTED_MANIFEST["zig_target_path"], "// fixture zig starter\n")
        assert validate_root(root) == [
            "manifest:zig_target_present_vs_repo:False:True"
        ]

    print("PHASE4_KPROBE_SAMPLE_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 4 kprobe sample-gap survey packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated synthetic coverage for the kprobe sample survey checker.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_KPROBE_SAMPLE_SURVEY=fail")
        print("PHASE4_KPROBE_SAMPLE_SURVEY_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE4_KPROBE_SAMPLE_SURVEY_FAILURES_END")
        return 1

    print("PHASE4_KPROBE_SAMPLE_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

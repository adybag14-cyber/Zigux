#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTE_PATH = Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase4_test_fsmount_manifest.json")
SURVEY_PATH = Path("zigux/tests/phase4_test_fsmount_survey.zig")
BUILD_PATH = Path("zigux/tests/phase4_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
MATRIX_PATH = Path("Documentation/zigux/phase4-validation-matrix.md")

EXPECTED_MANIFEST_FIELDS = {
    "lane_key": "validation-perf",
    "phase": "Phase 4",
    "anchor_path": "samples/vfs/test-fsmount.c",
    "sample_path": "samples/zigux/test_fsmount.zig",
    "sample_present": False,
    "current_replay": "make M=samples/vfs",
    "survey_note": "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "survey_owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
    "shared_gate_evidence_packet_present": False,
    "validation_entrypoint": "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
}

NOTE_MARKERS = [
    "PHASE4_TEST_FSMOUNT_STATUS=parked_gap_survey",
    "PHASE4_LANE_KEY=validation-perf",
    "PHASE4_ANCHOR_PATH=samples/vfs/test-fsmount.c",
    "PHASE4_SAMPLE_PATH=samples/zigux/test_fsmount.zig",
    "PHASE4_SAMPLE_PRESENT=false",
    "PHASE4_CURRENT_REPLAY=make M=samples/vfs",
    "PHASE4_SURVEY_OWNER=Validation and Perf Team",
    "PHASE4_ROLLBACK_OWNER=Validation and Perf Team",
    "PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "`samples/zigux/test_fsmount.zig` is still absent",
    "shared validator route already rereads this parked packet through `scripts/zigux/check-phase4-gate-evidence.py`",
    "claiming a shipped Zig starter",
    "claiming that the shared Phase 4 exact-readback gate already carries this packet",
    "claiming approved hard perf thresholds for the test_fsmount anchor",
]

BUILD_MARKERS = [
    'root_source_file = b.path("phase4_test_fsmount_survey.zig")',
    'name = "phase4-test-fsmount-survey-tests"',
    '"phase4-test-fsmount-survey"',
    "Run the dedicated Phase 4 test_fsmount gap survey without promoting a shipped Zig starter",
]

MAKEFILE_MARKERS = [
    "PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4",
    "phase4-test-fsmount-survey:",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
]

MATRIX_MARKERS = [
    "Documentation/zigux/phase4-test-fsmount-gap-survey.md",
    "zigux/tests/phase4_test_fsmount_manifest.json",
    "zigux/tests/phase4_test_fsmount_survey.zig",
    "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
]


def _read(root: Path, path: Path) -> str:
    return (root / path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for path in [NOTE_PATH, MANIFEST_PATH, SURVEY_PATH, BUILD_PATH, MAKEFILE_PATH, MATRIX_PATH]:
        if not (root / path).exists():
            problems.append(f"file:{path}")
    if problems:
        return problems

    manifest = json.loads(_read(root, MANIFEST_PATH))
    for field, expected in EXPECTED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            problems.append(f"manifest:{field}:{actual}:{expected}")

    review_prompts = manifest.get("review_prompts")
    if not isinstance(review_prompts, list) or len(review_prompts) != 4:
        problems.append("manifest:review_prompts:length")
    non_goals = manifest.get("non_goals")
    if not isinstance(non_goals, list) or len(non_goals) != 3:
        problems.append("manifest:non_goals:length")

    note = _read(root, NOTE_PATH)
    for marker in NOTE_MARKERS:
        if marker not in note:
            problems.append(f"note:{marker}")
    anchor_blob_sha = manifest.get("anchor_blob_sha")
    if not isinstance(anchor_blob_sha, str) or len(anchor_blob_sha) != 40:
        problems.append("manifest:anchor_blob_sha")
    elif anchor_blob_sha not in note:
        problems.append("note:anchor_blob_sha")
    if EXPECTED_MANIFEST_FIELDS["validation_entrypoint"] not in note:
        problems.append("note:validation_entrypoint")

    build = _read(root, BUILD_PATH)
    for marker in BUILD_MARKERS:
        if marker not in build:
            problems.append(f"build:{marker}")
    if "test_step.dependOn(&run_test_fsmount_survey_tests.step);" in build:
        problems.append("build:shared_test_step_should_not_depend_on_test_fsmount")

    makefile = _read(root, MAKEFILE_PATH)
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            problems.append(f"makefile:{marker}")

    matrix = _read(root, MATRIX_PATH)
    for marker in MATRIX_MARKERS:
        if marker not in matrix:
            problems.append(f"matrix:{marker}")

    return problems


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build_fixture_tree(root: Path) -> None:
    _write(
        root / MANIFEST_PATH,
        json.dumps(
            {
                **EXPECTED_MANIFEST_FIELDS,
                "anchor_blob_sha": "50f47b72e85fbc8dd52dedad96ee96e6379da5b8",
                "review_prompts": [
                    "the survey keeps the Linux anchor path and blob sha explicit while the Zig starter stays absent",
                    "the packet keeps the live VFS replay command explicit without implying a shipped Zig sample",
                    "the owner and rollback owner remain Validation and Perf Team while the packet stays adjacent to the shared Phase 4 validator-first route",
                    "the packet stays outside the shared gate-evidence target set while the shared validator still rereads it through the dedicated exact-readback checker",
                ],
                "non_goals": [
                    "shipped test_fsmount Zig starter",
                    "shared gate-evidence promotion",
                    "approved fsmount perf threshold",
                ],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root / NOTE_PATH,
        "\n".join(
            [
                "# Phase 4 Test Fsmount Gap Survey",
                *[f"- `{marker}`" for marker in NOTE_MARKERS[:9]],
                "- `PHASE4_ANCHOR_BLOB_SHA=50f47b72e85fbc8dd52dedad96ee96e6379da5b8`",
                "- `PHASE4_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
                "",
                *NOTE_MARKERS[9:],
                "zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
                "",
            ]
        ),
    )
    _write(root / SURVEY_PATH, "// survey fixture\n")
    _write(root / BUILD_PATH, "\n".join(BUILD_MARKERS + [""]))
    _write(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS + [""]))
    _write(root / MATRIX_PATH, "\n".join(MATRIX_MARKERS + [""]))


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_test_fsmount_gap_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)
        assert validate(root) == []

        bad = root / "bad"
        build_fixture_tree(bad)
        (bad / MAKEFILE_PATH).write_text("phase4-test-fsmount-survey:\n", encoding="utf-8")
        assert validate(bad) == [
            "makefile:PHONY += phase4-validate phase4-artifact-diff-contract phase4-test phase4-runtime-atomic64-diff phase4-runtime-atomic64-diff-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4-bitmap-diff-survey phase4-bitmap-live-helper-replay phase4-test-fsmount-survey phase4-kprobe-example-survey phase4",
            "makefile:zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig",
        ]

        bad2 = root / "bad2"
        build_fixture_tree(bad2)
        manifest = json.loads((bad2 / MANIFEST_PATH).read_text(encoding="utf-8"))
        manifest["shared_gate_evidence_packet_present"] = True
        _write(bad2 / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        assert validate(bad2) == [
            "manifest:shared_gate_evidence_packet_present:True:False"
        ]

    print("PHASE4_TEST_FSMOUNT_GAP_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the parked Phase 4 test_fsmount gap packet and its local replay route."
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = validate(ROOT)
    if problems:
        print("PHASE4_TEST_FSMOUNT_GAP=fail")
        print("PHASE4_TEST_FSMOUNT_GAP_PROBLEMS_START")
        for item in problems:
            print(item)
        print("PHASE4_TEST_FSMOUNT_GAP_PROBLEMS_END")
        return 1

    print("PHASE4_TEST_FSMOUNT_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

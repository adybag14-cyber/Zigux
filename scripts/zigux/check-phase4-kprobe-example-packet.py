#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_build.zig",
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "samples/kprobes/Makefile",
    "samples/kprobes/kprobe_example.c",
]

MANIFEST_EXPECTATIONS = {
    "lane_key": "P4-L19",
    "phase": "Phase 4",
    "owner": "Validation and Perf Team",
    "rollback_owner": "Validation and Perf Team",
    "anchor": "samples/kprobes/kprobe_example.c",
    "current_replay": "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "isolated_survey_replay": "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
    "shared_build_replay": "phase4-kprobe-example-survey-tests",
    "threshold_posture": "c_anchor_only_until_kprobe_example_starter_lands",
}

MANIFEST_SURVEY_SUMMARY_EXPECTATIONS = {
    "kprobe_makefile_replay_present": True,
    "kprobe_anchor_symbol_present": True,
    "zig_sample_present": False,
    "phase4_build_present": True,
    "phase4_validation_matrix_present": True,
    "phase4_gate_evidence_present": True,
}

MANIFEST_REQUIRED_GAPS = {
    "phase4-kprobe-example-survey-manifest": ("starter_landed", "zigux/tests/phase4_kprobe_example_manifest.json"),
    "phase4-kprobe-example-survey-gate": ("starter_landed", "zigux/tests/phase4_kprobe_example_survey.zig"),
    "phase4-kprobe-example-c-anchor-replay": ("starter_landed", "samples/kprobes/kprobe_example.c"),
    "phase4-kprobe-example-shared-validator-promotion": ("ready_next", "scripts/zigux/validate-phase4.py"),
    "phase4-kprobe-example-zig-sample": ("ready_next", "samples/zigux/kprobe_example.zig"),
}

SURVEY_MARKERS = [
    'const current_surveyed_commit = "',
    "phase4_kprobe_example_manifest.json",
    "samples/kprobes/kprobe_example.c",
    "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "phase4-kprobe-example-survey-tests",
    "phase4-kprobe-example-survey",
    "samples/zigux/kprobe_example.zig",
    "shared validator still does not fail closed on the kprobe survey packet itself",
]

BUILD_MARKERS = [
    "phase4_kprobe_example_survey.zig",
    "phase4-kprobe-example-survey-tests",
    '"phase4-kprobe-example-survey"',
    "Run the Phase 4 kprobe example survey gate without claiming a landed Zig sample",
]

MATRIX_MARKERS = [
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "phase4-kprobe-example-survey-tests",
    "zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig",
    "make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m",
    "samples/zigux/kprobe_example.zig",
    "c_anchor_only_until_kprobe_example_starter_lands",
]

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase4-validation-matrix.md",
    "Documentation/zigux/phase4-gate-evidence.md",
    "direct `zig build phase4-kprobe-example-survey --build-file zigux/tests/phase4_build.zig`",
    "phase4-kprobe-example-survey-tests",
    "still-absent `samples/zigux/kprobe_example.zig` sample explicitly survey-only",
]

SCRIPTS_README_MARKERS = [
    "check-phase4-kprobe-example-packet.py --self-test",
    "check-phase4-kprobe-example-packet.py",
    "phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
]

TESTS_README_MARKERS = [
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "make -C zigux phase4-kprobe-example-survey",
    "phase4-kprobe-example-survey-tests",
    "c_anchor_only_until_kprobe_example_starter_lands",
]

GATE_EVIDENCE_MARKERS = [
    "PHASE4_KPROBE_EXAMPLE_MANIFEST_BLOB_SHA=",
    "PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA=",
    "phase4-kprobe-example-survey-tests",
    "zigux/tests/phase4_kprobe_example_survey.zig",
    "zigux/tests/phase4_kprobe_example_manifest.json",
    "shared validator still does not fail closed on the kprobe survey packet itself",
]

ANCHOR_MARKERS = [
    ("makefile", "obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o"),
    ("anchor", 'static char symbol[KSYM_NAME_LEN] = "kernel_clone";'),
]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def collect_text_misses(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_manifest_misses(manifest: dict[str, object]) -> list[str]:
    missing: list[str] = []

    for key, expected_value in MANIFEST_EXPECTATIONS.items():
        if manifest.get(key) != expected_value:
            missing.append(
                f"manifest:{key}:expected={expected_value}:actual={manifest.get(key)}"
            )

    roadmap_destinations = manifest.get("roadmap_destinations")
    if roadmap_destinations != ["samples/zigux/kprobe_example.zig"]:
        missing.append(
            "manifest:roadmap_destinations:expected=['samples/zigux/kprobe_example.zig']"
        )

    survey_summary = manifest.get("survey_summary")
    if not isinstance(survey_summary, dict):
        missing.append("manifest:survey_summary:missing")
    else:
        for key, expected_value in MANIFEST_SURVEY_SUMMARY_EXPECTATIONS.items():
            if survey_summary.get(key) != expected_value:
                missing.append(
                    f"manifest:survey_summary:{key}:expected={expected_value}:actual={survey_summary.get(key)}"
                )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("manifest:gaps:missing")
        return missing

    gap_index = {
        gap.get("id"): gap
        for gap in gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id, (expected_status, expected_destination) in MANIFEST_REQUIRED_GAPS.items():
        gap = gap_index.get(gap_id)
        if gap is None:
            missing.append(f"manifest:gap_missing:{gap_id}")
            continue
        if gap.get("status") != expected_status:
            missing.append(
                f"manifest:gap_status:{gap_id}:expected={expected_status}:actual={gap.get('status')}"
            )
        if gap.get("zigux_destination") != expected_destination:
            missing.append(
                f"manifest:gap_destination:{gap_id}:expected={expected_destination}:actual={gap.get('zigux_destination')}"
            )

    return missing


def collect_missing(
    *,
    present_files: set[str],
    manifest: dict[str, object],
    survey_text: str,
    build_text: str,
    matrix_text: str,
    docs_root_text: str,
    scripts_readme_text: str,
    tests_readme_text: str,
    gate_evidence_text: str,
    kprobe_makefile_text: str,
    kprobe_anchor_text: str,
) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_manifest_misses(manifest))
    missing.extend(collect_text_misses(survey_text, SURVEY_MARKERS, "survey"))
    missing.extend(collect_text_misses(build_text, BUILD_MARKERS, "build"))
    missing.extend(collect_text_misses(matrix_text, MATRIX_MARKERS, "matrix"))
    missing.extend(collect_text_misses(docs_root_text, DOCS_ROOT_MARKERS, "docs_root"))
    missing.extend(
        collect_text_misses(scripts_readme_text, SCRIPTS_README_MARKERS, "scripts_readme")
    )
    missing.extend(
        collect_text_misses(tests_readme_text, TESTS_README_MARKERS, "tests_readme")
    )
    missing.extend(
        collect_text_misses(gate_evidence_text, GATE_EVIDENCE_MARKERS, "gate_evidence")
    )
    for prefix, marker in ANCHOR_MARKERS:
        target_text = kprobe_makefile_text if prefix == "makefile" else kprobe_anchor_text
        if marker not in target_text:
            missing.append(f"{prefix}:{marker}")
    return missing


def build_live_inputs() -> dict[str, object]:
    return {
        "present_files": {path for path in REQUIRED_FILES if (ROOT / path).exists()},
        "manifest": json.loads(read_text("zigux/tests/phase4_kprobe_example_manifest.json")),
        "survey_text": read_text("zigux/tests/phase4_kprobe_example_survey.zig"),
        "build_text": read_text("zigux/tests/phase4_build.zig"),
        "matrix_text": read_text("Documentation/zigux/phase4-validation-matrix.md"),
        "docs_root_text": read_text("Documentation/zigux/README.md"),
        "scripts_readme_text": read_text("scripts/zigux/README.md"),
        "tests_readme_text": read_text("zigux/tests/README.md"),
        "gate_evidence_text": read_text("Documentation/zigux/phase4-gate-evidence.md"),
        "kprobe_makefile_text": read_text("samples/kprobes/Makefile"),
        "kprobe_anchor_text": read_text("samples/kprobes/kprobe_example.c"),
    }


def expect_contains(label: str, missing: list[str], expected_item: str) -> None:
    if expected_item not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase4-kprobe-packet-self-test:{label}:expected_missing:{expected_item}:actual:{actual}"
        )


def run_self_test() -> int:
    base_manifest = {
        **MANIFEST_EXPECTATIONS,
        "surveyed_commit": "3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3",
        "roadmap_destinations": ["samples/zigux/kprobe_example.zig"],
        "survey_summary": dict(MANIFEST_SURVEY_SUMMARY_EXPECTATIONS),
        "gaps": [
            {
                "id": gap_id,
                "status": status,
                "kind": "synthetic",
                "zigux_destination": destination,
                "why_now": "synthetic fixture",
            }
            for gap_id, (status, destination) in MANIFEST_REQUIRED_GAPS.items()
        ],
    }
    base_inputs = {
        "present_files": set(REQUIRED_FILES),
        "manifest": base_manifest,
        "survey_text": "\n".join(SURVEY_MARKERS) + "\n",
        "build_text": "\n".join(BUILD_MARKERS) + "\n",
        "matrix_text": "\n".join(MATRIX_MARKERS) + "\n",
        "docs_root_text": "\n".join(DOCS_ROOT_MARKERS) + "\n",
        "scripts_readme_text": "\n".join(SCRIPTS_README_MARKERS) + "\n",
        "tests_readme_text": "\n".join(TESTS_README_MARKERS) + "\n",
        "gate_evidence_text": "\n".join(GATE_EVIDENCE_MARKERS) + "\n",
        "kprobe_makefile_text": ANCHOR_MARKERS[0][1] + "\n",
        "kprobe_anchor_text": ANCHOR_MARKERS[1][1] + "\n",
    }

    missing = collect_missing(**base_inputs)
    if missing:
        raise SystemExit(
            "phase4-kprobe-packet-self-test:unexpected_failures:" + ",".join(missing)
        )

    missing = collect_missing(
        **{**base_inputs, "present_files": set(REQUIRED_FILES[1:])}
    )
    expect_contains(
        "missing_file_detection",
        missing,
        "missing_file:zigux/tests/phase4_kprobe_example_manifest.json",
    )

    broken_manifest = json.loads(json.dumps(base_manifest))
    broken_manifest["threshold_posture"] = "wrong"
    missing = collect_missing(**{**base_inputs, "manifest": broken_manifest})
    expect_contains(
        "manifest_field_detection",
        missing,
        "manifest:threshold_posture:expected=c_anchor_only_until_kprobe_example_starter_lands:actual=wrong",
    )

    broken_manifest = json.loads(json.dumps(base_manifest))
    broken_manifest["survey_summary"]["phase4_gate_evidence_present"] = False
    missing = collect_missing(**{**base_inputs, "manifest": broken_manifest})
    expect_contains(
        "manifest_summary_detection",
        missing,
        "manifest:survey_summary:phase4_gate_evidence_present:expected=True:actual=False",
    )

    broken_manifest = json.loads(json.dumps(base_manifest))
    broken_manifest["gaps"] = broken_manifest["gaps"][:-1]
    missing = collect_missing(**{**base_inputs, "manifest": broken_manifest})
    expect_contains(
        "manifest_gap_detection",
        missing,
        "manifest:gap_missing:phase4-kprobe-example-zig-sample",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace(
                "shared validator still does not fail closed on the kprobe survey packet itself\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "survey_marker_detection",
        missing,
        "survey:shared validator still does not fail closed on the kprobe survey packet itself",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "build_text": base_inputs["build_text"].replace(
                "phase4-kprobe-example-survey-tests\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "build_marker_detection",
        missing,
        "build:phase4-kprobe-example-survey-tests",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_text": base_inputs["docs_root_text"].replace(
                "still-absent `samples/zigux/kprobe_example.zig` sample explicitly survey-only\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "docs_root_marker_detection",
        missing,
        "docs_root:still-absent `samples/zigux/kprobe_example.zig` sample explicitly survey-only",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "scripts_readme_text": base_inputs["scripts_readme_text"].replace(
                "check-phase4-kprobe-example-packet.py --self-test\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "scripts_readme_marker_detection",
        missing,
        "scripts_readme:check-phase4-kprobe-example-packet.py --self-test",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "tests_readme_text": base_inputs["tests_readme_text"].replace(
                "make -C zigux phase4-kprobe-example-survey\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "tests_readme_marker_detection",
        missing,
        "tests_readme:make -C zigux phase4-kprobe-example-survey",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "gate_evidence_text": base_inputs["gate_evidence_text"].replace(
                "PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA=\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "gate_evidence_marker_detection",
        missing,
        "gate_evidence:PHASE4_KPROBE_EXAMPLE_SURVEY_BLOB_SHA=",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "matrix_text": base_inputs["matrix_text"].replace(
                "phase4-kprobe-example-survey-tests\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "matrix_marker_detection",
        missing,
        "matrix:phase4-kprobe-example-survey-tests",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "kprobe_anchor_text": "",
        }
    )
    expect_contains(
        "anchor_marker_detection",
        missing,
        'anchor:static char symbol[KSYM_NAME_LEN] = "kernel_clone";',
    )

    print("PHASE4_KPROBE_EXAMPLE_PACKET_SELF_TEST=pass")
    print("PHASE4_KPROBE_EXAMPLE_PACKET_SELF_TEST_CASE_COUNT=12")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


live_inputs = build_live_inputs()
missing = collect_missing(**live_inputs)
if missing:
    print("PHASE4_KPROBE_EXAMPLE_PACKET=fail")
    print("PHASE4_KPROBE_EXAMPLE_PACKET_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE4_KPROBE_EXAMPLE_PACKET_MISSING_END")
    sys.exit(1)

print("PHASE4_KPROBE_EXAMPLE_PACKET=pass")
print(f"PHASE4_KPROBE_EXAMPLE_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE4_KPROBE_EXAMPLE_PACKET_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
print(f"PHASE4_KPROBE_EXAMPLE_PACKET_GATE_EVIDENCE_MARKER_COUNT={len(GATE_EVIDENCE_MARKERS)}")
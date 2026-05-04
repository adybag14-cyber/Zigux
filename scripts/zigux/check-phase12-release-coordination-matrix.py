#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
]

SURVEY_MARKERS = [
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "the release packet now also keeps `Documentation/zigux/phase12-release-coordination-matrix.md` explicit as the compact PMO handoff",
]

MATRIX_MARKERS = [
    "PHASE12_STATUS=active",
    "PHASE12_RELEASE_CLOSED=no",
    "PHASE12_ROADMAP_ANCHOR_COUNT=4",
    "PHASE12_APPROVED_CROSS_TARGET_COUNT=3",
    "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2",
    "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
    "| `drivers/net/virtio_net.c` | `Network Driver Lane` | active bounded starter plus survey packet |",
    "| `drivers/nvme/host/pci.c` | `Storage Driver Lane` | active bounded starter plus survey-and-slice packet |",
    "| `drivers/scsi/virtio_scsi.c` | `Storage Driver Lane` | active bounded starter plus survey-and-slice packet |",
    "| `tools/lib/bpf/libbpf.c` | `BPF Tooling Lane` | active bounded heavy-helper survey packet with a focused libbpf-only replay shard |",
    "`zigux/tests/README.md` should explicitly name this matrix plus `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, and `zigux/tests/phase12_raw_github_coverage_survey.zig`",
]

MATRIX_EXACT_COUNT_MARKERS = {
    "PHASE12_STATUS=active": 1,
    "PHASE12_RELEASE_CLOSED=no": 1,
    "PHASE12_ROADMAP_ANCHOR_COUNT=4": 1,
    "PHASE12_APPROVED_CROSS_TARGET_COUNT=3": 1,
    "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2": 1,
    "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2": 1,
    "`zigux/tests/README.md` should explicitly name this matrix plus `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, and `zigux/tests/phase12_raw_github_coverage_survey.zig`": 1,
}


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def collect_marker_misses(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_exact_count_misses(text: str, expected_counts: dict[str, int], prefix: str) -> list[str]:
    missing: list[str] = []
    for marker, expected_count in expected_counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(f"{prefix}:{marker}:expected={expected_count}:actual={actual_count}")
    return missing


def collect_missing(*, present_files: set[str], survey_text: str, matrix_text: str) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_marker_misses(survey_text, SURVEY_MARKERS, "survey"))
    missing.extend(collect_marker_misses(matrix_text, MATRIX_MARKERS, "matrix"))
    missing.extend(collect_exact_count_misses(matrix_text, MATRIX_EXACT_COUNT_MARKERS, "matrix_count"))
    return missing


def expect_contains(label: str, items: list[str], expected: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(
            f"phase12-release-coordination-matrix-self-test:{label}:expected={expected}:actual={actual}"
        )


def run_self_test() -> int:
    survey_text = "\n".join(SURVEY_MARKERS) + "\n"
    matrix_text = "\n".join(MATRIX_MARKERS) + "\n"
    for marker in MATRIX_EXACT_COUNT_MARKERS:
        if marker not in MATRIX_MARKERS:
            matrix_text += marker + "\n"

    base_inputs = {
        "present_files": set(REQUIRED_FILES),
        "survey_text": survey_text,
        "matrix_text": matrix_text,
    }

    missing = collect_missing(**base_inputs)
    if missing:
        raise SystemExit(
            "phase12-release-coordination-matrix-self-test:unexpected_failures:" + ",".join(missing)
        )

    missing = collect_missing(**{**base_inputs, "present_files": {REQUIRED_FILES[1]}})
    expect_contains(
        "release_survey_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase12-release-readiness-survey.md",
    )

    missing = collect_missing(**{**base_inputs, "present_files": {REQUIRED_FILES[0]}})
    expect_contains(
        "coord_matrix_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase12-release-coordination-matrix.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": survey_text.replace(SURVEY_MARKERS[1] + "\n", "", 1),
        }
    )
    expect_contains("survey_marker_detection", missing, f"survey:{SURVEY_MARKERS[1]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "matrix_text": matrix_text.replace(MATRIX_MARKERS[6] + "\n", "", 1),
        }
    )
    expect_contains("virtio_net_row_detection", missing, f"matrix:{MATRIX_MARKERS[6]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "matrix_text": matrix_text.replace(MATRIX_MARKERS[10] + "\n", "", 1),
        }
    )
    expect_contains("tests_root_handoff_detection", missing, f"matrix:{MATRIX_MARKERS[10]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "matrix_text": matrix_text + MATRIX_MARKERS[10] + "\n",
        }
    )
    expect_contains(
        "tests_root_handoff_exact_count_detection",
        missing,
        f"matrix_count:{MATRIX_MARKERS[10]}:expected=1:actual=2",
    )

    print("PHASE12_RELEASE_COORDINATION_MATRIX_SELF_TEST=pass")
    print("PHASE12_RELEASE_COORDINATION_MATRIX_SELF_TEST_CASE_COUNT=6")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


live_inputs = {
    "present_files": {path for path in REQUIRED_FILES if (ROOT / path).exists()},
    "survey_text": read_text("Documentation/zigux/phase12-release-readiness-survey.md"),
    "matrix_text": read_text("Documentation/zigux/phase12-release-coordination-matrix.md"),
}

missing = collect_missing(**live_inputs)
if missing:
    print("PHASE12_RELEASE_COORDINATION_MATRIX=fail")
    print("PHASE12_RELEASE_COORDINATION_MATRIX_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE12_RELEASE_COORDINATION_MATRIX_MISSING_END")
    raise SystemExit(1)

print("PHASE12_RELEASE_COORDINATION_MATRIX=pass")
print(f"PHASE12_RELEASE_COORDINATION_MATRIX_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE12_RELEASE_COORDINATION_MATRIX_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
print(f"PHASE12_RELEASE_COORDINATION_MATRIX_MARKER_COUNT={len(MATRIX_MARKERS)}")

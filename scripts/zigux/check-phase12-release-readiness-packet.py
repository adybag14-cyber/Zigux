#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
]

SURVEY_MARKERS = [
    "PHASE12_STATUS=active",
    "PHASE12_SHARED_VALIDATE_ENTRYPOINT=make -C zigux phase12-validate",
    "PHASE12_SHARED_REPLAY_ENTRYPOINT=make -C zigux phase12",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "Documentation/zigux/README.md` now also mirrors the mixed fallback split directly",
    "approved non-native musl targets `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl`",
    "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2",
    "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
    "PHASE12_APPROVED_CROSS_TARGET_COUNT=3",
    "PHASE12_RELEASE_CLOSED=no",
]

SURVEY_EXACT_COUNT_MARKERS = {
    "Documentation/zigux/README.md` now also mirrors the mixed fallback split directly": 1,
    "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2": 1,
    "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2": 1,
    "PHASE12_APPROVED_CROSS_TARGET_COUNT=3": 1,
    "PHASE12_RELEASE_CLOSED=no": 1,
}

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "the docs-root Phase 12 release packet now also states the mixed fallback split directly: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remain the dedicated commit-pinned public fallback artifacts, while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` still rely on shared-tree-only fallback reads.",
    "the active Phase 12 heavy-helper survey packet now also keeps the bounded `tools/lib/bpf/zigux_segments/` helper foundations, the reproducibility snapshot, the focused libbpf-only replay shard rooted in `scripts/zigux/check-phase12-libbpf-focused-replay.py` plus `zigux/tests/phase12_libbpf_only_build.zig`, the still-deferred file-path-and-handle bridge and perf-buffer-online-cpu-routing boundaries, and the blocked object-model, loader, and relocation split visible from the top-level docs index.",
]

DOCS_ROOT_EXACT_COUNT_MARKERS = {
    "Documentation/zigux/phase12-release-readiness-survey.md": 1,
    "the docs-root Phase 12 release packet now also states the mixed fallback split directly: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remain the dedicated commit-pinned public fallback artifacts, while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` still rely on shared-tree-only fallback reads.": 1,
}

CROSS_SMOKE_MARKERS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

RAW_COVERAGE_MARKERS = [
    "commit-pinned",
    "shared-tree-only",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
]


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


def collect_missing(
    *,
    present_files: set[str],
    survey_text: str,
    docs_root_text: str,
    cross_smoke_text: str,
    raw_coverage_text: str,
) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_marker_misses(survey_text, SURVEY_MARKERS, "survey"))
    missing.extend(collect_exact_count_misses(survey_text, SURVEY_EXACT_COUNT_MARKERS, "survey_count"))
    missing.extend(collect_marker_misses(docs_root_text, DOCS_ROOT_MARKERS, "docs_root"))
    missing.extend(collect_exact_count_misses(docs_root_text, DOCS_ROOT_EXACT_COUNT_MARKERS, "docs_root_count"))
    missing.extend(collect_marker_misses(cross_smoke_text, CROSS_SMOKE_MARKERS, "cross_smoke"))
    missing.extend(collect_marker_misses(raw_coverage_text, RAW_COVERAGE_MARKERS, "raw_coverage"))
    return missing


def build_live_inputs() -> dict[str, object]:
    return {
        "present_files": {path for path in REQUIRED_FILES if (ROOT / path).exists()},
        "survey_text": read_text("Documentation/zigux/phase12-release-readiness-survey.md"),
        "docs_root_text": read_text("Documentation/zigux/README.md"),
        "cross_smoke_text": read_text("Documentation/zigux/phase12-cross-compile-smoke.md"),
        "raw_coverage_text": read_text("Documentation/zigux/phase12-raw-github-coverage-survey.md"),
    }


def expect_contains(label: str, missing: list[str], expected_item: str) -> None:
    if expected_item not in missing:
        actual = ",".join(missing) if missing else "none"
        raise SystemExit(
            f"phase12-release-readiness-self-test:{label}:expected_missing:{expected_item}:actual:{actual}"
        )


def run_self_test() -> int:
    base_inputs = {
        "present_files": set(REQUIRED_FILES),
        "survey_text": "\n".join(SURVEY_MARKERS) + "\n",
        "docs_root_text": "\n".join(DOCS_ROOT_MARKERS) + "\n",
        "cross_smoke_text": "\n".join(CROSS_SMOKE_MARKERS) + "\n",
        "raw_coverage_text": "\n".join(RAW_COVERAGE_MARKERS) + "\n",
    }

    missing = collect_missing(**base_inputs)
    if missing:
        raise SystemExit(
            "phase12-release-readiness-self-test:unexpected_failures:" + ",".join(missing)
        )

    missing = collect_missing(**{**base_inputs, "present_files": set(REQUIRED_FILES[1:])})
    expect_contains(
        "missing_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase12-release-readiness-survey.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace(
                "PHASE12_RELEASE_CLOSED=no\n",
                "",
                1,
            ),
        }
    )
    expect_contains("survey_marker_detection", missing, "survey:PHASE12_RELEASE_CLOSED=no")

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"] + "PHASE12_RELEASE_CLOSED=no\n",
        }
    )
    expect_contains(
        "survey_exact_count_detection",
        missing,
        "survey_count:PHASE12_RELEASE_CLOSED=no:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_text": base_inputs["docs_root_text"].replace(
                DOCS_ROOT_MARKERS[5] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains("docs_root_marker_detection", missing, f"docs_root:{DOCS_ROOT_MARKERS[5]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_text": base_inputs["docs_root_text"]
            + DOCS_ROOT_MARKERS[5]
            + "\n",
        }
    )
    expect_contains(
        "docs_root_exact_count_detection",
        missing,
        f"docs_root_count:{DOCS_ROOT_MARKERS[5]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "cross_smoke_text": base_inputs["cross_smoke_text"].replace(
                "riscv64-linux-musl\n",
                "",
                1,
            ),
        }
    )
    expect_contains("cross_smoke_marker_detection", missing, "cross_smoke:riscv64-linux-musl")

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace(
                "shared-tree-only\n",
                "",
                1,
            ),
        }
    )
    expect_contains("raw_coverage_marker_detection", missing, "raw_coverage:shared-tree-only")

    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT=7")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


live_inputs = build_live_inputs()
missing = collect_missing(**live_inputs)
if missing:
    print("PHASE12_RELEASE_READINESS_PACKET=fail")
    print("PHASE12_RELEASE_READINESS_PACKET_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE12_RELEASE_READINESS_PACKET_MISSING_END")
    sys.exit(1)

print("PHASE12_RELEASE_READINESS_PACKET=pass")
print(f"PHASE12_RELEASE_READINESS_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE12_RELEASE_READINESS_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
print(f"PHASE12_RELEASE_READINESS_DOCS_ROOT_MARKER_COUNT={len(DOCS_ROOT_MARKERS)}")
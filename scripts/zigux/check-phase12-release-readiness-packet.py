#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


_resolved = Path(__file__).resolve()
ROOT = _resolved.parents[2] if len(_resolved.parents) > 2 else _resolved.parent

REQUIRED_FILES = [
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-shared-replay-contract.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase12-cross.py",
    "scripts/zigux/check-phase12-libbpf-snapshot.py",
    "scripts/zigux/check-phase12-libbpf-packet.py",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "scripts/zigux/check-phase12-raw-github-coverage.py",
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "scripts/zigux/validate-phase12.py",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "zigux/tests/phase12_raw_github_coverage_manifest.json",
    "zigux/tests/phase12_raw_github_coverage_survey.zig",
    "zigux/Makefile",
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
    "scripts/zigux/check-phase12-cross.py",
    "scripts/zigux/check-phase12-libbpf-snapshot.py",
    "scripts/zigux/check-phase12-libbpf-packet.py",
    "scripts/zigux/check-phase12-raw-github-coverage.py",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "zigux/tests/phase12_raw_github_coverage_manifest.json",
    "zigux/tests/phase12_raw_github_coverage_survey.zig",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "Documentation/zigux/README.md` now also mirrors the mixed fallback split directly",
    "approved non-native musl targets `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl`",
    "the release-facing note now also names `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test` plus `python3 scripts/zigux/check-phase12-release-readiness-packet.py` as the dedicated PMO packet guard, so this release-coordination note has its own fail-closed review hook instead of relying only on the broader validator and reviewer habit",
    "that same mixed fallback packet is also backed by `scripts/zigux/check-phase12-raw-github-coverage.py`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, and `zigux/tests/phase12_raw_github_coverage_survey.zig`, so the release-facing note now names the checker and manifest-backed survey evidence instead of treating the split as prose-only release guidance",
    "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2",
    "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
    "PHASE12_APPROVED_CROSS_TARGET_COUNT=3",
    "PHASE12_RELEASE_CLOSED=no",
]

SURVEY_EXACT_COUNT_MARKERS = {
    "Documentation/zigux/README.md` now also mirrors the mixed fallback split directly": 1,
    "scripts/zigux/check-phase12-cross.py": 2,
    "scripts/zigux/check-phase12-raw-github-coverage.py": 3,
    "zigux/tests/phase12_raw_github_coverage_manifest.json": 3,
    "zigux/tests/phase12_raw_github_coverage_survey.zig": 3,
    "the release-facing note now also names `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test` plus `python3 scripts/zigux/check-phase12-release-readiness-packet.py` as the dedicated PMO packet guard, so this release-coordination note has its own fail-closed review hook instead of relying only on the broader validator and reviewer habit": 1,
    "that same mixed fallback packet is also backed by `scripts/zigux/check-phase12-raw-github-coverage.py`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, and `zigux/tests/phase12_raw_github_coverage_survey.zig`, so the release-facing note now names the checker and manifest-backed survey evidence instead of treating the split as prose-only release guidance": 1,
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

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the Phase 12 release-facing PMO packet, do `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase12-cross-compile-smoke.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate` still keep the active-not-closed release posture, the approved `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl` smoke set, and the current two commit-pinned versus two shared-tree-only fallback split explicit?",
]

REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = {
    "if the change touches the Phase 12 release-facing PMO packet, do `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/README.md`, `Documentation/zigux/phase12-cross-compile-smoke.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate` still keep the active-not-closed release posture, the approved `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl` smoke set, and the current two commit-pinned versus two shared-tree-only fallback split explicit?": 1,
}

SCRIPTS_README_MARKERS = [
    "check-phase12-release-readiness-packet.py",
]

SCRIPTS_README_EXACT_COUNT_MARKERS = {
    "check-phase12-release-readiness-packet.py": 1,
}

VALIDATOR_MARKERS = [
    "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "Documentation/zigux/phase12-release-readiness-survey.md",
]

VALIDATOR_EXACT_COUNT_MARKERS = {
    "scripts/zigux/check-phase12-release-readiness-packet.py --self-test": 1,
    "scripts/zigux/check-phase12-release-readiness-packet.py": 2,
    "Documentation/zigux/phase12-release-readiness-survey.md": 1,
}

CONTRACT_NOTE_MARKERS = [
    "The release-readiness packet checker is intentionally part of that same stack before the broader validator runs",
    "- `Documentation/zigux/phase12-release-readiness-survey.md`",
    "- `Documentation/zigux/phase12-cross-compile-smoke.md`",
    "- `Documentation/zigux/phase12-raw-github-coverage-survey.md`",
    "- `scripts/zigux/check-phase12-release-readiness-packet.py`",
    "- `scripts/zigux/check-phase12-libbpf-snapshot.py`",
    "- `scripts/zigux/check-phase12-libbpf-packet.py`",
]

MAKEFILE_SELF_TEST_MARKER = "scripts/zigux/check-phase12-release-readiness-packet.py --self-test"
MAKEFILE_RUN_MARKER = "scripts/zigux/check-phase12-release-readiness-packet.py"

CROSS_SMOKE_MARKERS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

RAW_COVERAGE_MARKERS = [
    "commit-pinned",
    "shared-tree-only",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "scripts/zigux/check-phase12-raw-github-coverage.py",
    "zigux/tests/phase12_raw_github_coverage_manifest.json",
    "zigux/tests/phase12_raw_github_coverage_survey.zig",
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
    contract_note_text: str,
    docs_root_text: str,
    review_checklist_text: str,
    scripts_readme_text: str,
    validator_text: str,
    makefile_text: str,
    cross_smoke_text: str,
    raw_coverage_text: str,
) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_marker_misses(survey_text, SURVEY_MARKERS, "survey"))
    missing.extend(collect_exact_count_misses(survey_text, SURVEY_EXACT_COUNT_MARKERS, "survey_count"))
    missing.extend(collect_marker_misses(contract_note_text, CONTRACT_NOTE_MARKERS, "contract_note"))
    missing.extend(collect_marker_misses(docs_root_text, DOCS_ROOT_MARKERS, "docs_root"))
    missing.extend(collect_exact_count_misses(docs_root_text, DOCS_ROOT_EXACT_COUNT_MARKERS, "docs_root_count"))
    missing.extend(collect_marker_misses(review_checklist_text, REVIEW_CHECKLIST_MARKERS, "review_checklist"))
    missing.extend(
        collect_exact_count_misses(
            review_checklist_text,
            REVIEW_CHECKLIST_EXACT_COUNT_MARKERS,
            "review_checklist_count",
        )
    )
    missing.extend(collect_marker_misses(scripts_readme_text, SCRIPTS_README_MARKERS, "scripts_readme"))
    missing.extend(
        collect_exact_count_misses(
            scripts_readme_text,
            SCRIPTS_README_EXACT_COUNT_MARKERS,
            "scripts_readme_count",
        )
    )
    missing.extend(collect_marker_misses(validator_text, VALIDATOR_MARKERS, "validator"))
    missing.extend(
        collect_exact_count_misses(
            validator_text,
            VALIDATOR_EXACT_COUNT_MARKERS,
            "validator_count",
        )
    )
    missing.extend(collect_marker_misses(cross_smoke_text, CROSS_SMOKE_MARKERS, "cross_smoke"))
    missing.extend(collect_marker_misses(raw_coverage_text, RAW_COVERAGE_MARKERS, "raw_coverage"))
    return missing


def shared_validate_wires_release_guard(makefile_text: str) -> bool:
    return MAKEFILE_SELF_TEST_MARKER in makefile_text and MAKEFILE_RUN_MARKER in makefile_text


def build_live_inputs() -> dict[str, object]:
    return {
        "present_files": {path for path in REQUIRED_FILES if (ROOT / path).exists()},
        "survey_text": read_text("Documentation/zigux/phase12-release-readiness-survey.md"),
        "contract_note_text": read_text("Documentation/zigux/phase12-shared-replay-contract.md"),
        "docs_root_text": read_text("Documentation/zigux/README.md"),
        "review_checklist_text": read_text("Documentation/zigux/review-checklist.md"),
        "scripts_readme_text": read_text("scripts/zigux/README.md"),
        "validator_text": read_text("scripts/zigux/validate-phase12.py"),
        "cross_smoke_text": read_text("Documentation/zigux/phase12-cross-compile-smoke.md"),
        "raw_coverage_text": read_text("Documentation/zigux/phase12-raw-github-coverage-survey.md"),
        "makefile_text": read_text("zigux/Makefile"),
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
        "survey_text": "\n".join(
            SURVEY_MARKERS
            + [
                "scripts/zigux/check-phase12-cross.py",
                "scripts/zigux/check-phase12-libbpf-snapshot.py",
                "scripts/zigux/check-phase12-libbpf-packet.py",
                "scripts/zigux/check-phase12-raw-github-coverage.py",
                "zigux/tests/phase12_raw_github_coverage_manifest.json",
                "zigux/tests/phase12_raw_github_coverage_survey.zig",
            ]
        )
        + "\n",
        "contract_note_text": "\n".join(CONTRACT_NOTE_MARKERS) + "\n",
        "docs_root_text": "\n".join(DOCS_ROOT_MARKERS) + "\n",
        "review_checklist_text": "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        "scripts_readme_text": "\n".join(SCRIPTS_README_MARKERS) + "\n",
        "validator_text": "\n".join(VALIDATOR_MARKERS) + "\n",
        "cross_smoke_text": "\n".join(CROSS_SMOKE_MARKERS) + "\n",
        "raw_coverage_text": "\n".join(RAW_COVERAGE_MARKERS) + "\n",
        "makefile_text": "\n".join([MAKEFILE_SELF_TEST_MARKER, MAKEFILE_RUN_MARKER, "scripts/zigux/validate-phase12.py"]) + "\n",
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
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "Documentation/zigux/phase12-shared-replay-contract.md"
            },
        }
    )
    expect_contains(
        "contract_note_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase12-shared-replay-contract.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "Documentation/zigux/phase12-libbpf-segment-survey.md"
            },
        }
    )
    expect_contains(
        "libbpf_survey_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase12-libbpf-segment-survey.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "scripts/zigux/check-phase12-libbpf-focused-replay.py"
            },
        }
    )
    expect_contains(
        "focused_replay_checker_file_detection",
        missing,
        "missing_file:scripts/zigux/check-phase12-libbpf-focused-replay.py",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "scripts/zigux/check-phase12-libbpf-snapshot.py"
            },
        }
    )
    expect_contains(
        "libbpf_snapshot_checker_file_detection",
        missing,
        "missing_file:scripts/zigux/check-phase12-libbpf-snapshot.py",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "scripts/zigux/check-phase12-libbpf-packet.py"
            },
        }
    )
    expect_contains(
        "libbpf_packet_checker_file_detection",
        missing,
        "missing_file:scripts/zigux/check-phase12-libbpf-packet.py",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "zigux/tests/phase12_libbpf_only_build.zig"
            },
        }
    )
    expect_contains(
        "focused_replay_build_file_detection",
        missing,
        "missing_file:zigux/tests/phase12_libbpf_only_build.zig",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "scripts/zigux/check-phase12-raw-github-coverage.py"
            },
        }
    )
    expect_contains(
        "raw_coverage_checker_file_detection",
        missing,
        "missing_file:scripts/zigux/check-phase12-raw-github-coverage.py",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "zigux/tests/phase12_raw_github_coverage_manifest.json"
            },
        }
    )
    expect_contains(
        "raw_coverage_manifest_file_detection",
        missing,
        "missing_file:zigux/tests/phase12_raw_github_coverage_manifest.json",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "zigux/tests/phase12_raw_github_coverage_survey.zig"
            },
        }
    )
    expect_contains(
        "raw_coverage_survey_file_detection",
        missing,
        "missing_file:zigux/tests/phase12_raw_github_coverage_survey.zig",
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

    release_guard_marker = (
        "the release-facing note now also names `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test` plus "
        "`python3 scripts/zigux/check-phase12-release-readiness-packet.py` as the dedicated PMO packet guard, so this release-coordination "
        "note has its own fail-closed review hook instead of relying only on the broader validator and reviewer habit"
    )
    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace(release_guard_marker + "\n", "", 1),
        }
    )
    expect_contains("survey_release_guard_detection", missing, f"survey:{release_guard_marker}")

    raw_coverage_packet_marker = (
        "that same mixed fallback packet is also backed by `scripts/zigux/check-phase12-raw-github-coverage.py`, "
        "`zigux/tests/phase12_raw_github_coverage_manifest.json`, and `zigux/tests/phase12_raw_github_coverage_survey.zig`, "
        "so the release-facing note now names the checker and manifest-backed survey evidence instead of treating the split as prose-only release guidance"
    )
    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace(raw_coverage_packet_marker + "\n", "", 1),
        }
    )
    expect_contains(
        "survey_raw_coverage_packet_detection",
        missing,
        f"survey:{raw_coverage_packet_marker}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"] + raw_coverage_packet_marker + "\n",
        }
    )
    expect_contains(
        "survey_raw_coverage_packet_exact_count_detection",
        missing,
        f"survey_count:{raw_coverage_packet_marker}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("scripts/zigux/check-phase12-cross.py\n", "", 1),
        }
    )
    expect_contains("survey_cross_checker_detection", missing, "survey_count:scripts/zigux/check-phase12-cross.py:expected=2:actual=1")

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"] + "scripts/zigux/check-phase12-cross.py\n",
        }
    )
    expect_contains(
        "survey_cross_checker_exact_count_detection",
        missing,
        "survey_count:scripts/zigux/check-phase12-cross.py:expected=2:actual=3",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("scripts/zigux/check-phase12-libbpf-snapshot.py\n", "", 1),
        }
    )
    expect_contains(
        "survey_libbpf_snapshot_checker_detection",
        missing,
        "survey:scripts/zigux/check-phase12-libbpf-snapshot.py",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("scripts/zigux/check-phase12-libbpf-packet.py\n", "", 1),
        }
    )
    expect_contains(
        "survey_libbpf_packet_checker_detection",
        missing,
        "survey:scripts/zigux/check-phase12-libbpf-packet.py",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("scripts/zigux/check-phase12-raw-github-coverage.py\n", "", 1),
        }
    )
    expect_contains(
        "survey_raw_coverage_checker_detection",
        missing,
        "survey_count:scripts/zigux/check-phase12-raw-github-coverage.py:expected=3:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace(
                "zigux/tests/phase12_raw_github_coverage_survey.zig\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "survey_raw_coverage_survey_artifact_exact_count_detection",
        missing,
        "survey_count:zigux/tests/phase12_raw_github_coverage_survey.zig:expected=3:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace(
                "zigux/tests/phase12_raw_github_coverage_manifest.json\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "raw_coverage_manifest_marker_detection",
        missing,
        "raw_coverage:zigux/tests/phase12_raw_github_coverage_manifest.json",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace(
                "zigux/tests/phase12_raw_github_coverage_survey.zig\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "raw_coverage_survey_marker_detection",
        missing,
        "raw_coverage:zigux/tests/phase12_raw_github_coverage_survey.zig",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "contract_note_text": base_inputs["contract_note_text"].replace(
                CONTRACT_NOTE_MARKERS[0] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "contract_note_marker_detection",
        missing,
        f"contract_note:{CONTRACT_NOTE_MARKERS[0]}",
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
            "docs_root_text": base_inputs["docs_root_text"] + DOCS_ROOT_MARKERS[5] + "\n",
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
            "review_checklist_text": base_inputs["review_checklist_text"].replace(
                REVIEW_CHECKLIST_MARKERS[0] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "review_checklist_marker_detection",
        missing,
        f"review_checklist:{REVIEW_CHECKLIST_MARKERS[0]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "review_checklist_text": base_inputs["review_checklist_text"]
            + REVIEW_CHECKLIST_MARKERS[0]
            + "\n",
        }
    )
    expect_contains(
        "review_checklist_exact_count_detection",
        missing,
        f"review_checklist_count:{REVIEW_CHECKLIST_MARKERS[0]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "scripts_readme_text": "",
        }
    )
    expect_contains(
        "scripts_readme_marker_detection",
        missing,
        "scripts_readme:check-phase12-release-readiness-packet.py",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "scripts_readme_text": base_inputs["scripts_readme_text"]
            + "check-phase12-release-readiness-packet.py\n",
        }
    )
    expect_contains(
        "scripts_readme_exact_count_detection",
        missing,
        "scripts_readme_count:check-phase12-release-readiness-packet.py:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "validator_text": base_inputs["validator_text"].replace(
                "Documentation/zigux/phase12-release-readiness-survey.md\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "validator_marker_detection",
        missing,
        "validator:Documentation/zigux/phase12-release-readiness-survey.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "validator_text": base_inputs["validator_text"]
            + "scripts/zigux/check-phase12-release-readiness-packet.py\n",
        }
    )
    expect_contains(
        "validator_exact_count_detection",
        missing,
        "validator_count:scripts/zigux/check-phase12-release-readiness-packet.py:expected=2:actual=3",
    )

    if not shared_validate_wires_release_guard(base_inputs["makefile_text"]):
        raise SystemExit("phase12-release-readiness-self-test:unexpected_makefile_wireup_failure")

    if shared_validate_wires_release_guard(base_inputs["makefile_text"].replace(MAKEFILE_SELF_TEST_MARKER + "\n", "", 1)):
        raise SystemExit("phase12-release-readiness-self-test:makefile_wireup_detection_failed")

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
    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT=36")
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
print(f"PHASE12_RELEASE_READINESS_REVIEW_CHECKLIST_MARKER_COUNT={len(REVIEW_CHECKLIST_MARKERS)}")
print(f"PHASE12_RELEASE_READINESS_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_MARKERS)}")
print(f"PHASE12_RELEASE_READINESS_VALIDATOR_MARKER_COUNT={len(VALIDATOR_MARKERS)}")
print(
    "PHASE12_RELEASE_READINESS_SHARED_VALIDATE_WIRES_PACKET_GUARD="
    + ("yes" if shared_validate_wires_release_guard(live_inputs["makefile_text"]) else "no")
)

#!/usr/bin/env python3
from __future__ import annotations

import json
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

CONTRACT_NOTE_EXACT_COUNT_MARKERS = {
    "that same release-facing PMO packet now also names `zigux/tests/phase12_raw_github_coverage_manifest.json` and `zigux/tests/phase12_raw_github_coverage_survey.zig` directly, so the mixed public-read fallback split stays tied to manifest-backed and Zig-survey-backed evidence instead of living only in note-level prose.": 1,
    "- `zigux/tests/phase12_raw_github_coverage_manifest.json`": 1,
    "- `zigux/tests/phase12_raw_github_coverage_survey.zig`": 1,
}

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
    "one anchor keeps a commit-pinned raw fallback catalog with a last bounded replay note: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
    "one anchor keeps a commit-pinned raw fallback map for the archived NVMe packet: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`",
    "two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`",
    "`PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`",
    "`PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`",
    "`PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4`",
    "`PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2`",
]

RAW_COVERAGE_EXACT_COUNT_MARKERS = {
    "one anchor keeps a commit-pinned raw fallback catalog with a last bounded replay note: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`": 1,
    "one anchor keeps a commit-pinned raw fallback map for the archived NVMe packet: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`": 1,
    "two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`": 1,
    "`PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`": 1,
    "`PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`": 1,
    "`PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4`": 1,
    "`PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2`": 1,
}

RAW_COVERAGE_EXPECTED_ROOTS = [
    "https://github.com/adybag14-cyber/Zigux/tree/master/drivers/net",
    "https://github.com/adybag14-cyber/Zigux/tree/master/tools/lib/bpf",
    "https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux",
    "https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests",
]

RAW_COVERAGE_EXPECTED_BRANCH_RAW_PATHS = [
    "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c",
    "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/tools/lib/bpf/libbpf.c",
]

RAW_COVERAGE_EXPECTED_ANCHORS = {
    "virtio_net": {
        "anchor": "drivers/net/virtio_net.c",
        "roadmap_destination": "drivers/net/virtio_net.zig",
        "survey_note_path": "Documentation/zigux/phase12-virtio-net-survey.md",
        "public_read_status": "shared_tree_only",
        "raw_fallback_catalog_path": "",
        "raw_fallback_map_path": "",
        "shared_tree_branch_raw_path": "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c",
    },
    "nvme_pci": {
        "anchor": "drivers/nvme/host/pci.c",
        "roadmap_destination": "drivers/nvme/host/pci.zig",
        "survey_note_path": "Documentation/zigux/phase12-nvme-pci-survey.md",
        "public_read_status": "commit_pinned_raw_map",
        "raw_fallback_catalog_path": "",
        "raw_fallback_map_path": "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        "shared_tree_branch_raw_path": "",
    },
    "virtio_scsi": {
        "anchor": "drivers/scsi/virtio_scsi.c",
        "roadmap_destination": "drivers/scsi/virtio_scsi.zig",
        "survey_note_path": "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "public_read_status": "commit_pinned_raw_catalog",
        "raw_fallback_catalog_path": "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        "raw_fallback_map_path": "",
        "shared_tree_branch_raw_path": "",
    },
    "libbpf": {
        "anchor": "tools/lib/bpf/libbpf.c",
        "roadmap_destination": "tools/lib/bpf/zigux_segments/",
        "survey_note_path": "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "public_read_status": "shared_tree_only",
        "raw_fallback_catalog_path": "",
        "raw_fallback_map_path": "",
        "shared_tree_branch_raw_path": "https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/tools/lib/bpf/libbpf.c",
    },
}

RAW_COVERAGE_SURVEY_ZIG_MARKERS = [
    'test "phase12 raw GitHub coverage survey keeps the roadmap-wide public-read split explicit" {',
    'try std.testing.expectEqualStrings("P12-L07", manifest.lane_key);',
    'try std.testing.expectEqualStrings("Phase 12", manifest.phase);',
    'try std.testing.expectEqualStrings("0bd402fd6ca83ba2ace6b21e9e57459401b631cd", manifest.last_replayed_public_head);',
    'try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_anchor_count);',
    'try std.testing.expectEqual(@as(usize, 1), manifest.commit_pinned_raw_fallback_catalog_count);',
    'try std.testing.expectEqual(@as(usize, 1), manifest.commit_pinned_raw_fallback_map_count);',
    'try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_only_anchor_count);',
    'try std.testing.expectEqual(@as(usize, 4), manifest.shared_tree_readback_root_count);',
    'try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_branch_raw_path_count);',
    'try std.testing.expectEqual(@as(usize, 4), manifest.shared_tree_readback_roots.len);',
    'try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_branch_raw_paths.len);',
    'try std.testing.expectEqual(@as(usize, 4), manifest.anchors.len);',
    'try std.testing.expectEqual(@as(usize, 2), shared_tree_only_count);',
    'try std.testing.expectEqual(@as(usize, 1), commit_pinned_catalog_count);',
    'try std.testing.expectEqual(@as(usize, 1), commit_pinned_map_count);',
    'try std.testing.expectEqual(@as(usize, 2), shared_tree_branch_raw_path_count);',
    '"one anchor keeps a commit-pinned raw fallback catalog"',
    '"one anchor keeps a commit-pinned raw fallback map"',
    '"two anchors remain shared-tree-only fallback reads"',
    '"https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c"',
    '"https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/tools/lib/bpf/libbpf.c"',
    '"PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4"',
    '"PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2"',
]

RAW_COVERAGE_SURVEY_ZIG_EXACT_COUNT_MARKERS = {
    'try std.testing.expectEqualStrings("P12-L07", manifest.lane_key);': 1,
    'try std.testing.expectEqual(@as(usize, 4), manifest.roadmap_anchor_count);': 1,
    'try std.testing.expectEqual(@as(usize, 1), manifest.commit_pinned_raw_fallback_catalog_count);': 1,
    'try std.testing.expectEqual(@as(usize, 1), manifest.commit_pinned_raw_fallback_map_count);': 1,
    'try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_only_anchor_count);': 1,
    'try std.testing.expectEqual(@as(usize, 4), manifest.shared_tree_readback_root_count);': 1,
    'try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_branch_raw_path_count);': 1,
    'try std.testing.expectEqual(@as(usize, 2), shared_tree_only_count);': 1,
    'try std.testing.expectEqual(@as(usize, 1), commit_pinned_catalog_count);': 1,
    'try std.testing.expectEqual(@as(usize, 1), commit_pinned_map_count);': 1,
    'try std.testing.expectEqual(@as(usize, 2), shared_tree_branch_raw_path_count);': 1,
    '"one anchor keeps a commit-pinned raw fallback catalog"': 1,
    '"one anchor keeps a commit-pinned raw fallback map"': 1,
    '"two anchors remain shared-tree-only fallback reads"': 1,
    '"https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c"': 1,
    '"https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/tools/lib/bpf/libbpf.c"': 1,
    '"PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2"': 1,
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


def collect_raw_coverage_manifest_misses(manifest_text: str, prefix: str) -> list[str]:
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return [f"{prefix}:json_decode"]

    missing: list[str] = []
    expected_scalars = {
        "lane_key": "P12-L07",
        "phase": "Phase 12",
        "scope": "raw GitHub fallback catalog survey public-read coverage gaps vs roadmap",
        "public_read_boundary": "read_only_public_github_tree_and_raw_paths_only",
        "last_replayed_public_head": "0bd402fd6ca83ba2ace6b21e9e57459401b631cd",
        "roadmap_anchor_count": 4,
        "commit_pinned_raw_fallback_catalog_count": 1,
        "commit_pinned_raw_fallback_map_count": 1,
        "shared_tree_only_anchor_count": 2,
        "shared_tree_readback_root_count": 4,
        "shared_tree_branch_raw_path_count": 2,
    }
    for key, expected_value in expected_scalars.items():
        actual_value = manifest.get(key)
        if actual_value != expected_value:
            missing.append(f"{prefix}:{key}:expected={expected_value}:actual={actual_value}")

    roots = manifest.get("shared_tree_readback_roots")
    if roots != RAW_COVERAGE_EXPECTED_ROOTS:
        missing.append(
            f"{prefix}:shared_tree_readback_roots:expected={RAW_COVERAGE_EXPECTED_ROOTS}:actual={roots}"
        )

    branch_raw_paths = manifest.get("shared_tree_branch_raw_paths")
    if branch_raw_paths != RAW_COVERAGE_EXPECTED_BRANCH_RAW_PATHS:
        missing.append(
            f"{prefix}:shared_tree_branch_raw_paths:expected={RAW_COVERAGE_EXPECTED_BRANCH_RAW_PATHS}:actual={branch_raw_paths}"
        )

    anchors = manifest.get("anchors")
    if not isinstance(anchors, list):
        missing.append(f"{prefix}:anchors:not_list")
        return missing
    if len(anchors) != len(RAW_COVERAGE_EXPECTED_ANCHORS):
        missing.append(
            f"{prefix}:anchors:expected={len(RAW_COVERAGE_EXPECTED_ANCHORS)}:actual={len(anchors)}"
        )

    seen_ids: set[str] = set()
    for anchor in anchors:
        if not isinstance(anchor, dict):
            missing.append(f"{prefix}:anchor:not_dict")
            continue
        anchor_id = anchor.get("id")
        if not isinstance(anchor_id, str):
            missing.append(f"{prefix}:anchor:missing_id")
            continue
        seen_ids.add(anchor_id)
        expected_anchor = RAW_COVERAGE_EXPECTED_ANCHORS.get(anchor_id)
        if expected_anchor is None:
            missing.append(f"{prefix}:anchor:{anchor_id}:unexpected")
            continue
        for key, expected_value in expected_anchor.items():
            actual_value = anchor.get(key)
            if actual_value != expected_value:
                missing.append(
                    f"{prefix}:anchor:{anchor_id}:{key}:expected={expected_value}:actual={actual_value}"
                )

    missing_ids = set(RAW_COVERAGE_EXPECTED_ANCHORS) - seen_ids
    if missing_ids:
        missing.append(f"{prefix}:anchor_ids:missing={sorted(missing_ids)}")

    return missing


def collect_raw_coverage_survey_zig_misses(text: str, prefix: str) -> list[str]:
    missing = collect_marker_misses(text, RAW_COVERAGE_SURVEY_ZIG_MARKERS, prefix)
    missing.extend(
        collect_exact_count_misses(
            text,
            RAW_COVERAGE_SURVEY_ZIG_EXACT_COUNT_MARKERS,
            f"{prefix}_count",
        )
    )
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
    raw_coverage_manifest_text: str,
    raw_coverage_survey_zig_text: str,
) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_marker_misses(survey_text, SURVEY_MARKERS, "survey"))
    missing.extend(collect_exact_count_misses(survey_text, SURVEY_EXACT_COUNT_MARKERS, "survey_count"))
    missing.extend(collect_marker_misses(contract_note_text, CONTRACT_NOTE_MARKERS, "contract_note"))
    missing.extend(
        collect_exact_count_misses(
            contract_note_text,
            CONTRACT_NOTE_EXACT_COUNT_MARKERS,
            "contract_note_count",
        )
    )
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
    missing.extend(
        collect_exact_count_misses(
            raw_coverage_text,
            RAW_COVERAGE_EXACT_COUNT_MARKERS,
            "raw_coverage_count",
        )
    )
    missing.extend(collect_raw_coverage_manifest_misses(raw_coverage_manifest_text, "raw_coverage_manifest"))
    missing.extend(collect_raw_coverage_survey_zig_misses(raw_coverage_survey_zig_text, "raw_coverage_survey_zig"))
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
        "makefile_text": read_text("zigux/Makefile"),
        "cross_smoke_text": read_text("Documentation/zigux/phase12-cross-compile-smoke.md"),
        "raw_coverage_text": read_text("Documentation/zigux/phase12-raw-github-coverage-survey.md"),
        "raw_coverage_manifest_text": read_text("zigux/tests/phase12_raw_github_coverage_manifest.json"),
        "raw_coverage_survey_zig_text": read_text("zigux/tests/phase12_raw_github_coverage_survey.zig"),
    }


def expect_contains(case: str, haystack: list[str], needle: str) -> None:
    if needle not in haystack:
        raise SystemExit(f"phase12-release-readiness-self-test:{case}:missing={needle}:actual={haystack}")


def build_base_inputs() -> dict[str, object]:
    base_manifest = {
        "lane_key": "P12-L07",
        "phase": "Phase 12",
        "scope": "raw GitHub fallback catalog survey public-read coverage gaps vs roadmap",
        "public_read_boundary": "read_only_public_github_tree_and_raw_paths_only",
        "last_replayed_public_head": "0bd402fd6ca83ba2ace6b21e9e57459401b631cd",
        "roadmap_anchor_count": 4,
        "commit_pinned_raw_fallback_catalog_count": 1,
        "commit_pinned_raw_fallback_map_count": 1,
        "shared_tree_only_anchor_count": 2,
        "shared_tree_readback_root_count": 4,
        "shared_tree_branch_raw_path_count": 2,
        "shared_tree_readback_roots": RAW_COVERAGE_EXPECTED_ROOTS,
        "shared_tree_branch_raw_paths": RAW_COVERAGE_EXPECTED_BRANCH_RAW_PATHS,
        "anchors": [
            {
                "id": "virtio_net",
                **RAW_COVERAGE_EXPECTED_ANCHORS["virtio_net"],
            },
            {
                "id": "nvme_pci",
                **RAW_COVERAGE_EXPECTED_ANCHORS["nvme_pci"],
            },
            {
                "id": "virtio_scsi",
                **RAW_COVERAGE_EXPECTED_ANCHORS["virtio_scsi"],
            },
            {
                "id": "libbpf",
                **RAW_COVERAGE_EXPECTED_ANCHORS["libbpf"],
            },
        ],
    }
    return {
        "present_files": set(REQUIRED_FILES),
        "survey_text": "\n".join(
            SURVEY_MARKERS
            + [
                "scripts/zigux/check-phase12-cross.py",
                "scripts/zigux/check-phase12-raw-github-coverage.py",
                "zigux/tests/phase12_raw_github_coverage_manifest.json",
                "zigux/tests/phase12_raw_github_coverage_survey.zig",
            ]
        )
        + "\n",
        "contract_note_text": "\n".join(CONTRACT_NOTE_MARKERS + list(CONTRACT_NOTE_EXACT_COUNT_MARKERS)) + "\n",
        "docs_root_text": "\n".join(DOCS_ROOT_MARKERS) + "\n",
        "review_checklist_text": "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        "scripts_readme_text": "\n".join(SCRIPTS_README_MARKERS) + "\n",
        "validator_text": "\n".join(
            [
                "scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
                "scripts/zigux/check-phase12-release-readiness-packet.py",
                "Documentation/zigux/phase12-release-readiness-survey.md",
            ]
        )
        + "\n",
        "makefile_text": "\n".join([MAKEFILE_SELF_TEST_MARKER, MAKEFILE_RUN_MARKER, "scripts/zigux/validate-phase12.py"]) + "\n",
        "cross_smoke_text": "\n".join(CROSS_SMOKE_MARKERS) + "\n",
        "raw_coverage_text": "\n".join(RAW_COVERAGE_MARKERS) + "\n",
        "raw_coverage_manifest_text": json.dumps(base_manifest, indent=2),
        "raw_coverage_survey_zig_text": "\n".join(RAW_COVERAGE_SURVEY_ZIG_MARKERS) + "\n",
    }


def run_self_test() -> int:
    base_inputs = build_base_inputs()
    base_manifest = json.loads(base_inputs["raw_coverage_manifest_text"])

    missing = collect_missing(**base_inputs)
    if missing:
        raise SystemExit("phase12-release-readiness-self-test:unexpected_failures:" + ",".join(missing))

    missing = collect_missing(**{**base_inputs, "present_files": set(REQUIRED_FILES[1:])})
    expect_contains("missing_file_detection", missing, "missing_file:Documentation/zigux/phase12-release-readiness-survey.md")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "Documentation/zigux/phase12-shared-replay-contract.md"},
        }
    )
    expect_contains("contract_note_file_detection", missing, "missing_file:Documentation/zigux/phase12-shared-replay-contract.md")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "Documentation/zigux/phase12-libbpf-segment-survey.md"},
        }
    )
    expect_contains("libbpf_survey_file_detection", missing, "missing_file:Documentation/zigux/phase12-libbpf-segment-survey.md")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "scripts/zigux/check-phase12-cross.py"},
        }
    )
    expect_contains("cross_checker_file_detection", missing, "missing_file:scripts/zigux/check-phase12-cross.py")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "scripts/zigux/check-phase12-libbpf-focused-replay.py"},
        }
    )
    expect_contains("focused_replay_checker_file_detection", missing, "missing_file:scripts/zigux/check-phase12-libbpf-focused-replay.py")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "scripts/zigux/check-phase12-libbpf-snapshot.py"},
        }
    )
    expect_contains("libbpf_snapshot_checker_file_detection", missing, "missing_file:scripts/zigux/check-phase12-libbpf-snapshot.py")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "scripts/zigux/check-phase12-libbpf-packet.py"},
        }
    )
    expect_contains("libbpf_packet_checker_file_detection", missing, "missing_file:scripts/zigux/check-phase12-libbpf-packet.py")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "zigux/tests/phase12_libbpf_only_build.zig"},
        }
    )
    expect_contains("focused_replay_build_file_detection", missing, "missing_file:zigux/tests/phase12_libbpf_only_build.zig")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "scripts/zigux/check-phase12-raw-github-coverage.py"},
        }
    )
    expect_contains("raw_coverage_checker_file_detection", missing, "missing_file:scripts/zigux/check-phase12-raw-github-coverage.py")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "zigux/tests/phase12_raw_github_coverage_manifest.json"},
        }
    )
    expect_contains("raw_coverage_manifest_file_detection", missing, "missing_file:zigux/tests/phase12_raw_github_coverage_manifest.json")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "zigux/tests/phase12_raw_github_coverage_survey.zig"},
        }
    )
    expect_contains("raw_coverage_survey_file_detection", missing, "missing_file:zigux/tests/phase12_raw_github_coverage_survey.zig")

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("PHASE12_RELEASE_CLOSED=no\n", "", 1),
        }
    )
    expect_contains("survey_marker_detection", missing, "survey:PHASE12_RELEASE_CLOSED=no")

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"] + "PHASE12_RELEASE_CLOSED=no\n",
        }
    )
    expect_contains("survey_exact_count_detection", missing, "survey_count:PHASE12_RELEASE_CLOSED=no:expected=1:actual=2")

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
    expect_contains("survey_raw_coverage_packet_detection", missing, f"survey:{raw_coverage_packet_marker}")

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
    expect_contains("survey_cross_checker_exact_count_detection", missing, "survey_count:scripts/zigux/check-phase12-cross.py:expected=2:actual=3")

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("scripts/zigux/check-phase12-libbpf-snapshot.py\n", "", 1),
        }
    )
    expect_contains("survey_libbpf_snapshot_checker_detection", missing, "survey:scripts/zigux/check-phase12-libbpf-snapshot.py")

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("scripts/zigux/check-phase12-libbpf-packet.py\n", "", 1),
        }
    )
    expect_contains("survey_libbpf_packet_checker_detection", missing, "survey:scripts/zigux/check-phase12-libbpf-packet.py")

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("scripts/zigux/check-phase12-raw-github-coverage.py\n", "", 1),
        }
    )
    expect_contains("survey_raw_coverage_checker_detection", missing, "survey_count:scripts/zigux/check-phase12-raw-github-coverage.py:expected=3:actual=2")

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_text": base_inputs["survey_text"].replace("zigux/tests/phase12_raw_github_coverage_survey.zig\n", "", 1),
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
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace("zigux/tests/phase12_raw_github_coverage_manifest.json\n", "", 1),
        }
    )
    expect_contains("raw_coverage_manifest_marker_detection", missing, "raw_coverage:zigux/tests/phase12_raw_github_coverage_manifest.json")

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace("zigux/tests/phase12_raw_github_coverage_survey.zig\n", "", 1),
        }
    )
    expect_contains("raw_coverage_survey_marker_detection", missing, "raw_coverage:zigux/tests/phase12_raw_github_coverage_survey.zig")

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace(
                "one anchor keeps a commit-pinned raw fallback catalog with a last bounded replay note: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "raw_coverage_catalog_split_detection",
        missing,
        "raw_coverage:one anchor keeps a commit-pinned raw fallback catalog with a last bounded replay note: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"]
            + "one anchor keeps a commit-pinned raw fallback map for the archived NVMe packet: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`\n",
        }
    )
    expect_contains(
        "raw_coverage_map_split_exact_count_detection",
        missing,
        "raw_coverage_count:one anchor keeps a commit-pinned raw fallback map for the archived NVMe packet: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace("`PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4`\n", "", 1),
        }
    )
    expect_contains(
        "raw_coverage_readback_root_count_detection",
        missing,
        "raw_coverage_count:`PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4`:expected=1:actual=0",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"] + "two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`\n",
        }
    )
    expect_contains(
        "raw_coverage_shared_tree_split_exact_count_detection",
        missing,
        "raw_coverage_count:two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace("`PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2`\n", "", 1),
        }
    )
    expect_contains(
        "raw_coverage_branch_raw_path_count_detection",
        missing,
        "raw_coverage_count:`PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2`:expected=1:actual=0",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "contract_note_text": base_inputs["contract_note_text"].replace(CONTRACT_NOTE_MARKERS[0] + "\n", "", 1),
        }
    )
    expect_contains("contract_note_marker_detection", missing, f"contract_note:{CONTRACT_NOTE_MARKERS[0]}")

    contract_note_raw_coverage_sentence = next(iter(CONTRACT_NOTE_EXACT_COUNT_MARKERS))
    missing = collect_missing(
        **{
            **base_inputs,
            "contract_note_text": base_inputs["contract_note_text"].replace(contract_note_raw_coverage_sentence + "\n", "", 1),
        }
    )
    expect_contains(
        "contract_note_raw_coverage_sentence_exact_count_detection",
        missing,
        f"contract_note_count:{contract_note_raw_coverage_sentence}:expected=1:actual=0",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "contract_note_text": base_inputs["contract_note_text"] + "- `zigux/tests/phase12_raw_github_coverage_manifest.json`\n",
        }
    )
    expect_contains(
        "contract_note_manifest_review_use_exact_count_detection",
        missing,
        "contract_note_count:- `zigux/tests/phase12_raw_github_coverage_manifest.json`:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "contract_note_text": base_inputs["contract_note_text"] + "- `zigux/tests/phase12_raw_github_coverage_survey.zig`\n",
        }
    )
    expect_contains(
        "contract_note_survey_review_use_exact_count_detection",
        missing,
        "contract_note_count:- `zigux/tests/phase12_raw_github_coverage_survey.zig`:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_text": base_inputs["docs_root_text"].replace(DOCS_ROOT_MARKERS[5] + "\n", "", 1),
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
            "review_checklist_text": base_inputs["review_checklist_text"].replace(REVIEW_CHECKLIST_MARKERS[0] + "\n", "", 1),
        }
    )
    expect_contains("review_checklist_marker_detection", missing, f"review_checklist:{REVIEW_CHECKLIST_MARKERS[0]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "review_checklist_text": base_inputs["review_checklist_text"] + REVIEW_CHECKLIST_MARKERS[0] + "\n",
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
    expect_contains("scripts_readme_marker_detection", missing, "scripts_readme:check-phase12-release-readiness-packet.py")

    missing = collect_missing(
        **{
            **base_inputs,
            "scripts_readme_text": base_inputs["scripts_readme_text"] + "check-phase12-release-readiness-packet.py\n",
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
            "validator_text": base_inputs["validator_text"].replace("Documentation/zigux/phase12-release-readiness-survey.md\n", "", 1),
        }
    )
    expect_contains("validator_marker_detection", missing, "validator:Documentation/zigux/phase12-release-readiness-survey.md")

    missing = collect_missing(
        **{
            **base_inputs,
            "validator_text": base_inputs["validator_text"] + "scripts/zigux/check-phase12-release-readiness-packet.py\n",
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
            "cross_smoke_text": base_inputs["cross_smoke_text"].replace("riscv64-linux-musl\n", "", 1),
        }
    )
    expect_contains("cross_smoke_marker_detection", missing, "cross_smoke:riscv64-linux-musl")

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace(
                "two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "raw_coverage_marker_detection",
        missing,
        "raw_coverage:two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_manifest_text": "{",
        }
    )
    expect_contains("raw_coverage_manifest_json_detection", missing, "raw_coverage_manifest:json_decode")

    drifted_manifest = dict(base_manifest)
    drifted_manifest["shared_tree_only_anchor_count"] = 3
    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_manifest_text": json.dumps(drifted_manifest, indent=2),
        }
    )
    expect_contains(
        "raw_coverage_manifest_count_detection",
        missing,
        "raw_coverage_manifest:shared_tree_only_anchor_count:expected=2:actual=3",
    )

    drifted_manifest = dict(base_manifest)
    drifted_manifest["last_replayed_public_head"] = "bc2373f7deedf021c73beaae29555a9ac6b0536d"
    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_manifest_text": json.dumps(drifted_manifest, indent=2),
        }
    )
    expect_contains(
        "raw_coverage_manifest_head_detection",
        missing,
        "raw_coverage_manifest:last_replayed_public_head:expected=0bd402fd6ca83ba2ace6b21e9e57459401b631cd:actual=bc2373f7deedf021c73beaae29555a9ac6b0536d",
    )

    drifted_manifest = dict(base_manifest)
    drifted_manifest["shared_tree_branch_raw_path_count"] = 1
    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_manifest_text": json.dumps(drifted_manifest, indent=2),
        }
    )
    expect_contains(
        "raw_coverage_manifest_branch_raw_path_count_detection",
        missing,
        "raw_coverage_manifest:shared_tree_branch_raw_path_count:expected=2:actual=1",
    )

    drifted_manifest = json.loads(json.dumps(base_manifest))
    drifted_manifest["shared_tree_branch_raw_paths"] = RAW_COVERAGE_EXPECTED_BRANCH_RAW_PATHS[:1]
    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_manifest_text": json.dumps(drifted_manifest, indent=2),
        }
    )
    expect_contains(
        "raw_coverage_manifest_branch_raw_paths_detection",
        missing,
        f"raw_coverage_manifest:shared_tree_branch_raw_paths:expected={RAW_COVERAGE_EXPECTED_BRANCH_RAW_PATHS}:actual={RAW_COVERAGE_EXPECTED_BRANCH_RAW_PATHS[:1]}",
    )

    drifted_manifest = json.loads(json.dumps(base_manifest))
    drifted_manifest["anchors"][0]["shared_tree_branch_raw_path"] = ""
    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_manifest_text": json.dumps(drifted_manifest, indent=2),
        }
    )
    expect_contains(
        "raw_coverage_manifest_anchor_branch_raw_path_detection",
        missing,
        "raw_coverage_manifest:anchor:virtio_net:shared_tree_branch_raw_path:expected=https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/net/virtio_net.c:actual=",
    )

    drifted_manifest = json.loads(json.dumps(base_manifest))
    drifted_manifest["anchors"][3]["public_read_status"] = "commit_pinned_raw_catalog"
    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_manifest_text": json.dumps(drifted_manifest, indent=2),
        }
    )
    expect_contains(
        "raw_coverage_manifest_anchor_status_detection",
        missing,
        "raw_coverage_manifest:anchor:libbpf:public_read_status:expected=shared_tree_only:actual=commit_pinned_raw_catalog",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_survey_zig_text": base_inputs["raw_coverage_survey_zig_text"].replace(
                'try std.testing.expectEqual(@as(usize, 2), shared_tree_only_count);\n',
                "",
                1,
            ),
        }
    )
    expect_contains(
        "raw_coverage_survey_zig_marker_detection",
        missing,
        "raw_coverage_survey_zig:try std.testing.expectEqual(@as(usize, 2), shared_tree_only_count);",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_survey_zig_text": base_inputs["raw_coverage_survey_zig_text"].replace(
                'try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_branch_raw_path_count);\n',
                "",
                1,
            ),
        }
    )
    expect_contains(
        "raw_coverage_survey_zig_branch_raw_path_count_marker_detection",
        missing,
        "raw_coverage_survey_zig:try std.testing.expectEqual(@as(usize, 2), manifest.shared_tree_branch_raw_path_count);",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_survey_zig_text": base_inputs["raw_coverage_survey_zig_text"].replace(
                '"PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2"\n',
                "",
                1,
            ),
        }
    )
    expect_contains(
        "raw_coverage_survey_zig_branch_raw_path_banner_detection",
        missing,
        'raw_coverage_survey_zig:"PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2"',
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_survey_zig_text": base_inputs["raw_coverage_survey_zig_text"]
            + '"PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2"\n',
        }
    )
    expect_contains(
        "raw_coverage_survey_zig_branch_raw_path_banner_exact_count_detection",
        missing,
        'raw_coverage_survey_zig_count:"PHASE12_SHARED_TREE_BRANCH_RAW_PATH_COUNT=2":expected=1:actual=2',
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_survey_zig_text": base_inputs["raw_coverage_survey_zig_text"]
            + '"two anchors remain shared-tree-only fallback reads"\n',
        }
    )
    expect_contains(
        "raw_coverage_survey_zig_exact_count_detection",
        missing,
        'raw_coverage_survey_zig_count:"two anchors remain shared-tree-only fallback reads":expected=1:actual=2',
    )

    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST=pass")
    print("PHASE12_RELEASE_READINESS_PACKET_SELF_TEST_CASE_COUNT=54")
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

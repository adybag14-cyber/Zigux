#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

FILES = [
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase12_raw_github_coverage_manifest.json",
    "zigux/tests/phase12_raw_github_coverage_survey.zig",
    "zigux/Makefile",
]

MAKE_MARKERS = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-raw-github-coverage.py --self-test",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-raw-github-coverage.py\n",
]

SURVEY_MARKERS = [
    "lane: `P12-L07`",
    "phase: `Phase 12`",
    "public boundary: read-only GitHub tree and raw-path inspection only",
    "last replayed public head for this exact coverage split: `bc2373f7deedf021c73beaae29555a9ac6b0536d`",
    "`drivers/net/virtio_net.c`",
    "`drivers/nvme/host/pci.c`",
    "`drivers/scsi/virtio_scsi.c`",
    "`tools/lib/bpf/libbpf.c`",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "https://github.com/adybag14-cyber/Zigux/tree/master/drivers/net",
    "https://github.com/adybag14-cyber/Zigux/tree/master/tools/lib/bpf",
    "https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux",
    "https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests",
    "PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4",
]

SURVEY_EXACT_COUNT_MARKERS = {
    "lane: `P12-L07`": 1,
    "last replayed public head for this exact coverage split: `bc2373f7deedf021c73beaae29555a9ac6b0536d`": 1,
    "one anchor keeps a commit-pinned raw fallback catalog with a last bounded replay note: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`": 1,
    "one anchor keeps a commit-pinned raw fallback map for the archived NVMe packet: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`": 1,
    "two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`": 1,
    "PHASE12_ROADMAP_ANCHOR_COUNT=4": 1,
    "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2": 1,
    "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2": 1,
    "PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4": 1,
}

DOCS_ROOT_MARKERS = [
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "the docs-root Phase 12 release packet now also states the mixed fallback split directly",
    "Documentation/zigux/phase12-virtio-net-survey.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
]

RELEASE_MARKERS = [
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2",
    "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
    "the raw-fallback packet now keeps the split explicit: two anchors have dedicated commit-pinned fallback artifacts, and two anchors still rely on shared-tree fallback reads",
]

RELEASE_EXACT_COUNT_MARKERS = {
    "PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2": 1,
    "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2": 1,
    "the raw-fallback packet now keeps the split explicit: two anchors have dedicated commit-pinned fallback artifacts, and two anchors still rely on shared-tree fallback reads": 1,
}

CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 12 degraded-workflow packet",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    "including the current one commit-pinned raw catalog, one archival raw map, and two shared-tree-only anchors",
]

CHECKLIST_EXACT_COUNT_MARKERS = {
    "including the current one commit-pinned raw catalog, one archival raw map, and two shared-tree-only anchors": 1,
}

TEST_MARKERS = [
    "phase12 raw GitHub coverage survey keeps the roadmap-wide public-read split explicit",
    "phase12_raw_github_coverage_manifest.json",
    "phase12-virtio-scsi-raw-github-fallback-catalog.md",
    "phase12-nvme-pci-raw-github-fallback-map.md",
    "shared_tree_only",
    "commit_pinned_raw_catalog",
    "commit_pinned_raw_map",
    "shared_tree_readback_root_count",
    "shared_tree_readback_roots",
]

TEST_EXACT_COUNT_MARKERS = {
    'try std.testing.expectEqualStrings("P12-L07", manifest.lane_key);': 1,
    'try std.testing.expectEqual(@as(usize, 4), manifest.shared_tree_readback_root_count);': 1,
    'try std.testing.expectEqual(@as(usize, 2), shared_tree_only_count);': 1,
    'try std.testing.expectEqual(@as(usize, 1), commit_pinned_catalog_count);': 1,
    'try std.testing.expectEqual(@as(usize, 1), commit_pinned_map_count);': 1,
    '"one anchor keeps a commit-pinned raw fallback catalog"': 1,
    '"one anchor keeps a commit-pinned raw fallback map"': 1,
    '"two anchors remain shared-tree-only fallback reads"': 1,
    '"PHASE12_SHARED_TREE_READBACK_ROOT_COUNT=4"': 1,
}

EXPECTED_SHARED_TREE_READBACK_ROOTS = [
    "https://github.com/adybag14-cyber/Zigux/tree/master/drivers/net",
    "https://github.com/adybag14-cyber/Zigux/tree/master/tools/lib/bpf",
    "https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux",
    "https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests",
]

EXPECTED_ANCHORS = {
    "virtio_net": {
        "anchor": "drivers/net/virtio_net.c",
        "roadmap_destination": "drivers/net/virtio_net.zig",
        "survey_note_path": "Documentation/zigux/phase12-virtio-net-survey.md",
        "public_read_status": "shared_tree_only",
        "raw_fallback_catalog_path": "",
        "raw_fallback_map_path": "",
    },
    "nvme_pci": {
        "anchor": "drivers/nvme/host/pci.c",
        "roadmap_destination": "drivers/nvme/host/pci.zig",
        "survey_note_path": "Documentation/zigux/phase12-nvme-pci-survey.md",
        "public_read_status": "commit_pinned_raw_map",
        "raw_fallback_catalog_path": "",
        "raw_fallback_map_path": "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
    },
    "virtio_scsi": {
        "anchor": "drivers/scsi/virtio_scsi.c",
        "roadmap_destination": "drivers/scsi/virtio_scsi.zig",
        "survey_note_path": "Documentation/zigux/phase12-virtio-scsi-survey.md",
        "public_read_status": "commit_pinned_raw_catalog",
        "raw_fallback_catalog_path": "Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md",
        "raw_fallback_map_path": "",
    },
    "libbpf": {
        "anchor": "tools/lib/bpf/libbpf.c",
        "roadmap_destination": "tools/lib/bpf/zigux_segments/",
        "survey_note_path": "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "public_read_status": "shared_tree_only",
        "raw_fallback_catalog_path": "",
        "raw_fallback_map_path": "",
    },
}


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_manifest() -> dict[str, object]:
    return json.loads(read_text("zigux/tests/phase12_raw_github_coverage_manifest.json"))


def collect_exact_count_misses(text: str, expected_counts: dict[str, int], prefix: str) -> list[str]:
    missing: list[str] = []
    for marker, expected_count in expected_counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(f"{prefix}:{marker}:expected={expected_count}:actual={actual_count}")
    return missing


def validate_manifest(manifest: dict[str, object]) -> list[str]:
    missing: list[str] = []

    expected_scalars = {
        "lane_key": "P12-L07",
        "phase": "Phase 12",
        "scope": "raw GitHub fallback catalog survey public-read coverage gaps vs roadmap",
        "public_read_boundary": "read_only_public_github_tree_and_raw_paths_only",
        "last_replayed_public_head": "bc2373f7deedf021c73beaae29555a9ac6b0536d",
        "roadmap_anchor_count": 4,
        "commit_pinned_raw_fallback_catalog_count": 1,
        "commit_pinned_raw_fallback_map_count": 1,
        "shared_tree_only_anchor_count": 2,
        "shared_tree_readback_root_count": 4,
    }
    for key, value in expected_scalars.items():
        if manifest.get(key) != value:
            missing.append(f"manifest:{key}")

    readback_roots = manifest.get("shared_tree_readback_roots")
    if readback_roots != EXPECTED_SHARED_TREE_READBACK_ROOTS:
        missing.append("manifest:shared_tree_readback_roots")

    anchors = manifest.get("anchors")
    if not isinstance(anchors, list) or len(anchors) != 4:
        missing.append("manifest:anchors")
        return missing

    actual_ids: set[str] = set()
    for anchor in anchors:
        if not isinstance(anchor, dict):
            missing.append("manifest:anchor_shape")
            continue
        anchor_id = anchor.get("id")
        if not isinstance(anchor_id, str) or anchor_id not in EXPECTED_ANCHORS:
            missing.append("manifest:anchor_id")
            continue
        actual_ids.add(anchor_id)
        expected = EXPECTED_ANCHORS[anchor_id]
        for key, value in expected.items():
            if anchor.get(key) != value:
                missing.append(f"manifest:{anchor_id}:{key}")

    if actual_ids != set(EXPECTED_ANCHORS):
        missing.append("manifest:anchor_set")

    return missing


def validate_markers() -> list[str]:
    missing: list[str] = []
    make_text = read_text("zigux/Makefile")
    survey_text = read_text("Documentation/zigux/phase12-raw-github-coverage-survey.md")
    docs_root_text = read_text("Documentation/zigux/README.md")
    release_text = read_text("Documentation/zigux/phase12-release-readiness-survey.md")
    checklist_text = read_text("Documentation/zigux/review-checklist.md")
    test_text = read_text("zigux/tests/phase12_raw_github_coverage_survey.zig")
    raw_catalog_text = read_text("Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md")
    raw_map_text = read_text("Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md")

    for marker in MAKE_MARKERS:
        if marker not in make_text:
            missing.append(f"make:{marker}")
    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            missing.append(f"survey:{marker}")
    missing.extend(collect_exact_count_misses(survey_text, SURVEY_EXACT_COUNT_MARKERS, "survey_count"))
    for marker in DOCS_ROOT_MARKERS:
        if marker not in docs_root_text:
            missing.append(f"docs_root:{marker}")
    for marker in RELEASE_MARKERS:
        if marker not in release_text:
            missing.append(f"release:{marker}")
    missing.extend(collect_exact_count_misses(release_text, RELEASE_EXACT_COUNT_MARKERS, "release_count"))
    for marker in CHECKLIST_MARKERS:
        if marker not in checklist_text:
            missing.append(f"checklist:{marker}")
    missing.extend(collect_exact_count_misses(checklist_text, CHECKLIST_EXACT_COUNT_MARKERS, "checklist_count"))
    for marker in TEST_MARKERS:
        if marker not in test_text:
            missing.append(f"test:{marker}")
    missing.extend(collect_exact_count_misses(test_text, TEST_EXACT_COUNT_MARKERS, "test_count"))

    if "Phase 12 Virtio SCSI Raw GitHub Fallback Catalog" not in raw_catalog_text:
        missing.append("raw_catalog:title")
    if "PHASE12_SURVEYED_COMMIT=8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1" not in raw_map_text:
        missing.append("raw_map:surveyed_commit")

    return missing


def validate_tree() -> list[str]:
    missing_files = [path for path in FILES if not (ROOT / path).is_file()]
    if missing_files:
        return [f"missing_file:{path}" for path in missing_files]

    missing = []
    missing.extend(validate_manifest(load_manifest()))
    missing.extend(validate_markers())
    return missing


def expect_missing(label: str, items: list[str], expected: str) -> None:
    if expected not in items:
        actual = ",".join(items) if items else "none"
        raise SystemExit(
            f"phase12-raw-github-coverage:self-test:{label}:expected_missing:{expected}:actual:{actual}"
        )


def run_self_test() -> int:
    baseline = validate_tree()
    if baseline:
        raise SystemExit(
            "phase12-raw-github-coverage:self-test:baseline_failed:"
            + ",".join(baseline)
        )

    manifest = load_manifest()
    manifest["lane_key"] = "P12-L99"
    expect_missing("lane_key", validate_manifest(manifest), "manifest:lane_key")

    drifted_manifest = json.loads(json.dumps(load_manifest()))
    for anchor in drifted_manifest["anchors"]:
        if anchor.get("id") == "libbpf":
            anchor["public_read_status"] = "commit_pinned_raw_catalog"
            break
    expect_missing(
        "manifest_anchor_status",
        validate_manifest(drifted_manifest),
        "manifest:libbpf:public_read_status",
    )

    survey_path = ROOT / "Documentation/zigux/phase12-raw-github-coverage-survey.md"
    original_survey = survey_path.read_text(encoding="utf-8")
    survey_path.write_text(
        original_survey.replace(
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
            "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map-drift.md",
            1,
        ),
        encoding="utf-8",
    )
    try:
        expect_missing(
            "survey_marker",
            validate_tree(),
            "survey:Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md",
        )
    finally:
        survey_path.write_text(original_survey, encoding="utf-8")

    make_path = ROOT / "zigux/Makefile"
    original_make = make_path.read_text(encoding="utf-8")
    make_path.write_text(
        original_make.replace(
            "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-raw-github-coverage.py\n",
            "",
            1,
        ),
        encoding="utf-8",
    )
    try:
        expect_missing(
            "make_marker",
            validate_tree(),
            "make:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase12-raw-github-coverage.py\n",
        )
    finally:
        make_path.write_text(original_make, encoding="utf-8")

    raw_map_path = ROOT / "Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md"
    original_raw_map = raw_map_path.read_text(encoding="utf-8")
    raw_map_path.write_text(
        original_raw_map.replace(
            "PHASE12_SURVEYED_COMMIT=8b69e4dfd04553afeb08c0ecbf3060f800e7ecd1",
            "PHASE12_SURVEYED_COMMIT=8B69E4DFD04553AFEB08C0ECBF3060F800E7ECD1",
            1,
        ),
        encoding="utf-8",
    )
    try:
        expect_missing(
            "raw_map_surveyed_commit",
            validate_tree(),
            "raw_map:surveyed_commit",
        )
    finally:
        raw_map_path.write_text(original_raw_map, encoding="utf-8")

    release_path = ROOT / "Documentation/zigux/phase12-release-readiness-survey.md"
    original_release = release_path.read_text(encoding="utf-8")
    release_path.unlink()
    try:
        expect_missing(
            "missing_release_file",
            validate_tree(),
            "missing_file:Documentation/zigux/phase12-release-readiness-survey.md",
        )
    finally:
        release_path.write_text(original_release, encoding="utf-8")

    release_path.write_text(
        original_release.replace(
            "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
            "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=3",
            1,
        ),
        encoding="utf-8",
    )
    try:
        expect_missing(
            "release_marker",
            validate_tree(),
            "release:PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2",
        )
    finally:
        release_path.write_text(original_release, encoding="utf-8")

    survey_path.write_text(
        original_survey
        + "two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`\n",
        encoding="utf-8",
    )
    try:
        expect_missing(
            "survey_exact_count",
            validate_tree(),
            "survey_count:two anchors remain shared-tree-only fallback reads: `virtio_net` and `libbpf`:expected=1:actual=2",
        )
    finally:
        survey_path.write_text(original_survey, encoding="utf-8")

    release_path.write_text(
        original_release + "PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2\n",
        encoding="utf-8",
    )
    try:
        expect_missing(
            "release_exact_count",
            validate_tree(),
            "release_count:PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2:expected=1:actual=2",
        )
    finally:
        release_path.write_text(original_release, encoding="utf-8")

    checklist_path = ROOT / "Documentation/zigux/review-checklist.md"
    original_checklist = checklist_path.read_text(encoding="utf-8")
    checklist_path.write_text(
        original_checklist.replace(
            "including the current one commit-pinned raw catalog, one archival raw map, and two shared-tree-only anchors",
            "including the current one commit-pinned raw catalog, one archival raw map, and one shared-tree-only anchor",
            1,
        ),
        encoding="utf-8",
    )
    try:
        expect_missing(
            "checklist_marker",
            validate_tree(),
            "checklist:including the current one commit-pinned raw catalog, one archival raw map, and two shared-tree-only anchors",
        )
    finally:
        checklist_path.write_text(original_checklist, encoding="utf-8")

    checklist_path.write_text(
        original_checklist
        + "including the current one commit-pinned raw catalog, one archival raw map, and two shared-tree-only anchors\n",
        encoding="utf-8",
    )
    try:
        expect_missing(
            "checklist_exact_count",
            validate_tree(),
            "checklist_count:including the current one commit-pinned raw catalog, one archival raw map, and two shared-tree-only anchors:expected=1:actual=2",
        )
    finally:
        checklist_path.write_text(original_checklist, encoding="utf-8")

    test_path = ROOT / "zigux/tests/phase12_raw_github_coverage_survey.zig"
    original_test = test_path.read_text(encoding="utf-8")
    test_path.write_text(
        original_test + '"two anchors remain shared-tree-only fallback reads"\n',
        encoding="utf-8",
    )
    try:
        expect_missing(
            "test_exact_count",
            validate_tree(),
            'test_count:"two anchors remain shared-tree-only fallback reads":expected=1:actual=2',
        )
    finally:
        test_path.write_text(original_test, encoding="utf-8")

    print("PHASE12_RAW_GITHUB_COVERAGE_SELF_TEST=pass")
    print("PHASE12_RAW_GITHUB_COVERAGE_SELF_TEST_CASE_COUNT=12")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--self-test" in args:
        return run_self_test()

    missing = validate_tree()
    if missing:
        print("PHASE12_RAW_GITHUB_COVERAGE=fail")
        print("PHASE12_RAW_GITHUB_COVERAGE_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE12_RAW_GITHUB_COVERAGE_MISSING_END")
        return 1

    manifest = load_manifest()
    anchors = manifest["anchors"]
    shared_tree_only = sum(
        1 for anchor in anchors if anchor["public_read_status"] == "shared_tree_only"
    )
    commit_pinned = len(anchors) - shared_tree_only

    print("PHASE12_RAW_GITHUB_COVERAGE=pass")
    print(f"PHASE12_RAW_GITHUB_COVERAGE_ANCHOR_COUNT={len(anchors)}")
    print(f"PHASE12_RAW_GITHUB_COVERAGE_SHARED_TREE_ONLY_COUNT={shared_tree_only}")
    print(f"PHASE12_RAW_GITHUB_COVERAGE_COMMIT_PINNED_COUNT={commit_pinned}")
    print(f"PHASE12_RAW_GITHUB_COVERAGE_SHARED_TREE_ROOT_COUNT={manifest['shared_tree_readback_root_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

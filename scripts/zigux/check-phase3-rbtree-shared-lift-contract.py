#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from validate_phase3_core import PHASE3_SHARED_RBTREE_RECORD_MARKERS


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-rbtree-interop-survey.md"
ROADMAP_GAP_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"
SLICE_REL = "Documentation/zigux/phase3-rbtree-slice.md"
ABI_SLICE_REL = "Documentation/zigux/phase3-abi-slice.md"
REVIEW_CHECKLIST_REL = "Documentation/zigux/review-checklist.md"
DEDICATED_EXPECTED_REL = "zigux/tests/fixtures/phase3_rbtree/expected.json"
DEDICATED_HEADER_REL = "include/zigux/rbtree.h"
DEDICATED_BINDING_REL = "zigux/bindings/rbtree.zig"
SHARED_ABI_HEADER_REL = "include/zigux/abi.h"
SHARED_ABI_BINDING_REL = "zigux/bindings/abi.zig"
SHARED_ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
SHARED_ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
SHARED_ABI_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"
SHARED_ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
SHARED_CONTRACT_REL = "zigux/tests/phase3_rbtree_shared_contract.zig"
SHARED_CONTRACT_CHECK_REL = "scripts/zigux/check-phase3-rbtree-shared-lift-contract.py"
SHARED_SURVEY_VALIDATE_REL = "scripts/zigux/validate-phase3-rbtree-interop-survey.py"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"

SURVEY_MARKERS = (
    "PHASE3_RBTREE_SHARED_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet",
    "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid",
    "PHASE3_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig",
    "PHASE3_RBTREE_SHARED_PACKET_CATALOG=phase3_abi_manifest-catalogs-dedicated-rbtree-boundary-plus-shared-replay-and-lift-guards",
)

SURVEY_SNIPPETS = (
    "the shared Phase 3 ABI packet already replays `zigux_rbtree_root_view`",
    "shared replay, shared manifest catalog, and shared-lift note aligned before the shared ABI packet grows",
)

ROADMAP_MARKERS = (
    "PHASE3_CURRENT_SHARED_RBTREE_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_CURRENT_RBTREE_SHARED_LAYOUT_CONTRACT=shared-phase3-abi-replay-already-reuses-dedicated-rbtree-layout-shared-header-lift-still-missing",
    "PHASE3_CURRENT_RBTREE_SHARED_CATALOG=phase3-abi-manifest-catalogs-shared-rbtree-replay-and-lift-guards",
)

ROADMAP_SNIPPETS = (
    "the shared ABI replay already covers `zigux_rbtree_root_view`",
    "reuse the dedicated `zigux_rbtree_root_view` layout and flag constants unchanged",
    "the shared ABI manifest now also catalogs that shared replay and its lift guards",
)

SLICE_MARKERS = (
    "PHASE3_RBTREE_SHARED_BOUNDARY_STATUS=shared-parity-replay-present-shared-root-view-lift-still-missing",
    "PHASE3_RBTREE_SHARED_BOUNDARY_GAP=shared-abi-root-view-lift-still-missing",
    "PHASE3_RBTREE_SHARED_BOUNDARY_GUARDS=scripts/zigux/check-phase3-abi-layout-packet.py,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
)

SLICE_SNIPPETS = (
    "shared Phase 3 ABI parity replay that still reuses the dedicated `rbtree` header and Zig binding",
    "the shared ABI manifest now catalogs both that dedicated packet and the shared ABI replay plus the lift guards",
    "a shared `rbtree` record in `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "a shared Phase 3 ABI root-view implementation that no longer depends on `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig`",
)

ABI_SLICE_SNIPPETS = (
    "the shared ABI replay also already covers `zigux_rbtree_root_view` through `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`",
    "it still reaches that record through `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig` rather than a curated shared `include/zigux/abi.h` plus `zigux/bindings/abi.zig` lift",
    "closing the still-missing curated shared `rbtree` root-view lift inside `include/zigux/abi.h` and `zigux/bindings/abi.zig` before adding still more chrdev tail growth",
)

REVIEW_CHECKLIST_SNIPPETS = (
    "`include/zigux/abi.h`",
    "`zigux/bindings/abi.zig`",
    "`zigux/tests/phase3_abi.zig`",
    "`zigux/tests/fixtures/phase3_abi/expected.json`",
)

STALE_SLICE_SNIPPETS = (
    "PHASE3_RBTREE_SHARED_BOUNDARY_STATUS=shared-root-view-lift-landed",
    "This slice already carries both the dedicated `rbtree` boundary packet and the first shared root-view lift into the canonical Phase 3 ABI packet.",
)

DEDICATED_HEADER_TOKENS = (
    "#define ZIGUX_RBTREE_ROOT_FLAG_EMPTY 1U",
    "#define ZIGUX_RBTREE_ROOT_FLAG_CACHED 2U",
    "#define ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID 4U",
    "struct zigux_rbtree_root_view {",
)

DEDICATED_BINDING_TOKENS = (
    "pub const ROOT_FLAG_EMPTY: u32 = 1;",
    "pub const ROOT_FLAG_CACHED: u32 = 2;",
    "pub const ROOT_FLAG_LEFTMOST_VALID: u32 = 4;",
    "pub const RootView = extern struct {",
)

SHARED_CONTRACT_PREFIX_SNIPPETS = (
    "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT",
    "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT",
    "PHASE3_RBTREE_SHARED_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root",
)

SHARED_RECORD_EMPTY_DETAIL_SNIPPETS = (
    "try std.testing.expectEqual(@as(usize, 0), empty_root.root_addr);",
    "try std.testing.expectEqual(@as(usize, 0), empty_root.leftmost_addr);",
    "try std.testing.expectEqual(@as(u32, rbtree.ROOT_FLAG_EMPTY), empty_root.flags);",
    "try std.testing.expectEqual(@as(u32, 0), empty_root.reserved);",
)

SHARED_RECORD_EMPTY_PRESENCE_SNIPPETS = (
    "try std.testing.expect(rbtree.isValid(empty_root));",
    "try std.testing.expect(rbtree.isEmpty(empty_root));",
    "try std.testing.expect(!rbtree.isCached(empty_root));",
    "try std.testing.expect(!rbtree.hasLeftmost(empty_root));",
    "try std.testing.expect(rbtree.isCanonical(empty_root));",
)

SHARED_RECORD_CACHED_DETAIL_SNIPPETS = (
    "try std.testing.expectEqual(@as(usize, 0x2000), cached_root.root_addr);",
    "try std.testing.expectEqual(@as(usize, 0x1800), cached_root.leftmost_addr);",
    "try std.testing.expectEqual(@as(u32, rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID), cached_root.flags);",
    "try std.testing.expectEqual(@as(u32, 0), cached_root.reserved);",
)

SHARED_RECORD_CACHED_PRESENCE_SNIPPETS = (
    "try std.testing.expect(rbtree.isValid(cached_root));",
    "try std.testing.expect(!rbtree.isEmpty(cached_root));",
    "try std.testing.expect(rbtree.isCached(cached_root));",
    "try std.testing.expect(rbtree.hasLeftmost(cached_root));",
    "try std.testing.expect(rbtree.isCanonical(cached_root));",
)

SHARED_RECORD_UNCACHED_DETAIL_SNIPPETS = (
    "try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);",
    "try std.testing.expectEqual(@as(usize, 0), uncached_root.leftmost_addr);",
    "try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);",
    "try std.testing.expectEqual(@as(u32, 0), uncached_root.reserved);",
)

SHARED_RECORD_UNCACHED_PRESENCE_SNIPPETS = (
    "try std.testing.expect(rbtree.isValid(uncached_root));",
    "try std.testing.expect(!rbtree.isEmpty(uncached_root));",
    "try std.testing.expect(!rbtree.isCached(uncached_root));",
    "try std.testing.expect(!rbtree.hasLeftmost(uncached_root));",
    "try std.testing.expect(rbtree.isCanonical(uncached_root));",
)

SHARED_CONTRACT_SNIPPETS = (
    *SHARED_CONTRACT_PREFIX_SNIPPETS,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[0],
    *SHARED_RECORD_EMPTY_DETAIL_SNIPPETS,
    *SHARED_RECORD_EMPTY_PRESENCE_SNIPPETS,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[1],
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[2],
    *SHARED_RECORD_CACHED_DETAIL_SNIPPETS,
    *SHARED_RECORD_CACHED_PRESENCE_SNIPPETS,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[3],
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[4],
    *SHARED_RECORD_UNCACHED_DETAIL_SNIPPETS,
    *SHARED_RECORD_UNCACHED_PRESENCE_SNIPPETS,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[5],
)

SHARED_ABI_TEST_PREFIX_SNIPPETS = (
    'const rbtree = @import("rbtree_bindings");',
    "layout_assert.assertRbtreeRootViewLayout();",
)

SHARED_ABI_TEST_EMPTY_DETAIL_SNIPPETS = SHARED_RECORD_EMPTY_DETAIL_SNIPPETS
SHARED_ABI_TEST_EMPTY_PRESENCE_SNIPPETS = SHARED_RECORD_EMPTY_PRESENCE_SNIPPETS
SHARED_ABI_TEST_CACHED_DETAIL_SNIPPETS = SHARED_RECORD_CACHED_DETAIL_SNIPPETS
SHARED_ABI_TEST_CACHED_PRESENCE_SNIPPETS = SHARED_RECORD_CACHED_PRESENCE_SNIPPETS
SHARED_ABI_TEST_UNCACHED_DETAIL_SNIPPETS = (
    "try std.testing.expectEqual(@as(usize, 0x2400), uncached_root.root_addr);",
    "try std.testing.expectEqual(@as(usize, 0), uncached_root.leftmost_addr);",
    "try std.testing.expectEqual(@as(u32, 0), uncached_root.flags);",
    "try std.testing.expectEqual(@as(u32, 0), uncached_root.reserved);",
)

SHARED_ABI_TEST_UNCACHED_PRESENCE_SNIPPETS = SHARED_RECORD_UNCACHED_PRESENCE_SNIPPETS

SHARED_ABI_TEST_SNIPPETS = (
    *SHARED_ABI_TEST_PREFIX_SNIPPETS,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[0],
    *SHARED_ABI_TEST_EMPTY_DETAIL_SNIPPETS,
    *SHARED_ABI_TEST_EMPTY_PRESENCE_SNIPPETS,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[1],
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[2],
    *SHARED_ABI_TEST_CACHED_DETAIL_SNIPPETS,
    *SHARED_ABI_TEST_CACHED_PRESENCE_SNIPPETS,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[3],
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[4],
    *SHARED_ABI_TEST_UNCACHED_DETAIL_SNIPPETS,
    *SHARED_ABI_TEST_UNCACHED_PRESENCE_SNIPPETS,
    PHASE3_SHARED_RBTREE_RECORD_MARKERS[5],
)

SHARED_PACKET_SNIPPETS = {
    SHARED_ABI_TEST_REL: SHARED_ABI_TEST_SNIPPETS,
    SHARED_ABI_DUMP_REL: (
        'const rbtree = @import("rbtree_bindings");',
        'writeStructLayout(writer, "zigux_rbtree_root_view", rbtree.RootView, false);',
        'try writer.writeAll("},\\\"records\\\":{\\\"rbtree_empty_root\\\":{\\\"root_addr\\\":");',
        'try writer.writeAll(",\\\"reserved\\\":0},\\\"rbtree_cached_leftmost_root\\\":{\\\"root_addr\\\":");',
        'try writer.writeAll(",\\\"reserved\\\":0},\\\"rbtree_uncached_root\\\":{\\\"root_addr\\\":");',
    ),
    SHARED_ABI_HARNESS_REL: (
        "#include <zigux/rbtree.h>",
        "offsetof(struct zigux_rbtree_root_view, root_addr)",
        'fputs("},\\\"records\\\":{\\\"rbtree_empty_root\\\":{\\\"root_addr\\\":", stdout);',
        'fputs(",\\\"reserved\\\":0},\\\"rbtree_cached_leftmost_root\\\":{\\\"root_addr\\\":", stdout);',
        'fputs(",\\\"reserved\\\":0},\\\"rbtree_uncached_root\\\":{\\\"root_addr\\\":", stdout);',
    ),
    SHARED_ABI_EXPECTED_REL: (
        '"rbtree_empty_root":{"root_addr":0,"leftmost_addr":0,"flags":1,"reserved":0}',
        '"rbtree_cached_leftmost_root":{"root_addr":8192,"leftmost_addr":6144,"flags":6,"reserved":0}',
        '"rbtree_uncached_root":{"root_addr":9216,"leftmost_addr":0,"flags":0,"reserved":0}',
        '"zigux_rbtree_root_view":{"size":24,"align":8,"offsets":{"root_addr":0,"leftmost_addr":8,"flags":16,"reserved":20}}',
    ),
}

SHARED_PACKET_EXACT_ONCE_SNIPPETS = {
    SHARED_CONTRACT_REL: (
        "PHASE3_RBTREE_SHARED_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root",
        *PHASE3_SHARED_RBTREE_RECORD_MARKERS,
    ),
    SHARED_ABI_TEST_REL: (
        "// PHASE3_SHARED_RBTREE_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root",
        *PHASE3_SHARED_RBTREE_RECORD_MARKERS,
    ),
    SHARED_ABI_DUMP_REL: (
        'writeStructLayout(writer, "zigux_rbtree_root_view", rbtree.RootView, false);',
        'try writer.writeAll("},\\\"records\\\":{\\\"rbtree_empty_root\\\":{\\\"root_addr\\\":");',
        'try writer.writeAll(",\\\"reserved\\\":0},\\\"rbtree_cached_leftmost_root\\\":{\\\"root_addr\\\":");',
        'try writer.writeAll(",\\\"reserved\\\":0},\\\"rbtree_uncached_root\\\":{\\\"root_addr\\\":");',
    ),
    SHARED_ABI_HARNESS_REL: (
        "offsetof(struct zigux_rbtree_root_view, root_addr)",
        'fputs("},\\\"records\\\":{\\\"rbtree_empty_root\\\":{\\\"root_addr\\\":", stdout);',
        'fputs(",\\\"reserved\\\":0},\\\"rbtree_cached_leftmost_root\\\":{\\\"root_addr\\\":", stdout);',
        'fputs(",\\\"reserved\\\":0},\\\"rbtree_uncached_root\\\":{\\\"root_addr\\\":", stdout);',
    ),
    SHARED_ABI_EXPECTED_REL: (
        '"zigux_rbtree_root_view":{"size":24,"align":8,"offsets":{"root_addr":0,"leftmost_addr":8,"flags":16,"reserved":20}}',
        '"rbtree_empty_root":{"root_addr":0,"leftmost_addr":0,"flags":1,"reserved":0}',
        '"rbtree_cached_leftmost_root":{"root_addr":8192,"leftmost_addr":6144,"flags":6,"reserved":0}',
        '"rbtree_uncached_root":{"root_addr":9216,"leftmost_addr":0,"flags":0,"reserved":0}',
    ),
}

SHARED_ABI_FORBIDDEN = {
    SHARED_ABI_HEADER_REL: (
        "ZIGUX_RBTREE_ROOT_FLAG_EMPTY",
        "struct zigux_rbtree_root_view",
    ),
    SHARED_ABI_BINDING_REL: (
        "pub const ROOT_FLAG_EMPTY: u32 = 1;",
        "pub const RootView = extern struct {",
    ),
}

SHARED_CONTRACT_SELF_TEST_SNIPPETS = (
    *PHASE3_SHARED_RBTREE_RECORD_MARKERS,
    *SHARED_RECORD_EMPTY_DETAIL_SNIPPETS,
    *SHARED_RECORD_EMPTY_PRESENCE_SNIPPETS,
    *SHARED_RECORD_CACHED_DETAIL_SNIPPETS,
    *SHARED_RECORD_CACHED_PRESENCE_SNIPPETS,
    *SHARED_RECORD_UNCACHED_DETAIL_SNIPPETS,
    *SHARED_RECORD_UNCACHED_PRESENCE_SNIPPETS,
)

SHARED_PACKET_SELF_TEST_CASES = (
    *((SHARED_ABI_TEST_REL, snippet) for snippet in (
        *PHASE3_SHARED_RBTREE_RECORD_MARKERS,
        *SHARED_ABI_TEST_EMPTY_DETAIL_SNIPPETS,
        *SHARED_ABI_TEST_EMPTY_PRESENCE_SNIPPETS,
        *SHARED_ABI_TEST_CACHED_DETAIL_SNIPPETS,
        *SHARED_ABI_TEST_CACHED_PRESENCE_SNIPPETS,
        *SHARED_ABI_TEST_UNCACHED_DETAIL_SNIPPETS,
        *SHARED_ABI_TEST_UNCACHED_PRESENCE_SNIPPETS,
    )),
    (SHARED_ABI_DUMP_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_DUMP_REL][1]),
    (SHARED_ABI_DUMP_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_DUMP_REL][2]),
    (SHARED_ABI_DUMP_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_DUMP_REL][3]),
    (SHARED_ABI_DUMP_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_DUMP_REL][4]),
    (SHARED_ABI_HARNESS_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_HARNESS_REL][1]),
    (SHARED_ABI_HARNESS_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_HARNESS_REL][2]),
    (SHARED_ABI_HARNESS_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_HARNESS_REL][3]),
    (SHARED_ABI_HARNESS_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_HARNESS_REL][4]),
    (SHARED_ABI_EXPECTED_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_EXPECTED_REL][0]),
    (SHARED_ABI_EXPECTED_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_EXPECTED_REL][1]),
    (SHARED_ABI_EXPECTED_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_EXPECTED_REL][2]),
    (SHARED_ABI_EXPECTED_REL, SHARED_PACKET_SNIPPETS[SHARED_ABI_EXPECTED_REL][3]),
)

SHARED_PACKET_EXACT_ONCE_SELF_TEST_CASES = tuple(
    (rel, snippet)
    for rel, snippets in SHARED_PACKET_EXACT_ONCE_SNIPPETS.items()
    for snippet in snippets
)

MANIFEST_PATHS = (
    "include/zigux/rbtree.h",
    "zigux/bindings/rbtree.zig",
    "zigux/tests/phase3_rbtree_dump.zig",
    "zigux/tests/phase3_rbtree_survey.zig",
    "zigux/tests/phase3_rbtree_manifest.json",
    "zigux/tests/phase3_rbtree_shared_contract.zig",
    "zigux/tests/fixtures/phase3_rbtree/expected.json",
    "zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase3-rbtree-slice.md",
    "Documentation/zigux/phase3-rbtree-interop-survey.md",
    "scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
    "scripts/zigux/validate-phase3-rbtree-interop-survey.py",
)

EXPECTED_CONSTANTS = {
    "root_flag_empty": 1,
    "root_flag_cached": 2,
    "root_flag_leftmost_valid": 4,
}
EXPECTED_LAYOUT = {
    "size": 24,
    "align": 8,
    "offsets": {"root_addr": 0, "leftmost_addr": 8, "flags": 16, "reserved": 20},
}


def read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def require_contains(text: str, rel: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{rel}:{snippet}")


def require_absent(text: str, rel: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet in text:
            issues.append(f"{prefix}:{rel}:{snippet}")


def require_exact_count(
    text: str, rel: str, snippets: tuple[str, ...], expected_count: int, prefix: str, issues: list[str]
) -> None:
    for snippet in snippets:
        count = text.count(snippet)
        if count != expected_count:
            issues.append(f"{prefix}:{rel}:{expected_count}:{count}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = read_text(root, SURVEY_REL, issues)
    roadmap = read_text(root, ROADMAP_GAP_REL, issues)
    slice_text = read_text(root, SLICE_REL, issues)
    abi_slice = read_text(root, ABI_SLICE_REL, issues)
    review_checklist = read_text(root, REVIEW_CHECKLIST_REL, issues)
    header = read_text(root, DEDICATED_HEADER_REL, issues)
    binding = read_text(root, DEDICATED_BINDING_REL, issues)
    shared_contract = read_text(root, SHARED_CONTRACT_REL, issues)
    manifest = read_text(root, MANIFEST_REL, issues)
    expected_text = read_text(root, DEDICATED_EXPECTED_REL, issues)

    require_contains(survey, SURVEY_REL, SURVEY_MARKERS, "missing_marker", issues)
    require_contains(survey, SURVEY_REL, SURVEY_SNIPPETS, "missing_snippet", issues)
    require_contains(roadmap, ROADMAP_GAP_REL, ROADMAP_MARKERS, "missing_marker", issues)
    require_contains(roadmap, ROADMAP_GAP_REL, ROADMAP_SNIPPETS, "missing_snippet", issues)
    require_contains(slice_text, SLICE_REL, SLICE_MARKERS, "missing_marker", issues)
    require_contains(slice_text, SLICE_REL, SLICE_SNIPPETS, "missing_snippet", issues)
    require_contains(abi_slice, ABI_SLICE_REL, ABI_SLICE_SNIPPETS, "missing_snippet", issues)
    require_contains(
        review_checklist,
        REVIEW_CHECKLIST_REL,
        REVIEW_CHECKLIST_SNIPPETS,
        "missing_checklist_snippet",
        issues,
    )
    require_absent(slice_text, SLICE_REL, STALE_SLICE_SNIPPETS, "stale_snippet", issues)
    require_contains(header, DEDICATED_HEADER_REL, DEDICATED_HEADER_TOKENS, "missing_token", issues)
    require_contains(binding, DEDICATED_BINDING_REL, DEDICATED_BINDING_TOKENS, "missing_token", issues)
    require_contains(shared_contract, SHARED_CONTRACT_REL, SHARED_CONTRACT_SNIPPETS, "missing_snippet", issues)

    for rel, snippets in SHARED_PACKET_SNIPPETS.items():
        text = read_text(root, rel, issues)
        require_contains(text, rel, snippets, "missing_shared_packet", issues)
        if rel in SHARED_PACKET_EXACT_ONCE_SNIPPETS:
            require_exact_count(
                text,
                rel,
                SHARED_PACKET_EXACT_ONCE_SNIPPETS[rel],
                1,
                "unexpected_shared_packet_count",
                issues,
            )
    for rel, snippets in SHARED_ABI_FORBIDDEN.items():
        require_absent(read_text(root, rel, issues), rel, snippets, "unexpected_shared_lift", issues)

    for rel in MANIFEST_PATHS:
        if f'"{rel}"' not in manifest:
            issues.append(f"missing_manifest_entry:{rel}")

    if expected_text:
        try:
            expected = json.loads(expected_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid_expected_json:{exc.msg}")
        else:
            if expected.get("constants") != EXPECTED_CONSTANTS:
                issues.append(f"unexpected_expected_constants:{expected.get('constants')!r}")
            layout = expected.get("structs", {}).get("zigux_rbtree_root_view")
            if layout != EXPECTED_LAYOUT:
                issues.append(f"unexpected_expected_layout:{layout!r}")

    return issues


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def assert_missing_shared_contract_snippet(root: Path, snippet: str) -> None:
    write(
        root,
        SHARED_CONTRACT_REL,
        "\n".join(item for item in SHARED_CONTRACT_SNIPPETS if item != snippet) + "\n",
    )
    issues = validate(root)
    assert f"missing_snippet:{SHARED_CONTRACT_REL}:{snippet}" in issues


def assert_missing_shared_packet_snippet(root: Path, rel: str, snippet: str) -> None:
    write(root, rel, "\n".join(item for item in SHARED_PACKET_SNIPPETS[rel] if item != snippet) + "\n")
    issues = validate(root)
    assert f"missing_shared_packet:{rel}:{snippet}" in issues


def assert_duplicate_shared_packet_snippet(root: Path, rel: str, snippet: str) -> None:
    write(root, rel, "\n".join((*SHARED_PACKET_SNIPPETS[rel], snippet)) + "\n")
    issues = validate(root)
    assert f"unexpected_shared_packet_count:{rel}:1:2:{snippet}" in issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_shared_lift_") as tmp_dir:
        root = Path(tmp_dir)
        write(root, SURVEY_REL, "\n".join((*SURVEY_MARKERS, *SURVEY_SNIPPETS)) + "\n")
        write(root, ROADMAP_GAP_REL, "\n".join((*ROADMAP_MARKERS, *ROADMAP_SNIPPETS)) + "\n")
        write(root, SLICE_REL, "\n".join((*SLICE_MARKERS, *SLICE_SNIPPETS)) + "\n")
        write(root, ABI_SLICE_REL, "\n".join(ABI_SLICE_SNIPPETS) + "\n")
        write(root, REVIEW_CHECKLIST_REL, "\n".join(REVIEW_CHECKLIST_SNIPPETS) + "\n")
        write(root, DEDICATED_HEADER_REL, "\n".join(DEDICATED_HEADER_TOKENS) + "\n")
        write(root, DEDICATED_BINDING_REL, "\n".join(DEDICATED_BINDING_TOKENS) + "\n")
        write(root, SHARED_CONTRACT_REL, "\n".join(SHARED_CONTRACT_SNIPPETS) + "\n")
        for rel, snippets in SHARED_PACKET_SNIPPETS.items():
            write(root, rel, "\n".join(snippets) + "\n")
        for rel in SHARED_ABI_FORBIDDEN:
            write(root, rel, "// clean\n")
        write(root, MANIFEST_REL, json.dumps({"files": list(MANIFEST_PATHS)}))
        write(
            root,
            DEDICATED_EXPECTED_REL,
            json.dumps({"constants": EXPECTED_CONSTANTS, "structs": {"zigux_rbtree_root_view": EXPECTED_LAYOUT}}),
        )
        assert validate(root) == []

        write(root, SHARED_CONTRACT_REL, "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT\n")
        issues = validate(root)
        assert any(
            issue.startswith(f"missing_snippet:{SHARED_CONTRACT_REL}:PHASE3_RBTREE_SHARED_SAMPLE_RECORDS=")
            for issue in issues
        )

        for snippet in SHARED_CONTRACT_SELF_TEST_SNIPPETS:
            assert_missing_shared_contract_snippet(root, snippet)

        for rel, snippet in SHARED_PACKET_SELF_TEST_CASES:
            assert_missing_shared_packet_snippet(root, rel, snippet)

        for rel, snippet in SHARED_PACKET_EXACT_ONCE_SELF_TEST_CASES:
            write(root, rel, "\n".join(SHARED_PACKET_SNIPPETS[rel]) + "\n")
            assert_duplicate_shared_packet_snippet(root, rel, snippet)

        write(root, SHARED_ABI_TEST_REL, "\n".join(SHARED_PACKET_SNIPPETS[SHARED_ABI_TEST_REL]) + "\n")
        write(root, SHARED_ABI_DUMP_REL, "\n".join(SHARED_PACKET_SNIPPETS[SHARED_ABI_DUMP_REL]) + "\n")
        write(root, SHARED_ABI_HARNESS_REL, "\n".join(SHARED_PACKET_SNIPPETS[SHARED_ABI_HARNESS_REL]) + "\n")
        write(root, SHARED_ABI_EXPECTED_REL, "\n".join(SHARED_PACKET_SNIPPETS[SHARED_ABI_EXPECTED_REL]) + "\n")
        write(root, ABI_SLICE_REL, ABI_SLICE_SNIPPETS[0] + "\n")
        issues = validate(root)
        assert any(issue.startswith(f"missing_snippet:{ABI_SLICE_REL}:") for issue in issues)

        write(root, ABI_SLICE_REL, "\n".join(ABI_SLICE_SNIPPETS) + "\n")
        write(root, REVIEW_CHECKLIST_REL, "`include/zigux/abi.h`\n")
        issues = validate(root)
        assert any(issue.startswith("missing_checklist_snippet:") for issue in issues)

        write(root, REVIEW_CHECKLIST_REL, "\n".join(REVIEW_CHECKLIST_SNIPPETS) + "\n")
        write(root, SLICE_REL, STALE_SLICE_SNIPPETS[0] + "\n")
        issues = validate(root)
        assert any(issue.startswith("stale_snippet:") for issue in issues)

        write(root, SLICE_REL, "\n".join((*SLICE_MARKERS, *SLICE_SNIPPETS)) + "\n")
        write(root, SHARED_ABI_BINDING_REL, SHARED_ABI_FORBIDDEN[SHARED_ABI_BINDING_REL][0] + "\n")
        issues = validate(root)
        assert any(issue.startswith("unexpected_shared_lift:") for issue in issues)

        write(root, SHARED_ABI_BINDING_REL, "// clean\n")
        write(root, MANIFEST_REL, json.dumps({"files": [entry for entry in MANIFEST_PATHS if entry != SHARED_CONTRACT_CHECK_REL]}))
        issues = validate(root)
        assert f"missing_manifest_entry:{SHARED_CONTRACT_CHECK_REL}" in issues

    self_test_case_count = (
        1
        + len(SHARED_CONTRACT_SELF_TEST_SNIPPETS)
        + len(SHARED_PACKET_SELF_TEST_CASES)
        + len(SHARED_PACKET_EXACT_ONCE_SELF_TEST_CASES)
        + 5
    )
    print("PHASE3_RBTREE_SHARED_LIFT_CONTRACT_SELF_TEST=pass")
    print(f"PHASE3_RBTREE_SHARED_LIFT_CONTRACT_SELF_TEST_CASE_COUNT={self_test_case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the planned shared Phase 3 rbtree lift contract stays aligned with the dedicated boundary packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker tests without reading the full repo.")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_RBTREE_SHARED_LIFT_CONTRACT=fail")
        for issue in issues:
            print(issue)
        return 1
    print("PHASE3_RBTREE_SHARED_LIFT_CONTRACT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

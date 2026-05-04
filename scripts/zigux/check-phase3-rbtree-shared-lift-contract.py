#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEDICATED_HEADER_REL = "include/zigux/rbtree.h"
DEDICATED_BINDING_REL = "zigux/bindings/rbtree.zig"
SHARED_ABI_HEADER_REL = "include/zigux/abi.h"
SHARED_ABI_BINDING_REL = "zigux/bindings/abi.zig"
SHARED_CONTRACT_REL = "zigux/tests/phase3_rbtree_shared_contract.zig"
SHARED_ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
SHARED_ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
SHARED_ABI_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"
SHARED_ABI_EXPECTED_REL = "zigux/tests/fixtures/phase3_abi/expected.json"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"

DEDICATED_HEADER_SNIPPETS = (
    "#define ZIGUX_RBTREE_ROOT_FLAG_EMPTY 1U",
    "#define ZIGUX_RBTREE_ROOT_FLAG_CACHED 2U",
    "#define ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID 4U",
    "struct zigux_rbtree_root_view {",
)

DEDICATED_BINDING_SNIPPETS = (
    "pub const ROOT_FLAG_EMPTY: u32 = 1;",
    "pub const ROOT_FLAG_CACHED: u32 = 2;",
    "pub const ROOT_FLAG_LEFTMOST_VALID: u32 = 4;",
    "pub const RootView = extern struct {",
)

SHARED_ABI_HEADER_SNIPPETS = (
    "#define ZIGUX_RBTREE_ROOT_FLAG_EMPTY 1U",
    "#define ZIGUX_RBTREE_ROOT_FLAG_CACHED 2U",
    "#define ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID 4U",
    "struct zigux_rbtree_root_view {",
)

SHARED_ABI_BINDING_SNIPPETS = (
    "pub const RBTREE_ROOT_FLAG_EMPTY: u32 = 1;",
    "pub const RBTREE_ROOT_FLAG_CACHED: u32 = 2;",
    "pub const RBTREE_ROOT_FLAG_LEFTMOST_VALID: u32 = 4;",
    "pub const RbtreeRootView = extern struct {",
)

SHARED_CONTRACT_SNIPPETS = (
    'const abi = @import("abi_bindings");',
    'const rbtree = @import("rbtree_bindings");',
    "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet",
    "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid",
    "PHASE3_RBTREE_SHARED_SAMPLE_RECORDS=empty-root,cached-leftmost-root,uncached-root",
    "fn expectSameRootView(shared: abi.RbtreeRootView, dedicated: rbtree.RootView) !void {",
    "try std.testing.expectEqual(@sizeOf(rbtree.RootView), @sizeOf(abi.RbtreeRootView));",
    "try std.testing.expectEqual(abi.RBTREE_ROOT_FLAG_EMPTY, rbtree.ROOT_FLAG_EMPTY);",
    "try expectSameRootView(empty_root, rbtree.empty());",
)

SHARED_PACKET_SNIPPETS = {
    SHARED_ABI_TEST_REL: (
        "fn isRbtreeEmpty(view: abi.RbtreeRootView) bool {",
        "const empty_root: abi.RbtreeRootView = .{",
        "const cached_root: abi.RbtreeRootView = .{",
        "const uncached_root: abi.RbtreeRootView = .{",
        "try std.testing.expect(isCanonicalRbtreeRootView(uncached_root));",
    ),
    SHARED_ABI_DUMP_REL: (
        'try writer.writeAll("},\\\"records\\\":{\\\"rbtree_empty_root\\\":{\\\"root_addr\\\":");',
        'try writer.writeAll(",\\\"reserved\\\":0},\\\"rbtree_cached_leftmost_root\\\":{\\\"root_addr\\\":");',
        'try writer.writeAll(",\\\"reserved\\\":0},\\\"rbtree_uncached_root\\\":{\\\"root_addr\\\":");',
        'try writeStructLayout(writer, "zigux_rbtree_root_view", abi.RbtreeRootView, false);',
    ),
    SHARED_ABI_HARNESS_REL: (
        'fputs("},\\\"records\\\":{\\\"rbtree_empty_root\\\":{\\\"root_addr\\\":", stdout);',
        'fputs(",\\\"reserved\\\":0},\\\"rbtree_cached_leftmost_root\\\":{\\\"root_addr\\\":", stdout);',
        'fputs(",\\\"reserved\\\":0},\\\"rbtree_uncached_root\\\":{\\\"root_addr\\\":", stdout);',
        '{"zigux_rbtree_root_view", sizeof(struct zigux_rbtree_root_view), _Alignof(struct zigux_rbtree_root_view), ARRAY_SIZE(zigux_rbtree_root_view_fields), zigux_rbtree_root_view_fields},',
    ),
}

MANIFEST_ENTRIES = (
    '"include/zigux/rbtree.h"',
    '"zigux/bindings/rbtree.zig"',
    '"include/zigux/abi.h"',
    '"zigux/bindings/abi.zig"',
    '"zigux/tests/phase3_rbtree_shared_contract.zig"',
    '"zigux/tests/phase3_abi.zig"',
    '"zigux/tests/phase3_abi_dump.zig"',
    '"zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"',
    '"zigux/tests/fixtures/phase3_abi/expected.json"',
    '"scripts/zigux/check-phase3-rbtree-shared-lift-contract.py"',
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _require_contains(text: str, rel: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{rel}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    _require_contains(_read_text(root, DEDICATED_HEADER_REL, issues), DEDICATED_HEADER_REL, DEDICATED_HEADER_SNIPPETS, "missing_dedicated_header_snippet", issues)
    _require_contains(_read_text(root, DEDICATED_BINDING_REL, issues), DEDICATED_BINDING_REL, DEDICATED_BINDING_SNIPPETS, "missing_dedicated_binding_snippet", issues)
    _require_contains(_read_text(root, SHARED_ABI_HEADER_REL, issues), SHARED_ABI_HEADER_REL, SHARED_ABI_HEADER_SNIPPETS, "missing_shared_abi_header_snippet", issues)
    _require_contains(_read_text(root, SHARED_ABI_BINDING_REL, issues), SHARED_ABI_BINDING_REL, SHARED_ABI_BINDING_SNIPPETS, "missing_shared_abi_binding_snippet", issues)
    _require_contains(_read_text(root, SHARED_CONTRACT_REL, issues), SHARED_CONTRACT_REL, SHARED_CONTRACT_SNIPPETS, "missing_shared_contract_snippet", issues)

    for rel, snippets in SHARED_PACKET_SNIPPETS.items():
        _require_contains(_read_text(root, rel, issues), rel, snippets, "missing_shared_packet", issues)

    manifest = _read_text(root, MANIFEST_REL, issues)
    if manifest:
        for entry in MANIFEST_ENTRIES:
            if entry not in manifest:
                issues.append("missing_manifest_entry:" + entry.strip('"'))

    expected_text = _read_text(root, SHARED_ABI_EXPECTED_REL, issues)
    if expected_text:
        try:
            expected = json.loads(expected_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid_expected_json:{exc.msg}")
        else:
            records = expected.get("records", {})
            if records.get("rbtree_empty_root") != {"root_addr": 0, "leftmost_addr": 0, "flags": 1, "reserved": 0}:
                issues.append(f"unexpected_expected_record:rbtree_empty_root:{records.get('rbtree_empty_root')!r}")
            if records.get("rbtree_cached_leftmost_root") != {
                "root_addr": 8192,
                "leftmost_addr": 6144,
                "flags": 6,
                "reserved": 0,
            }:
                issues.append(
                    f"unexpected_expected_record:rbtree_cached_leftmost_root:{records.get('rbtree_cached_leftmost_root')!r}"
                )
            if records.get("rbtree_uncached_root") != {
                "root_addr": 9216,
                "leftmost_addr": 0,
                "flags": 0,
                "reserved": 0,
            }:
                issues.append(
                    f"unexpected_expected_record:rbtree_uncached_root:{records.get('rbtree_uncached_root')!r}"
                )
            layout = expected.get("structs", {}).get("zigux_rbtree_root_view")
            if layout != {"size": 24, "align": 8, "offsets": {"root_addr": 0, "leftmost_addr": 8, "flags": 16, "reserved": 20}}:
                issues.append(f"unexpected_expected_layout:{layout!r}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_shared_lift_") as tmp_dir:
        root = Path(tmp_dir)
        for rel in (
            DEDICATED_HEADER_REL,
            DEDICATED_BINDING_REL,
            SHARED_ABI_HEADER_REL,
            SHARED_ABI_BINDING_REL,
            SHARED_CONTRACT_REL,
            SHARED_ABI_TEST_REL,
            SHARED_ABI_DUMP_REL,
            SHARED_ABI_HARNESS_REL,
            SHARED_ABI_EXPECTED_REL,
            MANIFEST_REL,
        ):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)

        (root / DEDICATED_HEADER_REL).write_text("\n".join(DEDICATED_HEADER_SNIPPETS) + "\n", encoding="utf-8")
        (root / DEDICATED_BINDING_REL).write_text("\n".join(DEDICATED_BINDING_SNIPPETS) + "\n", encoding="utf-8")
        (root / SHARED_ABI_HEADER_REL).write_text("\n".join(SHARED_ABI_HEADER_SNIPPETS) + "\n", encoding="utf-8")
        (root / SHARED_ABI_BINDING_REL).write_text("\n".join(SHARED_ABI_BINDING_SNIPPETS) + "\n", encoding="utf-8")
        (root / SHARED_CONTRACT_REL).write_text("\n".join(SHARED_CONTRACT_SNIPPETS) + "\n", encoding="utf-8")
        for rel, snippets in SHARED_PACKET_SNIPPETS.items():
            (root / rel).write_text("\n".join(snippets) + "\n", encoding="utf-8")
        (root / MANIFEST_REL).write_text("\n".join(MANIFEST_ENTRIES) + "\n", encoding="utf-8")
        (root / SHARED_ABI_EXPECTED_REL).write_text(
            json.dumps(
                {
                    "records": {
                        "rbtree_empty_root": {"root_addr": 0, "leftmost_addr": 0, "flags": 1, "reserved": 0},
                        "rbtree_cached_leftmost_root": {
                            "root_addr": 8192,
                            "leftmost_addr": 6144,
                            "flags": 6,
                            "reserved": 0,
                        },
                        "rbtree_uncached_root": {"root_addr": 9216, "leftmost_addr": 0, "flags": 0, "reserved": 0},
                    },
                    "structs": {
                        "zigux_rbtree_root_view": {
                            "size": 24,
                            "align": 8,
                            "offsets": {"root_addr": 0, "leftmost_addr": 8, "flags": 16, "reserved": 20},
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        assert validate(root) == []

        (root / SHARED_ABI_HEADER_REL).write_text(SHARED_ABI_HEADER_SNIPPETS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_shared_abi_header_snippet:") for issue in issues)

        (root / SHARED_ABI_HEADER_REL).write_text("\n".join(SHARED_ABI_HEADER_SNIPPETS) + "\n", encoding="utf-8")
        (root / SHARED_ABI_BINDING_REL).write_text(SHARED_ABI_BINDING_SNIPPETS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_shared_abi_binding_snippet:") for issue in issues)

        (root / SHARED_ABI_BINDING_REL).write_text("\n".join(SHARED_ABI_BINDING_SNIPPETS) + "\n", encoding="utf-8")
        (root / SHARED_ABI_TEST_REL).write_text(SHARED_PACKET_SNIPPETS[SHARED_ABI_TEST_REL][0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_shared_packet:") for issue in issues)

        print("PHASE3_RBTREE_SHARED_LIFT_CONTRACT_SELF_TEST=pass")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the landed shared Phase 3 rbtree lift stays aligned across the dedicated contract packet and shared ABI replay.")
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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-rbtree-interop-survey.md"
ROADMAP_GAP_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"
SLICE_REL = "Documentation/zigux/phase3-rbtree-slice.md"
DEDICATED_EXPECTED_REL = "zigux/tests/fixtures/phase3_rbtree/expected.json"
DEDICATED_HEADER_REL = "include/zigux/rbtree.h"
DEDICATED_BINDING_REL = "zigux/bindings/rbtree.zig"
SHARED_ABI_HEADER_REL = "include/zigux/abi.h"
SHARED_ABI_BINDING_REL = "zigux/bindings/abi.zig"
SHARED_ABI_TEST_REL = "zigux/tests/phase3_abi.zig"
SHARED_ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
SHARED_ABI_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"
SHARED_CONTRACT_REL = "zigux/tests/phase3_rbtree_shared_contract.zig"
MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"

SURVEY_MARKERS = (
    "PHASE3_RBTREE_SHARED_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet",
    "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid",
    "PHASE3_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig",
)

SURVEY_SNIPPETS = (
    "the shared Phase 3 ABI packet already replays `zigux_rbtree_root_view`",
    "shared replay, and shared-lift note aligned before the shared ABI packet grows",
)

ROADMAP_MARKERS = (
    "PHASE3_CURRENT_SHARED_RBTREE_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_CURRENT_RBTREE_SHARED_LAYOUT_CONTRACT=shared-phase3-abi-replay-already-reuses-dedicated-rbtree-layout-shared-header-lift-still-missing",
)

ROADMAP_SNIPPETS = (
    "the shared ABI replay already covers `zigux_rbtree_root_view`",
    "reuse the dedicated `zigux_rbtree_root_view` layout and flag constants unchanged",
)

SLICE_MARKERS = (
    "PHASE3_RBTREE_SHARED_BOUNDARY_STATUS=shared-parity-replay-present-shared-root-view-lift-still-missing",
    "PHASE3_RBTREE_SHARED_BOUNDARY_GAP=shared-abi-root-view-lift-still-missing",
    "PHASE3_RBTREE_SHARED_BOUNDARY_GUARDS=scripts/zigux/check-phase3-abi-layout-packet.py,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
)

SLICE_SNIPPETS = (
    "shared Phase 3 ABI parity replay that still reuses the dedicated `rbtree` header and Zig binding",
    "a shared `rbtree` record in `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "a shared Phase 3 ABI root-view implementation that no longer depends on `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig`",
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

SHARED_PACKET_SNIPPETS = {
    SHARED_ABI_TEST_REL: (
        'const rbtree = @import("rbtree_bindings");',
        "layout_assert.assertRbtreeRootViewLayout();",
        "const cached_root: rbtree.RootView = .{",
    ),
    SHARED_ABI_DUMP_REL: (
        'const rbtree = @import("rbtree_bindings");',
        'writeStructLayout(writer, "zigux_rbtree_root_view", rbtree.RootView, false);',
        'try writer.writeAll(",\\"root_flag_empty\\":");',
    ),
    SHARED_ABI_HARNESS_REL: (
        "#include <zigux/rbtree.h>",
        "offsetof(struct zigux_rbtree_root_view, root_addr)",
        "ZIGUX_RBTREE_ROOT_FLAG_EMPTY",
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

MANIFEST_PATHS = (
    "include/zigux/rbtree.h",
    "zigux/bindings/rbtree.zig",
    "zigux/tests/phase3_rbtree_dump.zig",
    "zigux/tests/phase3_rbtree_survey.zig",
    "zigux/tests/phase3_rbtree_manifest.json",
    "zigux/tests/phase3_rbtree_shared_contract.zig",
    "zigux/tests/fixtures/phase3_rbtree/expected.json",
    "zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c",
    "Documentation/zigux/phase3-rbtree-slice.md",
    "Documentation/zigux/phase3-rbtree-interop-survey.md",
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


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = read_text(root, SURVEY_REL, issues)
    roadmap = read_text(root, ROADMAP_GAP_REL, issues)
    slice_text = read_text(root, SLICE_REL, issues)
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
    require_absent(slice_text, SLICE_REL, STALE_SLICE_SNIPPETS, "stale_snippet", issues)
    require_contains(header, DEDICATED_HEADER_REL, DEDICATED_HEADER_TOKENS, "missing_token", issues)
    require_contains(binding, DEDICATED_BINDING_REL, DEDICATED_BINDING_TOKENS, "missing_token", issues)
    require_contains(shared_contract, SHARED_CONTRACT_REL, ("PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT", "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT"), "missing_snippet", issues)

    for rel, snippets in SHARED_PACKET_SNIPPETS.items():
        require_contains(read_text(root, rel, issues), rel, snippets, "missing_shared_packet", issues)
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


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_shared_lift_") as tmp_dir:
        root = Path(tmp_dir)
        write(root, SURVEY_REL, "\n".join((*SURVEY_MARKERS, *SURVEY_SNIPPETS)) + "\n")
        write(root, ROADMAP_GAP_REL, "\n".join((*ROADMAP_MARKERS, *ROADMAP_SNIPPETS)) + "\n")
        write(root, SLICE_REL, "\n".join((*SLICE_MARKERS, *SLICE_SNIPPETS)) + "\n")
        write(root, DEDICATED_HEADER_REL, "\n".join(DEDICATED_HEADER_TOKENS) + "\n")
        write(root, DEDICATED_BINDING_REL, "\n".join(DEDICATED_BINDING_TOKENS) + "\n")
        write(root, SHARED_CONTRACT_REL, "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT\nPHASE3_RBTREE_SHARED_CONSTANT_CONTRACT\n")
        for rel, snippets in SHARED_PACKET_SNIPPETS.items():
            write(root, rel, "\n".join(snippets) + "\n")
        for rel in SHARED_ABI_FORBIDDEN:
            write(root, rel, "// clean\n")
        write(root, MANIFEST_REL, json.dumps({"files": list(MANIFEST_PATHS)}))
        write(root, DEDICATED_EXPECTED_REL, json.dumps({"constants": EXPECTED_CONSTANTS, "structs": {"zigux_rbtree_root_view": EXPECTED_LAYOUT}}))
        assert validate(root) == []

        write(root, SLICE_REL, STALE_SLICE_SNIPPETS[0] + "\n")
        issues = validate(root)
        assert any(issue.startswith("stale_snippet:") for issue in issues)

        write(root, SLICE_REL, "\n".join((*SLICE_MARKERS, *SLICE_SNIPPETS)) + "\n")
        write(root, SHARED_ABI_BINDING_REL, SHARED_ABI_FORBIDDEN[SHARED_ABI_BINDING_REL][0] + "\n")
        issues = validate(root)
        assert any(issue.startswith("unexpected_shared_lift:") for issue in issues)

    print("PHASE3_RBTREE_SHARED_LIFT_CONTRACT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the planned shared Phase 3 rbtree lift contract stays aligned with the dedicated boundary packet.")
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

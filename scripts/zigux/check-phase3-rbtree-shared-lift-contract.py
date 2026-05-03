#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-rbtree-interop-survey.md"
ROADMAP_GAP_SURVEY_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"
RBTREE_SLICE_REL = "Documentation/zigux/phase3-rbtree-slice.md"
DEDICATED_EXPECTED_REL = "zigux/tests/fixtures/phase3_rbtree/expected.json"
DEDICATED_HEADER_REL = "include/zigux/rbtree.h"
DEDICATED_BINDING_REL = "zigux/bindings/rbtree.zig"
SHARED_ABI_HEADER_REL = "include/zigux/abi.h"
SHARED_ABI_BINDING_REL = "zigux/bindings/abi.zig"
SHARED_PHASE3_ABI_REL = "zigux/tests/phase3_abi.zig"
SHARED_PHASE3_ABI_DUMP_REL = "zigux/tests/phase3_abi_dump.zig"
SHARED_PHASE3_ABI_C_HARNESS_REL = "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"
SHARED_CONTRACT_REL = "zigux/tests/phase3_rbtree_shared_contract.zig"
PHASE3_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_RBTREE_SHARED_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet",
    "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid",
    "PHASE3_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig",
    "PHASE3_RBTREE_SHARED_PACKET_CATALOG=phase3_abi_manifest-catalogs-dedicated-rbtree-boundary-packet",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`python3 scripts/zigux/check-phase3-rbtree-shared-lift-contract.py` keeps the dedicated root-view layout, constants, shared replay, and shared-lift note aligned before the shared ABI packet grows",
    "the shared Phase 3 ABI packet already replays `zigux_rbtree_root_view` through `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`",
    "the shared lift should reuse the dedicated `zigux_rbtree_root_view` layout and `root_flag_empty`, `root_flag_cached`, and `root_flag_leftmost_valid` constants unchanged so the contract stays reviewable across the existing dedicated parity fixture",
    "`zigux/tests/phase3_rbtree_shared_contract.zig` now keeps that planned shared packet layout and constant contract machine-checked before the full shared header lift lands",
    "the shared Phase 3 ABI manifest now explicitly catalogs the dedicated `rbtree` boundary header, binding, dump, survey, and parity fixture files so the remaining gap is the shared header and binding lift itself rather than whether the dedicated packet belongs to the shared ABI tranche",
)

REQUIRED_ROADMAP_GAP_MARKERS = (
    "PHASE3_CURRENT_SHARED_RBTREE_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_CURRENT_RBTREE_SHARED_LAYOUT_CONTRACT=shared-phase3-abi-replay-already-reuses-dedicated-rbtree-layout-shared-header-lift-still-missing",
)

REQUIRED_ROADMAP_GAP_SNIPPETS = (
    "the shared ABI replay already covers `zigux_rbtree_root_view` through `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`",
    "When that lift lands, it should reuse the dedicated `zigux_rbtree_root_view` layout and `root_flag_empty`, `root_flag_cached`, and `root_flag_leftmost_valid` constants unchanged inside the shared packet.",
    "reuse the dedicated `zigux_rbtree_root_view` layout and flag constants unchanged",
    "`zigux/tests/phase3_rbtree_shared_contract.zig` also keeps that planned shared packet contract machine-checked before the full shared header and binding lift lands.",
)

REQUIRED_RBTREE_SLICE_MARKERS = (
    "PHASE3_RBTREE_SHARED_BOUNDARY_STATUS=shared-parity-replay-present-shared-root-view-lift-still-missing",
    "PHASE3_RBTREE_SHARED_BOUNDARY_GAP=shared-abi-root-view-lift-still-missing",
    "PHASE3_RBTREE_SHARED_BOUNDARY_GUARDS=scripts/zigux/check-phase3-abi-layout-packet.py,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
)

REQUIRED_RBTREE_SLICE_SNIPPETS = (
    "This slice now carries the dedicated `rbtree` boundary packet, and it also carries a shared Phase 3 ABI parity replay that still reuses the dedicated `rbtree` header and Zig binding rather than a curated shared record.",
    "a shared Phase 3 ABI parity replay that still reuses the dedicated `rbtree` header and Zig binding in `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, and `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`",
    "a shared `rbtree` record in `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "a shared Phase 3 ABI root-view implementation that no longer depends on `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig`",
    "The remaining honest Phase 3 `rbtree` gap after this step is the shared ABI lift, not the absence of a dedicated boundary packet.",
    "The next honest follow-up is one curated shared Phase 3 `rbtree` root-view lift:",
)

STALE_RBTREE_SLICE_SNIPPETS = (
    "PHASE3_RBTREE_SHARED_BOUNDARY_STATUS=shared-root-view-lift-landed",
    "PHASE3_RBTREE_SHARED_BOUNDARY_PACKET=include/zigux/abi.h,zigux/bindings/abi.zig,zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/expected.json",
    "This slice already carries both the dedicated `rbtree` boundary packet and the first shared root-view lift into the canonical Phase 3 ABI packet.",
    "a shared `rbtree` root-view record in `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "The next honest follow-up is to keep the shared `rbtree` packet reviewable and bounded rather than pretending the lane still needs the first lift.",
)

REQUIRED_SHARED_CONTRACT_SNIPPETS = (
    "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet",
    "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid",
    "@sizeOf(rbtree.RootView)",
    "rbtree.ROOT_FLAG_EMPTY",
    "rbtree.ROOT_FLAG_CACHED",
    "rbtree.ROOT_FLAG_LEFTMOST_VALID",
)

REQUIRED_SHARED_MANIFEST_RBTREE_FILES = (
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

REQUIRED_PENDING_SHARED_PACKET_SNIPPETS = {
    SHARED_PHASE3_ABI_REL: (
        'const rbtree = @import("rbtree_bindings");',
        "layout_assert.assertRbtreeRootViewLayout();",
        "layout_assert.assertSize(rbtree.RootView, @sizeOf(usize) * 2 + 8);",
        "const cached_root: rbtree.RootView = .{",
        "rbtree.ROOT_FLAG_CACHED | rbtree.ROOT_FLAG_LEFTMOST_VALID",
    ),
    SHARED_PHASE3_ABI_DUMP_REL: (
        'const rbtree = @import("rbtree_bindings");',
        'writeStructLayout(writer, "zigux_rbtree_root_view", rbtree.RootView, false);',
        'try writer.writeAll(",\\"root_flag_empty\\":");',
        "rbtree.ROOT_FLAG_EMPTY",
        "rbtree.ROOT_FLAG_CACHED",
        "rbtree.ROOT_FLAG_LEFTMOST_VALID",
    ),
    SHARED_PHASE3_ABI_C_HARNESS_REL: (
        "#include <zigux/rbtree.h>",
        "offsetof(struct zigux_rbtree_root_view, root_addr)",
        "ZIGUX_RBTREE_ROOT_FLAG_EMPTY",
        "ZIGUX_RBTREE_ROOT_FLAG_CACHED",
        "ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID",
    ),
}

STALE_SHARED_LIFT_TOKENS = {
    SHARED_ABI_HEADER_REL: (
        "#define ZIGUX_RBTREE_ROOT_FLAG_EMPTY 1U",
        "#define ZIGUX_RBTREE_ROOT_FLAG_CACHED 2U",
        "#define ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID 4U",
        "struct zigux_rbtree_root_view {",
    ),
    SHARED_ABI_BINDING_REL: (
        "pub const ROOT_FLAG_EMPTY: u32 = 1;",
        "pub const ROOT_FLAG_CACHED: u32 = 2;",
        "pub const ROOT_FLAG_LEFTMOST_VALID: u32 = 4;",
        "pub const RootView = extern struct {",
    ),
}

EXPECTED_CONSTANTS = {
    "root_flag_empty": 1,
    "root_flag_cached": 2,
    "root_flag_leftmost_valid": 4,
}

EXPECTED_LAYOUT = {
    "size": 24,
    "align": 8,
    "offsets": {
        "root_addr": 0,
        "leftmost_addr": 8,
        "flags": 16,
        "reserved": 20,
    },
}


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    roadmap_gap = _read_text(root, ROADMAP_GAP_SURVEY_REL, issues)
    rbtree_slice = _read_text(root, RBTREE_SLICE_REL, issues)
    expected_text = _read_text(root, DEDICATED_EXPECTED_REL, issues)
    header_text = _read_text(root, DEDICATED_HEADER_REL, issues)
    binding_text = _read_text(root, DEDICATED_BINDING_REL, issues)
    shared_abi_header_text = _read_text(root, SHARED_ABI_HEADER_REL, issues)
    shared_abi_binding_text = _read_text(root, SHARED_ABI_BINDING_REL, issues)
    shared_phase3_abi_text = _read_text(root, SHARED_PHASE3_ABI_REL, issues)
    shared_phase3_abi_dump_text = _read_text(root, SHARED_PHASE3_ABI_DUMP_REL, issues)
    shared_phase3_abi_c_harness_text = _read_text(root, SHARED_PHASE3_ABI_C_HARNESS_REL, issues)
    shared_contract_text = _read_text(root, SHARED_CONTRACT_REL, issues)
    manifest_text = _read_text(root, PHASE3_MANIFEST_REL, issues)

    if survey:
        for marker in REQUIRED_SURVEY_MARKERS:
            if marker not in survey:
                issues.append(f"missing_layout_contract_marker:{marker}")
        for snippet in REQUIRED_SURVEY_SNIPPETS:
            if snippet not in survey:
                issues.append(f"missing_layout_contract_snippet:{snippet}")

    if roadmap_gap:
        for marker in REQUIRED_ROADMAP_GAP_MARKERS:
            if marker not in roadmap_gap:
                issues.append(f"missing_roadmap_gap_layout_marker:{marker}")
        for snippet in REQUIRED_ROADMAP_GAP_SNIPPETS:
            if snippet not in roadmap_gap:
                issues.append(f"missing_roadmap_gap_layout_snippet:{snippet}")

    if rbtree_slice:
        for marker in REQUIRED_RBTREE_SLICE_MARKERS:
            if marker not in rbtree_slice:
                issues.append(f"missing_rbtree_slice_marker:{marker}")
        for snippet in REQUIRED_RBTREE_SLICE_SNIPPETS:
            if snippet not in rbtree_slice:
                issues.append(f"missing_rbtree_slice_snippet:{snippet}")
        for snippet in STALE_RBTREE_SLICE_SNIPPETS:
            if snippet in rbtree_slice:
                issues.append(f"stale_rbtree_slice_snippet:{snippet}")

    if shared_contract_text:
        for snippet in REQUIRED_SHARED_CONTRACT_SNIPPETS:
            if snippet not in shared_contract_text:
                issues.append(f"missing_shared_contract_snippet:{snippet}")

    if manifest_text:
        for rel in REQUIRED_SHARED_MANIFEST_RBTREE_FILES:
            if f'\"{rel}\"' not in manifest_text:
                issues.append(f"missing_shared_contract_manifest_entry:{rel}")

    if header_text:
        for token in (
            "#define ZIGUX_RBTREE_ROOT_FLAG_EMPTY 1U",
            "#define ZIGUX_RBTREE_ROOT_FLAG_CACHED 2U",
            "#define ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID 4U",
            "struct zigux_rbtree_root_view {",
            "unsigned long root_addr;",
            "unsigned long leftmost_addr;",
            "uint32_t flags;",
            "uint32_t reserved;",
        ):
            if token not in header_text:
                issues.append(f"missing_dedicated_header_token:{token}")

    if binding_text:
        for token in (
            "pub const ROOT_FLAG_EMPTY: u32 = 1;",
            "pub const ROOT_FLAG_CACHED: u32 = 2;",
            "pub const ROOT_FLAG_LEFTMOST_VALID: u32 = 4;",
            "pub const RootView = extern struct {",
            "root_addr: usize,",
            "leftmost_addr: usize,",
            "flags: u32,",
            "reserved: u32,",
        ):
            if token not in binding_text:
                issues.append(f"missing_dedicated_binding_token:{token}")

    for rel, text in (
        (SHARED_PHASE3_ABI_REL, shared_phase3_abi_text),
        (SHARED_PHASE3_ABI_DUMP_REL, shared_phase3_abi_dump_text),
        (SHARED_PHASE3_ABI_C_HARNESS_REL, shared_phase3_abi_c_harness_text),
    ):
        if text:
            for snippet in REQUIRED_PENDING_SHARED_PACKET_SNIPPETS[rel]:
                if snippet not in text:
                    issues.append(f"missing_pending_shared_packet_snippet:{rel}:{snippet}")

    for rel, text in (
        (SHARED_ABI_HEADER_REL, shared_abi_header_text),
        (SHARED_ABI_BINDING_REL, shared_abi_binding_text),
    ):
        if text:
            for token in STALE_SHARED_LIFT_TOKENS[rel]:
                if token in text:
                    issues.append(f"unexpected_shared_lift_token:{rel}:{token}")

    if expected_text:
        try:
            expected = json.loads(expected_text)
        except json.JSONDecodeError as exc:
            issues.append(f"invalid_expected_json:{exc.msg}")
        else:
            constants = expected.get("constants")
            if constants != EXPECTED_CONSTANTS:
                issues.append(f"unexpected_expected_constants:{constants!r}")
            structs = expected.get("structs", {})
            layout = structs.get("zigux_rbtree_root_view")
            if layout != EXPECTED_LAYOUT:
                issues.append(f"unexpected_expected_layout:{layout!r}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_shared_lift_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        for rel in (
            SURVEY_REL,
            ROADMAP_GAP_SURVEY_REL,
            RBTREE_SLICE_REL,
            DEDICATED_EXPECTED_REL,
            DEDICATED_HEADER_REL,
            DEDICATED_BINDING_REL,
            SHARED_ABI_HEADER_REL,
            SHARED_ABI_BINDING_REL,
            SHARED_PHASE3_ABI_REL,
            SHARED_PHASE3_ABI_DUMP_REL,
            SHARED_PHASE3_ABI_C_HARNESS_REL,
            SHARED_CONTRACT_REL,
            PHASE3_MANIFEST_REL,
        ):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)

        (root / SURVEY_REL).write_text(
            "\n".join((*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS)) + "\n",
            encoding="utf-8",
        )
        (root / ROADMAP_GAP_SURVEY_REL).write_text(
            "\n".join((*REQUIRED_ROADMAP_GAP_MARKERS, *REQUIRED_ROADMAP_GAP_SNIPPETS)) + "\n",
            encoding="utf-8",
        )
        (root / RBTREE_SLICE_REL).write_text(
            "\n".join((*REQUIRED_RBTREE_SLICE_MARKERS, *REQUIRED_RBTREE_SLICE_SNIPPETS)) + "\n",
            encoding="utf-8",
        )
        (root / DEDICATED_EXPECTED_REL).write_text(
            json.dumps(
                {
                    "constants": EXPECTED_CONSTANTS,
                    "structs": {"zigux_rbtree_root_view": EXPECTED_LAYOUT},
                }
            ),
            encoding="utf-8",
        )
        (root / DEDICATED_HEADER_REL).write_text(
            "\n".join(
                (
                    "#define ZIGUX_RBTREE_ROOT_FLAG_EMPTY 1U",
                    "#define ZIGUX_RBTREE_ROOT_FLAG_CACHED 2U",
                    "#define ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID 4U",
                    "struct zigux_rbtree_root_view {",
                    "    unsigned long root_addr;",
                    "    unsigned long leftmost_addr;",
                    "    uint32_t flags;",
                    "    uint32_t reserved;",
                    "};",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        (root / DEDICATED_BINDING_REL).write_text(
            "\n".join(
                (
                    "pub const ROOT_FLAG_EMPTY: u32 = 1;",
                    "pub const ROOT_FLAG_CACHED: u32 = 2;",
                    "pub const ROOT_FLAG_LEFTMOST_VALID: u32 = 4;",
                    "pub const RootView = extern struct {",
                    "    root_addr: usize,",
                    "    leftmost_addr: usize,",
                    "    flags: u32,",
                    "    reserved: u32,",
                    "};",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        (root / SHARED_ABI_HEADER_REL).writeText = None
        (root / SHARED_ABI_HEADER_REL).write_text(
            "struct zigux_cpumask_view { unsigned long bits_addr; zigux_u32 nr_cpu_ids; zigux_u32 reserved; };\n",
            encoding="utf-8",
        )
        (root / SHARED_ABI_BINDING_REL).write_text(
            "pub const CpuMaskView = extern struct { bits_addr: usize, nr_cpu_ids: u32, reserved: u32, };\n",
            encoding="utf-8",
        )
        (root / SHARED_PHASE3_ABI_REL).write_text(
            "\n".join(REQUIRED_PENDING_SHARED_PACKET_SNIPPETS[SHARED_PHASE3_ABI_REL]) + "\n",
            encoding="utf-8",
        )
        (root / SHARED_PHASE3_ABI_DUMP_REL).write_text(
            "\n".join(REQUIRED_PENDING_SHARED_PACKET_SNIPPETS[SHARED_PHASE3_ABI_DUMP_REL]) + "\n",
            encoding="utf-8",
        )
        (root / SHARED_PHASE3_ABI_C_HARNESS_REL).write_text(
            "\n".join(REQUIRED_PENDING_SHARED_PACKET_SNIPPETS[SHARED_PHASE3_ABI_C_HARNESS_REL]) + "\n",
            encoding="utf-8",
        )
        (root / SHARED_CONTRACT_REL).write_text(
            "\n".join(REQUIRED_SHARED_CONTRACT_SNIPPETS) + "\n",
            encoding="utf-8",
        )
        (root / PHASE3_MANIFEST_REL).write_text(
            json.dumps({"files": list(REQUIRED_SHARED_MANIFEST_RBTREE_FILES)}),
            encoding="utf-8",
        )

        assert validate(root) == []

        (root / RBTREE_SLICE_REL).write_text(
            "\n".join(REQUIRED_RBTREE_SLICE_MARKERS + REQUIRED_RBTREE_SLICE_SNIPPETS[:1] + STALE_RBTREE_SLICE_SNIPPETS[:1]) + "\n",
            encoding="utf-8",
        )
        issues = validate(root)
        assert any(issue.startswith("stale_rbtree_slice_snippet:") for issue in issues)

        (root / RBTREE_SLICE_REL).write_text(
            "\n".join((*REQUIRED_RBTREE_SLICE_MARKERS, *REQUIRED_RBTREE_SLICE_SNIPPETS)) + "\n",
            encoding="utf-8",
        )
        (root / SHARED_CONTRACT_REL).write_text(REQUIRED_SHARED_CONTRACT_SNIPPETS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_shared_contract_snippet:") for issue in issues)

        (root / SHARED_CONTRACT_REL).write_text(
            "\n".join(REQUIRED_SHARED_CONTRACT_SNIPPETS) + "\n",
            encoding="utf-8",
        )
        (root / SHARED_ABI_BINDING_REL).write_text(
            "pub const ROOT_FLAG_EMPTY: u32 = 1;\n",
            encoding="utf-8",
        )
        issues = validate(root)
        assert f"unexpected_shared_lift_token:{SHARED_ABI_BINDING_REL}:pub const ROOT_FLAG_EMPTY: u32 = 1;" in issues

        (root / SHARED_ABI_BINDING_REL).write_text(
            "pub const CpuMaskView = extern struct { bits_addr: usize, nr_cpu_ids: u32, reserved: u32, };\n",
            encoding="utf-8",
        )
        (root / PHASE3_MANIFEST_REL).write_text(json.dumps({"files": []}), encoding="utf-8")
        issues = validate(root)
        assert f"missing_shared_contract_manifest_entry:{REQUIRED_SHARED_MANIFEST_RBTREE_FILES[0]}" in issues

    print("PHASE3_RBTREE_SHARED_LIFT_CONTRACT_SELF_TEST=pass")
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

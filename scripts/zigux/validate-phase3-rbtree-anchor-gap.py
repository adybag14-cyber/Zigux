#!/usr/bin/env python3
"""Validate the current Phase 3 rbtree anchor gap survey note."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase3-rbtree-anchor-gap.md")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDINGS_PATH = Path("zigux/bindings/abi.zig")
EXPORT_SHIM_PATH = Path("zigux/kernel/export_shim.zig")
ABI_TEST_PATH = Path("zigux/tests/phase3_abi.zig")
BITMAP_NOTE_PATH = Path("Documentation/zigux/phase3-bitmap-cpumask-slice.md")
BITMAP_HELPER_PATH = Path("zigux/helpers/bitmap_view.zig")
CPUMASK_HELPER_PATH = Path("zigux/helpers/cpumask_view.zig")
LIST_NOTE_PATH = Path("Documentation/zigux/phase3-list-hlist-slice.md")
LIST_HELPER_PATH = Path("zigux/helpers/list_view.zig")
HLIST_HELPER_PATH = Path("zigux/helpers/hlist_view.zig")

REQUIRED_NOTE_MARKERS = (
    "Phase 3 Rbtree Anchor Gap",
    "the Phase 3 roadmap names `lib/rbtree.c` as one of the permanent C/Zigux boundary anchors",
    "`include/zigux/abi.h` already exposes `zigux_rbtree_root_view`",
    "`zigux/bindings/abi.zig` already mirrors that shared ABI surface through `RbtreeRootView`",
    "`zigux/kernel/export_shim.zig` already keeps the runtime status relay explicit through `validateRbtreeRootView()`",
    "`zigux/tests/phase3_abi.zig` already replays the shared `RbtreeRootView` layout and validation path",
    "`Documentation/zigux/phase3-bitmap-cpumask-slice.md`, `zigux/helpers/bitmap_view.zig`, and `zigux/helpers/cpumask_view.zig` already provide a dedicated bounded packet",
    "`Documentation/zigux/phase3-list-hlist-slice.md`, `zigux/helpers/list_view.zig`, and `zigux/helpers/hlist_view.zig` already provide a dedicated adjacent boundary packet",
    "Current `master` carries shared `RbtreeRootView` ABI and validation evidence, but it does not yet carry a dedicated manifest-backed `lib/rbtree.c` boundary packet",
    "add a dedicated `phase3-rbtree` survey packet that reuses the existing `RbtreeRootView` ABI surface",
)

REQUIRED_SOURCE_MARKERS = {
    ABI_HEADER_PATH: (
        "typedef struct zigux_rbtree_root_view {",
        "static inline int zigux_rbtree_root_view_is_cached(zigux_rbtree_root_view view)",
        "static inline int zigux_rbtree_root_view_has_leftmost(zigux_rbtree_root_view view)",
        "static inline int zigux_rbtree_root_view_is_valid(zigux_rbtree_root_view view)",
        "static inline zigux_rbtree_root_view zigux_rbtree_root_view_canonicalize(",
    ),
    ABI_BINDINGS_PATH: (
        "pub const RbtreeRootView = extern struct {",
        "pub fn rbtreeRootViewIsCached(view: RbtreeRootView) bool {",
        "pub fn rbtreeRootViewHasLeftmost(view: RbtreeRootView) bool {",
        "pub fn rbtreeRootViewIsValid(view: RbtreeRootView) bool {",
        "pub fn canonicalizeRbtreeRootView(view: RbtreeRootView) RbtreeRootView {",
    ),
    EXPORT_SHIM_PATH: (
        "pub const RbtreeRootView = abi.RbtreeRootView;",
        "pub fn rbtreeRootViewIsValid(view: RbtreeRootView) bool {",
        "pub fn canonicalizeRbtreeRootView(view: RbtreeRootView) RbtreeRootView {",
        "pub fn validateRbtreeRootView(view: RbtreeRootView) ExportStatus {",
    ),
    ABI_TEST_PATH: (
        "test \"phase3 abi keeps export shim compatibility and status helpers reviewable\" {",
        "test \"phase3 abi keeps version and dev_t relays explicit\" {",
    ),
    BITMAP_NOTE_PATH: ("phase3-bitmap-cpumask",),
    BITMAP_HELPER_PATH: ("bitmap",),
    CPUMASK_HELPER_PATH: ("cpumask",),
    LIST_NOTE_PATH: ("phase3-list-hlist",),
    LIST_HELPER_PATH: ("list",),
    HLIST_HELPER_PATH: ("hlist",),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    note_path = repo_root / NOTE_PATH
    try:
        note_text = _read(note_path)
    except FileNotFoundError:
        issues.append(f"missing repo file: {NOTE_PATH.as_posix()}")
        return issues

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in note_text:
            issues.append(f"missing {NOTE_PATH.as_posix()} marker: {marker}")

    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        path = repo_root / rel_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    return issues


def _populate_repo(root: Path) -> None:
    _write(root / NOTE_PATH, "\n".join(REQUIRED_NOTE_MARKERS) + "\n")
    for rel_path, markers in REQUIRED_SOURCE_MARKERS.items():
        _write(root / rel_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_gap_") as temp_dir:
        repo_root = Path(temp_dir)
        _populate_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        note_text = _read(repo_root / NOTE_PATH)
        _write(
            repo_root / NOTE_PATH,
            note_text.replace(
                "Current `master` carries shared `RbtreeRootView` ABI and validation evidence, but it does not yet carry a dedicated manifest-backed `lib/rbtree.c` boundary packet",
                "",
                1,
            ),
        )
        issues = validate_repo(repo_root)
        expected = (
            "missing Documentation/zigux/phase3-rbtree-anchor-gap.md marker: "
            "Current `master` carries shared `RbtreeRootView` ABI and validation evidence, but it does not yet carry a dedicated manifest-backed `lib/rbtree.c` boundary packet"
        )
        if expected not in issues:
            print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=fail")
            print("expected missing note gap marker was not reported")
            return 1

        _populate_repo(repo_root)
        abi_text = _read(repo_root / ABI_HEADER_PATH)
        _write(
            repo_root / ABI_HEADER_PATH,
            abi_text.replace(
                "static inline int zigux_rbtree_root_view_is_valid(zigux_rbtree_root_view view)",
                "",
                1,
            ),
        )
        issues = validate_repo(repo_root)
        expected = (
            "missing include/zigux/abi.h marker: "
            "static inline int zigux_rbtree_root_view_is_valid(zigux_rbtree_root_view view)"
        )
        if expected not in issues:
            print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=fail")
            print("expected missing abi.h rbtree marker was not reported")
            return 1

        _populate_repo(repo_root)
        export_text = _read(repo_root / EXPORT_SHIM_PATH)
        _write(
            repo_root / EXPORT_SHIM_PATH,
            export_text.replace("pub fn validateRbtreeRootView(view: RbtreeRootView) ExportStatus {", "", 1),
        )
        issues = validate_repo(repo_root)
        expected = (
            "missing zigux/kernel/export_shim.zig marker: "
            "pub fn validateRbtreeRootView(view: RbtreeRootView) ExportStatus {"
        )
        if expected not in issues:
            print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=fail")
            print("expected missing export-shim rbtree marker was not reported")
            return 1

    print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=pass")
    print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 rbtree anchor gap survey note."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 rbtree anchor gap survey note",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_RBTREE_ANCHOR_GAP=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {NOTE_PATH.as_posix()}")
    print(f"validated {ABI_HEADER_PATH.as_posix()}")
    print(f"validated {ABI_BINDINGS_PATH.as_posix()}")
    print(f"validated {EXPORT_SHIM_PATH.as_posix()}")
    print(f"validated {ABI_TEST_PATH.as_posix()}")
    print("PHASE3_RBTREE_ANCHOR_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

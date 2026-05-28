#!/usr/bin/env python3
"""Check the bounded Phase 3 rbtree roadmap-gap note against current repo reality."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOC_PATH = Path("Documentation/zigux/phase3-rbtree-anchor-gap.md")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDING_PATH = Path("zigux/bindings/abi.zig")
EXPORT_SHIM_PATH = Path("zigux/kernel/export_shim.zig")
ABI_TEST_PATH = Path("zigux/tests/phase3_abi.zig")
ABI_DUMP_PATH = Path("zigux/tests/phase3_abi_dump_current.zig")

REQUIRED_DOC_MARKERS = (
    "- the Phase 3 roadmap names `lib/rbtree.c` as one of the permanent C/Zigux boundary anchors beside `rust/exports.c`, `lib/bitmap.c`, and `lib/cpumask.c`",
    "- `include/zigux/abi.h` already exposes `zigux_rbtree_root_view`, `zigux_rbtree_root_view_is_cached()`, `zigux_rbtree_root_view_has_leftmost()`, `zigux_rbtree_root_view_is_valid()`, and `zigux_rbtree_root_view_canonicalize()`",
    "- `zigux/bindings/abi.zig` already mirrors that shared ABI surface through `RbtreeRootView`, `rbtreeRootViewIsCached()`, `rbtreeRootViewHasLeftmost()`, `rbtreeRootViewIsValid()`, and `canonicalizeRbtreeRootView()`",
    "- `zigux/kernel/export_shim.zig` already keeps the runtime status relay explicit through `validateRbtreeRootView()`",
    "Current `master` carries shared `RbtreeRootView` ABI and validation evidence, but it does not yet carry a dedicated manifest-backed `lib/rbtree.c` boundary packet comparable to the landed bitmap/cpumask and list/hlist survey slices.",
    "- add a dedicated `phase3-rbtree` survey packet that reuses the existing `RbtreeRootView` ABI surface, keeps the scope at boundary and layout validation, and does not widen into broader runtime-core delivery",
)

REQUIRED_REPO_MARKERS = {
    ABI_HEADER_PATH: (
        "typedef struct zigux_rbtree_root_view {",
        "uintptr_t root;",
        "uintptr_t cached_leftmost;",
    ),
    ABI_BINDING_PATH: (
        "pub const RbtreeRootView = extern struct {",
        "pub const rbtree_root_view_root_offset = @offsetOf(RbtreeRootView, \"root\");",
        "pub const rbtree_root_view_cached_leftmost_offset = @offsetOf(RbtreeRootView, \"cached_leftmost\");",
        "pub fn canonicalizeRbtreeRootView(view: RbtreeRootView) RbtreeRootView {",
    ),
    EXPORT_SHIM_PATH: (
        "pub fn validateRbtreeRootView(view: abi.RbtreeRootView) abi.ExportStatus {",
    ),
}

DEDICATED_RBTREE_PACKET_PATHS = (
    Path("Documentation/zigux/phase3-rbtree-slice.md"),
    Path("zigux/helpers/rbtree_view.zig"),
    Path("zigux/tests/phase3_rbtree_starter_packet.zig"),
    Path("zigux/tests/phase3_rbtree_dump.zig"),
    Path("zigux/tests/fixtures/phase3_rbtree_manifest.json"),
    Path("scripts/zigux/check-phase3-rbtree.py"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    doc_path = repo_root / DOC_PATH
    if not doc_path.is_file():
        return [f"missing repo file: {DOC_PATH.as_posix()}"]
    doc_text = _read(doc_path)
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            issues.append(f"missing {DOC_PATH.as_posix()} marker: {marker}")

    for rel_path, markers in REQUIRED_REPO_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {rel_path.as_posix()} marker: {marker}")

    for rel_path in (ABI_TEST_PATH, ABI_DUMP_PATH):
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    present_dedicated_paths = [
        rel_path.as_posix()
        for rel_path in DEDICATED_RBTREE_PACKET_PATHS
        if (repo_root / rel_path).exists()
    ]
    if present_dedicated_paths:
        issues.append(
            "dedicated rbtree packet paths now exist and the gap note must be refreshed: "
            + ", ".join(present_dedicated_paths)
        )

    return issues


def _populate_self_test_repo(root: Path) -> None:
    _write(root / DOC_PATH, "\n".join(REQUIRED_DOC_MARKERS) + "\n")
    _write(
        root / ABI_HEADER_PATH,
        "\n".join(REQUIRED_REPO_MARKERS[ABI_HEADER_PATH]) + "\n",
    )
    _write(
        root / ABI_BINDING_PATH,
        "\n".join(REQUIRED_REPO_MARKERS[ABI_BINDING_PATH]) + "\n",
    )
    _write(
        root / EXPORT_SHIM_PATH,
        "\n".join(REQUIRED_REPO_MARKERS[EXPORT_SHIM_PATH]) + "\n",
    )
    _write(root / ABI_TEST_PATH, "// shared abi replay placeholder\n")
    _write(root / ABI_DUMP_PATH, "// shared abi dump placeholder\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_gap_") as tmp_dir:
        repo_root = Path(tmp_dir)
        _populate_self_test_repo(repo_root)

        issues = validate_repo(repo_root)
        if issues:
            print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        doc_path = repo_root / DOC_PATH
        doc_path.write_text("# broken\n", encoding="utf-8", newline="\n")
        issues = validate_repo(repo_root)
        expected_issue = (
            "missing Documentation/zigux/phase3-rbtree-anchor-gap.md marker: "
            + REQUIRED_DOC_MARKERS[0]
        )
        if expected_issue not in issues:
            print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=fail")
            print("expected missing-doc-marker issue was not reported")
            return 1

        _populate_self_test_repo(repo_root)
        dedicated_path = repo_root / DEDICATED_RBTREE_PACKET_PATHS[0]
        _write(dedicated_path, "# landed\n")
        issues = validate_repo(repo_root)
        expected_drift = "dedicated rbtree packet paths now exist and the gap note must be refreshed:"
        if not any(issue.startswith(expected_drift) for issue in issues):
            print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=fail")
            print("expected dedicated-packet drift issue was not reported")
            return 1

    print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST=pass")
    print("PHASE3_RBTREE_ANCHOR_GAP_SELF_TEST_CASE_COUNT=2")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 3 rbtree roadmap-gap note."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the bounded Phase 3 rbtree survey note",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root.resolve())
    if issues:
        print("PHASE3_RBTREE_ANCHOR_GAP=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_RBTREE_ANCHOR_GAP=pass")
    print(f"validated {DOC_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

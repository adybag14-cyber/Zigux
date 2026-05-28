#!/usr/bin/env python3
"""Validate the focused Phase 3 export/UAPI C smoke policy and rbtree relays."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SMOKE_PATH = Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")

REQUIRED_MARKERS = {
    SMOKE_PATH: (
        "static int check_interop_policy_relays(void)",
        "zigux_default_interop_policy()",
        "zigux_panic_mode_is_known(",
        "zigux_allocator_mode_is_known(",
        "zigux_unsafe_scope_is_known(",
        "zigux_interop_policy_reserved_clear(",
        "zigux_interop_policy_is_recognized(",
        "static int check_uapi_policy_and_rbtree_relays(void)",
        "zigux_uapi_default_interop_policy()",
        "zigux_uapi_panic_mode_is_known(",
        "zigux_uapi_allocator_mode_is_known(",
        "zigux_uapi_unsafe_scope_is_known(",
        "zigux_uapi_interop_policy_reserved_clear(",
        "zigux_uapi_interop_policy_is_recognized(",
        "reserved_status =\n        zigux_uapi_validate_interop_policy(reserved);",
        "unknown_status =\n        zigux_uapi_validate_interop_policy(unknown);",
        "zigux_uapi_rbtree_root_view_is_cached(",
        "zigux_uapi_rbtree_root_view_has_leftmost(",
        "zigux_uapi_rbtree_root_view_is_valid(",
        "zigux_uapi_rbtree_root_view_canonicalize(",
        "malformed_status =\n        zigux_uapi_validate_rbtree_root_view(malformed);",
        "if (reserved_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
        "if (unknown_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
        "if (malformed_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
    ),
    LINUX_HEADER_PATH: (
        "static inline struct zigux_interop_policy zigux_uapi_default_interop_policy(void)",
        "static inline int zigux_uapi_panic_mode_is_known(uint8_t mode)",
        "static inline int zigux_uapi_allocator_mode_is_known(uint8_t mode)",
        "static inline int zigux_uapi_unsafe_scope_is_known(uint8_t scope)",
        "static inline int zigux_uapi_interop_policy_reserved_clear(",
        "static inline int zigux_uapi_interop_policy_is_recognized(",
        "static inline struct zigux_export_status zigux_uapi_validate_interop_policy(",
        "static inline int zigux_uapi_rbtree_root_view_is_cached(zigux_rbtree_root_view view)",
        "static inline int zigux_uapi_rbtree_root_view_has_leftmost(zigux_rbtree_root_view view)",
        "static inline int zigux_uapi_rbtree_root_view_is_valid(zigux_rbtree_root_view view)",
        "static inline zigux_rbtree_root_view zigux_uapi_rbtree_root_view_canonicalize(",
        "static inline struct zigux_export_status zigux_uapi_validate_rbtree_root_view(",
    ),
}

SELFTEST_SMOKE = """#include <linux/zigux.h>

static int check_interop_policy_relays(void)
{
    struct zigux_interop_policy safe = zigux_default_interop_policy();

    if (!zigux_panic_mode_is_known(safe.panic_mode))
        return __LINE__;
    if (!zigux_allocator_mode_is_known(safe.allocator_mode))
        return __LINE__;
    if (!zigux_unsafe_scope_is_known(safe.unsafe_scope))
        return __LINE__;
    if (!zigux_interop_policy_reserved_clear(safe))
        return __LINE__;
    if (!zigux_interop_policy_is_recognized(safe))
        return __LINE__;

    return 0;
}

static int check_uapi_policy_and_rbtree_relays(void)
{
    struct zigux_interop_policy safe = zigux_uapi_default_interop_policy();
    struct zigux_interop_policy reserved = {
        .panic_mode = 1u,
        .allocator_mode = 2u,
        .unsafe_scope = 2u,
        .reserved = 1u,
    };
    struct zigux_interop_policy unknown = {
        .panic_mode = 9u,
        .allocator_mode = 9u,
        .unsafe_scope = 9u,
        .reserved = 0u,
    };
    zigux_rbtree_root_view cached = {
        .root = (uintptr_t)0x1000u,
        .cached_leftmost = (uintptr_t)0x0800u,
        .flags = 3u,
    };
    zigux_rbtree_root_view malformed = {
        .root = (uintptr_t)0x1000u,
        .cached_leftmost = (uintptr_t)0,
        .flags = 3u,
    };
    struct zigux_export_status reserved_status =
        zigux_uapi_validate_interop_policy(reserved);
    struct zigux_export_status unknown_status =
        zigux_uapi_validate_interop_policy(unknown);
    struct zigux_export_status malformed_status =
        zigux_uapi_validate_rbtree_root_view(malformed);

    if (!zigux_uapi_panic_mode_is_known(safe.panic_mode))
        return __LINE__;
    if (!zigux_uapi_allocator_mode_is_known(safe.allocator_mode))
        return __LINE__;
    if (!zigux_uapi_unsafe_scope_is_known(safe.unsafe_scope))
        return __LINE__;
    if (!zigux_uapi_interop_policy_reserved_clear(safe))
        return __LINE__;
    if (!zigux_uapi_interop_policy_is_recognized(safe))
        return __LINE__;
    if (!zigux_uapi_rbtree_root_view_is_cached(cached))
        return __LINE__;
    if (!zigux_uapi_rbtree_root_view_has_leftmost(cached))
        return __LINE__;
    if (!zigux_uapi_rbtree_root_view_is_valid(cached))
        return __LINE__;
    if (zigux_uapi_rbtree_root_view_is_valid(malformed))
        return __LINE__;
    if (zigux_uapi_rbtree_root_view_canonicalize(malformed).flags != 0u)
        return __LINE__;
    if (reserved_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (unknown_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (malformed_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;

    return 0;
}
"""

SELFTEST_LINUX_HEADER = """static inline struct zigux_interop_policy zigux_uapi_default_interop_policy(void)
static inline int zigux_uapi_panic_mode_is_known(uint8_t mode)
static inline int zigux_uapi_allocator_mode_is_known(uint8_t mode)
static inline int zigux_uapi_unsafe_scope_is_known(uint8_t scope)
static inline int zigux_uapi_interop_policy_reserved_clear(
static inline int zigux_uapi_interop_policy_is_recognized(
static inline struct zigux_export_status zigux_uapi_validate_interop_policy(
static inline int zigux_uapi_rbtree_root_view_is_cached(zigux_rbtree_root_view view)
static inline int zigux_uapi_rbtree_root_view_has_leftmost(zigux_rbtree_root_view view)
static inline int zigux_uapi_rbtree_root_view_is_valid(zigux_rbtree_root_view view)
static inline zigux_rbtree_root_view zigux_uapi_rbtree_root_view_canonicalize(
static inline struct zigux_export_status zigux_uapi_validate_rbtree_root_view(
"""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(
                    f"missing {relative_path.as_posix()} marker: {marker}"
                )
    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase3_export_uapi_policy_rbtree_"
    ) as temp_dir:
        root = Path(temp_dir)
        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        _write(root / LINUX_HEADER_PATH, SELFTEST_LINUX_HEADER)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_EXPORT_UAPI_POLICY_RBTREE_SMOKE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        cases = (
            (
                SMOKE_PATH,
                "static int check_interop_policy_relays(void)",
                "expected missing smoke interop-policy section to fail validation",
            ),
            (
                SMOKE_PATH,
                "reserved_status =\n        zigux_uapi_validate_interop_policy(reserved);",
                "expected missing reserved-status interop-policy relay marker to fail validation",
            ),
            (
                SMOKE_PATH,
                "malformed_status =\n        zigux_uapi_validate_rbtree_root_view(malformed);",
                "expected missing malformed-status rbtree validation marker to fail validation",
            ),
            (
                SMOKE_PATH,
                "if (malformed_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
                "expected missing malformed rbtree status marker to fail validation",
            ),
            (
                LINUX_HEADER_PATH,
                "static inline struct zigux_interop_policy zigux_uapi_default_interop_policy(void)",
                "expected missing linux header uapi default interop policy marker to fail validation",
            ),
            (
                LINUX_HEADER_PATH,
                "static inline struct zigux_export_status zigux_uapi_validate_interop_policy(",
                "expected missing linux header interop-policy status relay marker to fail validation",
            ),
            (
                LINUX_HEADER_PATH,
                "static inline struct zigux_export_status zigux_uapi_validate_rbtree_root_view(",
                "expected missing linux header rbtree status relay marker to fail validation",
            ),
        )

        for relative_path, marker, message in cases:
            text = _read(root / relative_path)
            _write(root / relative_path, text.replace(marker, "", 1))
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_EXPORT_UAPI_POLICY_RBTREE_SMOKE_SELF_TEST=fail")
                print(message)
                return 1
            if relative_path == SMOKE_PATH:
                _write(root / SMOKE_PATH, SELFTEST_SMOKE)
            else:
                _write(root / LINUX_HEADER_PATH, SELFTEST_LINUX_HEADER)

    print("PHASE3_EXPORT_UAPI_POLICY_RBTREE_SMOKE_SELF_TEST=pass")
    print(
        "PHASE3_EXPORT_UAPI_POLICY_RBTREE_SMOKE_SELF_TEST_CASES="
        f"{1 + len(cases)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 export/UAPI C smoke policy and rbtree relays."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains include/ and zigux/tests/",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_EXPORT_UAPI_POLICY_RBTREE_SMOKE=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SMOKE_PATH}")
    print(f"validated {args.repo_root / LINUX_HEADER_PATH}")
    print("PHASE3_EXPORT_UAPI_POLICY_RBTREE_SMOKE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

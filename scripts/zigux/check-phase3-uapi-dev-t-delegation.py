#!/usr/bin/env python3
"""Verify the Phase 3 Linux UAPI dev_t relays delegate to the canonical helpers."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path


LINUX_HEADER = Path("include/linux/zigux.h")
ABI_HEADER = Path("include/zigux/abi.h")
DEV_T_HEADER = Path("include/zigux/dev_t.h")

LINUX_MARKERS = (
    "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    "return zigux_dev_t_fields_is_valid(fields);",
    "static inline int zigux_uapi_dev_t_fields_range_is_valid(",
    "return zigux_dev_t_fields_range_is_valid(start, end);",
    "zigux_uapi_validate_dev_t_fields(",
    "zigux_uapi_validate_dev_t_components(",
    "zigux_uapi_validate_dev_t_range(",
)

DEV_T_MARKERS = (
    "static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    "fields.major <= ZIGUX_DEV_MAJOR_MAX",
    "fields.minor <= ZIGUX_DEV_MINOR_MASK",
    "static inline int zigux_dev_t_fields_range_is_valid(",
)

SMOKE_SOURCE = r"""
#include <linux/zigux.h>

static int check_dev_t_delegation(void)
{
    struct zigux_dev_t_fields valid = zigux_dev_t_fields_make(4u, 9u);
    struct zigux_dev_t_fields invalid_major =
        zigux_dev_t_fields_make(ZIGUX_DEV_MAJOR_MAX + 1u, 0u);
    struct zigux_dev_t_fields invalid_minor =
        zigux_dev_t_fields_make(0u, ZIGUX_DEV_MINOR_MASK + 1u);
    struct zigux_dev_t_fields start = zigux_dev_t_fields_make(4u, 8u);
    struct zigux_dev_t_fields end = zigux_dev_t_fields_make(4u, 9u);
    struct zigux_export_status valid_status =
        zigux_uapi_validate_dev_t_fields(valid);
    struct zigux_export_status invalid_status =
        zigux_uapi_validate_dev_t_fields(invalid_major);
    struct zigux_export_status invalid_minor_status =
        zigux_uapi_validate_dev_t_fields(invalid_minor);
    struct zigux_export_status valid_range_status =
        zigux_uapi_validate_dev_t_range(start, end);
    struct zigux_export_status invalid_range_status =
        zigux_uapi_validate_dev_t_range(end, start);

    if (zigux_uapi_dev_t_fields_is_valid(valid) != zigux_dev_t_fields_is_valid(valid))
        return __LINE__;
    if (zigux_uapi_dev_t_fields_is_valid(invalid_major) != zigux_dev_t_fields_is_valid(invalid_major))
        return __LINE__;
    if (zigux_uapi_dev_t_fields_is_valid(invalid_minor) != zigux_dev_t_fields_is_valid(invalid_minor))
        return __LINE__;
    if (zigux_uapi_dev_t_fields_range_is_valid(start, end) != zigux_dev_t_fields_range_is_valid(start, end))
        return __LINE__;
    if (zigux_uapi_dev_t_fields_range_is_valid(end, start) != zigux_dev_t_fields_range_is_valid(end, start))
        return __LINE__;
    if (zigux_export_status_ok(valid_status) == 0)
        return __LINE__;
    if (zigux_export_status_ok(invalid_status) != 0)
        return __LINE__;
    if (zigux_export_status_ok(invalid_minor_status) != 0)
        return __LINE__;
    if (invalid_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (zigux_export_status_ok(valid_range_status) == 0)
        return __LINE__;
    if (zigux_export_status_ok(invalid_range_status) != 0)
        return __LINE__;
    if (invalid_range_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;

    return 0;
}

int main(void)
{
    return check_dev_t_delegation();
}
"""

SELFTEST_ABI = r"""#ifndef _ZIGUX_ABI_H
#define _ZIGUX_ABI_H

#include <stdint.h>

#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_STATUS_FLAG_ERROR 1U

struct zigux_export_status {
    int32_t code;
    uint16_t facility;
    uint16_t flags;
};

static inline struct zigux_export_status zigux_make_status(
    int32_t code,
    uint16_t facility)
{
    struct zigux_export_status status = {
        .code = code,
        .facility = facility,
        .flags = (uint16_t)(code < 0 ? ZIGUX_STATUS_FLAG_ERROR : 0U),
    };
    return status;
}

static inline struct zigux_export_status zigux_ok_status(uint16_t facility)
{
    return zigux_make_status(0, facility);
}

static inline int zigux_export_status_ok(struct zigux_export_status status)
{
    return (status.flags & (uint16_t)ZIGUX_STATUS_FLAG_ERROR) == 0;
}

#endif
"""

SELFTEST_DEV_T = r"""#ifndef ZIGUX_DEV_T_H
#define ZIGUX_DEV_T_H

#include <stdint.h>

#define ZIGUX_DEV_MINOR_BITS 20u
#define ZIGUX_DEV_MINOR_MASK ((1u << ZIGUX_DEV_MINOR_BITS) - 1u)
#define ZIGUX_DEV_MAJOR_MAX ((1u << (32u - ZIGUX_DEV_MINOR_BITS)) - 1u)

struct zigux_dev_t_fields {
    uint32_t major;
    uint32_t minor;
};

static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(
    uint32_t major,
    uint32_t minor)
{
    struct zigux_dev_t_fields fields = {
        .major = major,
        .minor = minor,
    };
    return fields;
}

static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)
{
    return fields.major <= ZIGUX_DEV_MAJOR_MAX &&
        fields.minor <= ZIGUX_DEV_MINOR_MASK;
}

static inline int zigux_dev_t_fields_range_is_valid(
    struct zigux_dev_t_fields start,
    struct zigux_dev_t_fields end)
{
    if (!zigux_dev_t_fields_is_valid(start) || !zigux_dev_t_fields_is_valid(end))
        return 0;
    return start.major < end.major ||
        (start.major == end.major && start.minor <= end.minor);
}

#endif
"""

SELFTEST_LINUX = r"""#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#include <stdint.h>
#include <zigux/abi.h>
#include <zigux/dev_t.h>

#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)

static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)
{
    return zigux_dev_t_fields_is_valid(fields);
}

static inline struct zigux_export_status zigux_uapi_validate_dev_t_fields(
    struct zigux_dev_t_fields fields)
{
    if (zigux_uapi_dev_t_fields_is_valid(fields))
        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);
    return zigux_make_status(
        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,
        (uint16_t)ZIGUX_FACILITY_KERNEL);
}

static inline struct zigux_export_status zigux_uapi_validate_dev_t_components(
    uint32_t major,
    uint32_t minor)
{
    return zigux_uapi_validate_dev_t_fields(zigux_dev_t_fields_make(major, minor));
}

static inline int zigux_uapi_dev_t_fields_range_is_valid(
    struct zigux_dev_t_fields start,
    struct zigux_dev_t_fields end)
{
    return zigux_dev_t_fields_range_is_valid(start, end);
}

static inline struct zigux_export_status zigux_uapi_validate_dev_t_range(
    struct zigux_dev_t_fields start,
    struct zigux_dev_t_fields end)
{
    if (zigux_uapi_dev_t_fields_range_is_valid(start, end))
        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);
    return zigux_make_status(
        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,
        (uint16_t)ZIGUX_FACILITY_KERNEL);
}

#endif
"""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _check_markers(repo_root: Path) -> list[str]:
    issues: list[str] = []
    marker_sets = {
        LINUX_HEADER: LINUX_MARKERS,
        DEV_T_HEADER: DEV_T_MARKERS,
    }
    for relative_path, markers in marker_sets.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _compile_smoke(repo_root: Path, cc: str) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_uapi_dev_t_") as temp_dir:
        temp_path = Path(temp_dir)
        smoke_path = temp_path / "phase3_uapi_dev_t_delegation.c"
        exe_path = temp_path / "phase3_uapi_dev_t_delegation"
        _write(smoke_path, SMOKE_SOURCE)
        compile_result = subprocess.run(
            [
                cc,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                f"-I{(repo_root / 'include').as_posix()}",
                smoke_path.as_posix(),
                "-o",
                exe_path.as_posix(),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            return [
                "phase3 UAPI dev_t delegation smoke failed to compile: "
                + compile_result.stderr.strip()
            ]

        run_result = subprocess.run(
            [exe_path.as_posix()],
            check=False,
            capture_output=True,
            text=True,
        )
        if run_result.returncode != 0:
            return [
                "phase3 UAPI dev_t delegation smoke failed at runtime: "
                + f"exit {run_result.returncode}"
            ]
    return []


def validate_repo(repo_root: Path, cc: str) -> list[str]:
    issues = _check_markers(repo_root)
    if issues:
        return issues
    return _compile_smoke(repo_root, cc)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_uapi_dev_t_selftest_") as temp_dir:
        root = Path(temp_dir)
        _write(root / ABI_HEADER, SELFTEST_ABI)
        _write(root / DEV_T_HEADER, SELFTEST_DEV_T)
        _write(root / LINUX_HEADER, SELFTEST_LINUX)

        issues = validate_repo(root, "cc")
        if issues:
            print("PHASE3_UAPI_DEV_T_DELEGATION_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        broken_linux = _read(root / LINUX_HEADER).replace(
            "return zigux_dev_t_fields_is_valid(fields);",
            "return fields.major <= ZIGUX_DEV_MAJOR_MAX && fields.minor <= ZIGUX_DEV_MINOR_MASK;",
            1,
        )
        _write(root / LINUX_HEADER, broken_linux)
        issues = validate_repo(root, "cc")
        expected = (
            "missing include/linux/zigux.h marker: "
            "return zigux_dev_t_fields_is_valid(fields);"
        )
        if expected not in issues:
            print("PHASE3_UAPI_DEV_T_DELEGATION_SELF_TEST=fail")
            print("expected missing field-delegation marker was not reported")
            return 1

        _write(root / LINUX_HEADER, SELFTEST_LINUX)
        broken_range = _read(root / LINUX_HEADER).replace(
            "return zigux_dev_t_fields_range_is_valid(start, end);",
            "return start.major < end.major || (start.major == end.major && start.minor <= end.minor);",
            1,
        )
        _write(root / LINUX_HEADER, broken_range)
        issues = validate_repo(root, "cc")
        expected = (
            "missing include/linux/zigux.h marker: "
            "return zigux_dev_t_fields_range_is_valid(start, end);"
        )
        if expected not in issues:
            print("PHASE3_UAPI_DEV_T_DELEGATION_SELF_TEST=fail")
            print("expected missing range-delegation marker was not reported")
            return 1

    print("PHASE3_UAPI_DEV_T_DELEGATION_SELF_TEST=pass")
    print("PHASE3_UAPI_DEV_T_DELEGATION_SELF_TEST_CASE_COUNT=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Phase 3 Linux UAPI dev_t relays delegate to canonical helpers."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--cc", default="cc")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root, args.cc)
    if issues:
        print("PHASE3_UAPI_DEV_T_DELEGATION=fail")
        print("\n".join(issues))
        return 1

    print("PHASE3_UAPI_DEV_T_DELEGATION=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compile and run the current Phase 3 export/UAPI C header smoke."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

SMOKE_PATH = Path("zigux/tests/phase3_export_uapi_c_header_smoke.c")
LINUX_HEADER_PATH = Path("include/linux/zigux.h")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")

REQUIRED_MARKERS = {
    SMOKE_PATH: (
        "#include <linux/zigux.h>",
        "static int check_version_relays(void)",
        "zigux_uapi_version_current()",
        "if (!zigux_uapi_export_status_ok(valid))",
        "if (zigux_uapi_export_status_ok(invalid))",
        "static int check_status_facility_relays(void)",
        "if (!zigux_uapi_export_status_ok(ok))",
        "if (zigux_uapi_export_status_ok(err))",
        "if (!zigux_uapi_export_status_ok(unknown))",
        "if (!zigux_uapi_export_status_has_known_facility(ok))",
        "int main(void)",
    ),
    LINUX_HEADER_PATH: (
        "static inline int zigux_uapi_facility_is_known(uint16_t facility)",
        "static inline int zigux_uapi_export_status_ok(struct zigux_export_status status)",
        "return zigux_export_status_ok(status);",
        "static inline int zigux_uapi_export_status_has_known_facility(",
    ),
}

SELFTEST_ABI_HEADER = Path(__file__).with_name('abi_selftest_unused.txt')
SELFTEST_DEV_T_HEADER = Path(__file__).with_name('devt_selftest_unused.txt')

SELFTEST_ABI_HEADER_TEXT = """#ifndef _ZIGUX_ABI_H
#define _ZIGUX_ABI_H
#include <stdint.h>
#define ZIGUX_ABI_VERSION 1U
#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_FACILITY_HELPERS 2U
#define ZIGUX_STATUS_FLAG_ERROR 1U
typedef struct zigux_boundary_header { uint32_t size; uint16_t abi_version; uint16_t flags; } zigux_boundary_header;
struct zigux_export_status { int32_t code; uint16_t facility; uint16_t flags; };
static inline struct zigux_export_status zigux_make_status(int32_t code, uint16_t facility) { struct zigux_export_status s = { .code = code, .facility = facility, .flags = (uint16_t)(code < 0 ? ZIGUX_STATUS_FLAG_ERROR : 0U) }; return s; }
static inline struct zigux_export_status zigux_ok_status(uint16_t facility) { return zigux_make_status(0, facility); }
static inline int zigux_export_status_ok(struct zigux_export_status status) { return (status.flags & (uint16_t)ZIGUX_STATUS_FLAG_ERROR) == 0; }
static inline int zigux_facility_is_known(uint16_t facility) { return facility == 1U || facility == 2U; }
static inline int zigux_export_status_has_known_facility(struct zigux_export_status status) { return zigux_facility_is_known(status.facility); }
#endif
"""
SELFTEST_DEV_T_HEADER_TEXT = """#ifndef ZIGUX_DEV_T_H
#define ZIGUX_DEV_T_H
#include <stdint.h>
#define ZIGUX_DEV_MINOR_BITS 20u
#define ZIGUX_DEV_MINOR_MASK ((1u << ZIGUX_DEV_MINOR_BITS) - 1u)
#define ZIGUX_DEV_MAJOR_MAX ((1u << (32u - ZIGUX_DEV_MINOR_BITS)) - 1u)
struct zigux_dev_t_fields { uint32_t major; uint32_t minor; };
static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(uint32_t major, uint32_t minor) { struct zigux_dev_t_fields fields = { .major = major, .minor = minor }; return fields; }
static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor) { return (major << ZIGUX_DEV_MINOR_BITS) | (minor & ZIGUX_DEV_MINOR_MASK); }
static inline uint32_t zigux_major(uint32_t dev) { return dev >> ZIGUX_DEV_MINOR_BITS; }
static inline uint32_t zigux_minor(uint32_t dev) { return dev & ZIGUX_DEV_MINOR_MASK; }
static inline struct zigux_dev_t_fields zigux_dev_t_fields_from_device_number(uint32_t dev) { return zigux_dev_t_fields_make(zigux_major(dev), zigux_minor(dev)); }
#endif
"""
SELFTEST_LINUX_HEADER = """#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H
#include <stdint.h>
#include <zigux/abi.h>
#include <zigux/dev_t.h>
#define ZIGUX_UAPI_ABI_MAJOR 0u
#define ZIGUX_UAPI_ABI_MINOR 1u
#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u
#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)
struct zigux_uapi_version { uint32_t abi_major; uint32_t abi_minor; uint32_t header_family_revision; };
static inline struct zigux_uapi_version zigux_uapi_version_current(void) { struct zigux_uapi_version version = { .abi_major = ZIGUX_UAPI_ABI_MAJOR, .abi_minor = ZIGUX_UAPI_ABI_MINOR, .header_family_revision = ZIGUX_UAPI_HEADER_FAMILY_REVISION }; return version; }
static inline int zigux_uapi_version_has_current_abi_major(uint32_t abi_major) { return abi_major == ZIGUX_UAPI_ABI_MAJOR; }
static inline int zigux_uapi_version_has_current_abi_minor(uint32_t abi_minor) { return abi_minor == ZIGUX_UAPI_ABI_MINOR; }
static inline int zigux_uapi_version_has_current_header_family_revision(uint32_t header_family_revision) { return header_family_revision == ZIGUX_UAPI_HEADER_FAMILY_REVISION; }
static inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version) { return zigux_uapi_version_has_current_abi_major(version.abi_major) && zigux_uapi_version_has_current_abi_minor(version.abi_minor) && zigux_uapi_version_has_current_header_family_revision(version.header_family_revision); }
static inline struct zigux_export_status zigux_uapi_validate_version(struct zigux_uapi_version version) { if (zigux_uapi_version_matches_current(version)) return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL); return zigux_make_status((int32_t)ZIGUX_UAPI_INVALID_ARGUMENT, (uint16_t)ZIGUX_FACILITY_KERNEL); }
static inline int zigux_uapi_facility_is_known(uint16_t facility) { return zigux_facility_is_known(facility); }
static inline int zigux_uapi_export_status_ok(struct zigux_export_status status) { return zigux_export_status_ok(status); }
static inline int zigux_uapi_export_status_has_known_facility(struct zigux_export_status status) { return zigux_export_status_has_known_facility(status); }
#endif
"""
SELFTEST_SMOKE = """#include <linux/zigux.h>
static int check_version_relays(void) {
    struct zigux_uapi_version current = zigux_uapi_version_current();
    struct zigux_uapi_version stale = current;
    struct zigux_export_status valid = zigux_uapi_validate_version(current);
    struct zigux_export_status invalid;
    if (!zigux_uapi_version_has_current_abi_major(current.abi_major)) return __LINE__;
    if (!zigux_uapi_version_has_current_abi_minor(current.abi_minor)) return __LINE__;
    if (!zigux_uapi_version_has_current_header_family_revision(current.header_family_revision)) return __LINE__;
    if (!zigux_uapi_version_matches_current(current)) return __LINE__;
    if (!zigux_uapi_export_status_ok(valid)) return __LINE__;
    stale.header_family_revision += 1u;
    invalid = zigux_uapi_validate_version(stale);
    if (zigux_uapi_export_status_ok(invalid)) return __LINE__;
    return 0;
}
static int check_status_facility_relays(void) {
    struct zigux_export_status ok = zigux_ok_status((uint16_t)ZIGUX_FACILITY_HELPERS);
    struct zigux_export_status err = zigux_make_status(-22, (uint16_t)ZIGUX_FACILITY_KERNEL);
    struct zigux_export_status unknown = zigux_make_status(0, 9u);
    if (!zigux_uapi_export_status_ok(ok)) return __LINE__;
    if (zigux_uapi_export_status_ok(err)) return __LINE__;
    if (!zigux_uapi_export_status_ok(unknown)) return __LINE__;
    if (!zigux_uapi_export_status_has_known_facility(ok)) return __LINE__;
    return 0;
}
int main(void) { int rc = check_version_relays(); if (rc != 0) return rc; rc = check_status_facility_relays(); if (rc != 0) return rc; return 0; }
"""

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

def _compile_and_run(repo_root: Path, cc: str) -> list[str]:
    issues: list[str] = []
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_c_") as temp_dir:
        exe_path = Path(temp_dir) / "phase3_export_uapi_c_header_smoke"
        compile_result = subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", f"-I{(repo_root / 'include').as_posix()}", (repo_root / SMOKE_PATH).as_posix(), "-o", exe_path.as_posix()], check=False, capture_output=True, text=True)
        if compile_result.returncode != 0:
            issues.append("phase3 export/uapi c header smoke failed to compile: " + compile_result.stderr.strip())
            return issues
        run_result = subprocess.run([exe_path.as_posix()], check=False, capture_output=True, text=True)
        if run_result.returncode != 0:
            issues.append("phase3 export/uapi c header smoke failed at runtime: " + f"exit {run_result.returncode}")
    return issues

def validate_repo(repo_root: Path, cc: str) -> list[str]:
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
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    if issues:
        return issues
    return _compile_and_run(repo_root, cc)

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_export_uapi_c_selftest_") as temp_dir:
        root = Path(temp_dir)
        _write(root / ABI_HEADER_PATH, SELFTEST_ABI_HEADER_TEXT)
        _write(root / DEV_T_HEADER_PATH, SELFTEST_DEV_T_HEADER_TEXT)
        _write(root / LINUX_HEADER_PATH, SELFTEST_LINUX_HEADER)
        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        issues = validate_repo(root, "cc")
        if issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        text = _read(root / SMOKE_PATH).replace("if (!zigux_uapi_export_status_ok(ok))", "", 1)
        _write(root / SMOKE_PATH, text)
        issues = validate_repo(root, "cc")
        expected = "missing zigux/tests/phase3_export_uapi_c_header_smoke.c marker: if (!zigux_uapi_export_status_ok(ok))"
        if expected not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing UAPI status-ok smoke marker was not reported")
            return 1
        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        header = _read(root / LINUX_HEADER_PATH).replace("static inline int zigux_uapi_export_status_ok(struct zigux_export_status status)", "static inline int zigux_uapi_export_status_ok_missing(struct zigux_export_status status)", 1)
        _write(root / LINUX_HEADER_PATH, header)
        issues = validate_repo(root, "cc")
        expected = "missing include/linux/zigux.h marker: static inline int zigux_uapi_export_status_ok(struct zigux_export_status status)"
        if expected not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing UAPI status-ok header marker was not reported")
            return 1
    print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass")
    print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=3")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path('.'))
    parser.add_argument("--cc", default="cc")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = validate_repo(args.repo_root, args.cc)
    if issues:
        print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=fail")
        print("\n".join(issues))
        return 1
    print(f"validated {args.repo_root / SMOKE_PATH}")
    print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())

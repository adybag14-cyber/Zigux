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
        "zigux_uapi_version_has_current_abi_major(",
        "zigux_uapi_version_has_current_abi_minor(",
        "zigux_uapi_version_has_current_header_family_revision(",
        "zigux_uapi_version_matches_current(",
        "zigux_uapi_validate_version(",
        "if (invalid.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
        "static int check_boundary_header_relays(void)",
        "zigux_boundary_header_make(",
        "zigux_boundary_header_make_compatible(",
        "zigux_validate_boundary_header(",
        "zigux_boundary_header_is_current_abi_version(",
        "zigux_boundary_header_is_compatible_size(",
        "zigux_boundary_header_is_canonical_size(",
        "if (!zigux_boundary_header_is_compatible(canonical))",
        "zigux_boundary_header_is_canonical(",
        "zigux_boundary_header_extends_boundary(",
        "zigux_boundary_header_requested_extra_bytes(",
        "if (zigux_boundary_header_requested_extra_bytes(compatible) != 8u)",
        "zigux_boundary_header_canonicalize(",
        "struct zigux_export_status stale_status =",
        "struct zigux_export_status uapi_undersized_status =",
        "struct zigux_export_status uapi_stale_status =",
        "if (stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
        "if (uapi_undersized_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
        "if (uapi_stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
        "if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_compatible) != 12u)",
        "static int check_dev_t_relays(void)",
        "struct zigux_dev_t_fields invalid_major =",
        "struct zigux_dev_t_fields invalid_minor =",
        "zigux_uapi_validate_dev_t_fields(",
        "zigux_uapi_validate_dev_t_components(",
        "zigux_uapi_validate_dev_t_range(",
        "zigux_uapi_dev_t_fields_range_is_valid(",
        "struct zigux_export_status invalid_field_status =",
        "struct zigux_export_status invalid_minor_status =",
        "if (invalid_field_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
        "if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
        "int main(void)",
    ),
    LINUX_HEADER_PATH: (
        "zigux_uapi_version_current(",
        "zigux_uapi_version_has_current_abi_major(",
        "zigux_uapi_version_has_current_abi_minor(",
        "zigux_uapi_version_has_current_header_family_revision(",
        "zigux_uapi_version_matches_current(",
        "zigux_uapi_validate_version(",
        "zigux_uapi_boundary_header_current(",
        "zigux_uapi_boundary_header_compatible(",
        "zigux_uapi_validate_boundary_header(",
        "zigux_uapi_boundary_header_has_current_abi_version(",
        "static inline int zigux_uapi_boundary_header_is_canonical_size(uint32_t size)",
        "static inline int zigux_uapi_boundary_header_is_compatible_size(uint32_t size)",
        "zigux_uapi_boundary_header_is_canonical(",
        "zigux_uapi_boundary_header_is_compatible(",
        "zigux_uapi_boundary_header_extends_boundary(",
        "zigux_uapi_boundary_header_requested_extra_bytes(",
        "zigux_uapi_boundary_header_canonicalize(",
        "zigux_validate_boundary_header(",
        "zigux_boundary_header_make(",
        "zigux_boundary_header_make_compatible(",
        "zigux_boundary_header_is_current_abi_version(",
        "zigux_boundary_header_is_compatible_size(",
        "zigux_boundary_header_is_canonical_size(",
        "zigux_boundary_header_is_compatible(",
        "zigux_boundary_header_is_canonical(",
        "zigux_boundary_header_extends_boundary(",
        "zigux_boundary_header_requested_extra_bytes(",
        "zigux_boundary_header_canonicalize(",
        "zigux_uapi_validate_dev_t_fields(",
        "zigux_uapi_validate_dev_t_components(",
        "zigux_uapi_validate_dev_t_range(",
    ),
}

SELFTEST_ABI_HEADER = """#ifndef _ZIGUX_ABI_H
#define _ZIGUX_ABI_H

#include <stdint.h>

#define ZIGUX_ABI_VERSION 1U
#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_STATUS_FLAG_ERROR 1U

typedef struct zigux_boundary_header {
    uint32_t size;
    uint16_t abi_version;
    uint16_t flags;
} zigux_boundary_header;

struct zigux_export_status {
    int32_t code;
    uint16_t facility;
    uint16_t flags;
};

static inline zigux_boundary_header zigux_default_header(uint16_t flags)
{
    zigux_boundary_header header = {
        .size = (uint32_t)sizeof(zigux_boundary_header),
        .abi_version = (uint16_t)ZIGUX_ABI_VERSION,
        .flags = flags,
    };
    return header;
}

static inline zigux_boundary_header zigux_compatible_header(
    uint32_t size,
    uint16_t flags)
{
    zigux_boundary_header header = zigux_default_header(flags);
    header.size = size;
    return header;
}

static inline int zigux_abi_version_is_current(uint16_t abi_version)
{
    return abi_version == (uint16_t)ZIGUX_ABI_VERSION;
}

static inline int zigux_header_is_canonical(zigux_boundary_header header)
{
    return header.size == (uint32_t)sizeof(zigux_boundary_header) &&
        zigux_abi_version_is_current(header.abi_version);
}

static inline int zigux_header_is_compatible(zigux_boundary_header header)
{
    return header.size >= (uint32_t)sizeof(zigux_boundary_header) &&
        zigux_abi_version_is_current(header.abi_version);
}

static inline int zigux_header_extends_boundary(zigux_boundary_header header)
{
    return zigux_header_is_compatible(header) &&
        !zigux_header_is_canonical(header);
}

static inline uint32_t zigux_header_requested_extra_bytes(
    zigux_boundary_header header)
{
    if (!zigux_header_extends_boundary(header))
        return 0;
    return header.size - (uint32_t)sizeof(zigux_boundary_header);
}

static inline zigux_boundary_header zigux_header_canonicalize(
    zigux_boundary_header header)
{
    header.size = (uint32_t)sizeof(zigux_boundary_header);
    header.abi_version = (uint16_t)ZIGUX_ABI_VERSION;
    return header;
}

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

SELFTEST_DEV_T_HEADER = """#ifndef ZIGUX_DEV_T_H
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

SELFTEST_LINUX_HEADER = """#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#include <stdint.h>

#include <zigux/abi.h>
#include <zigux/dev_t.h>

#define ZIGUX_UAPI_ABI_MAJOR 0u
#define ZIGUX_UAPI_ABI_MINOR 1u
#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u
#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)

struct zigux_uapi_version {
    uint32_t abi_major;
    uint32_t abi_minor;
    uint32_t header_family_revision;
};

static inline struct zigux_uapi_version zigux_uapi_version_current(void)
{
    struct zigux_uapi_version version = {
        .abi_major = ZIGUX_UAPI_ABI_MAJOR,
        .abi_minor = ZIGUX_UAPI_ABI_MINOR,
        .header_family_revision = ZIGUX_UAPI_HEADER_FAMILY_REVISION,
    };
    return version;
}

static inline int zigux_uapi_version_has_current_abi_major(uint32_t abi_major)
{
    return abi_major == ZIGUX_UAPI_ABI_MAJOR;
}

static inline int zigux_uapi_version_has_current_abi_minor(uint32_t abi_minor)
{
    return abi_minor == ZIGUX_UAPI_ABI_MINOR;
}

static inline int zigux_uapi_version_has_current_header_family_revision(
    uint32_t header_family_revision)
{
    return header_family_revision == ZIGUX_UAPI_HEADER_FAMILY_REVISION;
}

static inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version)
{
    return zigux_uapi_version_has_current_abi_major(version.abi_major) &&
        zigux_uapi_version_has_current_abi_minor(version.abi_minor) &&
        zigux_uapi_version_has_current_header_family_revision(version.header_family_revision);
}

static inline struct zigux_export_status zigux_uapi_validate_version(
    struct zigux_uapi_version version)
{
    if (zigux_uapi_version_matches_current(version))
        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);
    return zigux_make_status(
        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,
        (uint16_t)ZIGUX_FACILITY_KERNEL);
}

static inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)
{
    return zigux_default_header(flags);
}

static inline zigux_boundary_header zigux_uapi_boundary_header_compatible(
    uint32_t size,
    uint16_t flags)
{
    zigux_boundary_header header = zigux_uapi_boundary_header_current(flags);
    header.size = size;
    return header;
}

static inline int zigux_uapi_boundary_header_has_current_abi_version(uint16_t abi_version)
{
    return abi_version == (uint16_t)ZIGUX_ABI_VERSION;
}

static inline int zigux_uapi_boundary_header_is_canonical_size(uint32_t size)
{
    return size == (uint32_t)sizeof(zigux_boundary_header);
}

static inline int zigux_uapi_boundary_header_is_compatible_size(uint32_t size)
{
    return size >= (uint32_t)sizeof(zigux_boundary_header);
}

static inline int zigux_uapi_boundary_header_is_canonical(zigux_boundary_header header)
{
    return zigux_uapi_boundary_header_is_canonical_size(header.size) &&
        zigux_uapi_boundary_header_has_current_abi_version(header.abi_version);
}

static inline int zigux_uapi_boundary_header_is_compatible(zigux_boundary_header header)
{
    return zigux_uapi_boundary_header_is_compatible_size(header.size) &&
        zigux_uapi_boundary_header_has_current_abi_version(header.abi_version);
}

static inline int zigux_uapi_boundary_header_extends_boundary(zigux_boundary_header header)
{
    return zigux_uapi_boundary_header_is_compatible(header) &&
        !zigux_uapi_boundary_header_is_canonical(header);
}

static inline uint32_t zigux_uapi_boundary_header_requested_extra_bytes(
    zigux_boundary_header header)
{
    if (!zigux_uapi_boundary_header_extends_boundary(header))
        return 0;
    return header.size - (uint32_t)sizeof(zigux_boundary_header);
}

static inline zigux_boundary_header zigux_uapi_boundary_header_canonicalize(
    zigux_boundary_header header)
{
    header.size = (uint32_t)sizeof(zigux_boundary_header);
    header.abi_version = (uint16_t)ZIGUX_ABI_VERSION;
    return header;
}

static inline struct zigux_export_status zigux_uapi_validate_boundary_header(
    zigux_boundary_header header)
{
    if (zigux_uapi_boundary_header_is_compatible(header))
        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);
    return zigux_make_status(
        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,
        (uint16_t)ZIGUX_FACILITY_KERNEL);
}

static inline struct zigux_export_status zigux_validate_boundary_header(
    zigux_boundary_header header)
{
    return zigux_uapi_validate_boundary_header(header);
}

static inline zigux_boundary_header zigux_boundary_header_make(uint16_t flags)
{
    return zigux_uapi_boundary_header_current(flags);
}

static inline zigux_boundary_header zigux_boundary_header_make_compatible(
    uint32_t size,
    uint16_t flags)
{
    return zigux_uapi_boundary_header_compatible(size, flags);
}

static inline int zigux_boundary_header_is_current_abi_version(uint16_t abi_version)
{
    return zigux_uapi_boundary_header_has_current_abi_version(abi_version);
}

static inline int zigux_boundary_header_is_compatible_size(uint32_t size)
{
    return size >= (uint32_t)sizeof(zigux_boundary_header);
}

static inline int zigux_boundary_header_is_canonical_size(uint32_t size)
{
    return size == (uint32_t)sizeof(zigux_boundary_header);
}

static inline int zigux_boundary_header_is_compatible(zigux_boundary_header header)
{
    return zigux_uapi_boundary_header_is_compatible(header);
}

static inline int zigux_boundary_header_is_canonical(zigux_boundary_header header)
{
    return zigux_uapi_boundary_header_is_canonical(header);
}

static inline int zigux_boundary_header_extends_boundary(zigux_boundary_header header)
{
    return zigux_uapi_boundary_header_extends_boundary(header);
}

static inline uint32_t zigux_boundary_header_requested_extra_bytes(
    zigux_boundary_header header)
{
    return zigux_uapi_boundary_header_requested_extra_bytes(header);
}

static inline zigux_boundary_header zigux_boundary_header_canonicalize(
    zigux_boundary_header header)
{
    return zigux_uapi_boundary_header_canonicalize(header);
}

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

SELFTEST_SMOKE = """#include <linux/zigux.h>

static int check_version_relays(void)
{
    struct zigux_uapi_version current = zigux_uapi_version_current();
    struct zigux_uapi_version stale = current;
    struct zigux_export_status valid = zigux_uapi_validate_version(current);
    struct zigux_export_status invalid;

    if (!zigux_uapi_version_has_current_abi_major(current.abi_major))
        return __LINE__;
    if (!zigux_uapi_version_has_current_abi_minor(current.abi_minor))
        return __LINE__;
    if (!zigux_uapi_version_has_current_header_family_revision(
            current.header_family_revision))
        return __LINE__;
    if (!zigux_uapi_version_matches_current(current))
        return __LINE__;
    if (!zigux_export_status_ok(valid))
        return __LINE__;

    stale.header_family_revision += 1u;
    invalid = zigux_uapi_validate_version(stale);
    if (zigux_uapi_version_matches_current(stale))
        return __LINE__;
    if (zigux_export_status_ok(invalid))
        return __LINE__;
    if (invalid.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;

    return 0;
}

static int check_boundary_header_relays(void)
{
    zigux_boundary_header canonical = zigux_boundary_header_make(0x41u);
    zigux_boundary_header compatible =
        zigux_boundary_header_make_compatible(
            (uint32_t)sizeof(zigux_boundary_header) + 8u,
            0x41u);
    zigux_boundary_header canonicalized =
        zigux_boundary_header_canonicalize(compatible);
    zigux_boundary_header stale = {
        .size = (uint32_t)sizeof(zigux_boundary_header),
        .abi_version = canonical.abi_version + 1u,
        .flags = canonical.flags,
    };
    zigux_boundary_header uapi_canonical =
        zigux_uapi_boundary_header_current(0x52u);
    zigux_boundary_header uapi_compatible =
        zigux_uapi_boundary_header_compatible(
            (uint32_t)sizeof(zigux_boundary_header) + 12u,
            0x52u);
    zigux_boundary_header uapi_canonicalized =
        zigux_uapi_boundary_header_canonicalize(uapi_compatible);
    zigux_boundary_header uapi_undersized = {
        .size = (uint32_t)sizeof(zigux_boundary_header) - 1u,
        .abi_version = uapi_canonical.abi_version,
        .flags = uapi_canonical.flags,
    };
    zigux_boundary_header uapi_stale = {
        .size = (uint32_t)sizeof(zigux_boundary_header),
        .abi_version = uapi_canonical.abi_version + 1u,
        .flags = uapi_canonical.flags,
    };
    struct zigux_export_status canonical_status =
        zigux_validate_boundary_header(canonical);
    struct zigux_export_status compatible_status =
        zigux_validate_boundary_header(compatible);
    struct zigux_export_status stale_status =
        zigux_validate_boundary_header(stale);
    struct zigux_export_status uapi_canonical_status =
        zigux_uapi_validate_boundary_header(uapi_canonical);
    struct zigux_export_status uapi_compatible_status =
        zigux_uapi_validate_boundary_header(uapi_compatible);
    struct zigux_export_status uapi_undersized_status =
        zigux_uapi_validate_boundary_header(uapi_undersized);
    struct zigux_export_status uapi_stale_status =
        zigux_uapi_validate_boundary_header(uapi_stale);
    struct zigux_export_status undersized_status =
        zigux_validate_boundary_header((zigux_boundary_header){
            .size = (uint32_t)sizeof(zigux_boundary_header) - 1u,
            .abi_version = canonical.abi_version,
            .flags = canonical.flags,
        });

    if (!zigux_boundary_header_is_current_abi_version(canonical.abi_version))
        return __LINE__;
    if (!zigux_boundary_header_is_canonical_size(canonical.size))
        return __LINE__;
    if (!zigux_boundary_header_is_compatible_size(canonical.size))
        return __LINE__;
    if (!zigux_boundary_header_is_canonical(canonical))
        return __LINE__;
    if (!zigux_boundary_header_is_compatible(canonical))
        return __LINE__;
    if (!zigux_export_status_ok(canonical_status))
        return __LINE__;
    if (zigux_boundary_header_extends_boundary(canonical))
        return __LINE__;
    if (zigux_boundary_header_requested_extra_bytes(canonical) != 0u)
        return __LINE__;

    if (zigux_boundary_header_is_canonical(compatible))
        return __LINE__;
    if (!zigux_boundary_header_is_compatible(compatible))
        return __LINE__;
    if (!zigux_export_status_ok(compatible_status))
        return __LINE__;
    if (!zigux_boundary_header_extends_boundary(compatible))
        return __LINE__;
    if (zigux_boundary_header_requested_extra_bytes(compatible) != 8u)
        return __LINE__;

    if (zigux_boundary_header_is_current_abi_version(stale.abi_version))
        return __LINE__;
    if (zigux_boundary_header_is_canonical(stale))
        return __LINE__;
    if (zigux_boundary_header_is_compatible(stale))
        return __LINE__;
    if (zigux_export_status_ok(stale_status))
        return __LINE__;
    if (stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;

    if (!zigux_boundary_header_is_canonical(canonicalized))
        return __LINE__;
    if (zigux_boundary_header_extends_boundary(canonicalized))
        return __LINE__;
    if (canonicalized.flags != compatible.flags)
        return __LINE__;

    if (!zigux_uapi_boundary_header_has_current_abi_version(
            uapi_canonical.abi_version))
        return __LINE__;
    if (!zigux_uapi_boundary_header_is_canonical_size(uapi_canonical.size))
        return __LINE__;
    if (!zigux_uapi_boundary_header_is_compatible_size(uapi_canonical.size))
        return __LINE__;
    if (!zigux_uapi_boundary_header_is_canonical(uapi_canonical))
        return __LINE__;
    if (!zigux_uapiBoundary_header_is_compatible(uapi_canonical))
        return __LINE__;
    if (!zigux_export_status_ok(uapi_canonical_status))
        return __LINE__;
    if (zigux_uapi_boundary_header_extends_boundary(uapi_canonical))
        return __LINE__;
    if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_canonical) != 0u)
        return __LINE__;

    if (zigux_uapi_boundary_header_is_canonical_size(uapi_compatible.size))
        return __LINE__;
    if (!zigux_uapi_boundary_header_is_compatible_size(uapi_compatible.size))
        return __LINE__;
    if (zigux_uapi_boundary_header_is_canonical(uapi_compatible))
        return __LINE__;
    if (!zigux_uapi_boundary_header_is_compatible(uapi_compatible))
        return __LINE__;
    if (!zigux_export_status_ok(uapi_compatible_status))
        return __LINE__;
    if (!zigux_uapi_boundary_header_extends_boundary(uapi_compatible))
        return __LINE__;
    if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_compatible) != 12u)
        return __LINE__;

    if (zigux_uapi_boundary_header_is_canonical_size(uapi_undersized.size))
        return __LINE__;
    if (zigux_uapi_boundary_header_is_compatible_size(uapi_undersized.size))
        return __LINE__;
    if (zigux_export_status_ok(uapi_undersized_status))
        return __LINE__;
    if (uapi_undersized_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;

    if (zigux_uapi_boundary_header_has_current_abi_version(uapi_stale.abi_version))
        return __LINE__;
    if (zigux_uapi_boundary_header_is_canonical(uapi_stale))
        return __LINE__;
    if (zigux_uapi_boundary_header_is_compatible(uapi_stale))
        return __LINE__;
    if (zigux_export_status_ok(uapi_stale_status))
        return __LINE__;
    if (uapi_stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;

    if (!zigux_uapi_boundary_header_is_canonical(uapi_canonicalized))
        return __LINE__;
    if (zigux_uapi_boundary_header_extends_boundary(uapi_canonicalized))
        return __LINE__;
    if (uapi_canonicalized.flags != uapi_compatible.flags)
        return __LINE__;

    if (uapi_canonical.size != canonical.size)
        return __LINE__;
    if (uapi_canonical.abi_version != canonical.abi_version)
        return __LINE__;

    if (zigux_export_status_ok(undersized_status))
        return __LINE__;
    if (undersized_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;

    return 0;
}

static int check_dev_t_relays(void)
{
    struct zigux_dev_t_fields valid = zigux_dev_t_fields_make(11u, 29u);
    struct zigux_dev_t_fields start = zigux_dev_t_fields_make(11u, 28u);
    struct zigux_dev_t_fields end = zigux_dev_t_fields_make(11u, 29u);
    struct zigux_dev_t_fields invalid_major =
        zigux_dev_t_fields_make(ZIGUX_DEV_MAJOR_MAX + 1u, 0u);
    struct zigux_dev_t_fields invalid_minor =
        zigux_dev_t_fields_make(0u, ZIGUX_DEV_MINOR_MASK + 1u);
    struct zigux_export_status valid_status =
        zigux_uapi_validate_dev_t_fields(valid);
    struct zigux_export_status invalid_field_status =
        zigux_uapi_validate_dev_t_fields(invalid_major);
    struct zigux_export_status invalid_minor_status =
        zigux_uapi_validate_dev_t_fields(invalid_minor);
    struct zigux_export_status invalid_components =
        zigux_uapi_validate_dev_t_components(ZIGUX_DEV_MAJOR_MAX + 1u, 0u);
    struct zigux_export_status range_status =
        zigux_uapi_validate_dev_t_range(start, end);
    struct zigux_export_status invalid_range =
        zigux_uapi_validate_dev_t_range(end, start);

    if (!zigux_uapi_dev_t_fields_is_valid(valid))
        return __LINE__;
    if (zigux_uapi_dev_t_fields_is_valid(invalid_major))
        return __LINE__;
    if (zigux_uapi_dev_t_fields_is_valid(invalid_minor))
        return __LINE__;
    if (!zigux_uapi_dev_t_fields_range_is_valid(start, end))
        return __LINE__;
    if (!zigux_export_status_ok(valid_status))
        return __LINE__;
    if (zigux_export_status_ok(invalid_field_status))
        return __LINE__;
    if (invalid_field_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (zigux_export_status_ok(invalid_minor_status))
        return __LINE__;
    if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (zigux_export_status_ok(invalid_components))
        return __LINE__;
    if (!zigux_export_status_ok(range_status))
        return __LINE__;
    if (zigux_export_status_ok(invalid_range))
        return __LINE__;
    if (invalid_range.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;

    return 0;
}

int main(void)
{
    int rc = check_version_relays();
    if (rc != 0)
        return rc;

    rc = check_boundary_header_relays();
    if (rc != 0)
        return rc;

    rc = check_dev_t_relays();
    if (rc != 0)
        return rc;

    return 0;
}
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
        compile_result = subprocess.run(
            [
                cc,
                "-std=c11",
                "-Wall",
                "-Wextra",
                "-Werror",
                f"-I{(repo_root / 'include').as_posix()}",
                (repo_root / SMOKE_PATH).as_posix(),
                "-o",
                exe_path.as_posix(),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            issues.append(
                "phase3 export/uapi c header smoke failed to compile: "
                + compile_result.stderr.strip()
            )
            return issues

        run_result = subprocess.run(
            [exe_path.as_posix()],
            check=False,
            capture_output=True,
            text=True,
        )
        if run_result.returncode != 0:
            issues.append(
                "phase3 export/uapi c header smoke failed at runtime: "
                + f"exit {run_result.returncode}"
            )
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
        _write(root / ABI_HEADER_PATH, SELFTEST_ABI_HEADER)
        _write(root / DEV_T_HEADER_PATH, SELFTEST_DEV_T_HEADER)
        _write(root / LINUX_HEADER_PATH, SELFTEST_LINUX_HEADER)
        _write(root / SMOKE_PATH, SELFTEST_SMOKE)

        issues = validate_repo(root, "cc")
        if issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        version_major_marker_text = _read(root / SMOKE_PATH).replace(
            "zigux_uapi_version_has_current_abi_major(",
            "zigux_uapi_version_has_current_abi_major_missing(",
            1,
        )
        _write(root / SMOKE_PATH, version_major_marker_text)
        issues = validate_repo(root, "cc")
        expected_version_major_marker = (
            "missing zigux/tests/phase3_export_uapi_c_header_smoke.c marker: "
            "zigux_uapi_version_has_current_abi_major("
        )
        if expected_version_major_marker not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing version-major relay marker was not reported")
            return 1

        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        missing_version_status_marker_text = _read(root / SMOKE_PATH).replace(
            "if (invalid.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
            "",
            1,
        )
        _write(root / SMOKE_PATH, missing_version_status_marker_text)
        issues = validate_repo(root, "cc")
        expected_version_status_marker = (
            "missing zigux/tests/phase3_export_uapi_c_header_smoke.c marker: "
            "if (invalid.code != ZIGUX_UAPI_INVALID_ARGUMENT)"
        )
        if expected_version_status_marker not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing version-status marker was not reported")
            return 1

        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        missing_marker_text = _read(root / SMOKE_PATH).replace(
            "if (!zigux_boundary_header_is_compatible(canonical))",
            "",
            1,
        )
        _write(root / SMOKE_PATH, missing_marker_text)
        issues = validate_repo(root, "cc")
        expected_marker = (
            "missing zigux/tests/phase3_export_uapi_c_header_smoke.c marker: "
            "if (!zigux_boundary_header_is_compatible(canonical))"
        )
        if expected_marker not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing smoke marker was not reported")
            return 1

        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        missing_stale_marker_text = _read(root / SMOKE_PATH).replace(
            "if (uapi_stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
            "",
            1,
        )
        _write(root / SMOKE_PATH, missing_stale_marker_text)
        issues = validate_repo(root, "cc")
        expected_stale_marker = (
            "missing zigux/tests/phase3_export_uapi_c_header_smoke.c marker: "
            "if (uapi_stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)"
        )
        if expected_stale_marker not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing stale boundary-header status marker was not reported")
            return 1

        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        missing_field_marker_text = _read(root / SMOKE_PATH).replace(
            "if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)",
            "",
            1,
        )
        _write(root / SMOKE_PATH, missing_field_marker_text)
        issues = validate_repo(root, "cc")
        expected_field_marker = (
            "missing zigux/tests/phase3_export_uapi_c_header_smoke.c marker: "
            "if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)"
        )
        if expected_field_marker not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing invalid dev_t field status marker was not reported")
            return 1

        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        broken_header = _read(root / LINUX_HEADER_PATH).replace(
            "static inline int zigux_uapi_boundary_header_is_canonical_size(uint32_t size)",
            "static inline int zigux_uapi_boundary_header_is_canonical_size_missing(uint32_t size)",
            1,
        )
        _write(root / LINUX_HEADER_PATH, broken_header)
        issues = validate_repo(root, "cc")
        expected_header = (
            "missing include/linux/zigux.h marker: "
            "static inline int zigux_uapi_boundary_header_is_canonical_size(uint32_t size)"
        )
        if expected_header not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing uapi boundary-header helper marker was not reported")
            return 1

        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        missing_extra_bytes_marker_text = _read(root / SMOKE_PATH).replace(
            "if (zigux_boundary_header_requested_extra_bytes(compatible) != 8u)",
            "",
            1,
        )
        _write(root / SMOKE_PATH, missing_extra_bytes_marker_text)
        issues = validate_repo(root, "cc")
        expected_extra_bytes_marker = (
            "missing zigux/tests/phase3_export_uapi_c_header_smoke.c marker: "
            "if (zigux_boundary_header_requested_extra_bytes(compatible) != 8u)"
        )
        if expected_extra_bytes_marker not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing boundary-header extension accounting marker was not reported")
            return 1

        _write(root / SMOKE_PATH, SELFTEST_SMOKE)
        missing_uapi_extra_bytes_marker_text = _read(root / SMOKE_PATH).replace(
            "if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_compatible) != 12u)",
            "",
            1,
        )
        _write(root / SMOKE_PATH, missing_uapi_extra_bytes_marker_text)
        issues = validate_repo(root, "cc")
        expected_uapi_extra_bytes_marker = (
            "missing zigux/tests/phase3_export_uapi_c_header_smoke.c marker: "
            "if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_compatible) != 12u)"
        )
        if expected_uapi_extra_bytes_marker not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing uapi boundary-header extension accounting marker was not reported")
            return 1

        _write(root / LINUX_HEADER_PATH, SELFTEST_LINUX_HEADER)
        broken_header = _read(root / LINUX_HEADER_PATH).replace(
            "zigux_uapi_validate_dev_t_range(",
            "zigux_uapi_validate_dev_t_range_missing(",
            1,
        )
        _write(root / LINUX_HEADER_PATH, broken_header)
        issues = validate_repo(root, "cc")
        expected_header = (
            "missing include/linux/zigux.h marker: "
            "zigux_uapi_validate_dev_t_range("
        )
        if expected_header not in issues:
            print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=fail")
            print("expected missing header helper marker was not reported")
            return 1

    print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass")
    print("PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST_CASE_COUNT=10")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compile and run the current Phase 3 export/UAPI C header smoke."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains include/ and zigux/tests/",
    )
    parser.add_argument(
        "--cc",
        default="cc",
        help="C compiler to use for the focused smoke build",
    )
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
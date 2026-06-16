const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE=pass";
pub const self_test_pass_marker = "PHASE3_EXPORT_UAPI_C_HEADER_SMOKE_SELF_TEST=pass";

const REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_c_header_smoke_c = [_][]const u8{
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
};

const REQUIRED_MARKERS__include_linux_zigux_h = [_][]const u8{
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
};

const SELFTEST_ABI_HEADER = [_][]const u8{
    "#ifndef _ZIGUX_ABI_H\n#define _ZIGUX_ABI_H\n\n#include <stdint.h>\n\n#define ZIGUX_ABI_VERSION 1U\n#define ZIGUX_FACILITY_KERNEL 1U\n#define ZIGUX_STATUS_FLAG_ERROR 1U\n\ntypedef struct zigux_boundary_header {\n    uint32_t size;\n    uint16_t abi_version;\n    uint16_t flags;\n} zigux_boundary_header;\n\nstruct zigux_export_status {\n    int32_t code;\n    uint16_t facility;\n    uint16_t flags;\n};\n\nstatic inline zigux_boundary_header zigux_default_header(uint16_t flags)\n{\n    zigux_boundary_header header = {\n        .size = (uint32_t)sizeof(zigux_boundary_header),\n        .abi_version = (uint16_t)ZIGUX_ABI_VERSION,\n        .flags = flags,\n    };\n    return header;\n}\n\nstatic inline zigux_boundary_header zigux_compatible_header(\n    uint32_t size,\n    uint16_t flags)\n{\n    zigux_boundary_header header = zigux_default_header(flags);\n    header.size = size;\n    return header;\n}\n\nstatic inline int zigux_abi_version_is_current(uint16_t abi_version)\n{\n    return abi_version == (uint16_t)ZIGUX_ABI_VERSION;\n}\n\nstatic inline int zigux_header_is_canonical(zigux_boundary_header header)\n{\n    return header.size == (uint32_t)sizeof(zigux_boundary_header) &&\n        zigux_abi_version_is_current(header.abi_version);\n}\n\nstatic inline int zigux_header_is_compatible(zigux_boundary_header header)\n{\n    return header.size >= (uint32_t)sizeof(zigux_boundary_header) &&\n        zigux_abi_version_is_current(header.abi_version);\n}\n\nstatic inline int zigux_header_extends_boundary(zigux_boundary_header header)\n{\n    return zigux_header_is_compatible(header) &&\n        !zigux_header_is_canonical(header);\n}\n\nstatic inline uint32_t zigux_header_requested_extra_bytes(\n    zigux_boundary_header header)\n{\n    if (!zigux_header_extends_boundary(header))\n        return 0;\n    return header.size - (uint32_t)sizeof(zigux_boundary_header);\n}\n\nstatic inline zigux_boundary_header zigux_header_canonicalize(\n    zigux_boundary_header header)\n{\n    header.size = (uint32_t)sizeof(zigux_boundary_header);\n    header.abi_version = (uint16_t)ZIGUX_ABI_VERSION;\n    return header;\n}\n\nstatic inline struct zigux_export_status zigux_make_status(\n    int32_t code,\n    uint16_t facility)\n{\n    struct zigux_export_status status = {\n        .code = code,\n        .facility = facility,\n        .flags = (uint16_t)(code < 0 ? ZIGUX_STATUS_FLAG_ERROR : 0U),\n    };\n    return status;\n}\n\nstatic inline struct zigux_export_status zigux_ok_status(uint16_t facility)\n{\n    return zigux_make_status(0, facility);\n}\n\nstatic inline int zigux_export_status_ok(struct zigux_export_status status)\n{\n    return (status.flags & (uint16_t)ZIGUX_STATUS_FLAG_ERROR) == 0;\n}\n\n#endif\n",
};

const SELFTEST_DEV_T_HEADER = [_][]const u8{
    "#ifndef ZIGUX_DEV_T_H\n#define ZIGUX_DEV_T_H\n\n#include <stdint.h>\n\n#define ZIGUX_DEV_MINOR_BITS 20u\n#define ZIGUX_DEV_MINOR_MASK ((1u << ZIGUX_DEV_MINOR_BITS) - 1u)\n#define ZIGUX_DEV_MAJOR_MAX ((1u << (32u - ZIGUX_DEV_MINOR_BITS)) - 1u)\n\nstruct zigux_dev_t_fields {\n    uint32_t major;\n    uint32_t minor;\n};\n\nstatic inline struct zigux_dev_t_fields zigux_dev_t_fields_make(\n    uint32_t major,\n    uint32_t minor)\n{\n    struct zigux_dev_t_fields fields = {\n        .major = major,\n        .minor = minor,\n    };\n    return fields;\n}\n\nstatic inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)\n{\n    return fields.major <= ZIGUX_DEV_MAJOR_MAX &&\n        fields.minor <= ZIGUX_DEV_MINOR_MASK;\n}\n\nstatic inline int zigux_dev_t_fields_range_is_valid(\n    struct zigux_dev_t_fields start,\n    struct zigux_dev_t_fields end)\n{\n    if (!zigux_dev_t_fields_is_valid(start) || !zigux_dev_t_fields_is_valid(end))\n        return 0;\n    return start.major < end.major ||\n        (start.major == end.major && start.minor <= end.minor);\n}\n\n#endif\n",
};

const SELFTEST_LINUX_HEADER = [_][]const u8{
    "#ifndef _LINUX_ZIGUX_H\n#define _LINUX_ZIGUX_H\n\n#include <stdint.h>\n\n#include <zigux/abi.h>\n#include <zigux/dev_t.h>\n\n#define ZIGUX_UAPI_ABI_MAJOR 0u\n#define ZIGUX_UAPI_ABI_MINOR 1u\n#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u\n#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)\n\nstruct zigux_uapi_version {\n    uint32_t abi_major;\n    uint32_t abi_minor;\n    uint32_t header_family_revision;\n};\n\nstatic inline struct zigux_uapi_version zigux_uapi_version_current(void)\n{\n    struct zigux_uapi_version version = {\n        .abi_major = ZIGUX_UAPI_ABI_MAJOR,\n        .abi_minor = ZIGUX_UAPI_ABI_MINOR,\n        .header_family_revision = ZIGUX_UAPI_HEADER_FAMILY_REVISION,\n    };\n    return version;\n}\n\nstatic inline int zigux_uapi_version_has_current_abi_major(uint32_t abi_major)\n{\n    return abi_major == ZIGUX_UAPI_ABI_MAJOR;\n}\n\nstatic inline int zigux_uapi_version_has_current_abi_minor(uint32_t abi_minor)\n{\n    return abi_minor == ZIGUX_UAPI_ABI_MINOR;\n}\n\nstatic inline int zigux_uapi_version_has_current_header_family_revision(\n    uint32_t header_family_revision)\n{\n    return header_family_revision == ZIGUX_UAPI_HEADER_FAMILY_REVISION;\n}\n\nstatic inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version)\n{\n    return zigux_uapi_version_has_current_abi_major(version.abi_major) &&\n        zigux_uapi_version_has_current_abi_minor(version.abi_minor) &&\n        zigux_uapi_version_has_current_header_family_revision(version.header_family_revision);\n}\n\nstatic inline struct zigux_export_status zigux_uapi_validate_version(\n    struct zigux_uapi_version version)\n{\n    if (zigux_uapi_version_matches_current(version))\n        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);\n    return zigux_make_status(\n        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,\n        (uint16_t)ZIGUX_FACILITY_KERNEL);\n}\n\nstatic inline zigux_boundary_header zigux_uapi_boundary_header_current(uint16_t flags)\n{\n    return zigux_default_header(flags);\n}\n\nstatic inline zigux_boundary_header zigux_uapi_boundary_header_compatible(\n    uint32_t size,\n    uint16_t flags)\n{\n    zigux_boundary_header header = zigux_uapi_boundary_header_current(flags);\n    header.size = size;\n    return header;\n}\n\nstatic inline int zigux_uapi_boundary_header_has_current_abi_version(uint16_t abi_version)\n{\n    return abi_version == (uint16_t)ZIGUX_ABI_VERSION;\n}\n\nstatic inline int zigux_uapi_boundary_header_is_canonical_size(uint32_t size)\n{\n    return size == (uint32_t)sizeof(zigux_boundary_header);\n}\n\nstatic inline int zigux_uapi_boundary_header_is_compatible_size(uint32_t size)\n{\n    return size >= (uint32_t)sizeof(zigux_boundary_header);\n}\n\nstatic inline int zigux_uapi_boundary_header_is_canonical(zigux_boundary_header header)\n{\n    return zigux_uapi_boundary_header_is_canonical_size(header.size) &&\n        zigux_uapi_boundary_header_has_current_abi_version(header.abi_version);\n}\n\nstatic inline int zigux_uapi_boundary_header_is_compatible(zigux_boundary_header header)\n{\n    return zigux_uapi_boundary_header_is_compatible_size(header.size) &&\n        zigux_uapi_boundary_header_has_current_abi_version(header.abi_version);\n}\n\nstatic inline int zigux_uapi_boundary_header_extends_boundary(zigux_boundary_header header)\n{\n    return zigux_uapi_boundary_header_is_compatible(header) &&\n        !zigux_uapi_boundary_header_is_canonical(header);\n}\n\nstatic inline uint32_t zigux_uapi_boundary_header_requested_extra_bytes(\n    zigux_boundary_header header)\n{\n    if (!zigux_uapi_boundary_header_extends_boundary(header))\n        return 0;\n    return header.size - (uint32_t)sizeof(zigux_boundary_header);\n}\n\nstatic inline zigux_boundary_header zigux_uapi_boundary_header_canonicalize(\n    zigux_boundary_header header)\n{\n    header.size = (uint32_t)sizeof(zigux_boundary_header);\n    header.abi_version = (uint16_t)ZIGUX_ABI_VERSION;\n    return header;\n}\n\nstatic inline struct zigux_export_status zigux_uapi_validate_boundary_header(\n    zigux_boundary_header header)\n{\n    if (zigux_uapi_boundary_header_is_compatible(header))\n        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);\n    return zigux_make_status(\n        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,\n        (uint16_t)ZIGUX_FACILITY_KERNEL);\n}\n\nstatic inline struct zigux_export_status zigux_validate_boundary_header(\n    zigux_boundary_header header)\n{\n    return zigux_uapi_validate_boundary_header(header);\n}\n\nstatic inline zigux_boundary_header zigux_boundary_header_make(uint16_t flags)\n{\n    return zigux_uapi_boundary_header_current(flags);\n}\n\nstatic inline zigux_boundary_header zigux_boundary_header_make_compatible(\n    uint32_t size,\n    uint16_t flags)\n{\n    return zigux_uapi_boundary_header_compatible(size, flags);\n}\n\nstatic inline int zigux_boundary_header_is_current_abi_version(uint16_t abi_version)\n{\n    return zigux_uapi_boundary_header_has_current_abi_version(abi_version);\n}\n\nstatic inline int zigux_boundary_header_is_compatible_size(uint32_t size)\n{\n    return size >= (uint32_t)sizeof(zigux_boundary_header);\n}\n\nstatic inline int zigux_boundary_header_is_canonical_size(uint32_t size)\n{\n    return size == (uint32_t)sizeof(zigux_boundary_header);\n}\n\nstatic inline int zigux_boundary_header_is_compatible(zigux_boundary_header header)\n{\n    return zigux_uapi_boundary_header_is_compatible(header);\n}\n\nstatic inline int zigux_boundary_header_is_canonical(zigux_boundary_header header)\n{\n    return zigux_uapi_boundary_header_is_canonical(header);\n}\n\nstatic inline int zigux_boundary_header_extends_boundary(zigux_boundary_header header)\n{\n    return zigux_uapi_boundary_header_extends_boundary(header);\n}\n\nstatic inline uint32_t zigux_boundary_header_requested_extra_bytes(\n    zigux_boundary_header header)\n{\n    return zigux_uapi_boundary_header_requested_extra_bytes(header);\n}\n\nstatic inline zigux_boundary_header zigux_boundary_header_canonicalize(\n    zigux_boundary_header header)\n{\n    return zigux_uapi_boundary_header_canonicalize(header);\n}\n\nstatic inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)\n{\n    return zigux_dev_t_fields_is_valid(fields);\n}\n\nstatic inline struct zigux_export_status zigux_uapi_validate_dev_t_fields(\n    struct zigux_dev_t_fields fields)\n{\n    if (zigux_uapi_dev_t_fields_is_valid(fields))\n        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);\n    return zigux_make_status(\n        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,\n        (uint16_t)ZIGUX_FACILITY_KERNEL);\n}\n\nstatic inline struct zigux_export_status zigux_uapi_validate_dev_t_components(\n    uint32_t major,\n    uint32_t minor)\n{\n    return zigux_uapi_validate_dev_t_fields(zigux_dev_t_fields_make(major, minor));\n}\n\nstatic inline int zigux_uapi_dev_t_fields_range_is_valid(\n    struct zigux_dev_t_fields start,\n    struct zigux_dev_t_fields end)\n{\n    return zigux_dev_t_fields_range_is_valid(start, end);\n}\n\nstatic inline struct zigux_export_status zigux_uapi_validate_dev_t_range(\n    struct zigux_dev_t_fields start,\n    struct zigux_dev_t_fields end)\n{\n    if (zigux_uapi_dev_t_fields_range_is_valid(start, end))\n        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);\n    return zigux_make_status(\n        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,\n        (uint16_t)ZIGUX_FACILITY_KERNEL);\n}\n\n#endif\n",
};

const SELFTEST_SMOKE = [_][]const u8{
    "#include <linux/zigux.h>\n\nstatic int check_version_relays(void)\n{\n    struct zigux_uapi_version current = zigux_uapi_version_current();\n    struct zigux_uapi_version stale = current;\n    struct zigux_export_status valid = zigux_uapi_validate_version(current);\n    struct zigux_export_status invalid;\n\n    if (!zigux_uapi_version_has_current_abi_major(current.abi_major))\n        return __LINE__;\n    if (!zigux_uapi_version_has_current_abi_minor(current.abi_minor))\n        return __LINE__;\n    if (!zigux_uapi_version_has_current_header_family_revision(\n            current.header_family_revision))\n        return __LINE__;\n    if (!zigux_uapi_version_matches_current(current))\n        return __LINE__;\n    if (!zigux_export_status_ok(valid))\n        return __LINE__;\n\n    stale.header_family_revision += 1u;\n    invalid = zigux_uapi_validate_version(stale);\n    if (zigux_uapi_version_matches_current(stale))\n        return __LINE__;\n    if (zigux_export_status_ok(invalid))\n        return __LINE__;\n    if (invalid.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n\n    return 0;\n}\n\nstatic int check_boundary_header_relays(void)\n{\n    zigux_boundary_header canonical = zigux_boundary_header_make(0x41u);\n    zigux_boundary_header compatible =\n        zigux_boundary_header_make_compatible(\n            (uint32_t)sizeof(zigux_boundary_header) + 8u,\n            0x41u);\n    zigux_boundary_header canonicalized =\n        zigux_boundary_header_canonicalize(compatible);\n    zigux_boundary_header stale = {\n        .size = (uint32_t)sizeof(zigux_boundary_header),\n        .abi_version = canonical.abi_version + 1u,\n        .flags = canonical.flags,\n    };\n    zigux_boundary_header uapi_canonical =\n        zigux_uapi_boundary_header_current(0x52u);\n    zigux_boundary_header uapi_compatible =\n        zigux_uapi_boundary_header_compatible(\n            (uint32_t)sizeof(zigux_boundary_header) + 12u,\n            0x52u);\n    zigux_boundary_header uapi_canonicalized =\n        zigux_uapi_boundary_header_canonicalize(uapi_compatible);\n    zigux_boundary_header uapi_undersized = {\n        .size = (uint32_t)sizeof(zigux_boundary_header) - 1u,\n        .abi_version = uapi_canonical.abi_version,\n        .flags = uapi_canonical.flags,\n    };\n    zigux_boundary_header uapi_stale = {\n        .size = (uint32_t)sizeof(zigux_boundary_header),\n        .abi_version = uapi_canonical.abi_version + 1u,\n        .flags = uapi_canonical.flags,\n    };\n    struct zigux_export_status canonical_status =\n        zigux_validate_boundary_header(canonical);\n    struct zigux_export_status compatible_status =\n        zigux_validate_boundary_header(compatible);\n    struct zigux_export_status stale_status =\n        zigux_validate_boundary_header(stale);\n    struct zigux_export_status uapi_canonical_status =\n        zigux_uapi_validate_boundary_header(uapi_canonical);\n    struct zigux_export_status uapi_compatible_status =\n        zigux_uapi_validate_boundary_header(uapi_compatible);\n    struct zigux_export_status uapi_undersized_status =\n        zigux_uapi_validate_boundary_header(uapi_undersized);\n    struct zigux_export_status uapi_stale_status =\n        zigux_uapi_validate_boundary_header(uapi_stale);\n    struct zigux_export_status undersized_status =\n        zigux_validate_boundary_header((zigux_boundary_header){\n            .size = (uint32_t)sizeof(zigux_boundary_header) - 1u,\n            .abi_version = canonical.abi_version,\n            .flags = canonical.flags,\n        });\n\n    if (!zigux_boundary_header_is_current_abi_version(canonical.abi_version))\n        return __LINE__;\n    if (!zigux_boundary_header_is_canonical_size(canonical.size))\n        return __LINE__;\n    if (!zigux_boundary_header_is_compatible_size(canonical.size))\n        return __LINE__;\n    if (!zigux_boundary_header_is_canonical(canonical))\n        return __LINE__;\n    if (!zigux_boundary_header_is_compatible(canonical))\n        return __LINE__;\n    if (!zigux_export_status_ok(canonical_status))\n        return __LINE__;\n    if (zigux_boundary_header_extends_boundary(canonical))\n        return __LINE__;\n    if (zigux_boundary_header_requested_extra_bytes(canonical) != 0u)\n        return __LINE__;\n\n    if (zigux_boundary_header_is_canonical(compatible))\n        return __LINE__;\n    if (!zigux_boundary_header_is_compatible(compatible))\n        return __LINE__;\n    if (!zigux_export_status_ok(compatible_status))\n        return __LINE__;\n    if (!zigux_boundary_header_extends_boundary(compatible))\n        return __LINE__;\n    if (zigux_boundary_header_requested_extra_bytes(compatible) != 8u)\n        return __LINE__;\n\n    if (zigux_boundary_header_is_current_abi_version(stale.abi_version))\n        return __LINE__;\n    if (zigux_boundary_header_is_canonical(stale))\n        return __LINE__;\n    if (zigux_boundary_header_is_compatible(stale))\n        return __LINE__;\n    if (zigux_export_status_ok(stale_status))\n        return __LINE__;\n    if (stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n\n    if (!zigux_boundary_header_is_canonical(canonicalized))\n        return __LINE__;\n    if (zigux_boundary_header_extends_boundary(canonicalized))\n        return __LINE__;\n    if (canonicalized.flags != compatible.flags)\n        return __LINE__;\n\n    if (!zigux_uapi_boundary_header_has_current_abi_version(\n            uapi_canonical.abi_version))\n        return __LINE__;\n    if (!zigux_uapi_boundary_header_is_canonical_size(uapi_canonical.size))\n        return __LINE__;\n    if (!zigux_uapi_boundary_header_is_compatible_size(uapi_canonical.size))\n        return __LINE__;\n    if (!zigux_uapi_boundary_header_is_canonical(uapi_canonical))\n        return __LINE__;\n    if (!zigux_uapi_boundary_header_is_compatible(uapi_canonical))\n        return __LINE__;\n    if (!zigux_export_status_ok(uapi_canonical_status))\n        return __LINE__;\n    if (zigux_uapi_boundary_header_extends_boundary(uapi_canonical))\n        return __LINE__;\n    if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_canonical) != 0u)\n        return __LINE__;\n\n    if (zigux_uapi_boundary_header_is_canonical_size(uapi_compatible.size))\n        return __LINE__;\n    if (!zigux_uapi_boundary_header_is_compatible_size(uapi_compatible.size))\n        return __LINE__;\n    if (zigux_uapi_boundary_header_is_canonical(uapi_compatible))\n        return __LINE__;\n    if (!zigux_uapi_boundary_header_is_compatible(uapi_compatible))\n        return __LINE__;\n    if (!zigux_export_status_ok(uapi_compatible_status))\n        return __LINE__;\n    if (!zigux_uapi_boundary_header_extends_boundary(uapi_compatible))\n        return __LINE__;\n    if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_compatible) != 12u)\n        return __LINE__;\n\n    if (zigux_uapi_boundary_header_is_canonical_size(uapi_undersized.size))\n        return __LINE__;\n    if (zigux_uapi_boundary_header_is_compatible_size(uapi_undersized.size))\n        return __LINE__;\n    if (zigux_export_status_ok(uapi_undersized_status))\n        return __LINE__;\n    if (uapi_undersized_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n\n    if (zigux_uapi_boundary_header_has_current_abi_version(uapi_stale.abi_version))\n        return __LINE__;\n    if (zigux_uapi_boundary_header_is_canonical(uapi_stale))\n        return __LINE__;\n    if (zigux_uapi_boundary_header_is_compatible(uapi_stale))\n        return __LINE__;\n    if (zigux_export_status_ok(uapi_stale_status))\n        return __LINE__;\n    if (uapi_stale_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n\n    if (!zigux_uapi_boundary_header_is_canonical(uapi_canonicalized))\n        return __LINE__;\n    if (zigux_uapi_boundary_header_extends_boundary(uapi_canonicalized))\n        return __LINE__;\n    if (uapi_canonicalized.flags != uapi_compatible.flags)\n        return __LINE__;\n\n    if (uapi_canonical.size != canonical.size)\n        return __LINE__;\n    if (uapi_canonical.abi_version != canonical.abi_version)\n        return __LINE__;\n\n    if (zigux_export_status_ok(undersized_status))\n        return __LINE__;\n    if (undersized_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n\n    return 0;\n}\n\nstatic int check_dev_t_relays(void)\n{\n    struct zigux_dev_t_fields valid = zigux_dev_t_fields_make(11u, 29u);\n    struct zigux_dev_t_fields start = zigux_dev_t_fields_make(11u, 28u);\n    struct zigux_dev_t_fields end = zigux_dev_t_fields_make(11u, 29u);\n    struct zigux_dev_t_fields invalid_major =\n        zigux_dev_t_fields_make(ZIGUX_DEV_MAJOR_MAX + 1u, 0u);\n    struct zigux_dev_t_fields invalid_minor =\n        zigux_dev_t_fields_make(0u, ZIGUX_DEV_MINOR_MASK + 1u);\n    struct zigux_export_status valid_status =\n        zigux_uapi_validate_dev_t_fields(valid);\n    struct zigux_export_status invalid_field_status =\n        zigux_uapi_validate_dev_t_fields(invalid_major);\n    struct zigux_export_status invalid_minor_status =\n        zigux_uapi_validate_dev_t_fields(invalid_minor);\n    struct zigux_export_status invalid_components =\n        zigux_uapi_validate_dev_t_components(ZIGUX_DEV_MAJOR_MAX + 1u, 0u);\n    struct zigux_export_status range_status =\n        zigux_uapi_validate_dev_t_range(start, end);\n    struct zigux_export_status invalid_range =\n        zigux_uapi_validate_dev_t_range(end, start);\n\n    if (!zigux_uapi_dev_t_fields_is_valid(valid))\n        return __LINE__;\n    if (zigux_uapi_dev_t_fields_is_valid(invalid_major))\n        return __LINE__;\n    if (zigux_uapi_dev_t_fields_is_valid(invalid_minor))\n        return __LINE__;\n    if (!zigux_uapi_dev_t_fields_range_is_valid(start, end))\n        return __LINE__;\n    if (!zigux_export_status_ok(valid_status))\n        return __LINE__;\n    if (zigux_export_status_ok(invalid_field_status))\n        return __LINE__;\n    if (invalid_field_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n    if (zigux_export_status_ok(invalid_minor_status))\n        return __LINE__;\n    if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n    if (zigux_export_status_ok(invalid_components))\n        return __LINE__;\n    if (!zigux_export_status_ok(range_status))\n        return __LINE__;\n    if (zigux_export_status_ok(invalid_range))\n        return __LINE__;\n    if (invalid_range.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n\n    return 0;\n}\n\nint main(void)\n{\n    int rc = check_version_relays();\n    if (rc != 0)\n        return rc;\n\n    rc = check_boundary_header_relays();\n    if (rc != 0)\n        return rc;\n\n    rc = check_dev_t_relays();\n    if (rc != 0)\n        return rc;\n\n    return 0;\n}\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c_path = try guard.joinPath(allocator, root, "zigux/tests/phase3/export/uapi/c/header/smoke/c");
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c_path);
    const text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c = try guard.readUtf8File(io, allocator, text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c_path);
    defer allocator.free(text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c);
    for (REQUIRED_MARKERS__zigux_tests_phase3_export_uapi_c_header_smoke_c) |marker| try guard.requireMarker(text_required_markers__zigux_tests_phase3_export_uapi_c_header_smoke_c, marker);
    const text_required_markers__include_linux_zigux_h_path = try guard.joinPath(allocator, root, "include/linux/zigux/h");
    defer allocator.free(text_required_markers__include_linux_zigux_h_path);
    const text_required_markers__include_linux_zigux_h = try guard.readUtf8File(io, allocator, text_required_markers__include_linux_zigux_h_path);
    defer allocator.free(text_required_markers__include_linux_zigux_h);
    for (REQUIRED_MARKERS__include_linux_zigux_h) |marker| try guard.requireMarker(text_required_markers__include_linux_zigux_h, marker);
    const text_selftest_abi_header_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_export_uapi_c_header_smoke.c");
    defer allocator.free(text_selftest_abi_header_path);
    const text_selftest_abi_header = try guard.readUtf8File(io, allocator, text_selftest_abi_header_path);
    defer allocator.free(text_selftest_abi_header);
    for (SELFTEST_ABI_HEADER) |marker| try guard.requireMarker(text_selftest_abi_header, marker);
    const text_selftest_dev_t_header_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_export_uapi_c_header_smoke.c");
    defer allocator.free(text_selftest_dev_t_header_path);
    const text_selftest_dev_t_header = try guard.readUtf8File(io, allocator, text_selftest_dev_t_header_path);
    defer allocator.free(text_selftest_dev_t_header);
    for (SELFTEST_DEV_T_HEADER) |marker| try guard.requireMarker(text_selftest_dev_t_header, marker);
    const text_selftest_linux_header_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_export_uapi_c_header_smoke.c");
    defer allocator.free(text_selftest_linux_header_path);
    const text_selftest_linux_header = try guard.readUtf8File(io, allocator, text_selftest_linux_header_path);
    defer allocator.free(text_selftest_linux_header);
    for (SELFTEST_LINUX_HEADER) |marker| try guard.requireMarker(text_selftest_linux_header, marker);
    const text_selftest_smoke_path = try guard.joinPath(allocator, root, "zigux/tests/phase3_export_uapi_c_header_smoke.c");
    defer allocator.free(text_selftest_smoke_path);
    const text_selftest_smoke = try guard.readUtf8File(io, allocator, text_selftest_smoke_path);
    defer allocator.free(text_selftest_smoke);
    for (SELFTEST_SMOKE) |marker| try guard.requireMarker(text_selftest_smoke, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

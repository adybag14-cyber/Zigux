#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#include <stdint.h>

#include <zigux/abi.h>
#include <zigux/dev_t.h>

#define ZIGUX_UAPI_ABI_MAJOR 0u
#define ZIGUX_UAPI_ABI_MINOR 1u
#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u
#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u

struct zigux_uapi_version {
    uint32_t abi_major;
    uint32_t abi_minor;
    uint32_t header_family_revision;
};

static inline struct zigux_uapi_version zigux_uapi_version_current(void) {
    struct zigux_uapi_version version = {
        .abi_major = ZIGUX_UAPI_ABI_MAJOR,
        .abi_minor = ZIGUX_UAPI_ABI_MINOR,
        .header_family_revision = ZIGUX_UAPI_HEADER_FAMILY_REVISION,
    };
    return version;
}

static inline int zigux_uapi_version_has_current_abi_major(uint32_t abi_major) {
    return abi_major == ZIGUX_UAPI_ABI_MAJOR;
}

static inline int zigux_uapi_version_has_current_abi_minor(uint32_t abi_minor) {
    return abi_minor == ZIGUX_UAPI_ABI_MINOR;
}

static inline int zigux_uapi_version_has_current_header_family_revision(uint32_t header_family_revision) {
    return header_family_revision == ZIGUX_UAPI_HEADER_FAMILY_REVISION;
}

static inline int zigux_uapi_version_matches_current(struct zigux_uapi_version version) {
    return zigux_uapi_version_has_current_abi_major(version.abi_major) &&
        zigux_uapi_version_has_current_abi_minor(version.abi_minor) &&
        zigux_uapi_version_has_current_header_family_revision(version.header_family_revision);
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

static inline int zigux_uapi_boundary_header_is_canonical(zigux_boundary_header header)
{
    return header.size == (uint32_t)sizeof(zigux_boundary_header) &&
        zigux_uapi_boundary_header_has_current_abi_version(header.abi_version);
}

static inline int zigux_uapi_boundary_header_is_compatible(zigux_boundary_header header)
{
    return header.size >= (uint32_t)sizeof(zigux_boundary_header) &&
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

static inline zigux_boundary_header zigux_uapi_boundary_header_canonicalize(zigux_boundary_header header)
{
    header.size = (uint32_t)sizeof(zigux_boundary_header);
    header.abi_version = (uint16_t)ZIGUX_ABI_VERSION;
    return header;
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

static inline int zigux_boundary_header_is_canonical(zigux_boundaryHeader header)
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
    return fields.major <= ZIGUX_DEV_MAJOR_MAX &&
        fields.minor <= ZIGUX_DEV_MINOR_MASK;
}

static inline int zigux_uapi_dev_t_fields_range_is_valid(
    struct zigux_dev_t_fields start,
    struct zigux_dev_t_fields end
)
{
    if (!zigux_uapi_dev_t_fields_is_valid(start) ||
        !zigux_uapi_dev_t_fields_is_valid(end))
        return 0;
    return start.major < end.major ||
        (start.major == end.major && start.minor <= end.minor);
}

#endif
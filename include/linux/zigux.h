#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#include <stdint.h>

#include <zigux/abi.h>
#include <zigux/dev_t.h>

#define ZIGUX_UAPI_ABI_MAJOR 0u
#define ZIGUX_UAPI_ABI_MINOR 1u
#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u
#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u
#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)

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

static inline int zigux_uapi_boundary_header_is_compatible_size(uint32_t size)
{
    return size >= (uint32_t)sizeof(zigux_boundary_header);
}

static inline int zigux_uapi_boundary_header_is_canonical_size(uint32_t size)
{
    return size == (uint32_t)sizeof(zigux_boundary_header);
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

static inline zigux_boundary_header zigux_uapi_boundary_header_canonicalize(zigux_boundary_header header)
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

static inline int zigux_uapi_interop_policy_is_recognized(
    struct zigux_interop_policy policy)
{
    return zigux_interop_policy_is_recognized(policy);
}

static inline struct zigux_export_status zigux_uapi_validate_interop_policy(
    struct zigux_interop_policy policy)
{
    if (zigux_uapi_interop_policy_is_recognized(policy))
        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);
    return zigux_make_status(
        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,
        (uint16_t)ZIGUX_FACILITY_KERNEL);
}

static inline int zigux_uapi_rbtree_root_view_is_valid(zigux_rbtree_root_view view)
{
    return zigux_rbtree_root_view_is_valid(view);
}

static inline zigux_rbtree_root_view zigux_uapi_rbtree_root_view_canonicalize(
    zigux_rbtree_root_view view)
{
    return zigux_rbtree_root_view_canonicalize(view);
}

static inline struct zigux_export_status zigux_uapi_validate_rbtree_root_view(
    zigux_rbtree_root_view view)
{
    if (zigux_uapi_rbtree_root_view_is_valid(view))
        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);
    return zigux_make_status(
        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,
        (uint16_t)ZIGUX_FACILITY_KERNEL);
}

static inline int zigux_uapi_facility_is_known(uint16_t facility)
{
    return zigux_facility_is_known(facility);
}

static inline int zigux_uapi_export_status_has_known_facility(
    struct zigux_export_status status)
{
    return zigux_export_status_has_known_facility(status);
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
    return zigux_uapi_boundary_header_is_compatible_size(size);
}

static inline int zigux_boundary_header_is_canonical_size(uint32_t size)
{
    return zigux_uapi_boundary_header_is_canonical_size(size);
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

static inline struct zigux_dev_t_fields zigux_uapi_dev_t_fields_make(
    uint32_t major,
    uint32_t minor)
{
    return zigux_dev_t_fields_make(major, minor);
}

static inline uint32_t zigux_uapi_mkdev(uint32_t major, uint32_t minor)
{
    return zigux_mkdev(major, minor);
}

static inline uint32_t zigux_uapi_major(uint32_t dev)
{
    return zigux_major(dev);
}

static inline uint32_t zigux_uapi_minor(uint32_t dev)
{
    return zigux_minor(dev);
}

static inline struct zigux_dev_t_fields zigux_uapi_dev_t_fields_from_device_number(
    uint32_t dev)
{
    return zigux_dev_t_fields_from_device_number(dev);
}

static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)
{
    return fields.major <= ZIGUX_DEV_MAJOR_MAX &&
        fields.minor <= ZIGUX_DEV_MINOR_MASK;
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
    struct zigux_dev_t_fields end
)
{
    if (!zigux_uapi_dev_t_fields_is_valid(start) ||
        !zigux_uapi_dev_t_fields_is_valid(end))
        return 0;
    return start.major < end.major ||
        (start.major == end.major && start.minor <= end.minor);
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
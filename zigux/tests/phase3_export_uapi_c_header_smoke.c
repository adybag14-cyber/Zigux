#include <linux/zigux.h>

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
    zigux_boundary_header uapi_canonical =
        zigux_uapi_boundary_header_current(0x52u);
    zigux_boundary_header uapi_compatible =
        zigux_uapi_boundary_header_compatible(
            (uint32_t)sizeof(zigux_boundary_header) + 12u,
            0x52u);
    zigux_boundary_header uapi_canonicalized =
        zigux_uapi_boundary_header_canonicalize(uapi_compatible);
    struct zigux_export_status canonical_status =
        zigux_validate_boundary_header(canonical);
    struct zigux_export_status compatible_status =
        zigux_validate_boundary_header(compatible);
    struct zigux_export_status uapi_canonical_status =
        zigux_uapi_validate_boundary_header(uapi_canonical);
    struct zigux_export_status uapi_compatible_status =
        zigux_uapi_validate_boundary_header(uapi_compatible);
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

    if (!zigux_boundary_header_is_canonical(canonicalized))
        return __LINE__;
    if (zigux_boundary_header_extends_boundary(canonicalized))
        return __LINE__;
    if (canonicalized.flags != compatible.flags)
        return __LINE__;

    if (!zigux_uapi_boundary_header_has_current_abi_version(
            uapi_canonical.abi_version))
        return __LINE__;
    if (!zigux_uapi_boundary_header_is_canonical(uapi_canonical))
        return __LINE__;
    if (!zigux_uapi_boundary_header_is_compatible(uapi_canonical))
        return __LINE__;
    if (!zigux_export_status_ok(uapi_canonical_status))
        return __LINE__;
    if (zigux_uapi_boundary_header_extends_boundary(uapi_canonical))
        return __LINE__;
    if (zigux_uapi_boundary_header_requested_extra_bytes(uapi_canonical) != 0u)
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
    uint32_t encoded = zigux_mkdev(valid.major, valid.minor);
    struct zigux_dev_t_fields decoded =
        zigux_dev_t_fields_from_device_number(encoded);
    struct zigux_export_status valid_status =
        zigux_uapi_validate_dev_t_fields(valid);
    struct zigux_export_status invalid_components =
        zigux_uapi_validate_dev_t_components(ZIGUX_DEV_MAJOR_MAX + 1u, 0u);
    struct zigux_export_status range_status =
        zigux_uapi_validate_dev_t_range(start, end);
    struct zigux_export_status invalid_range =
        zigux_uapi_validate_dev_t_range(end, start);

    if (!zigux_uapi_dev_t_fields_is_valid(valid))
        return __LINE__;
    if (zigux_major(encoded) != valid.major)
        return __LINE__;
    if (zigux_minor(encoded) != valid.minor)
        return __LINE__;
    if (decoded.major != valid.major || decoded.minor != valid.minor)
        return __LINE__;
    if (!zigux_uapi_dev_t_fields_range_is_valid(start, end))
        return __LINE__;
    if (!zigux_export_status_ok(valid_status))
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

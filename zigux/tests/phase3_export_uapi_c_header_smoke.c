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
    if (valid.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (valid.flags != 0u)
        return __LINE__;

    stale.header_family_revision += 1u;
    invalid = zigux_uapi_validate_version(stale);
    if (zigux_uapi_version_matches_current(stale))
        return __LINE__;
    if (zigux_export_status_ok(invalid))
        return __LINE__;
    if (invalid.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (invalid.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (invalid.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
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
    if (canonical_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (canonical_status.flags != 0u)
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
    if (compatible_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (compatible_status.flags != 0u)
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
    if (stale_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (stale_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
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
    if (!zigux_uapi_boundary_header_is_compatible(uapi_canonical))
        return __LINE__;
    if (!zigux_export_status_ok(uapi_canonical_status))
        return __LINE__;
    if (uapi_canonical_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (uapi_canonical_status.flags != 0u)
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
    if (uapi_compatible_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (uapi_compatible_status.flags != 0u)
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
    if (uapi_undersized_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (uapi_undersized_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
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
    if (uapi_stale_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (uapi_stale_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
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
    if (undersized_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (undersized_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;

    return 0;
}

static int check_status_facility_relays(void)
{
    struct zigux_export_status ok = zigux_ok_status((uint16_t)ZIGUX_FACILITY_HELPERS);
    struct zigux_export_status err = zigux_make_status(-22, (uint16_t)ZIGUX_FACILITY_KERNEL);
    struct zigux_export_status unknown = zigux_make_status(0, 9u);

    if (!zigux_uapi_facility_is_known(ok.facility))
        return __LINE__;
    if (!zigux_uapi_facility_is_known(err.facility))
        return __LINE__;
    if (!zigux_uapi_export_status_has_known_facility(ok))
        return __LINE__;
    if (!zigux_uapi_export_status_has_known_facility(err))
        return __LINE__;
    if (ok.flags != 0u)
        return __LINE__;
    if (err.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;
    if (zigux_uapi_facility_is_known(unknown.facility))
        return __LINE__;
    if (zigux_uapi_export_status_has_known_facility(unknown))
        return __LINE__;

    return 0;
}

static int check_interop_policy_relays(void)
{
    struct zigux_interop_policy safe = zigux_default_interop_policy();
    struct zigux_interop_policy mmio = {
        .panic_mode = ZIGUX_PANIC_BUG,
        .allocator_mode = ZIGUX_ALLOC_KERNEL_HEAP,
        .unsafe_scope = ZIGUX_UNSAFE_VOLATILE_MMIO,
        .reserved = 0u,
    };
    struct zigux_interop_policy raw = {
        .panic_mode = ZIGUX_PANIC_WARN,
        .allocator_mode = ZIGUX_ALLOC_ARENA,
        .unsafe_scope = ZIGUX_UNSAFE_RAW_POINTER_BRIDGE,
        .reserved = 0u,
    };
    struct zigux_interop_policy reserved = raw;
    struct zigux_interop_policy unknown = {
        .panic_mode = 9u,
        .allocator_mode = 9u,
        .unsafe_scope = 9u,
        .reserved = 0u,
    };

    reserved.reserved = 1u;

    if (safe.panic_mode != ZIGUX_PANIC_ABORT)
        return __LINE__;
    if (safe.allocator_mode != ZIGUX_ALLOC_CALLER_PROVIDED)
        return __LINE__;
    if (safe.unsafe_scope != ZIGUX_UNSAFE_NONE)
        return __LINE__;
    if (safe.reserved != 0u)
        return __LINE__;

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

    if (!zigux_panic_mode_is_known(mmio.panic_mode))
        return __LINE__;
    if (!zigux_allocator_mode_is_known(mmio.allocator_mode))
        return __LINE__;
    if (!zigux_unsafe_scope_is_known(mmio.unsafe_scope))
        return __LINE__;
    if (!zigux_interop_policy_is_recognized(mmio))
        return __LINE__;

    if (!zigux_interop_policy_is_recognized(raw))
        return __LINE__;
    if (!zigux_interop_policy_reserved_clear(raw))
        return __LINE__;

    if (zigux_interop_policy_reserved_clear(reserved))
        return __LINE__;
    if (zigux_interop_policy_is_recognized(reserved))
        return __LINE__;

    if (zigux_panic_mode_is_known(unknown.panic_mode))
        return __LINE__;
    if (zigux_allocator_mode_is_known(unknown.allocator_mode))
        return __LINE__;
    if (zigux_unsafe_scope_is_known(unknown.unsafe_scope))
        return __LINE__;
    if (zigux_interop_policy_is_recognized(unknown))
        return __LINE__;

    return 0;
}

static int check_uapi_policy_and_rbtree_relays(void)
{
    struct zigux_interop_policy safe = zigux_default_interop_policy();
    struct zigux_interop_policy mmio = {
        .panic_mode = ZIGUX_PANIC_BUG,
        .allocator_mode = ZIGUX_ALLOC_KERNEL_HEAP,
        .unsafe_scope = ZIGUX_UNSAFE_VOLATILE_MMIO,
        .reserved = 0u,
    };
    struct zigux_interop_policy reserved = {
        .panic_mode = ZIGUX_PANIC_WARN,
        .allocator_mode = ZIGUX_ALLOC_ARENA,
        .unsafe_scope = ZIGUX_UNSAFE_RAW_POINTER_BRIDGE,
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
        .flags = (uint32_t)(ZIGUX_RBTREE_ROOT_VIEW_FLAG_CACHED |
            ZIGUX_RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID),
    };
    zigux_rbtree_root_view malformed = {
        .root = (uintptr_t)0x1000u,
        .cached_leftmost = (uintptr_t)0,
        .flags = (uint32_t)(ZIGUX_RBTREE_ROOT_VIEW_FLAG_CACHED |
            ZIGUX_RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID),
    };
    zigux_rbtree_root_view canonicalized =
        zigux_uapi_rbtree_root_view_canonicalize(malformed);
    struct zigux_export_status safe_status = zigux_uapi_validate_interop_policy(safe);
    struct zigux_export_status mmio_status = zigux_uapi_validate_interop_policy(mmio);
    struct zigux_export_status reserved_status = zigux_uapi_validate_interop_policy(reserved);
    struct zigux_export_status unknown_status = zigux_uapi_validate_interop_policy(unknown);
    struct zigux_export_status cached_status = zigux_uapi_validate_rbtree_root_view(cached);
    struct zigux_export_status malformed_status = zigux_uapi_validate_rbtree_root_view(malformed);

    if (!zigux_uapi_interop_policy_is_recognized(safe))
        return __LINE__;
    if (!zigux_uapi_interop_policy_is_recognized(mmio))
        return __LINE__;
    if (zigux_uapi_interop_policy_is_recognized(reserved))
        return __LINE__;
    if (zigux_uapi_interop_policy_is_recognized(unknown))
        return __LINE__;

    if (!zigux_export_status_ok(safe_status))
        return __LINE__;
    if (!zigux_export_status_ok(mmio_status))
        return __LINE__;
    if (safe_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (mmio_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (safe_status.flags != 0u)
        return __LINE__;
    if (mmio_status.flags != 0u)
        return __LINE__;
    if (zigux_export_status_ok(reserved_status))
        return __LINE__;
    if (zigux_export_status_ok(unknown_status))
        return __LINE__;
    if (reserved_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (unknown_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (reserved_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (unknown_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (reserved_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;
    if (unknown_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;

    if (!zigux_uapi_rbtree_root_view_is_valid(cached))
        return __LINE__;
    if (zigux_uapi_rbtree_root_view_is_valid(malformed))
        return __LINE__;
    if (!zigux_export_status_ok(cached_status))
        return __LINE__;
    if (zigux_export_status_ok(malformed_status))
        return __LINE__;
    if (cached_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (malformed_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (cached_status.flags != 0u)
        return __LINE__;
    if (malformed_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (malformed_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;
    if (!zigux_uapi_rbtree_root_view_is_valid(canonicalized))
        return __LINE__;
    if (canonicalized.flags != 0u)
        return __LINE__;
    if (canonicalized.cached_leftmost != (uintptr_t)0)
        return __LINE__;

    return 0;
}

static int check_chrdev_notify_window_relays(void)
{
    struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view view = {
        .ack_window = 7u,
        .delivery_window = 11u,
        .status =
            ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };
    struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary summary = {
        .applied =
            ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
        .skipped =
            ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
        .delivered = 3u,
    };
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary summary_alias =
        summary;

    if (view.status !=
        ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED)
        return __LINE__;
    if (summary.applied !=
        ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED)
        return __LINE__;
    if (summary.skipped != view.status)
        return __LINE__;
    if (summary.delivered != 3u)
        return __LINE__;
    if (sizeof(summary) != sizeof(summary_alias))
        return __LINE__;
    if (summary_alias.applied != summary.applied)
        return __LINE__;

    return 0;
}

static int check_dev_t_relays(void)
{
    struct zigux_dev_t_fields valid = zigux_uapi_dev_t_fields_make(11u, 29u);
    struct zigux_dev_t_fields start = zigux_uapi_dev_t_fields_make(11u, 28u);
    struct zigux_dev_t_fields end = zigux_uapi_dev_t_fields_make(11u, 29u);
    struct zigux_dev_t_fields invalid_major =
        zigux_uapi_dev_t_fields_make(ZIGUX_DEV_MAJOR_MAX + 1u, 0u);
    struct zigux_dev_t_fields invalid_minor =
        zigux_uapi_dev_t_fields_make(0u, ZIGUX_DEV_MINOR_MASK + 1u);
    uint32_t encoded = zigux_uapi_mkdev(valid.major, valid.minor);
    struct zigux_dev_t_fields decoded =
        zigux_uapi_dev_t_fields_from_device_number(encoded);
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
    if (zigux_uapi_major(encoded) != valid.major)
        return __LINE__;
    if (zigux_uapi_minor(encoded) != valid.minor)
        return __LINE__;
    if (decoded.major != valid.major || decoded.minor != valid.minor)
        return __LINE__;
    if (!zigux_uapi_dev_t_fields_range_is_valid(start, end))
        return __LINE__;
    if (!zigux_export_status_ok(valid_status))
        return __LINE__;
    if (valid_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (valid_status.flags != 0u)
        return __LINE__;
    if (zigux_export_status_ok(invalid_field_status))
        return __LINE__;
    if (invalid_field_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (invalid_field_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (invalid_field_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;
    if (zigux_export_status_ok(invalid_minor_status))
        return __LINE__;
    if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (invalid_minor_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (invalid_minor_status.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;
    if (zigux_export_status_ok(invalid_components))
        return __LINE__;
    if (invalid_components.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (invalid_components.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;
    if (!zigux_export_status_ok(range_status))
        return __LINE__;
    if (range_status.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (range_status.flags != 0u)
        return __LINE__;
    if (zigux_export_status_ok(invalid_range))
        return __LINE__;
    if (invalid_range.code != ZIGUX_UAPI_INVALID_ARGUMENT)
        return __LINE__;
    if (invalid_range.facility != (uint16_t)ZIGUX_FACILITY_KERNEL)
        return __LINE__;
    if (invalid_range.flags != (uint16_t)ZIGUX_STATUS_FLAG_ERROR)
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

    rc = check_status_facility_relays();
    if (rc != 0)
        return rc;

    rc = check_interop_policy_relays();
    if (rc != 0)
        return rc;

    rc = check_uapi_policy_and_rbtree_relays();
    if (rc != 0)
        return rc;

    rc = check_chrdev_notify_window_relays();
    if (rc != 0)
        return rc;

    rc = check_dev_t_relays();
    if (rc != 0)
        return rc;

    return 0;
}
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "linux/zigux.h"
#include "zigux/abi.h"
#include "zigux/dev_t.h"

int main(void)
{
    const struct zigux_boundary_header canonical_header = zigux_boundary_header_make(0x22U);
    const struct zigux_boundary_header future_compatible_header =
        zigux_boundary_header_make_compatible(
            (uint32_t)sizeof(struct zigux_boundary_header) + 16U,
            0x22U);
    const struct zigux_boundary_header undersized_header =
        zigux_boundary_header_make_compatible(
            (uint32_t)sizeof(struct zigux_boundary_header) - 1U,
            0x22U);
    struct zigux_boundary_header mismatched_version_header = zigux_boundary_header_make(0x22U);
    mismatched_version_header.abi_version = (uint16_t)(ZIGUX_ABI_VERSION + 1U);

    const struct zigux_export_status invalid_major_status = {
        .code = -22,
        .facility = ZIGUX_FACILITY_DRIVERS,
        .flags = ZIGUX_STATUS_FLAG_ERROR,
    };
    const struct zigux_export_status invalid_range_status = {
        .code = -34,
        .facility = ZIGUX_FACILITY_HELPERS,
        .flags = ZIGUX_STATUS_FLAG_ERROR,
    };
    const uint32_t invalid_major_id = ZIGUX_DEV_MAJOR_MAX + 1U;
    const uint32_t invalid_range_first_minor = ZIGUX_DEV_MINOR_MASK - 1U;
    const uint32_t invalid_range_count = 3U;

    const struct zigux_notifier_block single = {
        .notifier_call = 0,
        .next = (uintptr_t)0,
        .priority = 7,
    };
    const struct zigux_notifier_block descending_third = {
        .notifier_call = 0,
        .next = (uintptr_t)0,
        .priority = -4,
    };
    const struct zigux_notifier_block descending_second = {
        .notifier_call = 0,
        .next = (uintptr_t)&descending_third,
        .priority = 8,
    };
    const struct zigux_notifier_block descending_first = {
        .notifier_call = 0,
        .next = (uintptr_t)&descending_second,
        .priority = 8,
    };
    const struct zigux_notifier_block rising_second = {
        .notifier_call = 0,
        .next = (uintptr_t)0,
        .priority = 5,
    };
    const struct zigux_notifier_block rising_first = {
        .notifier_call = 0,
        .next = (uintptr_t)&rising_second,
        .priority = 3,
    };
    zigux_notifier_chain_priority_increase rising_increase = {
        .previous_index = 0U,
        .current_index = 0U,
        .previous_priority = 0,
        .current_priority = 0,
    };
    const unsigned rising_found =
        (unsigned)zigux_notifier_first_chain_priority_increase(&rising_first, &rising_increase);

    printf(
        "{"
        "\"abi_version\":%u,"
        "\"constants\":{"
        "\"facility_kernel\":%u,"
        "\"facility_helpers\":%u,"
        "\"facility_drivers\":%u,"
        "\"status_flag_error\":%u,"
        "\"panic_abort\":%u,"
        "\"panic_bug\":%u,"
        "\"panic_warn\":%u,"
        "\"allocator_caller_provided\":%u,"
        "\"allocator_kernel_heap\":%u,"
        "\"allocator_arena\":%u,"
        "\"unsafe_scope_none\":%u,"
        "\"unsafe_scope_volatile_mmio\":%u,"
        "\"unsafe_scope_raw_pointer_bridge\":%u,"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_status_skipped\":%u,"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_WINDOW_budget_flag_budget_applied\":%u,"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_flag_window_applied\":%u,"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_status_skipped\":%u,"
        "\"notifier_done\":%u,"
        "\"notifier_ok\":%u,"
        "\"notifier_stop\":%u"
        "},"
        "\"uapi_boundary_header\":{"
        "\"header_size\":%zu,"
        "\"abi_version\":%u,"
        "\"canonical_header\":{"
        "\"size\":%u,"
        "\"abi_version\":%u,"
        "\"flags\":%u,"
        "\"current_abi\":%u,"
        "\"compatible_size\":%u,"
        "\"canonical_size\":%u,"
        "\"compatible\":%u,"
        "\"canonical\":%u,"
        "\"extends_boundary\":%u,"
        "\"requested_extra_bytes\":%u"
        "},"
        "\"future_compatible\":{"
        "\"size\":%u,"
        "\"abi_version\":%u,"
        "\"flags\":%u,"
        "\"current_abi\":%u,"
        "\"compatible_size\":%u,"
        "\"canonical_size\":%u,"
        "\"compatible\":%u,"
        "\"canonical\":%u,"
        "\"extends_boundary\":%u,"
        "\"requested_extra_bytes\":%u"
        "},"
        "\"undersized\":{"
        "\"size\":%u,"
        "\"abi_version\":%u,"
        "\"flags\":%u,"
        "\"current_abi\":%u,"
        "\"compatible_size\":%u,"
        "\"canonical_size\":%u,"
        "\"compatible\":%u,"
        "\"canonical\":%u,"
        "\"extends_boundary\":%u,"
        "\"requested_extra_bytes\":%u"
        "},"
        "\"mismatched_version\":{"
        "\"size\":%u,"
        "\"abi_version\":%u,"
        "\"flags\":%u,"
        "\"current_abi\":%u,"
        "\"compatible_size\":%u,"
        "\"canonical_size\":%u,"
        "\"compatible\":%u,"
        "\"canonical\":%u,"
        "\"extends_boundary\":%u,"
        "\"requested_extra_bytes\":%u"
        "}"
        "},"
        "\"dev_t\":{"
        "\"minor_bits\":%u,"
        "\"minor_mask\":%u,"
        "\"max_major\":%u,"
        "\"sample_major\":%u,"
        "\"sample_minor\":%u,"
        "\"sample_encoded\":%u,"
        "\"range_first_minor\":%u,"
        "\"range_count\":%u,"
        "\"range_fits\":%u,"
        "\"range_last_encoded\":%u,"
        "\"invalid_major\":{\"major\":%u,\"minor\":%u,\"value\":%u,\"ok\":%u,\"code\":%d,\"flags\":%u},"
        "\"invalid_range\":{\"major\":%u,\"first_minor\":%u,\"count\":%u,\"value\":%u,\"ok\":%u,\"code\":%d,\"flags\":%u}"
        "},"
        "\"notifier_chain\":{"
        "\"empty_ok\":%u,"
        "\"single_ok\":%u,"
        "\"descending_ok\":%u,"
        "\"rising_ok\":%u,"
        "\"rising_first_increase\":{\"found\":%u,\"previous_index\":%zu,\"current_index\":%zu,\"previous_priority\":%d,\"current_priority\":%d}"
        "},"
        "\"structs\":{"
        "\"boundary_header\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"size\":%zu,\"abi_version\":%zu,\"flags\":%zu}},"
        "\"export_status\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"code\":%zu,\"facility\":%zu,\"flags\":%zu}},"
        "\"interop_policy\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"panic_mode\":%zu,\"allocator_mode\":%zu,\"unsafe_scope\":%zu,\"reserved\":%zu}},"
        "\"notifier_chain_priority_increase\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"previous_index\":%zu,\"current_index\":%zu,\"previous_priority\":%zu,\"current_priority\":%zu}},"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_view\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"ack_window\":%zu,\"delivery_window\":%zu,\"status\":%zu}},"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_summary\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"applied\":%zu,\"skipped\":%zu,\"delivered\":%zu}},"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"budget\":%zu,\"window\":%zu,\"flags\":%zu}},"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"attempted\":%zu,\"applied\":%zu,\"skipped\":%zu}},"
        "\"notifier_block\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"notifier_call\":%zu,\"next\":%zu,\"priority\":%zu}}"
        "}"
        "}\n",
        ZIGUX_ABI_VERSION,
        ZIGUX_FACILITY_KERNEL,
        ZIGUX_FACILITY_HELPERS,
        ZIGUX_FACILITY_DRIVERS,
        ZIGUX_STATUS_FLAG_ERROR,
        ZIGUX_PANIC_ABORT,
        ZIGUX_PANIC_BUG,
        ZIGUX_PANIC_WARN,
        ZIGUX_ALLOC_CALLER_PROVIDED,
        ZIGUX_ALLOC_KERNEL_HEAP,
        ZIGUX_ALLOC_ARENA,
        ZIGUX_UNSAFE_NONE,
        ZIGUX_UNSAFE_VOLATILE_MMIO,
        ZIGUX_UNSAFE_RAW_POINTER_BRIDGE,
        ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
        ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
        ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
        ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
        ZIGUX_NOTIFIER_DONE,
        ZIGUX_NOTIFIER_OK,
        ZIGUX_NOTIFIER_STOP,
        sizeof(struct zigux_boundary_header),
        ZIGUX_ABI_VERSION,
        canonical_header.size,
        canonical_header.abi_version,
        canonical_header.flags,
        (unsigned)zigux_boundary_header_is_current_abi_version(canonical_header.abi_version),
        (unsigned)zigux_boundary_header_is_compatible_size(canonical_header.size),
        (unsigned)zigux_boundary_header_is_canonical_size(canonical_header.size),
        (unsigned)zigux_boundary_header_is_compatible(canonical_header),
        (unsigned)zigux_boundary_header_is_canonical(canonical_header),
        (unsigned)(zigux_boundary_header_is_compatible(canonical_header) &&
                   !zigux_boundary_header_is_canonical(canonical_header)),
        0U,
        future_compatible_header.size,
        future_compatible_header.abi_version,
        future_compatible_header.flags,
        (unsigned)zigux_boundary_header_is_current_abi_version(future_compatible_header.abi_version),
        (unsigned)zigux_boundary_header_is_compatible_size(future_compatible_header.size),
        (unsigned)zigux_boundary_header_is_canonical_size(future_compatible_header.size),
        (unsigned)zigux_boundary_header_is_compatible(future_compatible_header),
        (unsigned)zigux_boundary_header_is_canonical(future_compatible_header),
        (unsigned)(zigux_boundary_header_is_compatible(future_compatible_header) &&
                   !zigux_boundary_header_is_canonical(future_compatible_header)),
        (unsigned)(future_compatible_header.size - (uint32_t)sizeof(struct zigux_boundary_header)),
        undersized_header.size,
        undersized_header.abi_version,
        undersized_header.flags,
        (unsigned)zigux_boundary_header_is_current_abi_version(undersized_header.abi_version),
        (unsigned)zigux_boundary_header_is_compatible_size(undersized_header.size),
        (unsigned)zigux_boundary_header_is_canonical_size(undersized_header.size),
        (unsigned)zigux_boundary_header_is_compatible(undersized_header),
        (unsigned)zigux_boundary_header_is_canonical(undersized_header),
        0U,
        0U,
        mismatched_version_header.size,
        mismatched_version_header.abi_version,
        mismatched_version_header.flags,
        (unsigned)zigux_boundary_header_is_current_abi_version(mismatched_version_header.abi_version),
        (unsigned)zigux_boundary_header_is_compatible_size(mismatched_version_header.size),
        (unsigned)zigux_boundary_header_is_canonical_size(mismatched_version_header.size),
        (unsigned)zigux_boundary_header_is_compatible(mismatched_version_header),
        (unsigned)zigux_boundary_header_is_canonical(mismatched_version_header),
        0U,
        0U,
        ZIGUX_DEV_MINOR_BITS,
        ZIGUX_DEV_MINOR_MASK,
        ZIGUX_DEV_MAJOR_MAX,
        42U,
        7U,
        zigux_mkdev(42U, 7U),
        7U,
        4U,
        (unsigned)(zigux_major(zigux_mkdev(42U, 7U)) == 42U &&
                   zigux_minor(zigux_mkdev(42U, 7U)) == 7U &&
                   (7U + 4U - 1U) <= ZIGUX_DEV_MINOR_MASK),
        zigux_mkdev(42U, 7U + 4U - 1U),
        invalid_major_id,
        7U,
        0U,
        (unsigned)zigux_export_status_ok(invalid_major_status),
        invalid_major_status.code,
        invalid_major_status.flags,
        42U,
        invalid_range_first_minor,
        invalid_range_count,
        0U,
        (unsigned)zigux_export_status_ok(invalid_range_status),
        invalid_range_status.code,
        invalid_range_status.flags,
        (unsigned)zigux_notifier_chain_has_nonincreasing_priority(NULL),
        (unsigned)zigux_notifier_chain_has_nonincreasing_priority(&single),
        (unsigned)zigux_notifier_chain_has_nonincreasing_priority(&descending_first),
        (unsigned)zigux_notifier_chain_has_nonincreasing_priority(&rising_first),
        rising_found,
        rising_increase.previous_index,
        rising_increase.current_index,
        rising_increase.previous_priority,
        rising_increase.current_priority,
        sizeof(struct zigux_boundary_header),
        _Alignof(struct zigux_boundary_header),
        offsetof(struct zigux_boundary_header, size),
        offsetof(struct zigux_boundary_header, abi_version),
        offsetof(struct zigux_boundary_header, flags),
        sizeof(struct zigux_export_status),
        _Alignof(struct zigux_export_status),
        offsetof(struct zigux_export_status, code),
        offsetof(struct zigux_export_status, facility),
        offsetof(struct zigux_export_status, flags),
        sizeof(struct zigux_interop_policy),
        _Alignof(struct zigux_interop_policy),
        offsetof(struct zigux_interop_policy, panic_mode),
        offsetof(struct zigux_interop_policy, allocator_mode),
        offsetof(struct zigux_interop_policy, unsafe_scope),
        offsetof(struct zigux_interop_policy, reserved),
        sizeof(zigux_notifier_chain_priority_increase),
        _Alignof(zigux_notifier_chain_priority_increase),
        offsetof(zigux_notifier_chain_priority_increase, previous_index),
        offsetof(zigux_notifier_chain_priority_increase, current_index),
        offsetof(zigux_notifier_chain_priority_increase, previous_priority),
        offsetof(zigux_notifier_chain_priority_increase, current_priority),
        sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view),
        _Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, ack_window),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, delivery_window),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, status),
        sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary),
        _Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary, applied),
        offsetof(struct zigux_chrdev_notify_ack_WINDOW_policy_budget_window_delivery_window_summary, skipped),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary, delivered),
        sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view),
        _Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view, budget),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view, window),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view, flags),
        sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary),
        _Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary, attempted),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary, applied),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary, skipped),
        sizeof(struct zigux_notifier_block),
        _Alignof(struct zigux_notifier_block),
        offsetof(struct zigux_notifier_block, notifier_call),
        offsetof(struct zigux_notifier_block, next),
        offsetof(struct zigux_notifier_block, priority));
    return 0;
}

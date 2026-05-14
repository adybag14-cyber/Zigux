#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "zigux/abi.h"
#include "zigux/dev_t.h"

int main(void)
{
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
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_flag_budget_applied\":%u,"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_flag_window_applied\":%u,"
        "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_status_skipped\":%u,"
        "\"notifier_done\":%u,"
        "\"notifier_ok\":%u,"
        "\"notifier_stop\":%u"
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
        "\"range_last_encoded\":%u"
        "},"
        "\"structs\":{"
        "\"boundary_header\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"size\":%zu,\"abi_version\":%zu,\"flags\":%zu}},"
        "\"export_status\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"code\":%zu,\"facility\":%zu,\"flags\":%zu}},"
        "\"interop_policy\":{\"size\":%zu,\"align\":%zu,\"offsets\":{\"panic_mode\":%zu,\"allocator_mode\":%zu,\"unsafe_scope\":%zu,\"reserved\":%zu}},"
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
        sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view),
        _Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, ack_window),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, delivery_window),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, status),
        sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary),
        _Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary, applied),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary, skipped),
        offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary, delivered),
        sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view),
        _Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_WINDOW_budget_view),
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

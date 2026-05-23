#include <stddef.h>

#include <zigux/abi.h>

static int check_header_helpers(void)
{
    zigux_boundary_header canonical = zigux_default_header(0x41u);
    zigux_boundary_header compatible =
        zigux_compatible_header((uint32_t)sizeof(zigux_boundary_header) + 8u, 0x41u);
    zigux_boundary_header stale = canonical;
    zigux_boundary_header canonicalized;

    stale.abi_version += 1u;
    canonicalized = zigux_header_canonicalize(compatible);

    if (!zigux_abi_version_is_current(canonical.abi_version))
        return __LINE__;
    if (!zigux_header_is_canonical(canonical))
        return __LINE__;
    if (!zigux_header_is_compatible(canonical))
        return __LINE__;
    if (zigux_header_extends_boundary(canonical))
        return __LINE__;
    if (zigux_header_requested_extra_bytes(canonical) != 0u)
        return __LINE__;

    if (zigux_header_is_canonical(compatible))
        return __LINE__;
    if (!zigux_header_is_compatible(compatible))
        return __LINE__;
    if (!zigux_header_extends_boundary(compatible))
        return __LINE__;
    if (zigux_header_requested_extra_bytes(compatible) != 8u)
        return __LINE__;

    if (zigux_header_is_compatible(stale))
        return __LINE__;
    if (!zigux_header_is_canonical(canonicalized))
        return __LINE__;
    if (canonicalized.flags != compatible.flags)
        return __LINE__;

    return 0;
}

static int check_status_and_policy_helpers(void)
{
    struct zigux_interop_policy policy = zigux_default_interop_policy();
    struct zigux_export_status ok = zigux_ok_status((uint16_t)ZIGUX_FACILITY_HELPERS);
    struct zigux_export_status err = zigux_make_status(-22, (uint16_t)ZIGUX_FACILITY_KERNEL);

    if (sizeof(struct zigux_interop_policy) != 4u)
        return __LINE__;
    if (offsetof(struct zigux_interop_policy, panic_mode) != 0u)
        return __LINE__;
    if (offsetof(struct zigux_interop_policy, allocator_mode) != 1u)
        return __LINE__;
    if (offsetof(struct zigux_interop_policy, unsafe_scope) != 2u)
        return __LINE__;
    if (offsetof(struct zigux_interop_policy, reserved) != 3u)
        return __LINE__;
    if (policy.panic_mode != ZIGUX_PANIC_ABORT)
        return __LINE__;
    if (policy.allocator_mode != ZIGUX_ALLOC_CALLER_PROVIDED)
        return __LINE__;
    if (policy.unsafe_scope != ZIGUX_UNSAFE_NONE)
        return __LINE__;
    if (policy.reserved != 0u)
        return __LINE__;
    if (!zigux_export_status_ok(ok))
        return __LINE__;
    if (zigux_export_status_ok(err))
        return __LINE__;
    if (err.flags != ZIGUX_STATUS_FLAG_ERROR)
        return __LINE__;

    return 0;
}

static int check_notifier_and_list_helpers(void)
{
    struct zigux_notifier_block tail = { .notifier_call = 0, .next = 0, .priority = 7 };
    struct zigux_notifier_block head = {
        .notifier_call = 0,
        .next = (uintptr_t)&tail,
        .priority = 3,
    };
    zigux_notifier_chain_priority_increase increase;
    struct zigux_list_head list_head = { .next = 0, .prev = 0 };
    struct zigux_list_head list_first = { .next = 0, .prev = 0 };
    struct zigux_list_head list_second = { .next = 0, .prev = 0 };
    zigux_list_backlink_break list_break;
    struct zigux_hlist_head hlist_head = { .first = 0 };
    struct zigux_hlist_node hlist_first = { .next = 0, .pprev = 0 };
    struct zigux_hlist_node hlist_second = { .next = 0, .pprev = 0 };
    zigux_hlist_prev_link_break hlist_break;

    if (zigux_notifier_chain_has_nonincreasing_priority(&head))
        return __LINE__;
    if (!zigux_notifier_first_chain_priority_increase(&head, &increase))
        return __LINE__;
    if (increase.previous_index != 0u || increase.current_index != 1u)
        return __LINE__;
    if (increase.previous_priority != 3 || increase.current_priority != 7)
        return __LINE__;

    list_head.next = (uintptr_t)&list_first;
    list_head.prev = (uintptr_t)&list_second;
    list_first.next = (uintptr_t)&list_second;
    list_first.prev = (uintptr_t)&list_head;
    list_second.next = (uintptr_t)&list_head;
    list_second.prev = (uintptr_t)&list_head;
    if (zigux_list_has_consistent_backlinks(&list_head))
        return __LINE__;
    if (!zigux_list_first_broken_backlink(&list_head, &list_break))
        return __LINE__;
    if (list_break.current_index != 1u)
        return __LINE__;

    hlist_head.first = (uintptr_t)&hlist_first;
    hlist_first.next = (uintptr_t)&hlist_second;
    hlist_first.pprev = (uintptr_t)&hlist_head.first;
    hlist_second.next = 0;
    hlist_second.pprev = (uintptr_t)&hlist_head.first;
    if (zigux_hlist_has_consistent_prev_links(&hlist_head))
        return __LINE__;
    if (!zigux_hlist_first_broken_prev_link(&hlist_head, &hlist_break))
        return __LINE__;
    if (hlist_break.current_index != 1u)
        return __LINE__;

    return 0;
}

static int check_chrdev_layout_helpers(void)
{
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view view = {
        .ack_window = 7u,
        .delivery_window = 11u,
        .status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };

    if (ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED != 1u)
        return __LINE__;
    if (ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED != 1u)
        return __LINE__;
    if (ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED != 1u)
        return __LINE__;
    if (sizeof(view) != 12u)
        return __LINE__;
    if (offsetof(
            zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view,
            status) != 8u)
        return __LINE__;

    return 0;
}

int main(void)
{
    int rc = check_header_helpers();
    if (rc != 0)
        return rc;

    rc = check_status_and_policy_helpers();
    if (rc != 0)
        return rc;

    rc = check_notifier_and_list_helpers();
    if (rc != 0)
        return rc;

    rc = check_chrdev_layout_helpers();
    if (rc != 0)
        return rc;

    return 0;
}

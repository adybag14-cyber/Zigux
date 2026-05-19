#ifndef _ZIGUX_ABI_H
#define _ZIGUX_ABI_H

#include <stddef.h>
#include <stdint.h>

#define ZIGUX_ABI_VERSION 1U

#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_FACILITY_HELPERS 2U
#define ZIGUX_FACILITY_DRIVERS 3U

#define ZIGUX_STATUS_FLAG_ERROR 1U

#define ZIGUX_PANIC_ABORT 0U
#define ZIGUX_PANIC_BUG 1U
#define ZIGUX_PANIC_WARN 2U

#define ZIGUX_ALLOC_CALLER_PROVIDED 0U
#define ZIGUX_ALLOC_KERNEL_HEAP 1U
#define ZIGUX_ALLOC_ARENA 2U

#define ZIGUX_UNSAFE_NONE 0U
#define ZIGUX_UNSAFE_VOLATILE_MMIO 1U
#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U

#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED 1U
#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED 1U

#define ZIGUX_NOTIFIER_DONE 0U
#define ZIGUX_NOTIFIER_OK 1U
#define ZIGUX_NOTIFIER_STOP 2U

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

typedef struct zigux_notifier_chain_priority_increase {
    size_t previous_index;
    size_t current_index;
    int32_t previous_priority;
    int32_t current_priority;
} zigux_notifier_chain_priority_increase;

struct zigux_interop_policy {
    uint8_t panic_mode;
    uint8_t allocator_mode;
    uint8_t unsafe_scope;
    uint8_t reserved;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {
    uint32_t ack_window;
    uint32_t delivery_window;
    uint32_t status;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {
    uint32_t applied;
    uint32_t skipped;
    uint32_t delivered;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {
    uint32_t budget;
    uint32_t window;
    uint32_t flags;
};

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {
    uint32_t attempted;
    uint32_t applied;
    uint32_t skipped;
};

struct zigux_notifier_block {
    uintptr_t notifier_call;
    uintptr_t next;
    int32_t priority;
};

struct zigux_list_head {
    uintptr_t next;
    uintptr_t prev;
};

struct zigux_hlist_head {
    uintptr_t first;
};

struct zigux_hlist_node {
    uintptr_t next;
    uintptr_t pprev;
};

static inline int zigux_notifier_chain_has_nonincreasing_priority(
    const struct zigux_notifier_block *head)
{
    int32_t previous_priority;
    const struct zigux_notifier_block *node;

    if (!head)
        return 1;

    previous_priority = head->priority;
    while (head->next != (uintptr_t)0) {
        node = (const struct zigux_notifier_block *)(uintptr_t)head->next;
        if (node->priority > previous_priority)
            return 0;
        previous_priority = node->priority;
        head = node;
    }

    return 1;
}

static inline int zigux_notifier_first_chain_priority_increase(
    const struct zigux_notifier_block *head,
    zigux_notifier_chain_priority_increase *out)
{
    size_t previous_index = 0;
    int32_t previous_priority;

    if (!head || head->next == (uintptr_t)0 || !out)
        return 0;

    previous_priority = head->priority;
    while (head->next != (uintptr_t)0) {
        const struct zigux_notifier_block *node =
            (const struct zigux_notifier_block *)(uintptr_t)head->next;
        const size_t current_index = previous_index + 1;
        if (node->priority > previous_priority) {
            out->previous_index = previous_index;
            out->current_index = current_index;
            out->previous_priority = previous_priority;
            out->current_priority = node->priority;
            return 1;
        }
        previous_index = current_index;
        previous_priority = node->priority;
        head = node;
    }

    return 0;
}

static inline int zigux_list_has_consistent_backlinks(
    const struct zigux_list_head *head)
{
    uintptr_t expected_prev;
    const struct zigux_list_head *cursor;

    if (!head)
        return 0;

    expected_prev = (uintptr_t)head;
    cursor = (const struct zigux_list_head *)(uintptr_t)head->next;
    if (!cursor)
        return 0;

    while (cursor != head) {
        if (cursor->prev != expected_prev)
            return 0;
        expected_prev = (uintptr_t)cursor;
        cursor = (const struct zigux_list_head *)(uintptr_t)cursor->next;
        if (!cursor)
            return 0;
    }

    return head->prev == expected_prev;
}

static inline int zigux_hlist_has_consistent_prev_links(
    const struct zigux_hlist_head *head)
{
    uintptr_t expected_pprev;
    const struct zigux_hlist_node *cursor;

    if (!head)
        return 0;

    expected_pprev = (uintptr_t)&head->first;
    cursor = (const struct zigux_hlist_node *)(uintptr_t)head->first;
    while (cursor) {
        if (cursor->pprev != expected_pprev)
            return 0;
        expected_pprev = (uintptr_t)&cursor->next;
        cursor = (const struct zigux_hlist_node *)(uintptr_t)cursor->next;
    }

    return 1;
}

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

static inline struct zigux_interop_policy zigux_default_interop_policy(void)
{
    struct zigux_interop_policy policy = {
        .panic_mode = (uint8_t)ZIGUX_PANIC_ABORT,
        .allocator_mode = (uint8_t)ZIGUX_ALLOC_CALLER_PROVIDED,
        .unsafe_scope = (uint8_t)ZIGUX_UNSAFE_NONE,
        .reserved = 0,
    };
    return policy;
}

static inline int zigux_export_status_ok(struct zigux_export_status status)
{
    return (status.flags & (uint16_t)ZIGUX_STATUS_FLAG_ERROR) == 0;
}

#endif
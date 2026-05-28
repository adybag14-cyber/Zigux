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

#define ZIGUX_RBTREE_ROOT_VIEW_FLAG_CACHED 1U
#define ZIGUX_RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID 2U

#define ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED 1U
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

typedef struct zigux_rbtree_root_view {
    uintptr_t root;
    uintptr_t cached_leftmost;
    uint32_t flags;
} zigux_rbtree_root_view;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {
    uint32_t ack_window;
    uint32_t delivery_window;
    uint32_t status;
};
typedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view;
typedef zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
    zigux_chrdev_notify_delivery_window_view;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {
    uint32_t applied;
    uint32_t skipped;
    uint32_t delivered;
};
typedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary;
typedef zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary
    zigux_chrdev_notify_delivery_window_summary;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view {
    uint32_t budget;
    uint32_t window;
    uint32_t flags;
};
typedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view;
typedef zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
    zigux_chrdev_notify_delivery_window_budget_view;

struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary {
    uint32_t attempted;
    uint32_t applied;
    uint32_t skipped;
};
typedef struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary
    zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary;
typedef zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary
    zigux_chrdev_notify_delivery_window_budget_summary;

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

typedef struct zigux_list_backlink_break {
    size_t current_index;
    uintptr_t expected_prev;
    uintptr_t actual_prev;
} zigux_list_backlink_break;

typedef struct zigux_hlist_prev_link_break {
    size_t current_index;
    uintptr_t expected_pprev;
    uintptr_t actual_pprev;
} zigux_hlist_prev_link_break;

static inline int zigux_notifier_result_is_known(uint32_t result)
{
    return result == (uint32_t)ZIGUX_NOTIFIER_DONE ||
        result == (uint32_t)ZIGUX_NOTIFIER_OK ||
        result == (uint32_t)ZIGUX_NOTIFIER_STOP;
}

static inline int zigux_notifier_result_stops_chain(uint32_t result)
{
    return result == (uint32_t)ZIGUX_NOTIFIER_STOP;
}

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

static inline int zigux_list_is_empty(const struct zigux_list_head *head)
{
    if (!head)
        return 0;

    return head->next == (uintptr_t)head && head->prev == (uintptr_t)head;
}

static inline int zigux_list_first_broken_backlink(
    const struct zigux_list_head *head,
    zigux_list_backlink_break *out)
{
    uintptr_t expected_prev;
    size_t current_index = 0;
    const struct zigux_list_head *cursor;

    if (!head)
        return 0;

    expected_prev = (uintptr_t)head;
    cursor = (const struct zigux_list_head *)(uintptr_t)head->next;
    if (!cursor) {
        if (out) {
            out->current_index = 0;
            out->expected_prev = expected_prev;
            out->actual_prev = 0;
        }
        return 1;
    }

    while (cursor != head) {
        if (cursor->prev != expected_prev) {
            if (out) {
                out->current_index = current_index;
                out->expected_prev = expected_prev;
                out->actual_prev = cursor->prev;
            }
            return 1;
        }
        expected_prev = (uintptr_t)cursor;
        current_index += 1;
        cursor = (const struct zigux_list_head *)(uintptr_t)cursor->next;
        if (!cursor) {
            if (out) {
                out->current_index = current_index;
                out->expected_prev = expected_prev;
                out->actual_prev = 0;
            }
            return 1;
        }
    }

    if (head->prev != expected_prev) {
        if (out) {
            out->current_index = current_index;
            out->expected_prev = expected_prev;
            out->actual_prev = head->prev;
        }
        return 1;
    }

    return 0;
}

static inline int zigux_list_has_consistent_backlinks(
    const struct zigux_list_head *head)
{
    return head != NULL && zigux_list_first_broken_backlink(head, NULL) == 0;
}

static inline int zigux_hlist_first_pprev_matches_head(
    const struct zigux_hlist_head *head)
{
    const struct zigux_hlist_node *first;

    if (!head)
        return 0;

    first = (const struct zigux_hlist_node *)(uintptr_t)head->first;
    if (!first)
        return 1;

    return first->pprev == (uintptr_t)&head->first;
}

static inline int zigux_hlist_first_broken_prev_link(
    const struct zigux_hlist_head *head,
    zigux_hlist_prev_link_break *out)
{
    uintptr_t expected_pprev;
    size_t current_index = 0;
    const struct zigux_hlist_node *cursor;

    if (!head)
        return 0;

    expected_pprev = (uintptr_t)&head->first;
    cursor = (const struct zigux_hlist_node *)(uintptr_t)head->first;
    while (cursor) {
        if (cursor->pprev != expected_pprev) {
            if (out) {
                out->current_index = current_index;
                out->expected_pprev = expected_pprev;
                out->actual_pprev = cursor->pprev;
            }
            return 1;
        }
        expected_pprev = (uintptr_t)&cursor->next;
        current_index += 1;
        cursor = (const struct zigux_hlist_node *)(uintptr_t)cursor->next;
    }

    return 0;
}

static inline int zigux_hlist_has_consistent_prev_links(
    const struct zigux_hlist_head *head)
{
    return head != NULL && zigux_hlist_first_broken_prev_link(head, NULL) == 0;
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

static inline int zigux_header_is_compatible_size(uint32_t size)
{
    return size >= (uint32_t)sizeof(zigux_boundary_header);
}

static inline int zigux_header_is_canonical_size(uint32_t size)
{
    return size == (uint32_t)sizeof(zigux_boundary_header);
}

static inline int zigux_header_is_canonical(zigux_boundary_header header)
{
    return zigux_header_is_canonical_size(header.size) &&
        zigux_abi_version_is_current(header.abi_version);
}

static inline int zigux_header_is_compatible(zigux_boundary_header header)
{
    return zigux_header_is_compatible_size(header.size) &&
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

static inline int zigux_rbtree_root_view_is_cached(zigux_rbtree_root_view view)
{
    return (view.flags & (uint32_t)ZIGUX_RBTREE_ROOT_VIEW_FLAG_CACHED) != 0U;
}

static inline int zigux_rbtree_root_view_has_leftmost(zigux_rbtree_root_view view)
{
    return (view.flags & (uint32_t)ZIGUX_RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID) != 0U;
}

static inline int zigux_rbtree_root_view_is_valid(zigux_rbtree_root_view view)
{
    const int cached = zigux_rbtree_root_view_is_cached(view);
    const int has_leftmost_flag = zigux_rbtree_root_view_has_leftmost(view);
    const int has_leftmost_addr = view.cached_leftmost != (uintptr_t)0;

    if (view.root == (uintptr_t)0)
        return 0;
    if (cached != has_leftmost_flag)
        return 0;
    if (cached != has_leftmost_addr)
        return 0;
    return 1;
}

static inline zigux_rbtree_root_view zigux_rbtree_root_view_canonicalize(
    zigux_rbtree_root_view view)
{
    if (view.root == (uintptr_t)0) {
        view.cached_leftmost = (uintptr_t)0;
        view.flags = 0U;
        return view;
    }

    if (view.cached_leftmost == (uintptr_t)0) {
        view.flags = 0U;
        return view;
    }

    view.flags = (uint32_t)(ZIGUX_RBTREE_ROOT_VIEW_FLAG_CACHED |
        ZIGUX_RBTREE_ROOT_VIEW_FLAG_LEFTMOST_VALID);
    return view;
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

static inline int zigux_panic_mode_is_known(uint8_t mode)
{
    return mode == (uint8_t)ZIGUX_PANIC_ABORT ||
        mode == (uint8_t)ZIGUX_PANIC_BUG ||
        mode == (uint8_t)ZIGUX_PANIC_WARN;
}

static inline int zigux_allocator_mode_is_known(uint8_t mode)
{
    return mode == (uint8_t)ZIGUX_ALLOC_CALLER_PROVIDED ||
        mode == (uint8_t)ZIGUX_ALLOC_KERNEL_HEAP ||
        mode == (uint8_t)ZIGUX_ALLOC_ARENA;
}

static inline int zigux_unsafe_scope_is_known(uint8_t scope)
{
    return scope == (uint8_t)ZIGUX_UNSAFE_NONE ||
        scope == (uint8_t)ZIGUX_UNSAFE_VOLATILE_MMIO ||
        scope == (uint8_t)ZIGUX_UNSAFE_RAW_POINTER_BRIDGE;
}

static inline int zigux_interop_policy_reserved_clear(
    struct zigux_interop_policy policy)
{
    return policy.reserved == 0;
}

static inline int zigux_interop_policy_is_recognized(
    struct zigux_interop_policy policy)
{
    return zigux_interop_policy_reserved_clear(policy) &&
        zigux_panic_mode_is_known(policy.panic_mode) &&
        zigux_allocator_mode_is_known(policy.allocator_mode) &&
        zigux_unsafe_scope_is_known(policy.unsafe_scope);
}

static inline int zigux_facility_is_known(uint16_t facility)
{
    return facility == (uint16_t)ZIGUX_FACILITY_KERNEL ||
        facility == (uint16_t)ZIGUX_FACILITY_HELPERS ||
        facility == (uint16_t)ZIGUX_FACILITY_DRIVERS;
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

static inline int zigux_export_status_has_known_facility(
    struct zigux_export_status status)
{
    return zigux_facility_is_known(status.facility);
}

#endif
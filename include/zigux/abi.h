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

#define ZIGUX_STATIC_ASSERT(expr, msg) _Static_assert((expr), msg)

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

typedef struct zigux_notifier_chain_priority_increase {
    size_t previous_index;
    size_t current_index;
    int32_t previous_priority;
    int32_t current_priority;
} zigux_notifier_chain_priority_increase;

ZIGUX_STATIC_ASSERT(sizeof(zigux_boundary_header) == 8U,
    "zigux_boundary_header size must stay canonical");
ZIGUX_STATIC_ASSERT(_Alignof(zigux_boundary_header) == 4U,
    "zigux_boundary_header alignment must stay canonical");
ZIGUX_STATIC_ASSERT(offsetof(zigux_boundary_header, size) == 0U,
    "zigux_boundary_header.size offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(zigux_boundary_header, abi_version) == 4U,
    "zigux_boundary_header.abi_version offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(zigux_boundary_header, flags) == 6U,
    "zigux_boundary_header.flags offset drifted");

ZIGUX_STATIC_ASSERT(sizeof(struct zigux_export_status) == 8U,
    "zigux_export_status size must stay canonical");
ZIGUX_STATIC_ASSERT(_Alignof(struct zigux_export_status) == 4U,
    "zigux_export_status alignment must stay canonical");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_export_status, code) == 0U,
    "zigux_export_status.code offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_export_status, facility) == 4U,
    "zigux_export_status.facility offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_export_status, flags) == 6U,
    "zigux_export_status.flags offset drifted");

ZIGUX_STATIC_ASSERT(sizeof(struct zigux_interop_policy) == 4U,
    "zigux_interop_policy size must stay canonical");
ZIGUX_STATIC_ASSERT(_Alignof(struct zigux_interop_policy) == 1U,
    "zigux_interop_policy alignment must stay canonical");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_interop_policy, panic_mode) == 0U,
    "zigux_interop_policy.panic_mode offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_interop_policy, allocator_mode) == 1U,
    "zigux_interop_policy.allocator_mode offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_interop_policy, unsafe_scope) == 2U,
    "zigux_interop_policy.unsafe_scope offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_interop_policy, reserved) == 3U,
    "zigux_interop_policy.reserved offset drifted");

ZIGUX_STATIC_ASSERT(sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view) == 12U,
    "zigux chrdev delivery window view size must stay canonical");
ZIGUX_STATIC_ASSERT(_Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view) == 4U,
    "zigux chrdev delivery window view alignment must stay canonical");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, ack_window) == 0U,
    "zigux chrdev delivery window view ack_window offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, delivery_window) == 4U,
    "zigux chrdev delivery window view delivery_window offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view, status) == 8U,
    "zigux chrdev delivery window view status offset drifted");

ZIGUX_STATIC_ASSERT(sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary) == 12U,
    "zigux chrdev delivery window summary size must stay canonical");
ZIGUX_STATIC_ASSERT(_Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary) == 4U,
    "zigux chrdev delivery window summary alignment must stay canonical");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary, applied) == 0U,
    "zigux chrdev delivery window summary applied offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary, skipped) == 4U,
    "zigux chrdev delivery window summary skipped offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary, delivered) == 8U,
    "zigux chrdev delivery window summary delivered offset drifted");

ZIGUX_STATIC_ASSERT(sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view) == 12U,
    "zigux chrdev budget view size must stay canonical");
ZIGUX_STATIC_ASSERT(_Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view) == 4U,
    "zigux chrdev budget view alignment must stay canonical");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view, budget) == 0U,
    "zigux chrdev budget view budget offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view, window) == 4U,
    "zigux chrdev budget view window offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view, flags) == 8U,
    "zigux chrdev budget view flags offset drifted");

ZIGUX_STATIC_ASSERT(sizeof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary) == 12U,
    "zigux chrdev budget summary size must stay canonical");
ZIGUX_STATIC_ASSERT(_Alignof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary) == 4U,
    "zigux chrdev budget summary alignment must stay canonical");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary, attempted) == 0U,
    "zigux chrdev budget summary attempted offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary, applied) == 4U,
    "zigux chrdev budget summary applied offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary, skipped) == 8U,
    "zigux chrdev budget summary skipped offset drifted");

ZIGUX_STATIC_ASSERT(offsetof(struct zigux_notifier_block, notifier_call) == 0U,
    "zigux_notifier_block.notifier_call offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_notifier_block, next) == sizeof(uintptr_t),
    "zigux_notifier_block.next offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(struct zigux_notifier_block, priority) == sizeof(uintptr_t) * 2U,
    "zigux_notifier_block.priority offset drifted");
ZIGUX_STATIC_ASSERT(_Alignof(struct zigux_notifier_block) == _Alignof(uintptr_t),
    "zigux_notifier_block alignment must track uintptr_t");

ZIGUX_STATIC_ASSERT(offsetof(zigux_notifier_chain_priority_increase, previous_index) == 0U,
    "zigux_notifier_chain_priority_increase.previous_index offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(zigux_notifier_chain_priority_increase, current_index) == sizeof(size_t),
    "zigux_notifier_chain_priority_increase.current_index offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(zigux_notifier_chain_priority_increase, previous_priority) == sizeof(size_t) * 2U,
    "zigux_notifier_chain_priority_increase.previous_priority offset drifted");
ZIGUX_STATIC_ASSERT(offsetof(zigux_notifier_chain_priority_increase, current_priority) == (sizeof(size_t) * 2U) + sizeof(int32_t),
    "zigux_notifier_chain_priority_increase.current_priority offset drifted");
ZIGUX_STATIC_ASSERT(_Alignof(zigux_notifier_chain_priority_increase) == _Alignof(size_t),
    "zigux_notifier_chain_priority_increase alignment must track size_t");

static inline int zigux_notifier_first_chain_priority_increase(
    const struct zigux_notifier_block *head,
    zigux_notifier_chain_priority_increase *out)
{
    int32_t previous_priority;
    size_t previous_index = 0;
    const struct zigux_notifier_block *node;

    if (!head)
        return 0;

    previous_priority = head->priority;
    while (head->next != (uintptr_t)0) {
        const size_t current_index = previous_index + 1;
        node = (const struct zigux_notifier_block *)(uintptr_t)head->next;
        if (node->priority > previous_priority) {
            if (out) {
                out->previous_index = previous_index;
                out->current_index = current_index;
                out->previous_priority = previous_priority;
                out->current_priority = node->priority;
            }
            return 1;
        }
        previous_index = current_index;
        previous_priority = node->priority;
        head = node;
    }

    return 0;
}

static inline int zigux_notifier_chain_has_nonincreasing_priority(
    const struct zigux_notifier_block *head)
{
    return !zigux_notifier_first_chain_priority_increase(head, NULL);
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

#endif
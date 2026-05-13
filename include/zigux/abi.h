#ifndef _ZIGUX_ABI_H
#define _ZIGUX_ABI_H

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

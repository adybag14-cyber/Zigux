#ifndef _ZIGUX_NOTIFIER_ABI_H
#define _ZIGUX_NOTIFIER_ABI_H

#include <stddef.h>
#include <stdint.h>

#define ZIGUX_NOTIFIER_DONE 0U
#define ZIGUX_NOTIFIER_OK 1U
#define ZIGUX_NOTIFIER_STOP 2U

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
    if (!head)
        return 0;

    return !zigux_list_first_broken_backlink(head, NULL);
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
    if (!head)
        return 0;

    return !zigux_hlist_first_broken_prev_link(head, NULL);
}

static inline int zigux_hlist_tail_next_is_null(
    const struct zigux_hlist_head *head)
{
    const struct zigux_hlist_node *cursor;
    const struct zigux_hlist_node *tail = NULL;

    if (!head)
        return 0;

    cursor = (const struct zigux_hlist_node *)(uintptr_t)head->first;
    while (cursor) {
        tail = cursor;
        cursor = (const struct zigux_hlist_node *)(uintptr_t)cursor->next;
    }

    return tail ? tail->next == (uintptr_t)0 : 1;
}

#endif /* _ZIGUX_NOTIFIER_ABI_H */

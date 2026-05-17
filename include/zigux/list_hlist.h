#ifndef ZIGUX_LIST_HLIST_H
#define ZIGUX_LIST_HLIST_H

#include <stdint.h>

#define ZIGUX_LIST_HLIST_ABI_VERSION 1u

#define ZIGUX_LIST_HEAD_SIZE ((uint32_t)(2u * sizeof(uintptr_t)))
#define ZIGUX_LIST_HEAD_ALIGN ((uint32_t)sizeof(uintptr_t))
#define ZIGUX_LIST_HEAD_NEXT_OFFSET 0u
#define ZIGUX_LIST_HEAD_PREV_OFFSET ((uint32_t)sizeof(uintptr_t))

#define ZIGUX_HLIST_HEAD_SIZE ((uint32_t)sizeof(uintptr_t))
#define ZIGUX_HLIST_HEAD_ALIGN ((uint32_t)sizeof(uintptr_t))
#define ZIGUX_HLIST_HEAD_FIRST_OFFSET 0u

#define ZIGUX_HLIST_NODE_SIZE ((uint32_t)(2u * sizeof(uintptr_t)))
#define ZIGUX_HLIST_NODE_ALIGN ((uint32_t)sizeof(uintptr_t))
#define ZIGUX_HLIST_NODE_NEXT_OFFSET 0u
#define ZIGUX_HLIST_NODE_PPREV_OFFSET ((uint32_t)sizeof(uintptr_t))

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

static inline struct zigux_list_head zigux_list_head_empty(void)
{
    struct zigux_list_head head = { 0, 0 };
    return head;
}

static inline struct zigux_hlist_head zigux_hlist_head_empty(void)
{
    struct zigux_hlist_head head = { 0 };
    return head;
}

static inline struct zigux_hlist_node zigux_hlist_node_empty(void)
{
    struct zigux_hlist_node node = { 0, 0 };
    return node;
}

#endif

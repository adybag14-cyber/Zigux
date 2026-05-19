#ifndef ZIGUX_LIST_HLIST_H
#define ZIGUX_LIST_HLIST_H

#include <stddef.h>
#include <zigux/abi.h>

#define ZIGUX_LIST_HLIST_ABI_VERSION 1u

#define ZIGUX_LIST_HEAD_SIZE ((uint32_t)sizeof(struct zigux_list_head))
#define ZIGUX_LIST_HEAD_ALIGN ((uint32_t)_Alignof(struct zigux_list_head))
#define ZIGUX_LIST_HEAD_NEXT_OFFSET ((uint32_t)offsetof(struct zigux_list_head, next))
#define ZIGUX_LIST_HEAD_PREV_OFFSET ((uint32_t)offsetof(struct zigux_list_head, prev))

#define ZIGUX_HLIST_HEAD_SIZE ((uint32_t)sizeof(struct zigux_hlist_head))
#define ZIGUX_HLIST_HEAD_ALIGN ((uint32_t)_Alignof(struct zigux_hlist_head))
#define ZIGUX_HLIST_HEAD_FIRST_OFFSET ((uint32_t)offsetof(struct zigux_hlist_head, first))

#define ZIGUX_HLIST_NODE_SIZE ((uint32_t)sizeof(struct zigux_hlist_node))
#define ZIGUX_HLIST_NODE_ALIGN ((uint32_t)_Alignof(struct zigux_hlist_node))
#define ZIGUX_HLIST_NODE_NEXT_OFFSET ((uint32_t)offsetof(struct zigux_hlist_node, next))
#define ZIGUX_HLIST_NODE_PPREV_OFFSET ((uint32_t)offsetof(struct zigux_hlist_node, pprev))

_Static_assert(ZIGUX_LIST_HLIST_ABI_VERSION == 1u, "Lane 28 list_hlist ABI version drifted");
_Static_assert(sizeof(struct zigux_list_head) == ZIGUX_LIST_HEAD_SIZE, "list_head size drifted");
_Static_assert(_Alignof(struct zigux_list_head) == ZIGUX_LIST_HEAD_ALIGN, "list_head align drifted");
_Static_assert(offsetof(struct zigux_list_head, next) == ZIGUX_LIST_HEAD_NEXT_OFFSET, "list_head next offset drifted");
_Static_assert(offsetof(struct zigux_list_head, prev) == ZIGUX_LIST_HEAD_PREV_OFFSET, "list_head prev offset drifted");
_Static_assert(sizeof(struct zigux_hlist_head) == ZIGUX_HLIST_HEAD_SIZE, "hlist_head size drifted");
_Static_assert(_Alignof(struct zigux_hlist_head) == ZIGUX_HLIST_HEAD_ALIGN, "hlist_head align drifted");
_Static_assert(offsetof(struct zigux_hlist_head, first) == ZIGUX_HLIST_HEAD_FIRST_OFFSET, "hlist_head first offset drifted");
_Static_assert(sizeof(struct zigux_hlist_node) == ZIGUX_HLIST_NODE_SIZE, "hlist_node size drifted");
_Static_assert(_Alignof(struct zigux_hlist_node) == ZIGUX_HLIST_NODE_ALIGN, "hlist_node align drifted");
_Static_assert(offsetof(struct zigux_hlist_node, next) == ZIGUX_HLIST_NODE_NEXT_OFFSET, "hlist_node next offset drifted");
_Static_assert(offsetof(struct zigux_hlist_node, pprev) == ZIGUX_HLIST_NODE_PPREV_OFFSET, "hlist_node pprev offset drifted");

static inline struct zigux_list_head zigux_list_head_make(uintptr_t next, uintptr_t prev)
{
    struct zigux_list_head head = {
        .next = next,
        .prev = prev,
    };
    return head;
}

static inline struct zigux_hlist_head zigux_hlist_head_make(uintptr_t first)
{
    struct zigux_hlist_head head = {
        .first = first,
    };
    return head;
}

static inline struct zigux_hlist_node zigux_hlist_node_make(uintptr_t next, uintptr_t pprev)
{
    struct zigux_hlist_node node = {
        .next = next,
        .pprev = pprev,
    };
    return node;
}

static inline struct zigux_list_head zigux_list_head_empty(void)
{
    return zigux_list_head_make(0, 0);
}

static inline struct zigux_hlist_head zigux_hlist_head_empty(void)
{
    return zigux_hlist_head_make(0);
}

static inline struct zigux_hlist_node zigux_hlist_node_empty(void)
{
    return zigux_hlist_node_make(0, 0);
}

#endif

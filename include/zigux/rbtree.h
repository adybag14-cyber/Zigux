#ifndef _ZIGUX_RBTREE_H
#define _ZIGUX_RBTREE_H

#include <stdint.h>

#define ZIGUX_RBTREE_ROOT_FLAG_EMPTY 1U
#define ZIGUX_RBTREE_ROOT_FLAG_CACHED 2U
#define ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID 4U

struct zigux_rbtree_root_view {
    unsigned long root_addr;
    unsigned long leftmost_addr;
    uint32_t flags;
    uint32_t reserved;
};

#define ZIGUX_RBTREE_ROOT_KNOWN_FLAG_MASK \
    (ZIGUX_RBTREE_ROOT_FLAG_EMPTY | ZIGUX_RBTREE_ROOT_FLAG_CACHED | ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID)

static inline struct zigux_rbtree_root_view zigux_rbtree_root_view_empty(void)
{
    return (struct zigux_rbtree_root_view){
        .root_addr = 0,
        .leftmost_addr = 0,
        .flags = ZIGUX_RBTREE_ROOT_FLAG_EMPTY,
        .reserved = 0,
    };
}

static inline struct zigux_rbtree_root_view zigux_rbtree_root_view_uncached(unsigned long root_addr)
{
    return (struct zigux_rbtree_root_view){
        .root_addr = root_addr,
        .leftmost_addr = 0,
        .flags = 0,
        .reserved = 0,
    };
}

static inline struct zigux_rbtree_root_view zigux_rbtree_root_view_cached(unsigned long root_addr,
                                                                          unsigned long leftmost_addr)
{
    return (struct zigux_rbtree_root_view){
        .root_addr = root_addr,
        .leftmost_addr = leftmost_addr,
        .flags = ZIGUX_RBTREE_ROOT_FLAG_CACHED | ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID,
        .reserved = 0,
    };
}

static inline int zigux_rbtree_root_view_is_empty(const struct zigux_rbtree_root_view *view)
{
    return view && (view->flags & ZIGUX_RBTREE_ROOT_FLAG_EMPTY) != 0;
}

static inline int zigux_rbtree_root_view_is_cached(const struct zigux_rbtree_root_view *view)
{
    return view && (view->flags & ZIGUX_RBTREE_ROOT_FLAG_CACHED) != 0;
}

static inline int zigux_rbtree_root_view_has_leftmost(const struct zigux_rbtree_root_view *view)
{
    return view && (view->flags & ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID) != 0;
}

static inline int zigux_rbtree_root_view_has_only_known_flags(const struct zigux_rbtree_root_view *view)
{
    return view && (view->flags & ~ZIGUX_RBTREE_ROOT_KNOWN_FLAG_MASK) == 0;
}

static inline int zigux_rbtree_root_view_has_root(const struct zigux_rbtree_root_view *view)
{
    return view && !zigux_rbtree_root_view_is_empty(view) && view->root_addr != 0;
}

static inline int zigux_rbtree_root_view_is_valid(const struct zigux_rbtree_root_view *view)
{
    if (!view)
        return 0;
    if (!zigux_rbtree_root_view_has_only_known_flags(view))
        return 0;
    if (view->reserved != 0)
        return 0;
    if (zigux_rbtree_root_view_is_empty(view) && view->root_addr != 0)
        return 0;
    if (!zigux_rbtree_root_view_is_empty(view) && view->root_addr == 0)
        return 0;
    if (zigux_rbtree_root_view_has_leftmost(view) != zigux_rbtree_root_view_is_cached(view))
        return 0;
    if (zigux_rbtree_root_view_is_cached(view) && view->leftmost_addr == 0)
        return 0;
    if (!zigux_rbtree_root_view_is_cached(view) && view->leftmost_addr != 0)
        return 0;
    return 1;
}

static inline int zigux_rbtree_root_view_canonicalize(const struct zigux_rbtree_root_view *view,
                                                      struct zigux_rbtree_root_view *out)
{
    if (!view || !out)
        return 0;
    if (!zigux_rbtree_root_view_is_valid(view))
        return 0;
    if (zigux_rbtree_root_view_is_empty(view)) {
        *out = zigux_rbtree_root_view_empty();
        return 1;
    }
    if (zigux_rbtree_root_view_is_cached(view)) {
        *out = zigux_rbtree_root_view_cached(view->root_addr, view->leftmost_addr);
        return 1;
    }
    *out = zigux_rbtree_root_view_uncached(view->root_addr);
    return 1;
}

static inline int zigux_rbtree_root_view_is_canonical(const struct zigux_rbtree_root_view *view)
{
    struct zigux_rbtree_root_view normalized;

    if (!zigux_rbtree_root_view_canonicalize(view, &normalized))
        return 0;

    return normalized.root_addr == view->root_addr &&
        normalized.leftmost_addr == view->leftmost_addr &&
        normalized.flags == view->flags &&
        normalized.reserved == view->reserved;
}

#endif

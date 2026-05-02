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

#endif

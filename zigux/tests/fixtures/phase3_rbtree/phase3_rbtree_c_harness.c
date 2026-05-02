#include <stddef.h>
#include <stdio.h>

#include <zigux/rbtree.h>

int main(void)
{
    printf(
        "{\"constants\":{\"root_flag_empty\":%u,\"root_flag_cached\":%u,\"root_flag_leftmost_valid\":%u},"
        "\"structs\":{\"zigux_rbtree_root_view\":{\"size\":%zu,\"align\":%zu,"
        "\"offsets\":{\"root_addr\":%zu,\"leftmost_addr\":%zu,\"flags\":%zu,\"reserved\":%zu}}}}\n",
        ZIGUX_RBTREE_ROOT_FLAG_EMPTY,
        ZIGUX_RBTREE_ROOT_FLAG_CACHED,
        ZIGUX_RBTREE_ROOT_FLAG_LEFTMOST_VALID,
        sizeof(struct zigux_rbtree_root_view),
        _Alignof(struct zigux_rbtree_root_view),
        offsetof(struct zigux_rbtree_root_view, root_addr),
        offsetof(struct zigux_rbtree_root_view, leftmost_addr),
        offsetof(struct zigux_rbtree_root_view, flags),
        offsetof(struct zigux_rbtree_root_view, reserved));
    return 0;
}

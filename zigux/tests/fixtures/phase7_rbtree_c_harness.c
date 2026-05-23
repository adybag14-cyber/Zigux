// SPDX-License-Identifier: GPL-2.0-only
#include <stdbool.h>
#include <stddef.h>

struct phase7_rbtree_ordered_duplicate_range_case {
    int inorder_keys[6];
    size_t inorder_key_count;
    size_t match_serials[3];
    size_t match_serial_count;
};

struct phase7_rbtree_cached_leftmost_promotion_case {
    int leftmost_before_erase;
    int leftmost_after_erase;
    int leftmost_after_replace;
};

struct phase7_rbtree_postorder_null_stop_case {
    int order[3];
    size_t order_count;
    bool detached_next_is_null;
};

struct phase7_rbtree_reverse_alias_detached_case {
    int reverse_order[4];
    size_t reverse_order_count;
    bool detached_prev_is_null;
};

struct phase7_rbtree_c_harness {
    const char *packet;
    const char *anchor;
    const char *current_master_state;
    struct phase7_rbtree_ordered_duplicate_range_case ordered_duplicate_range;
    struct phase7_rbtree_cached_leftmost_promotion_case cached_leftmost_promotion;
    struct phase7_rbtree_postorder_null_stop_case postorder_null_stop;
    struct phase7_rbtree_reverse_alias_detached_case reverse_alias_detached;
};

const struct phase7_rbtree_c_harness phase7_rbtree_c_harness = {
    .packet = "phase7-rbtree-parity-fixture",
    .anchor = "lib/rbtree.c",
    .current_master_state = "ordered-duplicate-cached-postorder-reverse-c-harness",
    .ordered_duplicate_range = {
        .inorder_keys = { 5, 10, 10, 10, 15, 20 },
        .inorder_key_count = 6,
        .match_serials = { 0, 2, 4 },
        .match_serial_count = 3,
    },
    .cached_leftmost_promotion = {
        .leftmost_before_erase = 5,
        .leftmost_after_erase = 10,
        .leftmost_after_replace = 10,
    },
    .postorder_null_stop = {
        .order = { 1, 3, 2 },
        .order_count = 3,
        .detached_next_is_null = true,
    },
    .reverse_alias_detached = {
        .reverse_order = { 4, 3, 2, 1 },
        .reverse_order_count = 4,
        .detached_prev_is_null = true,
    },
};
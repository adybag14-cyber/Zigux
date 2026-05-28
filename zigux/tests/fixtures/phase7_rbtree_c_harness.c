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

struct phase7_rbtree_non_leftmost_cached_erase_case {
    int leftmost_after_erase;
    int right_predecessor_key;
    int remaining_left_key;
    bool erased_node_requires_clear;
};

struct phase7_rbtree_singleton_cached_erase_case {
    bool leftmost_after_erase_is_null;
    bool root_after_erase_is_null;
    bool erased_node_requires_clear;
};

struct phase7_rbtree_plain_erase_init_reseed_case {
    int inorder_after_root_erase[2];
    size_t inorder_after_root_erase_count;
    int leftmost_after_reseed;
    int last_after_reseed;
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

struct phase7_rbtree_cached_churn_invariants_case {
    int leftmost_checkpoints[6];
    size_t leftmost_checkpoint_count;
    int promoted_leftmost_after_erase;
    int replacement_leftmost;
    int leftmost_after_detach;
    int leftmost_after_new_minimum;
    bool root_stays_black;
    bool invariants_hold_after_each_step;
};

struct phase7_rbtree_c_harness {
    const char *packet;
    const char *anchor;
    const char *current_master_state;
    struct phase7_rbtree_ordered_duplicate_range_case ordered_duplicate_range;
    struct phase7_rbtree_cached_leftmost_promotion_case cached_leftmost_promotion;
    struct phase7_rbtree_non_leftmost_cached_erase_case non_leftmost_cached_erase;
    struct phase7_rbtree_singleton_cached_erase_case singleton_cached_erase;
    struct phase7_rbtree_plain_erase_init_reseed_case plain_erase_init_reseed;
    struct phase7_rbtree_postorder_null_stop_case postorder_null_stop;
    struct phase7_rbtree_reverse_alias_detached_case reverse_alias_detached;
    struct phase7_rbtree_cached_churn_invariants_case cached_churn_invariants;
};

const struct phase7_rbtree_c_harness phase7_rbtree_c_harness = {
    .packet = "phase7-rbtree-parity-fixture",
    .anchor = "lib/rbtree.c",
    .current_master_state = "ordered-duplicate-cached-eraseinit-postorder-reverse-c-harness",
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
    .non_leftmost_cached_erase = {
        .leftmost_after_erase = 5,
        .right_predecessor_key = 5,
        .remaining_left_key = 5,
        .erased_node_requires_clear = true,
    },
    .singleton_cached_erase = {
        .leftmost_after_erase_is_null = true,
        .root_after_erase_is_null = true,
        .erased_node_requires_clear = true,
    },
    .plain_erase_init_reseed = {
        .inorder_after_root_erase = { 5, 15 },
        .inorder_after_root_erase_count = 2,
        .leftmost_after_reseed = 12,
        .last_after_reseed = 12,
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
    .cached_churn_invariants = {
        .leftmost_checkpoints = { 1, 5, 5, 5, 7, 0 },
        .leftmost_checkpoint_count = 6,
        .promoted_leftmost_after_erase = 5,
        .replacement_leftmost = 5,
        .leftmost_after_detach = 7,
        .leftmost_after_new_minimum = 0,
        .root_stays_black = true,
        .invariants_hold_after_each_step = true,
    },
};

#ifndef ZIGUX_BITMAP_CPUMASK_H
#define ZIGUX_BITMAP_CPUMASK_H

#include <stdint.h>

#define ZIGUX_BITMAP_VIEW_ABI_VERSION 1u
#define ZIGUX_BITMAP_SUMMARY_ABI_VERSION 1u
#define ZIGUX_CPUMASK_VIEW_ABI_VERSION 1u

struct zigux_bitmap_view {
    uintptr_t words_addr;
    uint32_t nbits;
    uint32_t word_count;
};

struct zigux_bitmap_summary {
    uint32_t first_set;
    uint32_t first_zero;
    uint32_t weight;
    uint32_t reserved;
};

struct zigux_cpumask_view {
    uintptr_t words_addr;
    uint32_t nbits;
    uint32_t word_count;
    uint32_t nr_cpu_ids;
    uint32_t reserved;
};

static inline struct zigux_bitmap_view zigux_bitmap_view_make(
    uintptr_t words_addr,
    uint32_t nbits,
    uint32_t word_count
) {
    struct zigux_bitmap_view view = {
        .words_addr = words_addr,
        .nbits = nbits,
        .word_count = word_count,
    };
    return view;
}

static inline struct zigux_cpumask_view zigux_cpumask_view_make(
    uintptr_t words_addr,
    uint32_t nbits,
    uint32_t word_count,
    uint32_t nr_cpu_ids
) {
    struct zigux_cpumask_view view = {
        .words_addr = words_addr,
        .nbits = nbits,
        .word_count = word_count,
        .nr_cpu_ids = nr_cpu_ids,
        .reserved = 0u,
    };
    return view;
}

#endif

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define CHUNK_SIZE_BYTES 128U
#define WORD_BITS ((uint32_t)(sizeof(size_t) * 8U))
#define BITMAP_LONGS ((uint32_t)(CHUNK_SIZE_BYTES / sizeof(size_t)))
#define BITMAP_BITS (BITMAP_LONGS * WORD_BITS)

struct selection {
    uint32_t id;
    uint32_t relative_bit;
};

struct window {
    uint32_t first_id;
    uint32_t last_id;
    uint32_t first_relative_bit;
    uint32_t last_relative_bit;
    uint32_t span_len;
};

struct summary {
    struct window window;
    uint32_t allocated_bits;
    bool has_first_allocated;
    struct selection first_allocated;
    bool has_first_free;
    struct selection first_free;
    bool fully_allocated;
    bool fully_free;
};

static bool bit_is_set(const size_t *words, uint32_t relative_bit) {
    const uint32_t word_index = relative_bit / WORD_BITS;
    const uint32_t bit_index = relative_bit % WORD_BITS;
    return (words[word_index] & ((size_t)1u << bit_index)) != 0;
}

static bool clamp_window(uint32_t chunk_base, uint32_t min_id, uint32_t max_id, struct window *out) {
    const uint32_t chunk_end = chunk_base + BITMAP_BITS - 1U;
    uint32_t first_id;
    uint32_t last_id;

    if (min_id > max_id) {
        return false;
    }
    if (max_id < chunk_base || min_id > chunk_end) {
        return false;
    }

    first_id = min_id > chunk_base ? min_id : chunk_base;
    last_id = max_id < chunk_end ? max_id : chunk_end;

    out->first_id = first_id;
    out->last_id = last_id;
    out->first_relative_bit = first_id - chunk_base;
    out->last_relative_bit = last_id - chunk_base;
    out->span_len = last_id - first_id + 1U;
    return true;
}

static bool summarize(
    const size_t *words,
    uint32_t chunk_base,
    uint32_t min_id,
    uint32_t max_id,
    struct summary *out
) {
    struct window window;
    uint32_t id;
    bool first_allocated_seen = false;
    bool first_free_seen = false;
    uint32_t allocated_bits = 0;

    if (!clamp_window(chunk_base, min_id, max_id, &window)) {
        return false;
    }

    out->window = window;
    for (id = window.first_id; id <= window.last_id; ++id) {
        const uint32_t relative_bit = id - chunk_base;
        if (bit_is_set(words, relative_bit)) {
            allocated_bits += 1U;
            if (!first_allocated_seen) {
                out->first_allocated.id = id;
                out->first_allocated.relative_bit = relative_bit;
                first_allocated_seen = true;
            }
        } else if (!first_free_seen) {
            out->first_free.id = id;
            out->first_free.relative_bit = relative_bit;
            first_free_seen = true;
        }
    }

    out->allocated_bits = allocated_bits;
    out->has_first_allocated = first_allocated_seen;
    out->has_first_free = first_free_seen;
    out->fully_allocated = allocated_bits == window.span_len;
    out->fully_free = allocated_bits == 0U;
    return true;
}

static void write_selection(const struct selection *selection) {
    printf("{\"id\":%u,\"relative_bit\":%u}", selection->id, selection->relative_bit);
}

static void write_summary(const struct summary *summary) {
    printf("{");
    printf("\"window\":{");
    printf("\"first_id\":%u,", summary->window.first_id);
    printf("\"last_id\":%u,", summary->window.last_id);
    printf("\"first_relative_bit\":%u,", summary->window.first_relative_bit);
    printf("\"last_relative_bit\":%u,", summary->window.last_relative_bit);
    printf("\"span_len\":%u", summary->window.span_len);
    printf("},");
    printf("\"allocated_bits\":%u,", summary->allocated_bits);
    printf("\"first_allocated\":");
    if (summary->has_first_allocated) {
        write_selection(&summary->first_allocated);
    } else {
        printf("null");
    }
    printf(",");
    printf("\"first_free\":");
    if (summary->has_first_free) {
        write_selection(&summary->first_free);
    } else {
        printf("null");
    }
    printf(",");
    printf("\"fully_allocated\":%s,", summary->fully_allocated ? "true" : "false");
    printf("\"fully_free\":%s", summary->fully_free ? "true" : "false");
    printf("}");
}

static void write_case(
    const char *name,
    const size_t *words,
    uint32_t chunk_base,
    uint32_t min_id,
    uint32_t max_id,
    bool trailing_comma
) {
    struct summary summary;
    const bool has_summary = summarize(words, chunk_base, min_id, max_id, &summary);

    printf("{\"name\":\"%s\",\"summary\":", name);
    if (has_summary) {
        write_summary(&summary);
    } else {
        printf("null");
    }
    printf("}");
    if (trailing_comma) {
        printf(",");
    }
}

int main(void) {
    size_t floor_words[BITMAP_LONGS];
    size_t ceiling_words[BITMAP_LONGS];
    size_t clear_words[BITMAP_LONGS];
    const uint32_t high_a = BITMAP_BITS - 2U;
    const uint32_t high_b = BITMAP_BITS - 1U;

    memset(floor_words, 0, sizeof(floor_words));
    memset(ceiling_words, 0, sizeof(ceiling_words));
    memset(clear_words, 0, sizeof(clear_words));

    floor_words[0] |= ((size_t)1u << 0) | ((size_t)1u << 2) | ((size_t)1u << 3);
    ceiling_words[high_a / WORD_BITS] |= (size_t)1u << (high_a % WORD_BITS);
    ceiling_words[high_b / WORD_BITS] |= (size_t)1u << (high_b % WORD_BITS);

    printf("[");
    write_case("clamped_floor_partial", floor_words, 1024, 1000, 1027, true);
    write_case("clamped_ceiling_full", ceiling_words, 2048, 3070, 4096, true);
    write_case("clear_middle_window", clear_words, 0, 8, 11, true);
    write_case("disjoint_window", clear_words, 0, 2048, 2050, true);
    write_case("unordered_window", clear_words, 0, 17, 12, false);
    printf("]\n");
    return 0;
}

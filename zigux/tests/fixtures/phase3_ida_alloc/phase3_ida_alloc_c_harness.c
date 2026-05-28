#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define CHUNK_SIZE_BYTES 128u
#define WORD_BITS ((uint32_t)(sizeof(uintptr_t) * 8u))
#define BITMAP_LONGS (CHUNK_SIZE_BYTES / sizeof(uintptr_t))
#define BITMAP_BITS (BITMAP_LONGS * WORD_BITS)

struct selection {
    uint32_t id;
    uint32_t relative_bit;
    bool present;
};

static bool range_is_ordered(uint32_t min_id, uint32_t max_id)
{
    return min_id <= max_id;
}

static uint32_t chunk_end(uint32_t chunk_base)
{
    return chunk_base + BITMAP_BITS - 1u;
}

static bool intersects_range(uint32_t chunk_base, uint32_t min_id, uint32_t max_id)
{
    return range_is_ordered(min_id, max_id) &&
        max_id >= chunk_base &&
        min_id <= chunk_end(chunk_base);
}

static bool is_set(const uintptr_t *words, uint32_t relative_bit)
{
    const uint32_t word_index = relative_bit / WORD_BITS;
    const uint32_t bit_index = relative_bit % WORD_BITS;
    return (words[word_index] & ((uintptr_t)1u << bit_index)) != 0;
}

static struct selection first_candidate(
    uint32_t chunk_base,
    uint32_t min_id,
    uint32_t max_id)
{
    struct selection selection = { .id = 0, .relative_bit = 0, .present = false };
    if (!intersects_range(chunk_base, min_id, max_id))
        return selection;

    selection.id = min_id > chunk_base ? min_id : chunk_base;
    selection.relative_bit = selection.id - chunk_base;
    selection.present = true;
    return selection;
}

static struct selection last_candidate(
    uint32_t chunk_base,
    uint32_t min_id,
    uint32_t max_id)
{
    struct selection selection = { .id = 0, .relative_bit = 0, .present = false };
    const uint32_t ceiling = chunk_end(chunk_base);
    if (!intersects_range(chunk_base, min_id, max_id))
        return selection;

    selection.id = max_id < ceiling ? max_id : ceiling;
    selection.relative_bit = selection.id - chunk_base;
    selection.present = true;
    return selection;
}

static struct selection first_free(
    const uintptr_t *words,
    uint32_t chunk_base,
    uint32_t min_id,
    uint32_t max_id)
{
    struct selection selection = first_candidate(chunk_base, min_id, max_id);
    const struct selection last = last_candidate(chunk_base, min_id, max_id);
    uint32_t id;

    if (!selection.present || !last.present)
        return selection;

    for (id = selection.id; id <= last.id; ++id) {
        const uint32_t relative_bit = id - chunk_base;
        if (!is_set(words, relative_bit)) {
            selection.id = id;
            selection.relative_bit = relative_bit;
            selection.present = true;
            return selection;
        }
    }

    selection.present = false;
    selection.id = 0;
    selection.relative_bit = 0;
    return selection;
}

static void write_selection(const struct selection *selection)
{
    if (!selection->present) {
        fputs("null", stdout);
        return;
    }

    printf("{\"id\":%" PRIu32 ",\"relative_bit\":%" PRIu32 "}",
        selection->id, selection->relative_bit);
}

static void write_case(
    const char *name,
    const uintptr_t *words,
    uint32_t chunk_base,
    uint32_t min_id,
    uint32_t max_id,
    bool trailing_comma)
{
    const struct selection first = first_candidate(chunk_base, min_id, max_id);
    const struct selection last = last_candidate(chunk_base, min_id, max_id);
    const struct selection free_slot = first_free(words, chunk_base, min_id, max_id);

    printf(
        "    {\n"
        "      \"name\": \"%s\",\n"
        "      \"ordered\": %s,\n"
        "      \"first_candidate\": ",
        name,
        range_is_ordered(min_id, max_id) ? "true" : "false");
    write_selection(&first);
    fputs(",\n      \"last_candidate\": ", stdout);
    write_selection(&last);
    fputs(",\n      \"first_free\": ", stdout);
    write_selection(&free_slot);
    fputs("\n    }", stdout);
    if (trailing_comma)
        fputc(',', stdout);
    fputc('\n', stdout);
}

int main(void)
{
    uintptr_t empty_words[BITMAP_LONGS] = {0};
    uintptr_t sparse_words[BITMAP_LONGS] = {0};
    uintptr_t floor_words[BITMAP_LONGS] = {0};
    uintptr_t ceiling_words[BITMAP_LONGS] = {0};
    uintptr_t full_window_words[BITMAP_LONGS] = {0};

    sparse_words[0] = ((uintptr_t)1u << 0) | ((uintptr_t)1u << 1) | ((uintptr_t)1u << 3);
    floor_words[0] = (uintptr_t)1u;
    ceiling_words[(BITMAP_BITS - 2u) / WORD_BITS] |=
        (uintptr_t)1u << ((BITMAP_BITS - 2u) % WORD_BITS);
    full_window_words[0] = (uintptr_t)0xffu;

    printf("{\n  \"bitmap_bits\": %" PRIu32 ",\n  \"cases\": [\n", BITMAP_BITS);
    write_case("empty_window", empty_words, 0, 0, 7, true);
    write_case("sparse_window", sparse_words, 0, 0, 7, true);
    write_case("clamped_floor_window", floor_words, 1024, 1000, 1027, true);
    write_case("clamped_ceiling_window", ceiling_words, 2048, 3070, 4096, true);
    write_case("disjoint_window", empty_words, 4096, 0, 100, true);
    write_case("unordered_window", empty_words, 0, 9, 3, true);
    write_case("full_window", full_window_words, 0, 0, 7, false);
    fputs("  ]\n}\n", stdout);
    return 0;
}

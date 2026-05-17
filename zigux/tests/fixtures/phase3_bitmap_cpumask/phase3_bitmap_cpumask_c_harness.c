#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

#include "../../../../include/zigux/bitmap_cpumask.h"

static uint32_t bits_per_word(void) {
    return (uint32_t)(sizeof(uintptr_t) * 8U);
}

static uint32_t word_count(uint32_t nbits) {
    const uint32_t bpw = bits_per_word();
    return nbits == 0 ? 0 : (nbits + bpw - 1U) / bpw;
}

static uintptr_t last_word_mask(uint32_t nbits) {
    const uint32_t bpw = bits_per_word();
    const uint32_t remainder = nbits % bpw;
    if (nbits == 0) {
        return 0;
    }
    if (remainder == 0) {
        return ~(uintptr_t)0;
    }
    return ~(uintptr_t)0 >> (bpw - remainder);
}

static const uintptr_t *words(const struct zigux_bitmap_view *view) {
    return (const uintptr_t *)(uintptr_t)view->words_addr;
}

static int test_bit(struct zigux_bitmap_view view, uint32_t bit) {
    const uintptr_t *slice;
    uint32_t word_index;
    uint32_t bit_index;
    if (bit >= view.nbits || view.word_count == 0) {
        return 0;
    }
    slice = words(&view);
    word_index = bit / bits_per_word();
    bit_index = bit % bits_per_word();
    return ((slice[word_index] >> bit_index) & 1U) != 0;
}

static uint32_t first_set(struct zigux_bitmap_view view) {
    const uintptr_t *slice = words(&view);
    uint32_t index;
    if (view.word_count == 0) {
        return view.nbits;
    }
    for (index = 0; index < view.word_count; ++index) {
        uintptr_t masked = slice[index];
        uint32_t offset = 0;
        if (index + 1U == view.word_count) {
            masked &= last_word_mask(view.nbits);
        }
        if (masked == 0) {
            continue;
        }
        while (((masked >> offset) & 1U) == 0U) {
            ++offset;
        }
        return index * bits_per_word() + offset;
    }
    return view.nbits;
}

static uint32_t first_zero(struct zigux_bitmap_view view) {
    const uintptr_t *slice = words(&view);
    uint32_t index;
    if (view.word_count == 0) {
        return view.nbits;
    }
    for (index = 0; index < view.word_count; ++index) {
        uintptr_t masked = ~slice[index];
        uint32_t offset = 0;
        if (index + 1U == view.word_count) {
            masked &= last_word_mask(view.nbits);
        }
        if (masked == 0) {
            continue;
        }
        while (((masked >> offset) & 1U) == 0U) {
            ++offset;
        }
        return index * bits_per_word() + offset;
    }
    return view.nbits;
}

static uint32_t weight(struct zigux_bitmap_view view) {
    const uintptr_t *slice = words(&view);
    uint32_t index;
    uint32_t total = 0;
    for (index = 0; index < view.word_count; ++index) {
        uintptr_t masked = slice[index];
        if (index + 1U == view.word_count) {
            masked &= last_word_mask(view.nbits);
        }
        while (masked != 0U) {
            total += (uint32_t)(masked & 1U);
            masked >>= 1U;
        }
    }
    return total;
}

static struct zigux_bitmap_summary summarize(struct zigux_bitmap_view view) {
    struct zigux_bitmap_summary summary = {
        .first_set = first_set(view),
        .first_zero = first_zero(view),
        .weight = weight(view),
        .reserved = 0U,
    };
    return summary;
}

static void write_nullable_u32(const uint32_t *value) {
    if (value != NULL) {
        printf("%" PRIu32, *value);
        return;
    }
    printf("null");
}

static void write_case(
    const char *name,
    const char *kind,
    uint32_t nbits,
    const uint32_t *nr_cpu_ids,
    uint32_t wc,
    uint32_t first,
    uint32_t zero,
    uint32_t total,
    uint32_t probe_present_index,
    int probe_present,
    uint32_t probe_absent_index,
    int probe_absent,
    int trailing_comma
) {
    printf("    {\n");
    printf("      \"name\": \"%s\",\n", name);
    printf("      \"kind\": \"%s\",\n", kind);
    printf("      \"nbits\": %" PRIu32 ",\n", nbits);
    printf("      \"nr_cpu_ids\": ");
    write_nullable_u32(nr_cpu_ids);
    printf(",\n");
    printf("      \"word_count\": %" PRIu32 ",\n", wc);
    printf("      \"first_set\": %" PRIu32 ",\n", first);
    printf("      \"first_zero\": %" PRIu32 ",\n", zero);
    printf("      \"weight\": %" PRIu32 ",\n", total);
    printf("      \"probe_present_index\": %" PRIu32 ",\n", probe_present_index);
    printf("      \"probe_present\": %s,\n", probe_present ? "true" : "false");
    printf("      \"probe_absent_index\": %" PRIu32 ",\n", probe_absent_index);
    printf("      \"probe_absent\": %s\n", probe_absent ? "true" : "false");
    printf("    }");
    if (trailing_comma) {
        printf(",");
    }
    printf("\n");
}

int main(void) {
    uintptr_t bitmap_words[2];
    uintptr_t cpumask_words[1];
    struct zigux_bitmap_view bitmap;
    struct zigux_cpumask_view cpumask;
    struct zigux_bitmap_summary bitmap_summary;
    struct zigux_bitmap_summary cpumask_summary;
    uint32_t cpumask_nr = 16U;

    bitmap_words[0] = ((uintptr_t)1 << 1) | ((uintptr_t)1 << 3) | ((uintptr_t)1 << 5);
    bitmap_words[1] = ((uintptr_t)1 << 1) | ((uintptr_t)1 << 5) | ((uintptr_t)1 << 10);
    cpumask_words[0] = ((uintptr_t)1 << 0) | ((uintptr_t)1 << 2) | ((uintptr_t)1 << 7);

    bitmap = zigux_bitmap_view_make((uintptr_t)bitmap_words, bits_per_word() + 6U, word_count(bits_per_word() + 6U));
    cpumask = zigux_cpumask_view_make((uintptr_t)cpumask_words, 16U, word_count(16U), 16U);
    bitmap_summary = summarize(bitmap);
    cpumask_summary = summarize(zigux_bitmap_view_make(cpumask.words_addr, cpumask.nbits, cpumask.word_count));

    printf("{\n");
    printf("  \"word_bits\": %zu,\n", sizeof(uintptr_t) * 8U);
    printf("  \"bitmap_view_abi_version\": %u,\n", ZIGUX_BITMAP_VIEW_ABI_VERSION);
    printf("  \"cpumask_view_abi_version\": %u,\n", ZIGUX_CPUMASK_VIEW_ABI_VERSION);
    printf("  \"cases\": [\n");

    write_case(
        "bitmap_tail_masked",
        "bitmap",
        bitmap.nbits,
        NULL,
        bitmap.word_count,
        bitmap_summary.first_set,
        bitmap_summary.first_zero,
        bitmap_summary.weight,
        69U,
        test_bit(bitmap, 69U),
        66U,
        test_bit(bitmap, 66U),
        1
    );
    write_case(
        "cpumask_window",
        "cpumask",
        cpumask.nbits,
        &cpumask_nr,
        cpumask.word_count,
        cpumask_summary.first_set,
        cpumask_summary.first_zero,
        cpumask_summary.weight,
        7U,
        test_bit(zigux_bitmap_view_make(cpumask.words_addr, cpumask.nbits, cpumask.word_count), 7U),
        1U,
        test_bit(zigux_bitmap_view_make(cpumask.words_addr, cpumask.nbits, cpumask.word_count), 1U),
        0
    );

    printf("  ]\n");
    printf("}\n");
    return 0;
}

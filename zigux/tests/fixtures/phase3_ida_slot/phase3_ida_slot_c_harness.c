#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define MAX_ERRNO ((uintptr_t)4095)
#define ERR_FLOOR ((uintptr_t)(-(intptr_t)MAX_ERRNO))
#define VALUE_TAG_MASK ((uintptr_t)0x1)
#define INLINE_BIT_CAPACITY ((unsigned)(sizeof(uintptr_t) * 8U - 1U))

static bool is_err_value(uintptr_t raw) {
    return raw >= ERR_FLOOR;
}

static bool is_inline_value(uintptr_t raw) {
    return (raw & VALUE_TAG_MASK) == VALUE_TAG_MASK && !is_err_value(raw);
}

static const char *kind_name(uintptr_t raw) {
    if (raw == 0) {
        return "empty";
    }
    if (is_err_value(raw)) {
        return "unexpected_err";
    }
    if (is_inline_value(raw)) {
        return "inline_bits";
    }
    return "bitmap_pointer";
}

static uint64_t inline_mask(uintptr_t raw) {
    return (uint64_t)(raw >> 1);
}

static unsigned inline_bit_count(uint64_t mask) {
    unsigned count = 0;
    while (mask != 0) {
        count += (unsigned)(mask & 1U);
        mask >>= 1U;
    }
    return count;
}

static int first_inline_bit(uint64_t mask) {
    if (mask == 0) {
        return -1;
    }
    for (unsigned bit = 0; bit < INLINE_BIT_CAPACITY; ++bit) {
        if ((mask & ((uint64_t)1U << bit)) != 0) {
            return (int)bit;
        }
    }
    return -1;
}

static void write_optional_u64(uint64_t value, bool present) {
    if (present) {
        printf("%" PRIu64, value);
        return;
    }
    printf("null");
}

static void write_optional_i64(int64_t value, bool present) {
    if (present) {
        printf("%" PRId64, value);
        return;
    }
    printf("null");
}

static void write_case(const char *name, uintptr_t raw, bool trailing_comma) {
    const bool inline_bits = is_inline_value(raw);
    const bool unexpected_err = is_err_value(raw);
    const bool bitmap_pointer = raw != 0 && !inline_bits && !unexpected_err;
    const uint64_t mask = inline_bits ? inline_mask(raw) : 0;
    const int first_bit = inline_bits ? first_inline_bit(mask) : -1;

    printf("    {\n");
    printf("      \"name\": \"%s\",\n", name);
    printf("      \"kind\": \"%s\",\n", kind_name(raw));
    printf("      \"raw_hex\": \"0x%" PRIxPTR "\",\n", raw);
    printf("      \"inline_mask\": ");
    write_optional_u64(mask, inline_bits);
    printf(",\n      \"inline_bit_count\": ");
    write_optional_u64((uint64_t)inline_bit_count(mask), inline_bits);
    printf(",\n      \"first_inline_bit\": ");
    write_optional_u64((uint64_t)first_bit, inline_bits && first_bit >= 0);
    printf(",\n      \"bitmap_pointer\": ");
    write_optional_u64((uint64_t)raw, bitmap_pointer);
    printf(",\n      \"unexpected_error\": ");
    write_optional_i64((int64_t)(intptr_t)raw, unexpected_err);
    printf("\n    }");
    if (trailing_comma) {
        printf(",");
    }
    printf("\n");
}

int main(void) {
    const uintptr_t inline_one = ((uintptr_t)1U << 1U) | VALUE_TAG_MASK;
    const uintptr_t inline_sparse = (((uintptr_t)1U << 1U) | ((uintptr_t)1U << 4U) | ((uintptr_t)1U << 9U)) << 1U | VALUE_TAG_MASK;
    const uintptr_t inline_top = ((uintptr_t)1U << (INLINE_BIT_CAPACITY - 1U)) << 1U | VALUE_TAG_MASK;

    printf("{\n");
    printf("  \"word_bits\": %u,\n", (unsigned)(sizeof(uintptr_t) * 8U));
    printf("  \"inline_bit_capacity\": %u,\n", INLINE_BIT_CAPACITY);
    printf("  \"cases\": [\n");
    write_case("empty", 0, true);
    write_case("inline_one", inline_one, true);
    write_case("inline_sparse", inline_sparse, true);
    write_case("inline_top", inline_top, true);
    write_case("bitmap_pointer", (uintptr_t)0x4000, true);
    write_case("unexpected_err", (uintptr_t)(intptr_t)-22, false);
    printf("  ]\n}\n");
    return 0;
}

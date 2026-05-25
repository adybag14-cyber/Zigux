#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

static uintptr_t tail_mask(size_t bit_len, size_t word_bits) {
    const size_t remainder = bit_len % word_bits;
    if (remainder == 0) {
        return ~(uintptr_t)0;
    }
    return (((uintptr_t)1) << remainder) - 1;
}

static size_t active_word_len(size_t bit_len, size_t word_bits) {
    if (bit_len == 0) {
        return 0;
    }
    return (bit_len + (word_bits - 1)) / word_bits;
}

static size_t count_set_bits(const uintptr_t *words, size_t word_count, size_t bit_len) {
    (void)word_count;
    const size_t word_bits = sizeof(uintptr_t) * 8;
    const size_t active_len = active_word_len(bit_len, word_bits);
    size_t total = 0;

    for (size_t index = 0; index < active_len; ++index) {
        uintptr_t masked = words[index];
        if (index + 1 == active_len) {
            masked &= tail_mask(bit_len, word_bits);
        }
        total += (size_t)__builtin_popcountll((unsigned long long)masked);
    }
    return total;
}

static int first_set_bit(const uintptr_t *words, size_t word_count, size_t bit_len) {
    (void)word_count;
    const size_t word_bits = sizeof(uintptr_t) * 8;
    const size_t active_len = active_word_len(bit_len, word_bits);

    for (size_t index = 0; index < active_len; ++index) {
        uintptr_t masked = words[index];
        if (index + 1 == active_len) {
            masked &= tail_mask(bit_len, word_bits);
        }
        if (masked == 0) {
            continue;
        }
        return (int)(index * word_bits + (size_t)__builtin_ctzll((unsigned long long)masked));
    }
    return -1;
}

static int first_clear_bit(const uintptr_t *words, size_t word_count, size_t bit_len) {
    (void)word_count;
    if (bit_len == 0) {
        return -1;
    }

    const size_t word_bits = sizeof(uintptr_t) * 8;
    const size_t active_len = active_word_len(bit_len, word_bits);

    for (size_t index = 0; index < active_len; ++index) {
        uintptr_t masked = ~words[index];
        if (index + 1 == active_len) {
            masked &= tail_mask(bit_len, word_bits);
        }
        if (masked == 0) {
            continue;
        }
        return (int)(index * word_bits + (size_t)__builtin_ctzll((unsigned long long)masked));
    }
    return -1;
}

static bool has_cpu(const uintptr_t *words, size_t bit_len, size_t cpu) {
    if (cpu >= bit_len) {
        return false;
    }
    const size_t word_bits = sizeof(uintptr_t) * 8;
    return (words[cpu / word_bits] & (((uintptr_t)1) << (cpu % word_bits))) != 0;
}

static bool is_subset_of(
    const uintptr_t *lhs,
    const uintptr_t *rhs,
    size_t word_count,
    size_t bit_len
) {
    const size_t word_bits = sizeof(uintptr_t) * 8;
    const size_t active_len = active_word_len(bit_len, word_bits);

    for (size_t index = 0; index < active_len; ++index) {
        uintptr_t masked = lhs[index];
        if (index + 1 == active_len) {
            masked &= tail_mask(bit_len, word_bits);
        }
        if ((masked & ~rhs[index]) != 0) {
            return false;
        }
    }
    (void)word_count;
    return true;
}

static bool intersects(
    const uintptr_t *lhs,
    const uintptr_t *rhs,
    size_t word_count,
    size_t bit_len
) {
    const size_t word_bits = sizeof(uintptr_t) * 8;
    const size_t active_len = active_word_len(bit_len, word_bits);

    for (size_t index = 0; index < active_len; ++index) {
        uintptr_t overlap = lhs[index] & rhs[index];
        if (index + 1 == active_len) {
            overlap &= tail_mask(bit_len, word_bits);
        }
        if (overlap != 0) {
            return true;
        }
    }
    (void)word_count;
    return false;
}

int main(void) {
    const size_t word_bits = sizeof(uintptr_t) * 8;

    const uintptr_t bitmap_full_words[] = { ~(uintptr_t)0, ~(uintptr_t)0 };
    const size_t bitmap_full_capacity = word_bits + 3;

    const uintptr_t bitmap_sparse_words[] = {
        (((uintptr_t)1) << 2) |
        (((uintptr_t)1) << 9),
    };

    const uintptr_t cpumask_presence_words[] = {
        (((uintptr_t)1) << 0) |
        (((uintptr_t)1) << 2) |
        (((uintptr_t)1) << 7),
    };

    const uintptr_t cpumask_base_words[] = {
        (((uintptr_t)1) << 1) |
        (((uintptr_t)1) << 4),
        ~(uintptr_t)0,
    };
    const uintptr_t cpumask_superset_words[] = {
        (((uintptr_t)1) << 1) |
        (((uintptr_t)1) << 3) |
        (((uintptr_t)1) << 4),
        0,
    };
    const uintptr_t cpumask_disjoint_words[] = {
        (((uintptr_t)1) << 0) |
        (((uintptr_t)1) << 2),
        0,
    };

    printf(
        "{\n"
        "  \"word_bits\": %zu,\n"
        "  \"cases\": [\n"
        "    {\n"
        "      \"name\": \"bitmap_full_range\",\n"
        "      \"capacity\": %zu,\n"
        "      \"set_count\": %zu,\n"
        "      \"first_set_bit\": %d,\n"
        "      \"first_clear_bit\": null\n"
        "    },\n"
        "    {\n"
        "      \"name\": \"bitmap_sparse\",\n"
        "      \"capacity\": 16,\n"
        "      \"is_set_2\": %s,\n"
        "      \"is_set_3\": %s,\n"
        "      \"set_count\": %zu,\n"
        "      \"first_set_bit\": %d,\n"
        "      \"first_clear_bit\": %d\n"
        "    },\n"
        "    {\n"
        "      \"name\": \"cpumask_presence\",\n"
        "      \"capacity\": 8,\n"
        "      \"has_cpu_0\": %s,\n"
        "      \"has_cpu_1\": %s,\n"
        "      \"has_cpu_7\": %s,\n"
        "      \"present_count\": %zu,\n"
        "      \"first_cpu\": %d,\n"
        "      \"first_missing_cpu\": %d\n"
        "    },\n"
        "    {\n"
        "      \"name\": \"cpumask_subset_overlap\",\n"
        "      \"capacity\": 8,\n"
        "      \"base_subset_of_superset\": %s,\n"
        "      \"superset_subset_of_base\": %s,\n"
        "      \"base_intersects_superset\": %s,\n"
        "      \"base_intersects_disjoint\": %s\n"
        "    }\n"
        "  ]\n"
        "}\n",
        word_bits,
        bitmap_full_capacity,
        count_set_bits(bitmap_full_words, 2, bitmap_full_capacity),
        first_set_bit(bitmap_full_words, 2, bitmap_full_capacity),
        has_cpu(bitmap_sparse_words, 16, 2) ? "true" : "false",
        has_cpu(bitmap_sparse_words, 16, 3) ? "true" : "false",
        count_set_bits(bitmap_sparse_words, 1, 16),
        first_set_bit(bitmap_sparse_words, 1, 16),
        first_clear_bit(bitmap_sparse_words, 1, 16),
        has_cpu(cpumask_presence_words, 8, 0) ? "true" : "false",
        has_cpu(cpumask_presence_words, 8, 1) ? "true" : "false",
        has_cpu(cpumask_presence_words, 8, 7) ? "true" : "false",
        count_set_bits(cpumask_presence_words, 1, 8),
        first_set_bit(cpumask_presence_words, 1, 8),
        first_clear_bit(cpumask_presence_words, 1, 8),
        is_subset_of(cpumask_base_words, cpumask_superset_words, 2, 8) ? "true" : "false",
        is_subset_of(cpumask_superset_words, cpumask_base_words, 2, 8) ? "true" : "false",
        intersects(cpumask_base_words, cpumask_superset_words, 2, 8) ? "true" : "false",
        intersects(cpumask_base_words, cpumask_disjoint_words, 2, 8) ? "true" : "false"
    );
    return 0;
}

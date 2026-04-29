// SPDX-License-Identifier: GPL-2.0-only
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef int (*cmp_func_t)(const void *key, const void *elt);

static void *inline_bsearch(const void *key, const void *base, size_t num, size_t size, cmp_func_t cmp)
{
    const unsigned char *base_ptr = (const unsigned char *)base;

    while (num > 0) {
        size_t pivot = num >> 1;
        const void *element = base_ptr + (pivot * size);
        int result = cmp(key, element);

        if (result == 0)
            return (void *)element;
        if (result > 0) {
            base_ptr = (const unsigned char *)element + size;
            num--;
        }
        num >>= 1;
    }

    return NULL;
}

struct symbol {
    const char *name;
    uintptr_t address;
};

static int compare_u32(const void *key, const void *elt)
{
    const uint32_t lhs = *(const uint32_t *)key;
    const uint32_t rhs = *(const uint32_t *)elt;

    if (lhs < rhs)
        return -1;
    if (lhs > rhs)
        return 1;
    return 0;
}

static int compare_descending_u32(const void *key, const void *elt)
{
    return compare_u32(elt, key);
}

static int compare_symbol_name(const void *key, const void *elt)
{
    const char *name = (const char *)key;
    const struct symbol *symbol = (const struct symbol *)elt;
    const int order = strcmp(name, symbol->name);

    if (order < 0)
        return -1;
    if (order > 0)
        return 1;
    return 0;
}

static void print_index_case(const char *label, uint32_t key, const uint32_t *base, const uint32_t *found)
{
    if (found != NULL)
        printf("%s\t%u\t%td\n", label, key, found - base);
    else
        printf("%s\t%u\tnull\n", label, key);
}

static void print_duplicate_case(const char *label, uint32_t key, const uint32_t *found)
{
    if (found != NULL)
        printf("%s\t%u\tfound\n", label, key);
    else
        printf("%s\t%u\tnull\n", label, key);
}

int main(void)
{
    static const uint32_t values[] = { 3, 8, 13, 21, 34, 55, 89 };
    static const uint32_t duplicate_at_beginning[] = { 7, 7, 7, 12, 18, 24 };
    static const uint32_t duplicate_in_middle[] = { 2, 7, 7, 7, 12, 18 };
    static const uint32_t duplicate_at_end[] = { 2, 7, 12, 18, 18, 18 };
    static const uint32_t singleton[] = { 21 };
    static const uint32_t descending_values[] = { 89, 55, 34, 21, 13, 8, 3 };
    static const struct symbol symbols[] = {
        { "do_exit", 0x1000u },
        { "kfree", 0x1200u },
        { "kmalloc", 0x1400u },
        { "schedule", 0x1800u },
    };
    uint32_t mutable_values[] = { 3, 8, 13, 21, 34, 55, 89 };

    {
        const uint32_t key = 3;
        print_index_case("u32-hit", key, values, inline_bsearch(&key, values, sizeof(values) / sizeof(values[0]), sizeof(values[0]), compare_u32));
    }
    {
        const uint32_t key = 21;
        print_index_case("u32-hit", key, values, inline_bsearch(&key, values, sizeof(values) / sizeof(values[0]), sizeof(values[0]), compare_u32));
    }
    {
        const uint32_t key = 89;
        print_index_case("u32-hit", key, values, inline_bsearch(&key, values, sizeof(values) / sizeof(values[0]), sizeof(values[0]), compare_u32));
    }
    {
        const uint32_t key = 0;
        print_index_case("u32-miss", key, values, inline_bsearch(&key, values, sizeof(values) / sizeof(values[0]), sizeof(values[0]), compare_u32));
    }
    {
        const uint32_t key = 15;
        print_index_case("u32-miss", key, values, inline_bsearch(&key, values, sizeof(values) / sizeof(values[0]), sizeof(values[0]), compare_u32));
    }
    {
        const uint32_t key = 90;
        print_index_case("u32-miss", key, values, inline_bsearch(&key, values, sizeof(values) / sizeof(values[0]), sizeof(values[0]), compare_u32));
    }
    {
        const uint32_t key = 21;
        print_index_case("singleton-hit", key, singleton, inline_bsearch(&key, singleton, 1, sizeof(singleton[0]), compare_u32));
    }
    {
        const uint32_t key = 20;
        print_index_case("singleton-miss", key, singleton, inline_bsearch(&key, singleton, 1, sizeof(singleton[0]), compare_u32));
    }
    {
        const uint32_t key = 21;
        print_index_case("empty-miss", key, values, inline_bsearch(&key, values, 0, sizeof(values[0]), compare_u32));
    }
    {
        const uint32_t key = 34;
        print_index_case("descending-hit", key, descending_values, inline_bsearch(&key, descending_values, sizeof(descending_values) / sizeof(descending_values[0]), sizeof(descending_values[0]), compare_descending_u32));
    }
    {
        const uint32_t key = 20;
        print_index_case("descending-miss", key, descending_values, inline_bsearch(&key, descending_values, sizeof(descending_values) / sizeof(descending_values[0]), sizeof(descending_values[0]), compare_descending_u32));
    }
    {
        const uint32_t key = 7;
        print_duplicate_case("duplicate-hit-begin", key, inline_bsearch(&key, duplicate_at_beginning, sizeof(duplicate_at_beginning) / sizeof(duplicate_at_beginning[0]), sizeof(duplicate_at_beginning[0]), compare_u32));
    }
    {
        const uint32_t key = 7;
        print_duplicate_case("duplicate-hit-middle", key, inline_bsearch(&key, duplicate_in_middle, sizeof(duplicate_in_middle) / sizeof(duplicate_in_middle[0]), sizeof(duplicate_in_middle[0]), compare_u32));
    }
    {
        const uint32_t key = 18;
        print_duplicate_case("duplicate-hit-end", key, inline_bsearch(&key, duplicate_at_end, sizeof(duplicate_at_end) / sizeof(duplicate_at_end[0]), sizeof(duplicate_at_end[0]), compare_u32));
    }
    {
        const char key[] = "kmalloc";
        const struct symbol *found = inline_bsearch(key, symbols, sizeof(symbols) / sizeof(symbols[0]), sizeof(symbols[0]), compare_symbol_name);
        if (found != NULL)
            printf("sym-hit\tkmalloc\t0x%tx\n", found->address);
        else
            printf("sym-hit\tkmalloc\tnull\n");
    }
    {
        const char key[] = "vfree";
        const struct symbol *found = inline_bsearch(key, symbols, sizeof(symbols) / sizeof(symbols[0]), sizeof(symbols[0]), compare_symbol_name);
        if (found != NULL)
            printf("sym-miss\tvfree\t0x%tx\n", found->address);
        else
            printf("sym-miss\tvfree\tnull\n");
    }
    {
        const uint32_t key = 21;
        uint32_t *found = inline_bsearch(&key, mutable_values, sizeof(mutable_values) / sizeof(mutable_values[0]), sizeof(mutable_values[0]), compare_u32);
        if (found != NULL) {
            *found = 22;
            printf("mutable-hit\t21\t%u\n", mutable_values[3]);
        } else {
            printf("mutable-hit\t21\tnull\n");
        }
    }

    return 0;
}

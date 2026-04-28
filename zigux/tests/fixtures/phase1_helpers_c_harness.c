#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <linux/bitmap.h>
#include <linux/ctype.h>
#include <linux/kernel.h>
#include <linux/list.h>
#include <linux/list_sort.h>
#include <linux/rbtree.h>
#include <linux/slab.h>
#include <linux/string.h>
#include <linux/zalloc.h>

struct rb_entry_fixture {
	int key;
	struct rb_node node;
};

static bool rb_less(struct rb_node *lhs, const struct rb_node *rhs)
{
	const struct rb_entry_fixture *left = rb_entry(lhs, struct rb_entry_fixture, node);
	const struct rb_entry_fixture *right = rb_entry(rhs, struct rb_entry_fixture, node);
	return left->key < right->key;
}

static void emit_int_array(const int *values, size_t count)
{
	putchar('[');
	for (size_t i = 0; i < count; i++) {
		if (i)
			putchar(',');
		printf("%d", values[i]);
	}
	putchar(']');
}

static void emit_word_array(const unsigned long *values, size_t count)
{
	putchar('[');
	for (size_t i = 0; i < count; i++) {
		if (i)
			putchar(',');
		printf("%lu", values[i]);
	}
	putchar(']');
}

static void emit_string_array(char **argv, int argc)
{
	putchar('[');
	for (int i = 0; i < argc; i++) {
		if (i)
			putchar(',');
		printf("\"%s\"", argv[i]);
	}
	putchar(']');
}

static void run_find_bit_section(void)
{
	unsigned long bitmap[3] = {0, 0, 0};
	unsigned long lhs[2] = {(1UL << 1) | (1UL << 9), 1UL << 2};
	unsigned long rhs[2] = {1UL << 9, 1UL << 2};
	unsigned long nbits = BITS_PER_LONG * 3;
	unsigned long tail_nbits = BITS_PER_LONG + 5;
	unsigned long tail_bitmap[2] = {0, 1UL << 9};
	unsigned long tail_zero_bitmap[2] = {~0UL, BITMAP_LAST_WORD_MASK(BITS_PER_LONG + 5)};
	unsigned long tail_and_mixed[2] = {0, (1UL << 3) | (1UL << 9)};

	bitmap[0] |= 1UL << 5;
	bitmap[1] |= 1UL << 3;
	bitmap[2] |= 1UL << 7;

	printf("\"find_bit\":{");
	printf("\"bits_per_long\":%d,", BITS_PER_LONG);
	printf("\"first\":%lu,", find_first_bit(bitmap, nbits));
	printf("\"next_after_6\":%lu,", find_next_bit(bitmap, nbits, 6));
	printf("\"next_after_word\":%lu,", find_next_bit(bitmap, nbits, BITS_PER_LONG + 4));
	printf("\"first_zero\":%lu,", find_first_zero_bit((unsigned long[]){0xf7UL}, 12));
	printf("\"next_zero\":%lu,", find_next_zero_bit((unsigned long[]){~0UL, ~(1UL << 4)}, BITS_PER_LONG * 2, BITS_PER_LONG));
	printf("\"first_and\":%lu,", find_first_and_bit(lhs, rhs, BITS_PER_LONG * 2));
	printf("\"next_and\":%lu,", find_next_and_bit(lhs, rhs, BITS_PER_LONG * 2, 10));
	printf("\"tail_clamped_first\":%lu,", find_first_bit(tail_bitmap, tail_nbits));
	printf("\"tail_clamped_next\":%lu,", find_next_bit(tail_bitmap, tail_nbits, BITS_PER_LONG));
	printf("\"tail_zero_clamped_first\":%lu,", find_first_zero_bit(tail_zero_bitmap, tail_nbits));
	printf("\"tail_zero_clamped_next\":%lu,", find_next_zero_bit(tail_zero_bitmap, tail_nbits, BITS_PER_LONG));
	printf("\"tail_and_clamped_first\":%lu,", find_first_and_bit(tail_bitmap, tail_bitmap, tail_nbits));
	printf("\"tail_and_clamped_next\":%lu,", find_next_and_bit(tail_bitmap, tail_bitmap, tail_nbits, BITS_PER_LONG));
	printf("\"tail_and_mixed_first\":%lu,", find_first_and_bit(tail_and_mixed, tail_and_mixed, tail_nbits));
	printf("\"tail_and_mixed_next\":%lu", find_next_and_bit(tail_and_mixed, tail_and_mixed, tail_nbits, BITS_PER_LONG + 4));
	printf("}");
}

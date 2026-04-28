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

static void run_bitmap_section(void)
{
	unsigned long map[2] = {0, 0};
	unsigned long lhs[2] = {0x0eUL, 0};
	unsigned long rhs[2] = {0x0aUL, 0};
	unsigned long dst[2] = {0, 0};
	unsigned long range_map[3] = {0, 0, 0};
	unsigned long partial_lhs[1] = {0x1fUL};
	unsigned long partial_rhs[1] = {0x11UL};
	unsigned long partial_dst[1] = {0};
	unsigned long copy_nbits = BITS_PER_LONG + 5;
	unsigned long copy_src[3] = {0, 0, 0};
	unsigned long copy_dst[3] = {~0UL, ~0UL, ~0UL};
	unsigned long empty_map[1] = {0};
	char buffer[64] = {0};
	char trunc_buffer[4] = {0};
	char empty_buffer[4] = {0xaa, 0xaa, 0xaa, 0xaa};
	bool and_result;
	bool andnot_result;
	bool equal_result;
	bool intersects_result;
	bool subset_result;

	bitmap_set(map, 1, 3);
	bitmap_set(map, 7, 1);
	bitmap_set(map, 10, 2);

	and_result = bitmap_and(dst, lhs, rhs, 8);
	unsigned long and_values[2] = {dst[0], dst[1]};
	andnot_result = bitmap_andnot(dst, lhs, rhs, 8);
	unsigned long andnot_values[2] = {dst[0], dst[1]};
	bitmap_or(dst, lhs, rhs, 8);
	unsigned long or_values[2] = {dst[0], dst[1]};
	bitmap_xor(dst, lhs, rhs, 8);
	unsigned long xor_values[2] = {dst[0], dst[1]};
	bitmap_set(copy_src, 0, copy_nbits);
	bitmap_copy(copy_dst, copy_src, copy_nbits);
	unsigned long copy_values[3] = {copy_dst[0], copy_dst[1], copy_dst[2]};
	bitmap_xor(partial_dst, partial_lhs, partial_rhs, 4);
	unsigned long partial_xor_masked_values[1] = {
		partial_dst[0] & BITMAP_LAST_WORD_MASK(4)
	};
	size_t empty_len = bitmap_scnprintf(empty_map, 8, empty_buffer, sizeof(empty_buffer));
	unsigned long empty_bytes[4] = {
		(unsigned char)empty_buffer[0],
		(unsigned char)empty_buffer[1],
		(unsigned char)empty_buffer[2],
		(unsigned char)empty_buffer[3],
	};
	bitmap_set(range_map, 1, 3);
	bitmap_set(range_map, BITS_PER_LONG + 2, 2);
	unsigned long range_after_set[3] = {range_map[0], range_map[1], range_map[2]};
	bitmap_clear(range_map, 1, 3);
	bitmap_clear(range_map, BITS_PER_LONG + 2, 2);
	unsigned long range_after_clear[3] = {range_map[0], range_map[1], range_map[2]};
	bitmap_fill(dst, BITS_PER_LONG * 2);
	bool full_result = bitmap_full(dst, BITS_PER_LONG * 2);
	bitmap_zero(dst, BITS_PER_LONG * 2);
	bool empty_result = bitmap_empty(dst, BITS_PER_LONG * 2);
	bitmap_scnprintf(map, 32, buffer, sizeof(buffer));
	size_t trunc_len = bitmap_scnprintf(map, 8, trunc_buffer, sizeof(trunc_buffer));
	bitmap_clear(map, 1, 3);
	bitmap_clear(map, 7, 1);
	bitmap_clear(map, 10, 2);
	equal_result = bitmap_equal(lhs, (unsigned long[]){0x0eUL, 0}, 8);
	intersects_result = bitmap_intersects(lhs, rhs, 8);
	subset_result = bitmap_subset(rhs, lhs, 8);

	printf("\"bitmap\":{");
	printf("\"weight\":%u,", bitmap_weight((unsigned long[]){0x0eUL, 0}, 8));
	printf("\"scnprintf\":\"%s\",", buffer);
	printf("\"and_result\":%s,", and_result ? "true" : "false");
	printf("\"and_values\":"); emit_word_array(and_values, 2); printf(",");
	printf("\"andnot_result\":%s,", andnot_result ? "true" : "false");
	printf("\"andnot_values\":"); emit_word_array(andnot_values, 2); printf(",");
	printf("\"or_values\":"); emit_word_array(or_values, 2); printf(",");
	printf("\"xor_values\":"); emit_word_array(xor_values, 2); printf(",");
	printf("\"copy_nbits\":%lu,", copy_nbits);
	printf("\"copy_values\":"); emit_word_array(copy_values, 3); printf(",");
	printf("\"partial_xor_nbits\":4,");
	printf("\"partial_xor_masked_values\":"); emit_word_array(partial_xor_masked_values, 1); printf(",");
	printf("\"scnprintf_empty_len\":%zu,", empty_len);
	printf("\"scnprintf_empty_bytes\":"); emit_word_array(empty_bytes, 4); printf(",");
	printf("\"equal\":%s,", equal_result ? "true" : "false");
	printf("\"intersects\":%s,", intersects_result ? "true" : "false");
	printf("\"subset\":%s,", subset_result ? "true" : "false");
	printf("\"range_after_set\":"); emit_word_array(range_after_set, 3); printf(",");
	printf("\"range_after_clear\":"); emit_word_array(range_after_clear, 3); printf(",");
	printf("\"full_after_fill\":%s,", full_result ? "true" : "false");
	printf("\"empty_after_zero\":%s,", empty_result ? "true" : "false");
	printf("\"scnprintf_trunc_len\":%zu,", trunc_len);
	printf("\"scnprintf_trunc\":\"%s\"", trunc_buffer);
	printf("}");
}
-®ιάjΧ
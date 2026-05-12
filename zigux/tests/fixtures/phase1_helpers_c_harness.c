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
	int serial;
	struct rb_node node;
};

static bool rb_less(struct rb_node *lhs, const struct rb_node *rhs)
{
	const struct rb_entry_fixture *left = rb_entry(lhs, struct rb_entry_fixture, node);
	const struct rb_entry_fixture *right = rb_entry(rhs, struct rb_entry_fixture, node);
	return left->key < right->key;
}

static int rb_cmp_key(const void *key, const struct rb_node *node)
{
	const int *wanted = key;
	const struct rb_entry_fixture *entry = rb_entry(node, struct rb_entry_fixture, node);

	if (*wanted < entry->key)
		return -1;
	if (*wanted > entry->key)
		return 1;
	return 0;
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
	unsigned long boundary = BITS_PER_LONG - 1;
	unsigned long boundary_nbits = BITS_PER_LONG * 2;
	unsigned long boundary_set_map[2] = {1UL << boundary, 0};
	unsigned long boundary_and_lhs[2] = {1UL << boundary, 0};
	unsigned long boundary_and_rhs[2] = {1UL << boundary, 0};
	unsigned long boundary_zero_map[2] = {~(1UL << boundary), ~0UL};
	unsigned long tail_nbits = BITS_PER_LONG + 5;
	unsigned long tail_bitmap[2] = {0, 1UL << 9};
	unsigned long tail_zero_bitmap[2] = {~0UL, BITMAP_LAST_WORD_MASK(BITS_PER_LONG + 5)};
	unsigned long tail_last_bitmap[2] = {0, (1UL << 3) | (1UL << 10)};
	unsigned long tail_empty_last_bitmap[2] = {0, 1UL << 10};
	unsigned long clump_bitmap[2] = {0, 0};
	unsigned long tail_clump_bitmap[2] = {0, 1UL << 3};
	unsigned long empty_clump_bitmap[1] = {0};
	unsigned long first_clump = 0;
	unsigned long next_clump = 0;
	unsigned long tail_clump = 0;
	unsigned long empty_first_clump = 0xaa;
	unsigned long empty_next_clump = 0xaa;

	bitmap[0] |= 1UL << 5;
	bitmap[1] |= 1UL << 3;
	bitmap[2] |= 1UL << 7;
	clump_bitmap[0] |= 1UL << 9;
	clump_bitmap[0] |= 1UL << 14;
	clump_bitmap[1] |= 1UL << 8;

	printf("\"find_bit\":{");
	printf("\"bits_per_long\":%d,", BITS_PER_LONG);
	printf("\"first\":%lu,", find_first_bit(bitmap, nbits));
	printf("\"next_after_6\":%lu,", find_next_bit(bitmap, nbits, 6));
	printf("\"next_after_word\":%lu,", find_next_bit(bitmap, nbits, BITS_PER_LONG + 4));
	printf("\"first_zero\":%lu,", find_first_zero_bit((unsigned long[]){0xf7UL}, 12));
	printf("\"next_zero\":%lu,", find_next_zero_bit((unsigned long[]){~0UL, ~(1UL << 4)}, BITS_PER_LONG * 2, BITS_PER_LONG));
	printf("\"first_and\":%lu,", find_first_and_bit(lhs, rhs, BITS_PER_LONG * 2));
	printf("\"next_and\":%lu,", find_next_and_bit(lhs, rhs, BITS_PER_LONG * 2, 10));
	printf("\"last\":%lu,", find_last_bit(bitmap, nbits));
	printf("\"inclusive_boundary_next\":%lu,", find_next_bit(boundary_set_map, boundary_nbits, boundary));
	printf("\"inclusive_boundary_zero\":%lu,", find_next_zero_bit(boundary_zero_map, boundary_nbits, boundary));
	printf("\"inclusive_boundary_and\":%lu,", find_next_and_bit(boundary_and_lhs, boundary_and_rhs, boundary_nbits, boundary));
	printf("\"past_nbits_next\":%lu,", find_next_bit((unsigned long[]){0}, 7, 11));
	printf("\"past_nbits_zero\":%lu,", find_next_zero_bit((unsigned long[]){0}, 7, 11));
	printf("\"past_nbits_and\":%lu,", find_next_and_bit((unsigned long[]){0}, (unsigned long[]){0}, 7, 11));
	printf("\"tail_clamped_first\":%lu,", find_first_bit(tail_bitmap, tail_nbits));
	printf("\"tail_clamped_next\":%lu,", find_next_bit(tail_bitmap, tail_nbits, BITS_PER_LONG));
	printf("\"tail_zero_clamped_first\":%lu,", find_first_zero_bit(tail_zero_bitmap, tail_nbits));
	printf("\"tail_zero_clamped_next\":%lu,", find_next_zero_bit(tail_zero_bitmap, tail_nbits, BITS_PER_LONG));
	printf("\"tail_and_clamped_first\":%lu,", find_first_and_bit(tail_bitmap, tail_bitmap, tail_nbits));
	printf("\"tail_and_clamped_next\":%lu,", find_next_and_bit(tail_bitmap, tail_bitmap, tail_nbits, BITS_PER_LONG));
	printf("\"tail_clamped_last\":%lu,", find_last_bit(tail_last_bitmap, tail_nbits));
	printf("\"tail_clamped_empty_last\":%lu,", find_last_bit(tail_empty_last_bitmap, tail_nbits));
	printf("\"first_clump_offset\":%lu,", find_first_clump8(&first_clump, clump_bitmap, BITS_PER_LONG * 2));
	printf("\"first_clump_value\":%lu,", first_clump);
	printf("\"next_clump_offset\":%lu,", find_next_clump8(&next_clump, clump_bitmap, BITS_PER_LONG * 2, 10));
	printf("\"next_clump_value\":%lu,", next_clump);
	printf("\"tail_clump_offset\":%lu,", find_first_clump8(&tail_clump, tail_clump_bitmap, tail_nbits));
	printf("\"tail_clump_value\":%lu,", tail_clump);
	printf("\"empty_clump_first_offset\":%lu,", find_first_clump8(&empty_first_clump, empty_clump_bitmap, 8));
	printf("\"empty_clump_first_value\":%lu,", empty_first_clump);
	printf("\"empty_clump_next_offset\":%lu,", find_next_clump8(&empty_next_clump, empty_clump_bitmap, 8, 4));
	printf("\"empty_clump_next_value\":%lu", empty_next_clump);
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
	unsigned long truncated_map[1] = {0};
	unsigned long single_bit_map[1] = {0};
	char buffer[64] = {0};
	char truncated_buffer[8] = {0};
	char terminator_only[1] = {0xaa};
	char zero_length[1] = {0};
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
	bitmap_xor(partial_dst, partial_lhs, partial_rhs, 4);
	unsigned long partial_xor_masked_values[1] = {
		partial_dst[0] & BITMAP_LAST_WORD_MASK(4)
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
	bitmap_set(truncated_map, 1, 3);
	bitmap_set(truncated_map, 7, 1);
	bitmap_set(truncated_map, 10, 3);
	size_t truncated_len = bitmap_scnprintf(truncated_map, 32, truncated_buffer, sizeof(truncated_buffer));
	bitmap_set(single_bit_map, 9, 1);
	size_t terminator_only_len = bitmap_scnprintf(single_bit_map, 32, terminator_only, sizeof(terminator_only));
	size_t zero_length_len = bitmap_scnprintf(single_bit_map, 32, zero_length, 0);
	unsigned long alloc_nbits = BITS_PER_LONG + 5;
	unsigned long *allocated = bitmap_alloc(alloc_nbits);
	unsigned long *zero_allocated = bitmap_zalloc(alloc_nbits);
	unsigned long alloc_words = allocated ? BITS_TO_LONGS(alloc_nbits) : 0;
	unsigned long zalloc_words = zero_allocated ? BITS_TO_LONGS(alloc_nbits) : 0;
	unsigned long zalloc_values[2] = {0, 0};

	if (zero_allocated) {
		for (size_t i = 0; i < zalloc_words && i < 2; i++)
			zalloc_values[i] = zero_allocated[i];
	}
	bitmap_free(allocated);
	bitmap_free(zero_allocated);
	bitmap_clear(map, 1, 3);
	bitmap_clear(map, 7, 1);
	bitmap_clear(map, 10, 2);
	equal_result = bitmap_equal(lhs, (unsigned long[]){0x0eUL, 0}, 8);
	intersects_result = bitmap_intersects(lhs, rhs, 8);
	subset_result = bitmap_subset(rhs, lhs, 8);

	printf("\"bitmap\":{");
	printf("\"weight\":%u,", bitmap_weight((unsigned long[]){0x0eUL, 0}, 8));
	printf("\"scnprintf\":\"%s\",", buffer);
	printf("\"truncated_scnprintf_len\":%zu,", truncated_len);
	printf("\"truncated_scnprintf\":\"%s\",", truncated_buffer);
	printf("\"terminator_only_scnprintf_len\":%zu,", terminator_only_len);
	printf("\"terminator_only_nul\":%u,", (unsigned int)(unsigned char)terminator_only[0]);
	printf("\"zero_length_scnprintf_len\":%zu,", zero_length_len);
	printf("\"alloc_words\":%lu,", alloc_words);
	printf("\"zalloc_words\":%lu,", zalloc_words);
	printf("\"zalloc_values\":"); emit_word_array(zalloc_values, zalloc_words); printf(",");
	printf("\"and_result\":%s,", and_result ? "true" : "false");
	printf("\"and_values\":"); emit_word_array(and_values, 2); printf(",");
	printf("\"andnot_result\":%s,", andnot_result ? "true" : "false");
	printf("\"andnot_values\":"); emit_word_array(andnot_values, 2); printf(",");
	printf("\"or_values\":"); emit_word_array(or_values, 2); printf(",");
	printf("\"xor_values\":"); emit_word_array(xor_values, 2); printf(",");
	printf("\"partial_xor_nbits\":4,");
	printf("\"partial_xor_masked_values\":"); emit_word_array(partial_xor_masked_values, 1); printf(",");
	printf("\"equal\":%s,", equal_result ? "true" : "false");
	printf("\"intersects\":%s,", intersects_result ? "true" : "false");
	printf("\"subset\":%s,", subset_result ? "true" : "false");
	printf("\"range_after_set\":"); emit_word_array(range_after_set, 3); printf(",");
	printf("\"range_after_clear\":"); emit_word_array(range_after_clear, 3); printf(",");
	printf("\"full_after_fill\":%s,", full_result ? "true" : "false");
	printf("\"empty_after_zero\":%s", empty_result ? "true" : "false");
	printf("}");
}

static void run_string_section(void)
{
	bool value = false;
	char dst[4] = {0};
	char trim_buf[] = " \thi \n";
	char remove_buf[] = "a b c";
	char replace_buf[] = "a-b";
	char replace_cstr_buf[] = { 'a', '-', 0, '-', 'z' };
	char *replace_end;
	char *replace_cstr_end;
	char *skip = skip_spaces("   hello");
	char *trimmed = strim(trim_buf);
	remove_spaces(remove_buf);
	replace_end = strreplace(replace_buf, '-', '_');
	replace_cstr_end = strreplace(replace_cstr_buf, '-', '_');
	void *memchr_hit = memchr_inv("aaaaXaaa", 'a', 8);
	void *memchr_none = memchr_inv("bbbb", 'b', 4);
 
	printf("\"string\":{");
	strtobool("y", &value);
	printf("\"strtobool_y\":%s,", value ? "true" : "false");
	strtobool("On", &value);
	printf("\"strtobool_on\":%s,", value ? "true" : "false");
	strtobool("0", &value);
	printf("\"strtobool_zero\":%s,", value ? "true" : "false");
	strtobool("of", &value);
	printf("\"strtobool_off\":%s,", value ? "true" : "false");
	printf("\"strtobool_invalid\":%d,", strtobool("maybe", &value));
	printf("\"strlcpy_len\":%zu,", strlcpy(dst, "hello", sizeof(dst)));
	printf("\"strlcpy_buffer\":\"%s\",", dst);
	printf("\"skip_spaces\":\"%s\",", skip);
	printf("\"trim_spaces\":\"%s\",", trimmed);
	printf("\"remove_spaces\":\"%s\",", remove_buf);
	printf("\"replace_char\":\"%s\",", replace_buf);
	printf("\"replace_char_end\":%td,", (ptrdiff_t)(replace_end - replace_buf));
	printf("\"replace_char_cstr_end\":%td,", (ptrdiff_t)(replace_cstr_end - replace_cstr_buf));
	printf("\"replace_char_cstr_bytes\":[%u,%u,%u,%u,%u],",
		(unsigned int)(unsigned char)replace_cstr_buf[0],
		(unsigned int)(unsigned char)replace_cstr_buf[1],
		(unsigned int)(unsigned char)replace_cstr_buf[2],
		(unsigned int)(unsigned char)replace_cstr_buf[3],
		(unsigned int)(unsigned char)replace_cstr_buf[4]);
	printf("\"memchr_inv_index\":%td,", (ptrdiff_t)((const char *)memchr_hit - "aaaaXaaa"));
	printf("\"memchr_inv_none\":%s", memchr_none ? "false" : "true");
	printf("}");
}

static void run_rbtree_section(void)
{
	struct rb_entry_fixture entries[] = {
		{ .key = 10 },
		{ .key = 20 },
		{ .key = 5 },
		{ .key = 15 },
		{ .key = 25 },
	};
	struct rb_entry_fixture replacement = { .key = 10 };
	struct rb_entry_fixture postorder_entries[] = {
		{ .key = 2 },
		{ .key = 1 },
		{ .key = 3 },
	};
	struct rb_entry_fixture search_entries[] = {
		{ .key = 10, .serial = 0 },
		{ .key = 5, .serial = 1 },
		{ .key = 10, .serial = 2 },
		{ .key = 20, .serial = 3 },
		{ .key = 10, .serial = 4 },
		{ .key = 15, .serial = 5 },
	};
	struct rb_root root = RB_ROOT;
	struct rb_root postorder_root = RB_ROOT;
	struct rb_root search_root = RB_ROOT;
	int order[5] = {0};
	int reverse[5] = {0};
	int replaced[4] = {0};
	int erase_init_order[3] = {0};
	int next_match_serials[3] = {0};
	size_t count = 0;
	struct rb_node *node;
	struct rb_node *last_match = NULL;
	bool empty_root = RB_EMPTY_ROOT(&root);
	int find_wanted = 15;
	int missing_wanted = 17;
	int duplicate_wanted = 10;
	struct rb_node *found;
	struct rb_node *first_match;

	for (size_t i = 0; i < sizeof(entries) / sizeof(entries[0]); i++)
		rb_add(&entries[i].node, &root, rb_less);

	for (node = rb_first(&root); node; node = rb_next(node))
		order[count++] = rb_entry(node, struct rb_entry_fixture, node)->key;

	count = 0;
	for (node = rb_last(&root); node; node = rb_prev(node))
		reverse[count++] = rb_entry(node, struct rb_entry_fixture, node)->key;

	rb_erase(&entries[1].node, &root);
	rb_replace_node(&entries[0].node, &replacement.node, &root);

	count = 0;
	for (node = rb_first(&root); node; node = rb_next(node))
		replaced[count++] = rb_entry(node, struct rb_entry_fixture, node)->key;

	rb_erase_init(&replacement.node, &root);

	count = 0;
	for (node = rb_first(&root); node; node = rb_next(node))
		erase_init_order[count++] = rb_entry(node, struct rb_entry_fixture, node)->key;

	for (size_t i = 0; i < sizeof(postorder_entries) / sizeof(postorder_entries[0]); i++)
		rb_add(&postorder_entries[i].node, &postorder_root, rb_less);
	for (size_t i = 0; i < sizeof(search_entries) / sizeof(search_entries[0]); i++)
		rb_add(&search_entries[i].node, &search_root, rb_less);

	int postorder_count = 0;
	for (node = rb_first_postorder(&postorder_root); node; node = rb_next_postorder(node))
		postorder_count++;

	found = rb_find(&find_wanted, &search_root, rb_cmp_key);
	first_match = rb_find_first(&duplicate_wanted, &search_root, rb_cmp_key);

	count = 0;
	for (node = first_match; node; node = rb_next_match(&duplicate_wanted, node, rb_cmp_key)) {
		last_match = node;
		next_match_serials[count++] = rb_entry(node, struct rb_entry_fixture, node)->serial;
	}

	RB_CLEAR_NODE(&replacement.node);

	printf("\"rbtree\":{");
	printf("\"empty_root\":%s,", empty_root ? "true" : "false");
	printf("\"insert_order\":"); emit_int_array(order, 5); printf(",");
	printf("\"reverse_order\":"); emit_int_array(reverse, 5); printf(",");
	printf("\"replace_order\":"); emit_int_array(replaced, 4); printf(",");
	printf("\"erase_init_order\":"); emit_int_array(erase_init_order, 3); printf(",");
	printf("\"postorder_count\":%d,", postorder_count);
	printf("\"erase_init_node_empty\":%s,", RB_EMPTY_NODE(&replacement.node) ? "true" : "false");
	printf("\"cleared_node_empty\":%s,", RB_EMPTY_NODE(&replacement.node) ? "true" : "false");
	printf("\"find_found_key\":%d,", rb_entry(found, struct rb_entry_fixture, node)->key);
	printf("\"find_missing\":%s,", rb_find(&missing_wanted, &search_root, rb_cmp_key) ? "false" : "true");
	printf("\"find_first_serial\":%d,", rb_entry(first_match, struct rb_entry_fixture, node)->serial);
	printf("\"next_match_serials\":"); emit_int_array(next_match_serials, count); printf(",");
	printf("\"next_match_terminal_null\":%s", rb_next_match(&duplicate_wanted, last_match, rb_cmp_key) ? "false" : "true");
	printf("}");
}

static void run_argv_split_section(void)
{
	int argc = 0;
	char **argv = argv_split(" alpha  beta\tgamma\n", &argc);
	int blank_argc = -1;
	char **blank_argv = argv_split("   \t\n", &blank_argc);

	printf("\"argv_split\":{");
	printf("\"argc\":%d,", argc);
	printf("\"argv\":"); emit_string_array(argv, argc); printf(",");
	printf("\"blank_argc\":%d", blank_argc);
	printf("}");

	argv_free(argv);
	argv_free(blank_argv);
}

static void run_cmdline_section(void)
{
	char *endptr = NULL;
	unsigned long long decimal = memparse("64K rest", &endptr);
	char *decimal_rest = endptr;
	unsigned long long hexadecimal = memparse("0x20M", &endptr);
	char *hex_rest = endptr;
	unsigned long long octal = memparse("010K", &endptr);
	char *octal_rest = endptr;
	unsigned long long invalid = memparse("xyz", &endptr);
	char *invalid_rest = endptr;

	printf("\"cmdline\":{");
	printf("\"decimal_k\":{\"value\":%llu,\"rest\":\"%s\"},", decimal, decimal_rest);
	printf("\"hex_m\":{\"value\":%llu,\"rest\":\"%s\"},", hexadecimal, hex_rest);
	printf("\"octal_k\":{\"value\":%llu,\"rest\":\"%s\"},", octal, octal_rest);
	printf("\"invalid\":{\"value\":%llu,\"rest\":\"%s\"}", invalid, invalid_rest);
	printf("}");
}

static void run_ctype_section(void)
{
	printf("\"ctype\":{");
	printf("\"mask_A\":%u,", __ismask('A'));
	printf("\"mask_a\":%u,", __ismask('a'));
	printf("\"mask_space\":%u,", __ismask(' '));
	printf("\"isalnum_A\":%s,", isalnum('A') ? "true" : "false");
	printf("\"isalpha_z\":%s,", isalpha('z') ? "true" : "false");
	printf("\"isdigit_7\":%s,", isdigit('7') ? "true" : "false");
	printf("\"isspace_tab\":%s,", isspace('\t') ? "true" : "false");
	printf("\"isxdigit_f\":%s,", isxdigit('f') ? "true" : "false");
	printf("\"ispunct_bang\":%s,", ispunct('!') ? "true" : "false");
	printf("\"tolower_A\":%u,", tolower('A'));
	printf("\"toupper_z\":%u,", toupper('z'));
	printf("\"isodigit_7\":%s,", isodigit('7') ? "true" : "false");
	printf("\"isodigit_8\":%s", isodigit('8') ? "true" : "false");
	printf("}");
}

static void run_hweight_section(void)
{
	printf("\"hweight\":{");
	printf("\"w8\":%u,", __sw_hweight8(0xf0));
	printf("\"w16\":%u,", __sw_hweight16(0xf0f0));
	printf("\"w32\":%u,", __sw_hweight32(0xf0f0f0f0u));
	printf("\"w64\":%lu,", __sw_hweight64(0xf0f0f0f0f0f0f0f0ULL));
	printf("\"wlong\":%lu", hweight_long(0xf0f0UL));
	printf("}");
}

struct list_entry_fixture {
	int key;
	int ordinal;
	struct list_head node;
};

static int list_cmp_tristate(void *priv, const struct list_head *a,
			     const struct list_head *b)
{
	const struct list_entry_fixture *lhs = list_entry(a, struct list_entry_fixture, node);
	const struct list_entry_fixture *rhs = list_entry(b, struct list_entry_fixture, node);
	(void)priv;

	if (lhs->key < rhs->key)
		return -1;
	if (lhs->key > rhs->key)
		return 1;
	return 0;
}

static int list_cmp_bool(void *priv, const struct list_head *a,
			 const struct list_head *b)
{
	const struct list_entry_fixture *lhs = list_entry(a, struct list_entry_fixture, node);
	const struct list_entry_fixture *rhs = list_entry(b, struct list_entry_fixture, node);
	(void)priv;

	return lhs->key > rhs->key;
}

static void emit_list_sort_result(struct list_head *head, const char *keys_name,
				  const char *ordinals_name)
{
	struct list_head *pos;
	int keys[5] = {0};
	int ordinals[5] = {0};
	size_t idx = 0;

	list_for_each(pos, head) {
		const struct list_entry_fixture *entry = list_entry(pos, struct list_entry_fixture, node);
		keys[idx] = entry->key;
		ordinals[idx] = entry->ordinal;
		idx++;
	}

	printf("\"%s\":", keys_name);
	emit_int_array(keys, idx);
	printf(",");
	printf("\"%s\":", ordinals_name);
	emit_int_array(ordinals, idx);
}

static void run_list_sort_section(void)
{
	struct list_entry_fixture tri_entries[] = {
		{ .key = 2, .ordinal = 0 },
		{ .key = 1, .ordinal = 1 },
		{ .key = 3, .ordinal = 2 },
		{ .key = 1, .ordinal = 3 },
		{ .key = 3, .ordinal = 4 },
	};
	struct list_entry_fixture bool_entries[] = {
		{ .key = 2, .ordinal = 0 },
		{ .key = 1, .ordinal = 1 },
		{ .key = 3, .ordinal = 2 },
		{ .key = 1, .ordinal = 3 },
		{ .key = 3, .ordinal = 4 },
	};
	struct list_head tri_head;
	struct list_head bool_head;
	size_t i;

	INIT_LIST_HEAD(&tri_head);
	INIT_LIST_HEAD(&bool_head);

	for (i = 0; i < sizeof(tri_entries) / sizeof(tri_entries[0]); i++) {
		INIT_LIST_HEAD(&tri_entries[i].node);
		list_add_tail(&tri_entries[i].node, &tri_head);
		INIT_LIST_HEAD(&bool_entries[i].node);
		list_add_tail(&bool_entries[i].node, &bool_head);
	}

	list_sort(NULL, &tri_head, list_cmp_tristate);
	list_sort(NULL, &bool_head, list_cmp_bool);

	printf("\"list_sort\":{");
	emit_list_sort_result(&tri_head, "tri_sorted_keys", "tri_sorted_ordinals");
	printf(",");
	emit_list_sort_result(&bool_head, "bool_sorted_keys", "bool_sorted_ordinals");
	printf("}");
}

static void run_zalloc_section(void)
{
	void *ptr = zalloc(8);
	bool zeroed = true;
	for (size_t i = 0; i < 8; i++) {
		if (((unsigned char *)ptr)[i] != 0) {
			zeroed = false;
			break;
		}
	}
	zfree(&ptr);

	struct {
		uint32_t a;
		bool b;
	} *value = zalloc(sizeof(*value));
	bool value_zeroed = value->a == 0 && !value->b;
	zfree(&value);

	printf("\"zalloc\":{");
	printf("\"zeroed\":%s,", zeroed ? "true" : "false");
	printf("\"freed_is_null\":%s,", ptr == NULL ? "true" : "false");
	printf("\"value_zeroed\":%s,", value_zeroed ? "true" : "false");
	printf("\"value_freed_is_null\":%s", value == NULL ? "true" : "false");
	printf("}");
}

static void run_str_error_r_section(void)
{
	char buffer[64];
	char unknown[64];

	str_error_r(2, buffer, sizeof(buffer));
	str_error_r(4096, unknown, sizeof(unknown));

	printf("\"str_error_r\":{");
	printf("\"enoent\":\"%s\",", buffer);
	printf("\"unknown\":\"%s\"", unknown);
	printf("}");
}

static void run_slab_section(void)
{
	void *plain;
	void *array;
	bool array_zeroed = true;
	bool null_without_reclaim;

	kmalloc_nr_allocated = 0;
	null_without_reclaim = kmalloc(8, 0) == NULL;
	plain = kmalloc(8, GFP_KERNEL | __GFP_ZERO);
	bool zero_after_kmalloc = true;
	for (size_t i = 0; i < 8; i++) {
		if (((unsigned char *)plain)[i] != 0) {
			zero_after_kmalloc = false;
			break;
		}
	}
	int alloc_count_after_kmalloc = kmalloc_nr_allocated;
	kfree(plain);
	int alloc_count_after_kmalloc_free = kmalloc_nr_allocated;

	array = kmalloc_array(4, 2, GFP_KERNEL);
	for (size_t i = 0; i < 8; i++) {
		if (((unsigned char *)array)[i] != 0) {
			array_zeroed = false;
			break;
		}
	}
	int alloc_count_after_kmalloc_array = kmalloc_nr_allocated;
	kfree(array);
	int alloc_count_after_kmalloc_array_free = kmalloc_nr_allocated;

	printf("\"slab\":{");
	printf("\"null_without_reclaim\":%s,", null_without_reclaim ? "true" : "false");
	printf("\"alloc_count_after_kmalloc\":%d,", alloc_count_after_kmalloc);
	printf("\"zero_after_kmalloc\":%s,", zero_after_kmalloc ? "true" : "false");
	printf("\"alloc_count_after_kmalloc_free\":%d,", alloc_count_after_kmalloc_free);
	printf("\"array_zeroed\":%s,", array_zeroed ? "true" : "false");
	printf("\"alloc_count_after_kmalloc_array\":%d,", alloc_count_after_kmalloc_array);
	printf("\"alloc_count_after_kmalloc_array_free\":%d,", alloc_count_after_kmalloc_array_free);
	printf("\"slab_is_available\":%s", slab_is_available() ? "true" : "false");
	printf("}");
}

static void run_vsprintf_section(void)
{
	char fmt[16] = {0};
	char pad[9] = {0};
	int fmt_len = scnprintf(fmt, sizeof(fmt), "%s:%d", "zigux", 7);
	int pad_len = scnprintf_pad(pad, sizeof(pad) - 1, "id=%d", 7);

	printf("\"vsprintf\":{");
	printf("\"scnprintf_text\":\"%s\",", fmt);
	printf("\"scnprintf_len\":%d,", fmt_len);
	printf("\"pad_text\":\"%s\",", pad);
	printf("\"pad_len\":%d", pad_len);
	printf("}");
}

int main(void)
{
	printf("{");
	run_find_bit_section();
	printf(",");
	run_bitmap_section();
	printf(",");
	run_string_section();
	printf(",");
	run_rbtree_section();
	printf(",");
	run_argv_split_section();
	printf(",");
	run_cmdline_section();
	printf(",");
	run_ctype_section();
	printf(",");
	run_hweight_section();
	printf(",");
	run_list_sort_section();
	printf(",");
	run_zalloc_section();
	printf(",");
	run_str_error_r_section();
	printf(",");
	run_slab_section();
	printf(",");
	run_vsprintf_section();
	printf("}\n");
	return 0;
}

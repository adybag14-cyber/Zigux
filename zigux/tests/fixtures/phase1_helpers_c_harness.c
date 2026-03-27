#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <linux/bitmap.h>
#include <linux/ctype.h>
#include <linux/kernel.h>
#include <linux/rbtree.h>
#include <linux/string.h>

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
	printf("\"next_and\":%lu", find_next_and_bit(lhs, rhs, BITS_PER_LONG * 2, 10));
	printf("}");
}

static void run_bitmap_section(void)
{
	unsigned long map[2] = {0, 0};
	unsigned long lhs[2] = {0x0eUL, 0};
	unsigned long rhs[2] = {0x0aUL, 0};
	unsigned long dst[2] = {0, 0};
	char buffer[64] = {0};
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
	bitmap_fill(dst, BITS_PER_LONG * 2);
	bool full_result = bitmap_full(dst, BITS_PER_LONG * 2);
	bitmap_zero(dst, BITS_PER_LONG * 2);
	bool empty_result = bitmap_empty(dst, BITS_PER_LONG * 2);
	bitmap_scnprintf(map, 32, buffer, sizeof(buffer));
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
	printf("\"equal\":%s,", equal_result ? "true" : "false");
	printf("\"intersects\":%s,", intersects_result ? "true" : "false");
	printf("\"subset\":%s,", subset_result ? "true" : "false");
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
	char *skip = skip_spaces("   hello");
	char *trimmed = strim(trim_buf);
	remove_spaces(remove_buf);
	strreplace(replace_buf, '-', '_');
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
	struct rb_root root = RB_ROOT;
	struct rb_root postorder_root = RB_ROOT;
	int order[5] = {0};
	int replaced[4] = {0};
	size_t count = 0;
	struct rb_node *node;

	for (size_t i = 0; i < sizeof(entries) / sizeof(entries[0]); i++)
		rb_add(&entries[i].node, &root, rb_less);

	for (node = rb_first(&root); node; node = rb_next(node))
		order[count++] = rb_entry(node, struct rb_entry_fixture, node)->key;

	rb_erase(&entries[1].node, &root);
	rb_replace_node(&entries[0].node, &replacement.node, &root);

	count = 0;
	for (node = rb_first(&root); node; node = rb_next(node))
		replaced[count++] = rb_entry(node, struct rb_entry_fixture, node)->key;

	for (size_t i = 0; i < sizeof(postorder_entries) / sizeof(postorder_entries[0]); i++)
		rb_add(&postorder_entries[i].node, &postorder_root, rb_less);

	int postorder_count = 0;
	for (node = rb_first_postorder(&postorder_root); node; node = rb_next_postorder(node))
		postorder_count++;

	RB_CLEAR_NODE(&replacement.node);

	printf("\"rbtree\":{");
	printf("\"insert_order\":"); emit_int_array(order, 5); printf(",");
	printf("\"replace_order\":"); emit_int_array(replaced, 4); printf(",");
	printf("\"postorder_count\":%d,", postorder_count);
	printf("\"cleared_node_empty\":%s", RB_EMPTY_NODE(&replacement.node) ? "true" : "false");
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
	printf("}\n");
	return 0;
}

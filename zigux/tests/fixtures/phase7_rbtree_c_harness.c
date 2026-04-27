#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

#include <linux/rbtree.h>

struct rb_order_entry {
	int key;
	struct rb_node node;
};

struct rb_duplicate_entry {
	int key;
	int serial;
	struct rb_node node;
};

static bool rb_order_less(struct rb_node *lhs, const struct rb_node *rhs)
{
	const struct rb_order_entry *left = rb_entry(lhs, struct rb_order_entry, node);
	const struct rb_order_entry *right = rb_entry(rhs, struct rb_order_entry, node);
	return left->key < right->key;
}

static bool rb_duplicate_less(struct rb_node *lhs, const struct rb_node *rhs)
{
	const struct rb_duplicate_entry *left = rb_entry(lhs, struct rb_duplicate_entry, node);
	const struct rb_duplicate_entry *right = rb_entry(rhs, struct rb_duplicate_entry, node);
	if (left->key != right->key)
		return left->key < right->key;
	return left->serial < right->serial;
}

static int rb_duplicate_cmp(const void *key_ptr, const struct rb_node *node)
{
	const int key = *(const int *)key_ptr;
	const struct rb_duplicate_entry *entry = rb_entry(node, struct rb_duplicate_entry, node);
	if (key < entry->key)
		return -1;
	if (key > entry->key)
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

static void run_ordered_section(void)
{
	struct rb_order_entry entries[] = {
		{ .key = 10 },
		{ .key = 20 },
		{ .key = 5 },
		{ .key = 15 },
		{ .key = 25 },
	};
	struct rb_order_entry replace_entries[] = {
		{ .key = 10 },
		{ .key = 20 },
		{ .key = 5 },
		{ .key = 15 },
		{ .key = 25 },
	};
	struct rb_order_entry replacement = { .key = 10 };
	struct rb_root root = RB_ROOT;
	struct rb_root replace_root = RB_ROOT;
	int insert_order[5] = {0};
	int reverse_order[5] = {0};
	int erase_order[4] = {0};
	int replace_order[4] = {0};
	size_t count = 0;
	struct rb_node *node;

	for (size_t i = 0; i < sizeof(entries) / sizeof(entries[0]); i++)
		rb_add(&entries[i].node, &root, rb_order_less);

	for (node = rb_first(&root); node; node = rb_next(node))
		insert_order[count++] = rb_entry(node, struct rb_order_entry, node)->key;

	count = 0;
	for (node = rb_last(&root); node; node = rb_prev(node))
		reverse_order[count++] = rb_entry(node, struct rb_order_entry, node)->key;

	rb_erase(&entries[0].node, &root);

	count = 0;
	for (node = rb_first(&root); node; node = rb_next(node))
		erase_order[count++] = rb_entry(node, struct rb_order_entry, node)->key;

	for (size_t i = 0; i < sizeof(replace_entries) / sizeof(replace_entries[0]); i++)
		rb_add(&replace_entries[i].node, &replace_root, rb_order_less);

	rb_erase(&replace_entries[1].node, &replace_root);
	rb_replace_node(&replace_entries[0].node, &replacement.node, &replace_root);

	count = 0;
	for (node = rb_first(&replace_root); node; node = rb_next(node))
		replace_order[count++] = rb_entry(node, struct rb_order_entry, node)->key;

	printf("\"ordered\":{");
	printf("\"insert_order\":");
	emit_int_array(insert_order, 5);
	printf(",");
	printf("\"reverse_order\":");
	emit_int_array(reverse_order, 5);
	printf(",");
	printf("\"erase_order\":");
	emit_int_array(erase_order, 4);
	printf(",");
	printf("\"replace_order\":");
	emit_int_array(replace_order, 4);
	printf("}");
}

static void run_duplicate_section(void)
{
	struct rb_duplicate_entry entries[] = {
		{ .key = 10, .serial = 0 },
		{ .key = 20, .serial = 0 },
		{ .key = 10, .serial = 1 },
		{ .key = 5, .serial = 0 },
		{ .key = 10, .serial = 2 },
		{ .key = 15, .serial = 0 },
	};
	struct rb_root root = RB_ROOT;
	int key = 10;
	int match_serials[3] = {0};
	size_t count = 0;
	struct rb_node *node;

	for (size_t i = 0; i < sizeof(entries) / sizeof(entries[0]); i++)
		rb_add(&entries[i].node, &root, rb_duplicate_less);

	for (node = rb_find_first(&key, &root, rb_duplicate_cmp); node; node = rb_next_match(&key, node, rb_duplicate_cmp))
		match_serials[count++] = rb_entry(node, struct rb_duplicate_entry, node)->serial;

	printf("\"duplicates\":{");
	printf("\"key\":%d,", key);
	printf("\"match_serials\":");
	emit_int_array(match_serials, count);
	printf("}");
}

static void run_postorder_section(void)
{
	struct rb_order_entry entries[] = {
		{ .key = 2 },
		{ .key = 1 },
		{ .key = 3 },
	};
	struct rb_root root = RB_ROOT;
	int traversal[3] = {0};
	size_t count = 0;
	struct rb_node *node;

	for (size_t i = 0; i < sizeof(entries) / sizeof(entries[0]); i++)
		rb_add(&entries[i].node, &root, rb_order_less);

	for (node = rb_first_postorder(&root); node; node = rb_next_postorder(node))
		traversal[count++] = rb_entry(node, struct rb_order_entry, node)->key;

	printf("\"postorder\":{");
	printf("\"traversal\":");
	emit_int_array(traversal, count);
	printf("}");
}

int main(void)
{
	printf("{");
	run_ordered_section();
	printf(",");
	run_duplicate_section();
	printf(",");
	run_postorder_section();
	printf("}\n");
	return 0;
}

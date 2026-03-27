#include <stdint.h>
#include <stdio.h>

#include <linux/zigux.h>

int main(void)
{
	struct zigux_list_head_ref empty_list_head;
	struct zigux_list_head_ref single_list_head;
	struct zigux_list_head_ref single_list_node;
	struct zigux_list_head_ref triple_list_head;
	struct zigux_list_head_ref triple_list_a;
	struct zigux_list_head_ref triple_list_b;
	struct zigux_list_head_ref triple_list_c;
	struct zigux_list_view empty_list;
	struct zigux_list_view single_list;
	struct zigux_list_view triple_list;
	struct zigux_list_view truncated_list;
	struct zigux_hlist_head_ref empty_hlist_head = { .first_addr = 0 };
	struct zigux_hlist_head_ref single_hlist_head;
	struct zigux_hlist_node_ref single_hlist_node;
	struct zigux_hlist_head_ref triple_hlist_head;
	struct zigux_hlist_node_ref triple_hlist_a;
	struct zigux_hlist_node_ref triple_hlist_b;
	struct zigux_hlist_node_ref triple_hlist_c;
	struct zigux_hlist_view empty_hlist;
	struct zigux_hlist_view single_hlist;
	struct zigux_hlist_view triple_hlist;
	struct zigux_hlist_view truncated_hlist;

	empty_list_head.next_addr = (unsigned long)(uintptr_t)&empty_list_head;
	empty_list_head.prev_addr = (unsigned long)(uintptr_t)&empty_list_head;

	single_list_head.next_addr = (unsigned long)(uintptr_t)&single_list_node;
	single_list_head.prev_addr = (unsigned long)(uintptr_t)&single_list_node;
	single_list_node.next_addr = (unsigned long)(uintptr_t)&single_list_head;
	single_list_node.prev_addr = (unsigned long)(uintptr_t)&single_list_head;

	triple_list_head.next_addr = (unsigned long)(uintptr_t)&triple_list_a;
	triple_list_head.prev_addr = (unsigned long)(uintptr_t)&triple_list_c;
	triple_list_a.next_addr = (unsigned long)(uintptr_t)&triple_list_b;
	triple_list_a.prev_addr = (unsigned long)(uintptr_t)&triple_list_head;
	triple_list_b.next_addr = (unsigned long)(uintptr_t)&triple_list_c;
	triple_list_b.prev_addr = (unsigned long)(uintptr_t)&triple_list_a;
	triple_list_c.next_addr = (unsigned long)(uintptr_t)&triple_list_head;
	triple_list_c.prev_addr = (unsigned long)(uintptr_t)&triple_list_b;

	empty_list = zigux_list_view_from_head(&empty_list_head, 8);
	single_list = zigux_list_view_from_head(&single_list_head, 8);
	triple_list = zigux_list_view_from_head(&triple_list_head, 8);
	truncated_list = zigux_list_view_from_head(&triple_list_head, 2);

	single_hlist_head.first_addr = (unsigned long)(uintptr_t)&single_hlist_node;
	single_hlist_node.next_addr = 0;
	single_hlist_node.pprev_addr = (unsigned long)(uintptr_t)&single_hlist_head.first_addr;

	triple_hlist_head.first_addr = (unsigned long)(uintptr_t)&triple_hlist_a;
	triple_hlist_a.next_addr = (unsigned long)(uintptr_t)&triple_hlist_b;
	triple_hlist_a.pprev_addr = (unsigned long)(uintptr_t)&triple_hlist_head.first_addr;
	triple_hlist_b.next_addr = (unsigned long)(uintptr_t)&triple_hlist_c;
	triple_hlist_b.pprev_addr = (unsigned long)(uintptr_t)&triple_hlist_a.next_addr;
	triple_hlist_c.next_addr = 0;
	triple_hlist_c.pprev_addr = (unsigned long)(uintptr_t)&triple_hlist_b.next_addr;

	empty_hlist = zigux_hlist_view_from_head(&empty_hlist_head, 8);
	single_hlist = zigux_hlist_view_from_head(&single_hlist_head, 8);
	triple_hlist = zigux_hlist_view_from_head(&triple_hlist_head, 8);
	truncated_hlist = zigux_hlist_view_from_head(&triple_hlist_head, 2);

	printf(
		"{\"constants\":{\"list_empty\":%u,\"list_singular\":%u,"
		"\"list_circular\":%u,\"list_truncated\":%u,"
		"\"hlist_empty\":%u,\"hlist_singular\":%u,"
		"\"hlist_terminated\":%u,\"hlist_truncated\":%u},"
		"\"list\":{"
		"\"empty\":{\"valid\":%s,\"empty\":%s,\"singular\":%s,"
		"\"summary\":{\"length\":%u,\"flags\":%u}},"
		"\"single\":{\"length\":%u,\"empty\":%s,\"singular\":%s,"
		"\"summary\":{\"length\":%u,\"flags\":%u}},"
		"\"triple\":{\"length\":%u,\"summary\":{\"length\":%u,\"flags\":%u}},"
		"\"truncated\":{\"length\":%u,\"summary\":{\"length\":%u,\"flags\":%u}}},"
		"\"hlist\":{"
		"\"empty\":{\"valid\":%s,\"empty\":%s,\"singular\":%s,"
		"\"summary\":{\"length\":%u,\"flags\":%u}},"
		"\"single\":{\"length\":%u,\"empty\":%s,\"singular\":%s,"
		"\"summary\":{\"length\":%u,\"flags\":%u}},"
		"\"triple\":{\"length\":%u,\"summary\":{\"length\":%u,\"flags\":%u}},"
		"\"truncated\":{\"length\":%u,\"summary\":{\"length\":%u,\"flags\":%u}}}}\n",
		ZIGUX_LIST_FLAG_EMPTY,
		ZIGUX_LIST_FLAG_SINGULAR,
		ZIGUX_LIST_FLAG_CIRCULAR,
		ZIGUX_LIST_FLAG_TRUNCATED,
		ZIGUX_HLIST_FLAG_EMPTY,
		ZIGUX_HLIST_FLAG_SINGULAR,
		ZIGUX_HLIST_FLAG_TERMINATED,
		ZIGUX_HLIST_FLAG_TRUNCATED,
		zigux_list_view_valid(&empty_list) ? "true" : "false",
		zigux_list_empty(&empty_list) ? "true" : "false",
		zigux_list_is_singular(&empty_list) ? "true" : "false",
		zigux_list_summarize(&empty_list).length,
		zigux_list_summarize(&empty_list).flags,
		zigux_list_length_bounded(&single_list),
		zigux_list_empty(&single_list) ? "true" : "false",
		zigux_list_is_singular(&single_list) ? "true" : "false",
		zigux_list_summarize(&single_list).length,
		zigux_list_summarize(&single_list).flags,
		zigux_list_length_bounded(&triple_list),
		zigux_list_summarize(&triple_list).length,
		zigux_list_summarize(&triple_list).flags,
		zigux_list_length_bounded(&truncated_list),
		zigux_list_summarize(&truncated_list).length,
		zigux_list_summarize(&truncated_list).flags,
		zigux_hlist_view_valid(&empty_hlist) ? "true" : "false",
		zigux_hlist_empty(&empty_hlist) ? "true" : "false",
		zigux_hlist_is_singular(&empty_hlist) ? "true" : "false",
		zigux_hlist_summarize(&empty_hlist).length,
		zigux_hlist_summarize(&empty_hlist).flags,
		zigux_hlist_length_bounded(&single_hlist),
		zigux_hlist_empty(&single_hlist) ? "true" : "false",
		zigux_hlist_is_singular(&single_hlist) ? "true" : "false",
		zigux_hlist_summarize(&single_hlist).length,
		zigux_hlist_summarize(&single_hlist).flags,
		zigux_hlist_length_bounded(&triple_hlist),
		zigux_hlist_summarize(&triple_hlist).length,
		zigux_hlist_summarize(&triple_hlist).flags,
		zigux_hlist_length_bounded(&truncated_hlist),
		zigux_hlist_summarize(&truncated_hlist).length,
		zigux_hlist_summarize(&truncated_hlist).flags);
	return 0;
}
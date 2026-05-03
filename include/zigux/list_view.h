#ifndef _ZIGUX_LIST_VIEW_H
#define _ZIGUX_LIST_VIEW_H

#include <zigux/abi.h>

#ifdef __KERNEL__
#include <linux/types.h>
#define zigux_list_ptr_addr(ptr) ((unsigned long)(ptr))
#else
#include <stdbool.h>
#include <stdint.h>
#define zigux_list_ptr_addr(ptr) ((unsigned long)(uintptr_t)(ptr))
#endif

static inline struct zigux_list_view
zigux_list_view_from_head(const struct zigux_list_head_ref *head, zigux_u32 max_nodes)
{
	return (struct zigux_list_view){
		.head_addr = zigux_list_ptr_addr(head),
		.max_nodes = max_nodes,
		.reserved = 0,
	};
}

static inline bool
zigux_list_view_valid(const struct zigux_list_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return view->head_addr != 0 && view->max_nodes != 0;
}

static inline const struct zigux_list_head_ref *
zigux_list_head_ptr(const struct zigux_list_view *view)
{
	return (const struct zigux_list_head_ref *)(uintptr_t)view->head_addr;
}

static inline const struct zigux_list_head_ref *
zigux_list_node_ptr(unsigned long addr)
{
	return (const struct zigux_list_head_ref *)(uintptr_t)addr;
}

static inline bool
zigux_list_empty(const struct zigux_list_view *view)
{
	const struct zigux_list_head_ref *head;

	if (!zigux_list_view_valid(view))
		return false;
	head = zigux_list_head_ptr(view);
	return head->next_addr == view->head_addr && head->prev_addr == view->head_addr;
}

static inline bool
zigux_list_singular(const struct zigux_list_view *view)
{
	const struct zigux_list_head_ref *head;
	const struct zigux_list_head_ref *node;

	if (!zigux_list_view_valid(view) || zigux_list_empty(view))
		return false;
	head = zigux_list_head_ptr(view);
	if (head->next_addr != head->prev_addr)
		return false;
	node = zigux_list_node_ptr(head->next_addr);
	return node->next_addr == view->head_addr && node->prev_addr == view->head_addr;
}

static inline struct zigux_list_summary
zigux_list_summarize(const struct zigux_list_view *view)
{
	struct zigux_list_summary summary = {0, 0};
	unsigned long current;
	zigux_u32 count = 0;

	if (!zigux_list_view_valid(view))
		return summary;
	if (zigux_list_empty(view)) {
		summary.flags = ZIGUX_LIST_FLAG_EMPTY | ZIGUX_LIST_FLAG_CIRCULAR;
		return summary;
	}

	current = zigux_list_head_ptr(view)->next_addr;
	while (count < view->max_nodes && current != 0 && current != view->head_addr) {
		current = zigux_list_node_ptr(current)->next_addr;
		count++;
	}

	summary.length = count;
	if (zigux_list_singular(view))
		summary.flags |= ZIGUX_LIST_FLAG_SINGULAR;
	if (current == view->head_addr)
		summary.flags |= ZIGUX_LIST_FLAG_CIRCULAR;
	else
		summary.flags |= ZIGUX_LIST_FLAG_TRUNCATED;
	return summary;
}

static inline zigux_u32
zigux_list_length_bounded(const struct zigux_list_view *view)
{
	return zigux_list_summarize(view).length;
}

static inline struct zigux_hlist_view
zigux_hlist_view_from_head(const struct zigux_hlist_head_ref *head, zigux_u32 max_nodes)
{
	return (struct zigux_hlist_view){
		.head_addr = zigux_list_ptr_addr(head),
		.max_nodes = max_nodes,
		.reserved = 0,
	};
}

static inline bool
zigux_hlist_view_valid(const struct zigux_hlist_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return view->head_addr != 0 && view->max_nodes != 0;
}

static inline const struct zigux_hlist_head_ref *
zigux_hlist_head_ptr(const struct zigux_hlist_view *view)
{
	return (const struct zigux_hlist_head_ref *)(uintptr_t)view->head_addr;
}

static inline const struct zigux_hlist_node_ref *
zigux_hlist_node_ptr(unsigned long addr)
{
	return (const struct zigux_hlist_node_ref *)(uintptr_t)addr;
}

static inline bool
zigux_hlist_empty(const struct zigux_hlist_view *view)
{
	if (!zigux_hlist_view_valid(view))
		return false;
	return zigux_hlist_head_ptr(view)->first_addr == 0;
}

static inline bool
zigux_hlist_singular(const struct zigux_hlist_view *view)
{
	if (!zigux_hlist_view_valid(view) || zigux_hlist_empty(view))
		return false;
	return zigux_hlist_node_ptr(zigux_hlist_head_ptr(view)->first_addr)->next_addr == 0;
}

static inline struct zigux_hlist_summary
zigux_hlist_summarize(const struct zigux_hlist_view *view)
{
	struct zigux_hlist_summary summary = {0, 0};
	unsigned long current;
	zigux_u32 count = 0;

	if (!zigux_hlist_view_valid(view))
		return summary;
	if (zigux_hlist_empty(view)) {
		summary.flags = ZIGUX_HLIST_FLAG_EMPTY | ZIGUX_HLIST_FLAG_TERMINATED;
		return summary;
	}

	current = zigux_hlist_head_ptr(view)->first_addr;
	while (count < view->max_nodes && current != 0) {
		current = zigux_hlist_node_ptr(current)->next_addr;
		count++;
	}

	summary.length = count;
	if (zigux_hlist_singular(view))
		summary.flags |= ZIGUX_HLIST_FLAG_SINGULAR;
	if (current == 0)
		summary.flags |= ZIGUX_HLIST_FLAG_TERMINATED;
	else
		summary.flags |= ZIGUX_HLIST_FLAG_TRUNCATED;
	return summary;
}

static inline zigux_u32
zigux_hlist_length_bounded(const struct zigux_hlist_view *view)
{
	return zigux_hlist_summarize(view).length;
}

#endif

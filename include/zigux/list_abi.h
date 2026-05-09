#ifndef _ZIGUX_LIST_ABI_H
#define _ZIGUX_LIST_ABI_H

#include "abi.h"

#ifdef __KERNEL__
#include <linux/list.h>
#else
#include <stdbool.h>

struct list_head {
	struct list_head *next;
	struct list_head *prev;
};

struct hlist_node {
	struct hlist_node *next;
	struct hlist_node **pprev;
};

struct hlist_head {
	struct hlist_node *first;
};
#endif

static inline struct zigux_list_view zigux_list_view_from_head(
	const struct list_head *head,
	zigux_u32 max_nodes)
{
	struct zigux_list_view view;
	view.head_addr = (unsigned long)head;
	view.max_nodes = max_nodes;
	view.reserved = 0;
	return view;
}

static inline bool zigux_list_view_valid(struct zigux_list_view view)
{
	return view.head_addr != 0 && view.max_nodes > 0 && view.reserved == 0;
}

static inline const struct list_head *zigux_list_view_head(
	struct zigux_list_view view)
{
	return (const struct list_head *)view.head_addr;
}

static inline struct zigux_list_summary zigux_list_summarize(
	struct zigux_list_view view)
{
	struct zigux_list_summary summary;
	const struct list_head *head;
	const struct list_head *cursor;
	zigux_u32 count;
	zigux_u32 flags;

	summary.length = 0;
	summary.flags = 0;

	if (!zigux_list_view_valid(view))
		return summary;

	head = zigux_list_view_head(view);
	if (head->next == head && head->prev == head) {
		summary.flags = ZIGUX_LIST_FLAG_EMPTY | ZIGUX_LIST_FLAG_CIRCULAR;
		return summary;
	}

	cursor = head->next;
	count = 0;
	flags = 0;
	while (cursor != 0 && cursor != head && count < view.max_nodes) {
		count += 1;
		cursor = cursor->next;
	}

	if (head->next == head->prev && head->next != head) {
		const struct list_head *node = head->next;
		if (node->next == head && node->prev == head)
			flags |= ZIGUX_LIST_FLAG_SINGULAR;
	}

	if (cursor == head)
		flags |= ZIGUX_LIST_FLAG_CIRCULAR;
	else
		flags |= ZIGUX_LIST_FLAG_TRUNCATED;

	summary.length = count;
	summary.flags = flags;
	return summary;
}

static inline zigux_u32 zigux_list_length_bounded(struct zigux_list_view view)
{
	return zigux_list_summarize(view).length;
}

static inline bool zigux_list_empty(struct zigux_list_view view)
{
	return (zigux_list_summarize(view).flags & ZIGUX_LIST_FLAG_EMPTY) != 0;
}

static inline bool zigux_list_is_singular(struct zigux_list_view view)
{
	return (zigux_list_summarize(view).flags & ZIGUX_LIST_FLAG_SINGULAR) != 0;
}

static inline struct zigux_hlist_view zigux_hlist_view_from_head(
	const struct hlist_head *head,
	zigux_u32 max_nodes)
{
	struct zigux_hlist_view view;
	view.head_addr = (unsigned long)head;
	view.max_nodes = max_nodes;
	view.reserved = 0;
	return view;
}

static inline bool zigux_hlist_view_valid(struct zigux_hlist_view view)
{
	return view.head_addr != 0 && view.max_nodes > 0 && view.reserved == 0;
}

static inline const struct hlist_head *zigux_hlist_view_head(
	struct zigux_hlist_view view)
{
	return (const struct hlist_head *)view.head_addr;
}

static inline struct zigux_hlist_summary zigux_hlist_summarize(
	struct zigux_hlist_view view)
{
	struct zigux_hlist_summary summary;
	const struct hlist_node *cursor;
	zigux_u32 count;
	zigux_u32 flags;

	summary.length = 0;
	summary.flags = 0;

	if (!zigux_hlist_view_valid(view))
		return summary;

	cursor = zigux_hlist_view_head(view)->first;
	if (cursor == 0) {
		summary.flags = ZIGUX_HLIST_FLAG_EMPTY | ZIGUX_HLIST_FLAG_TERMINATED;
		return summary;
	}

	count = 0;
	flags = 0;
	while (cursor != 0 && count < view.max_nodes) {
		count += 1;
		cursor = cursor->next;
	}

	if (zigux_hlist_view_head(view)->first != 0 &&
	    zigux_hlist_view_head(view)->first->next == 0)
		flags |= ZIGUX_HLIST_FLAG_SINGULAR;

	if (cursor == 0)
		flags |= ZIGUX_HLIST_FLAG_TERMINATED;
	else
		flags |= ZIGUX_HLIST_FLAG_TRUNCATED;

	summary.length = count;
	summary.flags = flags;
	return summary;
}

static inline zigux_u32 zigux_hlist_length_bounded(struct zigux_hlist_view view)
{
	return zigux_hlist_summarize(view).length;
}

static inline bool zigux_hlist_empty(struct zigux_hlist_view view)
{
	return (zigux_hlist_summarize(view).flags & ZIGUX_HLIST_FLAG_EMPTY) != 0;
}

static inline bool zigux_hlist_is_singular(struct zigux_hlist_view view)
{
	return (zigux_hlist_summarize(view).flags & ZIGUX_HLIST_FLAG_SINGULAR) != 0;
}

#endif

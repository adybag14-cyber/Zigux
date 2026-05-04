#ifndef _ZIGUX_NOTIFIER_ABI_H
#define _ZIGUX_NOTIFIER_ABI_H

#include <zigux/abi.h>

#ifdef __KERNEL__
#include <linux/types.h>
#define zigux_notifier_ptr_addr(ptr) ((unsigned long)(ptr))
#else
#include <stdbool.h>
#include <stdint.h>
#define zigux_notifier_ptr_addr(ptr) ((unsigned long)(uintptr_t)(ptr))
#endif

#define ZIGUX_NOTIFIER_CHAIN_FLAG_EMPTY 1U
#define ZIGUX_NOTIFIER_CHAIN_FLAG_TERMINATED 2U
#define ZIGUX_NOTIFIER_CHAIN_FLAG_TRUNCATED 4U
#define ZIGUX_NOTIFIER_CHAIN_FLAG_SELF_LOOP 8U
#define ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING 16U

struct zigux_notifier_block_ref {
	unsigned long notifier_call_addr;
	unsigned long next_addr;
	zigux_s32 priority;
	zigux_u32 reserved;
};

struct zigux_raw_notifier_head_ref {
	unsigned long head_addr;
};

struct zigux_notifier_chain_view {
	unsigned long head_addr;
	zigux_u32 max_nodes;
	zigux_u32 reserved;
};

struct zigux_notifier_chain_summary {
	zigux_u32 length;
	zigux_u32 flags;
	zigux_s32 highest_priority;
	zigux_s32 lowest_priority;
};

static inline struct zigux_notifier_chain_view
zigux_notifier_chain_view_from_head(const struct zigux_raw_notifier_head_ref *head,
				       zigux_u32 max_nodes)
{
	return (struct zigux_notifier_chain_view){
		.head_addr = zigux_notifier_ptr_addr(head),
		.max_nodes = max_nodes,
		.reserved = 0,
	};
}

static inline bool
zigux_notifier_chain_view_valid(const struct zigux_notifier_chain_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return view->head_addr != 0 && view->max_nodes != 0;
}

static inline const struct zigux_raw_notifier_head_ref *
zigux_notifier_chain_head_ptr(const struct zigux_notifier_chain_view *view)
{
	return (const struct zigux_raw_notifier_head_ref *)(uintptr_t)view->head_addr;
}

static inline const struct zigux_notifier_block_ref *
zigux_notifier_chain_node_ptr(unsigned long addr)
{
	return (const struct zigux_notifier_block_ref *)(uintptr_t)addr;
}

static inline bool
zigux_notifier_chain_empty(const struct zigux_notifier_chain_view *view)
{
	const struct zigux_raw_notifier_head_ref *head;

	if (!zigux_notifier_chain_view_valid(view))
		return false;
	head = zigux_notifier_chain_head_ptr(view);
	return head->head_addr == 0;
}

static inline struct zigux_notifier_chain_summary
zigux_notifier_chain_summarize(const struct zigux_notifier_chain_view *view)
{
	struct zigux_notifier_chain_summary summary = {0, 0, 0, 0};
	unsigned long current;
	zigux_u32 count = 0;
	bool priority_nonincreasing = true;
	bool have_priority = false;
	zigux_s32 previous_priority = 0;

	if (!zigux_notifier_chain_view_valid(view))
		return summary;
	if (zigux_notifier_chain_empty(view)) {
		summary.flags = ZIGUX_NOTIFIER_CHAIN_FLAG_EMPTY |
				ZIGUX_NOTIFIER_CHAIN_FLAG_TERMINATED;
		return summary;
	}

	current = zigux_notifier_chain_head_ptr(view)->head_addr;
	summary.highest_priority = INT32_MIN;
	summary.lowest_priority = INT32_MAX;

	while (count < view->max_nodes && current != 0) {
		const struct zigux_notifier_block_ref *node =
			zigux_notifier_chain_node_ptr(current);
		unsigned long next_addr = node->next_addr;

		if (have_priority && node->priority > previous_priority)
			priority_nonincreasing = false;
		have_priority = true;
		previous_priority = node->priority;
		if (node->priority > summary.highest_priority)
			summary.highest_priority = node->priority;
		if (node->priority < summary.lowest_priority)
			summary.lowest_priority = node->priority;

		count++;
		if (next_addr == current) {
			summary.length = count;
			summary.flags = ZIGUX_NOTIFIER_CHAIN_FLAG_SELF_LOOP;
			if (priority_nonincreasing)
				summary.flags |=
					ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING;
			return summary;
		}
		current = next_addr;
	}

	summary.length = count;
	if (have_priority && priority_nonincreasing)
		summary.flags |= ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING;
	if (current == 0)
		summary.flags |= ZIGUX_NOTIFIER_CHAIN_FLAG_TERMINATED;
	else
		summary.flags |= ZIGUX_NOTIFIER_CHAIN_FLAG_TRUNCATED;
	return summary;
}

static inline zigux_u32
zigux_notifier_chain_length_bounded(const struct zigux_notifier_chain_view *view)
{
	return zigux_notifier_chain_summarize(view).length;
}

static inline bool
zigux_notifier_chain_has_nonincreasing_priority_order(const struct zigux_notifier_chain_view *view)
{
	return (zigux_notifier_chain_summarize(view).flags &
		ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING) != 0;
}

#endif

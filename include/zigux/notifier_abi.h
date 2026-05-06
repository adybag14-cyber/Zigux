#ifndef _ZIGUX_NOTIFIER_ABI_H
#define _ZIGUX_NOTIFIER_ABI_H

#include "abi.h"

#ifdef __KERNEL__
#include <linux/notifier.h>
#else
#include <stdbool.h>

struct notifier_block;
typedef int (*notifier_fn_t)(struct notifier_block *nb, unsigned long action, void *data);

struct notifier_block {
	notifier_fn_t notifier_call;
	struct notifier_block *next;
	int priority;
};

struct raw_notifier_head {
	struct notifier_block *head;
};
#endif

#define ZIGUX_NOTIFIER_CHAIN_FLAG_EMPTY 1U
#define ZIGUX_NOTIFIER_CHAIN_FLAG_TERMINATED 2U
#define ZIGUX_NOTIFIER_CHAIN_FLAG_TRUNCATED 4U
#define ZIGUX_NOTIFIER_CHAIN_FLAG_SELF_LOOP 8U
#define ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING 16U

struct zigux_notifier_chain_view {
	const struct raw_notifier_head *head;
	zigux_u32 max_nodes;
	zigux_u32 reserved;
};

struct zigux_notifier_chain_summary {
	zigux_u32 length;
	zigux_s32 highest_priority;
	zigux_s32 lowest_priority;
	zigux_u32 flags;
};

static inline struct zigux_notifier_chain_view zigux_notifier_chain_view_from_head(
	const struct raw_notifier_head *head,
	zigux_u32 max_nodes)
{
	struct zigux_notifier_chain_view view;
	view.head = head;
	view.max_nodes = max_nodes;
	view.reserved = 0;
	return view;
}

static inline bool zigux_notifier_chain_view_valid(struct zigux_notifier_chain_view view)
{
	return view.head != 0 && view.max_nodes > 0;
}

static inline struct zigux_notifier_chain_summary zigux_notifier_chain_summarize(
	struct zigux_notifier_chain_view view)
{
	struct zigux_notifier_chain_summary summary;
	const struct notifier_block *cursor;
	zigux_u32 count;
	bool saw_node;
	bool priorities_nonincreasing;
	zigux_s32 previous_priority;

	summary.length = 0;
	summary.highest_priority = 0;
	summary.lowest_priority = 0;
	summary.flags = 0;

	if (!zigux_notifier_chain_view_valid(view))
		return summary;

	cursor = view.head->head;
	if (cursor == 0) {
		summary.flags = ZIGUX_NOTIFIER_CHAIN_FLAG_EMPTY |
			ZIGUX_NOTIFIER_CHAIN_FLAG_TERMINATED |
			ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING;
		return summary;
	}

	count = 0;
	saw_node = false;
	priorities_nonincreasing = true;
	previous_priority = 0;

	while (cursor != 0 && count < view.max_nodes) {
		const struct notifier_block *node = cursor;
		const struct notifier_block *next;

		count += 1;
		if (!saw_node) {
			summary.highest_priority = node->priority;
			summary.lowest_priority = node->priority;
		} else {
			if (node->priority > summary.highest_priority)
				summary.highest_priority = node->priority;
			if (node->priority < summary.lowest_priority)
				summary.lowest_priority = node->priority;
			if (node->priority > previous_priority)
				priorities_nonincreasing = false;
		}
		previous_priority = node->priority;
		saw_node = true;

		next = node->next;
		if (next == node) {
			summary.flags |= ZIGUX_NOTIFIER_CHAIN_FLAG_SELF_LOOP;
			break;
		}
		if (next == 0) {
			summary.flags |= ZIGUX_NOTIFIER_CHAIN_FLAG_TERMINATED;
			break;
		}

		cursor = next;
	}

	if (cursor != 0 && count == view.max_nodes &&
	    (summary.flags & (ZIGUX_NOTIFIER_CHAIN_FLAG_SELF_LOOP |
			       ZIGUX_NOTIFIER_CHAIN_FLAG_TERMINATED)) == 0)
		summary.flags |= ZIGUX_NOTIFIER_CHAIN_FLAG_TRUNCATED;

	if (saw_node && priorities_nonincreasing)
		summary.flags |= ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING;

	summary.length = count;
	return summary;
}

static inline zigux_u32 zigux_notifier_chain_length_bounded(struct zigux_notifier_chain_view view)
{
	return zigux_notifier_chain_summarize(view).length;
}

static inline bool zigux_notifier_chain_has_nonincreasing_priority_order(
	struct zigux_notifier_chain_view view)
{
	return (zigux_notifier_chain_summarize(view).flags &
		ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING) != 0;
}

#endif

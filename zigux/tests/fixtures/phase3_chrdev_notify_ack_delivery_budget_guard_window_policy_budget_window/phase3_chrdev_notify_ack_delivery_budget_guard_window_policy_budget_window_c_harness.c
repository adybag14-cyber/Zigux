#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summary *summary)
{
	printf("{\"parent_budget_status\":%u,"
	       "\"budget_window_flags\":%u,"
	       "\"budget_window_before\":%u,"
	       "\"budget_window_after\":%u,"
	       "\"budget_window_floor\":%u,"
	       "\"budget_window_status\":%u,"
	       "\"acked_count\":%u,"
	       "\"deferred_count\":%u,"
	       "\"suppressed_count\":%u,"
	       "\"coalesced_count\":%u,"
	       "\"dropped_count\":%u,"
	       "\"skipped_count\":%u,"
	       "\"held_count\":%u}",
	       summary->parent.budget_status,
	       summary->budget_window_flags,
	       summary->budget_window_before,
	       summary->budget_window_after,
	       summary->budget_window_floor,
	       summary->budget_window_status,
	       summary->acked_count,
	       summary->deferred_count,
	       summary->suppressed_count,
	       summary->coalesced_count,
	       summary->dropped_count,
	       summary->skipped_count,
	       summary->held_count);
}

int main(void)
{
	const unsigned long words[] = {(1UL << 0) | (1UL << 3) | (1UL << 7)};
	const unsigned long exhausted_words[] = {(1UL << 0) | (1UL << 2) | (1UL << 4)};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_acked =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0, 3, 0, 2, 1);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_dropped =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDDDD, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_skipped =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(exhausted_words, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ, ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1);
	struct zigux_chrdev_notify_ack_delivery_budget_guard_view empty_guard;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view empty_window;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view empty_policy;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view empty_budget;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view empty;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summary summary;

	printf("{\"constants\":{"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_window_applied\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_window_used\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_floor_held\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_floor_blocked\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_flag_window_exhausted\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_none\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_acked\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_deferred\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_suppressed\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_coalesced\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_dropped\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_skipped\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_status_held\":%u}",
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_USED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_HELD,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_BLOCKED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_EXHAUSTED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_ACKED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SUPPRESSED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_COALESCED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SKIPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_HELD);

	printf(",\"acked\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_acked, 1, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&guard, 2, 1, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&window, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&policy, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&budget, 2, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summarize(&view);
	}
	print_summary(&summary);
	printf("}");

	printf(",\"policy_deferred\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_acked, 1, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&guard, 2, 1, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&window, ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&policy, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&budget, 2, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summarize(&view);
	}
	print_summary(&summary);
	printf("}");

	printf(",\"floor_held\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_acked, 1, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&guard, 2, 1, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&window, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&policy, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&budget, 1, 1);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summarize(&view);
	}
	print_summary(&summary);
	printf("}");

	printf(",\"held\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_acked, 1, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&guard, 1, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&window, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&policy, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&budget, 2, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summarize(&view);
	}
	print_summary(&summary);
	printf("}");

	printf(",\"suppressed_held\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_acked, 1, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&guard, 1, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&window, ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&policy, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&budget, 2, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summarize(&view);
	}
	print_summary(&summary);
	printf("}");

	printf(",\"dropped\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_dropped, 0, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&guard, 0, 0, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&window, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&policy, 0, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&budget, 2, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summarize(&view);
	}
	print_summary(&summary);
	printf("}");

	printf(",\"skipped\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_skipped, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&guard, 2, 2, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&window, 0);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&policy, 1, 1);
		struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view view = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&budget, 2, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summarize(&view);
	}
	print_summary(&summary);
	printf("}");

	empty_guard = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(NULL, 0, 0);
	empty_window = zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(&empty_guard, 0, 0, 0);
	empty_policy = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(&empty_window, 0);
	empty_budget = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(&empty_policy, 0, 0);
	empty = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_from_parent(&empty_budget, 0, 0);

	printf(",\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_view_valid(&empty) ? "true" : "false");
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_summarize(&empty);
	print_summary(&summary);
	printf("}}\n");
	return 0;
}

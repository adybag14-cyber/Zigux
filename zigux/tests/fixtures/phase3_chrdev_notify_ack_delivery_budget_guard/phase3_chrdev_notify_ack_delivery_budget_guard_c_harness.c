#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_notify_ack_delivery_budget_guard_summary *summary)
{
	printf("{\"parent_budget_status\":%u,"
	       "\"guard_flags\":%u,"
	       "\"primary_before\":%u,"
	       "\"primary_after\":%u,"
	       "\"deferred_before\":%u,"
	       "\"deferred_after\":%u,"
	       "\"primary_guard_floor\":%u,"
	       "\"deferred_guard_floor\":%u,"
	       "\"guard_status\":%u,"
	       "\"acked_count\":%u,"
	       "\"deferred_count\":%u,"
	       "\"suppressed_count\":%u,"
	       "\"coalesced_count\":%u,"
	       "\"dropped_count\":%u,"
	       "\"skipped_count\":%u,"
	       "\"held_count\":%u}",
	       summary->parent.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status,
	       summary->guard_flags,
	       summary->primary_before,
	       summary->primary_after,
	       summary->deferred_before,
	       summary->deferred_after,
	       summary->primary_guard_floor,
	       summary->deferred_guard_floor,
	       summary->guard_status,
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
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_policy_deferred =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED, 1, 1, 3, 0, 1, 1, 3, 0, 2, 1, 2, 0, 1, 1, 3, 0, 2, 1);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_coalesced =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE, 1, 0, 3, 0, 1, 0, 2, 1, 1, 0, 1, 0, 1, 0, 3, 0, 0, 0);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_suppressed =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED, 1, 1, 2, 0, 1, 1, 3, 0, 2, 1, 2, 1, 1, 1, 3, 0, 2, 1);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_dropped =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDDDD, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_skipped =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(exhausted_words, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ, ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 2, 1, 2, 1);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent_empty = {0};
	struct zigux_chrdev_notify_ack_delivery_budget_guard_view empty;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_summary summary;

	parent_empty.major = 240;
	parent_empty.request_count = 2;
	parent_empty.policy = ZIGUX_IDA_POLICY_FIRST_FIT;
	parent_empty.requested_mode = ZIGUX_CHRDEV_MODE_READ;
	parent_empty.supported_mode = ZIGUX_CHRDEV_MODE_READ;
	parent_empty.available_ops = ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ;
	parent_empty.io_op = ZIGUX_CHRDEV_IO_OP_READ;
	parent_empty.requested_bytes = 8;
	parent_empty.max_chunk_bytes = 8;
	parent_empty.max_segments = 1;
	parent_empty.resume_passes = 2;
	parent_empty.retry_budget = 1;
	parent_empty.stall_budget = 1;
	parent_empty.backoff_quanta = 5;
	parent_empty.queue_capacity = 2;
	parent_empty.requeue_budget = 1;
	parent_empty.completion_cookie = 0x9999;
	parent_empty.notify_mask = ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS;
	parent_empty.notify_cookie = 0xFFFF;
	parent_empty.ack_mask = ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED;
	parent_empty.ack_cookie = 0xABCD;
	parent_empty.ack_budget = 1;
	parent_empty.deferred_ack_budget = 1;
	empty = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_empty, 0, 0);

	printf("{\"constants\":{"
	       "\"chrdev_notify_ack_delivery_budget_guard_flag_applied\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_flag_primary_held\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_flag_deferred_held\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_flag_exhausted\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_flag_passthrough\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_status_none\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_status_acked\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_status_deferred\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_status_suppressed\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_status_coalesced\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_status_dropped\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_status_skipped\":%u,"
	       "\"chrdev_notify_ack_delivery_budget_guard_status_held\":%u}",
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_APPLIED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PRIMARY_HELD,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_DEFERRED_HELD,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_EXHAUSTED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_NONE,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_ACKED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SUPPRESSED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_COALESCED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DROPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SKIPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_HELD);

	printf(",\"acked\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view view = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_acked, 1, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&view);
	}
	print_summary(&summary);
	printf("}");
	printf(",\"primary_held\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view view = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_acked, 2, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&view);
	}
	print_summary(&summary);
	printf("}");
	printf(",\"policy_deferred\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view view = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_policy_deferred, 0, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&view);
	}
	print_summary(&summary);
	printf("}");
	printf(",\"coalesced\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view view = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_coalesced, 0, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&view);
	}
	print_summary(&summary);
	printf("}");
	printf(",\"suppressed\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view view = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_suppressed, 1, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&view);
	}
	print_summary(&summary);
	printf("}");
	printf(",\"dropped\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view view = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_dropped, 0, 0);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&view);
	}
	print_summary(&summary);
	printf("}");
	printf(",\"skipped\":{\"summary\":");
	{
		struct zigux_chrdev_notify_ack_delivery_budget_guard_view view = zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(&parent_skipped, 1, 1);
		summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&view);
	}
	print_summary(&summary);
	printf("}");
	printf(",\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_notify_ack_delivery_budget_guard_view_valid(&empty) ? "true" : "false");
	summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&empty);
	print_summary(&summary);
	printf("}}\n");
	return 0;
}

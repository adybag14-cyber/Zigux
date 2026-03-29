#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summary *summary)
{
	printf("{\"window_policy_budget_window_delivery_window_budget_window_status\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_flags\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_before\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_after\":%u,"
	       "\"deferred_window_policy_budget_window_delivery_window_budget_window_delivery_before\":%u,"
	       "\"deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_status\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_acked_count\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_deferred_count\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_suppressed_count\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_coalesced_count\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count\":%u,"
	       "\"window_policy_budget_window_delivery_window_budget_window_delivery_skipped_count\":%u}",
	       summary->window_policy_budget_window_delivery_window_budget_window_status,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_flags,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_before,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_after,
	       summary->deferred_window_policy_budget_window_delivery_window_budget_window_delivery_before,
	       summary->deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_status,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_acked_count,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_deferred_count,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_suppressed_count,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_coalesced_count,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count,
	       summary->window_policy_budget_window_delivery_window_budget_window_delivery_skipped_count);
}

int main(void)
{
	const unsigned long words[] = {(1UL << 0) | (1UL << 3) | (1UL << 7)};
	const unsigned long exhausted_words[] = {(1UL << 0) | (1UL << 2) | (1UL << 4)};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view acked =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 1, 0);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view fallback_deferred =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 1, 0, 3, 0, 2, 1, 2, 0, 0, 1);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view policy_deferred =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED, 1, 1, 3, 0, 1, 1, 3, 0, 2, 1, 2, 0, 1, 1);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view coalesced =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE, 1, 0, 3, 0, 1, 0, 2, 1, 1, 0, 1, 0, 1, 0);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view suppressed =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED, 1, 1, 2, 0, 1, 1, 3, 0, 2, 1, 2, 1, 1, 1);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view dropped =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xDDDD, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view skipped =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(exhausted_words, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ, ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0, 1, 1, 2, 0, 1, 1, 2, 1, 2, 1, 2, 1, 1, 1);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view empty = {0};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summary summary;

	empty.major = 240;
	empty.first_minor = 0;
	empty.minor_count = 0;
	empty.max_scan = 0;
	empty.request_count = 2;
	empty.policy = ZIGUX_IDA_POLICY_FIRST_FIT;
	empty.target_minor = 0;
	empty.requested_mode = ZIGUX_CHRDEV_MODE_READ;
	empty.supported_mode = ZIGUX_CHRDEV_MODE_READ;
	empty.available_ops = ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ;
	empty.io_op = ZIGUX_CHRDEV_IO_OP_READ;
	empty.requested_bytes = 8;
	empty.max_chunk_bytes = 8;
	empty.file_offset = 0;
	empty.bytes_completed = 0;
	empty.max_segments = 1;
	empty.resume_passes = 2;
	empty.retry_budget = 1;
	empty.stall_budget = 1;
	empty.backoff_quanta = 5;
	empty.queue_depth = 0;
	empty.queue_capacity = 2;
	empty.requeue_budget = 1;
	empty.completion_cookie = 0x9999;
	empty.completion_budget = 0;
	empty.notify_mask = ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS;
	empty.notify_budget = 0;
	empty.notify_cookie = 0xFFFF;
	empty.reserved = 0;
	empty.policy_flags = 0;
	empty.policy_reserved = 0;
	empty.delivery_budget = 0;
	empty.deferred_budget = 0;
	empty.ack_mask = ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED;
	empty.ack_window = 2;
	empty.ack_cookie = 0xABCD;
	empty.ack_observed = 0;
	empty.ack_reserved = 0;
	empty.ack_policy_flags = 0;
	empty.ack_policy_reserved = 0;
	empty.ack_budget = 1;
	empty.deferred_ack_budget = 1;
	empty.ack_budget_reserved = 0;
	empty.window_floor = 0;
	empty.window_reserved = 0;
	empty.window_policy_flags = 0;
	empty.window_policy_reserved = 0;
	empty.window_policy_budget = 0;
	empty.deferred_window_policy_budget = 0;
	empty.window_policy_budget_reserved = 0;
	empty.window_policy_budget_window = 0;
	empty.window_policy_budget_window_floor = 0;
	empty.window_policy_budget_window_reserved = 0;
	empty.window_policy_budget_window_delivery_budget = 0;
	empty.deferred_window_policy_budget_window_delivery_budget = 0;
	empty.window_policy_budget_window_delivery_reserved = 0;
	empty.window_policy_budget_window_delivery_window = 0;
	empty.window_policy_budget_window_delivery_window_floor = 0;
	empty.window_policy_budget_window_delivery_window_reserved = 0;
	empty.window_policy_budget_window_delivery_window_budget = 0;
	empty.deferred_window_policy_budget_window_delivery_window_budget = 0;
	empty.window_policy_budget_window_delivery_window_budget_reserved = 0;
	empty.window_policy_budget_window_delivery_window_budget_window = 0;
	empty.window_policy_budget_window_delivery_window_budget_window_floor = 0;
	empty.window_policy_budget_window_delivery_window_budget_window_reserved = 0;
	empty.window_policy_budget_window_delivery_window_budget_window_delivery_budget = 0;
	empty.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget = 0;
	empty.window_policy_budget_window_delivery_window_budget_window_delivery_reserved = 0;

	printf("{\"constants\":{\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_flag_budget_applied\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_flag_window_delivery_budget_used\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_flag_deferred_window_delivery_budget_used\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_flag_window_delivery_budget_exhausted\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_flag_deferred_window_delivery_budget_exhausted\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_status_none\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_status_acked\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_status_deferred\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_status_suppressed\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_status_coalesced\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_status_dropped\":%u,"
	       "\"chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_status_skipped\":%u}",
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_USED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_USED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_EXHAUSTED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_EXHAUSTED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_ACKED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED);
	printf(",\"acked\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&acked);
	print_summary(&summary);
	printf("}");
	printf(",\"fallback_deferred\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&fallback_deferred);
	print_summary(&summary);
	printf("}");
	printf(",\"policy_deferred\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&policy_deferred);
	print_summary(&summary);
	printf("}");
	printf(",\"coalesced\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&coalesced);
	print_summary(&summary);
	printf("}");
	printf(",\"suppressed\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&suppressed);
	print_summary(&summary);
	printf("}");
	printf(",\"dropped\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&dropped);
	print_summary(&summary);
	printf("}");
	printf(",\"skipped\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&skipped);
	print_summary(&summary);
	printf("}");
	printf(",\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_valid(&empty) ? "true" : "false");
	summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&empty);
	print_summary(&summary);
	printf("}}\n");
	return 0;
}

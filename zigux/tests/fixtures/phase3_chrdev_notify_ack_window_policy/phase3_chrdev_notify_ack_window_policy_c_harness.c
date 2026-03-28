#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_notify_ack_window_policy_summary *summary)
{
	printf("{\"window_status\":%u,\"window_after\":%u,\"window_floor\":%u,\"window_policy_flags\":%u,\"effective_window_policy_flags\":%u,\"effective_window_cookie\":%llu,\"window_policy_status\":%u,\"policy_window_acked_count\":%u,\"policy_window_deferred_count\":%u,\"policy_window_suppressed_count\":%u,\"policy_window_coalesced_count\":%u,\"policy_window_dropped_count\":%u,\"policy_window_skipped_count\":%u}",
	       summary->window_status, summary->window_after, summary->window_floor,
	       summary->window_policy_flags, summary->effective_window_policy_flags,
	       (unsigned long long)summary->effective_window_cookie,
	       summary->window_policy_status, summary->policy_window_acked_count,
	       summary->policy_window_deferred_count,
	       summary->policy_window_suppressed_count,
	       summary->policy_window_coalesced_count,
	       summary->policy_window_dropped_count,
	       summary->policy_window_skipped_count);
}

int main(void)
{
	const unsigned long words[] = {(1UL << 0) | (1UL << 3) | (1UL << 7)};
	const unsigned long exhausted_words[] = {(1UL << 0) | (1UL << 2) | (1UL << 4)};
	struct zigux_chrdev_notify_ack_window_policy_view acked =
		zigux_chrdev_notify_ack_window_policy_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0, 0, 0);
	struct zigux_chrdev_notify_ack_window_policy_view forced_deferred =
		zigux_chrdev_notify_ack_window_policy_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xB2B2, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED);
	struct zigux_chrdev_notify_ack_window_policy_view dropped =
		zigux_chrdev_notify_ack_window_policy_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xD4D4, 1, 0, 1, 0, 0, 0);
	struct zigux_chrdev_notify_ack_window_policy_view suppressed_dropped =
		zigux_chrdev_notify_ack_window_policy_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED);
	struct zigux_chrdev_notify_ack_window_policy_view coalesced =
		zigux_chrdev_notify_ack_window_policy_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0xE5E5, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xE5E5, 1, 0, 1, 0, 0, ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE);
	struct zigux_chrdev_notify_ack_window_policy_view skipped =
		zigux_chrdev_notify_ack_window_policy_view_from_bits(exhausted_words, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ, ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1, 0, 0);
	struct zigux_chrdev_notify_ack_window_policy_view empty = {0};
	struct zigux_chrdev_notify_ack_window_policy_summary summary;

	empty.major = 240;
	empty.request_count = 2;
	empty.policy = ZIGUX_IDA_POLICY_FIRST_FIT;
	empty.requested_mode = ZIGUX_CHRDEV_MODE_READ;
	empty.supported_mode = ZIGUX_CHRDEV_MODE_READ;
	empty.available_ops = ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ;
	empty.io_op = ZIGUX_CHRDEV_IO_OP_READ;
	empty.requested_bytes = 8;
	empty.max_chunk_bytes = 8;
	empty.max_segments = 1;
	empty.resume_passes = 2;
	empty.retry_budget = 1;
	empty.stall_budget = 1;
	empty.backoff_quanta = 5;
	empty.queue_capacity = 2;
	empty.requeue_budget = 1;
	empty.completion_cookie = 0x9999;
	empty.notify_mask = ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS;
	empty.notify_cookie = 0xFFFF;
	empty.ack_mask = ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED;
	empty.ack_cookie = 0xABCD;

	printf("{\"constants\":{\"chrdev_notify_ack_window_policy_force_deferred\":%u,"
	       "\"chrdev_notify_ack_window_policy_suppress_dropped\":%u,"
	       "\"chrdev_notify_ack_window_policy_coalesce_cookie\":%u,"
	       "\"chrdev_notify_ack_window_policy_status_none\":%u,"
	       "\"chrdev_notify_ack_window_policy_status_acked\":%u,"
	       "\"chrdev_notify_ack_window_policy_status_deferred\":%u,"
	       "\"chrdev_notify_ack_window_policy_status_suppressed\":%u,"
	       "\"chrdev_notify_ack_window_policy_status_coalesced\":%u,"
	       "\"chrdev_notify_ack_window_policy_status_dropped\":%u,"
	       "\"chrdev_notify_ack_window_policy_status_skipped\":%u}",
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_ACKED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SUPPRESSED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_COALESCED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DROPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SKIPPED);
	printf(",\"acked\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_summarize(&acked);
	print_summary(&summary);
	printf("}");
	printf(",\"forced_deferred\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_summarize(&forced_deferred);
	print_summary(&summary);
	printf("}");
	printf(",\"dropped\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_summarize(&dropped);
	print_summary(&summary);
	printf("}");
	printf(",\"suppressed_dropped\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_summarize(&suppressed_dropped);
	print_summary(&summary);
	printf("}");
	printf(",\"coalesced\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_summarize(&coalesced);
	print_summary(&summary);
	printf("}");
	printf(",\"skipped\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_window_policy_summarize(&skipped);
	print_summary(&summary);
	printf("}");
	printf(",\"empty\":{\"is_valid\":%s,\"summary\":", zigux_chrdev_notify_ack_window_policy_view_valid(&empty) ? "true" : "false");
	summary = zigux_chrdev_notify_ack_window_policy_summarize(&empty);
	print_summary(&summary);
	printf("}}\n");
	return 0;
}

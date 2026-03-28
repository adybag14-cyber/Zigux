#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_notify_ack_budget_summary *summary)
{
	printf("{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"io_op\":%u,\"requested_bytes\":%u,\"start_offset\":%llu,\"next_offset\":%llu,\"initial_bytes_completed\":%u,\"final_bytes_completed\":%u,\"pass_count\":%u,\"issued_bytes\":%u,\"remaining_bytes\":%u,\"projected_remaining_bytes\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"retry_count\":%u,\"stall_count\":%u,\"requeue_count\":%u,\"queue_depth_before\":%u,\"queue_depth_after\":%u,\"remaining_retry_budget\":%u,\"remaining_requeue_budget\":%u,\"backoff_ticks\":%u,\"completion_cookie\":%llu,\"completion_status\":%u,\"completion_count\":%u,\"deferred_count\":%u,\"failure_count\":%u,\"remaining_completion_budget\":%u,\"notify_mask\":%u,\"matched_notify_mask\":%u,\"notify_status\":%u,\"notify_count\":%u,\"deferred_notify_count\":%u,\"dropped_notify_count\":%u,\"remaining_notify_budget\":%u,\"notify_cookie\":%llu,\"flags\":%u,\"policy_flags\":%u,\"effective_policy_flags\":%u,\"effective_notify_cookie\":%llu,\"policy_status\":%u,\"policy_notify_count\":%u,\"policy_deferred_count\":%u,\"policy_suppressed_count\":%u,\"policy_coalesced_count\":%u,\"budget_flags\":%u,\"delivery_budget_before\":%u,\"delivery_budget_after\":%u,\"deferred_budget_before\":%u,\"deferred_budget_after\":%u,\"budget_status\":%u,\"budget_notify_count\":%u,\"budget_deferred_count\":%u,\"budget_dropped_count\":%u,\"budget_suppressed_count\":%u,\"ack_mask\":%u,\"matched_ack_mask\":%u,\"ack_status\":%u,\"ack_count\":%u,\"deferred_ack_count\":%u,\"expired_ack_count\":%u,\"skipped_ack_count\":%u,\"ack_window_before\":%u,\"ack_window_after\":%u,\"ack_cookie\":%llu,\"ack_flags\":%u,\"ack_policy_flags\":%u,\"effective_ack_policy_flags\":%u,\"effective_ack_cookie\":%llu,\"ack_policy_status\":%u,\"policy_acked_count\":%u,\"policy_deferred_ack_count\":%u,\"policy_suppressed_ack_count\":%u,\"policy_coalesced_ack_count\":%u,\"policy_expired_ack_count\":%u,\"policy_skipped_ack_count\":%u,\"ack_budget_flags\":%u,\"ack_budget_before\":%u,\"ack_budget_after\":%u,\"deferred_ack_budget_before\":%u,\"deferred_ack_budget_after\":%u,\"ack_budget_status\":%u,\"budget_acked_count\":%u,\"budget_deferred_ack_count\":%u,\"budget_dropped_ack_count\":%u,\"budget_suppressed_ack_count\":%u,\"budget_skipped_ack_count\":%u}",
	       summary->major, summary->target_minor, summary->selected_count, summary->resolved_index, summary->resolved_dev, summary->granted_mode, summary->io_op, summary->requested_bytes,
	       (unsigned long long)summary->start_offset, (unsigned long long)summary->next_offset, summary->initial_bytes_completed, summary->final_bytes_completed,
	       summary->pass_count, summary->issued_bytes, summary->remaining_bytes, summary->projected_remaining_bytes, summary->entry_ops, summary->data_ops,
	       summary->exit_ops, summary->blocked_ops, summary->retry_count, summary->stall_count, summary->requeue_count, summary->queue_depth_before,
	       summary->queue_depth_after, summary->remaining_retry_budget, summary->remaining_requeue_budget, summary->backoff_ticks,
	       (unsigned long long)summary->completion_cookie, summary->completion_status, summary->completion_count, summary->deferred_count,
	       summary->failure_count, summary->remaining_completion_budget, summary->notify_mask, summary->matched_notify_mask, summary->notify_status,
	       summary->notify_count, summary->deferred_notify_count, summary->dropped_notify_count, summary->remaining_notify_budget,
	       (unsigned long long)summary->notify_cookie, summary->flags, summary->policy_flags, summary->effective_policy_flags,
	       (unsigned long long)summary->effective_notify_cookie, summary->policy_status, summary->policy_notify_count, summary->policy_deferred_count,
	       summary->policy_suppressed_count, summary->policy_coalesced_count, summary->budget_flags, summary->delivery_budget_before,
	       summary->delivery_budget_after, summary->deferred_budget_before, summary->deferred_budget_after, summary->budget_status,
	       summary->budget_notify_count, summary->budget_deferred_count, summary->budget_dropped_count, summary->budget_suppressed_count,
	       summary->ack_mask, summary->matched_ack_mask, summary->ack_status, summary->ack_count, summary->deferred_ack_count,
	       summary->expired_ack_count, summary->skipped_ack_count, summary->ack_window_before, summary->ack_window_after,
	       (unsigned long long)summary->ack_cookie, summary->ack_flags, summary->ack_policy_flags, summary->effective_ack_policy_flags,
	       (unsigned long long)summary->effective_ack_cookie, summary->ack_policy_status, summary->policy_acked_count, summary->policy_deferred_ack_count,
	       summary->policy_suppressed_ack_count, summary->policy_coalesced_ack_count, summary->policy_expired_ack_count, summary->policy_skipped_ack_count,
	       summary->ack_budget_flags, summary->ack_budget_before, summary->ack_budget_after, summary->deferred_ack_budget_before,
	       summary->deferred_ack_budget_after, summary->ack_budget_status, summary->budget_acked_count, summary->budget_deferred_ack_count,
	       summary->budget_dropped_ack_count, summary->budget_suppressed_ack_count, summary->budget_skipped_ack_count);
}

int main(void)
{
	const unsigned long words[] = {(1UL << 0) | (1UL << 3) | (1UL << 7)};
	const unsigned long exhausted_words[] = {(1UL << 0) | (1UL << 2) | (1UL << 4)};
	struct zigux_chrdev_notify_ack_budget_view acked =
		zigux_chrdev_notify_ack_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xAAAA, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xA1A1, 1, 0, 1, 0);
	struct zigux_chrdev_notify_ack_budget_view fallback_deferred =
		zigux_chrdev_notify_ack_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xBBBB, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xB2B2, 1, 0, 0, 1);
	struct zigux_chrdev_notify_ack_budget_view policy_deferred =
		zigux_chrdev_notify_ack_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xCCCC, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xC3C3, 1, ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED, 1, 1);
	struct zigux_chrdev_notify_ack_budget_view dropped =
		zigux_chrdev_notify_ack_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xDDDD, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xD4D4, 1, 0, 0, 0);
	struct zigux_chrdev_notify_ack_budget_view suppressed =
		zigux_chrdev_notify_ack_budget_view_from_bits(words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_WRITE, ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5, 1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1, 0xE5E5, 0, 1, 0, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 0, 0xE5E5, 0, ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED, 1, 1);
	struct zigux_chrdev_notify_ack_budget_view skipped =
		zigux_chrdev_notify_ack_budget_view_from_bits(exhausted_words, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE | ZIGUX_CHRDEV_FOP_READ, ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4, 2, 0x7777, 0, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xF6F6, ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE, 3, 4, ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED, 2, 0xF6F6, 0, 0, 1, 1);
	struct zigux_chrdev_notify_ack_budget_view empty = {0};
	struct zigux_chrdev_notify_ack_budget_summary summary;

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

	printf("{\"constants\":{\"chrdev_notify_ack_budget_flag_budget_applied\":%u,"
	       "\"chrdev_notify_ack_budget_flag_ack_budget_used\":%u,"
	       "\"chrdev_notify_ack_budget_flag_deferred_ack_budget_used\":%u,"
	       "\"chrdev_notify_ack_budget_status_none\":%u,"
	       "\"chrdev_notify_ack_budget_status_acked\":%u,"
	       "\"chrdev_notify_ack_budget_status_deferred\":%u,"
	       "\"chrdev_notify_ack_budget_status_dropped\":%u,"
	       "\"chrdev_notify_ack_budget_status_suppressed\":%u,"
	       "\"chrdev_notify_ack_budget_status_skipped\":%u}",
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_BUDGET_APPLIED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_ACK_BUDGET_USED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_USED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_ACKED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DROPPED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SUPPRESSED,
	       ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SKIPPED);
	printf(",\"acked\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_budget_summarize(&acked);
	print_summary(&summary);
	printf("}");
	printf(",\"fallback_deferred\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_budget_summarize(&fallback_deferred);
	print_summary(&summary);
	printf("}");
	printf(",\"policy_deferred\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_budget_summarize(&policy_deferred);
	print_summary(&summary);
	printf("}");
	printf(",\"dropped\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_budget_summarize(&dropped);
	print_summary(&summary);
	printf("}");
	printf(",\"suppressed\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_budget_summarize(&suppressed);
	print_summary(&summary);
	printf("}");
	printf(",\"skipped\":{\"summary\":");
	summary = zigux_chrdev_notify_ack_budget_summarize(&skipped);
	print_summary(&summary);
	printf("}");
	printf(",\"empty\":{\"is_valid\":%s,\"summary\":", zigux_chrdev_notify_ack_budget_view_valid(&empty) ? "true" : "false");
	summary = zigux_chrdev_notify_ack_budget_summarize(&empty);
	print_summary(&summary);
	printf("}}\n");
	return 0;
}

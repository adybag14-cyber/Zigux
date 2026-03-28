#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_notify_policy_summary *summary)
{
	printf("{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"io_op\":%u,\"requested_bytes\":%u,\"start_offset\":%llu,\"next_offset\":%llu,\"initial_bytes_completed\":%u,\"final_bytes_completed\":%u,\"pass_count\":%u,\"issued_bytes\":%u,\"remaining_bytes\":%u,\"projected_remaining_bytes\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"retry_count\":%u,\"stall_count\":%u,\"requeue_count\":%u,\"queue_depth_before\":%u,\"queue_depth_after\":%u,\"remaining_retry_budget\":%u,\"remaining_requeue_budget\":%u,\"backoff_ticks\":%u,\"completion_cookie\":%llu,\"completion_status\":%u,\"completion_count\":%u,\"deferred_count\":%u,\"failure_count\":%u,\"remaining_completion_budget\":%u,\"notify_mask\":%u,\"matched_notify_mask\":%u,\"notify_status\":%u,\"notify_count\":%u,\"deferred_notify_count\":%u,\"dropped_notify_count\":%u,\"remaining_notify_budget\":%u,\"notify_cookie\":%llu,\"flags\":%u,\"policy_flags\":%u,\"effective_policy_flags\":%u,\"effective_notify_cookie\":%llu,\"policy_status\":%u,\"policy_notify_count\":%u,\"policy_deferred_count\":%u,\"policy_suppressed_count\":%u,\"policy_coalesced_count\":%u}",
	       summary->major, summary->target_minor, summary->selected_count,
	       summary->resolved_index, summary->resolved_dev, summary->granted_mode,
	       summary->io_op, summary->requested_bytes,
	       (unsigned long long)summary->start_offset,
	       (unsigned long long)summary->next_offset,
	       summary->initial_bytes_completed, summary->final_bytes_completed,
	       summary->pass_count, summary->issued_bytes, summary->remaining_bytes,
	       summary->projected_remaining_bytes, summary->entry_ops,
	       summary->data_ops, summary->exit_ops, summary->blocked_ops,
	       summary->retry_count, summary->stall_count, summary->requeue_count,
	       summary->queue_depth_before, summary->queue_depth_after,
	       summary->remaining_retry_budget, summary->remaining_requeue_budget,
	       summary->backoff_ticks,
	       (unsigned long long)summary->completion_cookie,
	       summary->completion_status, summary->completion_count,
	       summary->deferred_count, summary->failure_count,
	       summary->remaining_completion_budget, summary->notify_mask,
	       summary->matched_notify_mask, summary->notify_status,
	       summary->notify_count, summary->deferred_notify_count,
	       summary->dropped_notify_count, summary->remaining_notify_budget,
	       (unsigned long long)summary->notify_cookie, summary->flags,
	       summary->policy_flags, summary->effective_policy_flags,
	       (unsigned long long)summary->effective_notify_cookie,
	       summary->policy_status, summary->policy_notify_count,
	       summary->policy_deferred_count, summary->policy_suppressed_count,
	       summary->policy_coalesced_count);
}

int main(void)
{
	const unsigned long words[] = {
		(1UL << 0) | (1UL << 3) | (1UL << 7),
	};
	const unsigned long exhausted_words[] = {
		(1UL << 0) | (1UL << 2) | (1UL << 4),
	};
	struct zigux_chrdev_notify_policy_view delivered =
		zigux_chrdev_notify_policy_view_from_bits(
			words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1,
			0xAAAA, 0);
	struct zigux_chrdev_notify_policy_view forced_deferred =
		zigux_chrdev_notify_policy_view_from_bits(
			words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1,
			0xBBBB, ZIGUX_CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED);
	struct zigux_chrdev_notify_policy_view suppressed_failure =
		zigux_chrdev_notify_policy_view_from_bits(
			exhausted_words, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT,
			20, ZIGUX_CHRDEV_MODE_READ, ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_READ,
			ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5, 1, 4,
			2, 0x7777, 0, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1, 0xCCCC,
			ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE);
	struct zigux_chrdev_notify_policy_view coalesced =
		zigux_chrdev_notify_policy_view_from_bits(
			words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0xDEAD, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1,
			0xDEAD, ZIGUX_CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE);
	struct zigux_chrdev_notify_policy_view dropped =
		zigux_chrdev_notify_policy_view_from_bits(
			words, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 0,
			0xEEEE, 0);
	struct zigux_chrdev_notify_policy_view empty = {
		.bits_addr = 0,
		.major = 240,
		.first_minor = 0,
		.minor_count = 0,
		.max_scan = 0,
		.request_count = 2,
		.policy = ZIGUX_IDA_POLICY_FIRST_FIT,
		.target_minor = 0,
		.requested_mode = ZIGUX_CHRDEV_MODE_READ,
		.supported_mode = ZIGUX_CHRDEV_MODE_READ,
		.available_ops = ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
					 ZIGUX_CHRDEV_FOP_READ,
		.io_op = ZIGUX_CHRDEV_IO_OP_READ,
		.requested_bytes = 8,
		.max_chunk_bytes = 8,
		.file_offset = 0,
		.bytes_completed = 0,
		.max_segments = 1,
		.resume_passes = 2,
		.retry_budget = 1,
		.stall_budget = 1,
		.backoff_quanta = 5,
		.queue_depth = 0,
		.queue_capacity = 2,
		.requeue_budget = 1,
		.completion_cookie = 0x9999,
		.completion_budget = 0,
		.notify_mask = ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS,
		.notify_cookie = 0xFFFF,
		.notify_budget = 0,
		.reserved = 0,
		.policy_flags = 0,
		.policy_reserved = 0,
	};
	struct zigux_chrdev_notify_policy_summary delivered_summary =
		zigux_chrdev_notify_policy_summarize(&delivered);
	struct zigux_chrdev_notify_policy_summary forced_deferred_summary =
		zigux_chrdev_notify_policy_summarize(&forced_deferred);
	struct zigux_chrdev_notify_policy_summary suppressed_failure_summary =
		zigux_chrdev_notify_policy_summarize(&suppressed_failure);
	struct zigux_chrdev_notify_policy_summary coalesced_summary =
		zigux_chrdev_notify_policy_summarize(&coalesced);
	struct zigux_chrdev_notify_policy_summary dropped_summary =
		zigux_chrdev_notify_policy_summarize(&dropped);
	struct zigux_chrdev_notify_policy_summary empty_summary =
		zigux_chrdev_notify_policy_summarize(&empty);

	printf("{\"constants\":{\"chrdev_notify_policy_force_deferred\":%u,"
	       "\"chrdev_notify_policy_suppress_failure\":%u,"
	       "\"chrdev_notify_policy_coalesce_cookie\":%u,"
	       "\"chrdev_notify_policy_status_none\":%u,"
	       "\"chrdev_notify_policy_status_delivered\":%u,"
	       "\"chrdev_notify_policy_status_deferred\":%u,"
	       "\"chrdev_notify_policy_status_suppressed\":%u,"
	       "\"chrdev_notify_policy_status_coalesced\":%u},"
	       "\"delivered\":{\"summary\":",
	       ZIGUX_CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE,
	       ZIGUX_CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE,
	       ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
	       ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED,
	       ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED,
	       ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_COALESCED);
	print_summary(&delivered_summary);
	printf("},\"forced_deferred\":{\"summary\":");
	print_summary(&forced_deferred_summary);
	printf("},\"suppressed_failure\":{\"summary\":");
	print_summary(&suppressed_failure_summary);
	printf("},\"coalesced\":{\"summary\":");
	print_summary(&coalesced_summary);
	printf("},\"dropped\":{\"summary\":");
	print_summary(&dropped_summary);
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_notify_policy_view_valid(&empty) ? "true" : "false");
	print_summary(&empty_summary);
	printf("}}\n");
	return 0;
}

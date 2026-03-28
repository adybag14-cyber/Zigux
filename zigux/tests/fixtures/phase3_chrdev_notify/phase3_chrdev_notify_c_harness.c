#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_notify_summary *summary)
{
	printf("{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"io_op\":%u,\"requested_bytes\":%u,\"start_offset\":%llu,\"next_offset\":%llu,\"initial_bytes_completed\":%u,\"final_bytes_completed\":%u,\"pass_count\":%u,\"issued_bytes\":%u,\"remaining_bytes\":%u,\"projected_remaining_bytes\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"retry_count\":%u,\"stall_count\":%u,\"requeue_count\":%u,\"queue_depth_before\":%u,\"queue_depth_after\":%u,\"remaining_retry_budget\":%u,\"remaining_requeue_budget\":%u,\"backoff_ticks\":%u,\"completion_cookie\":%llu,\"completion_status\":%u,\"completion_count\":%u,\"deferred_count\":%u,\"failure_count\":%u,\"remaining_completion_budget\":%u,\"notify_mask\":%u,\"matched_notify_mask\":%u,\"notify_status\":%u,\"notify_count\":%u,\"deferred_notify_count\":%u,\"dropped_notify_count\":%u,\"remaining_notify_budget\":%u,\"notify_cookie\":%llu,\"flags\":%u}",
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
	       (unsigned long long)summary->notify_cookie, summary->flags);
}

int main(void)
{
	const unsigned long words[] = {
		(1UL << 0) | (1UL << 3) | (1UL << 7),
	};
	const unsigned long exhausted_words[] = {
		(1UL << 0) | (1UL << 2) | (1UL << 4),
	};
	struct zigux_chrdev_notify_view delivered =
		zigux_chrdev_notify_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 1,
			0xAAAA);
	struct zigux_chrdev_notify_view dropped =
		zigux_chrdev_notify_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS, 0,
			0xBBBB);
	struct zigux_chrdev_notify_view deferred =
		zigux_chrdev_notify_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0,
			1, 4, 2, 0x3333, 1, ZIGUX_CHRDEV_NOTIFY_MASK_DEFERRED, 0,
			0xCCCC);
	struct zigux_chrdev_notify_view failed =
		zigux_chrdev_notify_view_from_bits(exhausted_words, 240, 16, 5, 5, 2,
			ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_READ,
			ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5,
			1, 4, 2, 0x7777, 0, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1,
			0xDDDD);
	struct zigux_chrdev_notify_view unmatched =
		zigux_chrdev_notify_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0x1111, 1, ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE, 1,
			0xEEEE);
	struct zigux_chrdev_notify_view empty = {
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
	};
	struct zigux_chrdev_notify_summary delivered_summary =
		zigux_chrdev_notify_summarize(&delivered);
	struct zigux_chrdev_notify_summary dropped_summary =
		zigux_chrdev_notify_summarize(&dropped);
	struct zigux_chrdev_notify_summary deferred_summary =
		zigux_chrdev_notify_summarize(&deferred);
	struct zigux_chrdev_notify_summary failed_summary =
		zigux_chrdev_notify_summarize(&failed);
	struct zigux_chrdev_notify_summary unmatched_summary =
		zigux_chrdev_notify_summarize(&unmatched);
	struct zigux_chrdev_notify_summary empty_summary =
		zigux_chrdev_notify_summarize(&empty);

	printf("{\"constants\":{\"chrdev_notify_mask_success\":%u,"
	       "\"chrdev_notify_mask_deferred\":%u,"
	       "\"chrdev_notify_mask_failure\":%u,"
	       "\"chrdev_notify_flag_matched_notify\":%u,"
	       "\"chrdev_notify_flag_notify_planned\":%u,"
	       "\"chrdev_notify_index_none\":%u,"
	       "\"chrdev_notify_status_none\":%u,"
	       "\"chrdev_notify_status_delivered\":%u,"
	       "\"chrdev_notify_status_deferred\":%u,"
	       "\"chrdev_notify_status_dropped\":%u},"
	       "\"delivered\":{\"summary\":",
	       ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS,
	       ZIGUX_CHRDEV_NOTIFY_MASK_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE,
	       ZIGUX_CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY,
	       ZIGUX_CHRDEV_NOTIFY_FLAG_NOTIFY_PLANNED,
	       ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
	       ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
	       ZIGUX_CHRDEV_NOTIFY_STATUS_DELIVERED,
	       ZIGUX_CHRDEV_NOTIFY_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_NOTIFY_STATUS_DROPPED);
	print_summary(&delivered_summary);
	printf("},\"dropped\":{\"summary\":");
	print_summary(&dropped_summary);
	printf("},\"deferred\":{\"summary\":");
	print_summary(&deferred_summary);
	printf("},\"failed\":{\"summary\":");
	print_summary(&failed_summary);
	printf("},\"unmatched\":{\"summary\":");
	print_summary(&unmatched_summary);
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_notify_view_valid(&empty) ? "true" : "false");
	print_summary(&empty_summary);
	printf("}}\n");
	return 0;
}

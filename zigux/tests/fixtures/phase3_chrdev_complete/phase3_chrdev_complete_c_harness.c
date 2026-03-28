#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_complete_summary *summary)
{
	printf("{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"io_op\":%u,\"requested_bytes\":%u,\"start_offset\":%llu,\"next_offset\":%llu,\"initial_bytes_completed\":%u,\"final_bytes_completed\":%u,\"pass_count\":%u,\"issued_bytes\":%u,\"remaining_bytes\":%u,\"projected_remaining_bytes\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"retry_count\":%u,\"stall_count\":%u,\"requeue_count\":%u,\"queue_depth_before\":%u,\"queue_depth_after\":%u,\"remaining_retry_budget\":%u,\"remaining_requeue_budget\":%u,\"backoff_ticks\":%u,\"completion_cookie\":%llu,\"completion_status\":%u,\"completion_count\":%u,\"deferred_count\":%u,\"failure_count\":%u,\"remaining_completion_budget\":%u,\"flags\":%u}",
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
	       summary->remaining_completion_budget, summary->flags);
}

int main(void)
{
	const unsigned long words[] = {
		(1UL << 0) | (1UL << 3) | (1UL << 7),
	};
	const unsigned long exhausted_words[] = {
		(1UL << 0) | (1UL << 2) | (1UL << 4),
	};
	struct zigux_chrdev_complete_view complete =
		zigux_chrdev_complete_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0x1111, 1);
	struct zigux_chrdev_complete_view complete_deferred =
		zigux_chrdev_complete_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2, 0x2222, 0);
	struct zigux_chrdev_complete_view requeued =
		zigux_chrdev_complete_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0,
			1, 4, 2, 0x3333, 1);
	struct zigux_chrdev_complete_view delayed =
		zigux_chrdev_complete_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5,
			2, 4, 3, 0x4444, 2);
	struct zigux_chrdev_complete_view saturated =
		zigux_chrdev_complete_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0,
			4, 4, 2, 0x5555, 1);
	struct zigux_chrdev_complete_view denied =
		zigux_chrdev_complete_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_READ | ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5,
			1, 4, 2, 0x6666, 1);
	struct zigux_chrdev_complete_view exhausted =
		zigux_chrdev_complete_view_from_bits(exhausted_words, 240, 16, 5, 5, 2,
			ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_READ,
			ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5,
			1, 4, 2, 0x7777, 0);
	struct zigux_chrdev_complete_view empty = {
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
		.completion_cookie = 0x8888,
		.completion_budget = 0,
		.reserved = 0,
	};
	struct zigux_chrdev_complete_summary complete_summary =
		zigux_chrdev_complete_summarize(&complete);
	struct zigux_chrdev_complete_summary complete_deferred_summary =
		zigux_chrdev_complete_summarize(&complete_deferred);
	struct zigux_chrdev_complete_summary requeued_summary =
		zigux_chrdev_complete_summarize(&requeued);
	struct zigux_chrdev_complete_summary delayed_summary =
		zigux_chrdev_complete_summarize(&delayed);
	struct zigux_chrdev_complete_summary saturated_summary =
		zigux_chrdev_complete_summarize(&saturated);
	struct zigux_chrdev_complete_summary denied_summary =
		zigux_chrdev_complete_summarize(&denied);
	struct zigux_chrdev_complete_summary exhausted_summary =
		zigux_chrdev_complete_summarize(&exhausted);
	struct zigux_chrdev_complete_summary empty_summary =
		zigux_chrdev_complete_summarize(&empty);

	printf("{\"constants\":{\"chrdev_complete_flag_truncated\":%u,"
	       "\"chrdev_complete_flag_found\":%u,"
	       "\"chrdev_complete_flag_exhausted\":%u,"
	       "\"chrdev_complete_flag_hit\":%u,"
	       "\"chrdev_complete_flag_permitted\":%u,"
	       "\"chrdev_complete_flag_denied\":%u,"
	       "\"chrdev_complete_flag_routable\":%u,"
	       "\"chrdev_complete_flag_blocked\":%u,"
	       "\"chrdev_complete_flag_dispatchable\":%u,"
	       "\"chrdev_complete_flag_resumed\":%u,"
	       "\"chrdev_complete_flag_continuable\":%u,"
	       "\"chrdev_complete_flag_completes\":%u,"
	       "\"chrdev_complete_flag_progressed\":%u,"
	       "\"chrdev_complete_flag_stalled\":%u,"
	       "\"chrdev_complete_flag_complete_ok\":%u,"
	       "\"chrdev_complete_flag_retryable\":%u,"
	       "\"chrdev_complete_flag_retry_planned\":%u,"
	       "\"chrdev_complete_flag_retry_exhausted\":%u,"
	       "\"chrdev_complete_flag_backoff_applied\":%u,"
	       "\"chrdev_complete_flag_fails\":%u,"
	       "\"chrdev_complete_flag_requeueable\":%u,"
	       "\"chrdev_complete_flag_requeue_planned\":%u,"
	       "\"chrdev_complete_flag_delayed\":%u,"
	       "\"chrdev_complete_flag_saturated\":%u,"
	       "\"chrdev_complete_flag_dropped\":%u,"
	       "\"chrdev_complete_flag_complete\":%u,"
	       "\"chrdev_complete_flag_completion_planned\":%u,"
	       "\"chrdev_complete_flag_deferred_completion\":%u,"
	       "\"chrdev_complete_flag_failure_completion\":%u,"
	       "\"chrdev_complete_flag_finalized\":%u,"
	       "\"chrdev_complete_index_none\":%u,"
	       "\"chrdev_complete_status_none\":%u,"
	       "\"chrdev_complete_status_ok\":%u,"
	       "\"chrdev_complete_status_deferred\":%u,"
	       "\"chrdev_complete_status_failed\":%u},"
	       "\"complete\":{\"summary\":",
	       ZIGUX_CHRDEV_COMPLETE_FLAG_TRUNCATED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_FOUND,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_EXHAUSTED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_HIT,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_PERMITTED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_DENIED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_ROUTABLE,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_BLOCKED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_DISPATCHABLE,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_RESUMED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_CONTINUABLE,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETES,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_PROGRESSED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_STALLED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE_OK,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_RETRYABLE,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_RETRY_PLANNED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_RETRY_EXHAUSTED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_BACKOFF_APPLIED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_FAILS,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUEABLE,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_DELAYED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_SATURATED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_DROPPED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION,
	       ZIGUX_CHRDEV_COMPLETE_FLAG_FINALIZED,
	       ZIGUX_CHRDEV_COMPLETE_INDEX_NONE,
	       ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
	       ZIGUX_CHRDEV_COMPLETE_STATUS_OK,
	       ZIGUX_CHRDEV_COMPLETE_STATUS_DEFERRED,
	       ZIGUX_CHRDEV_COMPLETE_STATUS_FAILED);
	print_summary(&complete_summary);
	printf("},\"complete_deferred\":{\"summary\":");
	print_summary(&complete_deferred_summary);
	printf("},\"requeued\":{\"summary\":");
	print_summary(&requeued_summary);
	printf("},\"delayed\":{\"summary\":");
	print_summary(&delayed_summary);
	printf("},\"saturated\":{\"summary\":");
	print_summary(&saturated_summary);
	printf("},\"denied\":{\"summary\":");
	print_summary(&denied_summary);
	printf("},\"exhausted\":{\"summary\":");
	print_summary(&exhausted_summary);
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_complete_view_valid(&empty) ? "true" : "false");
	print_summary(&empty_summary);
	printf("}}\n");
	return 0;
}

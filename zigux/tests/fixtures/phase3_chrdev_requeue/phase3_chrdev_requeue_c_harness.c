#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_requeue_summary *summary)
{
	printf("{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"io_op\":%u,\"requested_bytes\":%u,\"start_offset\":%llu,\"next_offset\":%llu,\"initial_bytes_completed\":%u,\"final_bytes_completed\":%u,\"pass_count\":%u,\"issued_bytes\":%u,\"remaining_bytes\":%u,\"projected_remaining_bytes\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"retry_count\":%u,\"stall_count\":%u,\"requeue_count\":%u,\"queue_depth_before\":%u,\"queue_depth_after\":%u,\"remaining_retry_budget\":%u,\"remaining_requeue_budget\":%u,\"backoff_ticks\":%u,\"flags\":%u}",
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
	       summary->backoff_ticks, summary->flags);
}

int main(void)
{
	const unsigned long words[] = {
		(1UL << 0) | (1UL << 3) | (1UL << 7),
	};
	const unsigned long exhausted_words[] = {
		(1UL << 0) | (1UL << 2) | (1UL << 4),
	};
	struct zigux_chrdev_requeue_view complete =
		zigux_chrdev_requeue_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5,
			1, 4, 2);
	struct zigux_chrdev_requeue_view requeue_planned =
		zigux_chrdev_requeue_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0,
			1, 4, 2);
	struct zigux_chrdev_requeue_view delayed =
		zigux_chrdev_requeue_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5,
			2, 4, 3);
	struct zigux_chrdev_requeue_view saturated =
		zigux_chrdev_requeue_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 1, 1, 0,
			4, 4, 2);
	struct zigux_chrdev_requeue_view denied =
		zigux_chrdev_requeue_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_READ | ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5,
			1, 4, 2);
	struct zigux_chrdev_requeue_view exhausted =
		zigux_chrdev_requeue_view_from_bits(exhausted_words, 240, 16, 5, 5, 2,
			ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_READ,
			ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5,
			1, 4, 2);
	struct zigux_chrdev_requeue_view empty = {
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
		.reserved = 0,
	};
	struct zigux_chrdev_requeue_summary complete_summary =
		zigux_chrdev_requeue_summarize(&complete);
	struct zigux_chrdev_requeue_summary requeue_summary =
		zigux_chrdev_requeue_summarize(&requeue_planned);
	struct zigux_chrdev_requeue_summary delayed_summary =
		zigux_chrdev_requeue_summarize(&delayed);
	struct zigux_chrdev_requeue_summary saturated_summary =
		zigux_chrdev_requeue_summarize(&saturated);
	struct zigux_chrdev_requeue_summary denied_summary =
		zigux_chrdev_requeue_summarize(&denied);
	struct zigux_chrdev_requeue_summary exhausted_summary =
		zigux_chrdev_requeue_summarize(&exhausted);
	struct zigux_chrdev_requeue_summary empty_summary =
		zigux_chrdev_requeue_summarize(&empty);

	printf("{\"constants\":{\"chrdev_requeue_flag_truncated\":%u,"
	       "\"chrdev_requeue_flag_found\":%u,"
	       "\"chrdev_requeue_flag_exhausted\":%u,"
	       "\"chrdev_requeue_flag_hit\":%u,"
	       "\"chrdev_requeue_flag_permitted\":%u,"
	       "\"chrdev_requeue_flag_denied\":%u,"
	       "\"chrdev_requeue_flag_routable\":%u,"
	       "\"chrdev_requeue_flag_blocked\":%u,"
	       "\"chrdev_requeue_flag_dispatchable\":%u,"
	       "\"chrdev_requeue_flag_resumed\":%u,"
	       "\"chrdev_requeue_flag_continuable\":%u,"
	       "\"chrdev_requeue_flag_completes\":%u,"
	       "\"chrdev_requeue_flag_progressed\":%u,"
	       "\"chrdev_requeue_flag_stalled\":%u,"
	       "\"chrdev_requeue_flag_complete_ok\":%u,"
	       "\"chrdev_requeue_flag_retryable\":%u,"
	       "\"chrdev_requeue_flag_retry_planned\":%u,"
	       "\"chrdev_requeue_flag_retry_exhausted\":%u,"
	       "\"chrdev_requeue_flag_backoff_applied\":%u,"
	       "\"chrdev_requeue_flag_fails\":%u,"
	       "\"chrdev_requeue_flag_requeueable\":%u,"
	       "\"chrdev_requeue_flag_requeue_planned\":%u,"
	       "\"chrdev_requeue_flag_delayed\":%u,"
	       "\"chrdev_requeue_flag_saturated\":%u,"
	       "\"chrdev_requeue_flag_dropped\":%u,"
	       "\"chrdev_requeue_flag_complete\":%u,"
	       "\"chrdev_requeue_index_none\":%u},"
	       "\"complete\":{\"summary\":",
	       ZIGUX_CHRDEV_REQUEUE_FLAG_TRUNCATED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_FOUND,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_EXHAUSTED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_HIT,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_PERMITTED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_DENIED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_ROUTABLE,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_BLOCKED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_DISPATCHABLE,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_RESUMED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_CONTINUABLE,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETES,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_PROGRESSED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_STALLED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETE_OK,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_RETRYABLE,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_RETRY_PLANNED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_RETRY_EXHAUSTED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_BACKOFF_APPLIED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_FAILS,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_REQUEUEABLE,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_DELAYED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_SATURATED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_DROPPED,
	       ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETE,
	       ZIGUX_CHRDEV_REQUEUE_INDEX_NONE);
	print_summary(&complete_summary);
	printf("},\"requeue_planned\":{\"summary\":");
	print_summary(&requeue_summary);
	printf("},\"delayed\":{\"summary\":");
	print_summary(&delayed_summary);
	printf("},\"saturated\":{\"summary\":");
	print_summary(&saturated_summary);
	printf("},\"denied\":{\"summary\":");
	print_summary(&denied_summary);
	printf("},\"exhausted\":{\"summary\":");
	print_summary(&exhausted_summary);
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_requeue_view_valid(&empty) ? "true" : "false");
	print_summary(&empty_summary);
	printf("}}\n");
	return 0;
}

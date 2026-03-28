#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(const struct zigux_chrdev_retry_summary *summary)
{
	printf("{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"io_op\":%u,\"requested_bytes\":%u,\"start_offset\":%llu,\"next_offset\":%llu,\"initial_bytes_completed\":%u,\"final_bytes_completed\":%u,\"pass_count\":%u,\"issued_bytes\":%u,\"remaining_bytes\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"retry_count\":%u,\"stall_count\":%u,\"remaining_retry_budget\":%u,\"backoff_ticks\":%u,\"flags\":%u}",
	       summary->major, summary->target_minor, summary->selected_count,
	       summary->resolved_index, summary->resolved_dev, summary->granted_mode,
	       summary->io_op, summary->requested_bytes,
	       (unsigned long long)summary->start_offset,
	       (unsigned long long)summary->next_offset,
	       summary->initial_bytes_completed, summary->final_bytes_completed,
	       summary->pass_count, summary->issued_bytes, summary->remaining_bytes,
	       summary->entry_ops, summary->data_ops, summary->exit_ops,
	       summary->blocked_ops, summary->retry_count, summary->stall_count,
	       summary->remaining_retry_budget, summary->backoff_ticks,
	       summary->flags);
}

int main(void)
{
	const unsigned long words[] = {
		(1UL << 0) | (1UL << 3) | (1UL << 7),
	};
	const unsigned long exhausted_words[] = {
		(1UL << 0) | (1UL << 2) | (1UL << 4),
	};
	struct zigux_chrdev_retry_view complete =
		zigux_chrdev_retry_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 3, 2, 1, 5);
	struct zigux_chrdev_retry_view continuable =
		zigux_chrdev_retry_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 20, 8, 1024, 4, 1, 1, 2, 1, 0);
	struct zigux_chrdev_retry_view stalled =
		zigux_chrdev_retry_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 2048, 4, 2, 3, 2, 1, 5);
	struct zigux_chrdev_retry_view budget_exhausted =
		zigux_chrdev_retry_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 36, 8, 1024, 4, 1, 1, 2, 1, 0);
	struct zigux_chrdev_retry_view denied =
		zigux_chrdev_retry_view_from_bits(words, 240, 32, 8, 8, 2,
			ZIGUX_IDA_POLICY_LAST_FIT, 37,
			ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE,
			ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_READ | ZIGUX_CHRDEV_FOP_WRITE,
			ZIGUX_CHRDEV_IO_OP_WRITE, 12, 8, 512, 0, 2, 2, 2, 1, 5);
	struct zigux_chrdev_retry_view exhausted =
		zigux_chrdev_retry_view_from_bits(exhausted_words, 240, 16, 5, 5, 2,
			ZIGUX_IDA_POLICY_FIRST_FIT, 20, ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_MODE_READ,
			ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
				ZIGUX_CHRDEV_FOP_READ,
			ZIGUX_CHRDEV_IO_OP_READ, 12, 32, 0, 0, 2, 2, 2, 1, 5);
	struct zigux_chrdev_retry_view empty = {
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
		.reserved = 0,
	};
	struct zigux_chrdev_retry_summary complete_summary =
		zigux_chrdev_retry_summarize(&complete);
	struct zigux_chrdev_retry_summary continuable_summary =
		zigux_chrdev_retry_summarize(&continuable);
	struct zigux_chrdev_retry_summary stalled_summary =
		zigux_chrdev_retry_summarize(&stalled);
	struct zigux_chrdev_retry_summary budget_summary =
		zigux_chrdev_retry_summarize(&budget_exhausted);
	struct zigux_chrdev_retry_summary denied_summary =
		zigux_chrdev_retry_summarize(&denied);
	struct zigux_chrdev_retry_summary exhausted_summary =
		zigux_chrdev_retry_summarize(&exhausted);
	struct zigux_chrdev_retry_summary empty_summary =
		zigux_chrdev_retry_summarize(&empty);

	printf("{\"constants\":{\"chrdev_retry_flag_truncated\":%u,"
	       "\"chrdev_retry_flag_found\":%u,"
	       "\"chrdev_retry_flag_exhausted\":%u,"
	       "\"chrdev_retry_flag_hit\":%u,"
	       "\"chrdev_retry_flag_permitted\":%u,"
	       "\"chrdev_retry_flag_denied\":%u,"
	       "\"chrdev_retry_flag_routable\":%u,"
	       "\"chrdev_retry_flag_blocked\":%u,"
	       "\"chrdev_retry_flag_dispatchable\":%u,"
	       "\"chrdev_retry_flag_resumed\":%u,"
	       "\"chrdev_retry_flag_continuable\":%u,"
	       "\"chrdev_retry_flag_completes\":%u,"
	       "\"chrdev_retry_flag_progressed\":%u,"
	       "\"chrdev_retry_flag_stalled\":%u,"
	       "\"chrdev_retry_flag_complete_ok\":%u,"
	       "\"chrdev_retry_flag_retryable\":%u,"
	       "\"chrdev_retry_flag_retry_planned\":%u,"
	       "\"chrdev_retry_flag_retry_exhausted\":%u,"
	       "\"chrdev_retry_flag_backoff_applied\":%u,"
	       "\"chrdev_retry_flag_fails\":%u,"
	       "\"chrdev_retry_index_none\":%u},"
	       "\"complete\":{\"summary\":",
	       ZIGUX_CHRDEV_RETRY_FLAG_TRUNCATED,
	       ZIGUX_CHRDEV_RETRY_FLAG_FOUND,
	       ZIGUX_CHRDEV_RETRY_FLAG_EXHAUSTED,
	       ZIGUX_CHRDEV_RETRY_FLAG_HIT,
	       ZIGUX_CHRDEV_RETRY_FLAG_PERMITTED,
	       ZIGUX_CHRDEV_RETRY_FLAG_DENIED,
	       ZIGUX_CHRDEV_RETRY_FLAG_ROUTABLE,
	       ZIGUX_CHRDEV_RETRY_FLAG_BLOCKED,
	       ZIGUX_CHRDEV_RETRY_FLAG_DISPATCHABLE,
	       ZIGUX_CHRDEV_RETRY_FLAG_RESUMED,
	       ZIGUX_CHRDEV_RETRY_FLAG_CONTINUABLE,
	       ZIGUX_CHRDEV_RETRY_FLAG_COMPLETES,
	       ZIGUX_CHRDEV_RETRY_FLAG_PROGRESSED,
	       ZIGUX_CHRDEV_RETRY_FLAG_STALLED,
	       ZIGUX_CHRDEV_RETRY_FLAG_COMPLETE_OK,
	       ZIGUX_CHRDEV_RETRY_FLAG_RETRYABLE,
	       ZIGUX_CHRDEV_RETRY_FLAG_RETRY_PLANNED,
	       ZIGUX_CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED,
	       ZIGUX_CHRDEV_RETRY_FLAG_BACKOFF_APPLIED,
	       ZIGUX_CHRDEV_RETRY_FLAG_FAILS,
	       ZIGUX_CHRDEV_RETRY_INDEX_NONE);
	print_summary(&complete_summary);
	printf("},\"continuable\":{\"summary\":");
	print_summary(&continuable_summary);
	printf("},\"stalled\":{\"summary\":");
	print_summary(&stalled_summary);
	printf("},\"budget_exhausted\":{\"summary\":");
	print_summary(&budget_summary);
	printf("},\"denied\":{\"summary\":");
	print_summary(&denied_summary);
	printf("},\"exhausted\":{\"summary\":");
	print_summary(&exhausted_summary);
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_retry_view_valid(&empty) ? "true" : "false");
	print_summary(&empty_summary);
	printf("}}\n");
	return 0;
}

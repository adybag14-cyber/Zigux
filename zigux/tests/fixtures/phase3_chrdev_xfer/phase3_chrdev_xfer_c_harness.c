#include <stdbool.h>
#include <stdio.h>

#include <linux/zigux.h>

static void write_summary(FILE *out, const struct zigux_chrdev_xfer_summary *summary)
{
	fprintf(out,
		"{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"io_op\":%u,\"requested_bytes\":%u,\"start_offset\":%llu,\"next_offset\":%llu,\"bytes_completed\":%u,\"requested_remaining\":%u,\"segment_count\":%u,\"first_chunk_bytes\":%u,\"final_chunk_bytes\":%u,\"issued_bytes\":%u,\"remaining_bytes\":%u,\"entry_ops\":%u,\"data_ops\":%u,\"exit_ops\":%u,\"blocked_ops\":%u,\"flags\":%u}",
		summary->major,
		summary->target_minor,
		summary->selected_count,
		summary->resolved_index,
		summary->resolved_dev,
		summary->granted_mode,
		summary->io_op,
		summary->requested_bytes,
		(unsigned long long)summary->start_offset,
		(unsigned long long)summary->next_offset,
		summary->bytes_completed,
		summary->requested_remaining,
		summary->segment_count,
		summary->first_chunk_bytes,
		summary->final_chunk_bytes,
		summary->issued_bytes,
		summary->remaining_bytes,
		summary->entry_ops,
		summary->data_ops,
		summary->exit_ops,
		summary->blocked_ops,
		summary->flags);
}

int main(void)
{
	const unsigned long words[] = {(1UL << 0) | (1UL << 3) | (1UL << 7)};
	const struct zigux_chrdev_xfer_view continuable_view =
		zigux_chrdev_xfer_view_from_bits(words, 240, 32, 8, 6, 2,
						 ZIGUX_IDA_POLICY_FIRST_FIT,
						 34,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_READ |
							 ZIGUX_CHRDEV_FOP_WRITE,
						 ZIGUX_CHRDEV_IO_OP_READ,
						 16, 8, 4096, 0, 1);
	const struct zigux_chrdev_xfer_view complete_view =
		zigux_chrdev_xfer_view_from_bits(words, 240, 32, 8, 8, 2,
						 ZIGUX_IDA_POLICY_LAST_FIT,
						 37,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_WRITE,
						 ZIGUX_CHRDEV_IO_OP_WRITE,
						 20, 8, 1024, 4, 3);
	const struct zigux_chrdev_xfer_view blocked_view =
		zigux_chrdev_xfer_view_from_bits(words, 240, 32, 8, 8, 2,
						 ZIGUX_IDA_POLICY_LAST_FIT,
						 37,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_WRITE,
						 ZIGUX_CHRDEV_IO_OP_READ,
						 12, 32, 2048, 4, 2);
	const struct zigux_chrdev_xfer_view denied_view =
		zigux_chrdev_xfer_view_from_bits(words, 240, 32, 8, 8, 2,
						 ZIGUX_IDA_POLICY_LAST_FIT,
						 37,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_READ |
							 ZIGUX_CHRDEV_FOP_WRITE,
						 ZIGUX_CHRDEV_IO_OP_WRITE,
						 12, 8, 512, 0, 2);
	const unsigned long exhausted_words[] = {(1UL << 0) | (1UL << 2) | (1UL << 4)};
	const struct zigux_chrdev_xfer_view exhausted_view =
		zigux_chrdev_xfer_view_from_bits(exhausted_words, 240, 16, 5, 5, 2,
						 ZIGUX_IDA_POLICY_FIRST_FIT,
						 20, ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_READ,
						 ZIGUX_CHRDEV_IO_OP_READ,
						 12, 32, 0, 0, 2);
	const struct zigux_chrdev_xfer_view empty_view = {
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
		.reserved = 0,
	};

	fputs("{\"constants\":{\"chrdev_xfer_flag_truncated\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_TRUNCATED);
	fputs(",\"chrdev_xfer_flag_found\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_FOUND);
	fputs(",\"chrdev_xfer_flag_exhausted\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_EXHAUSTED);
	fputs(",\"chrdev_xfer_flag_hit\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_HIT);
	fputs(",\"chrdev_xfer_flag_permitted\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_PERMITTED);
	fputs(",\"chrdev_xfer_flag_denied\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_DENIED);
	fputs(",\"chrdev_xfer_flag_routable\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_ROUTABLE);
	fputs(",\"chrdev_xfer_flag_blocked\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_BLOCKED);
	fputs(",\"chrdev_xfer_flag_dispatchable\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_DISPATCHABLE);
	fputs(",\"chrdev_xfer_flag_resumed\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_RESUMED);
	fputs(",\"chrdev_xfer_flag_continuable\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_CONTINUABLE);
	fputs(",\"chrdev_xfer_flag_completes\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_FLAG_COMPLETES);
	fputs(",\"chrdev_xfer_index_none\":", stdout);
	fprintf(stdout, "%u", ZIGUX_CHRDEV_XFER_INDEX_NONE);

	fputs("},\"continuable\":{\"summary\":", stdout);
	{
		const struct zigux_chrdev_xfer_summary summary =
			zigux_chrdev_xfer_summarize(&continuable_view);
		write_summary(stdout, &summary);
	}

	fputs("},\"complete\":{\"summary\":", stdout);
	{
		const struct zigux_chrdev_xfer_summary summary =
			zigux_chrdev_xfer_summarize(&complete_view);
		write_summary(stdout, &summary);
	}

	fputs("},\"blocked\":{\"summary\":", stdout);
	{
		const struct zigux_chrdev_xfer_summary summary =
			zigux_chrdev_xfer_summarize(&blocked_view);
		write_summary(stdout, &summary);
	}

	fputs("},\"denied\":{\"summary\":", stdout);
	{
		const struct zigux_chrdev_xfer_summary summary =
			zigux_chrdev_xfer_summarize(&denied_view);
		write_summary(stdout, &summary);
	}

	fputs("},\"exhausted\":{\"summary\":", stdout);
	{
		const struct zigux_chrdev_xfer_summary summary =
			zigux_chrdev_xfer_summarize(&exhausted_view);
		write_summary(stdout, &summary);
	}

	fputs("},\"empty\":{\"is_valid\":", stdout);
	fputs(zigux_chrdev_xfer_view_valid(&empty_view) ? "true" : "false",
	      stdout);
	fputs(",\"summary\":", stdout);
	{
		const struct zigux_chrdev_xfer_summary summary =
			zigux_chrdev_xfer_summarize(&empty_view);
		write_summary(stdout, &summary);
	}

	fputs("}}\n", stdout);
	return 0;
}

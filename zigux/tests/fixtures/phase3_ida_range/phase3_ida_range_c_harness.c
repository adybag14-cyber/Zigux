#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_ida_range_summary summary)
{
	printf("{\"scanned_count\":%u,\"request_count\":%u,\"candidate_range_count\":%u,\"first_range_id\":%u,\"last_range_id\":%u,\"flags\":%u}",
	       summary.scanned_count,
	       summary.request_count,
	       summary.candidate_range_count,
	       summary.first_range_id,
	       summary.last_range_id,
	       summary.flags);
}

int main(void)
{
	unsigned long bits[] = {
		(1UL << 0) | (1UL << 3) | (1UL << 7),
	};
	unsigned long exhausted_bits[] = {
		(1UL << 0) | (1UL << 2) | (1UL << 4),
	};
	struct zigux_ida_range_view truncated = zigux_ida_range_view_from_bits(bits, 100, 8, 6, 2, 4);
	struct zigux_ida_range_view capped = zigux_ida_range_view_from_bits(bits, 100, 8, 8, 2, 2);
	struct zigux_ida_range_view exhausted = zigux_ida_range_view_from_bits(exhausted_bits, 40, 5, 5, 2, 4);
	struct zigux_ida_range_view empty = { .bits_addr = 0, .base_id = 32, .nbits = 0, .max_scan = 0, .request_count = 1, .max_ranges = 4, .reserved = 0 };

	printf("{\"constants\":{\"ida_range_flag_truncated\":%u,\"ida_range_flag_found\":%u,\"ida_range_flag_exhausted\":%u},",
	       ZIGUX_IDA_RANGE_FLAG_TRUNCATED,
	       ZIGUX_IDA_RANGE_FLAG_FOUND,
	       ZIGUX_IDA_RANGE_FLAG_EXHAUSTED);
	printf("\"truncated\":{\"summary\":");
	print_summary(zigux_ida_range_summarize(&truncated));
	printf("},\"capped\":{\"summary\":");
	print_summary(zigux_ida_range_summarize(&capped));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_ida_range_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_ida_range_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_ida_range_summarize(&empty));
	printf("}}\n");
	return 0;
}

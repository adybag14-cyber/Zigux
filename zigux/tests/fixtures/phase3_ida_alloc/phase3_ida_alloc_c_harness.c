#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_ida_alloc_summary summary)
{
	printf("{\"scanned_count\":%u,\"request_count\":%u,\"first_fit_id\":%u,\"longest_free_run\":%u,\"flags\":%u}",
	       summary.scanned_count,
	       summary.request_count,
	       summary.first_fit_id,
	       summary.longest_free_run,
	       summary.flags);
}

int main(void)
{
	unsigned long truncated_bits[] = {
		(1UL << 0) | (1UL << 3) | (1UL << 7),
	};
	unsigned long exhausted_bits[] = {
		(1UL << 0) | (1UL << 2) | (1UL << 4),
	};
	struct zigux_ida_alloc_view truncated = zigux_ida_alloc_view_from_bits(truncated_bits, 100, 8, 6, 2);
	struct zigux_ida_alloc_view full = zigux_ida_alloc_view_from_bits(truncated_bits, 100, 8, 8, 2);
	struct zigux_ida_alloc_view exhausted = zigux_ida_alloc_view_from_bits(exhausted_bits, 40, 5, 5, 2);
	struct zigux_ida_alloc_view empty = { .bits_addr = 0, .base_id = 32, .nbits = 0, .max_scan = 0, .request_count = 1, .reserved = 0 };

	printf("{\"constants\":{\"ida_alloc_flag_truncated\":%u,\"ida_alloc_flag_found\":%u,\"ida_alloc_flag_exhausted\":%u},",
	       ZIGUX_IDA_ALLOC_FLAG_TRUNCATED,
	       ZIGUX_IDA_ALLOC_FLAG_FOUND,
	       ZIGUX_IDA_ALLOC_FLAG_EXHAUSTED);
	printf("\"truncated\":{\"summary\":");
	print_summary(zigux_ida_alloc_summarize(&truncated));
	printf("},\"full\":{\"summary\":");
	print_summary(zigux_ida_alloc_summarize(&full));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_ida_alloc_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_ida_alloc_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_ida_alloc_summarize(&empty));
	printf("}}\n");
	return 0;
}

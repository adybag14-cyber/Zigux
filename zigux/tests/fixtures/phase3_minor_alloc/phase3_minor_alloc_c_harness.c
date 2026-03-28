#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_minor_alloc_summary summary)
{
	printf("{\"major\":%u,\"scanned_count\":%u,\"request_count\":%u,\"selected_minor_start\":%u,\"selected_minor_end\":%u,\"alternate_minor_start\":%u,\"longest_free_run\":%u,\"flags\":%u}",
	       summary.major,
	       summary.scanned_count,
	       summary.request_count,
	       summary.selected_minor_start,
	       summary.selected_minor_end,
	       summary.alternate_minor_start,
	       summary.longest_free_run,
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
	struct zigux_minor_alloc_view first_fit = zigux_minor_alloc_view_from_bits(bits, 240, 32, 8, 6, 2, ZIGUX_IDA_POLICY_FIRST_FIT);
	struct zigux_minor_alloc_view last_fit = zigux_minor_alloc_view_from_bits(bits, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT);
	struct zigux_minor_alloc_view exhausted = zigux_minor_alloc_view_from_bits(exhausted_bits, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT);
	struct zigux_minor_alloc_view empty = { .bits_addr = 0, .major = 240, .first_minor = 0, .minor_count = 0, .max_scan = 0, .request_count = 1, .policy = ZIGUX_IDA_POLICY_FIRST_FIT, .reserved = 0 };

	printf("{\"constants\":{\"minor_alloc_flag_truncated\":%u,\"minor_alloc_flag_found\":%u,\"minor_alloc_flag_exhausted\":%u,\"ida_policy_first_fit\":%u,\"ida_policy_last_fit\":%u},",
	       ZIGUX_MINOR_ALLOC_FLAG_TRUNCATED,
	       ZIGUX_MINOR_ALLOC_FLAG_FOUND,
	       ZIGUX_MINOR_ALLOC_FLAG_EXHAUSTED,
	       ZIGUX_IDA_POLICY_FIRST_FIT,
	       ZIGUX_IDA_POLICY_LAST_FIT);
	printf("\"first_fit\":{\"summary\":");
	print_summary(zigux_minor_alloc_summarize(&first_fit));
	printf("},\"last_fit\":{\"summary\":");
	print_summary(zigux_minor_alloc_summarize(&last_fit));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_minor_alloc_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_minor_alloc_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_minor_alloc_summarize(&empty));
	printf("}}\n");
	return 0;
}

#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_ida_policy_summary summary)
{
	printf("{\"scanned_count\":%u,\"request_count\":%u,\"selected_fit_id\":%u,\"alternate_fit_id\":%u,\"longest_free_run\":%u,\"flags\":%u}",
	       summary.scanned_count,
	       summary.request_count,
	       summary.selected_fit_id,
	       summary.alternate_fit_id,
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
	struct zigux_ida_policy_view first_fit = zigux_ida_policy_view_from_bits(bits, 100, 8, 6, 2, ZIGUX_IDA_POLICY_FIRST_FIT);
	struct zigux_ida_policy_view last_fit = zigux_ida_policy_view_from_bits(bits, 100, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT);
	struct zigux_ida_policy_view exhausted = zigux_ida_policy_view_from_bits(exhausted_bits, 40, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT);
	struct zigux_ida_policy_view empty = { .bits_addr = 0, .base_id = 32, .nbits = 0, .max_scan = 0, .request_count = 1, .policy = ZIGUX_IDA_POLICY_FIRST_FIT, .reserved = 0 };

	printf("{\"constants\":{\"ida_policy_first_fit\":%u,\"ida_policy_last_fit\":%u,\"ida_policy_flag_truncated\":%u,\"ida_policy_flag_found\":%u,\"ida_policy_flag_exhausted\":%u},",
	       ZIGUX_IDA_POLICY_FIRST_FIT,
	       ZIGUX_IDA_POLICY_LAST_FIT,
	       ZIGUX_IDA_POLICY_FLAG_TRUNCATED,
	       ZIGUX_IDA_POLICY_FLAG_FOUND,
	       ZIGUX_IDA_POLICY_FLAG_EXHAUSTED);
	printf("\"first_fit\":{\"summary\":");
	print_summary(zigux_ida_policy_summarize(&first_fit));
	printf("},\"last_fit\":{\"summary\":");
	print_summary(zigux_ida_policy_summarize(&last_fit));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_ida_policy_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_ida_policy_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_ida_policy_summarize(&empty));
	printf("}}\n");
	return 0;
}

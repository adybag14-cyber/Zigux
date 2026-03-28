#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_dev_region_summary summary)
{
	printf("{\"major\":%u,\"scanned_count\":%u,\"request_count\":%u,\"selected_minor_start\":%u,\"selected_minor_end\":%u,\"first_dev\":%u,\"last_dev\":%u,\"flags\":%u}",
	       summary.major,
	       summary.scanned_count,
	       summary.request_count,
	       summary.selected_minor_start,
	       summary.selected_minor_end,
	       summary.first_dev,
	       summary.last_dev,
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
	struct zigux_dev_region_view first_fit = zigux_dev_region_view_from_bits(bits, 240, 32, 8, 6, 2, ZIGUX_IDA_POLICY_FIRST_FIT);
	struct zigux_dev_region_view last_fit = zigux_dev_region_view_from_bits(bits, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT);
	struct zigux_dev_region_view exhausted = zigux_dev_region_view_from_bits(exhausted_bits, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT);
	struct zigux_dev_region_view empty = { .bits_addr = 0, .major = 240, .first_minor = 0, .minor_count = 0, .max_scan = 0, .request_count = 1, .policy = ZIGUX_IDA_POLICY_FIRST_FIT, .reserved = 0 };

	printf("{\"constants\":{\"dev_minor_bits\":%u,\"dev_minor_mask\":%u,\"dev_region_flag_truncated\":%u,\"dev_region_flag_found\":%u,\"dev_region_flag_exhausted\":%u},",
	       ZIGUX_DEV_MINOR_BITS,
	       ZIGUX_DEV_MINOR_MASK,
	       ZIGUX_DEV_REGION_FLAG_TRUNCATED,
	       ZIGUX_DEV_REGION_FLAG_FOUND,
	       ZIGUX_DEV_REGION_FLAG_EXHAUSTED);
	printf("\"first_fit\":{\"summary\":");
	print_summary(zigux_dev_region_summarize(&first_fit));
	printf("},\"last_fit\":{\"summary\":");
	print_summary(zigux_dev_region_summarize(&last_fit));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_dev_region_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_dev_region_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_dev_region_summarize(&empty));
	printf("}}\n");
	return 0;
}

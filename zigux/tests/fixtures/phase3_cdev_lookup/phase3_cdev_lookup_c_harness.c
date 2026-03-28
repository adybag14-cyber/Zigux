#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_cdev_lookup_summary summary)
{
	printf("{\"major\":%u,\"scanned_count\":%u,\"request_count\":%u,\"selected_count\":%u,\"first_minor\":%u,\"target_minor\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"flags\":%u}",
	       summary.major,
	       summary.scanned_count,
	       summary.request_count,
	       summary.selected_count,
	       summary.first_minor,
	       summary.target_minor,
	       summary.resolved_index,
	       summary.resolved_dev,
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
	struct zigux_cdev_lookup_view hit = zigux_cdev_lookup_view_from_bits(bits, 240, 32, 8, 6, 2, ZIGUX_IDA_POLICY_FIRST_FIT, 34);
	struct zigux_cdev_lookup_view miss = zigux_cdev_lookup_view_from_bits(bits, 240, 32, 8, 8, 2, ZIGUX_IDA_POLICY_LAST_FIT, 35);
	struct zigux_cdev_lookup_view exhausted = zigux_cdev_lookup_view_from_bits(exhausted_bits, 240, 16, 5, 5, 2, ZIGUX_IDA_POLICY_FIRST_FIT, 20);
	struct zigux_cdev_lookup_view empty = { .bits_addr = 0, .major = 240, .first_minor = 0, .minor_count = 0, .max_scan = 0, .request_count = 1, .policy = ZIGUX_IDA_POLICY_FIRST_FIT, .target_minor = 0, .reserved = 0 };

	printf("{\"constants\":{\"cdev_lookup_flag_truncated\":%u,\"cdev_lookup_flag_found\":%u,\"cdev_lookup_flag_exhausted\":%u,\"cdev_lookup_flag_hit\":%u,\"cdev_lookup_index_none\":%u},",
	       ZIGUX_CDEV_LOOKUP_FLAG_TRUNCATED,
	       ZIGUX_CDEV_LOOKUP_FLAG_FOUND,
	       ZIGUX_CDEV_LOOKUP_FLAG_EXHAUSTED,
	       ZIGUX_CDEV_LOOKUP_FLAG_HIT,
	       ZIGUX_CDEV_LOOKUP_INDEX_NONE);
	printf("\"hit\":{\"summary\":");
	print_summary(zigux_cdev_lookup_summarize(&hit));
	printf("},\"miss\":{\"summary\":");
	print_summary(zigux_cdev_lookup_summarize(&miss));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_cdev_lookup_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_cdev_lookup_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_cdev_lookup_summarize(&empty));
	printf("}}\n");
	return 0;
}

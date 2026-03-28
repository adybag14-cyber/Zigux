#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_chrdev_open_summary summary)
{
	printf("{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"requested_mode\":%u,\"supported_mode\":%u,\"granted_mode\":%u,\"denied_mode\":%u,\"flags\":%u}",
	       summary.major,
	       summary.target_minor,
	       summary.selected_count,
	       summary.resolved_index,
	       summary.resolved_dev,
	       summary.requested_mode,
	       summary.supported_mode,
	       summary.granted_mode,
	       summary.denied_mode,
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
	struct zigux_chrdev_open_view permitted =
		zigux_chrdev_open_view_from_bits(bits, 240, 32, 8, 6, 2,
						 ZIGUX_IDA_POLICY_FIRST_FIT, 34,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE);
	struct zigux_chrdev_open_view denied =
		zigux_chrdev_open_view_from_bits(bits, 240, 32, 8, 8, 2,
						 ZIGUX_IDA_POLICY_LAST_FIT, 37,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ);
	struct zigux_chrdev_open_view miss =
		zigux_chrdev_open_view_from_bits(bits, 240, 32, 8, 8, 2,
						 ZIGUX_IDA_POLICY_LAST_FIT, 35,
						 ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_MODE_READ);
	struct zigux_chrdev_open_view exhausted =
		zigux_chrdev_open_view_from_bits(exhausted_bits, 240, 16, 5, 5, 2,
						 ZIGUX_IDA_POLICY_FIRST_FIT, 20,
						 ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_MODE_READ);
	struct zigux_chrdev_open_view empty = {
		.bits_addr = 0,
		.major = 240,
		.first_minor = 0,
		.minor_count = 0,
		.max_scan = 0,
		.request_count = 1,
		.policy = ZIGUX_IDA_POLICY_FIRST_FIT,
		.target_minor = 0,
		.requested_mode = ZIGUX_CHRDEV_MODE_READ,
		.supported_mode = ZIGUX_CHRDEV_MODE_READ,
		.reserved = 0,
	};

	printf("{\"constants\":{\"chrdev_mode_read\":%u,\"chrdev_mode_write\":%u,\"chrdev_open_flag_truncated\":%u,\"chrdev_open_flag_found\":%u,\"chrdev_open_flag_exhausted\":%u,\"chrdev_open_flag_hit\":%u,\"chrdev_open_flag_permitted\":%u,\"chrdev_open_flag_denied\":%u,\"chrdev_open_index_none\":%u},",
	       ZIGUX_CHRDEV_MODE_READ,
	       ZIGUX_CHRDEV_MODE_WRITE,
	       ZIGUX_CHRDEV_OPEN_FLAG_TRUNCATED,
	       ZIGUX_CHRDEV_OPEN_FLAG_FOUND,
	       ZIGUX_CHRDEV_OPEN_FLAG_EXHAUSTED,
	       ZIGUX_CHRDEV_OPEN_FLAG_HIT,
	       ZIGUX_CHRDEV_OPEN_FLAG_PERMITTED,
	       ZIGUX_CHRDEV_OPEN_FLAG_DENIED,
	       ZIGUX_CHRDEV_OPEN_INDEX_NONE);
	printf("\"permitted\":{\"summary\":");
	print_summary(zigux_chrdev_open_summarize(&permitted));
	printf("},\"denied\":{\"summary\":");
	print_summary(zigux_chrdev_open_summarize(&denied));
	printf("},\"miss\":{\"summary\":");
	print_summary(zigux_chrdev_open_summarize(&miss));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_chrdev_open_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_open_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_chrdev_open_summarize(&empty));
	printf("}}\n");
	return 0;
}

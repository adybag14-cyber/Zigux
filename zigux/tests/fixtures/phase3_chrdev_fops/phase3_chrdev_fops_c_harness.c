#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_chrdev_fops_summary summary)
{
	printf("{\"major\":%u,\"target_minor\":%u,\"selected_count\":%u,\"resolved_index\":%u,\"resolved_dev\":%u,\"granted_mode\":%u,\"available_ops\":%u,\"required_ops\":%u,\"missing_ops\":%u,\"flags\":%u}",
	       summary.major,
	       summary.target_minor,
	       summary.selected_count,
	       summary.resolved_index,
	       summary.resolved_dev,
	       summary.granted_mode,
	       summary.available_ops,
	       summary.required_ops,
	       summary.missing_ops,
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
	struct zigux_chrdev_fops_view routable =
		zigux_chrdev_fops_view_from_bits(bits, 240, 32, 8, 6, 2,
						 ZIGUX_IDA_POLICY_FIRST_FIT, 34,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_READ |
							 ZIGUX_CHRDEV_FOP_WRITE);
	struct zigux_chrdev_fops_view missing_ops =
		zigux_chrdev_fops_view_from_bits(bits, 240, 32, 8, 8, 2,
						 ZIGUX_IDA_POLICY_LAST_FIT, 37,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_WRITE);
	struct zigux_chrdev_fops_view denied =
		zigux_chrdev_fops_view_from_bits(bits, 240, 32, 8, 8, 2,
						 ZIGUX_IDA_POLICY_LAST_FIT, 37,
						 ZIGUX_CHRDEV_MODE_READ |
							 ZIGUX_CHRDEV_MODE_WRITE,
						 ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_READ |
							 ZIGUX_CHRDEV_FOP_WRITE);
	struct zigux_chrdev_fops_view miss =
		zigux_chrdev_fops_view_from_bits(bits, 240, 32, 8, 8, 2,
						 ZIGUX_IDA_POLICY_LAST_FIT, 35,
						 ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_READ);
	struct zigux_chrdev_fops_view exhausted =
		zigux_chrdev_fops_view_from_bits(exhausted_bits, 240, 16, 5, 5,
						 2, ZIGUX_IDA_POLICY_FIRST_FIT,
						 20, ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_MODE_READ,
						 ZIGUX_CHRDEV_FOP_OPEN |
							 ZIGUX_CHRDEV_FOP_RELEASE |
							 ZIGUX_CHRDEV_FOP_READ);
	struct zigux_chrdev_fops_view empty = {
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
		.available_ops = ZIGUX_CHRDEV_FOP_OPEN |
				 ZIGUX_CHRDEV_FOP_RELEASE |
				 ZIGUX_CHRDEV_FOP_READ,
		.reserved = 0,
	};

	printf("{\"constants\":{\"chrdev_fop_open\":%u,\"chrdev_fop_release\":%u,\"chrdev_fop_read\":%u,\"chrdev_fop_write\":%u,\"chrdev_fops_flag_truncated\":%u,\"chrdev_fops_flag_found\":%u,\"chrdev_fops_flag_exhausted\":%u,\"chrdev_fops_flag_hit\":%u,\"chrdev_fops_flag_permitted\":%u,\"chrdev_fops_flag_denied\":%u,\"chrdev_fops_flag_routable\":%u,\"chrdev_fops_flag_missing_ops\":%u,\"chrdev_fops_index_none\":%u},",
	       ZIGUX_CHRDEV_FOP_OPEN,
	       ZIGUX_CHRDEV_FOP_RELEASE,
	       ZIGUX_CHRDEV_FOP_READ,
	       ZIGUX_CHRDEV_FOP_WRITE,
	       ZIGUX_CHRDEV_FOPS_FLAG_TRUNCATED,
	       ZIGUX_CHRDEV_FOPS_FLAG_FOUND,
	       ZIGUX_CHRDEV_FOPS_FLAG_EXHAUSTED,
	       ZIGUX_CHRDEV_FOPS_FLAG_HIT,
	       ZIGUX_CHRDEV_FOPS_FLAG_PERMITTED,
	       ZIGUX_CHRDEV_FOPS_FLAG_DENIED,
	       ZIGUX_CHRDEV_FOPS_FLAG_ROUTABLE,
	       ZIGUX_CHRDEV_FOPS_FLAG_MISSING_OPS,
	       ZIGUX_CHRDEV_FOPS_INDEX_NONE);
	printf("\"routable\":{\"summary\":");
	print_summary(zigux_chrdev_fops_summarize(&routable));
	printf("},\"missing_ops\":{\"summary\":");
	print_summary(zigux_chrdev_fops_summarize(&missing_ops));
	printf("},\"denied\":{\"summary\":");
	print_summary(zigux_chrdev_fops_summarize(&denied));
	printf("},\"miss\":{\"summary\":");
	print_summary(zigux_chrdev_fops_summarize(&miss));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_chrdev_fops_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":",
	       zigux_chrdev_fops_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_chrdev_fops_summarize(&empty));
	printf("}}\n");
	return 0;
}

#include <stdio.h>

#include <linux/zigux.h>

static void print_summary(struct zigux_ida_bitmap_summary summary)
{
	printf("{\"scanned_count\":%u,\"allocated_count\":%u,\"first_allocated_id\":%u,\"first_free_id\":%u,\"flags\":%u}",
	       summary.scanned_count,
	       summary.allocated_count,
	       summary.first_allocated_id,
	       summary.first_free_id,
	       summary.flags);
}

int main(void)
{
	unsigned long truncated_bits[] = {
		(1UL << 0) | (1UL << 2) | (1UL << 3) | (1UL << 5),
	};
	unsigned long exhausted_bits[] = {
		(1UL << 0) | (1UL << 1) | (1UL << 2),
	};
	struct zigux_ida_bitmap_view truncated = zigux_ida_bitmap_view_from_bits(truncated_bits, 100, 7, 6);
	struct zigux_ida_bitmap_view full = zigux_ida_bitmap_view_from_bits(truncated_bits, 100, 6, 6);
	struct zigux_ida_bitmap_view exhausted = zigux_ida_bitmap_view_from_bits(exhausted_bits, 40, 3, 3);
	struct zigux_ida_bitmap_view empty = { .bits_addr = 0, .base_id = 32, .nbits = 0, .max_scan = 0, .reserved = 0 };

	printf("{\"constants\":{\"ida_bitmap_flag_truncated\":%u,\"ida_bitmap_flag_exhausted\":%u},",
	       ZIGUX_IDA_BITMAP_FLAG_TRUNCATED,
	       ZIGUX_IDA_BITMAP_FLAG_EXHAUSTED);
	printf("\"truncated\":{\"summary\":");
	print_summary(zigux_ida_bitmap_summarize(&truncated));
	printf("},\"full\":{\"summary\":");
	print_summary(zigux_ida_bitmap_summarize(&full));
	printf("},\"exhausted\":{\"summary\":");
	print_summary(zigux_ida_bitmap_summarize(&exhausted));
	printf("},\"empty\":{\"is_valid\":%s,\"summary\":", zigux_ida_bitmap_view_valid(&empty) ? "true" : "false");
	print_summary(zigux_ida_bitmap_summarize(&empty));
	printf("}}\n");
	return 0;
}

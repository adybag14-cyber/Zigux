#include <stdio.h>

#include <linux/zigux.h>

int main(void)
{
	unsigned long bitmap_words[2] = {
		(1UL << 1) | (1UL << 5) | (1UL << 63),
		(1UL << 4) | (1UL << 9),
	};
	struct zigux_bitmap_view bitmap =
		zigux_bitmap_view_from_words(bitmap_words, ZIGUX_BITS_PER_LONG + 10U);
	struct zigux_bitmap_summary bitmap_summary =
		zigux_bitmap_summarize(&bitmap);
	struct zigux_bitmap_view empty_bitmap =
		zigux_bitmap_view_from_words(NULL, 0);
	struct zigux_bitmap_summary empty_bitmap_summary =
		zigux_bitmap_summarize(&empty_bitmap);
	unsigned long cpumask_bits[1] = {
		(1UL << 0) | (1UL << 2) | (1UL << 6) | (1UL << 9),
	};
	struct zigux_cpumask_view cpumask =
		zigux_cpumask_view_from_bits(cpumask_bits, 12);
	struct zigux_cpumask_summary cpumask_summary =
		zigux_cpumask_summarize(&cpumask);
	struct zigux_cpumask_view empty_cpumask =
		zigux_cpumask_view_from_bits(NULL, 0);
	struct zigux_cpumask_summary empty_cpumask_summary =
		zigux_cpumask_summarize(&empty_cpumask);

	printf(
		"{\"constants\":{\"bits_per_long\":%u},"
		"\"bitmap\":{\"word_count\":%u,\"valid\":%s,"
		"\"first_set\":%u,\"first_zero\":%u,\"weight\":%u,"
		"\"test_bit_4\":%s,\"test_bit_63\":%s,"
		"\"summary\":{\"first_set\":%u,\"first_zero\":%u,\"weight\":%u}},"
		"\"empty_bitmap\":{\"first_set\":%u,\"first_zero\":%u,\"weight\":%u},"
		"\"cpumask\":{\"word_count\":%u,\"valid\":%s,"
		"\"first_cpu\":%u,\"next_cpu_after_first\":%u,\"weight\":%u,"
		"\"test_cpu_3\":%s,\"test_cpu_9\":%s,"
		"\"summary\":{\"first_cpu\":%u,\"next_cpu\":%u,\"weight\":%u}},"
		"\"empty_cpumask\":{\"first_cpu\":%u,\"next_cpu\":%u,\"weight\":%u}}\n",
		ZIGUX_BITS_PER_LONG,
		bitmap.word_count,
		zigux_bitmap_view_valid(&bitmap) ? "true" : "false",
		zigux_bitmap_first_set(&bitmap),
		zigux_bitmap_first_zero(&bitmap),
		zigux_bitmap_weight(&bitmap),
		zigux_bitmap_test_bit(&bitmap, 4) ? "true" : "false",
		zigux_bitmap_test_bit(&bitmap, 63) ? "true" : "false",
		bitmap_summary.first_set,
		bitmap_summary.first_zero,
		bitmap_summary.weight,
		zigux_bitmap_first_set(&empty_bitmap),
		zigux_bitmap_first_zero(&empty_bitmap),
		empty_bitmap_summary.weight,
		zigux_bitmap_word_count(cpumask.nr_cpu_ids),
		zigux_cpumask_view_valid(&cpumask) ? "true" : "false",
		zigux_cpumask_first_cpu(&cpumask),
		zigux_cpumask_next_cpu(&cpumask, zigux_cpumask_first_cpu(&cpumask)),
		zigux_cpumask_weight(&cpumask),
		zigux_cpumask_test_cpu(&cpumask, 3) ? "true" : "false",
		zigux_cpumask_test_cpu(&cpumask, 9) ? "true" : "false",
		cpumask_summary.first_cpu,
		cpumask_summary.next_cpu,
		cpumask_summary.weight,
		zigux_cpumask_first_cpu(&empty_cpumask),
		zigux_cpumask_next_cpu(&empty_cpumask, 0),
		empty_cpumask_summary.weight);
	return 0;
}

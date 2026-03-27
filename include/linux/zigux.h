#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#ifdef __KERNEL__
#include <linux/build_bug.h>
#include <linux/types.h>
#else
#include <stdbool.h>
#include <stdint.h>
#endif

#include <zigux/abi.h>

#define ZIGUX_BITS_PER_LONG ((zigux_u32)(sizeof(unsigned long) * 8U))

#ifdef __KERNEL__
#define zigux_ptr_addr(ptr) ((unsigned long)(ptr))
#else
#define zigux_ptr_addr(ptr) ((unsigned long)(uintptr_t)(ptr))
#endif

static inline struct zigux_export_status zigux_status_ok(zigux_u16 facility)
{
	return (struct zigux_export_status){
		.code = 0,
		.facility = facility,
		.flags = 0,
	};
}

static inline struct zigux_export_status zigux_status_err(zigux_s32 code,
							  zigux_u16 facility)
{
	return (struct zigux_export_status){
		.code = code,
		.facility = facility,
		.flags = code < 0 ? ZIGUX_STATUS_FLAG_ERROR : 0,
	};
}

#ifdef __KERNEL__
#define zigux_assert_layout(type, expected_size) \
	BUILD_BUG_ON(sizeof(type) != (expected_size))
#endif

static inline zigux_u32 zigux_bitmap_word_count(zigux_u32 nbits)
{
	return nbits == 0 ? 0 : (nbits + ZIGUX_BITS_PER_LONG - 1U) / ZIGUX_BITS_PER_LONG;
}

static inline unsigned long zigux_bitmap_last_word_mask(zigux_u32 nbits)
{
	zigux_u32 rem;

	if (nbits == 0)
		return 0UL;

	rem = nbits % ZIGUX_BITS_PER_LONG;
	if (rem == 0)
		return ~0UL;

	return ~0UL >> (ZIGUX_BITS_PER_LONG - rem);
}

static inline struct zigux_bitmap_view
zigux_bitmap_view_from_words(const unsigned long *words, zigux_u32 nbits)
{
	return (struct zigux_bitmap_view){
		.words_addr = zigux_ptr_addr(words),
		.nbits = nbits,
		.word_count = zigux_bitmap_word_count(nbits),
	};
}

static inline bool zigux_bitmap_view_valid(const struct zigux_bitmap_view *view)
{
	zigux_u32 expected;

	if (!view)
		return false;

	expected = zigux_bitmap_word_count(view->nbits);
	if (view->word_count != expected)
		return false;

	return expected == 0 || view->words_addr != 0;
}

static inline const unsigned long *
zigux_bitmap_words(const struct zigux_bitmap_view *view)
{
	return (const unsigned long *)(uintptr_t)view->words_addr;
}

static inline bool zigux_bitmap_test_bit(const struct zigux_bitmap_view *view,
					 zigux_u32 bit)
{
	const unsigned long *words;
	zigux_u32 word_index;
	zigux_u32 bit_index;

	if (!zigux_bitmap_view_valid(view) || bit >= view->nbits)
		return false;

	words = zigux_bitmap_words(view);
	word_index = bit / ZIGUX_BITS_PER_LONG;
	bit_index = bit % ZIGUX_BITS_PER_LONG;
	return ((words[word_index] >> bit_index) & 1UL) != 0;
}

static inline zigux_u32 zigux_bitmap_first_set(const struct zigux_bitmap_view *view)
{
	const unsigned long *words;
	zigux_u32 index;

	if (!zigux_bitmap_view_valid(view))
		return 0;
	if (view->word_count == 0)
		return view->nbits;

	words = zigux_bitmap_words(view);
	for (index = 0; index < view->word_count; index++) {
		unsigned long value = words[index];

		if (index + 1U == view->word_count)
			value &= zigux_bitmap_last_word_mask(view->nbits);
		if (value != 0)
			return index * ZIGUX_BITS_PER_LONG + (zigux_u32)__builtin_ctzl(value);
	}

	return view->nbits;
}

static inline zigux_u32 zigux_bitmap_first_zero(const struct zigux_bitmap_view *view)
{
	const unsigned long *words;
	zigux_u32 index;

	if (!zigux_bitmap_view_valid(view))
		return 0;
	if (view->word_count == 0)
		return view->nbits;

	words = zigux_bitmap_words(view);
	for (index = 0; index < view->word_count; index++) {
		unsigned long value = ~words[index];

		if (index + 1U == view->word_count)
			value &= zigux_bitmap_last_word_mask(view->nbits);
		if (value != 0)
			return index * ZIGUX_BITS_PER_LONG + (zigux_u32)__builtin_ctzl(value);
	}

	return view->nbits;
}

static inline zigux_u32 zigux_bitmap_weight(const struct zigux_bitmap_view *view)
{
	const unsigned long *words;
	zigux_u32 index;
	zigux_u32 total = 0;

	if (!zigux_bitmap_view_valid(view))
		return 0;
	if (view->word_count == 0)
		return 0;

	words = zigux_bitmap_words(view);
	for (index = 0; index < view->word_count; index++) {
		unsigned long value = words[index];

		if (index + 1U == view->word_count)
			value &= zigux_bitmap_last_word_mask(view->nbits);
		total += (zigux_u32)__builtin_popcountl(value);
	}

	return total;
}

static inline struct zigux_bitmap_summary
zigux_bitmap_summarize(const struct zigux_bitmap_view *view)
{
	if (!zigux_bitmap_view_valid(view))
		return (struct zigux_bitmap_summary){0, 0, 0, 0};

	return (struct zigux_bitmap_summary){
		.first_set = zigux_bitmap_first_set(view),
		.first_zero = zigux_bitmap_first_zero(view),
		.weight = zigux_bitmap_weight(view),
		.reserved = 0,
	};
}

static inline struct zigux_cpumask_view
zigux_cpumask_view_from_bits(const unsigned long *bits, zigux_u32 nr_cpu_ids)
{
	return (struct zigux_cpumask_view){
		.bits_addr = zigux_ptr_addr(bits),
		.nr_cpu_ids = nr_cpu_ids,
		.reserved = 0,
	};
}

static inline bool zigux_cpumask_view_valid(const struct zigux_cpumask_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return view->nr_cpu_ids == 0 || view->bits_addr != 0;
}

static inline struct zigux_bitmap_view
zigux_cpumask_as_bitmap(const struct zigux_cpumask_view *view)
{
	if (!zigux_cpumask_view_valid(view))
		return (struct zigux_bitmap_view){0, 0, 0};

	return (struct zigux_bitmap_view){
		.words_addr = view->bits_addr,
		.nbits = view->nr_cpu_ids,
		.word_count = zigux_bitmap_word_count(view->nr_cpu_ids),
	};
}

static inline bool zigux_cpumask_test_cpu(const struct zigux_cpumask_view *view,
					  zigux_u32 cpu)
{
	const struct zigux_bitmap_view bitmap = zigux_cpumask_as_bitmap(view);
	return zigux_bitmap_test_bit(&bitmap, cpu);
}

static inline zigux_u32 zigux_cpumask_first_cpu(const struct zigux_cpumask_view *view)
{
	const struct zigux_bitmap_view bitmap = zigux_cpumask_as_bitmap(view);

	if (!zigux_cpumask_view_valid(view))
		return 0;
	return zigux_bitmap_first_set(&bitmap);
}

static inline zigux_u32 zigux_cpumask_next_cpu(const struct zigux_cpumask_view *view,
					       zigux_u32 prev_cpu)
{
	const struct zigux_bitmap_view bitmap = zigux_cpumask_as_bitmap(view);
	const unsigned long *words = zigux_bitmap_words(&bitmap);
	zigux_u32 start;
	zigux_u32 index;

	if (!zigux_cpumask_view_valid(view))
		return 0;
	if (prev_cpu >= view->nr_cpu_ids)
		return view->nr_cpu_ids;
	start = prev_cpu + 1U;
	if (start >= view->nr_cpu_ids)
		return view->nr_cpu_ids;

	for (index = start / ZIGUX_BITS_PER_LONG; index < bitmap.word_count; index++) {
		unsigned long value = words[index];
		zigux_u32 offset = 0;

		if (index == start / ZIGUX_BITS_PER_LONG) {
			offset = start % ZIGUX_BITS_PER_LONG;
			value &= ~0UL << offset;
		}
		if (index + 1U == bitmap.word_count)
			value &= zigux_bitmap_last_word_mask(bitmap.nbits);
		if (value != 0)
			return index * ZIGUX_BITS_PER_LONG + (zigux_u32)__builtin_ctzl(value);
	}

	return view->nr_cpu_ids;
}

static inline zigux_u32 zigux_cpumask_weight(const struct zigux_cpumask_view *view)
{
	const struct zigux_bitmap_view bitmap = zigux_cpumask_as_bitmap(view);
	return zigux_bitmap_weight(&bitmap);
}

static inline struct zigux_cpumask_summary
zigux_cpumask_summarize(const struct zigux_cpumask_view *view)
{
	zigux_u32 first;

	if (!zigux_cpumask_view_valid(view))
		return (struct zigux_cpumask_summary){0, 0, 0, 0};

	first = zigux_cpumask_first_cpu(view);
	return (struct zigux_cpumask_summary){
		.first_cpu = first,
		.next_cpu = first < view->nr_cpu_ids ? zigux_cpumask_next_cpu(view, first) : view->nr_cpu_ids,
		.weight = zigux_cpumask_weight(view),
		.reserved = 0,
	};
}

#endif

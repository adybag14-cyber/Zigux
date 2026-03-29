#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#ifdef __KERNEL__
#include <linux/build_bug.h>
#include <linux/string.h>
#include <linux/types.h>
#else
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#endif

#include <zigux/abi.h>

#define ZIGUX_BITS_PER_LONG ((zigux_u32)(sizeof(unsigned long) * 8U))
#define ZIGUX_MAX_ERRNO 4095U
#define ZIGUX_DEV_MINOR_BITS 20U
#define ZIGUX_DEV_MINOR_MASK ((1U << ZIGUX_DEV_MINOR_BITS) - 1U)

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

static inline struct zigux_list_view
zigux_list_view_from_head(const struct zigux_list_head_ref *head, zigux_u32 max_nodes)
{
	return (struct zigux_list_view){
		.head_addr = zigux_ptr_addr(head),
		.max_nodes = max_nodes,
		.reserved = 0,
	};
}

static inline bool zigux_list_view_valid(const struct zigux_list_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return view->head_addr != 0 && view->max_nodes != 0;
}

static inline const struct zigux_list_head_ref *
zigux_list_head_ptr(const struct zigux_list_view *view)
{
	return (const struct zigux_list_head_ref *)(uintptr_t)view->head_addr;
}

static inline const struct zigux_list_head_ref *
zigux_list_node_ptr(unsigned long addr)
{
	return (const struct zigux_list_head_ref *)(uintptr_t)addr;
}

static inline bool zigux_list_empty(const struct zigux_list_view *view)
{
	const struct zigux_list_head_ref *head;

	if (!zigux_list_view_valid(view))
		return false;
	head = zigux_list_head_ptr(view);
	return head->next_addr == view->head_addr && head->prev_addr == view->head_addr;
}

static inline bool zigux_list_is_singular(const struct zigux_list_view *view)
{
	const struct zigux_list_head_ref *head;
	const struct zigux_list_head_ref *node;

	if (!zigux_list_view_valid(view) || zigux_list_empty(view))
		return false;

	head = zigux_list_head_ptr(view);
	if (head->next_addr != head->prev_addr)
		return false;
	node = zigux_list_node_ptr(head->next_addr);
	return node->next_addr == view->head_addr && node->prev_addr == view->head_addr;
}

static inline zigux_u32 zigux_list_length_bounded(const struct zigux_list_view *view)
{
	const struct zigux_list_head_ref *head;
	unsigned long current;
	zigux_u32 count = 0;

	if (!zigux_list_view_valid(view))
		return 0;

	head = zigux_list_head_ptr(view);
	current = head->next_addr;
	while (count < view->max_nodes && current != 0 && current != view->head_addr) {
		const struct zigux_list_head_ref *node = zigux_list_node_ptr(current);
		count++;
		current = node->next_addr;
	}

	return count;
}

static inline struct zigux_list_summary
zigux_list_summarize(const struct zigux_list_view *view)
{
	struct zigux_list_summary summary = {0, 0};
	const struct zigux_list_head_ref *head;
	unsigned long current;
	zigux_u32 count = 0;

	if (!zigux_list_view_valid(view))
		return summary;

	if (zigux_list_empty(view)) {
		summary.flags = ZIGUX_LIST_FLAG_EMPTY | ZIGUX_LIST_FLAG_CIRCULAR;
		return summary;
	}

	head = zigux_list_head_ptr(view);
	current = head->next_addr;
	while (count < view->max_nodes && current != 0 && current != view->head_addr) {
		const struct zigux_list_head_ref *node = zigux_list_node_ptr(current);
		count++;
		current = node->next_addr;
	}

	summary.length = count;
	if (zigux_list_is_singular(view))
		summary.flags |= ZIGUX_LIST_FLAG_SINGULAR;
	if (current == view->head_addr)
		summary.flags |= ZIGUX_LIST_FLAG_CIRCULAR;
	else
		summary.flags |= ZIGUX_LIST_FLAG_TRUNCATED;
	return summary;
}

static inline struct zigux_hlist_view
zigux_hlist_view_from_head(const struct zigux_hlist_head_ref *head, zigux_u32 max_nodes)
{
	return (struct zigux_hlist_view){
		.head_addr = zigux_ptr_addr(head),
		.max_nodes = max_nodes,
		.reserved = 0,
	};
}

static inline bool zigux_hlist_view_valid(const struct zigux_hlist_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return view->head_addr != 0 && view->max_nodes != 0;
}

static inline const struct zigux_hlist_head_ref *
zigux_hlist_head_ptr(const struct zigux_hlist_view *view)
{
	return (const struct zigux_hlist_head_ref *)(uintptr_t)view->head_addr;
}

static inline const struct zigux_hlist_node_ref *
zigux_hlist_node_ptr(unsigned long addr)
{
	return (const struct zigux_hlist_node_ref *)(uintptr_t)addr;
}

static inline bool zigux_hlist_empty(const struct zigux_hlist_view *view)
{
	const struct zigux_hlist_head_ref *head;

	if (!zigux_hlist_view_valid(view))
		return false;
	head = zigux_hlist_head_ptr(view);
	return head->first_addr == 0;
}

static inline bool zigux_hlist_is_singular(const struct zigux_hlist_view *view)
{
	const struct zigux_hlist_head_ref *head;
	const struct zigux_hlist_node_ref *node;

	if (!zigux_hlist_view_valid(view) || zigux_hlist_empty(view))
		return false;

	head = zigux_hlist_head_ptr(view);
	node = zigux_hlist_node_ptr(head->first_addr);
	return node->next_addr == 0;
}

static inline zigux_u32 zigux_hlist_length_bounded(const struct zigux_hlist_view *view)
{
	const struct zigux_hlist_head_ref *head;
	unsigned long current;
	zigux_u32 count = 0;

	if (!zigux_hlist_view_valid(view))
		return 0;

	head = zigux_hlist_head_ptr(view);
	current = head->first_addr;
	while (count < view->max_nodes && current != 0) {
		const struct zigux_hlist_node_ref *node = zigux_hlist_node_ptr(current);
		count++;
		current = node->next_addr;
	}

	return count;
}

static inline struct zigux_hlist_summary
zigux_hlist_summarize(const struct zigux_hlist_view *view)
{
	struct zigux_hlist_summary summary = {0, 0};
	const struct zigux_hlist_head_ref *head;
	unsigned long current;
	zigux_u32 count = 0;

	if (!zigux_hlist_view_valid(view))
		return summary;

	head = zigux_hlist_head_ptr(view);
	current = head->first_addr;
	if (current == 0) {
		summary.flags = ZIGUX_HLIST_FLAG_EMPTY | ZIGUX_HLIST_FLAG_TERMINATED;
		return summary;
	}

	while (count < view->max_nodes && current != 0) {
		const struct zigux_hlist_node_ref *node = zigux_hlist_node_ptr(current);
		count++;
		current = node->next_addr;
	}

	summary.length = count;
	if (zigux_hlist_is_singular(view))
		summary.flags |= ZIGUX_HLIST_FLAG_SINGULAR;
	if (current == 0)
		summary.flags |= ZIGUX_HLIST_FLAG_TERMINATED;
	else
		summary.flags |= ZIGUX_HLIST_FLAG_TRUNCATED;
	return summary;
}

static inline unsigned long zigux_err_addr_from_errno(zigux_s32 errno_code)
{
	return (unsigned long)(long)errno_code;
}

static inline bool zigux_err_addr_is_err(unsigned long raw_addr)
{
	return raw_addr >= (unsigned long)(long)(-((zigux_s32)ZIGUX_MAX_ERRNO));
}

static inline bool zigux_err_addr_is_null(unsigned long raw_addr)
{
	return raw_addr == 0;
}

static inline bool zigux_err_addr_is_null_or_err(unsigned long raw_addr)
{
	return zigux_err_addr_is_null(raw_addr) || zigux_err_addr_is_err(raw_addr);
}

static inline zigux_s32 zigux_err_addr_to_errno(unsigned long raw_addr)
{
	return (zigux_s32)(long)raw_addr;
}

static inline struct zigux_err_ptr_summary
zigux_err_addr_summarize(unsigned long raw_addr)
{
	struct zigux_err_ptr_summary summary = {0, 0, 0};

	if (zigux_err_addr_is_err(raw_addr)) {
		summary.errno_code = zigux_err_addr_to_errno(raw_addr);
		summary.flags |= ZIGUX_ERR_PTR_FLAG_ERROR;
	}
	if (zigux_err_addr_is_null(raw_addr))
		summary.flags |= ZIGUX_ERR_PTR_FLAG_NULL;
	return summary;
}

static inline unsigned long zigux_xa_mk_value(zigux_u32 value)
{
	return ((unsigned long)value << 1) | 1UL;
}

static inline bool zigux_xa_is_value(unsigned long raw_addr)
{
	return (raw_addr & 1UL) != 0;
}

static inline zigux_u32 zigux_xa_to_value(unsigned long raw_addr)
{
	return (zigux_u32)(raw_addr >> 1);
}

static inline struct zigux_xa_value_summary
zigux_xa_summarize(unsigned long raw_addr)
{
	if (zigux_xa_is_value(raw_addr)) {
		return (struct zigux_xa_value_summary){
			.raw_addr = raw_addr,
			.decoded_value = zigux_xa_to_value(raw_addr),
			.flags = ZIGUX_XA_VALUE_FLAG_VALUE,
		};
	}

	return (struct zigux_xa_value_summary){
		.raw_addr = raw_addr,
		.decoded_value = 0,
		.flags = ZIGUX_XA_VALUE_FLAG_PLAIN,
	};
}

static inline struct zigux_xa_slot_view
zigux_xa_slot_view_from_entries(const unsigned long *entries, zigux_u32 slot_count,
				zigux_u32 max_scan)
{
	return (struct zigux_xa_slot_view){
		.slots_addr = zigux_ptr_addr(entries),
		.slot_count = slot_count,
		.max_scan = max_scan,
	};
}

static inline bool zigux_xa_slot_view_valid(const struct zigux_xa_slot_view *view)
{
	if (!view)
		return false;
	if (view->slot_count == 0)
		return true;
	return view->slots_addr != 0 && view->max_scan != 0;
}

static inline const unsigned long *
zigux_xa_slot_entries(const struct zigux_xa_slot_view *view)
{
	return (const unsigned long *)(uintptr_t)view->slots_addr;
}

static inline unsigned long
zigux_xa_slot_entry_at(const struct zigux_xa_slot_view *view, zigux_u32 index)
{
	const unsigned long *entries;

	if (!zigux_xa_slot_view_valid(view) || index >= view->slot_count)
		return 0;

	entries = zigux_xa_slot_entries(view);
	return entries[index];
}

static inline struct zigux_xa_slot_summary
zigux_xa_slot_summarize(const struct zigux_xa_slot_view *view)
{
	struct zigux_xa_slot_summary summary = {0, 0, 0, 0, 0, 0};
	const unsigned long *entries;
	zigux_u32 scanned;
	zigux_u32 index;

	if (!zigux_xa_slot_view_valid(view))
		return summary;
	if (view->slot_count == 0)
		return summary;

	scanned = view->slot_count < view->max_scan ? view->slot_count : view->max_scan;
	summary.scanned_count = scanned;
	if (scanned < view->slot_count)
		summary.flags |= ZIGUX_XA_SLOT_FLAG_TRUNCATED;

	entries = zigux_xa_slot_entries(view);
	for (index = 0; index < scanned; index++) {
		unsigned long raw_addr = entries[index];

		if (zigux_err_addr_is_null(raw_addr))
			summary.null_count++;
		else if (zigux_err_addr_is_err(raw_addr))
			summary.error_count++;
		else if (zigux_xa_is_value(raw_addr))
			summary.value_count++;
		else
			summary.plain_count++;
	}

	return summary;
}

static inline struct zigux_idr_slot_view
zigux_idr_slot_view_from_entries(const unsigned long *entries, zigux_u32 base_id,
				 zigux_u32 slot_count, zigux_u32 max_scan)
{
	return (struct zigux_idr_slot_view){
		.slots_addr = zigux_ptr_addr(entries),
		.base_id = base_id,
		.slot_count = slot_count,
		.max_scan = max_scan,
		.reserved = 0,
	};
}

static inline bool zigux_idr_slot_view_valid(const struct zigux_idr_slot_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->slot_count == 0)
		return true;
	return view->slots_addr != 0 && view->max_scan != 0;
}

static inline const unsigned long *
zigux_idr_slot_entries(const struct zigux_idr_slot_view *view)
{
	return (const unsigned long *)(uintptr_t)view->slots_addr;
}

static inline unsigned long
zigux_idr_slot_entry_at(const struct zigux_idr_slot_view *view, zigux_u32 index)
{
	const unsigned long *entries;

	if (!zigux_idr_slot_view_valid(view) || index >= view->slot_count)
		return 0;

	entries = zigux_idr_slot_entries(view);
	return entries[index];
}

static inline struct zigux_idr_slot_summary
zigux_idr_slot_summarize(const struct zigux_idr_slot_view *view)
{
	struct zigux_idr_slot_summary summary = {
		0, 0, 0, 0, 0, 0, 0, 0
	};
	const unsigned long *entries;
	zigux_u32 scanned;
	zigux_u32 index;
	bool have_first_present = false;
	bool have_first_free = false;

	if (!zigux_idr_slot_view_valid(view))
		return summary;
	if (view->slot_count == 0) {
		summary.first_present_id = view->base_id;
		summary.next_free_id = view->base_id;
		return summary;
	}

	scanned = view->slot_count < view->max_scan ? view->slot_count : view->max_scan;
	summary.scanned_count = scanned;
	summary.first_present_id = view->base_id + scanned;
	summary.next_free_id = view->base_id + scanned;
	if (scanned < view->slot_count)
		summary.flags |= ZIGUX_IDR_SLOT_FLAG_TRUNCATED;

	entries = zigux_idr_slot_entries(view);
	for (index = 0; index < scanned; index++) {
		unsigned long raw_addr = entries[index];
		zigux_u32 current_id = view->base_id + index;

		if (zigux_err_addr_is_null(raw_addr)) {
			if (!have_first_free) {
				summary.next_free_id = current_id;
				have_first_free = true;
			}
			continue;
		}

		summary.present_count++;
		if (!have_first_present) {
			summary.first_present_id = current_id;
			have_first_present = true;
		}

		if (zigux_err_addr_is_err(raw_addr))
			summary.error_count++;
		else if (zigux_xa_is_value(raw_addr))
			summary.value_count++;
		else
			summary.plain_count++;
	}

	return summary;
}

static inline struct zigux_ida_bitmap_view
zigux_ida_bitmap_view_from_bits(const unsigned long *bits, zigux_u32 base_id,
				zigux_u32 nbits, zigux_u32 max_scan)
{
	return (struct zigux_ida_bitmap_view){
		.bits_addr = zigux_ptr_addr(bits),
		.base_id = base_id,
		.nbits = nbits,
		.max_scan = max_scan,
		.reserved = 0,
	};
}

static inline bool zigux_ida_bitmap_view_valid(const struct zigux_ida_bitmap_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->nbits == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_bitmap_view
zigux_ida_bitmap_as_bitmap(const struct zigux_ida_bitmap_view *view)
{
	if (!zigux_ida_bitmap_view_valid(view))
		return (struct zigux_bitmap_view){0, 0, 0};

	return (struct zigux_bitmap_view){
		.words_addr = view->bits_addr,
		.nbits = view->nbits,
		.word_count = zigux_bitmap_word_count(view->nbits),
	};
}

static inline struct zigux_ida_bitmap_summary
zigux_ida_bitmap_summarize(const struct zigux_ida_bitmap_view *view)
{
	struct zigux_ida_bitmap_summary summary = {0, 0, 0, 0, 0, 0};
	struct zigux_bitmap_view bitmap;
	zigux_u32 scanned;
	zigux_u32 index;
	bool have_first_allocated = false;
	bool have_first_free = false;

	if (!zigux_ida_bitmap_view_valid(view))
		return summary;
	if (view->nbits == 0) {
		summary.first_allocated_id = view->base_id;
		summary.first_free_id = view->base_id;
		return summary;
	}

	scanned = view->nbits < view->max_scan ? view->nbits : view->max_scan;
	summary.scanned_count = scanned;
	summary.first_allocated_id = view->base_id + scanned;
	summary.first_free_id = view->base_id + scanned;
	if (scanned < view->nbits)
		summary.flags |= ZIGUX_IDA_BITMAP_FLAG_TRUNCATED;

	bitmap = zigux_ida_bitmap_as_bitmap(view);
	for (index = 0; index < scanned; index++) {
		zigux_u32 current_id = view->base_id + index;

		if (zigux_bitmap_test_bit(&bitmap, index)) {
			summary.allocated_count++;
			if (!have_first_allocated) {
				summary.first_allocated_id = current_id;
				have_first_allocated = true;
			}
		} else if (!have_first_free) {
			summary.first_free_id = current_id;
			have_first_free = true;
		}
	}

	if (!have_first_free)
		summary.flags |= ZIGUX_IDA_BITMAP_FLAG_EXHAUSTED;

	return summary;
}

static inline struct zigux_ida_alloc_view
zigux_ida_alloc_view_from_bits(const unsigned long *bits, zigux_u32 base_id,
			       zigux_u32 nbits, zigux_u32 max_scan,
			       zigux_u32 request_count)
{
	return (struct zigux_ida_alloc_view){
		.bits_addr = zigux_ptr_addr(bits),
		.base_id = base_id,
		.nbits = nbits,
		.max_scan = max_scan,
		.request_count = request_count,
		.reserved = 0,
	};
}

static inline bool zigux_ida_alloc_view_valid(const struct zigux_ida_alloc_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0)
		return false;
	if (view->nbits == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_bitmap_view
zigux_ida_alloc_as_bitmap(const struct zigux_ida_alloc_view *view)
{
	if (!zigux_ida_alloc_view_valid(view))
		return (struct zigux_bitmap_view){0, 0, 0};

	return (struct zigux_bitmap_view){
		.words_addr = view->bits_addr,
		.nbits = view->nbits,
		.word_count = zigux_bitmap_word_count(view->nbits),
	};
}

static inline struct zigux_ida_alloc_summary
zigux_ida_alloc_summarize(const struct zigux_ida_alloc_view *view)
{
	struct zigux_ida_alloc_summary summary = {0, 0, 0, 0, 0, 0};
	struct zigux_bitmap_view bitmap;
	zigux_u32 scanned;
	zigux_u32 index;
	zigux_u32 current_run = 0;
	zigux_u32 current_start = 0;

	if (!zigux_ida_alloc_view_valid(view))
		return summary;

	scanned = view->nbits < view->max_scan ? view->nbits : view->max_scan;
	summary.scanned_count = scanned;
	summary.request_count = view->request_count;
	summary.first_fit_id = view->base_id + scanned;
	if (scanned < view->nbits)
		summary.flags |= ZIGUX_IDA_ALLOC_FLAG_TRUNCATED;

	bitmap = zigux_ida_alloc_as_bitmap(view);
	for (index = 0; index < scanned; index++) {
		if (zigux_bitmap_test_bit(&bitmap, index)) {
			current_run = 0;
			continue;
		}

		if (current_run == 0)
			current_start = index;
		current_run++;
		if (current_run > summary.longest_free_run)
			summary.longest_free_run = current_run;
		if ((summary.flags & ZIGUX_IDA_ALLOC_FLAG_FOUND) == 0 &&
		    current_run >= view->request_count) {
			summary.first_fit_id = view->base_id + current_start;
			summary.flags |= ZIGUX_IDA_ALLOC_FLAG_FOUND;
		}
	}

	if ((summary.flags & ZIGUX_IDA_ALLOC_FLAG_FOUND) == 0)
		summary.flags |= ZIGUX_IDA_ALLOC_FLAG_EXHAUSTED;

	return summary;
}

static inline struct zigux_ida_range_view
zigux_ida_range_view_from_bits(const unsigned long *bits, zigux_u32 base_id,
			       zigux_u32 nbits, zigux_u32 max_scan,
			       zigux_u32 request_count, zigux_u32 max_ranges)
{
	return (struct zigux_ida_range_view){
		.bits_addr = zigux_ptr_addr(bits),
		.base_id = base_id,
		.nbits = nbits,
		.max_scan = max_scan,
		.request_count = request_count,
		.max_ranges = max_ranges,
		.reserved = 0,
	};
}

static inline bool zigux_ida_range_view_valid(const struct zigux_ida_range_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0 || view->max_ranges == 0)
		return false;
	if (view->nbits == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_bitmap_view
zigux_ida_range_as_bitmap(const struct zigux_ida_range_view *view)
{
	if (!zigux_ida_range_view_valid(view))
		return (struct zigux_bitmap_view){0, 0, 0};

	return (struct zigux_bitmap_view){
		.words_addr = view->bits_addr,
		.nbits = view->nbits,
		.word_count = zigux_bitmap_word_count(view->nbits),
	};
}

static inline struct zigux_ida_range_summary
zigux_ida_range_summarize(const struct zigux_ida_range_view *view)
{
	struct zigux_ida_range_summary summary = {0, 0, 0, 0, 0, 0};
	struct zigux_bitmap_view bitmap;
	zigux_u32 scanned;
	zigux_u32 start;

	if (!zigux_ida_range_view_valid(view))
		return summary;

	scanned = view->nbits < view->max_scan ? view->nbits : view->max_scan;
	summary.scanned_count = scanned;
	summary.request_count = view->request_count;
	summary.first_range_id = view->base_id + scanned;
	summary.last_range_id = view->base_id + scanned;
	if (scanned < view->nbits)
		summary.flags |= ZIGUX_IDA_RANGE_FLAG_TRUNCATED;
	if (scanned < view->request_count) {
		summary.flags |= ZIGUX_IDA_RANGE_FLAG_EXHAUSTED;
		return summary;
	}

	bitmap = zigux_ida_range_as_bitmap(view);
	for (start = 0; start + view->request_count <= scanned; start++) {
		zigux_u32 bit;
		bool fits = true;

		for (bit = 0; bit < view->request_count; bit++) {
			if (zigux_bitmap_test_bit(&bitmap, start + bit)) {
				fits = false;
				break;
			}
		}
		if (!fits)
			continue;

		if ((summary.flags & ZIGUX_IDA_RANGE_FLAG_FOUND) == 0)
			summary.first_range_id = view->base_id + start;
		summary.flags |= ZIGUX_IDA_RANGE_FLAG_FOUND;
		if (summary.candidate_range_count < view->max_ranges) {
			summary.last_range_id = view->base_id + start;
			summary.candidate_range_count++;
		} else {
			summary.flags |= ZIGUX_IDA_RANGE_FLAG_TRUNCATED;
		}
	}

	if ((summary.flags & ZIGUX_IDA_RANGE_FLAG_FOUND) == 0)
		summary.flags |= ZIGUX_IDA_RANGE_FLAG_EXHAUSTED;

	return summary;
}

static inline struct zigux_ida_range_set_view
zigux_ida_range_set_view_from_bits(const unsigned long *bits, zigux_u32 base_id,
				   zigux_u32 nbits, zigux_u32 max_scan,
				   zigux_u32 request_count, zigux_u32 max_ranges,
				   zigux_u32 max_selected)
{
	return (struct zigux_ida_range_set_view){
		.bits_addr = zigux_ptr_addr(bits),
		.base_id = base_id,
		.nbits = nbits,
		.max_scan = max_scan,
		.request_count = request_count,
		.max_ranges = max_ranges,
		.max_selected = max_selected,
		.reserved = 0,
	};
}

static inline bool
zigux_ida_range_set_view_valid(const struct zigux_ida_range_set_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0 || view->max_ranges == 0 ||
	    view->max_selected == 0)
		return false;
	if (view->nbits == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_bitmap_view
zigux_ida_range_set_as_bitmap(const struct zigux_ida_range_set_view *view)
{
	if (!zigux_ida_range_set_view_valid(view))
		return (struct zigux_bitmap_view){0, 0, 0};

	return (struct zigux_bitmap_view){
		.words_addr = view->bits_addr,
		.nbits = view->nbits,
		.word_count = zigux_bitmap_word_count(view->nbits),
	};
}

static inline struct zigux_ida_range_set_summary
zigux_ida_range_set_summarize(const struct zigux_ida_range_set_view *view)
{
	struct zigux_ida_range_set_summary summary = {0, 0, 0, 0, 0, 0, 0, 0};
	struct zigux_bitmap_view bitmap;
	zigux_u32 scanned;
	zigux_u32 start;
	zigux_u32 next_allowed_start = 0;

	if (!zigux_ida_range_set_view_valid(view))
		return summary;

	scanned = view->nbits < view->max_scan ? view->nbits : view->max_scan;
	summary.scanned_count = scanned;
	summary.request_count = view->request_count;
	summary.first_selected_id = view->base_id + scanned;
	summary.last_selected_id = view->base_id + scanned;
	if (scanned < view->nbits)
		summary.flags |= ZIGUX_IDA_RANGE_SET_FLAG_TRUNCATED;
	if (scanned < view->request_count) {
		summary.flags |= ZIGUX_IDA_RANGE_SET_FLAG_EXHAUSTED;
		return summary;
	}

	bitmap = zigux_ida_range_set_as_bitmap(view);
	for (start = 0; start + view->request_count <= scanned; start++) {
		zigux_u32 bit;
		bool fits = true;

		for (bit = 0; bit < view->request_count; bit++) {
			if (zigux_bitmap_test_bit(&bitmap, start + bit)) {
				fits = false;
				break;
			}
		}
		if (!fits)
			continue;

		summary.flags |= ZIGUX_IDA_RANGE_SET_FLAG_FOUND;
		if (summary.candidate_range_count < view->max_ranges) {
			summary.candidate_range_count++;
		} else {
			summary.flags |= ZIGUX_IDA_RANGE_SET_FLAG_TRUNCATED;
			continue;
		}

		if (start < next_allowed_start)
			continue;

		if (summary.selected_range_count < view->max_selected) {
			if ((summary.flags & ZIGUX_IDA_RANGE_SET_FLAG_SELECTED) == 0)
				summary.first_selected_id = view->base_id + start;
			summary.flags |= ZIGUX_IDA_RANGE_SET_FLAG_SELECTED;
			summary.last_selected_id = view->base_id + start;
			summary.selected_range_count++;
			next_allowed_start = start + view->request_count;
		} else {
			summary.flags |= ZIGUX_IDA_RANGE_SET_FLAG_TRUNCATED;
		}
	}

	if ((summary.flags & ZIGUX_IDA_RANGE_SET_FLAG_FOUND) == 0)
		summary.flags |= ZIGUX_IDA_RANGE_SET_FLAG_EXHAUSTED;

	return summary;
}

static inline struct zigux_ida_policy_view
zigux_ida_policy_view_from_bits(const unsigned long *bits, zigux_u32 base_id,
				zigux_u32 nbits, zigux_u32 max_scan,
				zigux_u32 request_count, zigux_u32 policy)
{
	return (struct zigux_ida_policy_view){
		.bits_addr = zigux_ptr_addr(bits),
		.base_id = base_id,
		.nbits = nbits,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.reserved = 0,
	};
}

static inline bool
zigux_ida_policy_view_valid(const struct zigux_ida_policy_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0)
		return false;
	if (view->policy != ZIGUX_IDA_POLICY_FIRST_FIT &&
	    view->policy != ZIGUX_IDA_POLICY_LAST_FIT)
		return false;
	if (view->nbits == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_bitmap_view
zigux_ida_policy_as_bitmap(const struct zigux_ida_policy_view *view)
{
	if (!zigux_ida_policy_view_valid(view))
		return (struct zigux_bitmap_view){0, 0, 0};

	return (struct zigux_bitmap_view){
		.words_addr = view->bits_addr,
		.nbits = view->nbits,
		.word_count = zigux_bitmap_word_count(view->nbits),
	};
}

static inline struct zigux_ida_policy_summary
zigux_ida_policy_summarize(const struct zigux_ida_policy_view *view)
{
	struct zigux_ida_policy_summary summary = {0, 0, 0, 0, 0, 0};
	struct zigux_bitmap_view bitmap;
	zigux_u32 scanned;
	zigux_u32 index;
	zigux_u32 current_run = 0;
	zigux_u32 current_start = 0;
	zigux_u32 first_candidate = 0;
	zigux_u32 last_candidate = 0;
	bool have_candidate = false;

	if (!zigux_ida_policy_view_valid(view))
		return summary;

	scanned = view->nbits < view->max_scan ? view->nbits : view->max_scan;
	summary.scanned_count = scanned;
	summary.request_count = view->request_count;
	summary.selected_fit_id = view->base_id + scanned;
	summary.alternate_fit_id = view->base_id + scanned;
	if (scanned < view->nbits)
		summary.flags |= ZIGUX_IDA_POLICY_FLAG_TRUNCATED;
	if (scanned < view->request_count) {
		summary.flags |= ZIGUX_IDA_POLICY_FLAG_EXHAUSTED;
		return summary;
	}

	bitmap = zigux_ida_policy_as_bitmap(view);
	for (index = 0; index < scanned; index++) {
		if (zigux_bitmap_test_bit(&bitmap, index)) {
			current_run = 0;
			continue;
		}

		if (current_run == 0)
			current_start = index;
		current_run++;
		if (current_run > summary.longest_free_run)
			summary.longest_free_run = current_run;
		if (current_run < view->request_count)
			continue;

		if (!have_candidate) {
			first_candidate = view->base_id + current_start;
			have_candidate = true;
		}
		last_candidate = view->base_id + current_start;
	}

	if (!have_candidate) {
		summary.flags |= ZIGUX_IDA_POLICY_FLAG_EXHAUSTED;
		return summary;
	}

	summary.flags |= ZIGUX_IDA_POLICY_FLAG_FOUND;
	if (view->policy == ZIGUX_IDA_POLICY_LAST_FIT) {
		summary.selected_fit_id = last_candidate;
		summary.alternate_fit_id = first_candidate;
	} else {
		summary.selected_fit_id = first_candidate;
		summary.alternate_fit_id = last_candidate;
	}

	return summary;
}

static inline struct zigux_minor_alloc_view
zigux_minor_alloc_view_from_bits(const unsigned long *bits, zigux_u32 major,
				 zigux_u32 first_minor, zigux_u32 minor_count,
				 zigux_u32 max_scan, zigux_u32 request_count,
				 zigux_u32 policy)
{
	return (struct zigux_minor_alloc_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.reserved = 0,
	};
}

static inline bool
zigux_minor_alloc_view_valid(const struct zigux_minor_alloc_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0)
		return false;
	if (view->policy != ZIGUX_IDA_POLICY_FIRST_FIT &&
	    view->policy != ZIGUX_IDA_POLICY_LAST_FIT)
		return false;
	if (view->minor_count == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_ida_policy_view
zigux_minor_alloc_as_ida_policy(const struct zigux_minor_alloc_view *view)
{
	if (!zigux_minor_alloc_view_valid(view))
		return (struct zigux_ida_policy_view){0, 0, 0, 0, 0, 0, 0};

	return (struct zigux_ida_policy_view){
		.bits_addr = view->bits_addr,
		.base_id = view->first_minor,
		.nbits = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.reserved = 0,
	};
}

static inline struct zigux_minor_alloc_summary
zigux_minor_alloc_summarize(const struct zigux_minor_alloc_view *view)
{
	struct zigux_minor_alloc_summary summary = {0, 0, 0, 0, 0, 0, 0, 0};
	struct zigux_ida_policy_view ida_view;
	struct zigux_ida_policy_summary ida_summary;

	if (!zigux_minor_alloc_view_valid(view))
		return summary;

	ida_view = zigux_minor_alloc_as_ida_policy(view);
	ida_summary = zigux_ida_policy_summarize(&ida_view);
	summary.major = view->major;
	summary.scanned_count = ida_summary.scanned_count;
	summary.request_count = ida_summary.request_count;
	summary.selected_minor_start = ida_summary.selected_fit_id;
	summary.selected_minor_end = ida_summary.selected_fit_id;
	summary.alternate_minor_start = ida_summary.alternate_fit_id;
	summary.longest_free_run = ida_summary.longest_free_run;
	if (ida_summary.flags & ZIGUX_IDA_POLICY_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_MINOR_ALLOC_FLAG_TRUNCATED;
	if (ida_summary.flags & ZIGUX_IDA_POLICY_FLAG_FOUND)
		summary.flags |= ZIGUX_MINOR_ALLOC_FLAG_FOUND;
	if (ida_summary.flags & ZIGUX_IDA_POLICY_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_MINOR_ALLOC_FLAG_EXHAUSTED;
	if (summary.flags & ZIGUX_MINOR_ALLOC_FLAG_FOUND)
		summary.selected_minor_end = ida_summary.selected_fit_id +
					     view->request_count - 1U;
	return summary;
}

static inline zigux_u32 zigux_mkdev(zigux_u32 major, zigux_u32 minor)
{
	return (major << ZIGUX_DEV_MINOR_BITS) | (minor & ZIGUX_DEV_MINOR_MASK);
}

static inline struct zigux_dev_region_view
zigux_dev_region_view_from_bits(const unsigned long *bits, zigux_u32 major,
				zigux_u32 first_minor, zigux_u32 minor_count,
				zigux_u32 max_scan, zigux_u32 request_count,
				zigux_u32 policy)
{
	return (struct zigux_dev_region_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.reserved = 0,
	};
}

static inline bool
zigux_dev_region_view_valid(const struct zigux_dev_region_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0)
		return false;
	if (view->policy != ZIGUX_IDA_POLICY_FIRST_FIT &&
	    view->policy != ZIGUX_IDA_POLICY_LAST_FIT)
		return false;
	if (view->minor_count == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_minor_alloc_view
zigux_dev_region_as_minor_alloc(const struct zigux_dev_region_view *view)
{
	if (!zigux_dev_region_view_valid(view))
		return (struct zigux_minor_alloc_view){0, 0, 0, 0, 0, 0, 0, 0};

	return (struct zigux_minor_alloc_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.reserved = 0,
	};
}

static inline struct zigux_dev_region_summary
zigux_dev_region_summarize(const struct zigux_dev_region_view *view)
{
	struct zigux_dev_region_summary summary = {0, 0, 0, 0, 0, 0, 0, 0};
	struct zigux_minor_alloc_view minor_view;
	struct zigux_minor_alloc_summary minor_summary;

	if (!zigux_dev_region_view_valid(view))
		return summary;

	minor_view = zigux_dev_region_as_minor_alloc(view);
	minor_summary = zigux_minor_alloc_summarize(&minor_view);
	summary.major = minor_summary.major;
	summary.scanned_count = minor_summary.scanned_count;
	summary.request_count = minor_summary.request_count;
	summary.selected_minor_start = minor_summary.selected_minor_start;
	summary.selected_minor_end = minor_summary.selected_minor_end;
	summary.flags = 0;
	if (minor_summary.flags & ZIGUX_MINOR_ALLOC_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_DEV_REGION_FLAG_TRUNCATED;
	if (minor_summary.flags & ZIGUX_MINOR_ALLOC_FLAG_FOUND) {
		summary.flags |= ZIGUX_DEV_REGION_FLAG_FOUND;
		summary.first_dev = zigux_mkdev(minor_summary.major,
						minor_summary.selected_minor_start);
		summary.last_dev = zigux_mkdev(minor_summary.major,
					       minor_summary.selected_minor_end);
	} else {
		summary.first_dev = zigux_mkdev(minor_summary.major,
						minor_summary.selected_minor_start);
		summary.last_dev = summary.first_dev;
	}
	if (minor_summary.flags & ZIGUX_MINOR_ALLOC_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_DEV_REGION_FLAG_EXHAUSTED;
	return summary;
}

static inline struct zigux_cdev_add_view
zigux_cdev_add_view_from_bits(const unsigned long *bits, zigux_u32 major,
			      zigux_u32 first_minor, zigux_u32 minor_count,
			      zigux_u32 max_scan, zigux_u32 request_count,
			      zigux_u32 policy)
{
	return (struct zigux_cdev_add_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.reserved = 0,
	};
}

static inline bool
zigux_cdev_add_view_valid(const struct zigux_cdev_add_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0)
		return false;
	if (view->policy != ZIGUX_IDA_POLICY_FIRST_FIT &&
	    view->policy != ZIGUX_IDA_POLICY_LAST_FIT)
		return false;
	if (view->minor_count == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_dev_region_view
zigux_cdev_add_as_dev_region(const struct zigux_cdev_add_view *view)
{
	if (!zigux_cdev_add_view_valid(view))
		return (struct zigux_dev_region_view){0, 0, 0, 0, 0, 0, 0, 0};

	return (struct zigux_dev_region_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.reserved = 0,
	};
}

static inline struct zigux_cdev_add_summary
zigux_cdev_add_summarize(const struct zigux_cdev_add_view *view)
{
	struct zigux_cdev_add_summary summary = {0, 0, 0, 0, 0, 0, 0, 0};
	struct zigux_dev_region_view dev_region_view;
	struct zigux_dev_region_summary dev_region_summary;

	if (!zigux_cdev_add_view_valid(view))
		return summary;

	dev_region_view = zigux_cdev_add_as_dev_region(view);
	dev_region_summary = zigux_dev_region_summarize(&dev_region_view);
	summary.major = dev_region_summary.major;
	summary.scanned_count = dev_region_summary.scanned_count;
	summary.request_count = dev_region_summary.request_count;
	summary.first_minor = dev_region_summary.selected_minor_start;
	if (dev_region_summary.flags & ZIGUX_DEV_REGION_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_CDEV_ADD_FLAG_TRUNCATED;
	if (dev_region_summary.flags & ZIGUX_DEV_REGION_FLAG_FOUND) {
		summary.flags |= ZIGUX_CDEV_ADD_FLAG_FOUND;
		summary.selected_count = view->request_count;
		summary.first_dev = dev_region_summary.first_dev;
		summary.last_dev = dev_region_summary.last_dev;
	}
	if (dev_region_summary.flags & ZIGUX_DEV_REGION_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_CDEV_ADD_FLAG_EXHAUSTED;
	return summary;
}

static inline struct zigux_cdev_lookup_view
zigux_cdev_lookup_view_from_bits(const unsigned long *bits, zigux_u32 major,
				 zigux_u32 first_minor, zigux_u32 minor_count,
				 zigux_u32 max_scan, zigux_u32 request_count,
				 zigux_u32 policy, zigux_u32 target_minor)
{
	return (struct zigux_cdev_lookup_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.reserved = 0,
	};
}

static inline bool
zigux_cdev_lookup_view_valid(const struct zigux_cdev_lookup_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0)
		return false;
	if (view->policy != ZIGUX_IDA_POLICY_FIRST_FIT &&
	    view->policy != ZIGUX_IDA_POLICY_LAST_FIT)
		return false;
	if (view->minor_count == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_cdev_add_view
zigux_cdev_lookup_as_cdev_add(const struct zigux_cdev_lookup_view *view)
{
	if (!zigux_cdev_lookup_view_valid(view))
		return (struct zigux_cdev_add_view){0, 0, 0, 0, 0, 0, 0, 0};

	return (struct zigux_cdev_add_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.reserved = 0,
	};
}

static inline struct zigux_cdev_lookup_summary
zigux_cdev_lookup_summarize(const struct zigux_cdev_lookup_view *view)
{
	struct zigux_cdev_lookup_summary summary = {
		0, 0, 0, 0, 0, 0, ZIGUX_CDEV_LOOKUP_INDEX_NONE, 0, 0
	};
	struct zigux_cdev_add_view add_view;
	struct zigux_cdev_add_summary add_summary;

	if (!zigux_cdev_lookup_view_valid(view))
		return summary;

	add_view = zigux_cdev_lookup_as_cdev_add(view);
	add_summary = zigux_cdev_add_summarize(&add_view);
	summary.major = add_summary.major;
	summary.scanned_count = add_summary.scanned_count;
	summary.request_count = add_summary.request_count;
	summary.selected_count = add_summary.selected_count;
	summary.first_minor = add_summary.first_minor;
	summary.target_minor = view->target_minor;
	if (add_summary.flags & ZIGUX_CDEV_ADD_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_CDEV_LOOKUP_FLAG_TRUNCATED;
	if (add_summary.flags & ZIGUX_CDEV_ADD_FLAG_FOUND) {
		zigux_u32 last_minor = add_summary.first_minor +
				       add_summary.selected_count - 1U;

		summary.flags |= ZIGUX_CDEV_LOOKUP_FLAG_FOUND;
		if (view->target_minor >= add_summary.first_minor &&
		    view->target_minor <= last_minor) {
			summary.flags |= ZIGUX_CDEV_LOOKUP_FLAG_HIT;
			summary.resolved_index = view->target_minor -
						 add_summary.first_minor;
			summary.resolved_dev = add_summary.first_dev +
					      summary.resolved_index;
		}
	}
	if (add_summary.flags & ZIGUX_CDEV_ADD_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_CDEV_LOOKUP_FLAG_EXHAUSTED;
	return summary;
}

static inline struct zigux_chrdev_open_view
zigux_chrdev_open_view_from_bits(const unsigned long *bits, zigux_u32 major,
				 zigux_u32 first_minor, zigux_u32 minor_count,
				 zigux_u32 max_scan, zigux_u32 request_count,
				 zigux_u32 policy, zigux_u32 target_minor,
				 zigux_u32 requested_mode,
				 zigux_u32 supported_mode)
{
	return (struct zigux_chrdev_open_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_open_view_valid(const struct zigux_chrdev_open_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->request_count == 0)
		return false;
	if (view->policy != ZIGUX_IDA_POLICY_FIRST_FIT &&
	    view->policy != ZIGUX_IDA_POLICY_LAST_FIT)
		return false;
	if (view->requested_mode == 0)
		return false;
	if (view->requested_mode &
	    ~(ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE))
		return false;
	if (view->supported_mode &
	    ~(ZIGUX_CHRDEV_MODE_READ | ZIGUX_CHRDEV_MODE_WRITE))
		return false;
	if (view->minor_count == 0)
		return true;
	return view->bits_addr != 0 && view->max_scan != 0;
}

static inline struct zigux_cdev_lookup_view
zigux_chrdev_open_as_cdev_lookup(const struct zigux_chrdev_open_view *view)
{
	if (!zigux_chrdev_open_view_valid(view))
		return (struct zigux_cdev_lookup_view){0, 0, 0, 0, 0, 0, 0, 0, 0};

	return (struct zigux_cdev_lookup_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.reserved = 0,
	};
}

static inline struct zigux_chrdev_open_summary
zigux_chrdev_open_summarize(const struct zigux_chrdev_open_view *view)
{
	struct zigux_chrdev_open_summary summary = {
		0, 0, 0, ZIGUX_CHRDEV_OPEN_INDEX_NONE, 0, 0, 0, 0, 0, 0
	};
	struct zigux_cdev_lookup_view lookup_view;
	struct zigux_cdev_lookup_summary lookup_summary;

	if (!zigux_chrdev_open_view_valid(view))
		return summary;

	lookup_view = zigux_chrdev_open_as_cdev_lookup(view);
	lookup_summary = zigux_cdev_lookup_summarize(&lookup_view);
	summary.major = lookup_summary.major;
	summary.target_minor = lookup_summary.target_minor;
	summary.selected_count = lookup_summary.selected_count;
	summary.resolved_index = lookup_summary.resolved_index;
	summary.resolved_dev = lookup_summary.resolved_dev;
	summary.requested_mode = view->requested_mode;
	summary.supported_mode = view->supported_mode;
	if (lookup_summary.flags & ZIGUX_CDEV_LOOKUP_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_CHRDEV_OPEN_FLAG_TRUNCATED;
	if (lookup_summary.flags & ZIGUX_CDEV_LOOKUP_FLAG_FOUND)
		summary.flags |= ZIGUX_CHRDEV_OPEN_FLAG_FOUND;
	if (lookup_summary.flags & ZIGUX_CDEV_LOOKUP_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_CHRDEV_OPEN_FLAG_EXHAUSTED;
	if (lookup_summary.flags & ZIGUX_CDEV_LOOKUP_FLAG_HIT) {
		zigux_u32 denied = view->requested_mode & ~view->supported_mode;

		summary.flags |= ZIGUX_CHRDEV_OPEN_FLAG_HIT;
		if (denied == 0) {
			summary.flags |= ZIGUX_CHRDEV_OPEN_FLAG_PERMITTED;
			summary.granted_mode = view->requested_mode;
		} else {
			summary.flags |= ZIGUX_CHRDEV_OPEN_FLAG_DENIED;
			summary.denied_mode = denied;
		}
	}
	return summary;
}

static inline struct zigux_chrdev_fops_view
zigux_chrdev_fops_view_from_bits(const unsigned long *bits, zigux_u32 major,
				 zigux_u32 first_minor, zigux_u32 minor_count,
				 zigux_u32 max_scan, zigux_u32 request_count,
				 zigux_u32 policy, zigux_u32 target_minor,
				 zigux_u32 requested_mode,
				 zigux_u32 supported_mode,
				 zigux_u32 available_ops)
{
	return (struct zigux_chrdev_fops_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_fops_view_valid(const struct zigux_chrdev_fops_view *view)
{
	struct zigux_chrdev_open_view open_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->available_ops &
	    ~(ZIGUX_CHRDEV_FOP_OPEN | ZIGUX_CHRDEV_FOP_RELEASE |
	      ZIGUX_CHRDEV_FOP_READ | ZIGUX_CHRDEV_FOP_WRITE))
		return false;

	open_view = (struct zigux_chrdev_open_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.reserved = 0,
	};
	return zigux_chrdev_open_view_valid(&open_view);
}

static inline struct zigux_chrdev_open_view
zigux_chrdev_fops_as_chrdev_open(const struct zigux_chrdev_fops_view *view)
{
	if (!zigux_chrdev_fops_view_valid(view))
		return (struct zigux_chrdev_open_view){
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		};

	return (struct zigux_chrdev_open_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.reserved = 0,
	};
}

static inline struct zigux_chrdev_fops_summary
zigux_chrdev_fops_summarize(const struct zigux_chrdev_fops_view *view)
{
	struct zigux_chrdev_fops_summary summary = {
		0, 0, 0, ZIGUX_CHRDEV_FOPS_INDEX_NONE, 0, 0, 0, 0, 0, 0
	};
	struct zigux_chrdev_open_view open_view;
	struct zigux_chrdev_open_summary open_summary;

	if (!zigux_chrdev_fops_view_valid(view))
		return summary;

	open_view = zigux_chrdev_fops_as_chrdev_open(view);
	open_summary = zigux_chrdev_open_summarize(&open_view);
	summary.major = open_summary.major;
	summary.target_minor = open_summary.target_minor;
	summary.selected_count = open_summary.selected_count;
	summary.resolved_index = open_summary.resolved_index ==
					 ZIGUX_CHRDEV_OPEN_INDEX_NONE ?
					 ZIGUX_CHRDEV_FOPS_INDEX_NONE :
					 open_summary.resolved_index;
	summary.resolved_dev = open_summary.resolved_dev;
	summary.granted_mode = open_summary.granted_mode;
	summary.available_ops = view->available_ops;
	if (open_summary.flags & ZIGUX_CHRDEV_OPEN_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_CHRDEV_FOPS_FLAG_TRUNCATED;
	if (open_summary.flags & ZIGUX_CHRDEV_OPEN_FLAG_FOUND)
		summary.flags |= ZIGUX_CHRDEV_FOPS_FLAG_FOUND;
	if (open_summary.flags & ZIGUX_CHRDEV_OPEN_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_CHRDEV_FOPS_FLAG_EXHAUSTED;
	if (open_summary.flags & ZIGUX_CHRDEV_OPEN_FLAG_HIT)
		summary.flags |= ZIGUX_CHRDEV_FOPS_FLAG_HIT;
	if (open_summary.flags & ZIGUX_CHRDEV_OPEN_FLAG_PERMITTED)
		summary.flags |= ZIGUX_CHRDEV_FOPS_FLAG_PERMITTED;
	if (open_summary.flags & ZIGUX_CHRDEV_OPEN_FLAG_DENIED)
		summary.flags |= ZIGUX_CHRDEV_FOPS_FLAG_DENIED;

	if ((summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_PERMITTED) &&
	    (summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_HIT)) {
		summary.required_ops = ZIGUX_CHRDEV_FOP_OPEN |
				       ZIGUX_CHRDEV_FOP_RELEASE;
		if (open_summary.granted_mode & ZIGUX_CHRDEV_MODE_READ)
			summary.required_ops |= ZIGUX_CHRDEV_FOP_READ;
		if (open_summary.granted_mode & ZIGUX_CHRDEV_MODE_WRITE)
			summary.required_ops |= ZIGUX_CHRDEV_FOP_WRITE;
		summary.missing_ops =
			summary.required_ops & ~view->available_ops;
		if (summary.required_ops != 0 && summary.missing_ops == 0)
			summary.flags |= ZIGUX_CHRDEV_FOPS_FLAG_ROUTABLE;
		else if (summary.missing_ops != 0)
			summary.flags |= ZIGUX_CHRDEV_FOPS_FLAG_MISSING_OPS;
	}
	return summary;
}

static inline struct zigux_chrdev_route_view
zigux_chrdev_route_view_from_bits(const unsigned long *bits, zigux_u32 major,
				  zigux_u32 first_minor, zigux_u32 minor_count,
				  zigux_u32 max_scan, zigux_u32 request_count,
				  zigux_u32 policy, zigux_u32 target_minor,
				  zigux_u32 requested_mode,
				  zigux_u32 supported_mode,
				  zigux_u32 available_ops)
{
	return (struct zigux_chrdev_route_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_route_view_valid(const struct zigux_chrdev_route_view *view)
{
	struct zigux_chrdev_fops_view fops_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;

	fops_view = (struct zigux_chrdev_fops_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.reserved = 0,
	};
	return zigux_chrdev_fops_view_valid(&fops_view);
}

static inline struct zigux_chrdev_fops_view
zigux_chrdev_route_as_chrdev_fops(const struct zigux_chrdev_route_view *view)
{
	if (!zigux_chrdev_route_view_valid(view))
		return (struct zigux_chrdev_fops_view){
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		};

	return (struct zigux_chrdev_fops_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.reserved = 0,
	};
}

static inline struct zigux_chrdev_route_summary
zigux_chrdev_route_summarize(const struct zigux_chrdev_route_view *view)
{
	struct zigux_chrdev_route_summary summary = {
		0, 0, 0, ZIGUX_CHRDEV_ROUTE_INDEX_NONE, 0, 0, 0, 0, 0, 0, 0
	};
	struct zigux_chrdev_fops_view fops_view;
	struct zigux_chrdev_fops_summary fops_summary;

	if (!zigux_chrdev_route_view_valid(view))
		return summary;

	fops_view = zigux_chrdev_route_as_chrdev_fops(view);
	fops_summary = zigux_chrdev_fops_summarize(&fops_view);
	summary.major = fops_summary.major;
	summary.target_minor = fops_summary.target_minor;
	summary.selected_count = fops_summary.selected_count;
	summary.resolved_index = fops_summary.resolved_index ==
					 ZIGUX_CHRDEV_FOPS_INDEX_NONE ?
					 ZIGUX_CHRDEV_ROUTE_INDEX_NONE :
					 fops_summary.resolved_index;
	summary.resolved_dev = fops_summary.resolved_dev;
	summary.granted_mode = fops_summary.granted_mode;
	if (fops_summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_CHRDEV_ROUTE_FLAG_TRUNCATED;
	if (fops_summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_FOUND)
		summary.flags |= ZIGUX_CHRDEV_ROUTE_FLAG_FOUND;
	if (fops_summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_CHRDEV_ROUTE_FLAG_EXHAUSTED;
	if (fops_summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_HIT)
		summary.flags |= ZIGUX_CHRDEV_ROUTE_FLAG_HIT;
	if (fops_summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_PERMITTED)
		summary.flags |= ZIGUX_CHRDEV_ROUTE_FLAG_PERMITTED;
	if (fops_summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_DENIED)
		summary.flags |= ZIGUX_CHRDEV_ROUTE_FLAG_DENIED;

	if ((summary.flags & ZIGUX_CHRDEV_ROUTE_FLAG_PERMITTED) &&
	    (summary.flags & ZIGUX_CHRDEV_ROUTE_FLAG_HIT)) {
		summary.entry_ops = ZIGUX_CHRDEV_FOP_OPEN;
		if (summary.granted_mode & ZIGUX_CHRDEV_MODE_READ)
			summary.data_ops |= ZIGUX_CHRDEV_FOP_READ;
		if (summary.granted_mode & ZIGUX_CHRDEV_MODE_WRITE)
			summary.data_ops |= ZIGUX_CHRDEV_FOP_WRITE;
		summary.exit_ops = ZIGUX_CHRDEV_FOP_RELEASE;
		summary.blocked_ops = fops_summary.missing_ops;
		if (fops_summary.flags & ZIGUX_CHRDEV_FOPS_FLAG_ROUTABLE)
			summary.flags |= ZIGUX_CHRDEV_ROUTE_FLAG_ROUTABLE;
		else if (summary.blocked_ops != 0)
			summary.flags |= ZIGUX_CHRDEV_ROUTE_FLAG_BLOCKED;
	}
	return summary;
}

static inline struct zigux_chrdev_io_view
zigux_chrdev_io_view_from_bits(const unsigned long *bits, zigux_u32 major,
			       zigux_u32 first_minor, zigux_u32 minor_count,
			       zigux_u32 max_scan, zigux_u32 request_count,
			       zigux_u32 policy, zigux_u32 target_minor,
			       zigux_u32 requested_mode,
			       zigux_u32 supported_mode,
			       zigux_u32 available_ops, zigux_u32 io_op,
			       zigux_u32 requested_bytes,
			       zigux_u32 max_chunk_bytes)
{
	return (struct zigux_chrdev_io_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_io_view_valid(const struct zigux_chrdev_io_view *view)
{
	struct zigux_chrdev_route_view route_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->io_op != ZIGUX_CHRDEV_IO_OP_READ &&
	    view->io_op != ZIGUX_CHRDEV_IO_OP_WRITE)
		return false;
	if (view->requested_bytes == 0 || view->max_chunk_bytes == 0)
		return false;

	route_view = (struct zigux_chrdev_route_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.reserved = 0,
	};
	return zigux_chrdev_route_view_valid(&route_view);
}

static inline struct zigux_chrdev_route_view
zigux_chrdev_io_as_chrdev_route(const struct zigux_chrdev_io_view *view)
{
	if (!zigux_chrdev_io_view_valid(view))
		return (struct zigux_chrdev_route_view){
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		};

	return (struct zigux_chrdev_route_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.reserved = 0,
	};
}

static inline struct zigux_chrdev_io_summary
zigux_chrdev_io_summarize(const struct zigux_chrdev_io_view *view)
{
	struct zigux_chrdev_io_summary summary = {
		0, 0, 0, ZIGUX_CHRDEV_IO_INDEX_NONE, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
	};
	struct zigux_chrdev_route_view route_view;
	struct zigux_chrdev_route_summary route_summary;
	zigux_u32 requested_data_op = 0;

	if (!zigux_chrdev_io_view_valid(view))
		return summary;

	route_view = zigux_chrdev_io_as_chrdev_route(view);
	route_summary = zigux_chrdev_route_summarize(&route_view);
	summary.major = route_summary.major;
	summary.target_minor = route_summary.target_minor;
	summary.selected_count = route_summary.selected_count;
	summary.resolved_index = route_summary.resolved_index ==
					 ZIGUX_CHRDEV_ROUTE_INDEX_NONE ?
					 ZIGUX_CHRDEV_IO_INDEX_NONE :
					 route_summary.resolved_index;
	summary.resolved_dev = route_summary.resolved_dev;
	summary.granted_mode = route_summary.granted_mode;
	summary.io_op = view->io_op;
	summary.requested_bytes = view->requested_bytes;

	if (route_summary.flags & ZIGUX_CHRDEV_ROUTE_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_CHRDEV_IO_FLAG_TRUNCATED;
	if (route_summary.flags & ZIGUX_CHRDEV_ROUTE_FLAG_FOUND)
		summary.flags |= ZIGUX_CHRDEV_IO_FLAG_FOUND;
	if (route_summary.flags & ZIGUX_CHRDEV_ROUTE_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_CHRDEV_IO_FLAG_EXHAUSTED;
	if (route_summary.flags & ZIGUX_CHRDEV_ROUTE_FLAG_HIT)
		summary.flags |= ZIGUX_CHRDEV_IO_FLAG_HIT;
	if (route_summary.flags & ZIGUX_CHRDEV_ROUTE_FLAG_PERMITTED)
		summary.flags |= ZIGUX_CHRDEV_IO_FLAG_PERMITTED;
	if (route_summary.flags & ZIGUX_CHRDEV_ROUTE_FLAG_DENIED)
		summary.flags |= ZIGUX_CHRDEV_IO_FLAG_DENIED;

	requested_data_op = view->io_op == ZIGUX_CHRDEV_IO_OP_READ ?
				ZIGUX_CHRDEV_FOP_READ :
				ZIGUX_CHRDEV_FOP_WRITE;
	if ((summary.flags & ZIGUX_CHRDEV_IO_FLAG_PERMITTED) &&
	    (summary.flags & ZIGUX_CHRDEV_IO_FLAG_HIT)) {
		bool op_blocked;
		summary.blocked_ops = route_summary.blocked_ops;
		op_blocked = (route_summary.blocked_ops & requested_data_op) != 0;
		if ((route_summary.data_ops & requested_data_op) != 0 &&
		    !op_blocked &&
		    route_summary.entry_ops != 0 &&
		    route_summary.exit_ops != 0) {
			summary.chunk_bytes = view->requested_bytes <
					      view->max_chunk_bytes ?
					      view->requested_bytes :
					      view->max_chunk_bytes;
			summary.entry_ops = route_summary.entry_ops;
			summary.data_ops = requested_data_op;
			summary.exit_ops = route_summary.exit_ops;
			summary.flags |= ZIGUX_CHRDEV_IO_FLAG_ROUTABLE;
			summary.flags |= ZIGUX_CHRDEV_IO_FLAG_DISPATCHABLE;
		} else {
			summary.blocked_ops |= requested_data_op;
			summary.flags |= ZIGUX_CHRDEV_IO_FLAG_BLOCKED;
		}
	}
	return summary;
}

static inline struct zigux_chrdev_xfer_view
zigux_chrdev_xfer_view_from_bits(const unsigned long *bits, zigux_u32 major,
				 zigux_u32 first_minor, zigux_u32 minor_count,
				 zigux_u32 max_scan, zigux_u32 request_count,
				 zigux_u32 policy, zigux_u32 target_minor,
				 zigux_u32 requested_mode,
				 zigux_u32 supported_mode,
				 zigux_u32 available_ops, zigux_u32 io_op,
				 zigux_u32 requested_bytes,
				 zigux_u32 max_chunk_bytes,
				 zigux_u64 file_offset,
				 zigux_u32 bytes_completed,
				 zigux_u32 max_segments)
{
	return (struct zigux_chrdev_xfer_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_xfer_view_valid(const struct zigux_chrdev_xfer_view *view)
{
	struct zigux_chrdev_io_view io_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->max_segments == 0)
		return false;
	if (view->bytes_completed > view->requested_bytes)
		return false;
	if ((zigux_u64)(view->file_offset + view->bytes_completed) <
	    view->file_offset)
		return false;

	io_view = (struct zigux_chrdev_io_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.reserved = 0,
	};
	return zigux_chrdev_io_view_valid(&io_view);
}

static inline struct zigux_chrdev_io_view
zigux_chrdev_xfer_as_chrdev_io(const struct zigux_chrdev_xfer_view *view)
{
	if (!zigux_chrdev_xfer_view_valid(view))
		return (struct zigux_chrdev_io_view){
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		};

	return (struct zigux_chrdev_io_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.reserved = 0,
	};
}

static inline zigux_u32 zigux_chrdev_xfer_ceil_div(zigux_u32 value,
						    zigux_u32 step)
{
	if (value == 0)
		return 0;
	return 1U + ((value - 1U) / step);
}

static inline struct zigux_chrdev_xfer_summary
zigux_chrdev_xfer_summarize(const struct zigux_chrdev_xfer_view *view)
{
	struct zigux_chrdev_xfer_summary summary = {
		0, 0, 0, ZIGUX_CHRDEV_XFER_INDEX_NONE, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0
	};
	struct zigux_chrdev_io_view io_view;
	struct zigux_chrdev_io_summary io_summary;
	zigux_u32 requested_remaining;

	if (!zigux_chrdev_xfer_view_valid(view))
		return summary;

	io_view = zigux_chrdev_xfer_as_chrdev_io(view);
	io_summary = zigux_chrdev_io_summarize(&io_view);
	requested_remaining = view->requested_bytes - view->bytes_completed;
	summary.major = io_summary.major;
	summary.target_minor = io_summary.target_minor;
	summary.selected_count = io_summary.selected_count;
	summary.resolved_index = io_summary.resolved_index ==
					 ZIGUX_CHRDEV_IO_INDEX_NONE ?
					 ZIGUX_CHRDEV_XFER_INDEX_NONE :
					 io_summary.resolved_index;
	summary.resolved_dev = io_summary.resolved_dev;
	summary.granted_mode = io_summary.granted_mode;
	summary.io_op = io_summary.io_op;
	summary.requested_bytes = io_summary.requested_bytes;
	summary.start_offset = view->file_offset + view->bytes_completed;
	summary.next_offset = summary.start_offset;
	summary.bytes_completed = view->bytes_completed;
	summary.requested_remaining = requested_remaining;
	summary.remaining_bytes = requested_remaining;
	summary.entry_ops = io_summary.entry_ops;
	summary.data_ops = io_summary.data_ops;
	summary.exit_ops = io_summary.exit_ops;
	summary.blocked_ops = io_summary.blocked_ops;

	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_TRUNCATED)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_TRUNCATED;
	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_FOUND)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_FOUND;
	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_EXHAUSTED)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_EXHAUSTED;
	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_HIT)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_HIT;
	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_PERMITTED)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_PERMITTED;
	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_DENIED)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_DENIED;
	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_ROUTABLE)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_ROUTABLE;
	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_BLOCKED)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_BLOCKED;
	if (io_summary.flags & ZIGUX_CHRDEV_IO_FLAG_DISPATCHABLE)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_DISPATCHABLE;
	if (view->bytes_completed != 0)
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_RESUMED;

	if ((summary.flags & ZIGUX_CHRDEV_XFER_FLAG_DISPATCHABLE) &&
	    requested_remaining != 0) {
		zigux_u32 needed_segments;
		zigux_u64 issued_bytes_u64;

		needed_segments = zigux_chrdev_xfer_ceil_div(requested_remaining,
							      view->max_chunk_bytes);
		summary.segment_count = needed_segments < view->max_segments ?
					needed_segments : view->max_segments;
		summary.first_chunk_bytes = requested_remaining <
					    view->max_chunk_bytes ?
					    requested_remaining :
					    view->max_chunk_bytes;
		issued_bytes_u64 = (zigux_u64)summary.segment_count *
				   (zigux_u64)view->max_chunk_bytes;
		if (issued_bytes_u64 > requested_remaining)
			issued_bytes_u64 = requested_remaining;
		summary.issued_bytes = (zigux_u32)issued_bytes_u64;
		summary.remaining_bytes = requested_remaining -
					  summary.issued_bytes;
		if (summary.segment_count == 0) {
			summary.final_chunk_bytes = 0;
		} else if (summary.segment_count == 1) {
			summary.final_chunk_bytes = summary.issued_bytes;
		} else {
			summary.final_chunk_bytes =
				summary.issued_bytes -
				(view->max_chunk_bytes *
				 (summary.segment_count - 1));
		}
		summary.next_offset = summary.start_offset +
				      summary.issued_bytes;
		if (summary.remaining_bytes == 0)
			summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_COMPLETES;
		else
			summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_CONTINUABLE;
	} else if ((summary.flags & ZIGUX_CHRDEV_XFER_FLAG_DISPATCHABLE) &&
		   requested_remaining == 0) {
		summary.flags |= ZIGUX_CHRDEV_XFER_FLAG_COMPLETES;
	}

	return summary;
}

static inline struct zigux_chrdev_resume_view
zigux_chrdev_resume_view_from_bits(const unsigned long *bits, zigux_u32 major,
				   zigux_u32 first_minor, zigux_u32 minor_count,
				   zigux_u32 max_scan, zigux_u32 request_count,
				   zigux_u32 policy, zigux_u32 target_minor,
				   zigux_u32 requested_mode,
				   zigux_u32 supported_mode,
				   zigux_u32 available_ops, zigux_u32 io_op,
				   zigux_u32 requested_bytes,
				   zigux_u32 max_chunk_bytes,
				   zigux_u64 file_offset,
				   zigux_u32 bytes_completed,
				   zigux_u32 max_segments,
				   zigux_u32 resume_passes)
{
	return (struct zigux_chrdev_resume_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_resume_view_valid(const struct zigux_chrdev_resume_view *view)
{
	struct zigux_chrdev_xfer_view xfer_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->resume_passes == 0)
		return false;

	xfer_view = (struct zigux_chrdev_xfer_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.reserved = 0,
	};
	return zigux_chrdev_xfer_view_valid(&xfer_view);
}

static inline struct zigux_chrdev_xfer_view
zigux_chrdev_resume_as_chrdev_xfer(const struct zigux_chrdev_resume_view *view)
{
	if (!zigux_chrdev_resume_view_valid(view))
		return (struct zigux_chrdev_xfer_view){
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		};

	return (struct zigux_chrdev_xfer_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.reserved = 0,
	};
}

static inline zigux_u32
zigux_chrdev_resume_map_xfer_flags(zigux_u32 xfer_flags)
{
	zigux_u32 flags = 0;

	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_TRUNCATED)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_TRUNCATED;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_FOUND)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_FOUND;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_EXHAUSTED)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_EXHAUSTED;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_HIT)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_HIT;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_PERMITTED)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_PERMITTED;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_DENIED)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_DENIED;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_ROUTABLE)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_ROUTABLE;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_BLOCKED)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_BLOCKED;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_DISPATCHABLE)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_DISPATCHABLE;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_RESUMED)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_RESUMED;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_CONTINUABLE)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_CONTINUABLE;
	if (xfer_flags & ZIGUX_CHRDEV_XFER_FLAG_COMPLETES)
		flags |= ZIGUX_CHRDEV_RESUME_FLAG_COMPLETES;
	return flags;
}

static inline struct zigux_chrdev_resume_summary
zigux_chrdev_resume_summarize(const struct zigux_chrdev_resume_view *view)
{
	struct zigux_chrdev_resume_summary summary = {
		0, 0, 0, ZIGUX_CHRDEV_RESUME_INDEX_NONE, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0
	};
	zigux_u32 current_completed;
	zigux_u32 issued_total;
	zigux_u32 pass_index;
	struct zigux_chrdev_xfer_view xfer_view;

	if (!zigux_chrdev_resume_view_valid(view))
		return summary;

	summary.major = view->major;
	summary.target_minor = view->target_minor;
	summary.io_op = view->io_op;
	summary.requested_bytes = view->requested_bytes;
	summary.start_offset = view->file_offset + view->bytes_completed;
	summary.next_offset = summary.start_offset;
	summary.initial_bytes_completed = view->bytes_completed;
	summary.final_bytes_completed = view->bytes_completed;
	current_completed = view->bytes_completed;
	issued_total = 0;
	xfer_view = zigux_chrdev_resume_as_chrdev_xfer(view);

	for (pass_index = 0; pass_index < view->resume_passes; ++pass_index) {
		struct zigux_chrdev_xfer_summary pass_summary;

		xfer_view.bytes_completed = current_completed;
		pass_summary = zigux_chrdev_xfer_summarize(&xfer_view);
		summary.selected_count = pass_summary.selected_count;
		summary.resolved_index = pass_summary.resolved_index ==
						 ZIGUX_CHRDEV_XFER_INDEX_NONE ?
						 ZIGUX_CHRDEV_RESUME_INDEX_NONE :
						 pass_summary.resolved_index;
		summary.resolved_dev = pass_summary.resolved_dev;
		summary.granted_mode = pass_summary.granted_mode;
		summary.entry_ops = pass_summary.entry_ops;
		summary.data_ops = pass_summary.data_ops;
		summary.exit_ops = pass_summary.exit_ops;
		summary.blocked_ops = pass_summary.blocked_ops;
		summary.flags |=
			zigux_chrdev_resume_map_xfer_flags(pass_summary.flags);

		if (pass_summary.issued_bytes == 0) {
			if (pass_summary.remaining_bytes != 0)
				summary.flags |=
					ZIGUX_CHRDEV_RESUME_FLAG_STALLED;
			break;
		}

		++summary.pass_count;
		issued_total += pass_summary.issued_bytes;
		current_completed += pass_summary.issued_bytes;
		summary.final_bytes_completed = current_completed;
		summary.next_offset = pass_summary.next_offset;

		if (pass_summary.remaining_bytes == 0) {
			summary.flags |= ZIGUX_CHRDEV_RESUME_FLAG_COMPLETE_OK;
			break;
		}
	}

	if (issued_total != 0)
		summary.flags |= ZIGUX_CHRDEV_RESUME_FLAG_PROGRESSED;
	summary.issued_bytes = issued_total;
	summary.remaining_bytes = view->requested_bytes - current_completed;
	return summary;
}

static inline struct zigux_chrdev_retry_view
zigux_chrdev_retry_view_from_bits(const unsigned long *bits, zigux_u32 major,
				  zigux_u32 first_minor, zigux_u32 minor_count,
				  zigux_u32 max_scan, zigux_u32 request_count,
				  zigux_u32 policy, zigux_u32 target_minor,
				  zigux_u32 requested_mode,
				  zigux_u32 supported_mode,
				  zigux_u32 available_ops, zigux_u32 io_op,
				  zigux_u32 requested_bytes,
				  zigux_u32 max_chunk_bytes,
				  zigux_u64 file_offset,
				  zigux_u32 bytes_completed,
				  zigux_u32 max_segments,
				  zigux_u32 resume_passes,
				  zigux_u32 retry_budget,
				  zigux_u32 stall_budget,
				  zigux_u32 backoff_quanta)
{
	return (struct zigux_chrdev_retry_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_retry_view_valid(const struct zigux_chrdev_retry_view *view)
{
	struct zigux_chrdev_resume_view resume_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;

	resume_view = (struct zigux_chrdev_resume_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.reserved = 0,
	};
	return zigux_chrdev_resume_view_valid(&resume_view);
}

static inline struct zigux_chrdev_resume_view
zigux_chrdev_retry_as_chrdev_resume(const struct zigux_chrdev_retry_view *view)
{
	if (!zigux_chrdev_retry_view_valid(view))
		return (struct zigux_chrdev_resume_view){
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		};

	return (struct zigux_chrdev_resume_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.reserved = 0,
	};
}

static inline zigux_u32
zigux_chrdev_retry_map_resume_flags(zigux_u32 resume_flags)
{
	zigux_u32 flags = 0;

	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_TRUNCATED)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_TRUNCATED;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_FOUND)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_FOUND;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_EXHAUSTED)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_EXHAUSTED;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_HIT)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_HIT;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_PERMITTED)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_PERMITTED;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_DENIED)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_DENIED;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_ROUTABLE)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_ROUTABLE;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_BLOCKED)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_BLOCKED;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_DISPATCHABLE)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_DISPATCHABLE;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_RESUMED)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_RESUMED;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_CONTINUABLE)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_CONTINUABLE;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_COMPLETES)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_COMPLETES;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_PROGRESSED)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_PROGRESSED;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_STALLED)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_STALLED;
	if (resume_flags & ZIGUX_CHRDEV_RESUME_FLAG_COMPLETE_OK)
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_COMPLETE_OK;
	return flags;
}

static inline zigux_u32 zigux_chrdev_retry_ceil_div(zigux_u32 value,
						     zigux_u32 step)
{
	if (value == 0)
		return 0;
	return 1U + ((value - 1U) / step);
}

static inline struct zigux_chrdev_retry_summary
zigux_chrdev_retry_summarize(const struct zigux_chrdev_retry_view *view)
{
	struct zigux_chrdev_retry_summary summary = {
		0, 0, 0, ZIGUX_CHRDEV_RETRY_INDEX_NONE, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
	};
	struct zigux_chrdev_resume_view resume_view;
	struct zigux_chrdev_resume_summary resume_summary;
	zigux_u32 flags;
	zigux_u32 stall_count = 0;
	zigux_u32 remaining;
	zigux_u32 progress_quantum = 0;
	zigux_u32 retry_count = 0;
	zigux_u32 remaining_retry_budget;
	zigux_u32 backoff_ticks = 0;
	zigux_u32 needed_retries = 0;
	bool retryable = false;

	if (!zigux_chrdev_retry_view_valid(view))
		return summary;

	resume_view = zigux_chrdev_retry_as_chrdev_resume(view);
	resume_summary = zigux_chrdev_resume_summarize(&resume_view);
	flags = zigux_chrdev_retry_map_resume_flags(resume_summary.flags);
	if (flags & ZIGUX_CHRDEV_RETRY_FLAG_STALLED)
		stall_count = 1;
	remaining = resume_summary.remaining_bytes;
	if (resume_summary.pass_count != 0 && resume_summary.issued_bytes != 0)
		progress_quantum =
			zigux_chrdev_retry_ceil_div(resume_summary.issued_bytes,
						     resume_summary.pass_count);
	remaining_retry_budget = view->retry_budget;

	if (remaining != 0 &&
	    (flags & ZIGUX_CHRDEV_RETRY_FLAG_PERMITTED) &&
	    !(flags & ZIGUX_CHRDEV_RETRY_FLAG_DENIED) &&
	    !(flags & ZIGUX_CHRDEV_RETRY_FLAG_EXHAUSTED)) {
		if ((flags & ZIGUX_CHRDEV_RETRY_FLAG_CONTINUABLE) &&
		    progress_quantum != 0) {
			retryable = true;
			needed_retries =
				zigux_chrdev_retry_ceil_div(remaining,
							     progress_quantum);
		} else if (flags & ZIGUX_CHRDEV_RETRY_FLAG_STALLED) {
			retryable = true;
			needed_retries = 1;
		}
	}

	if (retryable) {
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_RETRYABLE;
		if (view->retry_budget == 0 || stall_count > view->stall_budget) {
			flags |= ZIGUX_CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED;
			flags |= ZIGUX_CHRDEV_RETRY_FLAG_FAILS;
			remaining_retry_budget = 0;
		} else {
			retry_count = needed_retries < view->retry_budget ?
				      needed_retries : view->retry_budget;
			if (retry_count != 0) {
				flags |= ZIGUX_CHRDEV_RETRY_FLAG_RETRY_PLANNED;
				remaining_retry_budget =
					view->retry_budget - retry_count;
				if (stall_count != 0 && view->backoff_quanta != 0) {
					flags |= ZIGUX_CHRDEV_RETRY_FLAG_BACKOFF_APPLIED;
					backoff_ticks = retry_count * view->backoff_quanta;
				}
			}
			if (needed_retries > view->retry_budget)
				flags |= ZIGUX_CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED;
		}
	} else if (remaining != 0 &&
		   ((flags & ZIGUX_CHRDEV_RETRY_FLAG_DENIED) ||
		    (flags & ZIGUX_CHRDEV_RETRY_FLAG_EXHAUSTED) ||
		    (flags & ZIGUX_CHRDEV_RETRY_FLAG_BLOCKED) ||
		    (flags & ZIGUX_CHRDEV_RETRY_FLAG_STALLED))) {
		flags |= ZIGUX_CHRDEV_RETRY_FLAG_FAILS;
		if (flags & ZIGUX_CHRDEV_RETRY_FLAG_EXHAUSTED) {
			flags |= ZIGUX_CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED;
			remaining_retry_budget = 0;
		}
	}

	summary.major = resume_summary.major;
	summary.target_minor = resume_summary.target_minor;
	summary.selected_count = resume_summary.selected_count;
	summary.resolved_index =
		resume_summary.resolved_index == ZIGUX_CHRDEV_RESUME_INDEX_NONE ?
		ZIGUX_CHRDEV_RETRY_INDEX_NONE :
		resume_summary.resolved_index;
	summary.resolved_dev = resume_summary.resolved_dev;
	summary.granted_mode = resume_summary.granted_mode;
	summary.io_op = resume_summary.io_op;
	summary.requested_bytes = resume_summary.requested_bytes;
	summary.start_offset = resume_summary.start_offset;
	summary.next_offset = resume_summary.next_offset;
	summary.initial_bytes_completed = resume_summary.initial_bytes_completed;
	summary.final_bytes_completed = resume_summary.final_bytes_completed;
	summary.pass_count = resume_summary.pass_count;
	summary.issued_bytes = resume_summary.issued_bytes;
	summary.remaining_bytes = resume_summary.remaining_bytes;
	summary.entry_ops = resume_summary.entry_ops;
	summary.data_ops = resume_summary.data_ops;
	summary.exit_ops = resume_summary.exit_ops;
	summary.blocked_ops = resume_summary.blocked_ops;
	summary.retry_count = retry_count;
	summary.stall_count = stall_count;
	summary.remaining_retry_budget = remaining_retry_budget;
	summary.backoff_ticks = backoff_ticks;
	summary.flags = flags;
	return summary;
}

static inline struct zigux_chrdev_requeue_view
zigux_chrdev_requeue_view_from_bits(const unsigned long *bits, zigux_u32 major,
				     zigux_u32 first_minor, zigux_u32 minor_count,
				     zigux_u32 max_scan, zigux_u32 request_count,
				     zigux_u32 policy, zigux_u32 target_minor,
				     zigux_u32 requested_mode,
				     zigux_u32 supported_mode,
				     zigux_u32 available_ops, zigux_u32 io_op,
				     zigux_u32 requested_bytes,
				     zigux_u32 max_chunk_bytes,
				     zigux_u64 file_offset,
				     zigux_u32 bytes_completed,
				     zigux_u32 max_segments,
				     zigux_u32 resume_passes,
				     zigux_u32 retry_budget,
				     zigux_u32 stall_budget,
				     zigux_u32 backoff_quanta,
				     zigux_u32 queue_depth,
				     zigux_u32 queue_capacity,
				     zigux_u32 requeue_budget)
{
	return (struct zigux_chrdev_requeue_view){
		.bits_addr = (unsigned long)bits,
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_requeue_view_valid(const struct zigux_chrdev_requeue_view *view)
{
	struct zigux_chrdev_retry_view retry_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->queue_depth > view->queue_capacity)
		return false;

	retry_view = (struct zigux_chrdev_retry_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.reserved = 0,
	};
	return zigux_chrdev_retry_view_valid(&retry_view);
}

static inline struct zigux_chrdev_retry_view
zigux_chrdev_requeue_as_chrdev_retry(const struct zigux_chrdev_requeue_view *view)
{
	if (!zigux_chrdev_requeue_view_valid(view))
		return (struct zigux_chrdev_retry_view){
			.bits_addr = 0,
			.major = 0,
			.first_minor = 0,
			.minor_count = 0,
			.max_scan = 0,
			.request_count = 0,
			.policy = 0,
			.target_minor = 0,
			.requested_mode = 0,
			.supported_mode = 0,
			.available_ops = 0,
			.io_op = 0,
			.requested_bytes = 0,
			.max_chunk_bytes = 0,
			.file_offset = 0,
			.bytes_completed = 0,
			.max_segments = 0,
			.resume_passes = 0,
			.retry_budget = 0,
			.stall_budget = 0,
			.backoff_quanta = 0,
			.reserved = 0,
		};

	return (struct zigux_chrdev_retry_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.reserved = 0,
	};
}

static inline zigux_u32
zigux_chrdev_requeue_map_retry_flags(zigux_u32 retry_flags)
{
	zigux_u32 flags = 0;

	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_TRUNCATED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_TRUNCATED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_FOUND)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_FOUND;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_EXHAUSTED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_EXHAUSTED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_HIT)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_HIT;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_PERMITTED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_PERMITTED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_DENIED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_DENIED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_ROUTABLE)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_ROUTABLE;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_BLOCKED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_BLOCKED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_DISPATCHABLE)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_DISPATCHABLE;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_RESUMED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_RESUMED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_CONTINUABLE)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_CONTINUABLE;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_COMPLETES)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETES;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_PROGRESSED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_PROGRESSED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_STALLED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_STALLED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_COMPLETE_OK)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETE_OK;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_RETRYABLE)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_RETRYABLE;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_RETRY_PLANNED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_RETRY_PLANNED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_RETRY_EXHAUSTED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_RETRY_EXHAUSTED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_BACKOFF_APPLIED)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_BACKOFF_APPLIED;
	if (retry_flags & ZIGUX_CHRDEV_RETRY_FLAG_FAILS)
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_FAILS;
	return flags;
}

static inline zigux_u32
zigux_chrdev_requeue_progress_quantum(const struct zigux_chrdev_retry_summary *summary)
{
	if (summary->pass_count == 0 || summary->issued_bytes == 0)
		return 0;
	return zigux_chrdev_retry_ceil_div(summary->issued_bytes,
					   summary->pass_count);
}

static inline zigux_u32
zigux_chrdev_requeue_projected_remaining(const struct zigux_chrdev_retry_summary *summary)
{
	zigux_u32 quantum;
	zigux_u32 projected_progress;

	if (summary->remaining_bytes == 0)
		return 0;
	if (summary->retry_count == 0)
		return summary->remaining_bytes;

	quantum = zigux_chrdev_requeue_progress_quantum(summary);
	if (quantum == 0)
		return summary->remaining_bytes;

	projected_progress = summary->retry_count * quantum;
	if (projected_progress > summary->remaining_bytes)
		projected_progress = summary->remaining_bytes;
	return summary->remaining_bytes - projected_progress;
}

static inline struct zigux_chrdev_requeue_summary
zigux_chrdev_requeue_summarize(const struct zigux_chrdev_requeue_view *view)
{
	struct zigux_chrdev_requeue_summary summary = {
		0, 0, 0, ZIGUX_CHRDEV_REQUEUE_INDEX_NONE, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
	};
	struct zigux_chrdev_retry_view retry_view;
	struct zigux_chrdev_retry_summary retry_summary;
	zigux_u32 flags;
	zigux_u32 projected_remaining_bytes;
	zigux_u32 queue_depth_after;
	zigux_u32 requeue_count = 0;
	zigux_u32 remaining_requeue_budget;

	if (!zigux_chrdev_requeue_view_valid(view))
		return summary;

	retry_view = zigux_chrdev_requeue_as_chrdev_retry(view);
	retry_summary = zigux_chrdev_retry_summarize(&retry_view);
	flags = zigux_chrdev_requeue_map_retry_flags(retry_summary.flags);
	projected_remaining_bytes =
		zigux_chrdev_requeue_projected_remaining(&retry_summary);
	queue_depth_after = view->queue_depth;
	remaining_requeue_budget = view->requeue_budget;

	if (projected_remaining_bytes == 0) {
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETE;
	} else if ((flags & ZIGUX_CHRDEV_REQUEUE_FLAG_DENIED) ||
		   (flags & ZIGUX_CHRDEV_REQUEUE_FLAG_EXHAUSTED)) {
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_DROPPED;
	} else {
		flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_REQUEUEABLE;
		if (view->requeue_budget == 0) {
			remaining_requeue_budget = 0;
			flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_DROPPED;
		} else if (view->queue_depth >= view->queue_capacity) {
			flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_SATURATED;
			flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_DROPPED;
		} else {
			requeue_count = 1;
			queue_depth_after = view->queue_depth + 1;
			remaining_requeue_budget = view->requeue_budget - 1;
			flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED;
			if (retry_summary.backoff_ticks != 0 ||
			    retry_summary.stall_count != 0)
				flags |= ZIGUX_CHRDEV_REQUEUE_FLAG_DELAYED;
		}
	}

	summary.major = retry_summary.major;
	summary.target_minor = retry_summary.target_minor;
	summary.selected_count = retry_summary.selected_count;
	summary.resolved_index =
		retry_summary.resolved_index == ZIGUX_CHRDEV_RETRY_INDEX_NONE ?
		ZIGUX_CHRDEV_REQUEUE_INDEX_NONE :
		retry_summary.resolved_index;
	summary.resolved_dev = retry_summary.resolved_dev;
	summary.granted_mode = retry_summary.granted_mode;
	summary.io_op = retry_summary.io_op;
	summary.requested_bytes = retry_summary.requested_bytes;
	summary.start_offset = retry_summary.start_offset;
	summary.next_offset = retry_summary.next_offset;
	summary.initial_bytes_completed = retry_summary.initial_bytes_completed;
	summary.final_bytes_completed = retry_summary.final_bytes_completed;
	summary.pass_count = retry_summary.pass_count;
	summary.issued_bytes = retry_summary.issued_bytes;
	summary.remaining_bytes = retry_summary.remaining_bytes;
	summary.projected_remaining_bytes = projected_remaining_bytes;
	summary.entry_ops = retry_summary.entry_ops;
	summary.data_ops = retry_summary.data_ops;
	summary.exit_ops = retry_summary.exit_ops;
	summary.blocked_ops = retry_summary.blocked_ops;
	summary.retry_count = retry_summary.retry_count;
	summary.stall_count = retry_summary.stall_count;
	summary.requeue_count = requeue_count;
	summary.queue_depth_before = view->queue_depth;
	summary.queue_depth_after = queue_depth_after;
	summary.remaining_retry_budget = retry_summary.remaining_retry_budget;
	summary.remaining_requeue_budget = remaining_requeue_budget;
	summary.backoff_ticks = retry_summary.backoff_ticks;
	summary.flags = flags;
	return summary;
}

static inline struct zigux_chrdev_complete_view
zigux_chrdev_complete_view_from_bits(const unsigned long *bits, zigux_u32 major,
				     zigux_u32 first_minor, zigux_u32 minor_count,
				     zigux_u32 max_scan, zigux_u32 request_count,
				     zigux_u32 policy, zigux_u32 target_minor,
				     zigux_u32 requested_mode,
				     zigux_u32 supported_mode,
				     zigux_u32 available_ops, zigux_u32 io_op,
				     zigux_u32 requested_bytes,
				     zigux_u32 max_chunk_bytes,
				     zigux_u64 file_offset,
				     zigux_u32 bytes_completed,
				     zigux_u32 max_segments,
				     zigux_u32 resume_passes,
				     zigux_u32 retry_budget,
				     zigux_u32 stall_budget,
				     zigux_u32 backoff_quanta,
				     zigux_u32 queue_depth,
				     zigux_u32 queue_capacity,
				     zigux_u32 requeue_budget,
				     zigux_u64 completion_cookie,
				     zigux_u32 completion_budget)
{
	return (struct zigux_chrdev_complete_view){
		.bits_addr = (unsigned long)bits,
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_complete_view_valid(const struct zigux_chrdev_complete_view *view)
{
	struct zigux_chrdev_requeue_view requeue_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;

	requeue_view = (struct zigux_chrdev_requeue_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.reserved = 0,
	};

	return zigux_chrdev_requeue_view_valid(&requeue_view);
}

static inline struct zigux_chrdev_requeue_view
zigux_chrdev_complete_as_chrdev_requeue(const struct zigux_chrdev_complete_view *view)
{
	if (!zigux_chrdev_complete_view_valid(view))
		return (struct zigux_chrdev_requeue_view){
			.bits_addr = 0,
			.major = 0,
			.first_minor = 0,
			.minor_count = 0,
			.max_scan = 0,
			.request_count = 0,
			.policy = 0,
			.target_minor = 0,
			.requested_mode = 0,
			.supported_mode = 0,
			.available_ops = 0,
			.io_op = 0,
			.requested_bytes = 0,
			.max_chunk_bytes = 0,
			.file_offset = 0,
			.bytes_completed = 0,
			.max_segments = 0,
			.resume_passes = 0,
			.retry_budget = 0,
			.stall_budget = 0,
			.backoff_quanta = 0,
			.queue_depth = 0,
			.queue_capacity = 0,
			.requeue_budget = 0,
			.reserved = 0,
		};

	return (struct zigux_chrdev_requeue_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.reserved = 0,
	};
}

static inline zigux_u32
zigux_chrdev_complete_map_requeue_flags(zigux_u32 requeue_flags)
{
	zigux_u32 flags = 0;

	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_TRUNCATED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_TRUNCATED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_FOUND)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_FOUND;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_EXHAUSTED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_EXHAUSTED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_HIT)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_HIT;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_PERMITTED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_PERMITTED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_DENIED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_DENIED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_ROUTABLE)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_ROUTABLE;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_BLOCKED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_BLOCKED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_DISPATCHABLE)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_DISPATCHABLE;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_RESUMED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_RESUMED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_CONTINUABLE)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_CONTINUABLE;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETES)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETES;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_PROGRESSED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_PROGRESSED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_STALLED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_STALLED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETE_OK)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE_OK;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_RETRYABLE)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_RETRYABLE;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_RETRY_PLANNED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_RETRY_PLANNED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_RETRY_EXHAUSTED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_RETRY_EXHAUSTED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_BACKOFF_APPLIED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_BACKOFF_APPLIED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_FAILS)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_FAILS;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_REQUEUEABLE)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUEABLE;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_REQUEUE_PLANNED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_DELAYED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_DELAYED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_SATURATED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_SATURATED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_DROPPED)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_DROPPED;
	if (requeue_flags & ZIGUX_CHRDEV_REQUEUE_FLAG_COMPLETE)
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE;
	return flags;
}

static inline struct zigux_chrdev_complete_summary
zigux_chrdev_complete_summarize(const struct zigux_chrdev_complete_view *view)
{
	struct zigux_chrdev_complete_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_COMPLETE_INDEX_NONE,
	};
	struct zigux_chrdev_requeue_view requeue_view;
	struct zigux_chrdev_requeue_summary requeue_summary;
	zigux_u32 flags;
	zigux_u32 completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE;
	zigux_u32 completion_count = 0;
	zigux_u32 deferred_count = 0;
	zigux_u32 failure_count = 0;
	zigux_u32 remaining_completion_budget;

	if (!zigux_chrdev_complete_view_valid(view))
		return summary;

	requeue_view = zigux_chrdev_complete_as_chrdev_requeue(view);
	requeue_summary = zigux_chrdev_requeue_summarize(&requeue_view);
	flags = zigux_chrdev_complete_map_requeue_flags(requeue_summary.flags);
	remaining_completion_budget = view->completion_budget;

	if (flags & ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE) {
		completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_OK;
		if (view->completion_budget != 0) {
			completion_count = 1;
			remaining_completion_budget = view->completion_budget - 1;
			flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED;
			flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_FINALIZED;
		} else {
			deferred_count = 1;
			flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION;
		}
	} else if (flags & ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED) {
		completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_DEFERRED;
		deferred_count = 1;
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION;
	} else if (flags & (ZIGUX_CHRDEV_COMPLETE_FLAG_DENIED |
			    ZIGUX_CHRDEV_COMPLETE_FLAG_EXHAUSTED |
			    ZIGUX_CHRDEV_COMPLETE_FLAG_DROPPED |
			    ZIGUX_CHRDEV_COMPLETE_FLAG_SATURATED |
			    ZIGUX_CHRDEV_COMPLETE_FLAG_FAILS)) {
		completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_FAILED;
		failure_count = 1;
		flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION;
		if (view->completion_budget != 0) {
			completion_count = 1;
			remaining_completion_budget = view->completion_budget - 1;
			flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED;
			flags |= ZIGUX_CHRDEV_COMPLETE_FLAG_FINALIZED;
		}
	}

	summary.major = requeue_summary.major;
	summary.target_minor = requeue_summary.target_minor;
	summary.selected_count = requeue_summary.selected_count;
	summary.resolved_index =
		requeue_summary.resolved_index == ZIGUX_CHRDEV_REQUEUE_INDEX_NONE ?
		ZIGUX_CHRDEV_COMPLETE_INDEX_NONE :
		requeue_summary.resolved_index;
	summary.resolved_dev = requeue_summary.resolved_dev;
	summary.granted_mode = requeue_summary.granted_mode;
	summary.io_op = requeue_summary.io_op;
	summary.requested_bytes = requeue_summary.requested_bytes;
	summary.start_offset = requeue_summary.start_offset;
	summary.next_offset = requeue_summary.next_offset;
	summary.initial_bytes_completed = requeue_summary.initial_bytes_completed;
	summary.final_bytes_completed = requeue_summary.final_bytes_completed;
	summary.pass_count = requeue_summary.pass_count;
	summary.issued_bytes = requeue_summary.issued_bytes;
	summary.remaining_bytes = requeue_summary.remaining_bytes;
	summary.projected_remaining_bytes = requeue_summary.projected_remaining_bytes;
	summary.entry_ops = requeue_summary.entry_ops;
	summary.data_ops = requeue_summary.data_ops;
	summary.exit_ops = requeue_summary.exit_ops;
	summary.blocked_ops = requeue_summary.blocked_ops;
	summary.retry_count = requeue_summary.retry_count;
	summary.stall_count = requeue_summary.stall_count;
	summary.requeue_count = requeue_summary.requeue_count;
	summary.queue_depth_before = requeue_summary.queue_depth_before;
	summary.queue_depth_after = requeue_summary.queue_depth_after;
	summary.remaining_retry_budget = requeue_summary.remaining_retry_budget;
	summary.remaining_requeue_budget = requeue_summary.remaining_requeue_budget;
	summary.backoff_ticks = requeue_summary.backoff_ticks;
	summary.completion_cookie = view->completion_cookie;
	summary.completion_status = completion_status;
	summary.completion_count = completion_count;
	summary.deferred_count = deferred_count;
	summary.failure_count = failure_count;
	summary.remaining_completion_budget = remaining_completion_budget;
	summary.flags = flags;
	return summary;
}

static inline struct zigux_chrdev_notify_view
zigux_chrdev_notify_view_from_bits(const unsigned long *bits, zigux_u32 major,
				   zigux_u32 first_minor, zigux_u32 minor_count,
				   zigux_u32 max_scan, zigux_u32 request_count,
				   zigux_u32 policy, zigux_u32 target_minor,
				   zigux_u32 requested_mode,
				   zigux_u32 supported_mode,
				   zigux_u32 available_ops, zigux_u32 io_op,
				   zigux_u32 requested_bytes,
				   zigux_u32 max_chunk_bytes,
				   zigux_u64 file_offset,
				   zigux_u32 bytes_completed,
				   zigux_u32 max_segments,
				   zigux_u32 resume_passes,
				   zigux_u32 retry_budget,
				   zigux_u32 stall_budget,
				   zigux_u32 backoff_quanta,
				   zigux_u32 queue_depth,
				   zigux_u32 queue_capacity,
				   zigux_u32 requeue_budget,
				   zigux_u64 completion_cookie,
				   zigux_u32 completion_budget,
				   zigux_u32 notify_mask,
				   zigux_u32 notify_budget,
				   zigux_u64 notify_cookie)
{
	return (struct zigux_chrdev_notify_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_view_valid(const struct zigux_chrdev_notify_view *view)
{
	struct zigux_chrdev_complete_view complete_view;

	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if (view->notify_mask &
	    ~(ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS |
	      ZIGUX_CHRDEV_NOTIFY_MASK_DEFERRED |
	      ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE))
		return false;

	complete_view = (struct zigux_chrdev_complete_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.reserved = 0,
	};
	return zigux_chrdev_complete_view_valid(&complete_view);
}

static inline struct zigux_chrdev_complete_view
zigux_chrdev_notify_as_chrdev_complete(const struct zigux_chrdev_notify_view *view)
{
	if (!zigux_chrdev_notify_view_valid(view))
		return (struct zigux_chrdev_complete_view){0};

	return (struct zigux_chrdev_complete_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.reserved = 0,
	};
}

static inline zigux_u32
zigux_chrdev_notify_map_complete_flags(zigux_u32 complete_flags)
{
	zigux_u32 flags = 0;

	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_TRUNCATED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_TRUNCATED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_FOUND)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_FOUND;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_EXHAUSTED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_EXHAUSTED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_HIT)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_HIT;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_PERMITTED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_PERMITTED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_DENIED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_DENIED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_ROUTABLE)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_ROUTABLE;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_BLOCKED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_BLOCKED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_DISPATCHABLE)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_DISPATCHABLE;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_RESUMED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_RESUMED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_CONTINUABLE)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_CONTINUABLE;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETES)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_COMPLETES;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_PROGRESSED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_PROGRESSED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_STALLED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_STALLED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE_OK)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_COMPLETE_OK;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_RETRYABLE)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_RETRYABLE;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_RETRY_PLANNED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_RETRY_PLANNED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_RETRY_EXHAUSTED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_RETRY_EXHAUSTED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_BACKOFF_APPLIED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_BACKOFF_APPLIED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_FAILS)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_FAILS;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUEABLE)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_REQUEUEABLE;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_REQUEUE_PLANNED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_REQUEUE_PLANNED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_DELAYED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_DELAYED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_SATURATED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_SATURATED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_DROPPED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_DROPPED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETE)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_COMPLETE;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_COMPLETION_PLANNED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_COMPLETION_PLANNED;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_DEFERRED_COMPLETION)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_DEFERRED_COMPLETION;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_FAILURE_COMPLETION)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_FAILURE_COMPLETION;
	if (complete_flags & ZIGUX_CHRDEV_COMPLETE_FLAG_FINALIZED)
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_FINALIZED;
	return flags;
}

static inline zigux_u32
zigux_chrdev_notify_status_mask(zigux_u32 completion_status)
{
	switch (completion_status) {
	case ZIGUX_CHRDEV_COMPLETE_STATUS_OK:
		return ZIGUX_CHRDEV_NOTIFY_MASK_SUCCESS;
	case ZIGUX_CHRDEV_COMPLETE_STATUS_DEFERRED:
		return ZIGUX_CHRDEV_NOTIFY_MASK_DEFERRED;
	case ZIGUX_CHRDEV_COMPLETE_STATUS_FAILED:
		return ZIGUX_CHRDEV_NOTIFY_MASK_FAILURE;
	default:
		return 0;
	}
}

static inline struct zigux_chrdev_notify_summary
zigux_chrdev_notify_summarize(const struct zigux_chrdev_notify_view *view)
{
	struct zigux_chrdev_notify_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
	};
	struct zigux_chrdev_complete_view complete_view;
	struct zigux_chrdev_complete_summary complete_summary;
	zigux_u32 flags;
	zigux_u32 matched_notify_mask;
	zigux_u32 notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE;
	zigux_u32 notify_count = 0;
	zigux_u32 deferred_notify_count = 0;
	zigux_u32 dropped_notify_count = 0;
	zigux_u32 remaining_notify_budget;

	if (!zigux_chrdev_notify_view_valid(view))
		return summary;

	complete_view = zigux_chrdev_notify_as_chrdev_complete(view);
	complete_summary = zigux_chrdev_complete_summarize(&complete_view);
	flags = zigux_chrdev_notify_map_complete_flags(complete_summary.flags);
	matched_notify_mask =
		view->notify_mask &
		zigux_chrdev_notify_status_mask(complete_summary.completion_status);
	remaining_notify_budget = view->notify_budget;

	if (matched_notify_mask != 0) {
		flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_MATCHED_NOTIFY;
		switch (complete_summary.completion_status) {
		case ZIGUX_CHRDEV_COMPLETE_STATUS_DEFERRED:
			notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_DEFERRED;
			deferred_notify_count = 1;
			break;
		case ZIGUX_CHRDEV_COMPLETE_STATUS_OK:
		case ZIGUX_CHRDEV_COMPLETE_STATUS_FAILED:
			if (view->notify_budget != 0) {
				notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_DELIVERED;
				notify_count = 1;
				remaining_notify_budget = view->notify_budget - 1;
				flags |= ZIGUX_CHRDEV_NOTIFY_FLAG_NOTIFY_PLANNED;
			} else {
				notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_DROPPED;
				dropped_notify_count = 1;
			}
			break;
		default:
			break;
		}
	}

	summary.major = complete_summary.major;
	summary.target_minor = complete_summary.target_minor;
	summary.selected_count = complete_summary.selected_count;
	summary.resolved_index =
		complete_summary.resolved_index == ZIGUX_CHRDEV_COMPLETE_INDEX_NONE ?
		ZIGUX_CHRDEV_NOTIFY_INDEX_NONE :
		complete_summary.resolved_index;
	summary.resolved_dev = complete_summary.resolved_dev;
	summary.granted_mode = complete_summary.granted_mode;
	summary.io_op = complete_summary.io_op;
	summary.requested_bytes = complete_summary.requested_bytes;
	summary.start_offset = complete_summary.start_offset;
	summary.next_offset = complete_summary.next_offset;
	summary.initial_bytes_completed = complete_summary.initial_bytes_completed;
	summary.final_bytes_completed = complete_summary.final_bytes_completed;
	summary.pass_count = complete_summary.pass_count;
	summary.issued_bytes = complete_summary.issued_bytes;
	summary.remaining_bytes = complete_summary.remaining_bytes;
	summary.projected_remaining_bytes =
		complete_summary.projected_remaining_bytes;
	summary.entry_ops = complete_summary.entry_ops;
	summary.data_ops = complete_summary.data_ops;
	summary.exit_ops = complete_summary.exit_ops;
	summary.blocked_ops = complete_summary.blocked_ops;
	summary.retry_count = complete_summary.retry_count;
	summary.stall_count = complete_summary.stall_count;
	summary.requeue_count = complete_summary.requeue_count;
	summary.queue_depth_before = complete_summary.queue_depth_before;
	summary.queue_depth_after = complete_summary.queue_depth_after;
	summary.remaining_retry_budget = complete_summary.remaining_retry_budget;
	summary.remaining_requeue_budget = complete_summary.remaining_requeue_budget;
	summary.backoff_ticks = complete_summary.backoff_ticks;
	summary.completion_cookie = complete_summary.completion_cookie;
	summary.completion_status = complete_summary.completion_status;
	summary.completion_count = complete_summary.completion_count;
	summary.deferred_count = complete_summary.deferred_count;
	summary.failure_count = complete_summary.failure_count;
	summary.remaining_completion_budget =
		complete_summary.remaining_completion_budget;
	summary.notify_mask = view->notify_mask;
	summary.matched_notify_mask = matched_notify_mask;
	summary.notify_status = notify_status;
	summary.notify_count = notify_count;
	summary.deferred_notify_count = deferred_notify_count;
	summary.dropped_notify_count = dropped_notify_count;
	summary.remaining_notify_budget = remaining_notify_budget;
	summary.notify_cookie = view->notify_cookie;
	summary.flags = flags;
	return summary;
}

static inline struct zigux_chrdev_notify_policy_view
zigux_chrdev_notify_policy_view_from_bits(const unsigned long *bits,
					  zigux_u32 major,
					  zigux_u32 first_minor,
					  zigux_u32 minor_count,
					  zigux_u32 max_scan,
					  zigux_u32 request_count,
					  zigux_u32 policy,
					  zigux_u32 target_minor,
					  zigux_u32 requested_mode,
					  zigux_u32 supported_mode,
					  zigux_u32 available_ops,
					  zigux_u32 io_op,
					  zigux_u32 requested_bytes,
					  zigux_u32 max_chunk_bytes,
					  zigux_u64 file_offset,
					  zigux_u32 bytes_completed,
					  zigux_u32 max_segments,
					  zigux_u32 resume_passes,
					  zigux_u32 retry_budget,
					  zigux_u32 stall_budget,
					  zigux_u32 backoff_quanta,
					  zigux_u32 queue_depth,
					  zigux_u32 queue_capacity,
					  zigux_u32 requeue_budget,
					  zigux_u64 completion_cookie,
					  zigux_u32 completion_budget,
					  zigux_u32 notify_mask,
					  zigux_u32 notify_budget,
					  zigux_u64 notify_cookie,
					  zigux_u32 policy_flags)
{
	return (struct zigux_chrdev_notify_policy_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_policy_view_valid(const struct zigux_chrdev_notify_policy_view *view)
{
	struct zigux_chrdev_notify_view notify_view;

	if (!view)
		return false;
	if (view->reserved != 0 || view->policy_reserved != 0)
		return false;
	if (view->policy_flags &
	    ~(ZIGUX_CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED |
	      ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE |
	      ZIGUX_CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE))
		return false;

	notify_view = (struct zigux_chrdev_notify_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
	};
	return zigux_chrdev_notify_view_valid(&notify_view);
}

static inline struct zigux_chrdev_notify_view
zigux_chrdev_notify_policy_as_chrdev_notify(
	const struct zigux_chrdev_notify_policy_view *view)
{
	if (!view || view->reserved != 0 || view->policy_reserved != 0)
		return (struct zigux_chrdev_notify_view){0};

	return (struct zigux_chrdev_notify_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
	};
}

static inline struct zigux_chrdev_notify_policy_summary
zigux_chrdev_notify_policy_summarize(
	const struct zigux_chrdev_notify_policy_view *view)
{
	struct zigux_chrdev_notify_policy_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
	};
	struct zigux_chrdev_notify_view notify_view;
	struct zigux_chrdev_notify_summary notify_summary;
	zigux_u32 policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE;
	zigux_u32 policy_notify_count = 0;
	zigux_u32 policy_deferred_count = 0;
	zigux_u32 policy_suppressed_count = 0;
	zigux_u32 policy_coalesced_count = 0;
	zigux_u32 effective_policy_flags = 0;
	zigux_u64 effective_notify_cookie = 0;

	if (!zigux_chrdev_notify_policy_view_valid(view))
		return summary;

	notify_view = zigux_chrdev_notify_policy_as_chrdev_notify(view);
	notify_summary = zigux_chrdev_notify_summarize(&notify_view);

	switch (notify_summary.notify_status) {
	case ZIGUX_CHRDEV_NOTIFY_STATUS_DROPPED:
		policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED;
		policy_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_STATUS_DEFERRED:
		policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED;
		policy_deferred_count = 1;
		if (view->policy_flags & ZIGUX_CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED)
			effective_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED;
		effective_notify_cookie = notify_summary.notify_cookie;
		break;
	case ZIGUX_CHRDEV_NOTIFY_STATUS_DELIVERED:
		if (notify_summary.completion_status ==
			    ZIGUX_CHRDEV_COMPLETE_STATUS_FAILED &&
		    (view->policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE)) {
			policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED;
			policy_suppressed_count = 1;
			effective_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_POLICY_SUPPRESS_FAILURE;
			effective_notify_cookie = 0;
		} else if ((view->policy_flags &
			    ZIGUX_CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE) &&
			   notify_summary.notify_cookie != 0 &&
			   notify_summary.notify_cookie ==
				   notify_summary.completion_cookie) {
			policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_COALESCED;
			policy_coalesced_count = 1;
			effective_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_POLICY_COALESCE_COOKIE;
			effective_notify_cookie =
				notify_summary.completion_cookie;
		} else if (view->policy_flags &
			   ZIGUX_CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED) {
			policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED;
			policy_deferred_count = 1;
			effective_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_POLICY_FORCE_DEFERRED;
			effective_notify_cookie = notify_summary.notify_cookie;
		} else {
			policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED;
			policy_notify_count = 1;
			effective_notify_cookie = notify_summary.notify_cookie;
		}
		break;
	default:
		break;
	}

	summary.major = notify_summary.major;
	summary.target_minor = notify_summary.target_minor;
	summary.selected_count = notify_summary.selected_count;
	summary.resolved_index = notify_summary.resolved_index;
	summary.resolved_dev = notify_summary.resolved_dev;
	summary.granted_mode = notify_summary.granted_mode;
	summary.io_op = notify_summary.io_op;
	summary.requested_bytes = notify_summary.requested_bytes;
	summary.start_offset = notify_summary.start_offset;
	summary.next_offset = notify_summary.next_offset;
	summary.initial_bytes_completed =
		notify_summary.initial_bytes_completed;
	summary.final_bytes_completed = notify_summary.final_bytes_completed;
	summary.pass_count = notify_summary.pass_count;
	summary.issued_bytes = notify_summary.issued_bytes;
	summary.remaining_bytes = notify_summary.remaining_bytes;
	summary.projected_remaining_bytes =
		notify_summary.projected_remaining_bytes;
	summary.entry_ops = notify_summary.entry_ops;
	summary.data_ops = notify_summary.data_ops;
	summary.exit_ops = notify_summary.exit_ops;
	summary.blocked_ops = notify_summary.blocked_ops;
	summary.retry_count = notify_summary.retry_count;
	summary.stall_count = notify_summary.stall_count;
	summary.requeue_count = notify_summary.requeue_count;
	summary.queue_depth_before = notify_summary.queue_depth_before;
	summary.queue_depth_after = notify_summary.queue_depth_after;
	summary.remaining_retry_budget =
		notify_summary.remaining_retry_budget;
	summary.remaining_requeue_budget =
		notify_summary.remaining_requeue_budget;
	summary.backoff_ticks = notify_summary.backoff_ticks;
	summary.completion_cookie = notify_summary.completion_cookie;
	summary.completion_status = notify_summary.completion_status;
	summary.completion_count = notify_summary.completion_count;
	summary.deferred_count = notify_summary.deferred_count;
	summary.failure_count = notify_summary.failure_count;
	summary.remaining_completion_budget =
		notify_summary.remaining_completion_budget;
	summary.notify_mask = notify_summary.notify_mask;
	summary.matched_notify_mask = notify_summary.matched_notify_mask;
	summary.notify_status = notify_summary.notify_status;
	summary.notify_count = notify_summary.notify_count;
	summary.deferred_notify_count = notify_summary.deferred_notify_count;
	summary.dropped_notify_count = notify_summary.dropped_notify_count;
	summary.remaining_notify_budget =
		notify_summary.remaining_notify_budget;
	summary.notify_cookie = notify_summary.notify_cookie;
	summary.flags = notify_summary.flags;
	summary.policy_flags = view->policy_flags;
	summary.effective_policy_flags = effective_policy_flags;
	summary.effective_notify_cookie = effective_notify_cookie;
	summary.policy_status = policy_status;
	summary.policy_notify_count = policy_notify_count;
	summary.policy_deferred_count = policy_deferred_count;
	summary.policy_suppressed_count = policy_suppressed_count;
	summary.policy_coalesced_count = policy_coalesced_count;
	return summary;
}

static inline struct zigux_chrdev_notify_budget_view
zigux_chrdev_notify_budget_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget)
{
	return (struct zigux_chrdev_notify_budget_view){
		.bits_addr = (unsigned long)bits,
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
		.delivery_budget = delivery_budget,
		.deferred_budget = deferred_budget,
	};
}

static inline bool
zigux_chrdev_notify_budget_view_valid(
	const struct zigux_chrdev_notify_budget_view *view)
{
	struct zigux_chrdev_notify_policy_view policy_view;

	if (!view)
		return false;
	if (view->reserved != 0 || view->policy_reserved != 0)
		return false;

	policy_view = (struct zigux_chrdev_notify_policy_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
		.policy_flags = view->policy_flags,
		.policy_reserved = 0,
	};

	return zigux_chrdev_notify_policy_view_valid(&policy_view);
}

static inline struct zigux_chrdev_notify_policy_view
zigux_chrdev_notify_budget_as_chrdev_notify_policy(
	const struct zigux_chrdev_notify_budget_view *view)
{
	if (!view || view->reserved != 0 || view->policy_reserved != 0)
		return (struct zigux_chrdev_notify_policy_view){0};

	return (struct zigux_chrdev_notify_policy_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
		.policy_flags = view->policy_flags,
		.policy_reserved = 0,
	};
}

static inline struct zigux_chrdev_notify_budget_summary
zigux_chrdev_notify_budget_summarize(
	const struct zigux_chrdev_notify_budget_view *view)
{
	struct zigux_chrdev_notify_budget_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
	};
	struct zigux_chrdev_notify_policy_view policy_view;
	struct zigux_chrdev_notify_policy_summary policy_summary;

	if (!zigux_chrdev_notify_budget_view_valid(view))
		return summary;

	policy_view = zigux_chrdev_notify_budget_as_chrdev_notify_policy(view);
	policy_summary = zigux_chrdev_notify_policy_summarize(&policy_view);

	summary.major = policy_summary.major;
	summary.target_minor = policy_summary.target_minor;
	summary.selected_count = policy_summary.selected_count;
	summary.resolved_index = policy_summary.resolved_index;
	summary.resolved_dev = policy_summary.resolved_dev;
	summary.granted_mode = policy_summary.granted_mode;
	summary.io_op = policy_summary.io_op;
	summary.requested_bytes = policy_summary.requested_bytes;
	summary.start_offset = policy_summary.start_offset;
	summary.next_offset = policy_summary.next_offset;
	summary.initial_bytes_completed =
		policy_summary.initial_bytes_completed;
	summary.final_bytes_completed = policy_summary.final_bytes_completed;
	summary.pass_count = policy_summary.pass_count;
	summary.issued_bytes = policy_summary.issued_bytes;
	summary.remaining_bytes = policy_summary.remaining_bytes;
	summary.projected_remaining_bytes =
		policy_summary.projected_remaining_bytes;
	summary.entry_ops = policy_summary.entry_ops;
	summary.data_ops = policy_summary.data_ops;
	summary.exit_ops = policy_summary.exit_ops;
	summary.blocked_ops = policy_summary.blocked_ops;
	summary.retry_count = policy_summary.retry_count;
	summary.stall_count = policy_summary.stall_count;
	summary.requeue_count = policy_summary.requeue_count;
	summary.queue_depth_before = policy_summary.queue_depth_before;
	summary.queue_depth_after = policy_summary.queue_depth_after;
	summary.remaining_retry_budget =
		policy_summary.remaining_retry_budget;
	summary.remaining_requeue_budget =
		policy_summary.remaining_requeue_budget;
	summary.backoff_ticks = policy_summary.backoff_ticks;
	summary.completion_cookie = policy_summary.completion_cookie;
	summary.completion_status = policy_summary.completion_status;
	summary.completion_count = policy_summary.completion_count;
	summary.deferred_count = policy_summary.deferred_count;
	summary.failure_count = policy_summary.failure_count;
	summary.remaining_completion_budget =
		policy_summary.remaining_completion_budget;
	summary.notify_mask = policy_summary.notify_mask;
	summary.matched_notify_mask = policy_summary.matched_notify_mask;
	summary.notify_status = policy_summary.notify_status;
	summary.notify_count = policy_summary.notify_count;
	summary.deferred_notify_count = policy_summary.deferred_notify_count;
	summary.dropped_notify_count = policy_summary.dropped_notify_count;
	summary.remaining_notify_budget =
		policy_summary.remaining_notify_budget;
	summary.notify_cookie = policy_summary.notify_cookie;
	summary.flags = policy_summary.flags;
	summary.policy_flags = policy_summary.policy_flags;
	summary.effective_policy_flags =
		policy_summary.effective_policy_flags;
	summary.effective_notify_cookie =
		policy_summary.effective_notify_cookie;
	summary.policy_status = policy_summary.policy_status;
	summary.policy_notify_count = policy_summary.policy_notify_count;
	summary.policy_deferred_count =
		policy_summary.policy_deferred_count;
	summary.policy_suppressed_count =
		policy_summary.policy_suppressed_count;
	summary.policy_coalesced_count =
		policy_summary.policy_coalesced_count;
	summary.delivery_budget_before = view->delivery_budget;
	summary.delivery_budget_after = view->delivery_budget;
	summary.deferred_budget_before = view->deferred_budget;
	summary.deferred_budget_after = view->deferred_budget;

	switch (policy_summary.policy_status) {
	case ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_SUPPRESSED:
		summary.budget_status =
			ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_SUPPRESSED;
		summary.budget_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DEFERRED:
		summary.budget_flags |=
			ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.deferred_budget_after > 0) {
			summary.deferred_budget_after -= 1;
			summary.budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_USED;
			summary.budget_status =
				ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED;
			summary.budget_deferred_count = 1;
		} else {
			summary.budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED;
			summary.budget_status =
				ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED;
			summary.budget_dropped_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_DELIVERED:
	case ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_COALESCED:
		summary.budget_flags |=
			ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.delivery_budget_after > 0) {
			summary.delivery_budget_after -= 1;
			summary.budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DELIVERY_BUDGET_USED;
			summary.budget_status =
				ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_ISSUED;
			summary.budget_notify_count = 1;
		} else {
			summary.budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DELIVERY_BUDGET_EXHAUSTED;
			if (summary.deferred_budget_after > 0) {
				summary.deferred_budget_after -= 1;
				summary.budget_flags |=
					ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_USED;
				summary.budget_status =
					ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED;
				summary.budget_deferred_count = 1;
			} else {
				summary.budget_flags |=
					ZIGUX_CHRDEV_NOTIFY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED;
				summary.budget_status =
					ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED;
				summary.budget_dropped_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_view
zigux_chrdev_notify_ack_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget,
	zigux_u32 ack_mask, zigux_u32 ack_window, zigux_u64 ack_cookie,
	zigux_u32 ack_observed)
{
	return (struct zigux_chrdev_notify_ack_view){
		.bits_addr = (unsigned long)bits,
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
		.delivery_budget = delivery_budget,
		.deferred_budget = deferred_budget,
		.ack_mask = ack_mask,
		.ack_window = ack_window,
		.ack_cookie = ack_cookie,
		.ack_observed = ack_observed,
		.ack_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_view_valid(
	const struct zigux_chrdev_notify_ack_view *view)
{
	struct zigux_chrdev_notify_budget_view budget_view;

	if (!view)
		return false;
	if (view->reserved != 0 || view->policy_reserved != 0 ||
	    view->ack_reserved != 0)
		return false;

	budget_view = (struct zigux_chrdev_notify_budget_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
		.policy_flags = view->policy_flags,
		.policy_reserved = 0,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
	};

	return zigux_chrdev_notify_budget_view_valid(&budget_view);
}

static inline struct zigux_chrdev_notify_budget_view
zigux_chrdev_notify_ack_as_chrdev_notify_budget(
	const struct zigux_chrdev_notify_ack_view *view)
{
	if (!zigux_chrdev_notify_ack_view_valid(view))
		return (struct zigux_chrdev_notify_budget_view){0};

	return (struct zigux_chrdev_notify_budget_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
		.policy_flags = view->policy_flags,
		.policy_reserved = 0,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
	};
}

static inline zigux_u32
zigux_chrdev_notify_ack_match_mask(
	const struct zigux_chrdev_notify_ack_view *view,
	const struct zigux_chrdev_notify_budget_summary *budget_summary)
{
	zigux_u32 status_mask = 0;

	switch (budget_summary->budget_status) {
	case ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_ISSUED:
		status_mask = ZIGUX_CHRDEV_NOTIFY_ACK_MASK_ISSUED;
		break;
	case ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_DEFERRED:
		status_mask = ZIGUX_CHRDEV_NOTIFY_ACK_MASK_DEFERRED;
		break;
	case ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_DROPPED:
		status_mask = ZIGUX_CHRDEV_NOTIFY_ACK_MASK_DROPPED;
		break;
	case ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_SUPPRESSED:
		status_mask = ZIGUX_CHRDEV_NOTIFY_ACK_MASK_SUPPRESSED;
		break;
	default:
		break;
	}

	return view->ack_mask & status_mask;
}

static inline struct zigux_chrdev_notify_ack_summary
zigux_chrdev_notify_ack_summarize(
	const struct zigux_chrdev_notify_ack_view *view)
{
	struct zigux_chrdev_notify_ack_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
	};
	struct zigux_chrdev_notify_budget_view budget_view;
	struct zigux_chrdev_notify_budget_summary budget_summary;
	zigux_u32 matched_ack_mask;

	if (!zigux_chrdev_notify_ack_view_valid(view))
		return summary;

	budget_view = zigux_chrdev_notify_ack_as_chrdev_notify_budget(view);
	budget_summary = zigux_chrdev_notify_budget_summarize(&budget_view);
	matched_ack_mask =
		zigux_chrdev_notify_ack_match_mask(view, &budget_summary);

	summary.major = budget_summary.major;
	summary.target_minor = budget_summary.target_minor;
	summary.selected_count = budget_summary.selected_count;
	summary.resolved_index = budget_summary.resolved_index;
	summary.resolved_dev = budget_summary.resolved_dev;
	summary.granted_mode = budget_summary.granted_mode;
	summary.io_op = budget_summary.io_op;
	summary.requested_bytes = budget_summary.requested_bytes;
	summary.start_offset = budget_summary.start_offset;
	summary.next_offset = budget_summary.next_offset;
	summary.initial_bytes_completed =
		budget_summary.initial_bytes_completed;
	summary.final_bytes_completed =
		budget_summary.final_bytes_completed;
	summary.pass_count = budget_summary.pass_count;
	summary.issued_bytes = budget_summary.issued_bytes;
	summary.remaining_bytes = budget_summary.remaining_bytes;
	summary.projected_remaining_bytes =
		budget_summary.projected_remaining_bytes;
	summary.entry_ops = budget_summary.entry_ops;
	summary.data_ops = budget_summary.data_ops;
	summary.exit_ops = budget_summary.exit_ops;
	summary.blocked_ops = budget_summary.blocked_ops;
	summary.retry_count = budget_summary.retry_count;
	summary.stall_count = budget_summary.stall_count;
	summary.requeue_count = budget_summary.requeue_count;
	summary.queue_depth_before = budget_summary.queue_depth_before;
	summary.queue_depth_after = budget_summary.queue_depth_after;
	summary.remaining_retry_budget =
		budget_summary.remaining_retry_budget;
	summary.remaining_requeue_budget =
		budget_summary.remaining_requeue_budget;
	summary.backoff_ticks = budget_summary.backoff_ticks;
	summary.completion_cookie = budget_summary.completion_cookie;
	summary.completion_status = budget_summary.completion_status;
	summary.completion_count = budget_summary.completion_count;
	summary.deferred_count = budget_summary.deferred_count;
	summary.failure_count = budget_summary.failure_count;
	summary.remaining_completion_budget =
		budget_summary.remaining_completion_budget;
	summary.notify_mask = budget_summary.notify_mask;
	summary.matched_notify_mask = budget_summary.matched_notify_mask;
	summary.notify_status = budget_summary.notify_status;
	summary.notify_count = budget_summary.notify_count;
	summary.deferred_notify_count =
		budget_summary.deferred_notify_count;
	summary.dropped_notify_count =
		budget_summary.dropped_notify_count;
	summary.remaining_notify_budget =
		budget_summary.remaining_notify_budget;
	summary.notify_cookie = budget_summary.notify_cookie;
	summary.flags = budget_summary.flags;
	summary.policy_flags = budget_summary.policy_flags;
	summary.effective_policy_flags =
		budget_summary.effective_policy_flags;
	summary.effective_notify_cookie =
		budget_summary.effective_notify_cookie;
	summary.policy_status = budget_summary.policy_status;
	summary.policy_notify_count = budget_summary.policy_notify_count;
	summary.policy_deferred_count =
		budget_summary.policy_deferred_count;
	summary.policy_suppressed_count =
		budget_summary.policy_suppressed_count;
	summary.policy_coalesced_count =
		budget_summary.policy_coalesced_count;
	summary.budget_flags = budget_summary.budget_flags;
	summary.delivery_budget_before =
		budget_summary.delivery_budget_before;
	summary.delivery_budget_after =
		budget_summary.delivery_budget_after;
	summary.deferred_budget_before =
		budget_summary.deferred_budget_before;
	summary.deferred_budget_after =
		budget_summary.deferred_budget_after;
	summary.budget_status = budget_summary.budget_status;
	summary.budget_notify_count = budget_summary.budget_notify_count;
	summary.budget_deferred_count =
		budget_summary.budget_deferred_count;
	summary.budget_dropped_count =
		budget_summary.budget_dropped_count;
	summary.budget_suppressed_count =
		budget_summary.budget_suppressed_count;
	summary.ack_mask = view->ack_mask;
	summary.matched_ack_mask = matched_ack_mask;
	summary.ack_window_before = view->ack_window;
	summary.ack_window_after = view->ack_window;
	summary.ack_cookie = view->ack_cookie;

	if (budget_summary.budget_status !=
	    ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE)
		summary.ack_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_APPLICABLE;

	if (matched_ack_mask == 0) {
		if (budget_summary.budget_status !=
		    ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE) {
			summary.ack_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_SKIPPED;
			summary.ack_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_SKIPPED;
			summary.skipped_ack_count = 1;
		}
		return summary;
	}

	if (view->ack_observed != 0) {
		summary.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_ACKED;
		summary.ack_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_ACKED;
		summary.ack_count = 1;
		return summary;
	}

	if (summary.ack_window_after > 0) {
		summary.ack_window_after -= 1;
		summary.ack_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_DEFERRED;
		summary.ack_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_DEFERRED |
			ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_WINDOW_USED;
		summary.deferred_ack_count = 1;
		return summary;
	}

	summary.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_EXPIRED;
	summary.ack_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_EXPIRED |
			       ZIGUX_CHRDEV_NOTIFY_ACK_FLAG_WINDOW_EXHAUSTED;
	summary.expired_ack_count = 1;
	return summary;
}

static inline struct zigux_chrdev_notify_ack_policy_view
zigux_chrdev_notify_ack_policy_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget,
	zigux_u32 ack_mask, zigux_u32 ack_window, zigux_u64 ack_cookie,
	zigux_u32 ack_observed, zigux_u32 ack_policy_flags)
{
	return (struct zigux_chrdev_notify_ack_policy_view){
		.bits_addr = (unsigned long)bits,
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
		.delivery_budget = delivery_budget,
		.deferred_budget = deferred_budget,
		.ack_mask = ack_mask,
		.ack_window = ack_window,
		.ack_cookie = ack_cookie,
		.ack_observed = ack_observed,
		.ack_reserved = 0,
		.ack_policy_flags = ack_policy_flags,
		.ack_policy_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_policy_view_valid(
	const struct zigux_chrdev_notify_ack_policy_view *view)
{
	struct zigux_chrdev_notify_ack_view ack_view;
	const zigux_u32 allowed_flags =
		ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED |
		ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED |
		ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_COALESCE_COOKIE;

	if (!view)
		return false;
	if (view->ack_policy_reserved != 0)
		return false;
	if ((view->ack_policy_flags & ~allowed_flags) != 0)
		return false;

	ack_view = (struct zigux_chrdev_notify_ack_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
		.policy_flags = view->policy_flags,
		.policy_reserved = 0,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = 0,
	};

	return zigux_chrdev_notify_ack_view_valid(&ack_view);
}

static inline struct zigux_chrdev_notify_ack_view
zigux_chrdev_notify_ack_policy_as_chrdev_notify_ack(
	const struct zigux_chrdev_notify_ack_policy_view *view)
{
	if (!zigux_chrdev_notify_ack_policy_view_valid(view))
		return (struct zigux_chrdev_notify_ack_view){0};

	return (struct zigux_chrdev_notify_ack_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
		.policy_flags = view->policy_flags,
		.policy_reserved = 0,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = 0,
	};
}

static inline struct zigux_chrdev_notify_ack_policy_summary
zigux_chrdev_notify_ack_policy_summarize(
	const struct zigux_chrdev_notify_ack_policy_view *view)
{
	struct zigux_chrdev_notify_ack_policy_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
		.ack_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
	};
	struct zigux_chrdev_notify_ack_view ack_view;
	struct zigux_chrdev_notify_ack_summary ack_summary;

	if (!zigux_chrdev_notify_ack_policy_view_valid(view))
		return summary;

	ack_view = zigux_chrdev_notify_ack_policy_as_chrdev_notify_ack(view);
	ack_summary = zigux_chrdev_notify_ack_summarize(&ack_view);
	memcpy(&summary, &ack_summary, sizeof(ack_summary));
	summary.ack_policy_flags = view->ack_policy_flags;

	switch (ack_summary.ack_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_SKIPPED:
		summary.ack_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_SKIPPED;
		summary.policy_skipped_ack_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_EXPIRED:
		if ((view->ack_policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED) != 0) {
			summary.effective_ack_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_SUPPRESS_EXPIRED;
			summary.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_SUPPRESSED;
			summary.policy_suppressed_ack_count = 1;
		} else if ((view->ack_policy_flags &
			    ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED) != 0) {
			summary.effective_ack_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED;
			summary.effective_ack_cookie = ack_summary.ack_cookie;
			summary.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED;
			summary.policy_deferred_ack_count = 1;
		} else {
			summary.effective_ack_cookie = ack_summary.ack_cookie;
			summary.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_EXPIRED;
			summary.policy_expired_ack_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_DEFERRED:
		if ((view->ack_policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED) != 0)
			summary.effective_ack_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED;
		summary.effective_ack_cookie = ack_summary.ack_cookie;
		summary.ack_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED;
		summary.policy_deferred_ack_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_ACKED:
		if ((view->ack_policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_COALESCE_COOKIE) != 0 &&
		    ack_summary.ack_cookie != 0 &&
		    (ack_summary.ack_cookie == ack_summary.notify_cookie ||
		     ack_summary.ack_cookie ==
			     ack_summary.completion_cookie)) {
			summary.effective_ack_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_COALESCE_COOKIE;
			summary.effective_ack_cookie = ack_summary.ack_cookie;
			summary.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_COALESCED;
			summary.policy_coalesced_ack_count = 1;
		} else if ((view->ack_policy_flags &
			    ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED) != 0) {
			summary.effective_ack_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_FORCE_DEFERRED;
			summary.effective_ack_cookie = ack_summary.ack_cookie;
			summary.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED;
			summary.policy_deferred_ack_count = 1;
		} else {
			summary.effective_ack_cookie = ack_summary.ack_cookie;
			summary.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_ACKED;
			summary.policy_acked_count = 1;
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_budget_view
zigux_chrdev_notify_ack_budget_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget,
	zigux_u32 ack_mask, zigux_u32 ack_window, zigux_u64 ack_cookie,
	zigux_u32 ack_observed, zigux_u32 ack_policy_flags,
	zigux_u32 ack_budget, zigux_u32 deferred_ack_budget)
{
	return (struct zigux_chrdev_notify_ack_budget_view){
		.bits_addr = (unsigned long)bits,
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
		.delivery_budget = delivery_budget,
		.deferred_budget = deferred_budget,
		.ack_mask = ack_mask,
		.ack_window = ack_window,
		.ack_cookie = ack_cookie,
		.ack_observed = ack_observed,
		.ack_reserved = 0,
		.ack_policy_flags = ack_policy_flags,
		.ack_policy_reserved = 0,
		.ack_budget = ack_budget,
		.deferred_ack_budget = deferred_ack_budget,
		.ack_budget_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_budget_view_valid(
	const struct zigux_chrdev_notify_ack_budget_view *view)
{
	struct zigux_chrdev_notify_ack_policy_view ack_policy_view;

	if (!view)
		return false;
	if (view->ack_budget_reserved != 0)
		return false;

	ack_policy_view = (struct zigux_chrdev_notify_ack_policy_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
		.policy_flags = view->policy_flags,
		.policy_reserved = 0,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = 0,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = 0,
	};

	return zigux_chrdev_notify_ack_policy_view_valid(&ack_policy_view);
}

static inline struct zigux_chrdev_notify_ack_policy_view
zigux_chrdev_notify_ack_budget_as_chrdev_notify_ack_policy(
	const struct zigux_chrdev_notify_ack_budget_view *view)
{
	if (!zigux_chrdev_notify_ack_budget_view_valid(view))
		return (struct zigux_chrdev_notify_ack_policy_view){0};

	return (struct zigux_chrdev_notify_ack_policy_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = 0,
		.policy_flags = view->policy_flags,
		.policy_reserved = 0,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = 0,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = 0,
	};
}

static inline struct zigux_chrdev_notify_ack_budget_summary
zigux_chrdev_notify_ack_budget_summarize(
	const struct zigux_chrdev_notify_ack_budget_view *view)
{
	struct zigux_chrdev_notify_ack_budget_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
		.ack_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
		.ack_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
	};
	struct zigux_chrdev_notify_ack_policy_view ack_policy_view;
	struct zigux_chrdev_notify_ack_policy_summary ack_policy_summary;

	if (!zigux_chrdev_notify_ack_budget_view_valid(view))
		return summary;

	ack_policy_view = zigux_chrdev_notify_ack_budget_as_chrdev_notify_ack_policy(view);
	ack_policy_summary = zigux_chrdev_notify_ack_policy_summarize(&ack_policy_view);
	memcpy(&summary, &ack_policy_summary, sizeof(ack_policy_summary));
	summary.ack_budget_before = view->ack_budget;
	summary.ack_budget_after = view->ack_budget;
	summary.deferred_ack_budget_before = view->deferred_ack_budget;
	summary.deferred_ack_budget_after = view->deferred_ack_budget;

	switch (ack_policy_summary.ack_policy_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_SUPPRESSED:
		summary.ack_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SUPPRESSED;
		summary.budget_suppressed_ack_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_SKIPPED:
		summary.ack_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SKIPPED;
		summary.budget_skipped_ack_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_DEFERRED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_EXPIRED:
		summary.ack_budget_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.deferred_ack_budget_after > 0) {
			summary.deferred_ack_budget_after--;
			summary.ack_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_USED;
			summary.ack_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DEFERRED;
			summary.budget_deferred_ack_count = 1;
		} else {
			summary.ack_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_EXHAUSTED;
			summary.ack_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DROPPED;
			summary.budget_dropped_ack_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_COALESCED:
		summary.ack_budget_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.ack_budget_after > 0) {
			summary.ack_budget_after--;
			summary.ack_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_ACK_BUDGET_USED;
			summary.ack_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_ACKED;
			summary.budget_acked_count = 1;
		} else {
			summary.ack_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_ACK_BUDGET_EXHAUSTED;
			if (summary.deferred_ack_budget_after > 0) {
				summary.deferred_ack_budget_after--;
				summary.ack_budget_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_USED;
				summary.ack_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DEFERRED;
				summary.budget_deferred_ack_count = 1;
			} else {
				summary.ack_budget_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_FLAG_DEFERRED_ACK_BUDGET_EXHAUSTED;
				summary.ack_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DROPPED;
				summary.budget_dropped_ack_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_view
zigux_chrdev_notify_ack_window_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget,
	zigux_u32 ack_mask, zigux_u32 ack_window, zigux_u64 ack_cookie,
	zigux_u32 ack_observed, zigux_u32 ack_policy_flags,
	zigux_u32 ack_budget, zigux_u32 deferred_ack_budget,
	zigux_u32 window_floor)
{
	return (struct zigux_chrdev_notify_ack_window_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
		.delivery_budget = delivery_budget,
		.deferred_budget = deferred_budget,
		.ack_mask = ack_mask,
		.ack_window = ack_window,
		.ack_cookie = ack_cookie,
		.ack_observed = ack_observed,
		.ack_reserved = 0,
		.ack_policy_flags = ack_policy_flags,
		.ack_policy_reserved = 0,
		.ack_budget = ack_budget,
		.deferred_ack_budget = deferred_ack_budget,
		.ack_budget_reserved = 0,
		.window_floor = window_floor,
		.window_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_window_view_valid(
	const struct zigux_chrdev_notify_ack_window_view *view)
{
	struct zigux_chrdev_notify_ack_budget_view ack_budget_view;

	if (!view)
		return false;
	if (view->window_reserved != 0)
		return false;

	ack_budget_view = (struct zigux_chrdev_notify_ack_budget_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
	};
	return zigux_chrdev_notify_ack_budget_view_valid(&ack_budget_view);
}

static inline struct zigux_chrdev_notify_ack_budget_view
zigux_chrdev_notify_ack_window_as_chrdev_notify_ack_budget(
	const struct zigux_chrdev_notify_ack_window_view *view)
{
	if (!zigux_chrdev_notify_ack_window_view_valid(view))
		return (struct zigux_chrdev_notify_ack_budget_view){0};

	return (struct zigux_chrdev_notify_ack_budget_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
	};
}

static inline struct zigux_chrdev_notify_ack_window_summary
zigux_chrdev_notify_ack_window_summarize(
	const struct zigux_chrdev_notify_ack_window_view *view)
{
	struct zigux_chrdev_notify_ack_window_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
		.ack_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
		.ack_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
		.window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
	};
	struct zigux_chrdev_notify_ack_budget_view ack_budget_view;
	struct zigux_chrdev_notify_ack_budget_summary ack_budget_summary;

	if (!zigux_chrdev_notify_ack_window_view_valid(view))
		return summary;

	ack_budget_view =
		zigux_chrdev_notify_ack_window_as_chrdev_notify_ack_budget(view);
	ack_budget_summary = zigux_chrdev_notify_ack_budget_summarize(&ack_budget_view);
	memcpy(&summary, &ack_budget_summary, sizeof(ack_budget_summary));
	summary.window_before = ack_budget_summary.ack_window_after;
	summary.window_after = ack_budget_summary.ack_window_after;
	summary.window_floor = view->window_floor;

	switch (ack_budget_summary.ack_budget_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SUPPRESSED:
		summary.window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SUPPRESSED;
		summary.window_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_SKIPPED:
		summary.window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SKIPPED;
		summary.window_skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DROPPED:
		summary.window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DROPPED;
		summary.window_dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_DEFERRED:
		summary.window_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_APPLIED;
		if (summary.window_before == 0) {
			summary.window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_EXHAUSTED;
			summary.window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DROPPED;
			summary.window_dropped_count = 1;
		} else if (summary.window_before <= view->window_floor) {
			summary.window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_FLOOR_HELD |
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_FLOOR_BLOCKED;
			summary.window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DEFERRED;
			summary.window_deferred_count = 1;
		} else {
			summary.window_after = summary.window_before - 1U;
			summary.window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_FLAG_WINDOW_USED;
			if (ack_budget_summary.ack_budget_status ==
			    ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_ACKED) {
				summary.window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_ACKED;
				summary.window_acked_count = 1;
			} else {
				summary.window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DEFERRED;
				summary.window_deferred_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_policy_view
zigux_chrdev_notify_ack_window_policy_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget,
	zigux_u32 ack_mask, zigux_u32 ack_window, zigux_u64 ack_cookie,
	zigux_u32 ack_observed, zigux_u32 ack_policy_flags,
	zigux_u32 ack_budget, zigux_u32 deferred_ack_budget,
	zigux_u32 window_floor, zigux_u32 window_policy_flags)
{
	return (struct zigux_chrdev_notify_ack_window_policy_view){
		.bits_addr = zigux_ptr_addr(bits),
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
		.delivery_budget = delivery_budget,
		.deferred_budget = deferred_budget,
		.ack_mask = ack_mask,
		.ack_window = ack_window,
		.ack_cookie = ack_cookie,
		.ack_observed = ack_observed,
		.ack_reserved = 0,
		.ack_policy_flags = ack_policy_flags,
		.ack_policy_reserved = 0,
		.ack_budget = ack_budget,
		.deferred_ack_budget = deferred_ack_budget,
		.ack_budget_reserved = 0,
		.window_floor = window_floor,
		.window_reserved = 0,
		.window_policy_flags = window_policy_flags,
		.window_policy_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_window_policy_view_valid(
	const struct zigux_chrdev_notify_ack_window_policy_view *view)
{
	struct zigux_chrdev_notify_ack_window_view window_view;

	if (!view)
		return false;
	if (view->window_policy_reserved != 0)
		return false;
	if ((view->window_policy_flags &
	     ~(ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED |
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED |
	       ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE)) != 0)
		return false;

	window_view = (struct zigux_chrdev_notify_ack_window_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = 0,
	};
	return zigux_chrdev_notify_ack_window_view_valid(&window_view);
}

static inline struct zigux_chrdev_notify_ack_window_view
zigux_chrdev_notify_ack_window_policy_as_chrdev_notify_ack_window(
	const struct zigux_chrdev_notify_ack_window_policy_view *view)
{
	if (!zigux_chrdev_notify_ack_window_policy_view_valid(view))
		return (struct zigux_chrdev_notify_ack_window_view){0};

	return (struct zigux_chrdev_notify_ack_window_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = 0,
	};
}

static inline struct zigux_chrdev_notify_ack_window_policy_summary
zigux_chrdev_notify_ack_window_policy_summarize(
	const struct zigux_chrdev_notify_ack_window_policy_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
		.ack_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
		.ack_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
		.window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
		.window_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
	};
	struct zigux_chrdev_notify_ack_window_view window_view;
	struct zigux_chrdev_notify_ack_window_summary window_summary;

	if (!zigux_chrdev_notify_ack_window_policy_view_valid(view))
		return summary;

	window_view =
		zigux_chrdev_notify_ack_window_policy_as_chrdev_notify_ack_window(view);
	window_summary = zigux_chrdev_notify_ack_window_summarize(&window_view);
	memcpy(&summary, &window_summary, sizeof(window_summary));
	summary.window_policy_flags = view->window_policy_flags;

	switch (window_summary.window_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SKIPPED:
		summary.window_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SKIPPED;
		summary.policy_window_skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_SUPPRESSED:
		summary.window_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SUPPRESSED;
		summary.policy_window_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DROPPED:
		if ((view->window_policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED) != 0) {
			summary.effective_window_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_SUPPRESS_DROPPED;
			summary.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SUPPRESSED;
			summary.policy_window_suppressed_count = 1;
		} else {
			summary.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DROPPED;
			summary.policy_window_dropped_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_DEFERRED:
		if ((view->window_policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED) != 0)
			summary.effective_window_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED;
		summary.effective_window_cookie = window_summary.ack_cookie;
		summary.window_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DEFERRED;
		summary.policy_window_deferred_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_ACKED:
		if ((view->window_policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE) != 0 &&
		    window_summary.ack_cookie != 0 &&
		    (window_summary.ack_cookie == window_summary.notify_cookie ||
		     window_summary.ack_cookie == window_summary.completion_cookie)) {
			summary.effective_window_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_COALESCE_COOKIE;
			summary.effective_window_cookie = window_summary.ack_cookie;
			summary.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_COALESCED;
			summary.policy_window_coalesced_count = 1;
		} else if ((view->window_policy_flags &
			    ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED) != 0) {
			summary.effective_window_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_FORCE_DEFERRED;
			summary.effective_window_cookie = window_summary.ack_cookie;
			summary.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DEFERRED;
			summary.policy_window_deferred_count = 1;
		} else {
			summary.effective_window_cookie = window_summary.ack_cookie;
			summary.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_ACKED;
			summary.policy_window_acked_count = 1;
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_view
zigux_chrdev_notify_ack_window_policy_budget_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget,
	zigux_u32 ack_mask, zigux_u32 ack_window, zigux_u64 ack_cookie,
	zigux_u32 ack_observed, zigux_u32 ack_policy_flags,
	zigux_u32 ack_budget, zigux_u32 deferred_ack_budget,
	zigux_u32 window_floor, zigux_u32 window_policy_flags,
	zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget)
{
	return (struct zigux_chrdev_notify_ack_window_policy_budget_view){
		.bits_addr = bits ? (unsigned long)bits : 0UL,
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
		.delivery_budget = delivery_budget,
		.deferred_budget = deferred_budget,
		.ack_mask = ack_mask,
		.ack_window = ack_window,
		.ack_cookie = ack_cookie,
		.ack_observed = ack_observed,
		.ack_reserved = 0,
		.ack_policy_flags = ack_policy_flags,
		.ack_policy_reserved = 0,
		.ack_budget = ack_budget,
		.deferred_ack_budget = deferred_ack_budget,
		.ack_budget_reserved = 0,
		.window_floor = window_floor,
		.window_reserved = 0,
		.window_policy_flags = window_policy_flags,
		.window_policy_reserved = 0,
		.window_policy_budget = window_policy_budget,
		.deferred_window_policy_budget =
			deferred_window_policy_budget,
		.window_policy_budget_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_view_valid(
	const struct zigux_chrdev_notify_ack_window_policy_budget_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_view policy_view;

	if (!view)
		return false;
	if (view->window_policy_budget_reserved != 0)
		return false;

	policy_view = (struct zigux_chrdev_notify_ack_window_policy_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
	};
	return zigux_chrdev_notify_ack_window_policy_view_valid(&policy_view);
}

static inline struct zigux_chrdev_notify_ack_window_policy_view
zigux_chrdev_notify_ack_window_policy_budget_as_chrdev_notify_ack_window_policy(
	const struct zigux_chrdev_notify_ack_window_policy_budget_view *view)
{
	if (!zigux_chrdev_notify_ack_window_policy_budget_view_valid(view))
		return (struct zigux_chrdev_notify_ack_window_policy_view){0};

	return (struct zigux_chrdev_notify_ack_window_policy_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
	};
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_summary
zigux_chrdev_notify_ack_window_policy_budget_summarize(
	const struct zigux_chrdev_notify_ack_window_policy_budget_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
		.ack_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
		.ack_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
		.window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
		.window_policy_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
		.window_policy_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
	};
	struct zigux_chrdev_notify_ack_window_policy_view policy_view;
	struct zigux_chrdev_notify_ack_window_policy_summary policy_summary;

	if (!zigux_chrdev_notify_ack_window_policy_budget_view_valid(view))
		return summary;

	policy_view =
		zigux_chrdev_notify_ack_window_policy_budget_as_chrdev_notify_ack_window_policy(view);
	policy_summary = zigux_chrdev_notify_ack_window_policy_summarize(&policy_view);
	memcpy(&summary, &policy_summary, sizeof(policy_summary));

	summary.window_policy_budget_before = view->window_policy_budget;
	summary.window_policy_budget_after = view->window_policy_budget;
	summary.deferred_window_policy_budget_before =
		view->deferred_window_policy_budget;
	summary.deferred_window_policy_budget_after =
		view->deferred_window_policy_budget;

	switch (policy_summary.window_policy_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SUPPRESSED:
		summary.window_policy_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED;
		summary.budget_window_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_SKIPPED:
		summary.window_policy_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SKIPPED;
		summary.budget_window_skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DROPPED:
		summary.window_policy_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
		summary.budget_window_dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_DEFERRED:
		summary.window_policy_budget_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.deferred_window_policy_budget_after > 0) {
			summary.deferred_window_policy_budget_after -= 1;
			summary.window_policy_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_USED;
			summary.window_policy_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DEFERRED;
			summary.budget_window_deferred_count = 1;
		} else {
			summary.window_policy_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_EXHAUSTED;
			summary.window_policy_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
			summary.budget_window_dropped_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_COALESCED:
		summary.window_policy_budget_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.window_policy_budget_after > 0) {
			summary.window_policy_budget_after -= 1;
			summary.window_policy_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_USED;
			if (policy_summary.window_policy_status ==
			    ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_ACKED) {
				summary.window_policy_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_ACKED;
				summary.budget_window_acked_count = 1;
			} else {
				summary.window_policy_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_COALESCED;
				summary.budget_window_coalesced_count = 1;
			}
		} else {
			summary.window_policy_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_WINDOW_POLICY_BUDGET_EXHAUSTED;
			if (summary.deferred_window_policy_budget_after > 0) {
				summary.deferred_window_policy_budget_after -= 1;
				summary.window_policy_budget_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_USED;
				summary.window_policy_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DEFERRED;
				summary.budget_window_deferred_count = 1;
			} else {
				summary.window_policy_budget_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_WINDOW_POLICY_BUDGET_EXHAUSTED;
				summary.window_policy_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
				summary.budget_window_dropped_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_view
zigux_chrdev_notify_ack_window_policy_budget_window_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget,
	zigux_u32 ack_mask, zigux_u32 ack_window, zigux_u64 ack_cookie,
	zigux_u32 ack_observed, zigux_u32 ack_policy_flags,
	zigux_u32 ack_budget, zigux_u32 deferred_ack_budget,
	zigux_u32 window_floor, zigux_u32 window_policy_flags,
	zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget,
	zigux_u32 window_policy_budget_window,
	zigux_u32 window_policy_budget_window_floor)
{
	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_view){
		.bits_addr = bits ? (unsigned long)bits : 0UL,
		.major = major,
		.first_minor = first_minor,
		.minor_count = minor_count,
		.max_scan = max_scan,
		.request_count = request_count,
		.policy = policy,
		.target_minor = target_minor,
		.requested_mode = requested_mode,
		.supported_mode = supported_mode,
		.available_ops = available_ops,
		.io_op = io_op,
		.requested_bytes = requested_bytes,
		.max_chunk_bytes = max_chunk_bytes,
		.file_offset = file_offset,
		.bytes_completed = bytes_completed,
		.max_segments = max_segments,
		.resume_passes = resume_passes,
		.retry_budget = retry_budget,
		.stall_budget = stall_budget,
		.backoff_quanta = backoff_quanta,
		.queue_depth = queue_depth,
		.queue_capacity = queue_capacity,
		.requeue_budget = requeue_budget,
		.completion_cookie = completion_cookie,
		.completion_budget = completion_budget,
		.notify_mask = notify_mask,
		.notify_cookie = notify_cookie,
		.notify_budget = notify_budget,
		.reserved = 0,
		.policy_flags = policy_flags,
		.policy_reserved = 0,
		.delivery_budget = delivery_budget,
		.deferred_budget = deferred_budget,
		.ack_mask = ack_mask,
		.ack_window = ack_window,
		.ack_cookie = ack_cookie,
		.ack_observed = ack_observed,
		.ack_reserved = 0,
		.ack_policy_flags = ack_policy_flags,
		.ack_policy_reserved = 0,
		.ack_budget = ack_budget,
		.deferred_ack_budget = deferred_ack_budget,
		.ack_budget_reserved = 0,
		.window_floor = window_floor,
		.window_reserved = 0,
		.window_policy_flags = window_policy_flags,
		.window_policy_reserved = 0,
		.window_policy_budget = window_policy_budget,
		.deferred_window_policy_budget =
			deferred_window_policy_budget,
		.window_policy_budget_reserved = 0,
		.window_policy_budget_window = window_policy_budget_window,
		.window_policy_budget_window_floor =
			window_policy_budget_window_floor,
		.window_policy_budget_window_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_window_view_valid(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_view budget_view;

	if (!view)
		return false;
	if (view->window_policy_budget_window_reserved != 0)
		return false;

	budget_view =
		(struct zigux_chrdev_notify_ack_window_policy_budget_view){
			.bits_addr = view->bits_addr,
			.major = view->major,
			.first_minor = view->first_minor,
			.minor_count = view->minor_count,
			.max_scan = view->max_scan,
			.request_count = view->request_count,
			.policy = view->policy,
			.target_minor = view->target_minor,
			.requested_mode = view->requested_mode,
			.supported_mode = view->supported_mode,
			.available_ops = view->available_ops,
			.io_op = view->io_op,
			.requested_bytes = view->requested_bytes,
			.max_chunk_bytes = view->max_chunk_bytes,
			.file_offset = view->file_offset,
			.bytes_completed = view->bytes_completed,
			.max_segments = view->max_segments,
			.resume_passes = view->resume_passes,
			.retry_budget = view->retry_budget,
			.stall_budget = view->stall_budget,
			.backoff_quanta = view->backoff_quanta,
			.queue_depth = view->queue_depth,
			.queue_capacity = view->queue_capacity,
			.requeue_budget = view->requeue_budget,
			.completion_cookie = view->completion_cookie,
			.completion_budget = view->completion_budget,
			.notify_mask = view->notify_mask,
			.notify_cookie = view->notify_cookie,
			.notify_budget = view->notify_budget,
			.reserved = view->reserved,
			.policy_flags = view->policy_flags,
			.policy_reserved = view->policy_reserved,
			.delivery_budget = view->delivery_budget,
			.deferred_budget = view->deferred_budget,
			.ack_mask = view->ack_mask,
			.ack_window = view->ack_window,
			.ack_cookie = view->ack_cookie,
			.ack_observed = view->ack_observed,
			.ack_reserved = view->ack_reserved,
			.ack_policy_flags = view->ack_policy_flags,
			.ack_policy_reserved = view->ack_policy_reserved,
			.ack_budget = view->ack_budget,
			.deferred_ack_budget = view->deferred_ack_budget,
			.ack_budget_reserved = view->ack_budget_reserved,
			.window_floor = view->window_floor,
			.window_reserved = view->window_reserved,
			.window_policy_flags = view->window_policy_flags,
			.window_policy_reserved = view->window_policy_reserved,
			.window_policy_budget = view->window_policy_budget,
			.deferred_window_policy_budget =
				view->deferred_window_policy_budget,
			.window_policy_budget_reserved =
				view->window_policy_budget_reserved,
		};
	return zigux_chrdev_notify_ack_window_policy_budget_view_valid(
		&budget_view);
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_view
zigux_chrdev_notify_ack_window_policy_budget_window_as_chrdev_notify_ack_window_policy_budget(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_view *view)
{
	if (!zigux_chrdev_notify_ack_window_policy_budget_window_view_valid(
		    view))
		return (struct zigux_chrdev_notify_ack_window_policy_budget_view){
			0 };

	return (struct zigux_chrdev_notify_ack_window_policy_budget_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
		.window_policy_budget = view->window_policy_budget,
		.deferred_window_policy_budget =
			view->deferred_window_policy_budget,
		.window_policy_budget_reserved =
			view->window_policy_budget_reserved,
	};
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_summary
zigux_chrdev_notify_ack_window_policy_budget_window_summarize(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_summary
		summary = {
			.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
			.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
			.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
			.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
			.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
			.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
			.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
			.ack_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
			.window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
			.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
			.window_policy_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
			.window_policy_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
		};
	struct zigux_chrdev_notify_ack_window_policy_budget_view budget_view;
	struct zigux_chrdev_notify_ack_window_policy_budget_summary budget_summary;

	if (!zigux_chrdev_notify_ack_window_policy_budget_window_view_valid(
		    view))
		return summary;

	budget_view =
		zigux_chrdev_notify_ack_window_policy_budget_window_as_chrdev_notify_ack_window_policy_budget(
			view);
	budget_summary =
		zigux_chrdev_notify_ack_window_policy_budget_summarize(
			&budget_view);
	memcpy(&summary, &budget_summary, sizeof(budget_summary));

	summary.window_policy_budget_window_before =
		view->window_policy_budget_window;
	summary.window_policy_budget_window_after =
		view->window_policy_budget_window;
	summary.window_policy_budget_window_floor =
		view->window_policy_budget_window_floor;

	switch (budget_summary.window_policy_budget_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED:
		summary.window_policy_budget_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SUPPRESSED;
		summary.window_policy_budget_window_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_SKIPPED:
		summary.window_policy_budget_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SKIPPED;
		summary.window_policy_budget_window_skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DROPPED:
		summary.window_policy_budget_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED;
		summary.window_policy_budget_window_dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_DEFERRED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_COALESCED:
		summary.window_policy_budget_window_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_APPLIED;
		if (summary.window_policy_budget_window_before == 0) {
			summary.window_policy_budget_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_EXHAUSTED;
			summary.window_policy_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED;
			summary.window_policy_budget_window_dropped_count = 1;
		} else if (summary.window_policy_budget_window_before <=
			   view->window_policy_budget_window_floor) {
			summary.window_policy_budget_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_HELD |
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_BLOCKED;
			summary.window_policy_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED;
			summary.window_policy_budget_window_deferred_count = 1;
		} else {
			summary.window_policy_budget_window_after =
				summary.window_policy_budget_window_before - 1;
			summary.window_policy_budget_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_USED;
			if (budget_summary.window_policy_budget_status ==
			    ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_ACKED) {
				summary.window_policy_budget_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_ACKED;
				summary.window_policy_budget_window_acked_count =
					1;
			} else if (budget_summary.window_policy_budget_status ==
				   ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_COALESCED) {
				summary.window_policy_budget_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_COALESCED;
				summary.window_policy_budget_window_coalesced_count =
					1;
			} else {
				summary.window_policy_budget_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED;
				summary.window_policy_budget_window_deferred_count =
					1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget,
	zigux_u64 notify_cookie, zigux_u32 policy_flags,
	zigux_u32 delivery_budget, zigux_u32 deferred_budget,
	zigux_u32 ack_mask, zigux_u32 ack_window, zigux_u64 ack_cookie,
	zigux_u32 ack_observed, zigux_u32 ack_policy_flags,
	zigux_u32 ack_budget, zigux_u32 deferred_ack_budget,
	zigux_u32 window_floor, zigux_u32 window_policy_flags,
	zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget,
	zigux_u32 window_policy_budget_window,
	zigux_u32 window_policy_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_budget)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_view
		window_view =
			zigux_chrdev_notify_ack_window_policy_budget_window_view_from_bits(
				bits, major, first_minor, minor_count, max_scan,
				request_count, policy, target_minor,
				requested_mode, supported_mode, available_ops,
				io_op, requested_bytes, max_chunk_bytes,
				file_offset, bytes_completed, max_segments,
				resume_passes, retry_budget, stall_budget,
				backoff_quanta, queue_depth, queue_capacity,
				requeue_budget, completion_cookie,
				completion_budget, notify_mask, notify_budget,
				notify_cookie, policy_flags, delivery_budget,
				deferred_budget, ack_mask, ack_window, ack_cookie,
				ack_observed, ack_policy_flags, ack_budget,
				deferred_ack_budget, window_floor,
				window_policy_flags, window_policy_budget,
				deferred_window_policy_budget,
				window_policy_budget_window,
				window_policy_budget_window_floor);

	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view){
		.bits_addr = window_view.bits_addr,
		.major = window_view.major,
		.first_minor = window_view.first_minor,
		.minor_count = window_view.minor_count,
		.max_scan = window_view.max_scan,
		.request_count = window_view.request_count,
		.policy = window_view.policy,
		.target_minor = window_view.target_minor,
		.requested_mode = window_view.requested_mode,
		.supported_mode = window_view.supported_mode,
		.available_ops = window_view.available_ops,
		.io_op = window_view.io_op,
		.requested_bytes = window_view.requested_bytes,
		.max_chunk_bytes = window_view.max_chunk_bytes,
		.file_offset = window_view.file_offset,
		.bytes_completed = window_view.bytes_completed,
		.max_segments = window_view.max_segments,
		.resume_passes = window_view.resume_passes,
		.retry_budget = window_view.retry_budget,
		.stall_budget = window_view.stall_budget,
		.backoff_quanta = window_view.backoff_quanta,
		.queue_depth = window_view.queue_depth,
		.queue_capacity = window_view.queue_capacity,
		.requeue_budget = window_view.requeue_budget,
		.completion_cookie = window_view.completion_cookie,
		.completion_budget = window_view.completion_budget,
		.notify_mask = window_view.notify_mask,
		.notify_cookie = window_view.notify_cookie,
		.notify_budget = window_view.notify_budget,
		.reserved = window_view.reserved,
		.policy_flags = window_view.policy_flags,
		.policy_reserved = window_view.policy_reserved,
		.delivery_budget = window_view.delivery_budget,
		.deferred_budget = window_view.deferred_budget,
		.ack_mask = window_view.ack_mask,
		.ack_window = window_view.ack_window,
		.ack_cookie = window_view.ack_cookie,
		.ack_observed = window_view.ack_observed,
		.ack_reserved = window_view.ack_reserved,
		.ack_policy_flags = window_view.ack_policy_flags,
		.ack_policy_reserved = window_view.ack_policy_reserved,
		.ack_budget = window_view.ack_budget,
		.deferred_ack_budget = window_view.deferred_ack_budget,
		.ack_budget_reserved = window_view.ack_budget_reserved,
		.window_floor = window_view.window_floor,
		.window_reserved = window_view.window_reserved,
		.window_policy_flags = window_view.window_policy_flags,
		.window_policy_reserved = window_view.window_policy_reserved,
		.window_policy_budget = window_view.window_policy_budget,
		.deferred_window_policy_budget =
			window_view.deferred_window_policy_budget,
		.window_policy_budget_reserved =
			window_view.window_policy_budget_reserved,
		.window_policy_budget_window =
			window_view.window_policy_budget_window,
		.window_policy_budget_window_floor =
			window_view.window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			window_view.window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget =
			window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget =
			deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view_valid(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view
		*view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_view
		window_view;

	if (view->window_policy_budget_window_delivery_reserved != 0)
		return false;

	window_view = (struct zigux_chrdev_notify_ack_window_policy_budget_window_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
		.window_policy_budget = view->window_policy_budget,
		.deferred_window_policy_budget =
			view->deferred_window_policy_budget,
		.window_policy_budget_reserved =
			view->window_policy_budget_reserved,
		.window_policy_budget_window =
			view->window_policy_budget_window,
		.window_policy_budget_window_floor =
			view->window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			view->window_policy_budget_window_reserved,
	};

	return zigux_chrdev_notify_ack_window_policy_budget_window_view_valid(
		&window_view);
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_as_chrdev_notify_ack_window_policy_budget_window(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view
		*view)
{
	if (view->window_policy_budget_window_delivery_reserved != 0)
		return (struct zigux_chrdev_notify_ack_window_policy_budget_window_view){
			0 };

	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
		.window_policy_budget = view->window_policy_budget,
		.deferred_window_policy_budget =
			view->deferred_window_policy_budget,
		.window_policy_budget_reserved =
			view->window_policy_budget_reserved,
		.window_policy_budget_window =
			view->window_policy_budget_window,
		.window_policy_budget_window_floor =
			view->window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			view->window_policy_budget_window_reserved,
	};
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_summary
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_summarize(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view
		*view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_summary
		summary = {
			.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
			.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
			.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
			.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
			.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
			.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
			.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
			.ack_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
			.window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
			.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
			.window_policy_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
			.window_policy_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
			.window_policy_budget_window_delivery_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
		};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_view
		window_view;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_summary
		window_summary;

	if (!zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view_valid(
		    view))
		return summary;

	window_view =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_as_chrdev_notify_ack_window_policy_budget_window(
			view);
	window_summary =
		zigux_chrdev_notify_ack_window_policy_budget_window_summarize(
			&window_view);
	memcpy(&summary, &window_summary, sizeof(window_summary));

	summary.window_policy_budget_window_delivery_before =
		view->window_policy_budget_window_delivery_budget;
	summary.window_policy_budget_window_delivery_after =
		view->window_policy_budget_window_delivery_budget;
	summary.deferred_window_policy_budget_window_delivery_before =
		view->deferred_window_policy_budget_window_delivery_budget;
	summary.deferred_window_policy_budget_window_delivery_after =
		view->deferred_window_policy_budget_window_delivery_budget;

	switch (window_summary.window_policy_budget_window_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SUPPRESSED:
		summary.window_policy_budget_window_delivery_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED;
		summary.window_policy_budget_window_delivery_suppressed_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SKIPPED:
		summary.window_policy_budget_window_delivery_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED;
		summary.window_policy_budget_window_delivery_skipped_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED:
		summary.window_policy_budget_window_delivery_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
		summary.window_policy_budget_window_delivery_dropped_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED:
		summary.window_policy_budget_window_delivery_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED;
		if (summary.deferred_window_policy_budget_window_delivery_after >
		    0) {
			summary.deferred_window_policy_budget_window_delivery_after -=
				1;
			summary.window_policy_budget_window_delivery_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_USED;
			summary.window_policy_budget_window_delivery_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED;
			summary.window_policy_budget_window_delivery_deferred_count =
				1;
		} else {
			summary.window_policy_budget_window_delivery_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_EXHAUSTED;
			summary.window_policy_budget_window_delivery_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
			summary.window_policy_budget_window_delivery_dropped_count =
				1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_COALESCED:
		summary.window_policy_budget_window_delivery_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED;
		if (summary.window_policy_budget_window_delivery_after > 0) {
			summary.window_policy_budget_window_delivery_after -= 1;
			summary.window_policy_budget_window_delivery_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_USED;
			if (window_summary.window_policy_budget_window_status ==
			    ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_ACKED) {
				summary.window_policy_budget_window_delivery_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_ACKED;
				summary.window_policy_budget_window_delivery_acked_count =
					1;
			} else {
				summary.window_policy_budget_window_delivery_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED;
				summary.window_policy_budget_window_delivery_coalesced_count =
					1;
			}
		} else {
			summary.window_policy_budget_window_delivery_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_EXHAUSTED;
			if (summary.deferred_window_policy_budget_window_delivery_after >
			    0) {
				summary.deferred_window_policy_budget_window_delivery_after -=
					1;
				summary.window_policy_budget_window_delivery_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_USED;
				summary.window_policy_budget_window_delivery_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED;
				summary.window_policy_budget_window_delivery_deferred_count =
					1;
			} else {
				summary.window_policy_budget_window_delivery_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_EXHAUSTED;
				summary.window_policy_budget_window_delivery_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
				summary.window_policy_budget_window_delivery_dropped_count =
					1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget, zigux_u64 notify_cookie,
	zigux_u32 policy_flags, zigux_u32 delivery_budget,
	zigux_u32 deferred_budget, zigux_u32 ack_mask, zigux_u32 ack_window,
	zigux_u64 ack_cookie, zigux_u32 ack_observed,
	zigux_u32 ack_policy_flags, zigux_u32 ack_budget,
	zigux_u32 deferred_ack_budget, zigux_u32 window_floor,
	zigux_u32 window_policy_flags, zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget,
	zigux_u32 window_policy_budget_window,
	zigux_u32 window_policy_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_budget,
	zigux_u32 window_policy_budget_window_delivery_window,
	zigux_u32 window_policy_budget_window_delivery_window_floor)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view
		delivery_view =
			zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view_from_bits(
				bits, major, first_minor, minor_count,
				max_scan, request_count, policy, target_minor,
				requested_mode, supported_mode, available_ops,
				io_op, requested_bytes, max_chunk_bytes,
				file_offset, bytes_completed, max_segments,
				resume_passes, retry_budget, stall_budget,
				backoff_quanta, queue_depth, queue_capacity,
				requeue_budget, completion_cookie,
				completion_budget, notify_mask, notify_budget,
				notify_cookie, policy_flags, delivery_budget,
				deferred_budget, ack_mask, ack_window,
				ack_cookie, ack_observed, ack_policy_flags,
				ack_budget, deferred_ack_budget, window_floor,
				window_policy_flags, window_policy_budget,
				deferred_window_policy_budget,
				window_policy_budget_window,
				window_policy_budget_window_floor,
				window_policy_budget_window_delivery_budget,
				deferred_window_policy_budget_window_delivery_budget);

	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view){
		.bits_addr = delivery_view.bits_addr,
		.major = delivery_view.major,
		.first_minor = delivery_view.first_minor,
		.minor_count = delivery_view.minor_count,
		.max_scan = delivery_view.max_scan,
		.request_count = delivery_view.request_count,
		.policy = delivery_view.policy,
		.target_minor = delivery_view.target_minor,
		.requested_mode = delivery_view.requested_mode,
		.supported_mode = delivery_view.supported_mode,
		.available_ops = delivery_view.available_ops,
		.io_op = delivery_view.io_op,
		.requested_bytes = delivery_view.requested_bytes,
		.max_chunk_bytes = delivery_view.max_chunk_bytes,
		.file_offset = delivery_view.file_offset,
		.bytes_completed = delivery_view.bytes_completed,
		.max_segments = delivery_view.max_segments,
		.resume_passes = delivery_view.resume_passes,
		.retry_budget = delivery_view.retry_budget,
		.stall_budget = delivery_view.stall_budget,
		.backoff_quanta = delivery_view.backoff_quanta,
		.queue_depth = delivery_view.queue_depth,
		.queue_capacity = delivery_view.queue_capacity,
		.requeue_budget = delivery_view.requeue_budget,
		.completion_cookie = delivery_view.completion_cookie,
		.completion_budget = delivery_view.completion_budget,
		.notify_mask = delivery_view.notify_mask,
		.notify_cookie = delivery_view.notify_cookie,
		.notify_budget = delivery_view.notify_budget,
		.reserved = delivery_view.reserved,
		.policy_flags = delivery_view.policy_flags,
		.policy_reserved = delivery_view.policy_reserved,
		.delivery_budget = delivery_view.delivery_budget,
		.deferred_budget = delivery_view.deferred_budget,
		.ack_mask = delivery_view.ack_mask,
		.ack_window = delivery_view.ack_window,
		.ack_cookie = delivery_view.ack_cookie,
		.ack_observed = delivery_view.ack_observed,
		.ack_reserved = delivery_view.ack_reserved,
		.ack_policy_flags = delivery_view.ack_policy_flags,
		.ack_policy_reserved = delivery_view.ack_policy_reserved,
		.ack_budget = delivery_view.ack_budget,
		.deferred_ack_budget = delivery_view.deferred_ack_budget,
		.ack_budget_reserved = delivery_view.ack_budget_reserved,
		.window_floor = delivery_view.window_floor,
		.window_reserved = delivery_view.window_reserved,
		.window_policy_flags = delivery_view.window_policy_flags,
		.window_policy_reserved = delivery_view.window_policy_reserved,
		.window_policy_budget = delivery_view.window_policy_budget,
		.deferred_window_policy_budget =
			delivery_view.deferred_window_policy_budget,
		.window_policy_budget_reserved =
			delivery_view.window_policy_budget_reserved,
		.window_policy_budget_window =
			delivery_view.window_policy_budget_window,
		.window_policy_budget_window_floor =
			delivery_view.window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			delivery_view.window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget =
			delivery_view.window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget =
			delivery_view
				.deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved =
			delivery_view.window_policy_budget_window_delivery_reserved,
		.window_policy_budget_window_delivery_window =
			window_policy_budget_window_delivery_window,
		.window_policy_budget_window_delivery_window_floor =
			window_policy_budget_window_delivery_window_floor,
		.window_policy_budget_window_delivery_window_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view_valid(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
		*view)
{
	if (!view)
		return false;
	if (view->window_policy_budget_window_delivery_window_reserved != 0)
		return false;
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view_valid(
		(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view *)
			view);
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_as_chrdev_notify_ack_window_policy_budget_window_delivery(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
		*view)
{
	if (view->window_policy_budget_window_delivery_window_reserved != 0)
		return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view){
			0
		};

	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
		.window_policy_budget = view->window_policy_budget,
		.deferred_window_policy_budget =
			view->deferred_window_policy_budget,
		.window_policy_budget_reserved =
			view->window_policy_budget_reserved,
		.window_policy_budget_window =
			view->window_policy_budget_window,
		.window_policy_budget_window_floor =
			view->window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			view->window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget =
			view->window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget =
			view->deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved =
			view->window_policy_budget_window_delivery_reserved,
	};
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summarize(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
		*view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary
		summary = {
			.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
			.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
			.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
			.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
			.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
			.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
			.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
			.ack_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
			.window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
			.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
			.window_policy_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
			.window_policy_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
			.window_policy_budget_window_delivery_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
			.window_policy_budget_window_delivery_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
		};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_view
		delivery_view;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_summary
		delivery_summary;

	if (!zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view_valid(
		    view))
		return summary;

	delivery_view =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_as_chrdev_notify_ack_window_policy_budget_window_delivery(
			view);
	delivery_summary =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_summarize(
			&delivery_view);
	memcpy(&summary, &delivery_summary, sizeof(delivery_summary));

	summary.window_policy_budget_window_delivery_window_before =
		view->window_policy_budget_window_delivery_window;
	summary.window_policy_budget_window_delivery_window_after =
		view->window_policy_budget_window_delivery_window;
	summary.window_policy_budget_window_delivery_window_floor =
		view->window_policy_budget_window_delivery_window_floor;

	switch (delivery_summary.window_policy_budget_window_delivery_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED:
		summary.window_policy_budget_window_delivery_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED;
		summary.window_policy_budget_window_delivery_window_suppressed_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED:
		summary.window_policy_budget_window_delivery_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED;
		summary.window_policy_budget_window_delivery_window_skipped_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED:
		summary.window_policy_budget_window_delivery_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED;
		summary.window_policy_budget_window_delivery_window_dropped_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED:
		summary.window_policy_budget_window_delivery_window_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_APPLIED;
		if (summary.window_policy_budget_window_delivery_window_before ==
		    0) {
			summary.window_policy_budget_window_delivery_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_EXHAUSTED;
			summary.window_policy_budget_window_delivery_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED;
			summary.window_policy_budget_window_delivery_window_dropped_count =
				1;
		} else if (summary.window_policy_budget_window_delivery_window_before <=
			   view->window_policy_budget_window_delivery_window_floor) {
			summary.window_policy_budget_window_delivery_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_HELD |
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_BLOCKED;
			summary.window_policy_budget_window_delivery_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED;
			summary.window_policy_budget_window_delivery_window_deferred_count =
				1;
		} else {
			summary.window_policy_budget_window_delivery_window_after =
				summary.window_policy_budget_window_delivery_window_before - 1;
			summary.window_policy_budget_window_delivery_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_USED;
			if (delivery_summary.window_policy_budget_window_delivery_status ==
			    ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_ACKED) {
				summary.window_policy_budget_window_delivery_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED;
				summary.window_policy_budget_window_delivery_window_acked_count =
					1;
			} else if (delivery_summary.window_policy_budget_window_delivery_status ==
				   ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED) {
				summary.window_policy_budget_window_delivery_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED;
				summary.window_policy_budget_window_delivery_window_coalesced_count =
					1;
			} else {
				summary.window_policy_budget_window_delivery_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED;
				summary.window_policy_budget_window_delivery_window_deferred_count =
					1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget, zigux_u64 notify_cookie,
	zigux_u32 policy_flags, zigux_u32 delivery_budget,
	zigux_u32 deferred_budget, zigux_u32 ack_mask, zigux_u32 ack_window,
	zigux_u64 ack_cookie, zigux_u32 ack_observed,
	zigux_u32 ack_policy_flags, zigux_u32 ack_budget,
	zigux_u32 deferred_ack_budget, zigux_u32 window_floor,
	zigux_u32 window_policy_flags, zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget,
	zigux_u32 window_policy_budget_window,
	zigux_u32 window_policy_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_budget,
	zigux_u32 window_policy_budget_window_delivery_window,
	zigux_u32 window_policy_budget_window_delivery_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
		delivery_window_view =
			zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view_from_bits(
				bits, major, first_minor, minor_count,
				max_scan, request_count, policy, target_minor,
				requested_mode, supported_mode, available_ops,
				io_op, requested_bytes, max_chunk_bytes,
				file_offset, bytes_completed, max_segments,
				resume_passes, retry_budget, stall_budget,
				backoff_quanta, queue_depth, queue_capacity,
				requeue_budget, completion_cookie,
				completion_budget, notify_mask, notify_budget,
				notify_cookie, policy_flags, delivery_budget,
				deferred_budget, ack_mask, ack_window,
				ack_cookie, ack_observed, ack_policy_flags,
				ack_budget, deferred_ack_budget, window_floor,
				window_policy_flags, window_policy_budget,
				deferred_window_policy_budget,
				window_policy_budget_window,
				window_policy_budget_window_floor,
				window_policy_budget_window_delivery_budget,
				deferred_window_policy_budget_window_delivery_budget,
				window_policy_budget_window_delivery_window,
				window_policy_budget_window_delivery_window_floor);

	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view){
		.bits_addr = delivery_window_view.bits_addr,
		.major = delivery_window_view.major,
		.first_minor = delivery_window_view.first_minor,
		.minor_count = delivery_window_view.minor_count,
		.max_scan = delivery_window_view.max_scan,
		.request_count = delivery_window_view.request_count,
		.policy = delivery_window_view.policy,
		.target_minor = delivery_window_view.target_minor,
		.requested_mode = delivery_window_view.requested_mode,
		.supported_mode = delivery_window_view.supported_mode,
		.available_ops = delivery_window_view.available_ops,
		.io_op = delivery_window_view.io_op,
		.requested_bytes = delivery_window_view.requested_bytes,
		.max_chunk_bytes = delivery_window_view.max_chunk_bytes,
		.file_offset = delivery_window_view.file_offset,
		.bytes_completed = delivery_window_view.bytes_completed,
		.max_segments = delivery_window_view.max_segments,
		.resume_passes = delivery_window_view.resume_passes,
		.retry_budget = delivery_window_view.retry_budget,
		.stall_budget = delivery_window_view.stall_budget,
		.backoff_quanta = delivery_window_view.backoff_quanta,
		.queue_depth = delivery_window_view.queue_depth,
		.queue_capacity = delivery_window_view.queue_capacity,
		.requeue_budget = delivery_window_view.requeue_budget,
		.completion_cookie = delivery_window_view.completion_cookie,
		.completion_budget = delivery_window_view.completion_budget,
		.notify_mask = delivery_window_view.notify_mask,
		.notify_cookie = delivery_window_view.notify_cookie,
		.notify_budget = delivery_window_view.notify_budget,
		.reserved = delivery_window_view.reserved,
		.policy_flags = delivery_window_view.policy_flags,
		.policy_reserved = delivery_window_view.policy_reserved,
		.delivery_budget = delivery_window_view.delivery_budget,
		.deferred_budget = delivery_window_view.deferred_budget,
		.ack_mask = delivery_window_view.ack_mask,
		.ack_window = delivery_window_view.ack_window,
		.ack_cookie = delivery_window_view.ack_cookie,
		.ack_observed = delivery_window_view.ack_observed,
		.ack_reserved = delivery_window_view.ack_reserved,
		.ack_policy_flags = delivery_window_view.ack_policy_flags,
		.ack_policy_reserved = delivery_window_view.ack_policy_reserved,
		.ack_budget = delivery_window_view.ack_budget,
		.deferred_ack_budget = delivery_window_view.deferred_ack_budget,
		.ack_budget_reserved = delivery_window_view.ack_budget_reserved,
		.window_floor = delivery_window_view.window_floor,
		.window_reserved = delivery_window_view.window_reserved,
		.window_policy_flags = delivery_window_view.window_policy_flags,
		.window_policy_reserved = delivery_window_view.window_policy_reserved,
		.window_policy_budget = delivery_window_view.window_policy_budget,
		.deferred_window_policy_budget =
			delivery_window_view.deferred_window_policy_budget,
		.window_policy_budget_reserved =
			delivery_window_view.window_policy_budget_reserved,
		.window_policy_budget_window =
			delivery_window_view.window_policy_budget_window,
		.window_policy_budget_window_floor =
			delivery_window_view.window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			delivery_window_view.window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget =
			delivery_window_view.window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget =
			delivery_window_view
				.deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved =
			delivery_window_view.window_policy_budget_window_delivery_reserved,
		.window_policy_budget_window_delivery_window =
			delivery_window_view.window_policy_budget_window_delivery_window,
		.window_policy_budget_window_delivery_window_floor =
			delivery_window_view
				.window_policy_budget_window_delivery_window_floor,
		.window_policy_budget_window_delivery_window_reserved =
			delivery_window_view
				.window_policy_budget_window_delivery_window_reserved,
		.window_policy_budget_window_delivery_window_budget =
			window_policy_budget_window_delivery_window_budget,
		.deferred_window_policy_budget_window_delivery_window_budget =
			deferred_window_policy_budget_window_delivery_window_budget,
		.window_policy_budget_window_delivery_window_budget_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_valid(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
		*view)
{
	if (!view)
		return false;
	if (view->window_policy_budget_window_delivery_window_budget_reserved != 0)
		return false;
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view_valid(
		(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view *)
			view);
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_as_chrdev_notify_ack_window_policy_budget_window_delivery_window(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
		*view)
{
	if (view->window_policy_budget_window_delivery_window_budget_reserved != 0)
		return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view){
			0
		};

	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
		.window_policy_budget = view->window_policy_budget,
		.deferred_window_policy_budget = view->deferred_window_policy_budget,
		.window_policy_budget_reserved = view->window_policy_budget_reserved,
		.window_policy_budget_window = view->window_policy_budget_window,
		.window_policy_budget_window_floor =
			view->window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			view->window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget =
			view->window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget =
			view->deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved =
			view->window_policy_budget_window_delivery_reserved,
		.window_policy_budget_window_delivery_window =
			view->window_policy_budget_window_delivery_window,
		.window_policy_budget_window_delivery_window_floor =
			view->window_policy_budget_window_delivery_window_floor,
		.window_policy_budget_window_delivery_window_reserved =
			view->window_policy_budget_window_delivery_window_reserved,
	};
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summarize(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
		*view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary
		summary = {
			.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
			.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
			.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
			.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
			.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
			.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
			.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
			.ack_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
			.window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
			.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
			.window_policy_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
			.window_policy_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
			.window_policy_budget_window_delivery_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
			.window_policy_budget_window_delivery_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
			.window_policy_budget_window_delivery_window_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE,
		};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view
		delivery_window_view;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary
		delivery_window_summary;

	if (!zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_valid(
		    view))
		return summary;

	delivery_window_view =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_as_chrdev_notify_ack_window_policy_budget_window_delivery_window(
			view);
	delivery_window_summary =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summarize(
			&delivery_window_view);
	memcpy(&summary, &delivery_window_summary, sizeof(delivery_window_summary));

	summary.window_policy_budget_window_delivery_window_budget_before =
		view->window_policy_budget_window_delivery_window_budget;
	summary.window_policy_budget_window_delivery_window_budget_after =
		view->window_policy_budget_window_delivery_window_budget;
	summary.deferred_window_policy_budget_window_delivery_window_budget_before =
		view->deferred_window_policy_budget_window_delivery_window_budget;
	summary.deferred_window_policy_budget_window_delivery_window_budget_after =
		view->deferred_window_policy_budget_window_delivery_window_budget;

	switch (delivery_window_summary
			.window_policy_budget_window_delivery_window_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED:
		summary.window_policy_budget_window_delivery_window_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED;
		summary.window_policy_budget_window_delivery_window_budget_suppressed_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED:
		summary.window_policy_budget_window_delivery_window_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED;
		summary.window_policy_budget_window_delivery_window_budget_skipped_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED:
		summary.window_policy_budget_window_delivery_window_budget_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
		summary.window_policy_budget_window_delivery_window_budget_dropped_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED:
		summary.window_policy_budget_window_delivery_window_budget_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary
			    .deferred_window_policy_budget_window_delivery_window_budget_after >
		    0) {
			summary
				.deferred_window_policy_budget_window_delivery_window_budget_after -=
				1;
			summary.window_policy_budget_window_delivery_window_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_USED;
			summary.window_policy_budget_window_delivery_window_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED;
			summary.window_policy_budget_window_delivery_window_budget_deferred_count =
				1;
		} else {
			summary.window_policy_budget_window_delivery_window_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
			summary.window_policy_budget_window_delivery_window_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
			summary.window_policy_budget_window_delivery_window_budget_dropped_count =
				1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED:
		summary.window_policy_budget_window_delivery_window_budget_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.window_policy_budget_window_delivery_window_budget_after >
		    0) {
			summary.window_policy_budget_window_delivery_window_budget_after -=
				1;
			summary.window_policy_budget_window_delivery_window_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_USED;
			if (delivery_window_summary
				    .window_policy_budget_window_delivery_window_status ==
			    ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED) {
				summary.window_policy_budget_window_delivery_window_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED;
				summary.window_policy_budget_window_delivery_window_budget_acked_count =
					1;
			} else {
				summary.window_policy_budget_window_delivery_window_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED;
				summary.window_policy_budget_window_delivery_window_budget_coalesced_count =
					1;
			}
		} else {
			summary.window_policy_budget_window_delivery_window_budget_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
			if (summary
				    .deferred_window_policy_budget_window_delivery_window_budget_after >
			    0) {
				summary
					.deferred_window_policy_budget_window_delivery_window_budget_after -=
					1;
				summary.window_policy_budget_window_delivery_window_budget_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_USED;
				summary.window_policy_budget_window_delivery_window_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED;
				summary.window_policy_budget_window_delivery_window_budget_deferred_count =
					1;
			} else {
				summary.window_policy_budget_window_delivery_window_budget_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
				summary.window_policy_budget_window_delivery_window_budget_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
				summary.window_policy_budget_window_delivery_window_budget_dropped_count =
					1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget, zigux_u64 notify_cookie,
	zigux_u32 policy_flags, zigux_u32 delivery_budget,
	zigux_u32 deferred_budget, zigux_u32 ack_mask, zigux_u32 ack_window,
	zigux_u64 ack_cookie, zigux_u32 ack_observed,
	zigux_u32 ack_policy_flags, zigux_u32 ack_budget,
	zigux_u32 deferred_ack_budget, zigux_u32 window_floor,
	zigux_u32 window_policy_flags, zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget,
	zigux_u32 window_policy_budget_window,
	zigux_u32 window_policy_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_budget,
	zigux_u32 window_policy_budget_window_delivery_window,
	zigux_u32 window_policy_budget_window_delivery_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
		budget_view =
			zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_from_bits(
				bits, major, first_minor, minor_count,
				max_scan, request_count, policy, target_minor,
				requested_mode, supported_mode, available_ops,
				io_op, requested_bytes, max_chunk_bytes,
				file_offset, bytes_completed, max_segments,
				resume_passes, retry_budget, stall_budget,
				backoff_quanta, queue_depth, queue_capacity,
				requeue_budget, completion_cookie,
				completion_budget, notify_mask, notify_budget,
				notify_cookie, policy_flags, delivery_budget,
				deferred_budget, ack_mask, ack_window,
				ack_cookie, ack_observed, ack_policy_flags,
				ack_budget, deferred_ack_budget, window_floor,
				window_policy_flags, window_policy_budget,
				deferred_window_policy_budget,
				window_policy_budget_window,
				window_policy_budget_window_floor,
				window_policy_budget_window_delivery_budget,
				deferred_window_policy_budget_window_delivery_budget,
				window_policy_budget_window_delivery_window,
				window_policy_budget_window_delivery_window_floor,
				window_policy_budget_window_delivery_window_budget,
				deferred_window_policy_budget_window_delivery_window_budget);

	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view){
		.bits_addr = budget_view.bits_addr,
		.major = budget_view.major,
		.first_minor = budget_view.first_minor,
		.minor_count = budget_view.minor_count,
		.max_scan = budget_view.max_scan,
		.request_count = budget_view.request_count,
		.policy = budget_view.policy,
		.target_minor = budget_view.target_minor,
		.requested_mode = budget_view.requested_mode,
		.supported_mode = budget_view.supported_mode,
		.available_ops = budget_view.available_ops,
		.io_op = budget_view.io_op,
		.requested_bytes = budget_view.requested_bytes,
		.max_chunk_bytes = budget_view.max_chunk_bytes,
		.file_offset = budget_view.file_offset,
		.bytes_completed = budget_view.bytes_completed,
		.max_segments = budget_view.max_segments,
		.resume_passes = budget_view.resume_passes,
		.retry_budget = budget_view.retry_budget,
		.stall_budget = budget_view.stall_budget,
		.backoff_quanta = budget_view.backoff_quanta,
		.queue_depth = budget_view.queue_depth,
		.queue_capacity = budget_view.queue_capacity,
		.requeue_budget = budget_view.requeue_budget,
		.completion_cookie = budget_view.completion_cookie,
		.completion_budget = budget_view.completion_budget,
		.notify_mask = budget_view.notify_mask,
		.notify_cookie = budget_view.notify_cookie,
		.notify_budget = budget_view.notify_budget,
		.reserved = budget_view.reserved,
		.policy_flags = budget_view.policy_flags,
		.policy_reserved = budget_view.policy_reserved,
		.delivery_budget = budget_view.delivery_budget,
		.deferred_budget = budget_view.deferred_budget,
		.ack_mask = budget_view.ack_mask,
		.ack_window = budget_view.ack_window,
		.ack_cookie = budget_view.ack_cookie,
		.ack_observed = budget_view.ack_observed,
		.ack_reserved = budget_view.ack_reserved,
		.ack_policy_flags = budget_view.ack_policy_flags,
		.ack_policy_reserved = budget_view.ack_policy_reserved,
		.ack_budget = budget_view.ack_budget,
		.deferred_ack_budget = budget_view.deferred_ack_budget,
		.ack_budget_reserved = budget_view.ack_budget_reserved,
		.window_floor = budget_view.window_floor,
		.window_reserved = budget_view.window_reserved,
		.window_policy_flags = budget_view.window_policy_flags,
		.window_policy_reserved = budget_view.window_policy_reserved,
		.window_policy_budget = budget_view.window_policy_budget,
		.deferred_window_policy_budget =
			budget_view.deferred_window_policy_budget,
		.window_policy_budget_reserved =
			budget_view.window_policy_budget_reserved,
		.window_policy_budget_window =
			budget_view.window_policy_budget_window,
		.window_policy_budget_window_floor =
			budget_view.window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			budget_view.window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget =
			budget_view.window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget =
			budget_view
				.deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved =
			budget_view.window_policy_budget_window_delivery_reserved,
		.window_policy_budget_window_delivery_window =
			budget_view.window_policy_budget_window_delivery_window,
		.window_policy_budget_window_delivery_window_floor =
			budget_view
				.window_policy_budget_window_delivery_window_floor,
		.window_policy_budget_window_delivery_window_reserved =
			budget_view
				.window_policy_budget_window_delivery_window_reserved,
		.window_policy_budget_window_delivery_window_budget =
			budget_view
				.window_policy_budget_window_delivery_window_budget,
		.deferred_window_policy_budget_window_delivery_window_budget =
			budget_view
				.deferred_window_policy_budget_window_delivery_window_budget,
		.window_policy_budget_window_delivery_window_budget_reserved =
			budget_view
				.window_policy_budget_window_delivery_window_budget_reserved,
		.window_policy_budget_window_delivery_window_budget_window =
			window_policy_budget_window_delivery_window_budget_window,
		.window_policy_budget_window_delivery_window_budget_window_floor =
			window_policy_budget_window_delivery_window_budget_window_floor,
		.window_policy_budget_window_delivery_window_budget_window_reserved = 0,
	};
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view_valid(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view
		*view)
{
	if (!view)
		return false;
	if (view->window_policy_budget_window_delivery_window_budget_window_reserved != 0)
		return false;
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_valid(
		(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view *)
			view);
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_as_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view
		*view)
{
	if (view->window_policy_budget_window_delivery_window_budget_window_reserved != 0)
		return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view){
			0
		};

	return (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
		.window_policy_budget = view->window_policy_budget,
		.deferred_window_policy_budget = view->deferred_window_policy_budget,
		.window_policy_budget_reserved = view->window_policy_budget_reserved,
		.window_policy_budget_window = view->window_policy_budget_window,
		.window_policy_budget_window_floor =
			view->window_policy_budget_window_floor,
		.window_policy_budget_window_reserved =
			view->window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget =
			view->window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget =
			view->deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved =
			view->window_policy_budget_window_delivery_reserved,
		.window_policy_budget_window_delivery_window =
			view->window_policy_budget_window_delivery_window,
		.window_policy_budget_window_delivery_window_floor =
			view->window_policy_budget_window_delivery_window_floor,
		.window_policy_budget_window_delivery_window_reserved =
			view->window_policy_budget_window_delivery_window_reserved,
		.window_policy_budget_window_delivery_window_budget =
			view->window_policy_budget_window_delivery_window_budget,
		.deferred_window_policy_budget_window_delivery_window_budget =
			view->deferred_window_policy_budget_window_delivery_window_budget,
		.window_policy_budget_window_delivery_window_budget_reserved =
			view->window_policy_budget_window_delivery_window_budget_reserved,
	};
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_summary
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_summarize(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view
		*view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_summary
		summary = {
			.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
			.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
			.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
			.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
			.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
			.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
			.ack_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
			.ack_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
			.window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
			.window_policy_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
			.window_policy_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
			.window_policy_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
			.window_policy_budget_window_delivery_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
			.window_policy_budget_window_delivery_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
			.window_policy_budget_window_delivery_window_budget_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE,
			.window_policy_budget_window_delivery_window_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE,
		};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view
		budget_view;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary
		budget_summary;

	if (!zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view_valid(
		    view))
		return summary;

	budget_view =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_as_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget(
			view);
	budget_summary =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summarize(
			&budget_view);
	memcpy(&summary, &budget_summary, sizeof(budget_summary));

	summary.window_policy_budget_window_delivery_window_budget_window_before =
		view->window_policy_budget_window_delivery_window_budget_window;
	summary.window_policy_budget_window_delivery_window_budget_window_after =
		view->window_policy_budget_window_delivery_window_budget_window;
	summary.window_policy_budget_window_delivery_window_budget_window_floor =
		view->window_policy_budget_window_delivery_window_budget_window_floor;

	switch (budget_summary
			.window_policy_budget_window_delivery_window_budget_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED:
		summary.window_policy_budget_window_delivery_window_budget_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SUPPRESSED;
		summary.window_policy_budget_window_delivery_window_budget_window_suppressed_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED:
		summary.window_policy_budget_window_delivery_window_budget_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED;
		summary.window_policy_budget_window_delivery_window_budget_window_skipped_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED:
		summary.window_policy_budget_window_delivery_window_budget_window_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DROPPED;
		summary.window_policy_budget_window_delivery_window_budget_window_dropped_count =
			1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED:
		summary.window_policy_budget_window_delivery_window_budget_window_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED;
		if (summary
			    .window_policy_budget_window_delivery_window_budget_window_before ==
		    0) {
			summary.window_policy_budget_window_delivery_window_budget_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_EXHAUSTED;
			summary.window_policy_budget_window_delivery_window_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DROPPED;
			summary.window_policy_budget_window_delivery_window_budget_window_dropped_count =
				1;
		} else if (summary
				   .window_policy_budget_window_delivery_window_budget_window_before <=
			   view->window_policy_budget_window_delivery_window_budget_window_floor) {
			summary.window_policy_budget_window_delivery_window_budget_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_FLOOR_HELD |
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_FLOOR_BLOCKED;
			summary.window_policy_budget_window_delivery_window_budget_window_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DEFERRED;
			summary.window_policy_budget_window_delivery_window_budget_window_deferred_count =
				1;
		} else {
			summary.window_policy_budget_window_delivery_window_budget_window_after =
				summary.window_policy_budget_window_delivery_window_budget_window_before -
				1;
			summary.window_policy_budget_window_delivery_window_budget_window_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_USED;
			switch (budget_summary
					.window_policy_budget_window_delivery_window_budget_status) {
			case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED:
				summary.window_policy_budget_window_delivery_window_budget_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_ACKED;
				summary.window_policy_budget_window_delivery_window_budget_window_acked_count =
					1;
				break;
			case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED:
				summary.window_policy_budget_window_delivery_window_budget_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_COALESCED;
				summary.window_policy_budget_window_delivery_window_budget_window_coalesced_count =
					1;
				break;
			default:
				summary.window_policy_budget_window_delivery_window_budget_window_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DEFERRED;
				summary.window_policy_budget_window_delivery_window_budget_window_deferred_count =
					1;
				break;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}


static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget, zigux_u64 notify_cookie,
	zigux_u32 policy_flags, zigux_u32 delivery_budget,
	zigux_u32 deferred_budget, zigux_u32 ack_mask, zigux_u32 ack_window,
	zigux_u64 ack_cookie, zigux_u32 ack_observed,
	zigux_u32 ack_policy_flags, zigux_u32 ack_budget,
	zigux_u32 deferred_ack_budget, zigux_u32 window_floor,
	zigux_u32 window_policy_flags, zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget,
	zigux_u32 window_policy_budget_window,
	zigux_u32 window_policy_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_budget,
	zigux_u32 window_policy_budget_window_delivery_window,
	zigux_u32 window_policy_budget_window_delivery_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view parent =
		zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view_from_bits(
			bits, major, first_minor, minor_count, max_scan, request_count,
			policy, target_minor, requested_mode, supported_mode,
			available_ops, io_op, requested_bytes, max_chunk_bytes,
			file_offset, bytes_completed, max_segments, resume_passes,
			retry_budget, stall_budget, backoff_quanta, queue_depth,
			queue_capacity, requeue_budget, completion_cookie,
			completion_budget, notify_mask, notify_budget, notify_cookie,
			policy_flags, delivery_budget, deferred_budget, ack_mask,
			ack_window, ack_cookie, ack_observed, ack_policy_flags,
			ack_budget, deferred_ack_budget, window_floor,
			window_policy_flags, window_policy_budget,
			deferred_window_policy_budget, window_policy_budget_window,
			window_policy_budget_window_floor,
			window_policy_budget_window_delivery_budget,
			deferred_window_policy_budget_window_delivery_budget,
			window_policy_budget_window_delivery_window,
			window_policy_budget_window_delivery_window_floor,
			window_policy_budget_window_delivery_window_budget,
			deferred_window_policy_budget_window_delivery_window_budget,
			window_policy_budget_window_delivery_window_budget_window,
			window_policy_budget_window_delivery_window_budget_window_floor);
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view view;

	memset(&view, 0, sizeof(view));
	memcpy(&view, &parent, sizeof(parent));
	view.window_policy_budget_window_delivery_window_budget_window_delivery_budget =
		window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	view.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget =
		deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	view.window_policy_budget_window_delivery_window_budget_window_delivery_reserved = 0;
	return view;
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_valid(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view *view)
{
	if (!view)
		return false;
	if (view->window_policy_budget_window_delivery_window_budget_window_delivery_reserved != 0)
		return false;
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view_valid(
		(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view *)view);
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summary
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
		.ack_policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
		.ack_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
		.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
		.window_policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
		.window_policy_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
		.window_policy_budget_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
		.window_policy_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_delivery_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
	};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_summary parent_summary;

	if (!zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_valid(view))
		return summary;

	parent_summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_summarize(
		(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_view *)view);
	memcpy(&summary, &parent_summary, sizeof(parent_summary));

	summary.window_policy_budget_window_delivery_window_budget_window_delivery_before =
		view->window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_after =
		view->window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_before =
		view->deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget;
	summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after =
		view->deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget;

	switch (parent_summary.window_policy_budget_window_delivery_window_budget_window_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SUPPRESSED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DROPPED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DEFERRED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED;
		if (summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after > 0) {
			summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after -= 1;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_USED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_deferred_count = 1;
		} else {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_EXHAUSTED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_COALESCED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_flags |=
			ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED;
		if (summary.window_policy_budget_window_delivery_window_budget_window_delivery_after > 0) {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_after -= 1;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_USED;
			if (parent_summary.window_policy_budget_window_delivery_window_budget_window_status ==
			    ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_ACKED) {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_ACKED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_acked_count = 1;
			} else {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_coalesced_count = 1;
			}
		} else {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_flags |=
				ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_WINDOW_DELIVERY_BUDGET_EXHAUSTED;
			if (summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after > 0) {
				summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_after -= 1;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_USED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_deferred_count = 1;
			} else {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_flags |=
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_WINDOW_DELIVERY_BUDGET_EXHAUSTED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_status =
					ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_dropped_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget, zigux_u64 notify_cookie,
	zigux_u32 policy_flags, zigux_u32 delivery_budget,
	zigux_u32 deferred_budget, zigux_u32 ack_mask, zigux_u32 ack_window,
	zigux_u64 ack_cookie, zigux_u32 ack_observed,
	zigux_u32 ack_policy_flags, zigux_u32 ack_budget,
	zigux_u32 deferred_ack_budget, zigux_u32 window_floor,
	zigux_u32 window_policy_flags, zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget,
	zigux_u32 window_policy_budget_window,
	zigux_u32 window_policy_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_budget,
	zigux_u32 window_policy_budget_window_delivery_window,
	zigux_u32 window_policy_budget_window_delivery_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window, zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_floor)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view parent;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view view;

	parent = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_from_bits(bits, major, first_minor, minor_count,
		max_scan, request_count, policy, target_minor, requested_mode,
		supported_mode, available_ops, io_op, requested_bytes, max_chunk_bytes,
		file_offset, bytes_completed, max_segments, resume_passes, retry_budget,
		stall_budget, backoff_quanta, queue_depth, queue_capacity, requeue_budget,
		completion_cookie, completion_budget, notify_mask, notify_budget, notify_cookie,
		policy_flags, delivery_budget, deferred_budget, ack_mask, ack_window, ack_cookie,
		ack_observed, ack_policy_flags, ack_budget, deferred_ack_budget, window_floor,
		window_policy_flags, window_policy_budget, deferred_window_policy_budget,
		window_policy_budget_window, window_policy_budget_window_floor,
		window_policy_budget_window_delivery_budget, deferred_window_policy_budget_window_delivery_budget,
		window_policy_budget_window_delivery_window, window_policy_budget_window_delivery_window_floor,
		window_policy_budget_window_delivery_window_budget, deferred_window_policy_budget_window_delivery_window_budget,
		window_policy_budget_window_delivery_window_budget_window, window_policy_budget_window_delivery_window_budget_window_floor,
		window_policy_budget_window_delivery_window_budget_window_delivery_budget,
		deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget);
	memset(&view, 0, sizeof(view));
	memcpy(&view, &parent, sizeof(parent));
	view.window_policy_budget_window_delivery_window_budget_window_delivery_window = window_policy_budget_window_delivery_window_budget_window_delivery_window;
	view.window_policy_budget_window_delivery_window_budget_window_delivery_window_floor = window_policy_budget_window_delivery_window_budget_window_delivery_window_floor;
	view.window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved = 0;
	return view;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_as_parent_view(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view parent;

	memset(&parent, 0, sizeof(parent));
	parent = (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
		.window_policy_budget = view->window_policy_budget,
		.deferred_window_policy_budget = view->deferred_window_policy_budget,
		.window_policy_budget_reserved = view->window_policy_budget_reserved,
		.window_policy_budget_window = view->window_policy_budget_window,
		.window_policy_budget_window_floor = view->window_policy_budget_window_floor,
		.window_policy_budget_window_reserved = view->window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget = view->window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget = view->deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved = view->window_policy_budget_window_delivery_reserved,
		.window_policy_budget_window_delivery_window = view->window_policy_budget_window_delivery_window,
		.window_policy_budget_window_delivery_window_floor = view->window_policy_budget_window_delivery_window_floor,
		.window_policy_budget_window_delivery_window_reserved = view->window_policy_budget_window_delivery_window_reserved,
		.window_policy_budget_window_delivery_window_budget = view->window_policy_budget_window_delivery_window_budget,
		.deferred_window_policy_budget_window_delivery_window_budget = view->deferred_window_policy_budget_window_delivery_window_budget,
		.window_policy_budget_window_delivery_window_budget_reserved = view->window_policy_budget_window_delivery_window_budget_reserved,
		.window_policy_budget_window_delivery_window_budget_window = view->window_policy_budget_window_delivery_window_budget_window,
		.window_policy_budget_window_delivery_window_budget_window_floor = view->window_policy_budget_window_delivery_window_budget_window_floor,
		.window_policy_budget_window_delivery_window_budget_window_reserved = view->window_policy_budget_window_delivery_window_budget_window_reserved,
		.window_policy_budget_window_delivery_window_budget_window_delivery_budget = view->window_policy_budget_window_delivery_window_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget = view->deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_window_budget_window_delivery_reserved = view->window_policy_budget_window_delivery_window_budget_window_delivery_reserved,
	};
	return parent;
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view_valid(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view parent;

	if (!view)
		return false;
	if (view->window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved != 0)
		return false;
	parent = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_as_parent_view(view);
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view_valid(&parent);
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_summary
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_summarize(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
		.ack_policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
		.ack_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
		.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
		.window_policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
		.window_policy_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
		.window_policy_budget_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
		.window_policy_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_delivery_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
	};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summary parent_summary;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_view parent_view;

	if (!zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view_valid(view))
		return summary;

	parent_view = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_as_parent_view(view);
	parent_summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_summarize(&parent_view);
	memcpy(&summary, &parent_summary, sizeof(parent_summary));
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_before = view->window_policy_budget_window_delivery_window_budget_window_delivery_window;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_after = view->window_policy_budget_window_delivery_window_budget_window_delivery_window;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_floor = view->window_policy_budget_window_delivery_window_budget_window_delivery_window_floor;

	switch (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_APPLIED;
		if (summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_before == 0) {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_EXHAUSTED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_dropped_count = 1;
		} else if (summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_before <= view->window_policy_budget_window_delivery_window_budget_window_delivery_window_floor) {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_HELD | ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_FLOOR_BLOCKED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_deferred_count = 1;
		} else {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_after = summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_before - 1;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_WINDOW_USED;
			if (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_status == ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_ACKED) {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_acked_count = 1;
			} else if (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_status == ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED) {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_coalesced_count = 1;
			} else {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_deferred_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}


static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_from_bits(
	const unsigned long *bits, zigux_u32 major, zigux_u32 first_minor,
	zigux_u32 minor_count, zigux_u32 max_scan, zigux_u32 request_count,
	zigux_u32 policy, zigux_u32 target_minor, zigux_u32 requested_mode,
	zigux_u32 supported_mode, zigux_u32 available_ops, zigux_u32 io_op,
	zigux_u32 requested_bytes, zigux_u32 max_chunk_bytes,
	zigux_u64 file_offset, zigux_u32 bytes_completed,
	zigux_u32 max_segments, zigux_u32 resume_passes,
	zigux_u32 retry_budget, zigux_u32 stall_budget,
	zigux_u32 backoff_quanta, zigux_u32 queue_depth,
	zigux_u32 queue_capacity, zigux_u32 requeue_budget,
	zigux_u64 completion_cookie, zigux_u32 completion_budget,
	zigux_u32 notify_mask, zigux_u32 notify_budget, zigux_u64 notify_cookie,
	zigux_u32 policy_flags, zigux_u32 delivery_budget,
	zigux_u32 deferred_budget, zigux_u32 ack_mask, zigux_u32 ack_window,
	zigux_u64 ack_cookie, zigux_u32 ack_observed,
	zigux_u32 ack_policy_flags, zigux_u32 ack_budget,
	zigux_u32 deferred_ack_budget, zigux_u32 window_floor,
	zigux_u32 window_policy_flags, zigux_u32 window_policy_budget,
	zigux_u32 deferred_window_policy_budget,
	zigux_u32 window_policy_budget_window,
	zigux_u32 window_policy_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_budget,
	zigux_u32 window_policy_budget_window_delivery_window,
	zigux_u32 window_policy_budget_window_delivery_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window, zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_floor,
	zigux_u32 window_policy_budget_window_delivery_window_budget_window_delivery_window_budget,
	zigux_u32 deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view parent;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view view;

	parent = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view_from_bits(bits, major, first_minor, minor_count, max_scan, request_count, policy, target_minor, requested_mode, supported_mode, available_ops, io_op, requested_bytes, max_chunk_bytes, file_offset, bytes_completed, max_segments, resume_passes, retry_budget, stall_budget, backoff_quanta, queue_depth, queue_capacity, requeue_budget, completion_cookie, completion_budget, notify_mask, notify_budget, notify_cookie, policy_flags, delivery_budget, deferred_budget, ack_mask, ack_window, ack_cookie, ack_observed, ack_policy_flags, ack_budget, deferred_ack_budget, window_floor, window_policy_flags, window_policy_budget, deferred_window_policy_budget, window_policy_budget_window, window_policy_budget_window_floor, window_policy_budget_window_delivery_budget, deferred_window_policy_budget_window_delivery_budget, window_policy_budget_window_delivery_window, window_policy_budget_window_delivery_window_floor, window_policy_budget_window_delivery_window_budget, deferred_window_policy_budget_window_delivery_window_budget, window_policy_budget_window_delivery_window_budget_window, window_policy_budget_window_delivery_window_budget_window_floor, window_policy_budget_window_delivery_window_budget_window_delivery_budget, deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget, window_policy_budget_window_delivery_window_budget_window_delivery_window, window_policy_budget_window_delivery_window_budget_window_delivery_window_floor);
	memset(&view, 0, sizeof(view));
	memcpy(&view, &parent, sizeof(parent));
	view.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget = window_policy_budget_window_delivery_window_budget_window_delivery_window_budget;
	view.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget = deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget;
	view.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_reserved = 0;
	return view;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_as_parent_view(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view parent;

	memset(&parent, 0, sizeof(parent));
	parent = (struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view){
		.bits_addr = view->bits_addr,
		.major = view->major,
		.first_minor = view->first_minor,
		.minor_count = view->minor_count,
		.max_scan = view->max_scan,
		.request_count = view->request_count,
		.policy = view->policy,
		.target_minor = view->target_minor,
		.requested_mode = view->requested_mode,
		.supported_mode = view->supported_mode,
		.available_ops = view->available_ops,
		.io_op = view->io_op,
		.requested_bytes = view->requested_bytes,
		.max_chunk_bytes = view->max_chunk_bytes,
		.file_offset = view->file_offset,
		.bytes_completed = view->bytes_completed,
		.max_segments = view->max_segments,
		.resume_passes = view->resume_passes,
		.retry_budget = view->retry_budget,
		.stall_budget = view->stall_budget,
		.backoff_quanta = view->backoff_quanta,
		.queue_depth = view->queue_depth,
		.queue_capacity = view->queue_capacity,
		.requeue_budget = view->requeue_budget,
		.completion_cookie = view->completion_cookie,
		.completion_budget = view->completion_budget,
		.notify_mask = view->notify_mask,
		.notify_cookie = view->notify_cookie,
		.notify_budget = view->notify_budget,
		.reserved = view->reserved,
		.policy_flags = view->policy_flags,
		.policy_reserved = view->policy_reserved,
		.delivery_budget = view->delivery_budget,
		.deferred_budget = view->deferred_budget,
		.ack_mask = view->ack_mask,
		.ack_window = view->ack_window,
		.ack_cookie = view->ack_cookie,
		.ack_observed = view->ack_observed,
		.ack_reserved = view->ack_reserved,
		.ack_policy_flags = view->ack_policy_flags,
		.ack_policy_reserved = view->ack_policy_reserved,
		.ack_budget = view->ack_budget,
		.deferred_ack_budget = view->deferred_ack_budget,
		.ack_budget_reserved = view->ack_budget_reserved,
		.window_floor = view->window_floor,
		.window_reserved = view->window_reserved,
		.window_policy_flags = view->window_policy_flags,
		.window_policy_reserved = view->window_policy_reserved,
		.window_policy_budget = view->window_policy_budget,
		.deferred_window_policy_budget = view->deferred_window_policy_budget,
		.window_policy_budget_reserved = view->window_policy_budget_reserved,
		.window_policy_budget_window = view->window_policy_budget_window,
		.window_policy_budget_window_floor = view->window_policy_budget_window_floor,
		.window_policy_budget_window_reserved = view->window_policy_budget_window_reserved,
		.window_policy_budget_window_delivery_budget = view->window_policy_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_budget = view->deferred_window_policy_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_reserved = view->window_policy_budget_window_delivery_reserved,
		.window_policy_budget_window_delivery_window = view->window_policy_budget_window_delivery_window,
		.window_policy_budget_window_delivery_window_floor = view->window_policy_budget_window_delivery_window_floor,
		.window_policy_budget_window_delivery_window_reserved = view->window_policy_budget_window_delivery_window_reserved,
		.window_policy_budget_window_delivery_window_budget = view->window_policy_budget_window_delivery_window_budget,
		.deferred_window_policy_budget_window_delivery_window_budget = view->deferred_window_policy_budget_window_delivery_window_budget,
		.window_policy_budget_window_delivery_window_budget_reserved = view->window_policy_budget_window_delivery_window_budget_reserved,
		.window_policy_budget_window_delivery_window_budget_window = view->window_policy_budget_window_delivery_window_budget_window,
		.window_policy_budget_window_delivery_window_budget_window_floor = view->window_policy_budget_window_delivery_window_budget_window_floor,
		.window_policy_budget_window_delivery_window_budget_window_reserved = view->window_policy_budget_window_delivery_window_budget_window_reserved,
		.window_policy_budget_window_delivery_window_budget_window_delivery_budget = view->window_policy_budget_window_delivery_window_budget_window_delivery_budget,
		.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget = view->deferred_window_policy_budget_window_delivery_window_budget_window_delivery_budget,
		.window_policy_budget_window_delivery_window_budget_window_delivery_reserved = view->window_policy_budget_window_delivery_window_budget_window_delivery_reserved,
		.window_policy_budget_window_delivery_window_budget_window_delivery_window = view->window_policy_budget_window_delivery_window_budget_window_delivery_window,
		.window_policy_budget_window_delivery_window_budget_window_delivery_window_floor = view->window_policy_budget_window_delivery_window_budget_window_delivery_window_floor,
		.window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved = view->window_policy_budget_window_delivery_window_budget_window_delivery_window_reserved,
	};
	return parent;
}

static inline bool
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_valid(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view parent;

	if (!view)
		return false;
	if (view->window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_reserved != 0)
		return false;
	parent = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_as_parent_view(view);
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view_valid(&parent);
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_summary
zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_summary summary = {
		.resolved_index = ZIGUX_CHRDEV_NOTIFY_INDEX_NONE,
		.completion_status = ZIGUX_CHRDEV_COMPLETE_STATUS_NONE,
		.notify_status = ZIGUX_CHRDEV_NOTIFY_STATUS_NONE,
		.policy_status = ZIGUX_CHRDEV_NOTIFY_POLICY_STATUS_NONE,
		.budget_status = ZIGUX_CHRDEV_NOTIFY_BUDGET_STATUS_NONE,
		.ack_status = ZIGUX_CHRDEV_NOTIFY_ACK_STATUS_NONE,
		.ack_policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_POLICY_STATUS_NONE,
		.ack_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_BUDGET_STATUS_NONE,
		.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_STATUS_NONE,
		.window_policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_STATUS_NONE,
		.window_policy_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_STATUS_NONE,
		.window_policy_budget_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
		.window_policy_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_delivery_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_delivery_window_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE,
		.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE,
	};
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_summary parent_summary;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_view parent_view;

	if (!zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_valid(view))
		return summary;

	parent_view = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_as_parent_view(view);
	parent_summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_summarize(&parent_view);
	memcpy(&summary, &parent_summary, sizeof(parent_summary));
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags = 0;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before = view->window_policy_budget_window_delivery_window_budget_window_delivery_window_budget;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after = view->window_policy_budget_window_delivery_window_budget_window_delivery_window_budget;
	summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before = view->deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget;
	summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after = view->deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_acked_count = 0;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_deferred_count = 0;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_suppressed_count = 0;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_coalesced_count = 0;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dropped_count = 0;
	summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_skipped_count = 0;

	switch (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after > 0) {
			summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after -= 1;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_USED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_deferred_count = 1;
		} else {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dropped_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED:
		summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after > 0) {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after -= 1;
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_USED;
			if (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_status == ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED) {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_acked_count = 1;
			} else {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_coalesced_count = 1;
			}
		} else {
			summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
			if (summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after > 0) {
				summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after -= 1;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_USED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_deferred_count = 1;
			} else {
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_WINDOW_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
				summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_dropped_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_view
zigux_chrdev_notify_ack_delivery_budget_guard_view_from_parent(
	const struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view *parent,
	zigux_u32 primary_guard_floor, zigux_u32 deferred_guard_floor)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_view view;

	memset(&view, 0, sizeof(view));
	if (parent)
		view.parent = *parent;
	view.primary_guard_floor = primary_guard_floor;
	view.deferred_guard_floor = deferred_guard_floor;
	return view;
}

static inline struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view
zigux_chrdev_notify_ack_delivery_budget_guard_as_parent_view(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_view *view)
{
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view parent;

	memset(&parent, 0, sizeof(parent));
	if (view)
		parent = view->parent;
	return parent;
}

static inline bool
zigux_chrdev_notify_ack_delivery_budget_guard_view_valid(const struct zigux_chrdev_notify_ack_delivery_budget_guard_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_view_valid(&view->parent);
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_summary
zigux_chrdev_notify_ack_delivery_budget_guard_summarize(const struct zigux_chrdev_notify_ack_delivery_budget_guard_view *view)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_summary summary;
	struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_summary parent_summary;

	memset(&summary, 0, sizeof(summary));
	if (!zigux_chrdev_notify_ack_delivery_budget_guard_view_valid(view))
		return summary;

	parent_summary = zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_summarize(&view->parent);
	summary.parent = parent_summary;
	summary.primary_before = parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before;
	summary.primary_after = parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after;
	summary.deferred_before = parent_summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before;
	summary.deferred_after = parent_summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after;
	summary.primary_guard_floor = view->primary_guard_floor;
	summary.deferred_guard_floor = view->deferred_guard_floor;

	switch (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED:
		summary.guard_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
		summary.guard_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SUPPRESSED;
		summary.suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED:
		summary.guard_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
		summary.guard_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SKIPPED;
		summary.skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED:
		summary.guard_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
		if (summary.primary_after <= view->primary_guard_floor &&
		    summary.deferred_after <= view->deferred_guard_floor)
			summary.guard_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_EXHAUSTED;
		summary.guard_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DROPPED;
		summary.dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED:
		summary.guard_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_APPLIED;
		if (summary.deferred_after < view->deferred_guard_floor) {
			summary.deferred_after = summary.deferred_before;
			summary.guard_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_DEFERRED_HELD;
			if (summary.deferred_before <= view->deferred_guard_floor)
				summary.guard_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_EXHAUSTED;
			summary.guard_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_HELD;
			summary.held_count = 1;
		} else {
			summary.guard_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
			summary.guard_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DEFERRED;
			summary.deferred_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED:
		summary.guard_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_APPLIED;
		if (summary.primary_after < view->primary_guard_floor) {
			summary.primary_after = summary.primary_before;
			summary.guard_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PRIMARY_HELD;
			if (summary.primary_before <= view->primary_guard_floor &&
			    summary.deferred_after <= view->deferred_guard_floor)
				summary.guard_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_EXHAUSTED;
			summary.guard_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_HELD;
			summary.held_count = 1;
		} else {
			summary.guard_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
			if (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status ==
			    ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED) {
				summary.guard_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_ACKED;
				summary.acked_count = 1;
			} else {
				summary.guard_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_COALESCED;
				summary.coalesced_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view
zigux_chrdev_notify_ack_delivery_budget_guard_window_view_from_parent(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_view *parent,
	zigux_u32 primary_window, zigux_u32 deferred_window, zigux_u32 window_floor)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view view;

	memset(&view, 0, sizeof(view));
	if (parent)
		view.parent = *parent;
	view.primary_window = primary_window;
	view.deferred_window = deferred_window;
	view.window_floor = window_floor;
	return view;
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_view
zigux_chrdev_notify_ack_delivery_budget_guard_window_as_parent_view(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view *view)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_view parent;

	memset(&parent, 0, sizeof(parent));
	if (view)
		parent = view->parent;
	return parent;
}

static inline bool
zigux_chrdev_notify_ack_delivery_budget_guard_window_view_valid(const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return zigux_chrdev_notify_ack_delivery_budget_guard_view_valid(&view->parent);
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_window_summary
zigux_chrdev_notify_ack_delivery_budget_guard_window_summarize(const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view *view)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_summary summary;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_summary parent_summary;

	memset(&summary, 0, sizeof(summary));
	if (!zigux_chrdev_notify_ack_delivery_budget_guard_window_view_valid(view))
		return summary;

	parent_summary = zigux_chrdev_notify_ack_delivery_budget_guard_summarize(&view->parent);
	summary.parent = parent_summary;
	summary.primary_window_before = view->primary_window;
	summary.primary_window_after = view->primary_window;
	summary.deferred_window_before = view->deferred_window;
	summary.deferred_window_after = view->deferred_window;
	summary.window_floor = view->window_floor;

	switch (parent_summary.guard_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SUPPRESSED:
		summary.window_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH;
		summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SUPPRESSED;
		summary.suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SKIPPED:
		summary.window_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH;
		summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SKIPPED;
		summary.skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DROPPED:
		summary.window_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH;
		if (summary.primary_window_before == 0 &&
		    summary.deferred_window_before == 0)
			summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED;
		summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED;
		summary.dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_HELD:
		summary.window_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH;
		summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD;
		summary.held_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DEFERRED:
		summary.window_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_APPLIED;
		if (summary.deferred_window_before > view->window_floor) {
			summary.deferred_window_after -= 1;
			summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_WINDOW_USED;
			summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DEFERRED;
			summary.deferred_count = 1;
		} else if (summary.deferred_window_before == 0) {
			summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED;
			summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED;
			summary.dropped_count = 1;
		} else {
			summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_HELD;
			summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD;
			summary.held_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_COALESCED:
		summary.window_flags = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_APPLIED;
		if (summary.primary_window_before > view->window_floor) {
			summary.primary_window_after -= 1;
			summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PRIMARY_WINDOW_USED;
			if (parent_summary.guard_status == ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_ACKED) {
				summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_ACKED;
				summary.acked_count = 1;
			} else {
				summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_COALESCED;
				summary.coalesced_count = 1;
			}
		} else {
			if (summary.primary_window_before == 0)
				summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED;
			else
				summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PRIMARY_HELD;
			if (summary.deferred_window_before > view->window_floor) {
				summary.deferred_window_after -= 1;
				summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_WINDOW_USED;
				summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DEFERRED;
				summary.deferred_count = 1;
			} else if (summary.deferred_window_before == 0) {
				summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED;
				summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED;
				summary.dropped_count = 1;
			} else {
				summary.window_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_HELD;
				summary.window_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD;
				summary.held_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view
zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_from_parent(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view *parent,
	zigux_u32 policy_flags)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view view;

	memset(&view, 0, sizeof(view));
	if (parent)
		view.parent = *parent;
	view.policy_flags = policy_flags;
	return view;
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view
zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_as_parent_view(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view *view)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_view parent;

	memset(&parent, 0, sizeof(parent));
	if (view)
		parent = view->parent;
	return parent;
}

static inline bool
zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_valid(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	if ((view->policy_flags &
	     ~(ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED |
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD |
	       ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_DROPPED)) != 0)
		return false;
	return zigux_chrdev_notify_ack_delivery_budget_guard_window_view_valid(&view->parent);
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_summary
zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_summarize(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view *view)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_summary summary;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_summary parent_summary;

	memset(&summary, 0, sizeof(summary));
	if (!zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_valid(view))
		return summary;

	parent_summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_summarize(&view->parent);
	summary.parent = parent_summary;
	summary.policy_flags = view->policy_flags;

	switch (parent_summary.window_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SKIPPED:
		summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SKIPPED;
		summary.skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SUPPRESSED:
		summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED;
		summary.suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED:
		if ((view->policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_DROPPED) != 0) {
			summary.effective_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_DROPPED;
			summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED;
			summary.suppressed_count = 1;
		} else {
			summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DROPPED;
			summary.dropped_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD:
		if ((view->policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD) != 0) {
			summary.effective_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD;
			summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED;
			summary.suppressed_count = 1;
		} else {
			summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_HELD;
			summary.held_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DEFERRED:
		summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED;
		summary.deferred_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_ACKED:
		if ((view->policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED) != 0) {
			summary.effective_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED;
			summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED;
			summary.deferred_count = 1;
		} else {
			summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_ACKED;
			summary.acked_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_COALESCED:
		if ((view->policy_flags &
		     ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED) != 0) {
			summary.effective_policy_flags =
				ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED;
			summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED;
			summary.deferred_count = 1;
		} else {
			summary.policy_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_COALESCED;
			summary.coalesced_count = 1;
		}
		break;
	default:
		break;
	}

	return summary;
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view
zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_from_parent(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view *parent,
	zigux_u32 primary_budget,
	zigux_u32 deferred_budget)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view view;

	memset(&view, 0, sizeof(view));
	if (parent)
		view.parent = *parent;
	view.primary_budget = primary_budget;
	view.deferred_budget = deferred_budget;
	return view;
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view
zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_as_parent_view(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view *view)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view parent;

	memset(&parent, 0, sizeof(parent));
	if (view)
		parent = view->parent;
	return parent;
}

static inline bool
zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_valid(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view *view)
{
	if (!view)
		return false;
	if (view->reserved != 0)
		return false;
	return zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_view_valid(&view->parent);
}

static inline struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_summary
zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_summarize(
	const struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view *view)
{
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_summary summary;
	struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_summary parent_summary;

	memset(&summary, 0, sizeof(summary));
	if (!zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_view_valid(view))
		return summary;

	parent_summary = zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_summarize(&view->parent);
	summary.parent = parent_summary;
	summary.primary_budget_before = view->primary_budget;
	summary.primary_budget_after = view->primary_budget;
	summary.deferred_budget_before = view->deferred_budget;
	summary.deferred_budget_after = view->deferred_budget;

	switch (parent_summary.policy_status) {
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_NONE:
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SKIPPED:
		summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SKIPPED;
		summary.skipped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED:
		summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED;
		summary.suppressed_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DROPPED:
		summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
		summary.dropped_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_HELD:
		summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_HELD;
		summary.held_count = 1;
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED:
		summary.budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.deferred_budget_after > 0) {
			summary.deferred_budget_after -= 1;
			summary.budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_USED;
			summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DEFERRED;
			summary.deferred_count = 1;
		} else {
			summary.budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED;
			summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
			summary.dropped_count = 1;
		}
		break;
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_ACKED:
	case ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_COALESCED:
		summary.budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED;
		if (summary.primary_budget_after > 0) {
			summary.primary_budget_after -= 1;
			summary.budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_PRIMARY_BUDGET_USED;
			if (parent_summary.policy_status == ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_ACKED) {
				summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_ACKED;
				summary.acked_count = 1;
			} else {
				summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_COALESCED;
				summary.coalesced_count = 1;
			}
		} else {
			summary.budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_PRIMARY_BUDGET_EXHAUSTED;
			if (summary.deferred_budget_after > 0) {
				summary.deferred_budget_after -= 1;
				summary.budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_USED;
				summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DEFERRED;
				summary.deferred_count = 1;
			} else {
				summary.budget_flags |= ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED;
				summary.budget_status = ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
				summary.dropped_count = 1;
			}
		}
		break;
	default:
		break;
	}

	return summary;
}

#endif

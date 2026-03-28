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

#endif

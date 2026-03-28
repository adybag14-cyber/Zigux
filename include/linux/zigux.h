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

#endif

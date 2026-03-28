#include <stddef.h>
#include <stdio.h>

#include <linux/zigux.h>

int main(void)
{
	printf(
		"{\"abi_version\":%u,\"constants\":{\"facility_kernel\":%u,"
		"\"status_flag_error\":%u,\"panic_abort\":%u,"
		"\"allocator_caller_provided\":%u,"
		"\"unsafe_scope_raw_pointer_bridge\":%u},"
		"\"structs\":{\"zigux_boundary_header\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"size\":%zu,\"abi_version\":%zu,\"flags\":%zu}},"
		"\"zigux_export_status\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"code\":%zu,\"facility\":%zu,\"flags\":%zu}},"
		"\"zigux_bitmap_view\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"words_addr\":%zu,\"nbits\":%zu,\"word_count\":%zu}},"
		"\"zigux_cpumask_view\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"bits_addr\":%zu,\"nr_cpu_ids\":%zu,\"reserved\":%zu}},"
		"\"zigux_bitmap_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"first_set\":%zu,\"first_zero\":%zu,\"weight\":%zu,\"reserved\":%zu}},"
		"\"zigux_cpumask_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"first_cpu\":%zu,\"next_cpu\":%zu,\"weight\":%zu,\"reserved\":%zu}},"
		"\"zigux_list_head_ref\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"next_addr\":%zu,\"prev_addr\":%zu}},"
		"\"zigux_list_view\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"head_addr\":%zu,\"max_nodes\":%zu,\"reserved\":%zu}},"
		"\"zigux_list_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"length\":%zu,\"flags\":%zu}},"
		"\"zigux_hlist_head_ref\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"first_addr\":%zu}},"
		"\"zigux_hlist_node_ref\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"next_addr\":%zu,\"pprev_addr\":%zu}},"
		"\"zigux_hlist_view\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"head_addr\":%zu,\"max_nodes\":%zu,\"reserved\":%zu}},"
		"\"zigux_hlist_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"length\":%zu,\"flags\":%zu}},"
		"\"zigux_err_ptr_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"errno_code\":%zu,\"flags\":%zu,\"reserved\":%zu}},"
		"\"zigux_xa_value_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"raw_addr\":%zu,\"decoded_value\":%zu,\"flags\":%zu}},"
		"\"zigux_xa_slot_view\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"slots_addr\":%zu,\"slot_count\":%zu,\"max_scan\":%zu}},"
		"\"zigux_xa_slot_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"scanned_count\":%zu,\"null_count\":%zu,\"value_count\":%zu,"
		"\"error_count\":%zu,\"plain_count\":%zu,\"flags\":%zu}},"
		"\"zigux_idr_slot_view\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"slots_addr\":%zu,\"base_id\":%zu,\"slot_count\":%zu,\"max_scan\":%zu,\"reserved\":%zu}},"
		"\"zigux_idr_slot_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"scanned_count\":%zu,\"present_count\":%zu,\"value_count\":%zu,\"error_count\":%zu,"
		"\"plain_count\":%zu,\"first_present_id\":%zu,\"next_free_id\":%zu,\"flags\":%zu}},"
		"\"zigux_ida_bitmap_view\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"bits_addr\":%zu,\"base_id\":%zu,\"nbits\":%zu,\"max_scan\":%zu,\"reserved\":%zu}},"
		"\"zigux_ida_bitmap_summary\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"scanned_count\":%zu,\"allocated_count\":%zu,\"first_allocated_id\":%zu,\"first_free_id\":%zu,"
		"\"flags\":%zu,\"reserved\":%zu}},"
		"\"zigux_mmio_range\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"base_addr\":%zu,\"length\":%zu,\"stride\":%zu}},"
		"\"zigux_interop_policy\":{\"size\":%zu,\"align\":%zu,"
		"\"offsets\":{\"panic_mode\":%zu,\"allocator_mode\":%zu,"
		"\"unsafe_scope\":%zu,\"reserved\":%zu}}}}\n",
		ZIGUX_ABI_VERSION,
		ZIGUX_FACILITY_KERNEL,
		ZIGUX_STATUS_FLAG_ERROR,
		ZIGUX_PANIC_ABORT,
		ZIGUX_ALLOC_CALLER_PROVIDED,
		ZIGUX_UNSAFE_RAW_POINTER_BRIDGE,
		sizeof(struct zigux_boundary_header),
		_Alignof(struct zigux_boundary_header),
		offsetof(struct zigux_boundary_header, size),
		offsetof(struct zigux_boundary_header, abi_version),
		offsetof(struct zigux_boundary_header, flags),
		sizeof(struct zigux_export_status),
		_Alignof(struct zigux_export_status),
		offsetof(struct zigux_export_status, code),
		offsetof(struct zigux_export_status, facility),
		offsetof(struct zigux_export_status, flags),
		sizeof(struct zigux_bitmap_view),
		_Alignof(struct zigux_bitmap_view),
		offsetof(struct zigux_bitmap_view, words_addr),
		offsetof(struct zigux_bitmap_view, nbits),
		offsetof(struct zigux_bitmap_view, word_count),
		sizeof(struct zigux_cpumask_view),
		_Alignof(struct zigux_cpumask_view),
		offsetof(struct zigux_cpumask_view, bits_addr),
		offsetof(struct zigux_cpumask_view, nr_cpu_ids),
		offsetof(struct zigux_cpumask_view, reserved),
		sizeof(struct zigux_bitmap_summary),
		_Alignof(struct zigux_bitmap_summary),
		offsetof(struct zigux_bitmap_summary, first_set),
		offsetof(struct zigux_bitmap_summary, first_zero),
		offsetof(struct zigux_bitmap_summary, weight),
		offsetof(struct zigux_bitmap_summary, reserved),
		sizeof(struct zigux_cpumask_summary),
		_Alignof(struct zigux_cpumask_summary),
		offsetof(struct zigux_cpumask_summary, first_cpu),
		offsetof(struct zigux_cpumask_summary, next_cpu),
		offsetof(struct zigux_cpumask_summary, weight),
		offsetof(struct zigux_cpumask_summary, reserved),
		sizeof(struct zigux_list_head_ref),
		_Alignof(struct zigux_list_head_ref),
		offsetof(struct zigux_list_head_ref, next_addr),
		offsetof(struct zigux_list_head_ref, prev_addr),
		sizeof(struct zigux_list_view),
		_Alignof(struct zigux_list_view),
		offsetof(struct zigux_list_view, head_addr),
		offsetof(struct zigux_list_view, max_nodes),
		offsetof(struct zigux_list_view, reserved),
		sizeof(struct zigux_list_summary),
		_Alignof(struct zigux_list_summary),
		offsetof(struct zigux_list_summary, length),
		offsetof(struct zigux_list_summary, flags),
		sizeof(struct zigux_hlist_head_ref),
		_Alignof(struct zigux_hlist_head_ref),
		offsetof(struct zigux_hlist_head_ref, first_addr),
		sizeof(struct zigux_hlist_node_ref),
		_Alignof(struct zigux_hlist_node_ref),
		offsetof(struct zigux_hlist_node_ref, next_addr),
		offsetof(struct zigux_hlist_node_ref, pprev_addr),
		sizeof(struct zigux_hlist_view),
		_Alignof(struct zigux_hlist_view),
		offsetof(struct zigux_hlist_view, head_addr),
		offsetof(struct zigux_hlist_view, max_nodes),
		offsetof(struct zigux_hlist_view, reserved),
		sizeof(struct zigux_hlist_summary),
		_Alignof(struct zigux_hlist_summary),
		offsetof(struct zigux_hlist_summary, length),
		offsetof(struct zigux_hlist_summary, flags),
		sizeof(struct zigux_err_ptr_summary),
		_Alignof(struct zigux_err_ptr_summary),
		offsetof(struct zigux_err_ptr_summary, errno_code),
		offsetof(struct zigux_err_ptr_summary, flags),
		offsetof(struct zigux_err_ptr_summary, reserved),
		sizeof(struct zigux_xa_value_summary),
		_Alignof(struct zigux_xa_value_summary),
		offsetof(struct zigux_xa_value_summary, raw_addr),
		offsetof(struct zigux_xa_value_summary, decoded_value),
		offsetof(struct zigux_xa_value_summary, flags),
		sizeof(struct zigux_xa_slot_view),
		_Alignof(struct zigux_xa_slot_view),
		offsetof(struct zigux_xa_slot_view, slots_addr),
		offsetof(struct zigux_xa_slot_view, slot_count),
		offsetof(struct zigux_xa_slot_view, max_scan),
		sizeof(struct zigux_xa_slot_summary),
		_Alignof(struct zigux_xa_slot_summary),
		offsetof(struct zigux_xa_slot_summary, scanned_count),
		offsetof(struct zigux_xa_slot_summary, null_count),
		offsetof(struct zigux_xa_slot_summary, value_count),
		offsetof(struct zigux_xa_slot_summary, error_count),
		offsetof(struct zigux_xa_slot_summary, plain_count),
		offsetof(struct zigux_xa_slot_summary, flags),
		sizeof(struct zigux_idr_slot_view),
		_Alignof(struct zigux_idr_slot_view),
		offsetof(struct zigux_idr_slot_view, slots_addr),
		offsetof(struct zigux_idr_slot_view, base_id),
		offsetof(struct zigux_idr_slot_view, slot_count),
		offsetof(struct zigux_idr_slot_view, max_scan),
		offsetof(struct zigux_idr_slot_view, reserved),
		sizeof(struct zigux_idr_slot_summary),
		_Alignof(struct zigux_idr_slot_summary),
		offsetof(struct zigux_idr_slot_summary, scanned_count),
		offsetof(struct zigux_idr_slot_summary, present_count),
		offsetof(struct zigux_idr_slot_summary, value_count),
		offsetof(struct zigux_idr_slot_summary, error_count),
		offsetof(struct zigux_idr_slot_summary, plain_count),
		offsetof(struct zigux_idr_slot_summary, first_present_id),
		offsetof(struct zigux_idr_slot_summary, next_free_id),
		offsetof(struct zigux_idr_slot_summary, flags),
		sizeof(struct zigux_ida_bitmap_view),
		_Alignof(struct zigux_ida_bitmap_view),
		offsetof(struct zigux_ida_bitmap_view, bits_addr),
		offsetof(struct zigux_ida_bitmap_view, base_id),
		offsetof(struct zigux_ida_bitmap_view, nbits),
		offsetof(struct zigux_ida_bitmap_view, max_scan),
		offsetof(struct zigux_ida_bitmap_view, reserved),
		sizeof(struct zigux_ida_bitmap_summary),
		_Alignof(struct zigux_ida_bitmap_summary),
		offsetof(struct zigux_ida_bitmap_summary, scanned_count),
		offsetof(struct zigux_ida_bitmap_summary, allocated_count),
		offsetof(struct zigux_ida_bitmap_summary, first_allocated_id),
		offsetof(struct zigux_ida_bitmap_summary, first_free_id),
		offsetof(struct zigux_ida_bitmap_summary, flags),
		offsetof(struct zigux_ida_bitmap_summary, reserved),
		sizeof(struct zigux_mmio_range),
		_Alignof(struct zigux_mmio_range),
		offsetof(struct zigux_mmio_range, base_addr),
		offsetof(struct zigux_mmio_range, length),
		offsetof(struct zigux_mmio_range, stride),
		sizeof(struct zigux_interop_policy),
		_Alignof(struct zigux_interop_policy),
		offsetof(struct zigux_interop_policy, panic_mode),
		offsetof(struct zigux_interop_policy, allocator_mode),
		offsetof(struct zigux_interop_policy, unsafe_scope),
		offsetof(struct zigux_interop_policy, reserved));
	return 0;
}

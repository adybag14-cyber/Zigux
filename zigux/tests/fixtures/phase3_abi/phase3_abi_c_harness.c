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

#ifndef _ZIGUX_ABI_H
#define _ZIGUX_ABI_H

#ifdef __KERNEL__
#include <linux/types.h>
typedef __u8 zigux_u8;
typedef __u16 zigux_u16;
typedef __u32 zigux_u32;
typedef __s32 zigux_s32;
#else
#include <stdint.h>
typedef uint8_t zigux_u8;
typedef uint16_t zigux_u16;
typedef uint32_t zigux_u32;
typedef int32_t zigux_s32;
#endif

#define ZIGUX_ABI_VERSION 1U

#define ZIGUX_FACILITY_KERNEL 1U
#define ZIGUX_FACILITY_HELPERS 2U
#define ZIGUX_FACILITY_DRIVERS 3U

#define ZIGUX_STATUS_FLAG_ERROR 1U

#define ZIGUX_PANIC_ABORT 0U
#define ZIGUX_PANIC_BUG 1U
#define ZIGUX_PANIC_WARN 2U

#define ZIGUX_ALLOC_CALLER_PROVIDED 0U
#define ZIGUX_ALLOC_KERNEL_HEAP 1U
#define ZIGUX_ALLOC_ARENA 2U

#define ZIGUX_UNSAFE_NONE 0U
#define ZIGUX_UNSAFE_VOLATILE_MMIO 1U
#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U

#define ZIGUX_LIST_FLAG_EMPTY 1U
#define ZIGUX_LIST_FLAG_SINGULAR 2U
#define ZIGUX_LIST_FLAG_CIRCULAR 4U
#define ZIGUX_LIST_FLAG_TRUNCATED 8U

#define ZIGUX_HLIST_FLAG_EMPTY 1U
#define ZIGUX_HLIST_FLAG_SINGULAR 2U
#define ZIGUX_HLIST_FLAG_TERMINATED 4U
#define ZIGUX_HLIST_FLAG_TRUNCATED 8U

#define ZIGUX_ERR_PTR_FLAG_ERROR 1U
#define ZIGUX_ERR_PTR_FLAG_NULL 2U

#define ZIGUX_XA_VALUE_FLAG_VALUE 1U
#define ZIGUX_XA_VALUE_FLAG_PLAIN 2U

#define ZIGUX_XA_SLOT_FLAG_TRUNCATED 1U
#define ZIGUX_IDR_SLOT_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_BITMAP_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_BITMAP_FLAG_EXHAUSTED 2U
#define ZIGUX_IDA_ALLOC_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_ALLOC_FLAG_FOUND 2U
#define ZIGUX_IDA_ALLOC_FLAG_EXHAUSTED 4U
#define ZIGUX_IDA_RANGE_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_RANGE_FLAG_FOUND 2U
#define ZIGUX_IDA_RANGE_FLAG_EXHAUSTED 4U
#define ZIGUX_IDA_RANGE_SET_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_RANGE_SET_FLAG_FOUND 2U
#define ZIGUX_IDA_RANGE_SET_FLAG_EXHAUSTED 4U
#define ZIGUX_IDA_RANGE_SET_FLAG_SELECTED 8U
#define ZIGUX_IDA_POLICY_FIRST_FIT 1U
#define ZIGUX_IDA_POLICY_LAST_FIT 2U
#define ZIGUX_IDA_POLICY_FLAG_TRUNCATED 1U
#define ZIGUX_IDA_POLICY_FLAG_FOUND 2U
#define ZIGUX_IDA_POLICY_FLAG_EXHAUSTED 4U
#define ZIGUX_MINOR_ALLOC_FLAG_TRUNCATED 1U
#define ZIGUX_MINOR_ALLOC_FLAG_FOUND 2U
#define ZIGUX_MINOR_ALLOC_FLAG_EXHAUSTED 4U
#define ZIGUX_DEV_REGION_FLAG_TRUNCATED 1U
#define ZIGUX_DEV_REGION_FLAG_FOUND 2U
#define ZIGUX_DEV_REGION_FLAG_EXHAUSTED 4U
#define ZIGUX_CDEV_ADD_FLAG_TRUNCATED 1U
#define ZIGUX_CDEV_ADD_FLAG_FOUND 2U
#define ZIGUX_CDEV_ADD_FLAG_EXHAUSTED 4U
#define ZIGUX_CDEV_LOOKUP_FLAG_TRUNCATED 1U
#define ZIGUX_CDEV_LOOKUP_FLAG_FOUND 2U
#define ZIGUX_CDEV_LOOKUP_FLAG_EXHAUSTED 4U
#define ZIGUX_CDEV_LOOKUP_FLAG_HIT 8U
#define ZIGUX_CDEV_LOOKUP_INDEX_NONE 0xffffffffU

struct zigux_boundary_header {
	zigux_u32 size;
	zigux_u16 abi_version;
	zigux_u16 flags;
};

struct zigux_export_status {
	zigux_s32 code;
	zigux_u16 facility;
	zigux_u16 flags;
};

struct zigux_bitmap_view {
	unsigned long words_addr;
	zigux_u32 nbits;
	zigux_u32 word_count;
};

struct zigux_cpumask_view {
	unsigned long bits_addr;
	zigux_u32 nr_cpu_ids;
	zigux_u32 reserved;
};

struct zigux_bitmap_summary {
	zigux_u32 first_set;
	zigux_u32 first_zero;
	zigux_u32 weight;
	zigux_u32 reserved;
};

struct zigux_cpumask_summary {
	zigux_u32 first_cpu;
	zigux_u32 next_cpu;
	zigux_u32 weight;
	zigux_u32 reserved;
};

struct zigux_list_head_ref {
	unsigned long next_addr;
	unsigned long prev_addr;
};

struct zigux_list_view {
	unsigned long head_addr;
	zigux_u32 max_nodes;
	zigux_u32 reserved;
};

struct zigux_list_summary {
	zigux_u32 length;
	zigux_u32 flags;
};

struct zigux_hlist_head_ref {
	unsigned long first_addr;
};

struct zigux_hlist_node_ref {
	unsigned long next_addr;
	unsigned long pprev_addr;
};

struct zigux_hlist_view {
	unsigned long head_addr;
	zigux_u32 max_nodes;
	zigux_u32 reserved;
};

struct zigux_hlist_summary {
	zigux_u32 length;
	zigux_u32 flags;
};

struct zigux_err_ptr_summary {
	zigux_s32 errno_code;
	zigux_u16 flags;
	zigux_u16 reserved;
};

struct zigux_xa_value_summary {
	unsigned long raw_addr;
	zigux_u32 decoded_value;
	zigux_u32 flags;
};

struct zigux_xa_slot_view {
	unsigned long slots_addr;
	zigux_u32 slot_count;
	zigux_u32 max_scan;
};

struct zigux_xa_slot_summary {
	zigux_u32 scanned_count;
	zigux_u32 null_count;
	zigux_u32 value_count;
	zigux_u32 error_count;
	zigux_u32 plain_count;
	zigux_u32 flags;
};

struct zigux_idr_slot_view {
	unsigned long slots_addr;
	zigux_u32 base_id;
	zigux_u32 slot_count;
	zigux_u32 max_scan;
	zigux_u32 reserved;
};

struct zigux_idr_slot_summary {
	zigux_u32 scanned_count;
	zigux_u32 present_count;
	zigux_u32 value_count;
	zigux_u32 error_count;
	zigux_u32 plain_count;
	zigux_u32 first_present_id;
	zigux_u32 next_free_id;
	zigux_u32 flags;
};

struct zigux_ida_bitmap_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 reserved;
};

struct zigux_ida_bitmap_summary {
	zigux_u32 scanned_count;
	zigux_u32 allocated_count;
	zigux_u32 first_allocated_id;
	zigux_u32 first_free_id;
	zigux_u32 flags;
	zigux_u32 reserved;
};

struct zigux_ida_alloc_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 reserved;
};

struct zigux_ida_alloc_summary {
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 first_fit_id;
	zigux_u32 longest_free_run;
	zigux_u32 flags;
	zigux_u32 reserved;
};

struct zigux_ida_range_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 max_ranges;
	zigux_u32 reserved;
};

struct zigux_ida_range_summary {
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 candidate_range_count;
	zigux_u32 first_range_id;
	zigux_u32 last_range_id;
	zigux_u32 flags;
};

struct zigux_ida_range_set_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 max_ranges;
	zigux_u32 max_selected;
	zigux_u32 reserved;
};

struct zigux_ida_range_set_summary {
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 candidate_range_count;
	zigux_u32 selected_range_count;
	zigux_u32 first_selected_id;
	zigux_u32 last_selected_id;
	zigux_u32 flags;
	zigux_u32 reserved;
};

struct zigux_ida_policy_view {
	unsigned long bits_addr;
	zigux_u32 base_id;
	zigux_u32 nbits;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 reserved;
};

struct zigux_ida_policy_summary {
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_fit_id;
	zigux_u32 alternate_fit_id;
	zigux_u32 longest_free_run;
	zigux_u32 flags;
};

struct zigux_minor_alloc_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 reserved;
};

struct zigux_minor_alloc_summary {
	zigux_u32 major;
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_minor_start;
	zigux_u32 selected_minor_end;
	zigux_u32 alternate_minor_start;
	zigux_u32 longest_free_run;
	zigux_u32 flags;
};

struct zigux_dev_region_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 reserved;
};

struct zigux_dev_region_summary {
	zigux_u32 major;
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_minor_start;
	zigux_u32 selected_minor_end;
	zigux_u32 first_dev;
	zigux_u32 last_dev;
	zigux_u32 flags;
};

struct zigux_cdev_add_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 reserved;
};

struct zigux_cdev_add_summary {
	zigux_u32 major;
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_count;
	zigux_u32 first_minor;
	zigux_u32 first_dev;
	zigux_u32 last_dev;
	zigux_u32 flags;
};

struct zigux_cdev_lookup_view {
	unsigned long bits_addr;
	zigux_u32 major;
	zigux_u32 first_minor;
	zigux_u32 minor_count;
	zigux_u32 max_scan;
	zigux_u32 request_count;
	zigux_u32 policy;
	zigux_u32 target_minor;
	zigux_u32 reserved;
};

struct zigux_cdev_lookup_summary {
	zigux_u32 major;
	zigux_u32 scanned_count;
	zigux_u32 request_count;
	zigux_u32 selected_count;
	zigux_u32 first_minor;
	zigux_u32 target_minor;
	zigux_u32 resolved_index;
	zigux_u32 resolved_dev;
	zigux_u32 flags;
};

struct zigux_mmio_range {
	unsigned long base_addr;
	zigux_u32 length;
	zigux_u32 stride;
};

struct zigux_interop_policy {
	zigux_u8 panic_mode;
	zigux_u8 allocator_mode;
	zigux_u8 unsafe_scope;
	zigux_u8 reserved;
};

#endif

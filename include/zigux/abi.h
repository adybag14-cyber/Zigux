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

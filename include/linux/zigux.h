#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#ifdef __KERNEL__
#include <linux/build_bug.h>
#endif

#include <zigux/abi.h>

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

#endif

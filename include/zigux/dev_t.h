#ifndef _ZIGUX_DEV_T_H
#define _ZIGUX_DEV_T_H

#include <zigux/abi.h>

#ifdef __KERNEL__
#include <linux/zigux.h>
#else
#include <stdbool.h>

#define ZIGUX_DEV_MINOR_BITS 20U
#define ZIGUX_DEV_MINOR_MASK ((1U << ZIGUX_DEV_MINOR_BITS) - 1U)
#endif

#define ZIGUX_DEV_MAJOR_MAX (0xffffffffU >> ZIGUX_DEV_MINOR_BITS)

static inline bool zigux_dev_major_valid(zigux_u32 major)
{
	return major <= ZIGUX_DEV_MAJOR_MAX;
}

static inline bool zigux_dev_minor_valid(zigux_u32 minor)
{
	return minor <= ZIGUX_DEV_MINOR_MASK;
}

static inline zigux_u32 zigux_dev_encode(zigux_u32 major, zigux_u32 minor)
{
	return (major << ZIGUX_DEV_MINOR_BITS) | (minor & ZIGUX_DEV_MINOR_MASK);
}

static inline zigux_u32 zigux_dev_major(zigux_u32 dev)
{
	return dev >> ZIGUX_DEV_MINOR_BITS;
}

static inline zigux_u32 zigux_dev_minor(zigux_u32 dev)
{
	return dev & ZIGUX_DEV_MINOR_MASK;
}

static inline bool zigux_dev_range_fits(zigux_u32 first_minor, zigux_u32 count)
{
	if (!zigux_dev_minor_valid(first_minor))
		return false;
	if (count == 0)
		return true;
	return count - 1U <= ZIGUX_DEV_MINOR_MASK - first_minor;
}

#endif

#ifndef _ZIGUX_DEV_T_H
#define _ZIGUX_DEV_T_H

#include <zigux/abi.h>

#ifndef __KERNEL__
#include <stdbool.h>
#endif

#if defined(ZIGUX_DEV_MINOR_BITS)
#if ZIGUX_DEV_MINOR_BITS != 20U
#error "ZIGUX_DEV_MINOR_BITS drifted from the canonical zigux dev_t boundary"
#endif
#else
#define ZIGUX_DEV_MINOR_BITS 20U
#endif

#if defined(ZIGUX_DEV_MINOR_MASK)
#if ZIGUX_DEV_MINOR_MASK != ((1U << 20U) - 1U)
#error "ZIGUX_DEV_MINOR_MASK drifted from the canonical zigux dev_t boundary"
#endif
#else
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

static inline bool zigux_dev_last_in_range(zigux_u32 major, zigux_u32 first_minor,
					   zigux_u32 count, zigux_u32 *last_dev)
{
	if (!last_dev)
		return false;
	if (!zigux_dev_major_valid(major))
		return false;
	if (!zigux_dev_range_fits(first_minor, count))
		return false;
	if (count == 0)
		*last_dev = zigux_dev_encode(major, first_minor);
	else
		*last_dev = zigux_dev_encode(major, first_minor + count - 1U);
	return true;
}

#endif

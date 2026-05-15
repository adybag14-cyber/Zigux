#ifndef _ZIGUX_DEV_T_H
#define _ZIGUX_DEV_T_H

#include <stdint.h>

#define ZIGUX_DEV_MINOR_BITS 20U
#define ZIGUX_DEV_MINOR_MASK ((1U << ZIGUX_DEV_MINOR_BITS) - 1U)
#define ZIGUX_DEV_MAJOR_MAX ((1U << (32U - ZIGUX_DEV_MINOR_BITS)) - 1U)

static inline int zigux_major_valid(uint32_t major_id)
{
    return major_id <= ZIGUX_DEV_MAJOR_MAX;
}

static inline int zigux_minor_valid(uint32_t minor_id)
{
    return minor_id <= ZIGUX_DEV_MINOR_MASK;
}

static inline uint32_t zigux_mkdev(uint32_t major_id, uint32_t minor_id)
{
    return (major_id << ZIGUX_DEV_MINOR_BITS) | (minor_id & ZIGUX_DEV_MINOR_MASK);
}

static inline uint32_t zigux_major(uint32_t dev)
{
    return dev >> ZIGUX_DEV_MINOR_BITS;
}

static inline uint32_t zigux_minor(uint32_t dev)
{
    return dev & ZIGUX_DEV_MINOR_MASK;
}

static inline int zigux_dev_range_fits(uint32_t first_minor, uint32_t count)
{
    uint32_t last_minor;

    if (count == 0U)
        return 1;
    if (!zigux_minor_valid(first_minor))
        return 0;

    last_minor = first_minor + count - 1U;
    return last_minor <= ZIGUX_DEV_MINOR_MASK && last_minor >= first_minor;
}

static inline int zigux_last_in_range(
    uint32_t major_id,
    uint32_t first_minor,
    uint32_t count,
    uint32_t *dev)
{
    uint32_t last_minor = first_minor;

    if (!zigux_major_valid(major_id))
        return 0;
    if (count != 0U) {
        if (!zigux_dev_range_fits(first_minor, count))
            return 0;
        last_minor = first_minor + count - 1U;
    } else if (!zigux_minor_valid(first_minor)) {
        return 0;
    }

    if (dev)
        *dev = zigux_mkdev(major_id, last_minor);
    return 1;
}

#endif

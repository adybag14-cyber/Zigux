#ifndef _ZIGUX_DEV_T_H
#define _ZIGUX_DEV_T_H

#include <stdint.h>

#define ZIGUX_DEV_MINOR_BITS 20U
#define ZIGUX_DEV_MINOR_MASK ((1U << ZIGUX_DEV_MINOR_BITS) - 1U)
#define ZIGUX_DEV_MAJOR_MAX ((1U << (32U - ZIGUX_DEV_MINOR_BITS)) - 1U)

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

#endif

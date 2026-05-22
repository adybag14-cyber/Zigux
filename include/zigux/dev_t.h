#ifndef ZIGUX_DEV_T_H
#define ZIGUX_DEV_T_H

#include <stdint.h>

#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u
#define ZIGUX_DEV_T_FIELDS_SIZE 8u
#define ZIGUX_DEV_T_FIELDS_ALIGN 4u
#define ZIGUX_DEV_T_MAJOR_OFFSET 0u
#define ZIGUX_DEV_T_MINOR_OFFSET 4u
#define ZIGUX_DEV_MINOR_BITS 20u
#define ZIGUX_DEV_MINOR_MASK ((1u << ZIGUX_DEV_MINOR_BITS) - 1u)
#define ZIGUX_DEV_MAJOR_MAX ((1u << (32u - ZIGUX_DEV_MINOR_BITS)) - 1u)

struct zigux_dev_t_fields {
    uint32_t major;
    uint32_t minor;
};

static inline struct zigux_dev_t_fields zigux_dev_t_fields_make(
    uint32_t major,
    uint32_t minor
) {
    struct zigux_dev_t_fields fields = {
        .major = major,
        .minor = minor,
    };
    return fields;
}

static inline uint32_t zigux_mkdev(uint32_t major, uint32_t minor)
{
    return (major << ZIGUX_DEV_MINOR_BITS) | (minor & ZIGUX_DEV_MINOR_MASK);
}

static inline uint32_t zigux_major(uint32_t dev)
{
    return dev >> ZIGUX_DEV_MINOR_BITS;
}

static inline uint32_t zigux_minor(uint32_t dev)
{
    return dev & ZIGUX_DEV_MINOR_MASK;
}

static inline struct zigux_dev_t_fields zigux_dev_t_fields_from_device_number(
    uint32_t dev)
{
    return zigux_dev_t_fields_make(zigux_major(dev), zigux_minor(dev));
}

static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)
{
    return fields.major <= ZIGUX_DEV_MAJOR_MAX &&
        fields.minor <= ZIGUX_DEV_MINOR_MASK;
}

static inline int zigux_dev_t_fields_range_is_valid(
    struct zigux_dev_t_fields start,
    struct zigux_dev_t_fields end
)
{
    if (!zigux_dev_t_fields_is_valid(start) || !zigux_dev_t_fields_is_valid(end))
        return 0;
    return start.major < end.major ||
        (start.major == end.major && start.minor <= end.minor);
}

#endif

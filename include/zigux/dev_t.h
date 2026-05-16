#ifndef ZIGUX_DEV_T_H
#define ZIGUX_DEV_T_H

#include <stdint.h>

#define ZIGUX_DEV_T_FIELDS_ABI_VERSION 1u
#define ZIGUX_DEV_T_FIELDS_SIZE 8u
#define ZIGUX_DEV_T_FIELDS_ALIGN 4u

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

#endif

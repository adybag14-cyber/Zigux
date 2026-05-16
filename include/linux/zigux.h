#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#include <stdint.h>

#include <zigux/dev_t.h>

#define ZIGUX_UAPI_ABI_MAJOR 0u
#define ZIGUX_UAPI_ABI_MINOR 1u
#define ZIGUX_UAPI_HEADER_FAMILY_REVISION 1u
#define ZIGUX_UAPI_DEV_T_PACKET_PRESENT 1u

struct zigux_uapi_version {
    uint32_t abi_major;
    uint32_t abi_minor;
    uint32_t header_family_revision;
};

static inline struct zigux_uapi_version zigux_uapi_version_current(void) {
    struct zigux_uapi_version version = {
        .abi_major = ZIGUX_UAPI_ABI_MAJOR,
        .abi_minor = ZIGUX_UAPI_ABI_MINOR,
        .header_family_revision = ZIGUX_UAPI_HEADER_FAMILY_REVISION,
    };
    return version;
}

#endif

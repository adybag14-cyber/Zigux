#ifndef _LINUX_ZIGUX_H
#define _LINUX_ZIGUX_H

#include "../zigux/abi.h"
#include "../zigux/dev_t.h"

static inline int zigux_export_status_ok(struct zigux_export_status status)
{
    return status.code >= 0 && (status.flags & ZIGUX_STATUS_FLAG_ERROR) == 0;
}

static inline struct zigux_boundary_header zigux_boundary_header_make(uint16_t flags)
{
    return zigux_default_header(flags);
}

static inline struct zigux_boundary_header zigux_boundary_header_make_compatible(uint32_t size, uint16_t flags)
{
    struct zigux_boundary_header header = zigux_default_header(flags);
    header.size = size;
    return header;
}

#endif

#include <stddef.h>
#include <stdio.h>

#include "zigux/dev_t.h"

int main(void) {
    printf("{\"abi_version\":%u,", ZIGUX_DEV_T_FIELDS_ABI_VERSION);
    printf("\"fields_size\":%zu,", sizeof(struct zigux_dev_t_fields));
    printf("\"fields_align\":%zu,", _Alignof(struct zigux_dev_t_fields));
    printf("\"major_offset\":%zu,", offsetof(struct zigux_dev_t_fields, major));
    printf("\"minor_offset\":%zu}\n", offsetof(struct zigux_dev_t_fields, minor));
    return 0;
}

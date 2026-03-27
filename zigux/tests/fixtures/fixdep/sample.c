#include "sample.h"
/* CONFIG_ZIGUX_SOURCE */
#ifdef CONFIG_ZIGUX_DRIVER_MODULE
int zigux_source_enabled(void) {
    return 1;
}
#endif

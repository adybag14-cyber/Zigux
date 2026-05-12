#ifndef _DRIVERS_TTY_HVC_HVC_CONSOLE_H
#define _DRIVERS_TTY_HVC_HVC_CONSOLE_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Bounded exported HVC surface used by the Phase 11 header-parity packet.
 * This keeps the public helper declarations reviewable without claiming
 * tty-core registration or runtime callback execution parity.
 */

struct winsize {
    uint16_t ws_row;
    uint16_t ws_col;
    uint16_t ws_xpixel;
    uint16_t ws_ypixel;
};

struct hvc_struct;

#define MAX_NR_HVC_CONSOLES 16
#define HVC_ALLOC_TTY_ADAPTERS 1U

struct hv_ops {
    int (*get_chars)(uint32_t vtermno, char *buf, int count);
    int (*put_chars)(uint32_t vtermno, const char *buf, int count);
    int (*flush)(uint32_t vtermno, bool wait);
    int (*notifier_add)(struct hvc_struct *hp, int irq);
    void (*notifier_del)(struct hvc_struct *hp, int irq);
    void (*notifier_hangup)(struct hvc_struct *hp, int irq);
    int (*tiocmget)(struct hvc_struct *hp);
    int (*tiocmset)(struct hvc_struct *hp, unsigned int set, unsigned int clear);
    void (*dtr_rts)(struct hvc_struct *hp, bool active);
};

extern int hvc_instantiate(uint32_t vtermno, int index,
                           const struct hv_ops *ops);
extern struct hvc_struct * hvc_alloc(uint32_t vtermno, int data,
                                     const struct hv_ops *ops,
                                     int outbuf_size);
extern void hvc_remove(struct hvc_struct *hp);
int hvc_poll(struct hvc_struct *hp);
void hvc_kick(void);
extern void __hvc_resize(struct hvc_struct *hp, struct winsize ws);
extern int notifier_add_irq(struct hvc_struct *hp, int data);
extern void notifier_del_irq(struct hvc_struct *hp, int data);
extern void notifier_hangup_irq(struct hvc_struct *hp, int data);

#endif

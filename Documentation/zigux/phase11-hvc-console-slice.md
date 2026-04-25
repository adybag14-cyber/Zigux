# Phase 11 HVC Console Slice

This bounded Phase 11 slice adds the first Zigux `hvc_console` starter anchored to `drivers/tty/hvc/hvc_console.c`.

The starter stays intentionally narrow:

- publishes explicit descriptor metadata for the hvc console anchor and its still-missing Linux-owned work
- validates the early console slot range and adapter-presence gating before any write attempt
- mirrors the console path's newline framing by inserting `\r` ahead of bare `\n`
- records flush retry intent for `-EAGAIN` write results without pretending live hypervisor I/O or tty registration already exists

This slice does not claim tty-driver registration, early console registration, polling-kthread behavior, close-wait teardown parity, sysrq handling, or live hypervisor-backed character transport yet.

The next honest bounded step inside the same Phase 11 lane is to extend the starter with one tiny flush-progress helper that reports partial-write versus dropped-byte outcomes more explicitly before any broader tty-core or hypervisor-backed behavior lands.

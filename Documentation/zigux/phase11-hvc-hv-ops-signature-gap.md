# Phase 11 HVC hv_ops Signature Gap

This note records one bounded current-head gap inside the Phase 11 HVC
simple-production-driver lane.

## Status

- `PHASE11_HVC_HV_OPS_SIGNATURE_GAP=current_head_mismatch_visible`
- lane: `P11-L13`
- roadmap anchor: `drivers/tty/hvc/hvc_console.c`
- current readback anchors:
  - `drivers/tty/hvc/hvc_console.zig`
  - `drivers/tty/hvc/hvc_console.h`
- bounded purpose: keep one directly readable callback-signature mismatch explicit
  without widening into tty registration, notifier callback execution, khvcd
  worker execution, live sysrq dispatch, or host-backed hypervisor I/O

## Current Repo Reality

The Phase 11 roadmap still treats `drivers/tty/hvc/*.zig` as bounded simple
production-driver work, where hardware validation matrix discipline and teardown
or failure-mode parity should tighten before broader runtime expansion.

Current direct readback still shows the exported header and the directly readable
Zig `HvOps` surface disagree on the two byte-stream callbacks:

- `drivers/tty/hvc/hvc_console.h` keeps `get_chars` and `put_chars` on the
  exported `int` count and `int` return contract
- `drivers/tty/hvc/hvc_console.zig` currently spells `HvOps.get_chars` and
  `HvOps.put_chars` with `usize` count and `isize` return types

That mismatch is small, but it matters because the HVC packet already treats the
callback table as part of the exported helper ABI surface.

## Why This Gap Stays In-Lane

This is still Phase 11 reviewability work, not a wider driver expansion:

- it compares only the current readable Zig callback table to the exported HVC
  header
- it stays inside one direct ABI surface for the simple-driver packet
- it does not claim notifier execution, tty registration, khvcd execution,
  sysrq execution, or hardware-backed teardown parity

## Next Bounded Step

The next honest same-lane move is to realign `HvOps.get_chars` and
`HvOps.put_chars` with the current exported header contract, or refresh this note
if a future current-head reread shows the header or Zig surface changed first.

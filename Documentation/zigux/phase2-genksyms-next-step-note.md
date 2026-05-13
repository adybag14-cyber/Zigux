# Phase 2 genksyms next step note

Lane: `P2-Y04`

Current `master` already carries the bounded `genksyms` bridge packet.

## Current repo evidence

- `scripts/zigux/genksyms.zig` already carries the helper-local replay anchors for repeated short flags, long options and quiet override, version side effects, abbreviated long options, lone-dash passthrough, explicit terminator handling, getopt-style invalid and missing argument failures, normalized invocation rendering, and the bounded sixteen-reference-file limit.
- `zigux/tests/fixtures/genksyms_bridge/manifest.json` records the same closed wrapper-first bridge packet as a `22`-case surface with the committed stdout, process, normalized-stderr, and helper-local anchor packets.
- `zigux/tests/fixtures/genksyms_bridge/cases.json` still names that same `22`-case packet, including the process-mode `ambiguous_long_option` replay and the other normalized-stderr failure cases.
- `scripts/zigux/check-genksyms-bridge.py` keeps the shared reminder surfaces pinned to that same `22`-case manifest-backed packet and its current helper-local anchor count.
- `Documentation/zigux/phase2-closure.md` already describes the live `22`-case bridge surface and warns against drifting back to older undercounts or claiming standalone follow-through that current `master` does not ship.

## Survey result

- The fixture-count and closure-count drift for this tool family are already closed on current `master`.
- The honest remaining same-lane work is smaller than another parser expansion: keep the current bridge packet truthful and rerun the bounded checker plus direct Zig replay together when a writable checkout with Zig is available.
- If that replay ever reopens the lane, keep the first repair checker-local or fixture-local before widening into broader Phase 2 reminder maintenance.

## Next safe step

1. Keep this lane parked unless current `master` shows a new `genksyms`-local drift in `scripts/zigux/genksyms.zig`, `scripts/zigux/check-genksyms-bridge.py`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, `zigux/tests/fixtures/genksyms_bridge/cases.json`, or `Documentation/zigux/phase2-closure.md`.
2. When a writable checkout with Zig is available, rerun `python3 scripts/zigux/check-genksyms-bridge.py --self-test`, `python3 scripts/zigux/check-genksyms-bridge.py`, and `zig test scripts/zigux/genksyms.zig` so the shipped `22`-case fixture packet and the helper-local replay anchors are validated together end to end.

## Boundary

Stay inside the `genksyms` lane only. Do not reopen `fixdep`, the kconfig bridge packet, the shared Phase 2 route inventory, `genksyms_crc`, or broader parser-behavior work unless a new `genksyms`-local truthfulness drift appears.

# Phase 3 Unsafe Slice Closure Correction

## Why this note exists

Current `master` now exposes three directly readable files under `zigux/unsafe/`:

- `zigux/unsafe/narrow.zig`
- `zigux/unsafe/mmio_window.zig`
- `zigux/unsafe/value_bridge.zig`

The shared Phase 3 ABI reminder surfaces and the bounded low-level-wrapper survey still speak as if the unsafe slice is represented only by `zigux/unsafe/narrow.zig`. That is now an undercount of current repo reality.

## What changed in repo reality

This is not a new Phase 3 expansion claim. The repo already carries the extra unsafe-slice files on `master`.

The correction is simply that the unsafe substrate slice is now split into:

- one shared unsafe-scope decoder and raw-pointer bridge surface in `zigux/unsafe/narrow.zig`
- one dedicated volatile MMIO window surface in `zigux/unsafe/mmio_window.zig`
- one dedicated typed value-read bridge in `zigux/unsafe/value_bridge.zig`

## Bounded lane conclusion

For lane `P3-Y04`, the honest closure correction is to stop treating `narrow.zig` as the whole unsafe slice when reading current repo evidence.

## Next safe step

Re-read the bounded Phase 3 manifest and low-level-wrapper survey against this three-file unsafe slice and make one explicit choice:

- either promote `mmio_window.zig` and `value_bridge.zig` into the bounded reminder packet and its validator surfaces
- or keep them outside that packet, but state that exclusion directly so later scheduled runs do not mistake documentation drift for missing implementation

Until that choice is recorded, the unsafe slice should be treated as landed repo evidence with under-described closure notes, not as a missing-helper gap.

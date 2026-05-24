# Phase 8 Help Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/help.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=help-output-stable-packet`
- scope: roadmap-backed help-lane reminder truthfulness, helper-first output-stable tooling wording, focused build-route verification, and one future help-local reopen cue only
- current directly readable packet in this scheduled environment:
  - `Documentation/zigux/phase8-help-slice.md`
  - `scripts/zigux/validate-phase8.py`
  - `scripts/zigux/check-phase8-help-kallsyms-packet.py` through authenticated GitHub contents readback
  - `tools/lib/subcmd/help.zig` through authenticated GitHub contents readback
  - `zigux/tests/phase8_help_kallsyms_only_build.zig` through authenticated GitHub contents readback
  - `zigux/Makefile` through authenticated GitHub contents readback
  - `zigux/tests/phase8_help_only_build.zig` and `zigux/tests/phase8_help.zig` through current public default-branch raw readback only
  - `make -C zigux phase8-help-test`
  - `make -C zigux phase8-help-kallsyms-test`
- current degraded readback for the dedicated help lane:
  - authenticated GitHub contents reads from this environment still flap or return missing for `zigux/tests/phase8_help_only_build.zig` and `zigux/tests/phase8_help.zig`
  - the mixed `zigux/tests/phase8_help_kallsyms_only_build.zig` shard remains shared validation overlap only and does not transfer help-lane ownership into the dedicated symbol lane
  - current public raw reread now keeps `zigux/tests/phase8_help.zig` aligned with the shipped helper surface around `CommandNames`, `trimCommandPrefix`, `computePrettyLayout`, `renderPrettyStringList`, and `renderCommandSections`, so the remaining limitation is source consistency rather than stale helper API drift

## Why this slice exists

The Phase 8 roadmap explicitly names serious repo-hosted tooling as the next step after tiny helpers, keeps `tools/lib/subcmd/*.zig` inside the recommended destination set, and asks for output-stable tooling behavior instead of broad process-launch expansion.

This help packet therefore stays narrow: it keeps the helper-local command-list, filtering, layout, and emitted-section behavior reviewable beside the dedicated help-only route and the shared `help+kallsyms` smoke shard without reopening exec-cmd command ownership, bridge-heavy libbpf work, or deeper runtime boundaries.

## Verified current behavior

The current repo state that is directly verifiable from this run is narrower than a full dedicated help replay from one perfect source, but it is materially readable again.

This run could verify that:

- `tools/lib/subcmd/help.zig` is directly readable through authenticated GitHub contents readback on current `master`
- `zigux/tests/phase8_help_kallsyms_only_build.zig` is directly readable through authenticated GitHub contents readback on current `master`
- `zigux/tests/phase8_help_only_build.zig` and `zigux/tests/phase8_help.zig` are readable through current public raw default-branch readback even though authenticated contents reads still fail here
- `zigux/Makefile` keeps both `make -C zigux phase8-help-test` and `make -C zigux phase8-help-kallsyms-test` explicit on current `master`
- the live help helper keeps the stable output-local packet explicit through `trimCommandPrefix()`, `computePrettyLayout()`, `renderPrettyStringList()`, and `renderCommandSections()`
- the refreshed dedicated help replay now matches that shipped helper surface and keeps the row-major pretty layout plus stable section-heading behavior reviewable through the raw fallback
- the mixed `help+kallsyms` build shard is still shared validation overlap only, not a help-lane ownership handoff

That means the dedicated help packet is no longer missing from current `master`, and the dedicated replay now matches the shipped helper surface again. The remaining constraint is source consistency: authenticated contents reads for the dedicated help replay still flap in this runtime, so the packet stays mixed-source proof until the same path returns those files directly again.

## Current parity surface

The current readable packet now covers:

- the roadmap-backed claim that `help` remains a valid Phase 8 repo-hosted tooling lane
- one directly readable helper-local source in `tools/lib/subcmd/help.zig`
- one directly readable validator entrypoint in `scripts/zigux/validate-phase8.py`
- one directly readable shared Phase 8 checker in `scripts/zigux/check-phase8-help-kallsyms-packet.py`
- one directly readable shared build shard in `zigux/tests/phase8_help_kallsyms_only_build.zig`
- one current public-tree replay witness in `zigux/tests/phase8_help.zig`
- the dedicated `make -C zigux phase8-help-test` route
- the shared-overlap `make -C zigux phase8-help-kallsyms-test` route
- the parked help-and-kallsyms packet reviewable through this dedicated note plus the shared reminder surfaces

The current packet does not yet provide:

- one single exact-write-capable source that cleanly rereads `Documentation/zigux/phase8-help-slice.md`, `zigux/tests/phase8_help.zig`, and `zigux/tests/phase8_help_only_build.zig` together from this environment
- a fresh local replay of the dedicated help-only shard from a writable authoritative checkout of current `master`
- any reason to widen the packet into exec-cmd ownership, symbol-lane parser behavior, or bridge-heavy libbpf work

## Non-goals

This slice does not yet claim:

- exec-cmd command ownership or deferred execution behavior
- kallsyms parser, truncation, CRLF, or callback-wrapper ownership
- libbpf bridge, setup-side routing, object-model, or timeout-sensitive behavior
- broader process-launch, environment-plumbing, or runtime-substrate completion

## Next bounded step

Keep the lane narrow.

The next help-local reopen step is now to reread `Documentation/zigux/phase8-help-slice.md`, `tools/lib/subcmd/help.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, and `make -C zigux phase8-help-test` from one exact-write-capable source, then reopen only if that same-source pass proves a smaller help-local reminder or focused-test follow-through than the existing mixed-source packet already captures.

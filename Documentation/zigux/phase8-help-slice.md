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
  - `zigux/tests/phase8_help_only_build.zig` and `zigux/tests/phase8_help.zig` through authenticated GitHub contents readback on current `master`
  - `zigux/Makefile` through authenticated GitHub contents readback
  - `make -C zigux phase8-help-test`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig` through the public raw fallback as shared validation overlap only
  - `make -C zigux phase8-help-kallsyms-test`
- current degraded readback for the dedicated help lane:
  - authenticated GitHub contents reads still lag on some broader Phase 8 files from this environment, but the dedicated help note, helper, focused replay, focused build shard, and `zigux/Makefile` now read directly on current `master`, while the mixed `zigux/tests/phase8_help_kallsyms_only_build.zig` shard still needs the public raw fallback here
  - the mixed `zigux/tests/phase8_help_kallsyms_only_build.zig` shard remains shared validation overlap only and does not transfer help-lane ownership into the dedicated symbol lane
  - current authenticated contents readback shows `zigux/tests/phase8_help.zig` now directly embeds this slice note and exercises the shipped helper surface through `CommandNames`, `trimCommandPrefix`, `computePrettyLayout`, `renderPrettyStringList`, and `renderCommandSections`, so the dedicated help replay is again honest same-source evidence even while neighboring broader Phase 8 files still need mixed-source rereads here
  - authenticated GitHub contents readback during this pass also returns `zigux/tests/phase8_help_kallsyms_only_build.zig` directly on current `master`, so the shared build shard is readable from the same current branch packet again even though it still stays shared validation overlap only instead of a help-lane ownership handoff

## Why this slice exists

The Phase 8 roadmap explicitly names serious repo-hosted tooling as the next step after tiny helpers, keeps `tools/lib/subcmd/*.zig` inside the recommended destination set, and asks for output-stable tooling behavior instead of broad process-launch expansion.

This help packet therefore stays narrow: it keeps the helper-local command-list, filtering, layout, and emitted-section behavior reviewable beside the dedicated help-only route and the shared `help+kallsyms` smoke shard without reopening exec-cmd command ownership, symbol-lane parser behavior, or bridge-heavy libbpf work.

## Verified current behavior

The current repo state that is directly verifiable from this run is narrower than a perfect single-source replay, but it is still enough to keep the parked help packet truthful.

This run could verify that:

- `tools/lib/subcmd/help.zig` is directly readable through authenticated GitHub contents readback on current `master`
- `zigux/tests/phase8_help_only_build.zig` and `zigux/tests/phase8_help.zig` are directly readable through authenticated GitHub contents readback on current `master`
- `zigux/tests/phase8_help_kallsyms_only_build.zig` is still readable through the public raw fallback as shared validation overlap only
- `zigux/Makefile` keeps both `make -C zigux phase8-help-test` and `make -C zigux phase8-help-kallsyms-test` explicit on current `master`
- the live help helper keeps the stable output-local packet explicit through `trimCommandPrefix()`, `computePrettyLayout()`, `renderPrettyStringList()`, and `renderCommandSections()`
- the live help helper still keeps the stable pretty-printer and heading contract reviewable through the existing `renderPrettyStringList` and `renderCommandSections` tests
- the current authenticated contents `zigux/tests/phase8_help.zig` replay now matches that shipped helper surface through direct `@embedFile()` note binding plus helper-local command-set, pretty-layout, and section-rendering checks, so it is honest same-source proof for the parked help packet again while the neighboring broader Phase 8 packet still needs mixed-source rereads
- the mixed `help+kallsyms` build shard is still shared validation overlap only, not a help-lane ownership handoff

## Current parity surface

The current readable packet now covers:

- the roadmap-backed claim that `help` remains a valid Phase 8 repo-hosted tooling lane
- one directly readable helper-local source in `tools/lib/subcmd/help.zig`
- one directly readable validator entrypoint in `scripts/zigux/validate-phase8.py`
- one directly readable shared Phase 8 checker in `scripts/zigux/check-phase8-help-kallsyms-packet.py`
- one directly readable dedicated replay in `zigux/tests/phase8_help.zig`
- one directly readable dedicated build shard in `zigux/tests/phase8_help_only_build.zig`
- one shared-overlap build shard in `zigux/tests/phase8_help_kallsyms_only_build.zig` through the public raw fallback
- the dedicated `make -C zigux phase8-help-test` route
- the shared-overlap `make -C zigux phase8-help-kallsyms-test` route
- the parked help-and-kallsyms packet reviewable through this dedicated note plus the shared reminder surfaces

The current packet does not yet provide:

- a fresh local replay of the dedicated help-only shard from a writable authoritative checkout
- a same-source authenticated reread for the shared `help+kallsyms` build shard in this runtime
- any reason to widen the packet into exec-cmd ownership, symbol-lane parser behavior, or bridge-heavy libbpf work

## Non-goals

This slice does not yet claim:

- exec-cmd command ownership or deferred execution behavior
- kallsyms parser, truncation, CRLF, or callback-wrapper ownership
- libbpf bridge, setup-side routing, object-model, or timeout-sensitive behavior
- broader process-launch, environment-plumbing, or runtime-substrate completion

## Next bounded step

Keep the lane narrow.

The next help-local reopen step is now specific: reread `Documentation/zigux/phase8-help-slice.md`, `tools/lib/subcmd/help.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, and `make -C zigux phase8-help-test` from the strongest same-source packet the runtime can honestly provide, then land the smallest help-local reminder, helper, or focused-test follow-through that the reread actually proves without widening into exec-cmd ownership, symbol-lane parser behavior, or bridge-heavy libbpf routing.

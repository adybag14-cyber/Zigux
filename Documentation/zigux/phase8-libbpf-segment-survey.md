# Phase 8 Libbpf Segment Survey

This note records the current bounded Phase 8 libbpf segmentation reviewability gap against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SURVEY=libbpf-segment-gap-readback`
- survey checkpoint: refreshed against current `master` readback on 2026-05-19
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: current-tree reviewability and lane-safe next-step selection only

## Why this survey exists
Phase 8 only makes roadmap-aligned progress here if libbpf grows as reviewable helper-first shards instead of as a single opaque port attempt.

That means the dedicated survey has to separate directly readable current-head evidence from broader reminder surfaces when current exact GitHub reads are mixed.

## Current exact readback
Exact current-`master` readback on 2026-05-19 still returns content for:
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `Documentation/zigux/README.md`
- `zigux/Makefile`
- `tools/lib/bpf/zigux_segments/verify.zig`
- `tools/lib/bpf/zigux_segments/cpu_mask.zig`
- `tools/lib/bpf/zigux_segments/logging.zig`
- `tools/lib/bpf/zigux_segments/type_names.zig`
- `tools/lib/bpf/zigux_segments/pin_path.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`

Those directly readable files keep the currently provable helper-first packet explicit today:
- `verify.zig` now directly imports `cpu_mask.zig`, `logging.zig`, `perf_buffer_poll.zig`, `pin_path.zig`, and `type_names.zig`, keeps their bounded entrypoints explicit, and now replays stable cpu-mask, logging, type-name, pin-path, and perf-buffer helper outputs inside one narrow verifier shard.
- `cpu_mask.zig` keeps the bounded CPU-mask parsing, reader-backed summary, online-CPU eligibility, and perf-buffer auto-CPU-count selection helpers directly readable.
- `logging.zig` keeps the bounded libbpf log-level parsing, warning formatting, version formatting, errno normalization, and unknown-error rendering helpers explicit.
- `perf_buffer_poll.zig` keeps the bounded poll-summary helper surface directly readable too, including the ready-buffer attempt lookups plus the typed and errno-shaped buffer-fd and mapped-window wrappers that preserve stable caller-visible outputs below the still-deferred setup-side routing boundary.
- `type_names.zig` keeps the stable libbpf type-name tables and formatter outputs explicit.
- `pin_path.zig` keeps the bounded bpffs path join, validation, and sanitization helpers explicit.
- `Documentation/zigux/README.md` is exact-readable current repo context again, but it does not currently expose a dedicated Phase 8 or libbpf reminder packet from this runtime, so it should not be treated as shared proof for the helper packet below.
- `zigux/Makefile` is exact-readable current repo context again too, and its live body explicitly exposes the bounded `make -C zigux phase8-validate`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-libbpf-segments-test`, and `make -C zigux phase8-perf-buffer-poll-test` routes without implying that the missing focused build shards have returned through the same exact-read path.

The same authenticated exact-read path still returns `404` from this environment for:
- `tools/lib/bpf/zigux_segments/manifest.json`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`
- `zigux/tests/phase8_build.zig`
- `zigux/tests/phase8_libbpf_segments.zig`

That mixed readback means the survey should treat the bridge helper, routing helper, manifest-backed catalog, and focused build/test routes as reminder-surface or verify-shard evidence until those exact file reads become stable again, not as uniformly direct current-head proof.

The broader shared reminder packet is narrower than a full libbpf proof bundle but stronger than the older mixed-readback wording implied:
- authenticated contents reads for `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` still flap from this environment
- current repo-facing reminder surfaces already keep the landed bridge-plus-build packet explicit through `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `zigux/tests/phase8_build.zig`, `zigux/Makefile`, and `scripts/zigux/validate-phase8.py`
- the timing-adjacent poll boundary is also already explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`, and those reminder surfaces now sit on the landed ready-buffer attempt ordinals plus the typed and errno-shaped buffer-fd and mapped-window lookup packet rather than only the older wait-result wording
- those reminder surfaces keep the helper-first separation from standalone timer or clockevent helper behavior and from broader timeout-sensitive routing behavior explicit on current `master`

So those shared docs-root, tests-root, scripts-root, dedicated poll-note, and bridge-boundary surfaces should be treated as current reminder evidence for the bounded bridge-plus-build and timing-adjacent poll packet, even while they are not the same thing as uniform direct authenticated proof for every libbpf shard named by the roadmap.
That does not make the authenticated gaps irrelevant: the bridge helper, routing helper, manifest-backed catalog, and focused build files still need exact reread confirmation before they should be promoted back into the direct helper-proof bucket.

## Current bounded gap
The real same-lane gap is still truthfulness about directly readable segment evidence and the timing-adjacent poll reminder packet, not a new helper implementation claim.

Current `master` now exposes a slightly larger helper-first Phase 8 libbpf packet because `cpu_mask.zig`, `logging.zig`, and `perf_buffer_poll.zig` are exact-readable current-head evidence again, and the current reminder surfaces already keep the dedicated `Documentation/zigux/phase8-perf-buffer-poll-slice.md` timing boundary explicit. The smallest current truthful next step is to keep the survey honest about both the directly readable helper packet and the already-landed poll-boundary reminder packet without overstating the deferred setup-side routing work.

A fresh exact reread also now returns this survey itself and `zigux/Makefile`, and the still-current `scripts/zigux/README.md` Phase 8 packet is one concrete sibling reminder surface that still groups `Documentation/zigux/phase8-libbpf-segment-survey.md` with the remaining authenticated gaps. That scripts-root wording is now lagging current repo reality rather than defining it.

So the dedicated survey needs to keep four facts explicit at the same time:
- the roadmap still calls for segmented libbpf delivery under `tools/lib/bpf/zigux_segments/`
- `verify.zig`, `cpu_mask.zig`, `logging.zig`, `perf_buffer_poll.zig`, `type_names.zig`, `pin_path.zig`, and the current `zigux/Makefile` Phase 8 route family are current exact-readable evidence
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the bounded `make -C zigux phase8-perf-buffer-poll-test` route already keep the timing-adjacent no-timer and no-clockevent boundary explicit without claiming broader timeout-sensitive routing behavior
- `manifest.json`, `file_path_handle_bridge.zig`, `online_cpu_routing.zig`, `zigux/tests/phase8_build.zig`, and `zigux/tests/phase8_libbpf_segments.zig` are still exact-read gaps from this environment today even though adjacent reminder surfaces already keep that broader helper-first packet visible

## Non-goals
This survey slice does not yet claim:
- any direct Zig port of `tools/lib/bpf/libbpf.c`
- direct readable proof for every bridge, routing, manifest, or focused build shard named by roadmap or older reminder surfaces
- direct `perf_event_open()` setup, epoll wiring, mmap-backed ring ownership, or online-CPU setup parity
- live bpffs reopen flow, token materialization, `bpf_obj_get()` reopen flow, or broader fd ownership parity
- standalone timer or clockevent helper behavior, or broader timeout-sensitive routing behavior
- any reopen of the shared command or symbol packets
- any reopen of deferred object-model, descriptor-lifecycle, or bridge-heavy libbpf work

## Next bounded step
Keep this lane parked unless a fresh exact reread changes either the directly readable libbpf packet or the timing-adjacent poll reminder packet.

Preferred order:
1. reread `verify.zig`, `cpu_mask.zig`, `logging.zig`, `perf_buffer_poll.zig`, `type_names.zig`, `pin_path.zig`, `zigux/Makefile`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, and this survey note before treating any helper shard, shared Phase 8 route, or timing-boundary reminder as removed
2. if exact reads recover for `manifest.json`, `file_path_handle_bridge.zig`, `online_cpu_routing.zig`, or the focused Phase 8 build/test files, retell this survey to that larger directly readable packet
3. if sibling reminder surfaces still present `Documentation/zigux/phase8-libbpf-segment-survey.md` or the current `zigux/Makefile` Phase 8 routes as authenticated gaps, sync those reminder packets before widening into any new helper, routing, or shared validator follow-through
4. if the dedicated poll note or bridge-boundary reminder drops the no-timer or no-clockevent wording, restore that narrower boundary before widening into any helper, routing, or shared validator follow-through
5. otherwise keep bridge, routing, manifest, focused build, and shared-reminder references framed as direct gaps or reminder evidence according to the current reread surface, and reopen wider reminder-surface work only if a fresh reread proves it can be stated truthfully
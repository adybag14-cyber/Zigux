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

The same authenticated exact-read path still returns `404` from this environment for:
- `tools/lib/bpf/zigux_segments/manifest.json`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`
- `zigux/tests/phase8_build.zig`
- `zigux/tests/phase8_libbpf_segments.zig`

That mixed readback means the survey should treat the bridge helper, routing helper, manifest-backed catalog, and focused build/test routes as reminder-surface or verify-shard evidence until those exact file reads become stable again, not as uniformly direct current-head proof.

The broader shared reminder packet is also thinner than earlier wording implied:
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` still returns `404` through the authenticated contents path in this runtime.
- `Documentation/zigux/review-checklist.md` and `zigux/tests/README.md` are readable, but they do not currently carry dedicated Phase 8 or libbpf-specific reminder text.

So those shared docs-root, checklist, and tests-root surfaces should be treated as adjacent cross-phase context only, not as current shared proof for the broader Phase 8 libbpf bridge packet.
That does not make them irrelevant: the shared bridge-boundary note, review checklist, and tests-root guide remain useful reminder surfaces for bounded coordination even while they are not current dedicated proof for the broader Phase 8 libbpf bridge packet.

## Current bounded gap
The real same-lane gap is still truthfulness about directly readable segment evidence, not a new helper implementation claim.

Current `master` now exposes a slightly larger helper-first Phase 8 libbpf packet because `cpu_mask.zig`, `logging.zig`, and `perf_buffer_poll.zig` are exact-readable current-head evidence again, but the directly readable subset is still smaller than the broader bridge-and-build packet named by roadmap anchors and older reminder wording.

It also means the smallest current truthful next step is to keep the survey honest about two boundaries at once:
- the directly readable helper packet is real and now includes `verify.zig`, `cpu_mask.zig`, `logging.zig`, `perf_buffer_poll.zig`, `type_names.zig`, and `pin_path.zig`
- the broader shared Phase 8 reminder surfaces have not returned alongside it in this runtime, so docs-root, checklist, tests-root, bridge, routing, manifest, and focused build references cannot be overstated as current shared proof

So the dedicated survey needs to keep four facts explicit at the same time:
- the roadmap still calls for segmented libbpf delivery under `tools/lib/bpf/zigux_segments/`
- `verify.zig`, `cpu_mask.zig`, `logging.zig`, `perf_buffer_poll.zig`, `type_names.zig`, and `pin_path.zig` are current exact-readable evidence
- `manifest.json`, `file_path_handle_bridge.zig`, `online_cpu_routing.zig`, and the focused Phase 8 build/test files are still exact-read gaps from this environment today
- `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` should not be described as a current dedicated Phase 8 reminder packet until a fresh reread shows that Phase 8/libbpf-specific wording has actually returned there

## Non-goals
This survey slice does not yet claim:
- any direct Zig port of `tools/lib/bpf/libbpf.c`
- direct readable proof for every bridge, routing, manifest, or focused build shard named by roadmap or older reminder surfaces
- direct `perf_event_open()` setup, epoll wiring, mmap-backed ring ownership, or online-CPU setup parity
- live bpffs reopen flow, token materialization, `bpf_obj_get()` reopen flow, or broader fd ownership parity
- standalone timer or clockevent helper behavior
- any reopen of the shared command or symbol packets
- any reopen of deferred object-model, descriptor-lifecycle, or bridge-heavy libbpf work

## Next bounded step
Keep this lane parked unless a fresh exact reread changes the directly readable libbpf packet again.

Preferred order:
1. reread `verify.zig`, `cpu_mask.zig`, `logging.zig`, `perf_buffer_poll.zig`, `type_names.zig`, `pin_path.zig`, and this survey note before treating any helper shard as removed
2. if exact reads recover for `manifest.json`, `file_path_handle_bridge.zig`, `online_cpu_routing.zig`, or the focused Phase 8 build/test files, retell this survey to that larger directly readable packet
3. if `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, or `zigux/tests/README.md` later grow dedicated Phase 8 reminder wording, only then promote those shared surfaces from adjacent context to current packet proof
4. otherwise keep bridge, routing, manifest, focused build, and shared-reminder references framed as gaps or adjacent context only, and reopen wider reminder-surface work only if a fresh reread proves it can be stated truthfully
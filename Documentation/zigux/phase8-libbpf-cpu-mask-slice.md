# Phase 8 Libbpf Cpu-Mask Slice

This note records the current bounded Phase 8 cpu-mask helper slice against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-cpu-mask-helper-readback`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-23
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local cpu-mask parsing, summary, and auto-count truthfulness only

## Why this slice exists
Phase 8 makes roadmap-aligned progress here only if Zigux keeps the cpu-mask packet helper-first and reviewable instead of letting it blur into the broader perf-buffer setup and interrupt-routing path.

That means the slice has to keep the landed text-processing helper, the dedicated verifier shard, and the still-deferred setup-side routing boundary explicit at the same time.

## Current helper packet
Current `master` still keeps the bounded cpu-mask helper packet explicit through `tools/lib/bpf/zigux_segments/cpu_mask.zig` and `tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`.

That helper packet keeps `parseCpuMaskString()`, `parseCpuMaskFromReader()`, `summarizePossibleCpus()`, `summarizePossibleCpusFromReader()`, `derivePerfBufferAutoCpuCount()`, `derivePerfBufferAutoCpuCountFromString()`, `derivePerfBufferAutoCpuCountFromReader()`, and `isOnlineCpuEligible()` directly reviewable on current `master`.

The dedicated verifier shard keeps direct parse, string-backed summary, reader-backed summary, direct and reader-backed auto-count, delimiter-heavy reader inputs, injected read errors, and fail-closed malformed-input behavior explicit beside that helper.

That same landed helper packet still keeps the bounded auto-count contract honest: a requested cpu count of `0` or any request larger than the parsed possible-cpu count clamps back to the discovered possible-cpu total instead of widening into setup-side perf-event behavior.

It also keeps online-CPU eligibility reviewable as a helper-local mask-membership check only; it does not claim that current `master` already performs live sysfs reads or full routing setup.

## Deferred routing boundary
This slice still does not claim the deferred `perf-buffer-online-cpu-routing` packet.

That broader deferred packet still includes `/sys/devices/system/cpu/online` reads, `libbpf_num_possible_cpus()` interaction, online CPU filtering across live runtime state, per-CPU perf-event-array map updates, per-CPU `perf_event_open()` setup, `mmap()` ring setup, `PERF_EVENT_IOC_ENABLE` enablement, epoll-backed perf FD registration, and poll waits.

Those setup-side routing and ring-ownership steps remain intentionally deferred even though the helper-local cpu-mask parsing and auto-count packet is already reviewable on current `master`.

## Non-goals
This slice does not yet claim:
- live `/sys/devices/system/cpu/online` reads
- direct `libbpf_num_possible_cpus()` parity beyond helper-local shaping
- per-CPU perf-event-array updates or `perf_event_open()` setup
- `mmap()`-backed ring ownership, `PERF_EVENT_IOC_ENABLE`, or epoll registration
- broader timeout-sensitive routing or poll behavior
- any direct Zig port of the full `perf_buffer__new()` setup-side routing path

## Next bounded step
Keep this cpu-mask slice parked unless a future reread finds drift between this note, `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/cpu_mask_verify.zig`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, or the manifest's deferred `perf-buffer-online-cpu-routing` boundary around helper-local cpu-mask shaping.

If it reopens, reread those five surfaces together first and keep the next repair note-local or helper-proof-local rather than widening into shared validator ownership, bridge-proof ownership, or setup-side routing delivery.

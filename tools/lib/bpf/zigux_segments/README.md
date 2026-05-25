# Zigux `libbpf` Segments

This directory holds the bounded Phase 8 Zigux footholds for `tools/lib/bpf/libbpf.c`.

Current master materializes helper-first or helper-adjacent slices in:

- `cpu_mask.zig`
- `logging.zig`
- `online_cpu_routing.zig`
- `perf_buffer_poll.zig`
- `perf_buffer_ready_window.zig`
- `pin_path.zig`
- `ready_buffer_fd_lookup.zig`
- `type_names.zig`

Each materialized slice is paired with focused `*_verify.zig` coverage and the directory-level `verify.zig` aggregator so stable outputs stay reviewable without widening into loader, verifier, or object-model churn.

## Current Repo Gap

The segment manifest still needs to stay honest about one planned shared destination:

- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`

That file is not present on current `master`. Until it exists with bounded validators, the fdinfo-map-info and map-reuse helper slices remain queued groundwork rather than landed implementation.

## Still Deferred

The following Phase 8 families remain intentionally deferred:

- file-path and handle bridge side effects
- broader online-CPU setup and `perf_event` wiring
- skeleton population
- object and ELF loader work
- BTF relocation and program-load flow

That keeps the directory aligned with the roadmap rule for segmented `libbpf` work: helper-first progress with stable outputs, not speculative mirror-tree expansion.

# Phase 12 Libbpf Segment Survey

This document records the bounded Phase 12 survey lane around `tools/lib/bpf/libbpf.c` and the existing `tools/lib/bpf/zigux_segments/` rollout.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_SLICE=libbpf-segment-survey`
- scope: Phase 12 survey manifest, dedicated survey gate, shared build wiring, and a lane note that compares the current `zigux_segments/` footing against the roadmap's heavy-helper consumer plan
- product boundary:
  - `zigux/tests/phase12_libbpf_manifest.json`
  - `zigux/tests/phase12_libbpf_segments.zig`
  - `zigux/tests/phase12_libbpf_reviewability.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`

## Why this slice exists

The roadmap now places `tools/lib/bpf/libbpf.c` in Phase 12, alongside the other high-risk production-facing consumers, because the file is both large and semantically dense even though it lives under `tools/`.

That matters because the live repo already has real helper-first progress under `tools/lib/bpf/zigux_segments/`: a segment catalog, type-name helpers, and a CPU-mask parser. Those are useful footholds, but they do not yet replace the need for a current Phase 12 survey checkpoint that explains how the earlier helper work fits the modern roadmap instead of leaving libbpf stranded in Phase 8 wording.

The highest-value honest step in this lane is therefore a survey checkpoint that records the existing segmented footing, keeps the Phase 12 build gate aware of it, verifies that the landed helper files still match the segment plan, and points to the next helper-sized slice without widening into object loading, relocation, or syscall-backed behavior.

## Survey findings

- `tools/lib/bpf/libbpf.c` is present on `master` at 14,771 lines, which is large enough to cross helper, loader, object-model, relocation, and verifier-facing concerns in one file.
- the live repo already ships the earlier `tools/lib/bpf/zigux_segments/manifest.json` survey plus two landed helper slices:
  - `type_names.zig` for exported attach, link, map, and program type string tables
  - `cpu_mask.zig` for bounded CPU-mask parsing and set-bit counting
- the earlier Phase 8 tooling lane proved that helper-first segmentation works for libbpf, but the current roadmap places the broader heavy-consumer rollout in Phase 12 because the remaining work depends on object-model discipline, loader boundaries, and high-risk validation gates.
- the current Phase 12 build now re-checks the landed helper-first foundations directly by compiling `type_names.zig` and `cpu_mask.zig` through a reviewability gate and by confirming that the manifest's landed versus deferred file expectations match the real `tools/lib/bpf/zigux_segments/` directory.
- the repo still has no `logging.zig`, `pin_path.zig`, `object_loader.zig`, or relocation-facing Zig slice, and it still intentionally avoids direct ELF collection, `bpf_object` parity, BTF relocation, and load-time verifier interactions.
- the next honest libbpf-facing step is one more helper-first segment, with `logging.zig` currently the smallest roadmap-aligned follow-up.

## Recorded gaps

The survey manifest now records:

- the landed `phase12-build-gate`
- the landed `phase12-make-target`
- the landed `phase12-libbpf-segment-manifest-foundation`
- the landed `phase12-libbpf-type-name-helper-foundation`
- the landed `phase12-libbpf-cpu-mask-helper-foundation`
- the landed `phase12-libbpf-survey-gate`
- the landed `phase12-libbpf-reviewability-gate`
- the landed `phase12-libbpf-survey-note`
- the ready-next `phase12-libbpf-logging-helper`
- the still-blocked `phase12-libbpf-object-loader-and-program-load`

This keeps the lane explicit without overstating progress: Zigux already has real libbpf helper footholds, but the heavy helper consumer still needs more bounded utility slices before any object-model, loader, relocation, or syscall-backed surface should move.

## Non-goals

This survey slice does not claim:

- direct Zig parity for `tools/lib/bpf/libbpf.c`
- `logging.zig` or `pin_path.zig` implementation
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`
- ELF collection or object loading
- BTF relocation recording
- load-time verifier interactions
- syscall-backed libbpf runtime behavior

## Gates

1. run the dedicated Phase 12 build
- `zig build test --build-file zigux/tests/phase12_build.zig`

2. run the convenience target
- `make -C zigux phase12`

## Next bounded step

Stay in `tools/lib/bpf/zigux_segments/` and add `logging.zig` next so the libbpf lane can widen through one more table-driven helper slice before any pin-path, object-loader, relocation, or syscall-backed work.

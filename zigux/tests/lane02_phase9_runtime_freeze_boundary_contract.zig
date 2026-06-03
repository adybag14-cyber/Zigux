const std = @import("std");

const docs_root_phase9_packet =
    \\Phase 9 notes - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
    \\- `Documentation/zigux/review-checklist.md`
    \\- `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`
    \\- `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
    \\- `samples/zigux/runtime_trace_events.zig`
    \\- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
    \\- `samples/zigux/runtime_kretprobe.zig`
    \\- `samples/zigux/runtime_kretprobe_loader.zig`
    \\- `zigux/tests/phase9_build.zig`
    \\keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` as study-only freeze-map anchors
    \\blocked publication boundaries, install-root surfaces, and depmod-publication vocabulary stay historical blocked-boundary vocabulary
;

const review_checklist_phase9_prompt =
    \\Phase 9 reviewer prompt:
    \\if the change touches the shared Phase 9 runtime-pilot packet
    \\do `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `samples/zigux/README.md`, and `zigux/tests/README.md` still agree on the current shared reminder packet
    \\keep `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` explicit as the shipped trace-events runtime proof
    \\keep `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig` explicit
    \\keep `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig` explicit
    \\keep `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/kernel/runtime_loader_command_env_boundary_guard.zig` explicit as the narrower shared runtime-loader allocator/init-flow and command/environment boundary shard
    \\older blocked module-metadata and depmod-publication vocabulary such as `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, `Module.symvers`, module install-root, and depmod script, manifest, or alias-output state stays historical blocked-boundary vocabulary
    \\keep the returned family-local runtime kretprobe packet explicit through `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`, `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_first_loadable_parity_behavior.zig`, and the bounded `zigux/tests/phase9_build.zig` routes
;

const freeze_map_phase9_boundary =
    \\shared Phase 9 runtime-pilot freeze-boundary packet must keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, `scripts/zigux/check-phase9-trace-events-runtime-packet.py`, `scripts/zigux/check-phase9-freeze-map-study-boundaries.py`, `.github/workflows/zigux-bootstrap.yml`, `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`, `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`, `samples/zigux/runtime_kretprobe.zig`, and `samples/zigux/runtime_kretprobe_loader.zig` explicit together
    \\keep `zigux/Makefile` explicit only as a readable non-owner surface
    \\blocked publication, install-root, or deeper runtime-substrate work is complete
    \\must treat `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, `samples/zigux/runtime_trace_events_loader.zig`, the broader shared `zigux/tests/runtime_*` replay family beyond the returned trace-events survey witness and allocator/init-flow packet, and blocked publication or install-root loader boundaries as historical blocked-boundary vocabulary
    \\so the surviving narrow trace-events packet, the neighboring returned loader packet, the separate bounded runtime bitmap packet, and the returned kretprobe pilot packet do not imply that `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` has crossed the study-only boundary into delivery-ready runtime-substrate evidence
    \\the shared Phase 9 freeze-boundary packet is governance evidence only
    \\passing `scripts/zigux/check-phase9-freeze-map-study-boundaries.py` may prove the study-only inventory, reminder routes, and blocked-vocabulary warnings stayed aligned, but it must not be cited as proof that `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, blocked publication paths, install-root paths, or deeper runtime-loader substrate work became delivery-ready without a fresh Architecture Council status-change record
;

const study_only_anchors = [_][]const u8{
    "kernel/workqueue.c",
    "kernel/trace/ring_buffer.c",
};

const runtime_pilot_surfaces = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    "scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "samples/zigux/runtime_kretprobe.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "zigux/tests/phase9_build.zig",
};

const shared_reminder_surfaces = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "samples/zigux/runtime_kretprobe.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "zigux/tests/phase9_build.zig",
};

const docs_root_runtime_surfaces = [_][]const u8{
    "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    "scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    "samples/zigux/runtime_trace_events.zig",
    "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
    "samples/zigux/runtime_kretprobe.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "zigux/tests/phase9_build.zig",
};

const freeze_map_only_surfaces = [_][]const u8{
    "scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    ".github/workflows/zigux-bootstrap.yml",
};

const blocked_publication_terms = [_][]const u8{
    "blocked publication",
    "install-root",
    "blocked-boundary vocabulary",
};

const checklist_blocked_terms = [_][]const u8{
    "module install-root",
    "depmod",
    "blocked-boundary vocabulary",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireAll(haystack: []const u8, needles: []const []const u8) !void {
    for (needles) |needle| {
        try requireContains(haystack, needle);
    }
}

fn requireOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "docs root and checklist keep Phase 9 runtime freeze anchors visible" {
    try requireAll(docs_root_phase9_packet, &docs_root_runtime_surfaces);
    try requireAll(review_checklist_phase9_prompt, &shared_reminder_surfaces);
    try requireAll(docs_root_phase9_packet, &study_only_anchors);
    try requireContains(docs_root_phase9_packet, "study-only freeze-map anchors");
    try requireContains(review_checklist_phase9_prompt, "shared Phase 9 runtime-pilot packet");
}

test "freeze map keeps runtime-pilot evidence below study-only status change" {
    try requireContains(freeze_map_phase9_boundary, "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md");
    try requireContains(freeze_map_phase9_boundary, "Documentation/zigux/README.md");
    try requireContains(freeze_map_phase9_boundary, "Documentation/zigux/review-checklist.md");
    try requireContains(freeze_map_phase9_boundary, "samples/zigux/runtime_trace_events.zig");
    try requireContains(freeze_map_phase9_boundary, "samples/zigux/runtime_trace_events_registration_reentry_gate.zig");
    try requireContains(freeze_map_phase9_boundary, "samples/zigux/runtime_kretprobe.zig");
    try requireContains(freeze_map_phase9_boundary, "samples/zigux/runtime_kretprobe_loader.zig");
    try requireContains(freeze_map_phase9_boundary, "zigux/Makefile");
    try requireAll(freeze_map_phase9_boundary, &freeze_map_only_surfaces);
    try requireAll(freeze_map_phase9_boundary, &study_only_anchors);
    try requireAll(freeze_map_phase9_boundary, &blocked_publication_terms);
    try requireContains(freeze_map_phase9_boundary, "governance evidence only");
    try requireContains(freeze_map_phase9_boundary, "must not be cited as proof");
    try requireContains(freeze_map_phase9_boundary, "fresh Architecture Council status-change record");
    try requireOrdered(freeze_map_phase9_boundary, "governance evidence only", "must not be cited as proof");
}

test "runtime pilot prompt keeps returned packets separate from blocked loader vocabulary" {
    try requireContains(review_checklist_phase9_prompt, "trace-events runtime proof");
    try requireContains(review_checklist_phase9_prompt, "narrower shared runtime-loader allocator/init-flow");
    try requireContains(review_checklist_phase9_prompt, "family-local runtime kretprobe packet");
    try requireAll(review_checklist_phase9_prompt, &checklist_blocked_terms);
    try requireContains(review_checklist_phase9_prompt, ".modinfo");
    try requireContains(review_checklist_phase9_prompt, "MODULE_ALIAS()");
    try requireContains(review_checklist_phase9_prompt, "Module.symvers");
    try requireOrdered(review_checklist_phase9_prompt, "trace-events runtime proof", "family-local runtime kretprobe packet");
    try requireOrdered(review_checklist_phase9_prompt, "family-local runtime kretprobe packet", "zigux/tests/phase9_build.zig");
}

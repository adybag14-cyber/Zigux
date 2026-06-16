const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE01_DOCS_ROOT_PHASE9_NOTES=pass";
pub const self_test_pass_marker = "LANE01_DOCS_ROOT_PHASE9_NOTES_SELF_TEST=pass";

const PHASE6_HEADING = [_][]const u8{
    "Phase 6 notes -",
};

const PHASE9_HEADING = [_][]const u8{
    "Phase 9 notes -",
};

const PHASE12_HEADING = [_][]const u8{
    "Phase 12 notes -",
};

const REQUIRED_MARKERS = [_][]const u8{
    "Phase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig` - `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig` - `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig`",
    "keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.",
    "* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig`, and `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig` so the docs root matches the same study-only anchor inventory, returned loader shard, bounded build-bundle wording, and partial bitmap reminder packet already carried by the shared reviewer-facing guards.",
    "* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.",
    "* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.",
    "* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.",
    "* keep the partial runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig` are the current trusted bitmap-side evidence surfaces, and the shared build bundle now reruns that returned cold-stage guard through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle, while that returned bitmap-side visibility still must not be used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.",
    "* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the runtime bitmap sample, survey, module, diff, loader, and top-bit companion packet members, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, and the first-loadable parity-survey handle, but it is not proof that blocked publication boundaries, install-root surfaces, or broader shared runtime-loader completion returned.",
};

const CURRENT_LIKE_README = [_][]const u8{
    "# Zigux Documentation\nPhase 6 notes - placeholder\nPhase 9 notes - `Documentation/zigux/freeze-map.md` - `Documentation/zigux/phase15-study-only-anchor-accounting.md` - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` - `Documentation/zigux/review-checklist.md` - `Documentation/zigux/README.md` - `scripts/zigux/README.md` - `samples/zigux/README.md` - `zigux/tests/README.md` - `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig` - `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig` - `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig` keep the shared Phase 9 reminder packet honest by routing any study-only freeze-map summary back through the dedicated accounting note, keeping the returned loader shard and the bounded `zigux/tests/phase9_build.zig` rerun bundle explicit as shared-owner evidence, and not treating `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` as runtime-substrate readiness evidence.\n* the current docs-root Phase 9 reminder packet should stay parked on `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `scripts\\zigux/check_phase9_review_checklist_phase_boundaries.zig`, `scripts\\zigux/check_phase9_trace_events_runtime_packet.zig`, and `scripts\\zigux/check_phase9_freeze_map_study_boundaries.zig` so the docs root matches the same study-only anchor inventory, returned loader shard, bounded build-bundle wording, and partial bitmap reminder packet already carried by the shared reviewer-facing guards.\n* keep the freeze-map boundary explicit here too: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only anchors through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` rather than Phase 9 runtime-substrate readiness cues, and any shared reminder surface that summarizes them must route back through those two owner notes.\n* keep the narrow trace-events packet distinct too: `samples/zigux/runtime_trace_events.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` remain the current shipped runtime-pilot proof, while the study-only anchors stay non-owner governance context only.\n* keep the returned shared runtime-loader allocator/init-flow and command/environment boundary packet explicit as neighboring shared-owner evidence through `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, the bounded `zigux/tests/phase9_build.zig` `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` shards, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold without implying that blocked publication, install-root, or module-metadata boundaries are already solved.\n* keep the partial runtime bitmap reminder packet distinct from that returned loader shard too: `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `samples/zigux/README.md`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/phase9_build.zig`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig` are the current trusted bitmap-side evidence surfaces, and the shared build bundle now reruns that returned cold-stage guard through `phase9-runtime-bitmap-cold-stage-guard-tests` plus the aggregate `phase9-runtime-bitmap-tests` handle, while that returned bitmap-side visibility still must not be used to imply that the broader shared runtime-loader packet returned or that blocked publication boundaries are complete.\n* keep the bounded Phase 9 build bundle explicit as a rerun surface only: `zigux/tests/phase9_build.zig` now reruns the atomic64 diff, the runtime bitmap sample, survey, module, diff, loader, and top-bit companion packet members, the shared loader allocator/init-flow shard, the shared loader command/environment boundary guard, the shared trace-events loader-substrate-drift shard, and the first-loadable parity-survey handle, but it is not proof that blocked publication boundaries, install-root surfaces, or broader shared runtime-loader completion returned.\nPhase 12 notes - placeholder\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_phase6_heading_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_phase6_heading_path);
    const text_phase6_heading = try guard.readUtf8File(io, allocator, text_phase6_heading_path);
    defer allocator.free(text_phase6_heading);
    for (PHASE6_HEADING) |marker| try guard.requireMarker(text_phase6_heading, marker);
    const text_phase9_heading_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_phase9_heading_path);
    const text_phase9_heading = try guard.readUtf8File(io, allocator, text_phase9_heading_path);
    defer allocator.free(text_phase9_heading);
    for (PHASE9_HEADING) |marker| try guard.requireMarker(text_phase9_heading, marker);
    const text_phase12_heading_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_phase12_heading_path);
    const text_phase12_heading = try guard.readUtf8File(io, allocator, text_phase12_heading_path);
    defer allocator.free(text_phase12_heading);
    for (PHASE12_HEADING) |marker| try guard.requireMarker(text_phase12_heading, marker);
    const text_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_required_markers_path);
    const text_required_markers = try guard.readUtf8File(io, allocator, text_required_markers_path);
    defer allocator.free(text_required_markers);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text_required_markers, marker);
    const text_current_like_readme_path = try guard.joinPath(allocator, root, "Documentation/zigux/README.md");
    defer allocator.free(text_current_like_readme_path);
    const text_current_like_readme = try guard.readUtf8File(io, allocator, text_current_like_readme_path);
    defer allocator.free(text_current_like_readme);
    for (CURRENT_LIKE_README) |marker| try guard.requireMarker(text_current_like_readme, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

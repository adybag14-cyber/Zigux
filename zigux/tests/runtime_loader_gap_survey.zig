const std = @import("std");

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCount(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var remaining = haystack;
    while (std.mem.indexOf(u8, remaining, needle)) |match_index| {
        count += 1;
        remaining = remaining[match_index + needle.len ..];
    }
    try std.testing.expectEqual(expected_count, count);
}

test "phase 9 runtime loader gap survey keeps note and manifest aligned with the live shared packet" {
    const allocator = std.testing.allocator;

    const note = try readRepoFileAlloc(
        allocator,
        "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
        32 * 1024,
    );
    defer allocator.free(note);

    const manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_gap_manifest.json",
        32 * 1024,
    );
    defer allocator.free(manifest);

    try expectContains(note, "PHASE9_STATUS=shared-reminder-follow-through-open");
    try expectContains(note, "PHASE9_SLICE=runtime-loader-gap-survey");
    try expectContains(note, "PHASE9_LANE_KEY=P9-L18");
    try expectContains(note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(note, "`make -C zigux phase9-runtime-loader-shared-tests`");
    try expectContains(note, "`make -C zigux phase9-test`");
    try expectContains(note, "`make -C zigux phase9`");
    try expectContains(note, "There is no dedicated shared `validate-phase9.py`");
    try expectContains(note, "`scripts/zigux/README.md` still undercounts the\nlive shared loader packet");
    try expectContains(note, "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`");
    try expectContains(note, "`zigux/tests/runtime_loader_gap_manifest.json`");
    try expectContains(note, "`zigux/tests/runtime_loader_gap_survey.zig`");
    try expectContains(note, "Repair `scripts/zigux/README.md` first, then tighten");
    try expectContains(note, "`scripts/zigux/check-phase9-build-only-surface.py`");
    try expectContains(note, "`.modinfo`");
    try expectContains(note, "`MODULE_ALIAS()`");
    try expectContains(note, "`depmod` script or manifest state");

    try expectContains(manifest, "\"lane_key\": \"P9-L18\"");
    try expectContains(manifest, "\"shared_runtime_loader_files_present\": true");
    try expectContains(manifest, "\"shared_runtime_loader_contract_present\": true");
    try expectContains(manifest, "\"shared_loader_shared_tests_route_present\": true");
    try expectContains(manifest, "\"shared_phase9_bundle_route_present\": true");
    try expectContains(manifest, "\"dedicated_validate_phase9_present\": false");
    try expectContains(manifest, "\"current_honest_gate\": \"make -C zigux phase9-runtime-loader-shared-tests\"");
    try expectContains(manifest, "\"surface\": \"zigux/tests/runtime_loader_gap_survey.zig\"");
    try expectContains(manifest, "\"surface\": \"samples/zigux/runtime_trace_events_loader.zig\"");
    try expectContains(manifest, "\"surface\": \"zigux/tests/runtime_trace_events_loader_substrate_drift.zig\"");
    try expectContains(manifest, "\"next_sample_local_parity_gap\": \"none on current master;");
    try expectContains(manifest, "\"cleared_sample_local_parity_route\": \"zig build phase9-runtime-trace-events-tests --build-file zigux/tests/phase9_build.zig\"");
    try expectContains(manifest, "\"cleared_sample_local_parity_surface\": \"zigux/tests/runtime_trace_events_loader_substrate_drift.zig\"");
    try expectContains(manifest, "\"owner\": \"P9-L18\"");
    try expectContains(manifest, "\"owner\": \"P9-L11\"");
    try expectContains(manifest, "\"id\": \"runtime-loader-publication-metadata\"");
    try expectContains(manifest, "\"id\": \"runtime-trace-events-prepared-substrate-drift-proof\"");
    try expectContains(manifest, "\"status\": \"blocked_on_runtime_substrate\"");
    try expectContains(manifest, "\"status\": \"starter_landed\"");
}

test "phase 9 runtime loader gap survey keeps the shared replay routes and no-dedicated-validator boundary explicit" {
    const allocator = std.testing.allocator;

    const phase9_build = try readRepoFileAlloc(
        allocator,
        "zigux/tests/phase9_build.zig",
        96 * 1024,
    );
    defer allocator.free(phase9_build);

    const review_checklist = try readRepoFileAlloc(
        allocator,
        "Documentation/zigux/review-checklist.md",
        128 * 1024,
    );
    defer allocator.free(review_checklist);

    const lane_sequencing = try readRepoFileAlloc(
        allocator,
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        128 * 1024,
    );
    defer allocator.free(lane_sequencing);

    const scripts_readme = try readRepoFileAlloc(
        allocator,
        "scripts/zigux/README.md",
        128 * 1024,
    );
    defer allocator.free(scripts_readme);

    const tests_readme = try readRepoFileAlloc(
        allocator,
        "zigux/tests/README.md",
        128 * 1024,
    );
    defer allocator.free(tests_readme);

    const samples_readme = try readRepoFileAlloc(
        allocator,
        "samples/zigux/README.md",
        64 * 1024,
    );
    defer allocator.free(samples_readme);

    try expectContains(phase9_build, "../kernel/runtime_loader.zig");
    try expectContains(phase9_build, "../kernel/runtime_loader_contract.zig");
    try expectContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
    try expectContains(phase9_build, "runtime_loader_allocator_init_flow.zig");
    try expectContains(phase9_build, "runtime_loader_gap_survey.zig");

    try expectContains(review_checklist, "`scripts/zigux/check-phase9-build-only-surface.py`");
    try expectContains(review_checklist, "workflow-backed `make -C zigux phase9` route");
    try expectContains(review_checklist, "no-dedicated-`validate-phase9.py` posture");

    try expectContains(lane_sequencing, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(lane_sequencing, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(lane_sequencing, "`make -C zigux phase9-runtime-loader-shared-tests` remains the focused shared-loader replay");
    try expectContains(lane_sequencing, "blocked module-metadata and depmod-publication boundary");

    try expectContains(scripts_readme, "Phase 9 flow");
    try expectContains(scripts_readme, "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map");
    try expectContains(scripts_readme, "there is no dedicated shared `validate-phase9.py`");
    try expectContains(scripts_readme, "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`");
    try expectContains(scripts_readme, "`zigux/tests/runtime_loader_gap_manifest.json`");
    try expectContains(scripts_readme, "`zigux/tests/runtime_loader_gap_survey.zig`");

    try expectContains(tests_readme, "`zigux/tests/runtime_loader_allocator_init_flow.zig`");
    try expectContains(tests_readme, "`zigux/tests/runtime_loader_gap_survey.zig`");
    try expectContains(tests_readme, "`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`");

    try expectContains(samples_readme, "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map");
    try expectContains(samples_readme, "the focused `phase9-runtime-loader-shared-tests` step");
    try expectContains(samples_readme, "instead of implying a dedicated `validate-phase9.py` route");
}

test "phase 9 runtime loader gap survey keeps rollback, metadata-only trace-events evidence, and dedicated prepared-state drift proof explicit" {
    const allocator = std.testing.allocator;

    const init_flow = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_allocator_init_flow.zig",
        256 * 1024,
    );
    defer allocator.free(init_flow);

    const trace_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_trace_events_loader.zig",
        256 * 1024,
    );
    defer allocator.free(trace_loader);

    const trace_loader_substrate_drift = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_trace_events_loader_substrate_drift.zig",
        64 * 1024,
    );
    defer allocator.free(trace_loader_substrate_drift);

    try expectContains(init_flow, "phase 9 runtime loader allocator/init-flow replay covers all shipped runtime pilot handoffs");
    try expectContains(init_flow, "phase 9 runtime loader allocator/init-flow replay keeps the shared build route explicit");
    try expectContains(init_flow, "runtime_trace_events");
    try expectContains(init_flow, "runtime_kretprobe");
    try expectContains(init_flow, "runtime_loader_gap_survey.zig");
    try expectContains(init_flow, "request.plan.requires_runtime_substrate = false;");
    try expectContains(init_flow, "request.plan.module_name = \"runtime_trace_events_drift\";");
    try expectContains(init_flow, "request.plan.anchor = \"samples/trace_events/trace-events-sample-drift.c\";");
    try expectContains(init_flow, "request.plan.entry_symbol = \"zigux_runtime_trace_events_init_drift\";");
    try expectContains(init_flow, "request.plan.exit_symbol = \"zigux_runtime_trace_events_exit_drift\";");
    try expectContains(init_flow, "request.plan.allocator_handoff = .arena;");
    try expectContains(init_flow, "request.plan.provides_selftest_hook = false;");
    try expectContains(init_flow, "request.plan.init_flow.selftest_runs = 2;");
    try expectCount(
        init_flow,
        "try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));",
        7,
    );

    try expectContains(trace_loader, "registrationSnapshot");
    try expectContains(trace_loader, "prepareSharedRequest");
    try expectContains(trace_loader, "requestSharedRuntimeLoad");
    try expectContains(trace_loader, "releaseSharedWithoutSubstrate");
    try expectContains(trace_loader, "waiting_on_runtime_substrate");
    try expectContains(trace_loader, "released_without_substrate");
    try expectContains(trace_loader, "runtime trace-events loader rejects prepared shared approved-family anchor and staged init or exit symbol drift before any local runtime handoff");
    try expectContains(trace_loader, "anchor_request.plan.anchor = \"samples/trace_events/trace-events-sample-drift.c\";");
    try expectContains(trace_loader, "runtime trace-events loader rejects registration snapshot drift");
    try expectContains(trace_loader, "var drifted_register_api = snapshot;");
    try expectContains(trace_loader, "runtime trace-events loader keeps selftest-ready single registration drain explicit before shared handoff");

    try expectContains(trace_loader_substrate_drift, "phase 9 runtime trace-events loader rejects prepared shared runtime-substrate drift before any local runtime handoff");
    try expectContains(trace_loader_substrate_drift, "shared_request.plan.requires_runtime_substrate = false;");
    try expectContains(trace_loader_substrate_drift, "try std.testing.expectError(error.LoaderNotRequired, loader.requestSharedRuntimeLoad(&shared_request));");
    try expectContains(trace_loader_substrate_drift, "try std.testing.expectEqual(runtime_trace_events_loader.LoaderStage.prepared, loader.stage());");
    try expectContains(trace_loader_substrate_drift, "try std.testing.expectEqual(runtime_loader.RequestState.prepared, shared_request.state);");
}

test "phase 9 runtime loader gap survey keeps kretprobe prepared-snapshot ownership evidence explicit" {
    const allocator = std.testing.allocator;

    const kretprobe_manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_kretprobe_manifest.json",
        32 * 1024,
    );
    defer allocator.free(kretprobe_manifest);

    const kretprobe_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_kretprobe_loader.zig",
        256 * 1024,
    );
    defer allocator.free(kretprobe_loader);

    try expectContains(kretprobe_manifest, "\"prepared_snapshot_owned_by_loader_request\": true");
    try expectContains(kretprobe_manifest, "\"shared_request_surface\": \"zigux/kernel/runtime_loader.zig\"");
    try expectContains(kretprobe_manifest, "\"id\": \"runtime-kretprobe-shared-prepared-plan-drift\"");
    try expectContains(kretprobe_manifest, "\"status\": \"starter_landed\"");
    try expectContains(kretprobe_loader, "requestSharedRuntimeLoad");
    try expectContains(kretprobe_loader, "releaseSharedWithoutSubstrate");
    try expectContains(kretprobe_loader, "runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(kretprobe_loader, "runtime kretprobe loader surfaces prepared shared selftest-hook drift before any live registration claim");
    try expectContains(kretprobe_loader, "runtime kretprobe loader rejects prepared shared runtime-substrate drift before any live registration claim");
    try expectContains(kretprobe_loader, "runtime kretprobe loader rejects prepared shared allocator and init-flow drift before any live registration claim");
    try expectContains(kretprobe_loader, "runtime kretprobe loader surfaces shared request drift before any live registration claim");
    try expectContains(kretprobe_loader, "runtime kretprobe loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(
        kretprobe_loader,
        "try std.testing.expectError(error.PreparedPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));",
    );
    try expectContains(
        kretprobe_loader,
        "try std.testing.expectError(error.LoaderNotRequired, loader.requestSharedRuntimeLoad(&shared_request));",
    );
    try expectContains(
        kretprobe_loader,
        "try std.testing.expectError(error.PreparedPlanDrift, init_flow_loader.requestSharedRuntimeLoad(&init_flow_request));",
    );
}

test "phase 9 runtime loader gap survey keeps atomic64 approved-family drift proof and bitmap initialized shared-request stability explicit" {
    const allocator = std.testing.allocator;

    const atomic64_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_atomic64_loader.zig",
        256 * 1024,
    );
    defer allocator.free(atomic64_loader);

    const bitmap_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_bitmap_loader.zig",
        256 * 1024,
    );
    defer allocator.free(bitmap_loader);

    try expectContains(atomic64_loader, "runtime atomic64 loader rejects prepared shared approved-family anchor and symbol drift before any local runtime handoff");
    try expectContains(atomic64_loader, "anchor_request.plan.anchor = \"lib/atomic64_test_drift.c\";");
    try expectContains(atomic64_loader, "entry_request.plan.entry_symbol = \"zigux_runtime_atomic64_init_drift\";");
    try expectContains(atomic64_loader, "exit_request.plan.exit_symbol = \"zigux_runtime_atomic64_exit_drift\";");
    try expectContains(atomic64_loader, "try std.testing.expectError(error.InvalidPilotFamilyContract, anchor_loader.requestSharedRuntimeLoad(&anchor_request));");
    try expectContains(atomic64_loader, "try std.testing.expectError(error.InvalidPilotFamilyContract, entry_loader.requestSharedRuntimeLoad(&entry_request));");
    try expectContains(atomic64_loader, "try std.testing.expectError(error.InvalidPilotFamilyContract, exit_loader.requestSharedRuntimeLoad(&exit_request));");

    try expectContains(bitmap_loader, "runtime bitmap loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(bitmap_loader, "try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);");
    try expectContains(bitmap_loader, "try std.testing.expectEqual(@as(usize, 0), pending_plan.init_flow.selftest_runs);");
    try expectContains(bitmap_loader, "try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(");
    try expectContains(bitmap_loader, ".handoff_stage = .initialized,");
    try expectContains(bitmap_loader, ".selftest_runs = 0,");
}

test "phase 9 runtime loader gap survey keeps bitmap prepared-snapshot helper and selftest-complete shared-request stability explicit" {
    const allocator = std.testing.allocator;

    const bitmap_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_bitmap_loader.zig",
        256 * 1024,
    );
    defer allocator.free(bitmap_loader);

    try expectContains(bitmap_loader, "keepsSharedLoadPlanSnapshotExplicit(");
    try expectContains(bitmap_loader, "runtime bitmap loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(bitmap_loader, "try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);");
    try expectContains(bitmap_loader, "try std.testing.expectEqual(@as(usize, 1), pending_plan.init_flow.selftest_runs);");
    try expectContains(bitmap_loader, "try std.testing.expect(runtime_loader.keepsAllocatorInitFlowConsistent(");
    try expectContains(bitmap_loader, ".handoff_stage = .selftest_complete,");
    try expectContains(bitmap_loader, ".selftest_runs = 1,");
    try expectContains(bitmap_loader, "try loader.releaseSharedWithoutSubstrate(&shared_request);");
    try expectContains(bitmap_loader, "try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());");
    try expectContains(bitmap_loader, "try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);");
}

test "phase 9 runtime loader gap survey keeps trace-events rollback snapshots explicit after exit" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoFileAlloc(
        allocator,
        "zigux/tests/runtime_loader_gap_manifest.json",
        32 * 1024,
    );
    defer allocator.free(manifest);

    const trace_loader = try readRepoFileAlloc(
        allocator,
        "samples/zigux/runtime_trace_events_loader.zig",
        256 * 1024,
    );
    defer allocator.free(trace_loader);

    try expectContains(manifest, "Keeps metadata-only registration and rollback evidence reviewable.");
    try expectContains(manifest, "\"id\": \"runtime-trace-events-prepared-substrate-drift-proof\"");
    try expectContains(manifest, "\"status\": \"starter_landed\"");
    try expectContains(manifest, "\"cleared_sample_local_parity_surface\": \"zigux/tests/runtime_trace_events_loader_substrate_drift.zig\"");
    try expectContains(trace_loader, "runtime trace-events loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(trace_loader, "try std.testing.expectEqual(runtime_trace_events_sample.ModuleStage.exited, exited_summary.stage);");
    try expectContains(trace_loader, "try std.testing.expectError(error.InvalidModuleLifecycleForLoader, RuntimeTraceEventsLoader.planFor(&module));");
    try expectContains(trace_loader, "try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);");
    try expectContains(trace_loader, "try std.testing.expectEqual(@as(usize, 1), pending_plan.init_flow.selftest_runs);");
    try expectContains(trace_loader, "try std.testing.expectEqualStrings(\"foo_bar_reg\", selftested_summary.last_register_label orelse unreachable);");
    try expectContains(trace_loader, "try std.testing.expectEqualStrings(\"foo_bar_unreg\", selftested_summary.last_unregister_label orelse unreachable);");
    try expectContains(trace_loader, "try loader.releaseSharedWithoutSubstrate(&shared_request);");
    try expectContains(trace_loader, "try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());");
    try expectContains(trace_loader, "try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);");
}

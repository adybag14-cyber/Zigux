const std = @import("std");

const SurveySummary = struct {
    atomic64_test_c_lines: usize,
    preexisting_runtime_test_files: usize,
    preexisting_samples_zigux_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_phase9_doc_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate");
}

test "phase 9 runtime atomic64 survey manifest records the roadmap selftest hook and remaining loader blocker" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.atomic64_test_c_lines >= 200);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_samples_zigux_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_doc_present);
    try std.testing.expect(manifest.gaps.len >= 7);

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_sample_module = false;
    var saw_selftest_hook = false;
    var saw_diff_gate = false;
    var saw_loader_scaffold = false;
    var saw_live_loader_blocker = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        } else if (std.mem.startsWith(u8, gap.zigux_destination, "samples/zigux/")) {
            // Sample-side starter and loader handoff scaffolds stay under samples.
        } else {
            try std.testing.expect(std.mem.startsWith(u8, gap.zigux_destination, "zigux/kernel/"));
        }

        if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_runtime_substrate")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "runtime-atomic64-sample-module")) {
            saw_sample_module = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-selftest-hook")) {
            saw_selftest_hook = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest hooks") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-diff-gate")) {
            saw_diff_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_diff.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-loader-scaffold")) {
            saw_loader_scaffold = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "requires_runtime_substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "toSharedLoadPlan()") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runtime_loader.prepareRequest()") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-atomic64-live-loader-binding")) {
            saw_live_loader_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "lifecycle parity") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 7);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(blocked_count >= 1);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_selftest_hook);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_loader_scaffold);
    try std.testing.expect(saw_live_loader_blocker);
}

test "phase 9 runtime atomic64 survey note keeps exact selftest and loader snapshot checks explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const lane_key_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "`PHASE9_LANE_KEY={s}`",
        .{parsed.value.lane_key},
    );
    defer std.testing.allocator.free(lane_key_marker);

    const surveyed_commit_marker = try std.fmt.allocPrint(
        std.testing.allocator,
        "`PHASE9_SURVEYED_COMMIT={s}`",
        .{parsed.value.surveyed_commit},
    );
    defer std.testing.allocator.free(surveyed_commit_marker);

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, note, lane_key_marker));
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, note, surveyed_commit_marker));
    try std.testing.expect(std.mem.indexOf(u8, note, "The survey artifacts now advance to `P9-L01` because the bounded sample-side loader scaffold, the shared runtime-loader facade plus allocator/init-flow contract replay, and the shared request-surface proof are landed and reviewable on `master`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "The current direct atomic64 sample contract is verified through these exact checks:") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "the roadmap's selftest-hook requirement is already landed through the sample descriptor and `runSelftest()` contract in `samples/zigux/runtime_atomic64.zig`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "guarded init, selftest, and exit transitions plus the bounded loader handoff make lifecycle evidence reviewable, but full runtime module lifecycle parity still depends on the shared runtime substrate.") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "descriptor contract: the sample still advertises `name=runtime_atomic64`, `anchor=lib/atomic64_test.c`, `requires_runtime_substrate=true`, and `provides_selftest_hook=true`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "lifecycle and counter path: the sample still starts cold, rejects selftest before init, records one init run, swaps the seeded `0x1111_1111_2222_2222` counter down to `-9`, proves both compare-swap store and mismatch visibility, drives the blocked and changed `add_unless` branches, and finishes the bitwise path at counter `19`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "selftest closure: `runSelftest()` still reports the ordered operation families `arithmetic`, `bitwise`, `returning_ops`, `swap_ops`, and `guard_ops`, keeps the counter stable at `19`, records one selftest run, and leaves later swap or second-selftest attempts blocked after exit") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "loader snapshot stability: after `prepare()` captures the selftest-complete handoff with counter snapshot `17`, later sample mutation still leaves the pending loader handoff at snapshot `17` even while the live sample moves through swap, compare-swap, `add_unless`, `and`, and `xor` to the visible counter `15` before `requestRuntimeLoad()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "shared loader-request binding: `toSharedLoadPlan()` and `runtime_loader.prepareRequest()` still preserve the caller-provided allocator handoff, the bounded init-flow counts, the `waiting_on_runtime_substrate` transition, and the exact prepared snapshot without claiming a real loadable runtime substrate on `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "samples/zigux/runtime_atomic64_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/kernel/runtime_loader.zig") != null);
}

test "phase 9 runtime atomic64 module slice keeps the loader-backed survey packet explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "`PHASE9_LANE_KEY=P9-L01`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "selftest hook surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "guarded lifecycle parity evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "bounded loader-handoff scaffold") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "shared request-surface proof") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "dedicated runtime survey gate") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "survey-note ownership closure") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "survey-manifest closure only") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "samples/zigux/runtime_atomic64_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/kernel/runtime_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "toSharedLoadPlan()") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "runtime_loader.prepareRequest()") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "real runtime substrate remains unavailable") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "the shared `zigux/kernel/runtime_loader.zig` facade stays a review-only Phase 9 handoff packet under the freeze map's study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` boundary, so the starter keeps the shared request path explicit without implying scheduler-facing substrate closure or a freeze-map status change") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "Documentation/zigux/phase9-runtime-atomic64-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/tests/runtime_atomic64_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/tests/runtime_atomic64_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/tests/runtime_atomic64_diff.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/Makefile") != null);
}

test "phase 9 runtime atomic64 survey source-checks the direct sample evidence packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sample_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_atomic64.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sample_source);

    const loader_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_atomic64_loader.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(loader_source);

    const module_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_module.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_tests);

    const diff_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_atomic64_diff.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(diff_tests);

    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".name = \"runtime_atomic64\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".anchor = \"lib/atomic64_test.c\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".requires_runtime_substrate = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".provides_selftest_hook = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".arithmetic,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".bitwise,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".returning_ops,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".swap_ops,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".guard_ops,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "pub fn addUnlessCounter") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "self.setStage(.selftest_complete);") != null);

    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(@as(i64, 0x1111_1111_2222_2222), module.snapshotCounter());") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "const previous = try module.swapCounter(-9);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "const compare_mismatch = try module.compareSwapCounter(-9, 33);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "const add_unless_changed = try module.addUnlessCounter(-4, 99);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(@as(i64, 13), module.snapshotCounter());") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(@as(usize, 5), summary.operation_families.len);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(@as(usize, 1), module.exit_runs);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectError(error.InvalidLifecycleTransition, module.addUnlessCounter(1, 13));") != null);

    try std.testing.expect(std.mem.indexOf(u8, diff_tests, ".name = \"high-bit starter from atomic64_test.c still round-trips through exchange\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, ".seed = std.math.minInt(i64),") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, ".name = \"cmpxchg mismatch keeps the original value visible\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, ".name = \"add_unless applies the addend when the current value differs from the blocked value\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, "try std.testing.expectEqual(sample.OperationFamily.guard_ops, summary.operation_families[4]);") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, "try std.testing.expectError(error.InvalidLifecycleTransition, module.swapCounter(7));") != null);

    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".entry_symbol = \"zigux_runtime_atomic64_init\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".exit_symbol = \"zigux_runtime_atomic64_exit\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "pub fn toSharedLoadPlan(plan: RuntimeAtomic64LoadPlan) runtime_loader.LoadPlan {") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "pub fn keepsSharedLoadPlanSnapshotExplicit(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".allocator_handoff = .caller_provided,") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "var shared_request = try runtime_loader.prepareRequest(shared_plan);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "self.stage_state = .waiting_on_runtime_substrate;") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "self.stage_state = .released_without_substrate;") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(shared_plan));") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(prepared_plan));") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expect(runtime_loader.keepsSelftestHookEvidenceConsistent(pending_plan));") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "prepareSharedRequest(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "requestSharedRuntimeLoad(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "releaseSharedWithoutSubstrate(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "shared_request.requestRuntimeLoad()") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "shared_request.releaseWithoutSubstrate()") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "error.SharedLoadPlanDrift") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expectError(error.SharedLoadPlanDrift, loader.requestSharedRuntimeLoad(&shared_request));") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "runtime_loader.prepareRequest(initialized_shared_plan)") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "runtime_loader.prepareRequest(selftest_shared_plan)") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "error.InvalidSelftestHookEvidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader emits the shared runtime-loader contract plan\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader keeps initialized-stage shared contract plans explicit\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader keeps initialized shared-request snapshots stable across later selftest activity\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader bridges the shared request lifecycle without widening atomic64 claims\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader keeps shared release failures from desynchronizing loader state\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader surfaces shared request drift before any live atomic64 claim\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader surfaces prepared shared selftest-hook drift before any live atomic64 claim\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader rejects shared selftest-hook drift before any live atomic64 claim\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime atomic64 loader rejects shared-load-plan snapshot drift\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "initialized_shared_plan.provides_selftest_hook = false;") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "selftest_shared_plan.provides_selftest_hook = false;") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "const swapped = try module.swapCounter(-9);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "const compare = try module.compareSwapCounter(-9, 33);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "const add_unless = try module.addUnlessCounter(4, 99);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expectEqual(@as(i64, 15), live_counter);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expectEqual(@as(i64, 17), pending_plan.summary.counter_snapshot);") != null);
}

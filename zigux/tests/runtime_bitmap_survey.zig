const std = @import("std");

const SurveySummary = struct {
    test_bitmap_c_lines: usize,
    preexisting_runtime_bitmap_test_files: usize,
    preexisting_runtime_bitmap_sample_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_bitmap_doc_present: bool,
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

test "phase 9 runtime bitmap survey manifest records the roadmap selftest hook, landed diff gate, and remaining blocker" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_bitmap_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-Y05", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("lib/test_bitmap.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.test_bitmap_c_lines >= 1000);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_bitmap_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_bitmap_sample_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_bitmap_doc_present);
    try std.testing.expect(manifest.gaps.len >= 7);

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_phase9_build_gate = false;
    var saw_sample_module = false;
    var saw_selftest_hook = false;
    var saw_diff_gate = false;
    var saw_loader_scaffold = false;
    var saw_top_bit_boundary = false;
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

        if (std.mem.eql(u8, gap.id, "phase9-build-gate")) {
            saw_phase9_build_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "phase9-runtime-bitmap-sample-tests") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-sample-module")) {
            saw_sample_module = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-selftest-hook")) {
            saw_selftest_hook = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "selftest hooks") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-diff-gate")) {
            saw_diff_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_bitmap_diff.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-loader-scaffold")) {
            saw_loader_scaffold = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "requires_runtime_substrate") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-top-bit-boundary")) {
            saw_top_bit_boundary = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_bitmap_top_bit_contract.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "highest valid bit") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-bitmap-live-loader-binding")) {
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
    try std.testing.expect(saw_phase9_build_gate);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_selftest_hook);
    try std.testing.expect(saw_diff_gate);
    try std.testing.expect(saw_loader_scaffold);
    try std.testing.expect(saw_top_bit_boundary);
    try std.testing.expect(saw_live_loader_blocker);
}

test "phase 9 runtime bitmap survey note keeps the phase boundary and exact checks explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_bitmap_manifest.json",
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
        "Documentation/zigux/phase9-runtime-bitmap-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, note, lane_key_marker));
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, note, surveyed_commit_marker));
    try std.testing.expect(std.mem.indexOf(u8, note, "PHASE9_LANE_KEY=P9-Y05") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "not as a fifth approved Phase 5 reference idiom under `samples/zigux/`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "The shared sample-root catalog at `samples/zigux/README.md` keeps the approved Phase 5 anchors limited to `bytestream_fifo.zig`, `kobject_example.zig`, `kretprobe_example.zig`, and `trace_events_sample.zig`, while listing the runtime bitmap pair plus the focused top-bit companion replay only under the separate Phase 9 runtime pilot family.") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "the live repo still keeps that runtime bitmap family outside the four approved Phase 5 reference samples") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "the shared `samples/zigux/README.md` catalog still lists the runtime bitmap pair plus the focused top-bit companion replay only under the separate Phase 9 runtime pilot family and keeps the four approved Phase 5 anchors explicit") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "a Phase 5 approved `samples/zigux/` reference idiom") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "samples/zigux/runtime_bitmap.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "samples/zigux/runtime_bitmap_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "samples/zigux/runtime_bitmap_top_bit_contract.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "a landed sample-backed runtime starter with selftest-hook metadata under `samples/zigux/runtime_bitmap.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "the shared `zigux/tests/phase9_build.zig` gate still carries the direct `phase9-runtime-bitmap-sample-tests` leg") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "The current direct bitmap sample contract is verified through these exact checks:") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "summary stability: initializing bits `0`, `5`, `64`, and `70` still yields `first_set=0`, `first_zero=1`, `weight=4`, and `nbits=128`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "descriptor contract: the sample still advertises `name=runtime_bitmap`, `anchor=lib/test_bitmap.c`, `requires_runtime_substrate=true`, and `provides_selftest_hook=true`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "copy and selftest path: a second initialized sample can mirror the mutated bitmap, `runSelftest()` still reports the four ordered operation families `clear_set`, `copy`, `summary`, and `lifecycle`, and selftest leaves the bitmap summary unchanged") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "loader snapshot stability: after `prepare()` captures the `0,5,64,70` bitmap summary, later sample mutation still leaves the pending loader handoff at `first_set=0`, `first_zero=1`, and `weight=4` even while the live sample moves to `first_set=5`, `first_zero=0`, and `weight=7` before `requestRuntimeLoad()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "shared-loader contract replay: the loader still imports `runtime_loader`, maps initialized and selftest-complete sample stages into the shared handoff flow, fixes `allocator_handoff=.arena`, keeps `init_runs=1` and `exit_runs=0`, and rejects snapshot drift in module name, allocator handoff, handoff stage, or selftest count") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "top-bit boundary replay: the focused companion contract still proves that bit `127` is the highest valid bit") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "review-contract boundary: the direct sample still exposes the ordered review focus `descriptor_and_anchor`, `summary_replay`, and `selftest_lifecycle`; it does not claim standalone `initFromBitList()`, `formatSetBits()`, parse/print differential parity, or a loadable runtime bitmap module on `master`") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "diff-gate replay: the bounded parity cases still cover the single-word fill starter, the `79..97` cross-boundary clear cutout, the sparse `10,20,30,40,50,60,80,123` population replay, and the copied `0..108` tail-clear snapshot with `first_zero=109`") != null);
}

test "phase 9 runtime bitmap survey cross-checks the shared sample-root boundary catalog" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sample_root = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/README.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sample_root);

    try std.testing.expect(std.mem.indexOf(u8, sample_root, "Current Phase 5 reference anchors") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root, "- `samples/zigux/bytestream_fifo.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root, "- `samples/zigux/kobject_example.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root, "- `samples/zigux/kretprobe_example.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root, "- `samples/zigux/trace_events_sample.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root, "later runtime follow-ons stay under the separate Phase 9 `samples/zigux/runtime_*` family and should not be counted as extra Phase 5 reference anchors") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root, "Separate Phase 9 runtime pilot family") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root, "- `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` companion replay keep the `lib/test_bitmap.c` starter, loader handoff, and top-bit boundary fixture distinct from the Phase 5 sample packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_root, "samples/zigux/runtime_bitmap_top_bit_contract.zig") != null);
}

test "phase 9 runtime bitmap module slice keeps the loader-backed survey packet explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(note);

    try std.testing.expect(std.mem.indexOf(u8, note, "PHASE9_LANE_KEY=P9-Y05") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "sample-side loader scaffold") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "dedicated Phase 9 survey and test wiring") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "Documentation/zigux/phase9-runtime-bitmap-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "samples/zigux/runtime_bitmap_loader.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zigux/tests/runtime_bitmap_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "provides_selftest_hook=true") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, note, "make -C zigux phase9") != null);
}

test "phase 9 runtime bitmap survey source-checks the direct sample evidence packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sample_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_bitmap.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sample_source);

    const loader_source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_bitmap_loader.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(loader_source);

    const module_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_bitmap_module.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_tests);

    const diff_tests = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_bitmap_diff.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(diff_tests);

    const phase9_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase9_build.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(phase9_build);

    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".name = \"runtime_bitmap\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".anchor = \"lib/test_bitmap.c\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".requires_runtime_substrate = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".provides_selftest_hook = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".descriptor_and_anchor,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".summary_replay,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".selftest_lifecycle,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".summary,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, ".lifecycle,") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectEqual(@as(u32, 4), summary.weight);") != null);
    try std.testing.expect(std.mem.indexOf(u8, sample_source, "try std.testing.expectEqual(RuntimeBitmapSample.bitmap_nbits, summary.nbits);") != null);

    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try module.clearRange(second_word_base, 2);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try module.setRange(9, 4);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(@as(u32, 7), summary.weight);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(@as(usize, 4), selftest.operation_families.len);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(sample.OperationFamily.summary, selftest.operation_families[2]);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(sample.OperationFamily.lifecycle, selftest.operation_families[3]);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(sample.ModuleStage.exited, module.stage());") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(@as(usize, 1), module.exit_runs);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectError(error.InvalidLifecycleTransition, module.exit());") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectError(error.InvalidLifecycleTransition, module.initWithSetBits(&.{ 1, 2 }));") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectError(error.BitRangeOutOfBounds, module.setRange(sample.RuntimeBitmapSample.bitmap_nbits - 1, 2));") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectError(error.BitRangeOutOfBounds, module.clearRange(sample.RuntimeBitmapSample.bitmap_nbits, 1));") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "const before = module.summary();") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try module.setRange(5, 0);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try module.clearRange(sample.RuntimeBitmapSample.bitmap_nbits, 0);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "const after = module.summary();") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(before.first_set, after.first_set);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(before.first_zero, after.first_zero);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectEqual(before.weight, after.weight);") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectError(error.InvalidSourceLifecycle, module.copyFrom(&cold_source));") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_tests, "try std.testing.expectError(error.InvalidSourceLifecycle, module.copyFrom(&exited_source));") != null);

    try std.testing.expect(std.mem.indexOf(u8, diff_tests, ".name = \"test_fill_set single-word starter\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, ".clear_ranges = &.{.{ .start = 79, .len = 19 }},") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, ".init_bits = &.{ 10, 20, 30, 40, 50, 60, 80, 123 },") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, "try source.setRange(0, 109);") != null);
    try std.testing.expect(std.mem.indexOf(u8, diff_tests, "try std.testing.expectEqual(@as(u32, 109), summary.first_zero);") != null);

    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".entry_symbol = \"zigux_runtime_bitmap_init\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".exit_symbol = \"zigux_runtime_bitmap_exit\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "self.stage_state = .waiting_on_runtime_substrate;") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "self.stage_state = .released_without_substrate;") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "@import(\"runtime_loader\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "toSharedLoadPlan(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "prepareRequest(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "keepsAllocatorInitFlowConsistent(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "prepareSharedRequest(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "requestSharedRuntimeLoad(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "releaseSharedWithoutSubstrate(") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "shared_request.requestRuntimeLoad()") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "shared_request.releaseWithoutSubstrate()") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "error.SharedLoadPlanDrift") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, ".summary = module.summary(),") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader keeps the prepared snapshot stable across later bitmap mutation\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader emits the shared runtime-loader contract plan\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader keeps initialized-stage shared contract plans explicit\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader keeps initialized shared-request snapshots stable across later selftest activity\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader bridges the shared request lifecycle without widening bitmap claims\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader keeps shared release failures from desynchronizing loader state\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader surfaces shared request drift before any live bitmap claim\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader rejects shared selftest-hook drift before any live bitmap claim\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "test \"runtime bitmap loader rejects shared-load-plan snapshot drift\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try module.clearRange(0, 1);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try module.setRange(9, 4);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expectEqual(@as(u32, 5), live_summary.first_set);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expectEqual(@as(u32, 0), pending_plan.summary.first_set);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expectEqual(@as(u32, 7), live_summary.weight);") != null);
    try std.testing.expect(std.mem.indexOf(u8, loader_source, "try std.testing.expectEqual(@as(u32, 4), pending_plan.summary.weight);") != null);

    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-bitmap-sample-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-bitmap-top-bit-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-loader-shared-tests") != null);
}

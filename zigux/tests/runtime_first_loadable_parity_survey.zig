const std = @import("std");

fn readRepoFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase9 first-loadable parity note matches the surviving shared packet" {
    const parity_note = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-first-loadable-runtime-module-parity.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(parity_note);

    const atomic64_survey_note = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-runtime-atomic64-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(atomic64_survey_note);

    const atomic64_module_slice = try readRepoFileAlloc(
        "../../Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(atomic64_module_slice);

    const atomic64_manifest = try readRepoFileAlloc(
        "runtime_atomic64_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(atomic64_manifest);

    const atomic64_survey_test = try readRepoFileAlloc(
        "runtime_atomic64_survey.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(atomic64_survey_test);

    const kretprobe_sample = try readRepoFileAlloc(
        "../../samples/zigux/runtime_kretprobe.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(kretprobe_sample);

    const kretprobe_module = try readRepoFileAlloc(
        "runtime_kretprobe_module.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(kretprobe_module);

    const manifest = try readRepoFileAlloc(
        "runtime_bitmap_manifest.json",
        16 * 1024,
    );
    defer std.testing.allocator.free(manifest);

    const phase9_build = try readRepoFileAlloc(
        "phase9_build.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try expectContains(parity_note, "`PHASE9_STATUS=active`");
    try expectContains(parity_note, "`PHASE9_LANE_KEY=P9-L01`");
    try expectContains(
        parity_note,
        "`PHASE9_SURVEYED_COMMIT=2026-05-25-first-loadable-parity-bitmap-direct-init-readback`",
    );
    try expectContains(
        parity_note,
        "Trusted current-tree reads on 2026-05-25 now show a four-part Phase 9 pilot picture",
    );
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-atomic64-survey.md`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-atomic64-module-slice.md`");
    try expectContains(parity_note, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_atomic64_manifest.json`");
    try expectContains(
        parity_note,
        "Current `master` now directly materializes the atomic64 sample, survey, and manifest packet beside the already readable module, diff, and family-local note surfaces.",
    );
    try expectContains(parity_note, "`samples/zigux/runtime_kretprobe.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_kretprobe_module.zig`");
    try expectContains(parity_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(
        parity_note,
        "Current `master` now directly materializes the kretprobe sample and module lifecycle packet beside the shared Phase 9 build shard, but it still does not return a family-local loader scaffold for that direct packet.",
    );
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-bitmap-survey.md`");
    try expectContains(parity_note, "`Documentation/zigux/phase9-runtime-bitmap-module-slice.md`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_direct_init_contract.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_cold_stage_guard.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(parity_note, "`samples/zigux/runtime_bitmap_top_bit_contract.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_manifest.json`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_survey.zig`");
    try expectContains(parity_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_module.zig`");
    try expectContains(parity_note, "`zigux/tests/runtime_bitmap_diff.zig`");
    try expectContains(
        parity_note,
        "Current `master` now directly materializes the bitmap direct-init companion beside the visible sample, cold-stage guard, loader, top-bit, survey, manifest, module, and diff packet while broader shared loader completion remains blocked.",
    );
    try expectContains(
        parity_note,
        "These shared runtime-loader-facing surfaces are directly readable on current `master`:",
    );
    try expectContains(parity_note, "`zigux/tests/runtime_loader_allocator_init_flow.zig`");
    try expectContains(parity_note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(parity_note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(parity_note, "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`");
    try expectContains(parity_note, "phase9-runtime-atomic64-diff");
    try expectContains(parity_note, "the build-local `phase9-runtime-atomic64-module-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-atomic64-sample-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-kretprobe-sample-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-kretprobe-module-tests` route name");
    try expectContains(parity_note, "the aggregate `phase9-runtime-kretprobe-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-bitmap-direct-init-contract-tests` route name");
    try expectContains(parity_note, "the bounded bitmap sample, direct-init companion, cold-stage guard, loader, survey, top-bit, module, and diff routes");
    try expectContains(parity_note, "the build-local `phase9-runtime-loader-allocator-init-flow-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-loader-command-env-boundary-guard-tests` route name");
    try expectContains(parity_note, "the build-local `phase9-runtime-loader-shared-tests` route name");
    try expectContains(parity_note, "the shared `phase9-first-loadable-runtime-module-parity-survey-tests` handle");
    try expectContains(
        parity_note,
        "those surviving shared-loader and cross-family route names are reminder vocabulary rather than proof that the underlying Phase 9 parity target shipped",
    );
    try expectContains(parity_note, "does not yet materialize that target as a coherent cross-family packet");
    try expectContains(parity_note, "must not claim shipped cross-family loader parity");
    try expectContains(
        parity_note,
        "must not claim shipped cross-family loader parity, shipped runtime-loader handoff parity, or shipped end-to-end module lifecycle parity on current `master`.",
    );
    try expectContains(
        parity_note,
        "Leave `P9-L01` parked unless a fresh live reread finds another exact cross-family parity-summary mismatch between this note, the shared survey gate, the shared build shard, the visible atomic64 and kretprobe direct packets without returned family-local loader scaffolds, and the still-partial bitmap reminder packet with returned direct-init companion, restored cold-stage guard, module, and diff proof but without broader shared runtime-loader parity.",
    );

    try expectContains(atomic64_survey_note, "`PHASE9_STATUS=active`");
    try expectContains(atomic64_survey_note, "`PHASE9_SLICE=runtime-atomic64-survey`");
    try expectContains(atomic64_survey_note, "`PHASE9_LANE_KEY=P9-L04`");
    try expectContains(atomic64_survey_note, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(atomic64_survey_note, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(atomic64_survey_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(atomic64_survey_note, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(atomic64_survey_note, "`zigux/tests/runtime_atomic64_manifest.json`");
    try expectContains(
        atomic64_survey_note,
        "The shared-loader reminder surfaces visible here keep the broader runtime-substrate blocker explicit, so this packet is still not a completed loadable runtime-module path.",
    );
    try expectContains(
        atomic64_survey_note,
        "`phase9-runtime-atomic64-diff`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-tests`, and `phase9-runtime-loader-shared-tests` explicit",
    );

    try expectContains(atomic64_module_slice, "`PHASE9_STATUS=active`");
    try expectContains(atomic64_module_slice, "`PHASE9_SLICE=runtime-atomic64-module-starter`");
    try expectContains(atomic64_module_slice, "`PHASE9_LANE_KEY=P9-L04`");
    try expectContains(atomic64_module_slice, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(atomic64_module_slice, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(atomic64_module_slice, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(atomic64_module_slice, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(atomic64_module_slice, "`zigux/tests/runtime_atomic64_manifest.json`");
    try expectContains(atomic64_module_slice, "`samples/zigux/runtime_bitmap_loader.zig`");
    try expectContains(
        atomic64_module_slice,
        "the direct atomic64 packet is still narrower than full loader-backed parity",
    );
    try expectContains(
        atomic64_module_slice,
        "`phase9-runtime-atomic64-diff`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-tests`, and `phase9-runtime-loader-shared-tests` explicit",
    );
    try expectContains(
        atomic64_module_slice,
        "No claim of full loadable module lifecycle parity before the shared runtime substrate lands.",
    );

    try expectContains(atomic64_manifest, "\"phase\": \"Phase 9\"");
    try expectContains(atomic64_manifest, "\"lane_key\": \"P9-L04\"");
    try expectContains(
        atomic64_manifest,
        "\"surveyed_commit\": \"2026-05-23-runtime-atomic64-shared-loader-reminder-trim\"",
    );
    try expectContains(
        atomic64_manifest,
        "\"landed_pilot_state\": \"starter_landed_with_visible_shared_loader_packet\"",
    );
    try expectContains(atomic64_manifest, "runtime-bitmap-loader-companion");
    try expectContains(atomic64_manifest, "samples/zigux/runtime_bitmap_loader.zig");
    try expectContains(atomic64_manifest, "runtime-atomic64-family-make-route");
    try expectContains(atomic64_manifest, "\"path\": \"zigux/Makefile\"");
    try expectContains(atomic64_manifest, "runtime-atomic64-shared-build-boundary");
    try expectContains(atomic64_manifest, "runtime-atomic64-live-loader-binding");
    try expectContains(
        atomic64_manifest,
        "the direct survey gate and visible shared-loader reminder packet stay family-local evidence outside standalone shared-build route names",
    );

    try expectContains(
        atomic64_survey_test,
        "phase 9 runtime atomic64 survey manifest records the visible shared-loader reminder packet",
    );
    try expectContains(atomic64_survey_test, "runtime-atomic64-survey-note");
    try expectContains(
        atomic64_survey_test,
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
    );
    try expectContains(atomic64_survey_test, "runtime-atomic64-module-slice-note");
    try expectContains(
        atomic64_survey_test,
        "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
    );
    try expectContains(
        atomic64_survey_test,
        "starter_landed_with_visible_shared_loader_packet",
    );
    try expectContains(atomic64_survey_test, "runtime-atomic64-live-loader-binding");

    try expectContains(kretprobe_sample, "runtime kretprobe sample advertises the bounded pilot-module contract");
    try expectContains(kretprobe_sample, ".provides_selftest_hook = true");
    try expectContains(
        kretprobe_sample,
        "runtime kretprobe sample keeps reusable probe replay explicit after selftest",
    );
    try expectContains(
        kretprobe_sample,
        "runtime kretprobe sample keeps duplicate registration rollback explicit across initialized and selftested stages",
    );

    try expectContains(kretprobe_module, "runtime kretprobe sample advertises the bounded pilot-module contract");
    try expectContains(
        kretprobe_module,
        "runtime kretprobe sample keeps selftest summary replay explicit at the module boundary",
    );
    try expectContains(
        kretprobe_module,
        "runtime kretprobe sample keeps lifecycle snapshot replay explicit at the module boundary",
    );
    try expectContains(
        kretprobe_module,
        "runtime kretprobe sample keeps duplicate registration and failed exit rollback explicit at the module boundary",
    );

    try expectContains(manifest, "\"phase\": \"Phase 9\"");
    try expectContains(manifest, "\"lane_key\": \"P9-L08\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(
        manifest,
        "\"surveyed_commit\": \"e306440f579ded71e8441c1a513af6fd12bbbfdd\"",
    );
    try expectContains(manifest, "\"sample_path\": \"samples/zigux/runtime_bitmap.zig\"");
    try expectContains(manifest, "\"loader_path\": \"samples/zigux/runtime_bitmap_loader.zig\"");
    try expectContains(manifest, "\"module_path\": \"zigux/tests/runtime_bitmap_module.zig\"");
    try expectContains(manifest, "\"diff_path\": \"zigux/tests/runtime_bitmap_diff.zig\"");
    try expectContains(manifest, "\"top_bit_path\": \"samples/zigux/runtime_bitmap_top_bit_contract.zig\"");
    try expectContains(manifest, "diff_summary_replay");
    try expectContains(manifest, "diff_copy_tail_clearing");
    try expectContains(manifest, "diff_exit_lifecycle_guards");

    try expectContains(phase9_build, "phase9-runtime-atomic64-diff");
    try expectContains(phase9_build, "phase9-runtime-atomic64-loader-tests");
    try expectContains(phase9_build, "phase9-runtime-bitmap-tests");
    try expectContains(phase9_build, "phase9-runtime-bitmap-sample-tests");
    try expectContains(phase9_build, "phase9-runtime-bitmap-direct-init-contract-tests");
    try expectContains(phase9_build, "phase9-runtime-bitmap-loader-tests");
    try expectContains(phase9_build, "phase9-runtime-bitmap-survey-tests");
    try expectContains(phase9_build, "phase9-runtime-bitmap-diff-tests");
    try expectContains(phase9_build, "phase9-runtime-bitmap-top-bit-tests");
    try expectContains(phase9_build, "phase9-runtime-kretprobe-sample-tests");
    try expectContains(phase9_build, "phase9-runtime-kretprobe-module-tests");
    try expectContains(phase9_build, "phase9-runtime-kretprobe-tests");
    try expectContains(phase9_build, "phase9-runtime-loader-allocator-init-flow-tests");
    try expectContains(phase9_build, "phase9-runtime-loader-command-env-boundary-guard-tests");
    try expectContains(phase9_build, "phase9-runtime-loader-shared-tests");
    try expectContains(phase9_build, "phase9-first-loadable-runtime-module-parity-survey-tests");
    try expectContains(phase9_build, "runtime_first_loadable_parity_survey.zig");
    try expectContains(
        phase9_build,
        "Run the Phase 9 first-loadable runtime-module parity survey tests.",
    );
    try expectContains(phase9_build, "phase9-runtime-atomic64-sample-tests");
    try expectContains(phase9_build, "phase9-runtime-atomic64-module-tests");
    try std.testing.expect(
        std.mem.indexOf(u8, phase9_build, "phase9-runtime-atomic64-survey-tests") == null,
    );
    try expectContains(phase9_build, "phase9-runtime-bitmap-module-tests");
}

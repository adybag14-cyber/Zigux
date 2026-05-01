const std = @import("std");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const atomic64_diff_source = @embedFile("atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");
const phase4_runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");
const phase4_validation_matrix_source = @embedFile("../../Documentation/zigux/phase4-validation-matrix.md");

comptime {
    _ = runtime_atomic64_diff;
}

fn expectRuntimeMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, runtime_atomic64_diff_source, marker) != null);
}

fn expectWrapperMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, atomic64_diff_source, marker) != null);
}

fn expectWrapperNoMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, atomic64_diff_source, marker) == null);
}

fn expectManifestMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, phase4_runtime_atomic64_manifest_source, marker) != null);
}

fn expectMatrixMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, phase4_validation_matrix_source, marker) != null);
}

test "atomic64 diff wrapper keeps the bounded runtime replay body reachable" {
    try expectRuntimeMarker("runtime atomic64 diff gate replays bounded atomic64_test.c");
    try expectRuntimeMarker("runtime atomic64 diff gate keeps selftest family coverage explicit");
    try expectRuntimeMarker("runtime atomic64 diff gate keeps lifecycle transitions single-shot");
    try expectRuntimeMarker("runtime atomic64 diff gate keeps post-selftest replay explicit");
}

test "atomic64 diff wrapper stays a thin phase4 entrypoint" {
    const runtime_sample_import = "const sample = @import(\"runtime_" ++ "atomic64_sample\");";
    const runtime_struct_name = "RuntimeAtomic64" ++ "Sample";
    const runtime_selftest_call = "runSelf" ++ "test()";
    const runtime_add_call = "addCounter" ++ "(";

    try expectWrapperMarker(
        "const runtime_atomic64_diff = @import(\"runtime_atomic64_diff.zig\");",
    );
    try expectWrapperMarker(
        "const runtime_atomic64_diff_source = @embedFile(\"runtime_atomic64_diff.zig\");",
    );

    try expectWrapperNoMarker(runtime_sample_import);
    try expectWrapperNoMarker(runtime_struct_name);
    try expectWrapperNoMarker(runtime_selftest_call);
    try expectWrapperNoMarker(runtime_add_call);
}

test "atomic64 diff wrapper keeps roadmap entrypoint and rollback evidence aligned" {
    try expectManifestMarker("\"zigux/tests/atomic64_diff.zig\"");
    try expectManifestMarker("\"roadmap_atomic64_wrapper_targets_runtime_diff\": true");
    try expectManifestMarker("\"phase4_build_uses_atomic64_wrapper\": true");
    try expectManifestMarker("\"phase4_validator_atomic64_diff_present\": true");
    try expectManifestMarker("\"phase9_build_uses_runtime_atomic64_diff\": true");
    try expectManifestMarker("\"id\": \"phase4-roadmap-path-alignment\"");
}

test "atomic64 diff wrapper keeps roadmap Phase 4 matrix evidence explicit" {
    try expectMatrixMarker("### `zigux/tests/atomic64_diff.zig`");
    try expectMatrixMarker("- rollback owner: `ABI and Runtime Team`");
    try expectMatrixMarker(
        "workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests`",
    );
    try expectMatrixMarker("`make -C zigux phase4-runtime-atomic64-diff`");
    try expectMatrixMarker(
        "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`",
    );
    try expectMatrixMarker(
        "perf threshold status: correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set",
    );
    try expectMatrixMarker("`threshold_pending_until_runtime_atomic64_scope_widens`");
}

test "atomic64 diff wrapper records the exact bounded runtime atomic64 checks" {
    try expectRuntimeMarker("add grows the starter counter by the onestwos constant from atomic64_test.c");
    try expectRuntimeMarker("add accepts the negative one decrement path from atomic64_test.c");
    try expectRuntimeMarker("sub matches the wide onestwos decrement from atomic64_test.c");
    try expectRuntimeMarker("sub accepts the negative one increment path from atomic64_test.c");

    try expectRuntimeMarker("or matches the v0|v1 family from atomic64_test.c");
    try expectRuntimeMarker("and matches the v0&v1 family from atomic64_test.c");
    try expectRuntimeMarker("xor matches the v0^v1 family from atomic64_test.c");
    try expectRuntimeMarker("andnot matches the v0&~v1 family from atomic64_test.c");

    try expectRuntimeMarker("v0 to v1 keeps the original counter visible as the exchange return value");
    try expectRuntimeMarker("v1 to v2 keeps wide negative and positive 64-bit values distinct");
    try expectRuntimeMarker("high-bit starter from atomic64_test.c still round-trips through exchange");
    try expectRuntimeMarker("cmpxchg success path stores the desired value when the expected value matches");
    try expectRuntimeMarker("cmpxchg mismatch keeps the original value visible");

    try expectRuntimeMarker("add_unless leaves the counter untouched when it already matches the blocked value");
    try expectRuntimeMarker("add_unless applies the addend when the current value differs from the blocked value");
    try expectRuntimeMarker("inc_not_zero increments a positive non-zero counter");
    try expectRuntimeMarker("inc_not_zero leaves zero unchanged");
    try expectRuntimeMarker("inc_not_zero still increments -1 back to zero");
    try expectRuntimeMarker("inc_not_zero keeps the high-bit atomic64_test.c sentinel nonzero while incrementing it");
    try expectRuntimeMarker("dec_if_positive decrements a positive counter and returns the decremented value");
    try expectRuntimeMarker("dec_if_positive returns -1 for zero without changing storage");
    try expectRuntimeMarker("dec_if_positive returns seed minus one for negative inputs without storing it");

    try expectRuntimeMarker("checked_returning_paths");
    try expectRuntimeMarker("checked_guard_paths");
    try expectRuntimeMarker("const initialized_summary = module.summary();");
    try expectRuntimeMarker("const post_selftest_summary = module.summary();");
    try expectRuntimeMarker("const exited_summary = module.summary();");
    try expectRuntimeMarker("initialized_summary.init_runs");
    try expectRuntimeMarker("post_selftest_summary.selftest_runs");
    try expectRuntimeMarker("exited_summary.exit_runs");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, cold_module.exit()");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.init(11)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.init(13)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.exit()");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.init(17)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.incNotZeroCounter()");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.decIfPositiveCounter()");
}

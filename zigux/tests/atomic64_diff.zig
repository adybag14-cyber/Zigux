const std = @import("std");
const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");
const atomic64_diff_source = @embedFile("atomic64_diff.zig");
const runtime_atomic64_diff_source = @embedFile("runtime_atomic64_diff.zig");
const phase4_runtime_atomic64_manifest_source = @embedFile("phase4_runtime_atomic64_diff_manifest.json");
const phase4_build_source = @embedFile("phase4_build.zig");
const phase4_makefile_source = @embedFile("../Makefile");
const phase4_workflow_source = @embedFile("../../.github/workflows/zigux-bootstrap.yml");
const phase9_build_source = @embedFile("phase9_build.zig");
const validate_phase4_source = @embedFile("../../scripts/zigux/validate-phase4.py");
const phase4_gate_evidence_source = @embedFile("../../Documentation/zigux/phase4-gate-evidence.md");
const check_phase4_gate_evidence_source = @embedFile("../../scripts/zigux/check-phase4-gate-evidence.py");

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

fn expectValidatorMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, validate_phase4_source, marker) != null);
}

fn expectGateEvidenceMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, phase4_gate_evidence_source, marker) != null);
}

fn expectGateEvidenceCheckerMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, check_phase4_gate_evidence_source, marker) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;

    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }

    return count;
}

fn expectSingleOccurrence(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn expectRuntimeCaseGroupCardinality(
    group_header: []const u8,
    loop_header: []const u8,
    expected_case_count: usize,
) !void {
    const section_start = std.mem.indexOf(u8, runtime_atomic64_diff_source, group_header) orelse
        return error.MissingRuntimeCaseGroupHeader;
    const section_end = std.mem.indexOfPos(u8, runtime_atomic64_diff_source, section_start, loop_header) orelse
        return error.MissingRuntimeCaseGroupLoop;
    const section = runtime_atomic64_diff_source[section_start..section_end];

    try std.testing.expectEqual(expected_case_count, countOccurrences(section, ".name = "));
}

fn expectWorkspaceMarker(path: []const u8, marker: []const u8, limit: usize) !void {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const source = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
    defer std.testing.allocator.free(source);

    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectPhase4MatrixMarker(marker: []const u8) !void {
    try expectWorkspaceMarker(
        "Documentation/zigux/phase4-validation-matrix.md",
        marker,
        32 * 1024,
    );
}

fn expectPhase4BuildMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, phase4_build_source, marker) != null);
}

fn expectPhase4MakefileMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, phase4_makefile_source, marker) != null);
}

fn expectPhase4WorkflowMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, phase4_workflow_source, marker) != null);
}

fn expectPhase9BuildMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, phase9_build_source, marker) != null);
}

test "atomic64 diff wrapper keeps the bounded runtime replay body reachable" {
    try expectRuntimeMarker("runtime atomic64 diff gate replays bounded atomic64_test.c");
    try expectRuntimeMarker("runtime atomic64 diff gate keeps selftest family coverage explicit");
    try expectRuntimeMarker("runtime atomic64 diff gate keeps lifecycle transitions single-shot");
    try expectRuntimeMarker("runtime atomic64 diff gate keeps post-selftest replay explicit");
}

test "atomic64 diff wrapper stays a thin phase4 entrypoint" {
    const runtime_sample_import = "const sample = @import(\"runtime_" ++ "atomic64_sample\");";
    const runtime_sample_struct_name = "sample.RuntimeAtomic64" ++ "Sample";
    const runtime_operation_family_marker = "sample.OperationFamily.arithmetic";
    const runtime_stage_marker = "sample.ModuleStage.selftest_complete";
    const runtime_exited_stage_marker = "sample.ModuleStage.exited";
    const runtime_struct_name = "RuntimeAtomic64" ++ "Sample";
    const runtime_selftest_replay =
        "const summary = try module.runSelf" ++ "test();";
    const runtime_post_selftest_add =
        "const add_result = try module.add" ++ "Counter(";

    try expectWrapperMarker(
        "const runtime_atomic64_diff = @import(\"runtime_atomic64_diff.zig\");",
    );
    try expectWrapperMarker(
        "const runtime_atomic64_diff_source = @embedFile(\"runtime_atomic64_diff.zig\");",
    );

    try expectRuntimeMarker(runtime_sample_struct_name);
    try expectRuntimeMarker(runtime_operation_family_marker);
    try expectRuntimeMarker(runtime_stage_marker);
    try expectRuntimeMarker(runtime_exited_stage_marker);
    try expectSingleOccurrence(runtime_atomic64_diff_source, runtime_sample_import);
    try expectWrapperNoMarker(runtime_sample_import);
    try expectWrapperNoMarker(runtime_struct_name);
    try expectWrapperNoMarker(runtime_selftest_replay);
    try expectWrapperNoMarker(runtime_post_selftest_add);
}

test "atomic64 diff wrapper keeps roadmap entrypoint and rollback evidence aligned" {
    try expectManifestMarker("\"lane_key\": \"P4-L04\"");
    try expectManifestMarker("\"zigux/tests/atomic64_diff.zig\"");
    try expectManifestMarker("\"roadmap_atomic64_wrapper_targets_runtime_diff\": true");
    try expectManifestMarker("\"phase4_build_uses_atomic64_wrapper\": true");
    try expectManifestMarker("\"phase9_build_present\": true");
    try expectManifestMarker("\"phase4_validator_atomic64_diff_present\": true");
    try expectManifestMarker("\"phase4_validator_runtime_atomic64_diff_present\": true");
    try expectManifestMarker("\"phase9_build_uses_runtime_atomic64_diff\": true");
    try expectManifestMarker("\"id\": \"phase4-roadmap-path-alignment\"");
}

test "atomic64 diff wrapper keeps isolated rollback replay evidence explicit" {
    try expectPhase4MatrixMarker("`make -C zigux phase4-runtime-atomic64-diff`");
    try expectPhase4MatrixMarker(
        "`zig build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig`",
    );
    try expectPhase4MatrixMarker("`threshold_pending_until_runtime_atomic64_scope_widens`");
    try expectPhase4MatrixMarker("`runtime_atomic64_diff.zig` remains the single replay body");
    try expectPhase4MatrixMarker(
        "removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move",
    );
}

test "atomic64 diff wrapper checks live phase4 and phase9 build entrypoints directly" {
    try expectPhase4BuildMarker(".root_source_file = b.path(\"atomic64_diff.zig\")");
    try expectPhase4BuildMarker("phase4-runtime-atomic64-diff-tests");
    try expectPhase4BuildMarker("phase4-runtime-atomic64-diff-survey-tests");
    try expectPhase4BuildMarker("phase4-runtime-atomic64-diff");
    try std.testing.expect(std.mem.indexOf(
        u8,
        phase4_build_source,
        ".root_source_file = b.path(\"runtime_atomic64_diff.zig\")",
    ) == null);

    try expectPhase9BuildMarker(".root_source_file = b.path(\"runtime_atomic64_diff.zig\")");
    try expectPhase9BuildMarker("phase9-runtime-atomic64-diff-tests");
    try expectPhase9BuildMarker("runtime_atomic64_diff_module");
    try std.testing.expect(std.mem.indexOf(
        u8,
        phase9_build_source,
        ".root_source_file = b.path(\"atomic64_diff.zig\")",
    ) == null);
}

test "atomic64 diff wrapper checks the published phase4 make entrypoints directly" {
    try expectPhase4MakefileMarker("PHONY += phase4-validate phase4-test phase4-runtime-atomic64-diff");
    try expectPhase4MakefileMarker("phase4-test:");
    try expectPhase4MakefileMarker(
        "$(ZIG) build test --build-file zigux/tests/phase4_build.zig",
    );
    try expectPhase4MakefileMarker("phase4-runtime-atomic64-diff:");
    try expectPhase4MakefileMarker(
        "$(ZIG) build phase4-runtime-atomic64-diff --build-file zigux/tests/phase4_build.zig",
    );
}

test "atomic64 diff wrapper keeps standalone phase4 validator workflow evidence explicit" {
    try expectPhase4WorkflowMarker("Validate Phase 4 diff gates");
    try expectPhase4WorkflowMarker("Self-test Phase 4 validator");
    try expectPhase4WorkflowMarker("Run Phase 4 diff tests");
    try expectPhase4WorkflowMarker("run: make -C zigux phase4-validate");
    try expectPhase4WorkflowMarker("run: python3 scripts/zigux/validate-phase4.py --self-test");
    try expectPhase4WorkflowMarker("run: make -C zigux phase4-test");
    try expectSingleOccurrence(phase4_workflow_source, "run: make -C zigux phase4-validate");
    try expectSingleOccurrence(
        phase4_workflow_source,
        "run: python3 scripts/zigux/validate-phase4.py --self-test",
    );
    try expectSingleOccurrence(phase4_workflow_source, "run: make -C zigux phase4-test");
    try expectSingleOccurrence(
        phase4_makefile_source,
        "scripts/zigux/validate-phase4.py --self-test",
    );
    try expectValidatorMarker("print('PHASE4_VALIDATION=pass')");
    try expectValidatorMarker("print(f'PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}')");
    try expectValidatorMarker("print(f'PHASE4_REQUIRED_MARKER_COUNT={required_marker_count()}')");
    try expectGateEvidenceMarker("`PHASE4_VALIDATOR_SELF_TEST=pass`");
    try expectGateEvidenceMarker("`PHASE4_VALIDATION=pass`");
    try expectGateEvidenceMarker("`PHASE4_REQUIRED_FILE_COUNT=27`");
    try expectGateEvidenceMarker("`PHASE4_REQUIRED_MARKER_COUNT=55`");
}

test "atomic64 diff wrapper keeps the dedicated phase4 gate-evidence checker explicit" {
    try expectPhase4MakefileMarker("scripts/zigux/check-phase4-gate-evidence.py --self-test");
    try expectPhase4MakefileMarker("scripts/zigux/check-phase4-gate-evidence.py");
    try expectGateEvidenceCheckerMarker("PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA");
    try expectGateEvidenceCheckerMarker("REQUIRED_RUNTIME_ATOMIC64_REVERSIBLE_DELIVERY_MARKERS");
    try expectGateEvidenceCheckerMarker("make -C zigux phase4-validate");
    try expectGateEvidenceCheckerMarker("make -C zigux phase4-test");
    try expectGateEvidenceCheckerMarker("PHASE4_GATE_EVIDENCE_TARGET_COUNT");
    try expectGateEvidenceMarker("`PHASE4_GATE_EVIDENCE_CHECKER_BLOB_SHA=");
    try expectGateEvidenceMarker("`PHASE4_GATE_EVIDENCE_SELF_TEST=pass`");
    try expectGateEvidenceMarker("`PHASE4_GATE_EVIDENCE_CHECK=pass`");
    try expectGateEvidenceMarker("`PHASE4_GATE_EVIDENCE_TARGET_COUNT=17`");
    try expectGateEvidenceMarker("the dedicated `scripts/zigux/check-phase4-gate-evidence.py` checker");
    try expectGateEvidenceMarker("3ba64cd4e41a4de1c8fd8dbaecb23702ad9701a3");
}

test "atomic64 diff wrapper keeps phase4 validator aligned with wrapper and runtime split" {
    try expectValidatorMarker("'atomic64_diff.zig': {");
    try expectValidatorMarker("'zigux/tests/atomic64_diff.zig'");
    try expectValidatorMarker("'zigux/tests/runtime_atomic64_diff.zig'");
    try expectValidatorMarker("'phase4_validator_atomic64_diff_present': True");
    try expectValidatorMarker("'phase4_validator_runtime_atomic64_diff_present': True");
    try expectValidatorMarker("roadmap_atomic64_wrapper_targets_runtime_diff");
    try expectValidatorMarker("threshold_pending_until_runtime_atomic64_scope_widens");
    try expectValidatorMarker("removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint");
    try expectValidatorMarker("`runtime_atomic64_diff.zig` remains the single replay body");
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
    try expectRuntimeMarker("const blocked_add_unless = try module.addUnlessCounter(3, 0);");
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
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.addCounter(1)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.subCounter(1)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.swapCounter(7)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.compareSwapCounter(");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.orCounter(1)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.andCounter(1)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.xorCounter(1)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.andNotCounter(1)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.addUnlessCounter(");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.exit()");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.init(17)");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.incNotZeroCounter()");
    try expectRuntimeMarker("error.InvalidLifecycleTransition, module.decIfPositiveCounter()");
}

test "atomic64 diff wrapper pins bounded runtime case-group counts" {
    try expectRuntimeCaseGroupCardinality(
        "const add_cases = [_]AddCase{",
        "for (add_cases) |case| {",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const sub_cases = [_]SubCase{",
        "for (sub_cases) |case| {",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const or_cases = [_]BitwiseCase{",
        "for (or_cases) |case| {",
        1,
    );
    try expectRuntimeCaseGroupCardinality(
        "const and_cases = [_]BitwiseCase{",
        "for (and_cases) |case| {",
        1,
    );
    try expectRuntimeCaseGroupCardinality(
        "const xor_cases = [_]BitwiseCase{",
        "for (xor_cases) |case| {",
        1,
    );
    try expectRuntimeCaseGroupCardinality(
        "const andnot_cases = [_]BitwiseCase{",
        "for (andnot_cases) |case| {",
        1,
    );
    try expectRuntimeCaseGroupCardinality(
        "const exchange_cases = [_]DiffCase{",
        "for (exchange_cases) |case| {",
        3,
    );
    try expectRuntimeCaseGroupCardinality(
        "const compare_swap_cases = [_]CompareSwapCase{",
        "for (compare_swap_cases) |case| {",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const add_unless_cases = [_]AddUnlessCase{",
        "for (add_unless_cases) |case| {",
        2,
    );
    try expectRuntimeCaseGroupCardinality(
        "const inc_not_zero_cases = [_]IncNotZeroCase{",
        "for (inc_not_zero_cases) |case| {",
        4,
    );
    try expectRuntimeCaseGroupCardinality(
        "const dec_if_positive_cases = [_]DecIfPositiveCase{",
        "for (dec_if_positive_cases) |case| {",
        3,
    );
}

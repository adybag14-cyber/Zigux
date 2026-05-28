const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";

const required_genksyms_evidence = [_][]const u8{
    "PHASE2_STATUS=parked",
    "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest",
    "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "zig test scripts/zigux/genksyms.zig",
    "make -C zigux phase2-genksyms",
};

const expected_process_outputs = [_][]const u8{
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
};

const required_shared_tooling_evidence = [_][]const u8{
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
};

const expected_make_routes = [_][]const u8{
    "make -C zigux phase2-toolchain",
    "make -C zigux phase2-tools",
    "make -C zigux phase2-kconfig",
    "make -C zigux phase2-cross",
    "make -C zigux phase2-genksyms",
    "make -C zigux phase2-fixdep",
    "make -C zigux phase2-validate",
    "make -C zigux phase2",
};

fn readClosureNote(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        closure_note_path,
        allocator,
        .limited(24 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase2 closure keeps current genksyms evidence explicit" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Current Genksyms Evidence");
    for (required_genksyms_evidence) |needle| {
        try expectContains(closure_note, needle);
    }
}

test "phase2 closure names the full current genksyms process-output packet" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    for (expected_process_outputs) |needle| {
        try expectContains(closure_note, needle);
    }
}

test "phase2 closure preserves shared replay routes beside genksyms" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "## Current Shared Repo-Tooling Evidence");
    try expectContains(closure_note, "## Shared Replay Routes");
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");
    for (required_shared_tooling_evidence) |needle| {
        try expectContains(closure_note, needle);
    }
    for (expected_make_routes) |needle| {
        try expectContains(closure_note, needle);
    }
}

test "phase2 closure keeps the next genksyms step CRC-side and out of the shared note" {
    const closure_note = try readClosureNote(std.testing.allocator);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, "Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.");
    try expectContains(closure_note, "If the `genksyms` lane resumes substantive implementation instead of closure upkeep");
    try expectContains(closure_note, "still-missing CRC-side evidence recorded in the survey");
    try expectContains(closure_note, "rather than widening this shared note again");
}

const std = @import("std");

const closure_note_path = "Documentation/zigux/phase2-closure.md";
const closure_validator_path = "scripts/zigux/validate-phase2-closure.py";
const tool_manifest_path = "zigux/tests/fixtures/phase2_tool_manifest.json";

const process_output_fixtures = [_][]const u8{
    "abbreviated_version_expected.json",
    "ambiguous_long_option_expected.json",
    "invalid_option_expected.json",
    "missing_long_dump_types_argument_expected.json",
    "missing_long_reference_argument_expected.json",
    "missing_reference_argument_expected.json",
    "too_many_reference_files_expected.json",
    "unsupported_long_option_expected.json",
    "unexpected_long_help_argument_expected.json",
    "abbreviated_unexpected_long_help_argument_expected.json",
};

const expected_closure_line = "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json";

fn readRepoFile(io: std.Io, path: []const u8, max_bytes: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn fixturePath(name: []const u8) ![]u8 {
    return std.fmt.allocPrint(
        std.testing.allocator,
        "zigux/tests/fixtures/genksyms_bridge/{s}",
        .{name},
    );
}

test "lane24 phase2 closure note keeps the process-output fixture matrix exact" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const closure_note = try readRepoFile(io_instance.io(), closure_note_path, 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(closure_note, expected_closure_line);
    try expectContains(
        closure_note,
        "`zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json` is now part of the directly named process-output fixture set",
    );

    try expectAbsent(closure_note, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`");
}

test "lane24 phase2 closure validator self-test includes the restored fixture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const validator = try readRepoFile(io_instance.io(), closure_validator_path, 128 * 1024);
    defer std.testing.allocator.free(validator);

    try expectContains(validator, "process_output_packet = [");
    for (process_output_fixtures) |fixture| {
        try expectContains(validator, fixture);
    }
    try expectContains(validator, "expected_process_output_line = (");
    try expectContains(validator, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
}

test "lane24 phase2 tool manifest fixture roster carries the closure matrix" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest = try readRepoFile(io_instance.io(), tool_manifest_path, 256 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"fixture_roster\": [");
    for (process_output_fixtures) |fixture| {
        const path = try fixturePath(fixture);
        defer std.testing.allocator.free(path);
        try expectContains(manifest, path);
    }
}

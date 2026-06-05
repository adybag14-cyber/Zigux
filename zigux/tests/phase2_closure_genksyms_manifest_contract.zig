const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

const bridge_expected_packet_line =
    "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=" ++
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/inline_short_option_arguments_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json";

const process_output_packet_line =
    "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=" ++
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json," ++
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json";

test "phase 2 closure note preserves manifest-backed genksyms bridge roster" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    const manifest = try readRepoFile("zigux/tests/fixtures/genksyms_bridge/manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure_note, "eleven committed replay cases");
    try expectContains(closure_note, bridge_expected_packet_line);
    try expectContains(manifest, "\"case_count\": 11");
    try expectContains(manifest, "\"bridge_expected_packet\": [");
    try expectContains(manifest, "\"dash_prefixed_long_option_arguments_as_data_expected.json\"");
    try expectContains(manifest, "\"dash_prefixed_short_option_arguments_as_data_expected.json\"");
}

test "phase 2 closure note follows genksyms process-output manifest order" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    const manifest = try readRepoFile("zigux/tests/fixtures/genksyms_bridge/manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(closure_note, process_output_packet_line);
    try expectContains(manifest, "\"process_output_packet\": [");
    try expectBefore(
        manifest,
        "\"unexpected_long_help_argument_expected.json\"",
        "\"abbreviated_unexpected_long_help_argument_expected.json\"",
    );
    try expectBefore(
        closure_note,
        "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
        "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
    );
}

test "phase 2 closure note keeps genksyms proofs closed out of kconfig gap ownership" {
    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure_note);

    const manifest = try readRepoFile("zigux/tests/fixtures/genksyms_bridge/manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"status\": \"closed\"");
    try expectContains(manifest, "\"standalone_proof_packet\": [");
    try expectContains(manifest, "\"scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig\"");
    try expectContains(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md");
    try expectAbsent(closure_note, "PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectAbsent(closure_note, "genksyms_bridge/help_expected.json,zigux/tests/fixtures/genksyms_bridge/minimal_expected.json");
}

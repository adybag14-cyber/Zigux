const std = @import("std");
const testing = std.testing;

const closure_genksyms_bridge_packet =
    \\PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=zigux/tests/fixtures/genksyms_bridge/minimal_expected.json,zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json,zigux/tests/fixtures/genksyms_bridge/inline_short_option_arguments_expected.json,zigux/tests/fixtures/genksyms_bridge/long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json,zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json,zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json
;

const closure_genksyms_process_output_packet =
    \\PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json
;

const genksyms_manifest_packet =
    \\"case_count": 11
    \\"minimal"
    \\"debug_reference_types"
    \\"inline_short_option_arguments"
    \\"long_options"
    \\"abbreviated_long_options"
    \\"quiet_overrides_warning"
    \\"explicit_option_terminator"
    \\"positional_passthrough"
    \\"lone_dash_passthrough"
    \\"dash_prefixed_long_option_arguments_as_data"
    \\"dash_prefixed_short_option_arguments_as_data"
    \\"scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"
    \\"scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"
    \\"scripts/zigux/genksyms_inline_short_option_argument_test.zig"
;

const genksyms_cases_packet =
    \\"name": "minimal"
    \\"expected_file": "minimal_expected.json"
    \\"name": "debug_reference_types"
    \\"expected_file": "debug_reference_types_expected.json"
    \\"name": "inline_short_option_arguments"
    \\"expected_file": "inline_short_option_arguments_expected.json"
    \\"name": "long_options"
    \\"expected_file": "long_options_expected.json"
    \\"name": "abbreviated_long_options"
    \\"expected_file": "abbreviated_long_options_expected.json"
    \\"name": "quiet_overrides_warning"
    \\"expected_file": "quiet_overrides_warning_expected.json"
    \\"name": "explicit_option_terminator"
    \\"expected_file": "explicit_option_terminator_expected.json"
    \\"name": "positional_passthrough"
    \\"expected_file": "positional_passthrough_expected.json"
    \\"name": "lone_dash_passthrough"
    \\"expected_file": "lone_dash_passthrough_expected.json"
    \\"name": "dash_prefixed_long_option_arguments_as_data"
    \\"expected_file": "dash_prefixed_long_option_arguments_as_data_expected.json"
    \\"name": "dash_prefixed_short_option_arguments_as_data"
    \\"expected_file": "dash_prefixed_short_option_arguments_as_data_expected.json"
;

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectInOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.MissingExpectedMarker;
        cursor += found + needle.len;
    }
}

test "phase2 closure note keeps genksyms bridge expected packet explicit" {
    const expected_bridge_packet = [_][]const u8{
        "minimal_expected.json",
        "debug_reference_types_expected.json",
        "inline_short_option_arguments_expected.json",
        "long_options_expected.json",
        "abbreviated_long_options_expected.json",
        "quiet_overrides_warning_expected.json",
        "explicit_option_terminator_expected.json",
        "positional_passthrough_expected.json",
        "lone_dash_passthrough_expected.json",
        "dash_prefixed_long_option_arguments_as_data_expected.json",
        "dash_prefixed_short_option_arguments_as_data_expected.json",
    };

    try expectContains(closure_genksyms_bridge_packet, "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=");
    for (&expected_bridge_packet) |fixture| {
        try expectContains(closure_genksyms_bridge_packet, fixture);
    }
    try testing.expectEqual(@as(usize, 11), expected_bridge_packet.len);
    try expectInOrder(closure_genksyms_bridge_packet, expected_bridge_packet[0..]);
}

test "phase2 closure note keeps genksyms process output packet explicit" {
    const expected_process_output_packet = [_][]const u8{
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

    try expectContains(closure_genksyms_process_output_packet, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    for (&expected_process_output_packet) |fixture| {
        try expectContains(closure_genksyms_process_output_packet, fixture);
    }
    try testing.expectEqual(@as(usize, 10), expected_process_output_packet.len);
    try expectInOrder(closure_genksyms_process_output_packet, expected_process_output_packet[0..]);
}

test "genksyms manifest and cases keep closure fixture roster aligned" {
    const case_names = [_][]const u8{
        "minimal",
        "debug_reference_types",
        "inline_short_option_arguments",
        "long_options",
        "abbreviated_long_options",
        "quiet_overrides_warning",
        "explicit_option_terminator",
        "positional_passthrough",
        "lone_dash_passthrough",
        "dash_prefixed_long_option_arguments_as_data",
        "dash_prefixed_short_option_arguments_as_data",
    };
    const standalone_proofs = [_][]const u8{
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
        "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
        "scripts/zigux/genksyms_inline_short_option_argument_test.zig",
    };

    try expectContains(genksyms_manifest_packet, "\"case_count\": 11");
    for (&case_names) |case_name| {
        try expectContains(genksyms_manifest_packet, case_name);
        try expectContains(genksyms_cases_packet, case_name);
    }
    for (&standalone_proofs) |proof| {
        try expectContains(genksyms_manifest_packet, proof);
    }

    try testing.expectEqual(@as(usize, 11), case_names.len);
    try testing.expectEqual(@as(usize, 3), standalone_proofs.len);
}

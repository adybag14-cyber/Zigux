const std = @import("std");
const phase2_markers = @import("phase2_markers");

const phase2_closure = phase2_markers.phase2_closure;
const genksyms_manifest = phase2_markers.genksyms_manifest;
const scripts_readme = phase2_markers.scripts_readme;

const process_output_packet_line =
    "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json";

const expected_process_outputs = [_][]const u8{
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

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

test "closure note pins the full genksyms process-output packet line" {
    try requireContains(phase2_closure, "## Current Genksyms Evidence");
    try requireContains(phase2_closure, process_output_packet_line);
    try requireContains(phase2_closure, "The bridge expected-output packet now explicitly records the eleven committed replay cases");
    try requireContains(phase2_closure, "including the dash-prefixed long and short option argument-as-data cases");

    for (expected_process_outputs) |fixture| {
        try requireContains(phase2_closure, fixture);
    }
}

test "manifest process-output packet stays aligned with closure note" {
    try requireContains(genksyms_manifest, "\"process_output_packet\"");
    try requireContains(genksyms_manifest, "\"case_count\": 11");

    for (expected_process_outputs) |fixture| {
        try requireContains(genksyms_manifest, fixture);
        try requireContains(phase2_closure, fixture);
    }

    try std.testing.expectEqual(@as(usize, expected_process_outputs.len), countOccurrences(process_output_packet_line, "zigux/tests/fixtures/genksyms_bridge/"));
}

test "scripts root keeps genksyms bridge reminder beside Phase 2 shared tooling" {
    try requireContains(scripts_readme, "Phase 2 flow - the current scripts-root bridge packet stays reviewable");
    try requireContains(scripts_readme, "scripts/zigux/check-genksyms-bridge.py");
    try requireContains(scripts_readme, "fixdep packet, and returned make wrappers");
    try requireContains(scripts_readme, "make -C zigux phase2-genksyms");
    try requireContains(scripts_readme, "scripts/zigux/check-phase2-kconfig-selftest-alignment.py");
    try requireContains(scripts_readme, "scripts/zigux/kconfig/conf_bridge.zig");
    try requireContains(scripts_readme, "scripts/zigux/kconfig/confdata_bridge.zig");
}

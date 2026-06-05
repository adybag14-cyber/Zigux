const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

const confdata_cases = [_][]const u8{
    "sample",
    "escaped_strings",
    "escaped_control_sequences",
    "trailing_escaped_backslash",
    "sample_crlf",
    "explicit_n_tristate",
    "final_trailing_carriage_return",
    "final_unterminated_unset_comment",
    "uppercase_tristate",
    "non_config_lines",
    "empty_config_symbol_names",
    "malformed_unset_comment_tokens",
    "last_state_transitions",
    "duplicate_assignments",
    "duplicate_malformed_quoted_assignment",
    "explicit_empty_assignments",
};

const confdata_anchor_markers = [_][]const u8{
    "confdata bridge emits explicit empty assignments distinctly in json output",
    "confdata bridge parses explicit output modes",
    "confdata bridge emits auto.conf output through the explicit mode surface",
    "confdata bridge emits autoconf header output through the explicit mode surface",
    "confdata bridge file reader accepts config inputs beyond one mebibyte",
    "confdata bridge releases appended entry ownership on index-allocation failure",
    "confdata bridge preserves duplicate unset ownership on allocation failure",
};

test "confdata survey pins the current case and helper-anchor counts" {
    const survey = try readRepoFile("Documentation/zigux/phase2-confdata-bridge-survey.md", 128 * 1024);
    defer std.testing.allocator.free(survey);

    try expectContains(survey, "# Phase 2 Confdata Bridge Survey");
    try expectContains(survey, "`scripts/zigux/kconfig/confdata_bridge.zig` bridge");
    try expectContains(survey, "alongside `36` helper-local tests covering the current bridge-local edge cases");
    try expectContains(survey, "`confdata_cases` packet with 16 fixture cases");
    try expectContains(survey, "records the same 16-case packet");
    try expectContains(survey, "explicit-empty-assignment, output-mode, large-input, and allocation-failure ownership proofs");
    try expectContains(survey, "JSON output for preserved duplicate state, explicit empty assignment JSON output, `auto.conf` output, `autoconf.h` output, explicit output-mode parsing, large config-file readback, appended-entry allocation-failure ownership, and duplicate-unset allocation-failure ownership");
    try expectContains(survey, "shared `16`-case external packet plus `36` helper-local anchors");
    try expectContains(survey, "The stale `15`-case / `27`-anchor undercount is no longer a live repo gap");
    try expectContains(survey, "current `16-case` confdata packet and `36`-anchor helper-local bridge packet");

    try expectNotContains(survey, "15 fixture cases");
    try expectNotContains(survey, "records the same 15-case packet");
    try expectNotContains(survey, "27` helper-local");

    for (confdata_cases) |case_name| {
        try expectContains(survey, case_name);
    }
}

test "confdata manifest and bridge source expose the same expanded packet" {
    const manifest = try readRepoFile("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json", 128 * 1024);
    defer std.testing.allocator.free(manifest);

    const bridge = try readRepoFile("scripts/zigux/kconfig/confdata_bridge.zig", 256 * 1024);
    defer std.testing.allocator.free(bridge);

    try expectContains(manifest, "\"tool\": \"scripts/zigux/kconfig/confdata_bridge.zig\"");
    try expectContains(manifest, "\"status\": \"closed\"");
    try expectContains(manifest, "\"case_count\": 16");
    try expectContains(manifest, "\"explicit_empty_assignments\"");

    for (confdata_cases) |case_name| {
        try expectContains(manifest, case_name);
    }

    for (confdata_anchor_markers) |anchor| {
        try expectContains(manifest, anchor);
        try expectContains(bridge, anchor);
    }

    try expectContains(bridge, "runConfdataBridge");
    try expectContains(bridge, "OutputMode");
    try expectContains(bridge, "auto_conf");
    try expectContains(bridge, "autoconf_header");
}

test "phase 2 closure note stays aligned with the confdata survey counts" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "scripts/zigux/kconfig/confdata_bridge.zig");
    try expectContains(closure, "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json");
    try expectContains(closure, "16 committed fixture cases and 36 helper-local anchors");
    try expectContains(closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16");
    try expectContains(closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36");
    try expectContains(closure, "scripts/zigux/check-kconfig-bridge.py");
    try expectContains(closure, "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py");

    try expectNotContains(closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=15");
    try expectNotContains(closure, "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=27");
}

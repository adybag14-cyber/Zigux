const std = @import("std");

const manifest_text = @embedFile("phase13_notifier_list_manifest.json");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1 << 20));
}

test "phase13 notifier manifest records the checker-backed adjacent packet" {
    try requireContains(manifest_text, "\"lane_key\": \"P13-L18\"");
    try requireContains(manifest_text, "\"anchor\": \"drivers/tty/hvc/hvc_console.h\"");
    try requireContains(manifest_text, "\"current_notifier_packet_checker_present\": true");
    try requireContains(manifest_text, "\"current_phase13_notifier_list_manifest_present\": true");
    try requireContains(manifest_text, "\"current_phase13_notifier_list_reviewability_present\": true");
    try requireContains(manifest_text, "\"current_phase13_build_present\": false");
    try requireContains(manifest_text, "\"id\": \"phase13-notifier-focused-packet-checker\"");
    try requireContains(manifest_text, "\"id\": \"phase13-notifier-reviewability-gate\"");
    try requireContains(manifest_text, "\"id\": \"phase13-notifier-chain-helper-gap\"");
    try requireContains(manifest_text, "\"id\": \"phase13-build-route-gap\"");
}

test "phase13 notifier survey keeps the checker-backed adjacent packet explicit" {
    const survey = try readRepoFile(std.testing.allocator, "Documentation/zigux/phase13-notifier-list-survey.md");
    defer std.testing.allocator.free(survey);

    try requireContains(survey, "`scripts/zigux/check-phase13-notifier-packet.py`");
    try requireContains(survey, "`zigux/tests/phase13_notifier_list_manifest.json`");
    try requireContains(survey, "`zigux/tests/phase13_notifier_list_reviewability.zig`");
    try requireContains(survey, "`zigux/helpers/notifier_chain_view.zig`");
    try requireContains(survey, "`make -C zigux phase13-validate`");
    try requireContains(survey, "focused checker");
}

test "phase13 notifier checker stays explicit in the focused reviewability gate" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-notifier-packet.py");
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "PHASE13_NOTIFIER_PACKET=pass");
    try requireContains(checker, "phase13-notifier-focused-packet-checker");
    try requireContains(checker, "Documentation/zigux/phase13-notifier-list-survey.md");
    try requireContains(checker, "zigux/tests/phase13_notifier_list_manifest.json");
    try requireContains(checker, "drivers/tty/hvc/hvc_console.h");
}

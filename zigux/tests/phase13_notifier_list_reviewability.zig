const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const SurveySummary = struct {
    preexisting_phase13_build_present: bool,
    preexisting_notifier_binding_present: bool,
    preexisting_list_view_present: bool,
    preexisting_hlist_view_present: bool,
    preexisting_exported_list_abi_present: bool,
    preexisting_notifier_helper_present: bool,
    preexisting_exported_notifier_abi_present: bool,
    preexisting_phase13_notifier_reviewability_present: bool,
    preexisting_phase13_notifier_survey_note_present: bool,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchors: []const []const u8,
    roadmap_scope: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1 << 20),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase13 notifier/list survey records the landed adjacent notifier header surface" {
    var arena = std.heap.ArenaAllocator.init(std.testing.allocator);
    defer arena.deinit();
    const allocator = arena.allocator();

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase13_notifier_list_manifest.json");
    const notifier_binding_text = try readRepoFile(allocator, "zigux/bindings/notifier_abi.zig");
    const list_view_text = try readRepoFile(allocator, "zigux/helpers/list_view.zig");
    const hlist_view_text = try readRepoFile(allocator, "zigux/helpers/hlist_view.zig");
    const notifier_helper_text = try readRepoFile(allocator, "zigux/helpers/notifier_chain_view.zig");
    const exported_abi_text = try readRepoFile(allocator, "include/zigux/abi.h");
    const exported_notifier_abi_text = try readRepoFile(allocator, "include/zigux/notifier_abi.h");
    const phase13_build_text = try readRepoFile(allocator, "zigux/tests/phase13_build.zig");
    const survey_note = try readRepoFile(allocator, "Documentation/zigux/phase13-notifier-list-survey.md");

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P13-L18", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("23d15e44622d2cedd7691c88f78709db6bf1eb7e", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.anchors.len);
    try std.testing.expectEqualStrings("include/linux/list.h", manifest.anchors[0]);
    try std.testing.expectEqualStrings("include/linux/notifier.h", manifest.anchors[1]);
    try std.testing.expectEqualStrings("include/zigux/abi.h", manifest.anchors[2]);

    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_notifier_binding_present);
    try std.testing.expect(manifest.survey_summary.preexisting_list_view_present);
    try std.testing.expect(manifest.survey_summary.preexisting_hlist_view_present);
    try std.testing.expect(manifest.survey_summary.preexisting_exported_list_abi_present);
    try std.testing.expect(manifest.survey_summary.preexisting_notifier_helper_present);
    try std.testing.expect(manifest.survey_summary.preexisting_exported_notifier_abi_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_notifier_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_notifier_survey_note_present);

    try expectContains(notifier_binding_text, "pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING");
    try expectContains(notifier_binding_text, "pub const NotifierBlockRef");
    try expectContains(notifier_binding_text, "pub const RawNotifierHeadRef");
    try expectContains(notifier_binding_text, "pub const NotifierChainView");
    try expectContains(notifier_binding_text, "pub const NotifierChainSummary");
    try expectContains(list_view_text, "pub fn summarize");
    try expectContains(hlist_view_text, "pub fn summarize");
    try expectContains(notifier_helper_text, "pub fn viewFromHead");
    try expectContains(notifier_helper_text, "pub fn hasNonincreasingPriorityOrder");
    try expectContains(notifier_helper_text, "summarize keeps ordered terminated chains marked as nonincreasing priority");
    try expectContains(notifier_helper_text, "summarize clears the priority-order flag when priorities rise");
    try expectContains(exported_abi_text, "struct zigux_list_view");
    try expectContains(exported_abi_text, "struct zigux_hlist_view");
    try expectContains(exported_notifier_abi_text, "zigux_notifier");
    try expectContains(exported_notifier_abi_text, "ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING");
    try std.testing.expect(std.mem.indexOf(u8, phase13_build_text, "phase13_notifier") == null);
    try expectContains(survey_note, "lane key: `P13-L18`");
    try expectContains(survey_note, "surveyed commit: `23d15e44622d2cedd7691c88f78709db6bf1eb7e`");
    try expectContains(survey_note, "`include/zigux/notifier_abi.h` is now shipped as adjacent notifier interop evidence");
    try expectContains(survey_note, "`zigux/helpers/notifier_chain_view.zig` now provides the matching read-only notifier-chain summary helpers");
    try expectContains(survey_note, "shared Phase 13 build intentionally omits this packet");

    var landed_helper_gap = false;
    var landed_header_surface = false;
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, "phase13-notifier-helper-surface")) {
            landed_helper_gap = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("helper", gap.kind);
            try std.testing.expectEqualStrings("zigux/helpers/notifier_chain_view.zig", gap.zigux_destination);
        } else if (std.mem.eql(u8, gap.id, "phase13-exported-notifier-c-header-surface")) {
            landed_header_surface = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("header", gap.kind);
            try std.testing.expectEqualStrings("include/zigux/notifier_abi.h", gap.zigux_destination);
        }
    }

    try std.testing.expect(landed_helper_gap);
    try std.testing.expect(landed_header_surface);
}

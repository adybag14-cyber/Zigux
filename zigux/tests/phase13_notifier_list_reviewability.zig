const std = @import("std");

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

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
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

fn readRepoFile(
    io: std.Io,
    allocator: std.mem.Allocator,
    path: []const u8,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(64 * 1024));
}

fn expectMissing(path: []const u8) !void {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    _ = std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(1024)) catch |err| {
        try std.testing.expect(err == error.FileNotFound);
        return;
    };
    return error.TestUnexpectedResult;
}

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next");
}

test "phase13 notifier/list survey keeps the binding-only notifier foothold and explicit gaps aligned" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/tests/phase13_notifier_list_manifest.json");
    defer std.testing.allocator.free(manifest_json);
    const notifier_abi_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/bindings/notifier_abi.zig");
    defer std.testing.allocator.free(notifier_abi_text);
    const list_view_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/helpers/list_view.zig");
    defer std.testing.allocator.free(list_view_text);
    const hlist_view_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/helpers/hlist_view.zig");
    defer std.testing.allocator.free(hlist_view_text);
    const abi_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "include/zigux/abi.h");
    defer std.testing.allocator.free(abi_header_text);
    const phase13_build_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/tests/phase13_build.zig");
    defer std.testing.allocator.free(phase13_build_text);
    const survey_note = try readRepoFile(io_instance.io(), std.testing.allocator, "Documentation/zigux/phase13-notifier-list-survey.md");
    defer std.testing.allocator.free(survey_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P13-L17", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("master-reviewability", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.anchors.len);
    try std.testing.expectEqualStrings("include/linux/list.h", manifest.anchors[0]);
    try std.testing.expectEqualStrings("include/linux/notifier.h", manifest.anchors[1]);
    try std.testing.expectEqualStrings("include/zigux/abi.h", manifest.anchors[2]);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_scope, "roadmap-adjacent") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_scope, "libfs, devres, or Landlock") != null);

    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_notifier_binding_present);
    try std.testing.expect(manifest.survey_summary.preexisting_list_view_present);
    try std.testing.expect(manifest.survey_summary.preexisting_hlist_view_present);
    try std.testing.expect(manifest.survey_summary.preexisting_exported_list_abi_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_notifier_helper_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_exported_notifier_abi_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_notifier_reviewability_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase13_notifier_survey_note_present);
    try std.testing.expectEqual(@as(usize, 9), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING: u32 = 16;") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const NotifierBlockRef = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const RawNotifierHeadRef = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const NotifierChainView = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const NotifierChainSummary = extern struct") != null);

    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn viewFromHead") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn isEmpty") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn length") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn summarize") != null);

    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn viewFromHead") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn isEmpty") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn length") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn summarize") != null);

    try std.testing.expect(std.mem.indexOf(u8, abi_header_text, "struct zigux_list_view") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_header_text, "struct zigux_list_summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_header_text, "struct zigux_hlist_view") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_header_text, "struct zigux_hlist_summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_header_text, "struct zigux_notifier_chain_view") == null);

    try std.testing.expect(std.mem.indexOf(u8, phase13_build_text, "phase13_notifier_list") == null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lane key: `P13-L17`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "roadmap-adjacent reviewability evidence only") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Lane `P13-L17` keeps this packet reviewable while leaving the unpublished helper-side follow-up to `P13-L18`.") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no read-only notifier chain helper on current `master`; `zigux/helpers/notifier_chain_view.zig` remains the `P13-L18` helper-local follow-up if this lane reopens") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "no dedicated exported notifier C header yet; `include/zigux/notifier_abi.h` stays with the same `P13-L18` interop follow-up rather than becoming a hidden current capability") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared Phase 13 build intentionally omits") != null);

    try expectMissing("zigux/helpers/notifier_chain_view.zig");
    try expectMissing("include/zigux/notifier_abi.h");

    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_build_adjacency = false;
    var saw_binding_surface = false;
    var saw_list_helper = false;
    var saw_hlist_helper = false;
    var saw_exported_list_abi = false;
    var saw_reviewability_gate = false;
    var saw_survey_note_gap = false;
    var saw_notifier_helper_gap = false;
    var saw_notifier_header_gap = false;

    for (manifest.gaps) |gap| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.zigux_destination.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "phase13-build-adjacent-release-surface")) {
            saw_build_adjacency = true;
            try std.testing.expectEqualStrings("zigux/tests/phase13_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-notifier-binding-surface")) {
            saw_binding_surface = true;
            try std.testing.expectEqualStrings("zigux/bindings/notifier_abi.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-list-view-helper-surface")) {
            saw_list_helper = true;
            try std.testing.expectEqualStrings("zigux/helpers/list_view.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-hlist-view-helper-surface")) {
            saw_hlist_helper = true;
            try std.testing.expectEqualStrings("zigux/helpers/hlist_view.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-exported-list-abi-surface")) {
            saw_exported_list_abi = true;
            try std.testing.expectEqualStrings("include/zigux/abi.h", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-notifier-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("zigux/tests/phase13_notifier_list_reviewability.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-notifier-survey-note")) {
            saw_survey_note_gap = true;
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-notifier-list-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-notifier-helper-gap")) {
            saw_notifier_helper_gap = true;
            try std.testing.expectEqualStrings("zigux/helpers/notifier_chain_view.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`P13-L18`") != null);
        }
        if (std.mem.eql(u8, gap.id, "phase13-exported-notifier-c-header-gap")) {
            saw_notifier_header_gap = true;
            try std.testing.expectEqualStrings("include/zigux/notifier_abi.h", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "`P13-L18`") != null);
        }
    }

    try std.testing.expectEqual(@as(usize, 7), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 2), ready_next_count);
    try std.testing.expect(saw_build_adjacency);
    try std.testing.expect(saw_binding_surface);
    try std.testing.expect(saw_list_helper);
    try std.testing.expect(saw_hlist_helper);
    try std.testing.expect(saw_exported_list_abi);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_survey_note_gap);
    try std.testing.expect(saw_notifier_helper_gap);
    try std.testing.expect(saw_notifier_header_gap);
}

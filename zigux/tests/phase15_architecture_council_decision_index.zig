const std = @import("std");

const FileCheck = struct {
    path: []const u8,
    markers: []const []const u8,
};

const current_inventory_markers = [_][]const u8{
    "approved status-bucket changes recorded on current `master`: none",
    "stay-in-C closeout decision records recorded on current `master`: none",
    "no freeze-map anchor has an Architecture Council approval for a status change on current `master`",
    "zero-decision inventory",
};

const future_record_fields = [_][]const u8{
    "decision record ID:",
    "exact Linux anchor path:",
    "review outcome:",
    "evidence archive path:",
    "surveyed commit marker:",
    "next bounded step:",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAll(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try expectContains(haystack, marker);
    }
}

test "decision index keeps current zero-decision inventory explicit" {
    const decision_index = try readRepoFile("Documentation/zigux/phase15-architecture-council-decision-index.md", 64 * 1024);
    defer std.testing.allocator.free(decision_index);

    try expectContainsAll(decision_index, &current_inventory_markers);
    try expectContainsAll(decision_index, &future_record_fields);
    try expectContains(decision_index, "if no reviewable Architecture Council decision record exists yet");
    try expectContains(decision_index, "keep this note at an explicit zero-decision inventory");
}

test "decision index routes future records through owner governance notes" {
    const owner_surfaces = [_]FileCheck{
        .{
            .path = "Documentation/zigux/phase15-architecture-council-decision-index.md",
            .markers = &.{
                "Documentation/zigux/phase15-architecture-council-review-process.md",
                "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
                "Documentation/zigux/phase15-freeze-map-governance.md",
                "Documentation/zigux/phase15-parity-scorecard.md",
                "Documentation/zigux/phase15-indefinite-c-policy.md",
                "scripts/zigux/check-phase15-architecture-council-decision-index.py",
            },
        },
        .{
            .path = "Documentation/zigux/phase15-architecture-council-review-process.md",
            .markers = &.{
                "Documentation/zigux/phase15-architecture-council-decision-index.md",
                "Architecture Council approval for a status change",
                "If one of those fields cannot be stated honestly, the request stays blocked",
                "no freeze-map anchor has an Architecture Council approval for a status change",
            },
        },
        .{
            .path = "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            .markers = &.{
                "REVIEW_STATUS=<blocked_review|stay_in_c|approved_status_bucket_change>",
                "exact-head provenance exception note:",
                "If any required field above cannot be stated honestly",
                "A reopen request must cite the exact reopen trigger being exercised",
            },
        },
    };

    for (owner_surfaces) |surface| {
        const text = try readRepoFile(surface.path, 96 * 1024);
        defer std.testing.allocator.free(text);
        try expectContainsAll(text, surface.markers);
    }
}

test "freeze map keeps decision records as evidence gates, not approvals by omission" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(freeze_map, "changes to either list require an explicit Architecture Council decision with written rationale");
    try expectContains(freeze_map, "decision record ID");
    try expectContains(freeze_map, "evidence archive path");
    try expectContains(freeze_map, "required approver set");
    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
}

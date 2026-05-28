const std = @import("std");

const Surface = struct {
    label: []const u8,
    path: []const u8,
    required_markers: []const []const u8,
    forbidden_markers: []const []const u8 = &.{},
};

const review_closeout_markers = [_][]const u8{
    "if a freeze-map anchor is entering Architecture Council status review or recording a stay-in-C closeout",
    "shared entry-review and closeout prompts",
    "required approver set",
    "rollback owner",
    "evidence archive path",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "retained blocker posture",
    "trigger-specific evidence refresh",
    "return-to-blocked wording",
};

const freeze_closeout_markers = [_][]const u8{
    "closing a freeze-in-C review without a status change",
    "required approver set",
    "governance lane sequencing link or explicit scope note",
    "automatic return-to-blocked trigger",
    "retired_from_active_discussion",
    "evidence archive path",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
};

const docs_root_phase15_markers = [_][]const u8{
    "Phase 15 notes",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "keep the Phase 15 reminder bounded below any Architecture Council approval claim",
    "any freeze-map status change",
    "shared reminder surfaces explicit",
};

const approval_drift_markers = [_][]const u8{
    "Architecture Council approved",
    "Architecture Council approval landed",
    "freeze-map status change approved",
    "deep-core delivery approved",
};

const surfaces = [_]Surface{
    .{
        .label = "review checklist freeze closeout prompt",
        .path = "Documentation/zigux/review-checklist.md",
        .required_markers = &review_closeout_markers,
    },
    .{
        .label = "freeze map closeout policy",
        .path = "Documentation/zigux/freeze-map.md",
        .required_markers = &freeze_closeout_markers,
        .forbidden_markers = &approval_drift_markers,
    },
    .{
        .label = "docs root Phase 15 reminder boundary",
        .path = "Documentation/zigux/README.md",
        .required_markers = &docs_root_phase15_markers,
        .forbidden_markers = &approval_drift_markers,
    },
};

fn readSurface(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024));
}

fn expectMarkers(content: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, content, marker) != null);
    }
}

fn rejectMarkers(content: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, content, marker) == null);
    }
}

test "Phase 15 review checklist and freeze map keep closeout prompts bounded" {
    const allocator = std.testing.allocator;

    inline for (surfaces) |surface| {
        const content = try readSurface(allocator, surface.path);
        defer allocator.free(content);

        try std.testing.expect(surface.label.len > 0);
        try expectMarkers(content, surface.required_markers);
        try rejectMarkers(content, surface.forbidden_markers);
    }
}

const std = @import("std");

const DocSurface = struct {
    path: []const u8,
    required_terms: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsAll(haystack: []const u8, terms: []const []const u8) !void {
    for (terms) |term| {
        try expectContains(haystack, term);
    }
}

fn expectSurface(surface: DocSurface) !void {
    const text = try readRepoFile(surface.path, 96 * 1024);
    defer std.testing.allocator.free(text);
    try expectContainsAll(text, surface.required_terms);
}

test "freeze-map shorthand routes to the explicit Architecture Council field" {
    const freeze_map = try readRepoFile("Documentation/zigux/freeze-map.md", 96 * 1024);
    defer std.testing.allocator.free(freeze_map);

    try expectContains(freeze_map, "indefinite-C policy link or explicit non-applicability note");
    try expectContains(
        freeze_map,
        "the status-change field shorthand `indefinite-C policy link or non-applicability note` means the same explicit non-applicability note requirement recorded in the Architecture Council packet",
    );
    try expectContains(freeze_map, "freeze-map status-change requests must route through");
    try expectContains(freeze_map, "Documentation/zigux/phase15-architecture-council-review-process.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-indefinite-c-policy.md");
    try expectContains(freeze_map, "Documentation/zigux/phase15-architecture-council-decision-record-template.md");
    try expectContains(freeze_map, "there is no silent exception path around the stay-in-C policy");
}

test "Architecture Council packet keeps non-applicability explicit and blocked by default" {
    const surfaces = [_]DocSurface{
        .{
            .path = "Documentation/zigux/phase15-architecture-council-review-process.md",
            .required_terms = &.{
                "indefinite-C policy link or explicit non-applicability note",
                "If one of those fields cannot be stated honestly, the request stays blocked",
                "This note does not define an exception path outside those reviewable outcomes.",
                "There is no silent exception path around the indefinite-C policy.",
                "On current `master`, no freeze-map anchor has an Architecture Council approval for a status change.",
            },
        },
        .{
            .path = "Documentation/zigux/phase15-architecture-council-decision-record-template.md",
            .required_terms = &.{
                "indefinite-C policy link or explicit non-applicability note:",
                "If any required field above cannot be stated honestly, keep the request blocked",
                "exact-head provenance exception note:",
                "Any exact-head provenance exception must keep the lane owner, rollback owner, and required approver set explicit",
            },
        },
    };

    for (surfaces) |surface| {
        try expectSurface(surface);
    }
}

test "indefinite-C policy keeps exception and reopen ownership tied to explicit evidence" {
    const policy = try readRepoFile("Documentation/zigux/phase15-indefinite-c-policy.md", 96 * 1024);
    defer std.testing.allocator.free(policy);

    try expectContains(policy, "Required recorded fields");
    try expectContains(policy, "Those ownership, validation, and rollback fields stay coupled to `Documentation/zigux/phase15-architecture-council-decision-record-template.md`");
    try expectContains(policy, "governance lane sequencing link or explicit scope note");
    try expectContains(policy, "study-only anchor accounting link or explicit freeze-map-anchor confirmation");
    try expectContains(policy, "There is no silent exception path around the indefinite-C policy.");
    try expectContains(policy, "Any reopen request or exact-head provenance exception note must keep the lane owner, rollback owner, and required approver set explicit");
    try expectContains(policy, "the named reopen trigger now being exercised");
    try expectContains(policy, "the trigger-specific evidence refresh that reopens the packet");
}

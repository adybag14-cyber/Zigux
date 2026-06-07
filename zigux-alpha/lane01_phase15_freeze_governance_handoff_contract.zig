const std = @import("std");

const roadmap_path = "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md";
const alpha_readme_path = "zigux-alpha/README.md";
const freeze_map_path = "Documentation/zigux/freeze-map.md";
const governance_path = "Documentation/zigux/phase15-freeze-map-governance.md";

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(384 * 1024));
}

fn mustContain(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn mustPrecede(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

const freeze_in_c_anchors = [_][]const u8{
    "`kernel/sched/core.c`",
    "`mm/page_alloc.c`",
    "`kernel/rcu/tree.c`",
    "`net/core/skbuff.c`",
};

test "roadmap phase15 stays a governance packet, not an implementation promise" {
    const allocator = std.testing.allocator;
    const roadmap = try readFile(allocator, roadmap_path);
    defer allocator.free(roadmap);

    try mustContain(roadmap, "## Phase 15: Full-Parity Blockers and Long-Term Governance");
    try mustContain(roadmap, "Primary product goal:\n- govern the final mixed-language steady state honestly");
    try mustContain(roadmap, "Required Zigux features:");
    try mustContain(roadmap, "- freeze map");
    try mustContain(roadmap, "- Architecture Council review process");
    try mustContain(roadmap, "- parity scorecard");
    try mustContain(roadmap, "- policy for code that remains in C indefinitely");
    try mustContain(roadmap, "This phase is about discipline, not bravado.");

    for (freeze_in_c_anchors) |anchor| {
        try mustContain(roadmap, anchor);
    }

    try mustPrecede(
        roadmap,
        "## Phase 14: Core-Adjacent Bounded Internals",
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
    );
    try mustPrecede(
        roadmap,
        "## Phase 15: Full-Parity Blockers and Long-Term Governance",
        "## Freeze Map for Near- and Mid-Term Planning",
    );
}

test "alpha README points Lane 01 readers from bootstrap planning to live Phase15 governance" {
    const allocator = std.testing.allocator;
    const readme = try readFile(allocator, alpha_readme_path);
    defer allocator.free(readme);

    try mustContain(readme, "Documentation/zigux/phase15-freeze-map-governance.md");
    try mustContain(readme, "Freeze Governance Companion");
    try mustContain(readme, "Live Product Docs");
    try mustContain(readme, "Freeze Map");
    try mustContain(readme, "the bounded early commit train");
    try mustContain(readme, "current repo tree");
    try mustContain(readme, "active lane notes");
}

test "live freeze map and governance packet preserve the same deep-core blocker posture" {
    const allocator = std.testing.allocator;
    const freeze_map = try readFile(allocator, freeze_map_path);
    defer allocator.free(freeze_map);
    const governance = try readFile(allocator, governance_path);
    defer allocator.free(governance);

    try mustContain(freeze_map, "## Freeze In C Initially");
    try mustContain(freeze_map, "## Study / Boundary Only");
    try mustContain(freeze_map, "## Stay-In-C Policy");
    try mustContain(freeze_map, "only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review");
    try mustContain(governance, "PHASE15_STATUS=governance_slice_landed");
    try mustContain(governance, "current lane posture: `maintenance_mode`");
    try mustContain(governance, "The roadmap's Phase 15 work is about governance, not another burst of deep-core implementation.");
    try mustContain(governance, "Next bounded step");

    for (freeze_in_c_anchors) |anchor| {
        try mustContain(freeze_map, anchor);
        try mustContain(governance, anchor);
    }
}

test "Phase15 handoff keeps status-change evidence blocked until Architecture Council review" {
    const allocator = std.testing.allocator;
    const governance = try readFile(allocator, governance_path);
    defer allocator.free(governance);

    const blocker_markers = [_][]const u8{
        "blocked_no_bounded_scheduler_seam",
        "blocked_no_bounded_allocator_seam",
        "blocked_phase14_followup_still_wider_than_allowed_rcu_seam",
        "blocked_packet_lifetime_boundary_still_too_wide",
    };

    for (blocker_markers) |marker| {
        try mustContain(governance, marker);
    }

    try mustContain(governance, "direct Zig bridge or port claims for a freeze-in-C anchor stay blocked");
    try mustContain(governance, "Architecture Council records why the status can change");
    try mustContain(governance, "Keep the Phase 15 governance lane in maintenance mode");
}

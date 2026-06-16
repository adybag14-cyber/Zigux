const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_LANDLOCK_RULESET_PACKET_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "helper",
    "security/landlock/ruleset.zig",
    "ownership",
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "survey",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "test",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "manifest",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
};

const REQUIRED_MARKERS = [_][]const u8{
    "security/landlock/ruleset.zig",
    "pub fn planRulesetCreation(",
    "pub fn planRuleTreeSearch(",
    "pub fn planInsertRuleBranch(",
    ".provides_ruleset_creation_planning = true",
    ".provides_rule_tree_search_planning = true",
    ".provides_rule_insertion_planning = true",
    "Documentation/zigux/phase13-landlock-ruleset-ownership.md",
    "# Phase 13 Landlock Ruleset Ownership",
    "security/landlock/ruleset.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "Documentation/zigux/phase13-landlock-ruleset-slice.md",
    "zigux/tests/phase13_build.zig",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "`Documentation/zigux/phase13-landlock-ruleset-ownership.md`",
    "`scripts/zigux/check_phase13_landlock_ruleset_packet.zig`",
    "landed `phase13-landlock-ruleset-ownership-note`",
    "landed `phase13-landlock-ruleset-packet-checker`",
    "blocked `phase13-build-gate`",
    "blocked `phase13-landlock-ruleset-slice-note`",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "\"phase13 landlock ruleset descriptor keeps the current bounded helper scope explicit\"",
    "\"phase13 landlock ruleset manifest records the current bounded security helper packet\"",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "\"lane_key\": \"P13-L10\"",
    "\"current_phase13_landlock_ruleset_slice_present\": false",
    "\"current_phase13_landlock_ruleset_ownership_present\": true",
    "\"id\": \"phase13-landlock-ruleset-ownership-note\"",
    "\"id\": \"phase13-landlock-ruleset-packet-checker\"",
    "\"status\": \"blocked_on_missing_review_surface\"",
    "\"status\": \"starter_landed\"",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "blocked `phase13-landlock-ruleset-ownership-note`",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "\"current_phase13_landlock_ruleset_slice_present\": true",
    "\"current_phase13_landlock_ruleset_ownership_present\": false",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}

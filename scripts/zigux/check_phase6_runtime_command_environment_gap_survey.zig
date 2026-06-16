const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE6_RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY=pass";
pub const self_test_pass_marker = "PHASE6_RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY_SELF_TEST=pass";

const EXPECTED_PACKET = [_][]const u8{
    "phase6-helper-evidence",
};

const EXPECTED_LANE_SCOPE = [_][]const u8{
    "shared helper-evidence rows and machine-readable manifest only",
};

const EXPECTED_SURVEYED_HEAD = [_][]const u8{
    "current-master-readback-2026-05-22",
};

const EXPECTED_SURVEY_COMPANION = [_][]const u8{
    "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md",
};

const EXPECTED_HELPER_ANCHORS = [_][]const u8{
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
};

const EXPECTED_SURVEY_SNIPPETS = [_][]const u8{
    "# Phase 6 Runtime Command And Environment Gap Survey",
    "That is a runtime command substrate, not a Phase 6 leaf-helper replay.",
    "That is session and command-routing behavior, not helper-only Phase 6 evidence.",
    "These are environment-plumbing and orchestrator-state surfaces.",
    "A fresh current-master reread on 2026-05-27 did not change that boundary.",
    "Do not use it to claim that Zigux Phase 6 has already landed:",
    "- shell execution semantics",
    "- TTY session control",
    "- runtime RPC/session control",
    "- persisted workspace or app-runtime environment orchestration",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_expected_packet_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md");
    defer allocator.free(text_expected_packet_path);
    const text_expected_packet = try guard.readUtf8File(io, allocator, text_expected_packet_path);
    defer allocator.free(text_expected_packet);
    for (EXPECTED_PACKET) |marker| try guard.requireMarker(text_expected_packet, marker);
    const text_expected_lane_scope_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md");
    defer allocator.free(text_expected_lane_scope_path);
    const text_expected_lane_scope = try guard.readUtf8File(io, allocator, text_expected_lane_scope_path);
    defer allocator.free(text_expected_lane_scope);
    for (EXPECTED_LANE_SCOPE) |marker| try guard.requireMarker(text_expected_lane_scope, marker);
    const text_expected_surveyed_head_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md");
    defer allocator.free(text_expected_surveyed_head_path);
    const text_expected_surveyed_head = try guard.readUtf8File(io, allocator, text_expected_surveyed_head_path);
    defer allocator.free(text_expected_surveyed_head);
    for (EXPECTED_SURVEYED_HEAD) |marker| try guard.requireMarker(text_expected_surveyed_head, marker);
    const text_expected_survey_companion_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md");
    defer allocator.free(text_expected_survey_companion_path);
    const text_expected_survey_companion = try guard.readUtf8File(io, allocator, text_expected_survey_companion_path);
    defer allocator.free(text_expected_survey_companion);
    for (EXPECTED_SURVEY_COMPANION) |marker| try guard.requireMarker(text_expected_survey_companion, marker);
    const text_expected_helper_anchors_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md");
    defer allocator.free(text_expected_helper_anchors_path);
    const text_expected_helper_anchors = try guard.readUtf8File(io, allocator, text_expected_helper_anchors_path);
    defer allocator.free(text_expected_helper_anchors);
    for (EXPECTED_HELPER_ANCHORS) |marker| try guard.requireMarker(text_expected_helper_anchors, marker);
    const text_expected_survey_snippets_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md");
    defer allocator.free(text_expected_survey_snippets_path);
    const text_expected_survey_snippets = try guard.readUtf8File(io, allocator, text_expected_survey_snippets_path);
    defer allocator.free(text_expected_survey_snippets);
    for (EXPECTED_SURVEY_SNIPPETS) |marker| try guard.requireMarker(text_expected_survey_snippets, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

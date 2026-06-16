const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_NOTIFIER_PACKET=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "`scripts/zigux/check_phase13_notifier_packet.zig`",
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/helpers/list_view.zig`",
    "`zigux/helpers/hlist_view.zig`",
    "`zigux/helpers/notifier_chain_view.zig`",
    "`scripts\zigux/validate_phase13_release.zig`",
    "`zigux/tests/phase13_build.zig`",
    "`make -C zigux phase13-validate`",
    "focused checker",
    "repo-reality gaps",
    "listIsEmpty()",
    "zigux_list_is_empty()",
    "firstPprevMatchesHead()",
    "zigux_hlist_first_pprev_matches_head()",
    "firstBrokenPrevLink()",
    "zigux_hlist_first_broken_prev_link()",
    "tailNextIsNull()",
    "zigux_hlist_tail_next_is_null()",
    "Documentation/zigux/phase13-notifier-summary-gap.md",
    "`scripts/zigux/check_phase13_notifier_packet.zig`",
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "`zigux/helpers/list_view.zig`",
    "`zigux/helpers/hlist_view.zig`",
    "`zigux/helpers/notifier_chain_view.zig`",
    "`scripts\zigux/validate_phase13_release.zig`",
    "`zigux/tests/phase13_build.zig`",
    "`make -C zigux phase13-validate`",
    "repo-reality gaps",
    "The remaining notifier-family gaps are therefore the still-missing direct companions themselves rather than stale summary wording inside the already-shipped reminder set.",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "\"lane_key\": \"P13-L18\"",
    "\"anchor\": \"drivers/tty/hvc/hvc_console.h\"",
    "\"current_notifier_packet_checker_present\": true",
    "\"current_phase13_notifier_list_manifest_present\": true",
    "\"current_phase13_notifier_list_reviewability_present\": true",
    "\"current_list_view_present\": true",
    "\"current_hlist_view_present\": true",
    "\"current_phase13_release_validator_present\": true",
    "\"current_phase13_build_present\": false",
    "\"id\": \"phase13-notifier-list-view-helper\"",
    "\"id\": \"phase13-notifier-hlist-view-helper\"",
    "\"id\": \"phase13-notifier-focused-packet-checker\"",
    "\"id\": \"phase13-notifier-release-validator-companion\"",
    "\"id\": \"phase13-notifier-reviewability-gate\"",
    "\"id\": \"phase13-notifier-priority-signal-gap\"",
    "\"id\": \"phase13-notifier-chain-helper-gap\"",
    "\"id\": \"phase13-build-route-gap\"",
    "listIsEmpty()",
    "zigux_list_is_empty()",
    "firstPprevMatchesHead()",
    "zigux_hlist_first_pprev_matches_head()",
    "firstBrokenPrevLink()",
    "zigux_hlist_first_broken_prev_link()",
    "tailNextIsNull()",
    "zigux_hlist_tail_next_is_null()",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "const manifest_text = @embedFile(\"phase13_notifier_list_manifest.json\");",
    "readRepoFile(std.testing.allocator, \"Documentation/zigux/phase13-notifier-list-survey.md\")",
    "readRepoFile(std.testing.allocator, \"scripts/zigux/check_phase13_notifier_packet.zig\")",
    "\"phase13-notifier-focused-packet-checker\"",
    "\"PHASE13_NOTIFIER_PACKET=pass\"",
    "\"pub fn listIsEmpty\"",
    "\"zigux_list_is_empty\"",
    "\"pub fn firstPprevMatchesHead\"",
    "\"zigux_hlist_first_pprev_matches_head\"",
    "\"pub fn firstBrokenPrevLink\"",
    "\"zigux_hlist_first_broken_prev_link\"",
    "\"pub fn tailNextIsNull\"",
    "\"zigux_hlist_tail_next_is_null\"",
    "zigux/bindings/notifier_abi.zig",
    "pub const NotifierBlock = extern struct",
    "pub fn chainHasNonincreasingPriority",
    "pub fn listIsEmpty",
    "pub fn listHasConsistentBacklinks",
    "pub fn firstPprevMatchesHead",
    "pub fn firstBrokenPrevLink",
    "pub fn hlistHasConsistentPrevLinks",
    "zigux/helpers/list_view.zig",
    "pub const ListView = struct",
    "pub fn hasConsistentBacklinks(self: ListView) bool",
    "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak",
    "zigux/helpers/hlist_view.zig",
    "pub const HListView = struct",
    "pub fn firstPprevMatchesHead(self: HListView) bool",
    "pub fn hasConsistentPrevLinks(self: HListView) bool",
    "pub fn firstBrokenPrevLink(self: HListView) ?PrevLinkBreak",
    "pub fn tailNextIsNull(self: HListView) bool",
    "include/zigux/abi.h",
    "struct zigux_notifier_block {",
    "struct zigux_list_head {",
    "struct zigux_hlist_head {",
    "zigux_notifier_first_chain_priority_increase",
    "zigux_list_is_empty",
    "zigux_list_has_consistent_backlinks",
    "zigux_hlist_first_pprev_matches_head",
    "zigux_hlist_first_broken_prev_link",
    "zigux_hlist_has_consistent_prev_links",
    "zigux_hlist_tail_next_is_null",
    "drivers/tty/hvc/hvc_console.h",
    "int notifier_add_irq(struct hvc_struct *hp, int irq);",
    "void notifier_del_irq(struct hvc_struct *hp, int irq);",
    "void notifier_hangup_irq(struct hvc_struct *hp, int irq);",
    "scripts\zigux/validate_phase13_release.zig",
    "Documentation/zigux/phase13-notifier-summary-gap.md",
    "`scripts/zigux/check_phase13_notifier_packet.zig`",
    "`zigux/tests/phase13_notifier_list_manifest.json`",
    "`zigux/tests/phase13_notifier_list_reviewability.zig`",
    "zigux/Makefile",
    "PYTHON ?= python3",
    ".PHONY:",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "`zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `scripts/zigux/check_phase13_notifier_packet.zig`",
    "zigux/Makefile",
    "nphase13-validate:",
    "nphase13:",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
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

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
    try requireContains(manifest_text, "\"current_list_view_present\": true");
    try requireContains(manifest_text, "\"current_hlist_view_present\": true");
    try requireContains(manifest_text, "\"current_phase13_release_validator_present\": true");
    try requireContains(manifest_text, "\"current_phase13_build_present\": false");
    try requireContains(manifest_text, "\"id\": \"phase13-notifier-list-view-helper\"");
    try requireContains(manifest_text, "\"id\": \"phase13-notifier-hlist-view-helper\"");
    try requireContains(manifest_text, "\"id\": \"phase13-notifier-focused-packet-checker\"");
    try requireContains(manifest_text, "\"id\": \"phase13-notifier-release-validator-companion\"");
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
    try requireContains(survey, "`zigux/helpers/list_view.zig`");
    try requireContains(survey, "`zigux/helpers/hlist_view.zig`");
    try requireContains(survey, "`include/zigux/abi.h`");
    try requireContains(survey, "`drivers/tty/hvc/hvc_console.h`");
    try requireContains(survey, "`zigux/helpers/notifier_chain_view.zig`");
    try requireContains(survey, "`scripts/zigux/validate-phase13-release.py`");
    try requireContains(survey, "`make -C zigux phase13-validate`");
    try requireContains(survey, "focused checker");
}

test "phase13 notifier checker stays explicit in the focused reviewability gate" {
    const checker = try readRepoFile(std.testing.allocator, "scripts/zigux/check-phase13-notifier-packet.py");
    defer std.testing.allocator.free(checker);

    try requireContains(checker, "PHASE13_NOTIFIER_PACKET=pass");
    try requireContains(checker, "phase13-notifier-focused-packet-checker");
    try requireContains(checker, "phase13-notifier-list-view-helper");
    try requireContains(checker, "phase13-notifier-hlist-view-helper");
    try requireContains(checker, "Documentation/zigux/phase13-notifier-list-survey.md");
    try requireContains(checker, "zigux/tests/phase13_notifier_list_manifest.json");
    try requireContains(checker, "drivers/tty/hvc/hvc_console.h");
}

test "phase13 notifier binding keeps the shipped read-only interop foothold explicit" {
    const binding = try readRepoFile(std.testing.allocator, "zigux/bindings/notifier_abi.zig");
    defer std.testing.allocator.free(binding);

    try requireContains(binding, "pub const NotifierBlock = extern struct");
    try requireContains(binding, "pub const ListHead = extern struct");
    try requireContains(binding, "pub const HListHead = extern struct");
    try requireContains(binding, "pub fn chainHasNonincreasingPriority");
    try requireContains(binding, "pub fn firstChainPriorityIncrease");
    try requireContains(binding, "pub fn firstBrokenBacklink");
    try requireContains(binding, "pub fn listHasConsistentBacklinks");
    try requireContains(binding, "pub fn firstBrokenPrevLink");
    try requireContains(binding, "pub fn hlistHasConsistentPrevLinks");
}

test "phase13 list and hlist helpers keep the shipped read-only traversal packet explicit" {
    const list_view = try readRepoFile(std.testing.allocator, "zigux/helpers/list_view.zig");
    defer std.testing.allocator.free(list_view);
    try requireContains(list_view, "pub const ListView = struct");
    try requireContains(list_view, "pub fn hasConsistentBacklinks(self: ListView) bool");
    try requireContains(list_view, "pub fn firstBrokenBacklink(self: ListView) ?BackLinkBreak");

    const hlist_view = try readRepoFile(std.testing.allocator, "zigux/helpers/hlist_view.zig");
    defer std.testing.allocator.free(hlist_view);
    try requireContains(hlist_view, "pub const HListView = struct");
    try requireContains(hlist_view, "pub fn hasConsistentPrevLinks(self: HListView) bool");
    try requireContains(hlist_view, "pub fn firstBrokenPrevLink(self: HListView) ?PrevLinkBreak");
}

test "phase13 exported abi header keeps the C-side list and notifier witnesses explicit" {
    const abi_header = try readRepoFile(std.testing.allocator, "include/zigux/abi.h");
    defer std.testing.allocator.free(abi_header);

    try requireContains(abi_header, "struct zigux_notifier_block {");
    try requireContains(abi_header, "struct zigux_list_head {");
    try requireContains(abi_header, "struct zigux_hlist_head {");
    try requireContains(abi_header, "zigux_notifier_chain_has_nonincreasing_priority");
    try requireContains(abi_header, "zigux_notifier_first_chain_priority_increase");
    try requireContains(abi_header, "zigux_list_first_broken_backlink");
    try requireContains(abi_header, "zigux_list_has_consistent_backlinks");
    try requireContains(abi_header, "zigux_hlist_first_broken_prev_link");
    try requireContains(abi_header, "zigux_hlist_has_consistent_prev_links");
}

test "phase13 hvc header keeps the notifier declarations visible to the adjacent packet" {
    const hvc_header = try readRepoFile(std.testing.allocator, "drivers/tty/hvc/hvc_console.h");
    defer std.testing.allocator.free(hvc_header);

    try requireContains(hvc_header, "int notifier_add_irq(struct hvc_struct *hp, int irq);");
    try requireContains(hvc_header, "void notifier_del_irq(struct hvc_struct *hp, int irq);");
    try requireContains(hvc_header, "void notifier_hangup_irq(struct hvc_struct *hp, int irq);");
}

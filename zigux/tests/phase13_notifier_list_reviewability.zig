const std = @import("std");

const SurveySummary = struct {
    preexisting_phase13_build_present: bool,
    preexisting_phase3_build_present: bool,
    preexisting_list_abi_present: bool,
    preexisting_hlist_abi_present: bool,
    preexisting_list_view_present: bool,
    preexisting_hlist_view_present: bool,
    preexisting_chrdev_notify_plan_present: bool,
    preexisting_phase11_hvc_header_parity_present: bool,
    preexisting_generic_notifier_header_anchor_present: bool,
    preexisting_generic_notifier_abi_present: bool,
    preexisting_generic_notifier_helper_present: bool,
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

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "preexisting_phase3_surface") or
        std.mem.eql(u8, status, "preexisting_chrdev_surface") or
        std.mem.eql(u8, status, "preexisting_phase11_surface") or
        std.mem.eql(u8, status, "preexisting_header_surface") or
        std.mem.eql(u8, status, "ready_next");
}

fn readRepoFile(io: std.Io, allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(1024 * 1024));
}

test "phase13 notifier/list survey keeps the current list surface and generic notifier gap explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/tests/phase13_notifier_list_manifest.json");
    defer std.testing.allocator.free(manifest_json);
    const phase13_build = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/tests/phase13_build.zig");
    defer std.testing.allocator.free(phase13_build);
    const phase3_build = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/tests/build.zig");
    defer std.testing.allocator.free(phase3_build);
    const abi_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/bindings/abi.zig");
    defer std.testing.allocator.free(abi_text);
    const list_view_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/helpers/list_view.zig");
    defer std.testing.allocator.free(list_view_text);
    const hlist_view_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/helpers/hlist_view.zig");
    defer std.testing.allocator.free(hlist_view_text);
    const chrdev_notify_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/helpers/chrdev_notify_plan.zig");
    defer std.testing.allocator.free(chrdev_notify_text);
    const hvc_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "drivers/tty/hvc/hvc_console.h");
    defer std.testing.allocator.free(hvc_header_text);
    const hvc_console_text = try readRepoFile(io_instance.io(), std.testing.allocator, "drivers/tty/hvc/hvc_console.zig");
    defer std.testing.allocator.free(hvc_console_text);
    const notifier_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "include/linux/notifier.h");
    defer std.testing.allocator.free(notifier_header_text);
    const acpi_wbrf_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "include/linux/acpi_amd_wbrf.h");
    defer std.testing.allocator.free(acpi_wbrf_header_text);
    const survey_note = try readRepoFile(io_instance.io(), std.testing.allocator, "Documentation/zigux/phase13-notifier-list-survey.md");
    defer std.testing.allocator.free(survey_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P13-L17", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("05a762ea272fa488b877178987418c54c030b239", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 3), manifest.anchors.len);
    try std.testing.expectEqualStrings("include/linux/list.h", manifest.anchors[0]);
    try std.testing.expectEqualStrings("include/linux/notifier.h", manifest.anchors[1]);
    try std.testing.expectEqualStrings("include/linux/acpi_amd_wbrf.h", manifest.anchors[2]);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_scope, "shared helper") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_scope, "libfs, devres, and Landlock") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_scope, "generic notifier header anchors") != null);

    try std.testing.expect(manifest.survey_summary.preexisting_phase13_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase3_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_list_abi_present);
    try std.testing.expect(manifest.survey_summary.preexisting_hlist_abi_present);
    try std.testing.expect(manifest.survey_summary.preexisting_list_view_present);
    try std.testing.expect(manifest.survey_summary.preexisting_hlist_view_present);
    try std.testing.expect(manifest.survey_summary.preexisting_chrdev_notify_plan_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase11_hvc_header_parity_present);
    try std.testing.expect(manifest.survey_summary.preexisting_generic_notifier_header_anchor_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_generic_notifier_abi_present);
    try std.testing.expect(!manifest.survey_summary.preexisting_generic_notifier_helper_present);
    try std.testing.expectEqual(@as(usize, 11), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, phase13_build, "phase13_notifier_list_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase3_build, "../helpers/list_view.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase3_build, "../helpers/hlist_view.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase3_build, "../helpers/chrdev_notify_plan.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_text, "pub const ListHeadRef = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_text, "pub const HListHeadRef = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_text, "pub const NotifierBlockRef") == null);
    try std.testing.expect(std.mem.indexOf(u8, abi_text, "pub const BlockingNotifierHeadRef") == null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn viewFromHead") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn summarize") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn viewFromHead") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn summarize") != null);
    try std.testing.expect(std.mem.indexOf(u8, chrdev_notify_text, "pub fn viewFromBits") != null);
    try std.testing.expect(std.mem.indexOf(u8, chrdev_notify_text, "abi.ChrdevNotifyView") != null);
    try std.testing.expect(std.mem.indexOf(u8, chrdev_notify_text, "ListHeadRef") == null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_header_text, "typedef\tint (*notifier_fn_t)(struct notifier_block *nb,") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_header_text, "struct notifier_block {") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_header_text, "struct raw_notifier_head {") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header_text, "struct list_head next;") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header_text, "int (*notifier_add)(struct hvc_struct *hp, int irq);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header_text, "void (*notifier_del)(struct hvc_struct *hp, int irq);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header_text, "void (*notifier_hangup)(struct hvc_struct *hp, int irq);") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_console_text, "pub fn headerParitySnapshot() HeaderParitySnapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_console_text, ".has_notifier_add = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_console_text, ".has_notifier_del = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_console_text, ".has_notifier_hangup = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_console_text, ".notifier_callbacks_pending = true") != null);
    try std.testing.expect(std.mem.indexOf(u8, acpi_wbrf_header_text, "#include <linux/notifier.h>") != null);
    try std.testing.expect(std.mem.indexOf(u8, acpi_wbrf_header_text, "int amd_wbrf_register_notifier(struct notifier_block *nb);") != null);
    try std.testing.expect(std.mem.indexOf(u8, acpi_wbrf_header_text, "int amd_wbrf_unregister_notifier(struct notifier_block *nb);") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "generic notifier ABI surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "roadmap-adjacent reviewability evidence only") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "list and hlist view surface") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "driver-local notifier/list anchor") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "generic notifier header anchor") != null);

    var starter_landed_count: usize = 0;
    var preexisting_phase3_count: usize = 0;
    var preexisting_chrdev_count: usize = 0;
    var preexisting_phase11_count: usize = 0;
    var preexisting_header_count: usize = 0;
    var ready_next_count: usize = 0;
    var saw_build_gate = false;
    var saw_reviewability_gate = false;
    var saw_survey_note = false;
    var saw_list_abi = false;
    var saw_list_views = false;
    var saw_chrdev_notify = false;
    var saw_hvc_anchor = false;
    var saw_generic_notifier_header_anchor = false;
    var saw_generic_notifier_abi_gap = false;
    var saw_generic_notifier_helper_gap = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, gap.status, "preexisting_phase3_surface") ) preexisting_phase3_count += 1;
        if (std.mem.eql(u8, gap.status, "preexisting_chrdev_surface")) preexisting_chrdev_count += 1;
        if (std.mem.eql(u8, gap.status, "preexisting_phase11_surface")) preexisting_phase11_count += 1;
        if (std.mem.eql(u8, gap.status, "preexisting_header_surface")) preexisting_header_count += 1;
        if (std.mem.eql(u8, gap.status, "ready_next")) ready_next_count += 1;

        if (std.mem.eql(u8, gap.id, "phase13-build-gate")) {
            saw_build_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-notifier-list-reviewability-gate")) {
            saw_reviewability_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/phase13_notifier_list_reviewability.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-notifier-list-survey-note")) {
            saw_survey_note = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("Documentation/zigux/phase13-notifier-list-survey.md", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase3-list-abi-and-view-surface")) {
            saw_list_abi = true;
            try std.testing.expectEqualStrings("preexisting_phase3_surface", gap.status);
            try std.testing.expectEqualStrings("zigux/bindings/abi.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase3-list-hlist-replay-surface")) {
            saw_list_views = true;
            try std.testing.expectEqualStrings("preexisting_phase3_surface", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/build.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase3-chrdev-notify-surface")) {
            saw_chrdev_notify = true;
            try std.testing.expectEqualStrings("preexisting_chrdev_surface", gap.status);
            try std.testing.expectEqualStrings("zigux/helpers/chrdev_notify_plan.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase11-hvc-header-notifier-list-anchor")) {
            saw_hvc_anchor = true;
            try std.testing.expectEqualStrings("preexisting_phase11_surface", gap.status);
            try std.testing.expectEqualStrings("drivers/tty/hvc/hvc_console.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "linux-generic-notifier-header-anchor")) {
            saw_generic_notifier_header_anchor = true;
            try std.testing.expectEqualStrings("preexisting_header_surface", gap.status);
            try std.testing.expectEqualStrings("include/linux/acpi_amd_wbrf.h", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-generic-notifier-abi-gap")) {
            saw_generic_notifier_abi_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("zigux/bindings/abi.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-generic-notifier-helper-gap")) {
            saw_generic_notifier_helper_gap = true;
            try std.testing.expectEqualStrings("ready_next", gap.status);
            try std.testing.expectEqualStrings("zigux/helpers/", gap.zigux_destination);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
        }
    }

    try std.testing.expectEqual(@as(usize, 3), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 3), preexisting_phase3_count);
    try std.testing.expectEqual(@as(usize, 1), preexisting_chrdev_count);
    try std.testing.expectEqual(@as(usize, 1), preexisting_phase11_count);
    try std.testing.expectEqual(@as(usize, 1), preexisting_header_count);
    try std.testing.expectEqual(@as(usize, 2), ready_next_count);
    try std.testing.expect(saw_build_gate);
    try std.testing.expect(saw_reviewability_gate);
    try std.testing.expect(saw_survey_note);
    try std.testing.expect(saw_list_abi);
    try std.testing.expect(saw_list_views);
    try std.testing.expect(saw_chrdev_notify);
    try std.testing.expect(saw_hvc_anchor);
    try std.testing.expect(saw_generic_notifier_header_anchor);
    try std.testing.expect(saw_generic_notifier_abi_gap);
    try std.testing.expect(saw_generic_notifier_helper_gap);
}

const std = @import("std");

const SurveySummary = struct {
    preexisting_phase13_build_present: bool,
    preexisting_phase3_build_present: bool,
    preexisting_list_abi_present: bool,
    preexisting_hlist_abi_present: bool,
    preexisting_list_view_present: bool,
    preexisting_hlist_view_present: bool,
    preexisting_list_helper_api_companion_present: bool,
    preexisting_chrdev_notify_plan_present: bool,
    preexisting_phase11_hvc_header_parity_present: bool,
    preexisting_generic_notifier_header_anchor_present: bool,
    preexisting_generic_notifier_layout_anchor_present: bool,
    preexisting_public_list_notifier_coexistence_anchor_present: bool,
    preexisting_public_same_struct_list_notifier_anchor_present: bool,
    landed_generic_notifier_abi_present: bool,
    landed_generic_notifier_build_surface_present: bool,
    landed_generic_notifier_helper_present: bool,
    landed_generic_notifier_c_header_surface_present: bool,
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
        std.mem.eql(u8, status, "preexisting_header_surface");
}

fn readRepoFile(io: std.Io, allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(1024 * 1024));
}

test "phase13 notifier/list survey records the landed read-only generic notifier foothold" {
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
    const notifier_abi_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/bindings/notifier_abi.zig");
    defer std.testing.allocator.free(notifier_abi_text);
    const notifier_c_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "include/zigux/notifier_abi.h");
    defer std.testing.allocator.free(notifier_c_header_text);
    const linux_zigux_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "include/linux/zigux.h");
    defer std.testing.allocator.free(linux_zigux_header_text);
    const list_c_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "include/zigux/list_view.h");
    defer std.testing.allocator.free(list_c_header_text);
    const list_view_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/helpers/list_view.zig");
    defer std.testing.allocator.free(list_view_text);
    const hlist_view_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/helpers/hlist_view.zig");
    defer std.testing.allocator.free(hlist_view_text);
    const notifier_helper_text = try readRepoFile(io_instance.io(), std.testing.allocator, "zigux/helpers/notifier_chain_view.zig");
    defer std.testing.allocator.free(notifier_helper_text);
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
    const dsa_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "include/net/dsa.h");
    defer std.testing.allocator.free(dsa_header_text);
    const watchdog_header_text = try readRepoFile(io_instance.io(), std.testing.allocator, "include/linux/watchdog.h");
    defer std.testing.allocator.free(watchdog_header_text);
    const survey_note = try readRepoFile(io_instance.io(), std.testing.allocator, "Documentation/zigux/phase13-notifier-list-survey.md");
    defer std.testing.allocator.free(survey_note);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P13-L19", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 13", manifest.phase);
    try std.testing.expectEqualStrings("66b55d8a9a800345097f3c04b9f95130b1f8d0b8", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 5), manifest.anchors.len);
    try std.testing.expectEqualStrings("include/linux/list.h", manifest.anchors[0]);
    try std.testing.expectEqualStrings("include/linux/notifier.h", manifest.anchors[1]);
    try std.testing.expectEqualStrings("include/linux/acpi_amd_wbrf.h", manifest.anchors[2]);
    try std.testing.expectEqualStrings("include/net/dsa.h", manifest.anchors[3]);
    try std.testing.expectEqualStrings("include/linux/watchdog.h", manifest.anchors[4]);
    try std.testing.expect(std.mem.indexOf(u8, manifest.roadmap_scope, "dedicated exported C header") != null);
    try std.testing.expect(manifest.survey_summary.landed_generic_notifier_abi_present);
    try std.testing.expect(manifest.survey_summary.landed_generic_notifier_build_surface_present);
    try std.testing.expect(manifest.survey_summary.landed_generic_notifier_helper_present);
    try std.testing.expect(manifest.survey_summary.landed_generic_notifier_c_header_surface_present);
    try std.testing.expect(manifest.survey_summary.preexisting_list_helper_api_companion_present);
    try std.testing.expectEqual(@as(usize, 16), manifest.gaps.len);

    try std.testing.expect(std.mem.indexOf(u8, phase13_build, "../bindings/notifier_abi.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase13_build, "../helpers/notifier_chain_view.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase3_build, "../helpers/list_view.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase3_build, "../helpers/hlist_view.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, phase3_build, "../helpers/chrdev_notify_plan.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_text, "pub const ListHeadRef = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, abi_text, "pub const HListHeadRef = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const NotifierBlockRef = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const RawNotifierHeadRef = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const NotifierChainView = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const NotifierChainSummary = extern struct") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_abi_text, "pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING: u32 = 16;") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "struct zigux_notifier_block_ref") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "struct zigux_raw_notifier_head_ref") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "struct zigux_notifier_chain_view") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "struct zigux_notifier_chain_summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_view_from_head") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_view_valid") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_empty") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_length_bounded") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_summarize") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_has_nonincreasing_priority_order") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING") != null);
    try std.testing.expect(std.mem.indexOf(u8, linux_zigux_header_text, "struct zigux_notifier_chain_view") == null);
    try std.testing.expect(std.mem.indexOf(u8, linux_zigux_header_text, "struct zigux_notifier_chain_summary") == null);
    try std.testing.expect(std.mem.indexOf(u8, linux_zigux_header_text, "zigux_notifier_chain_view_from_head") == null);
    try std.testing.expect(std.mem.indexOf(u8, linux_zigux_header_text, "zigux_notifier_chain_summarize") == null);
    try std.testing.expect(std.mem.indexOf(u8, linux_zigux_header_text, "ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING") == null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "struct zigux_list_view") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "struct zigux_list_summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "struct zigux_hlist_view") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "struct zigux_hlist_summary") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "zigux_list_view_from_head") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "zigux_list_empty") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "zigux_list_length_bounded") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "zigux_list_summarize") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "zigux_hlist_view_from_head") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "zigux_hlist_empty") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "zigux_hlist_length_bounded") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "zigux_hlist_summarize") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "ZIGUX_LIST_FLAG_CIRCULAR") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_c_header_text, "ZIGUX_HLIST_FLAG_TERMINATED") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "pub fn viewFromHead") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "pub fn isEmpty") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "pub fn length") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "pub fn summarize") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "pub fn hasNonincreasingPriorityOrder") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "priority_nonincreasing") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "clears the priority-order flag when priorities rise") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn viewFromHead") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn isEmpty") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn length") != null);
    try std.testing.expect(std.mem.indexOf(u8, list_view_text, "pub fn summarize") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn viewFromHead") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn isEmpty") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn length") != null);
    try std.testing.expect(std.mem.indexOf(u8, hlist_view_text, "pub fn summarize") != null);
    try std.testing.expect(std.mem.indexOf(u8, chrdev_notify_text, "pub fn viewFromBits") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header_text, "struct list_head next;") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_header_text, "notifier_add") != null);
    try std.testing.expect(std.mem.indexOf(u8, hvc_console_text, "pub fn headerParitySnapshot() HeaderParitySnapshot") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_header_text, "typedef\tint (*notifier_fn_t)(struct notifier_block *nb,") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_header_text, "struct notifier_block {") != null);
    try std.testing.expect(std.mem.indexOf(u8, notifier_header_text, "struct raw_notifier_head {") != null);
    try std.testing.expect(std.mem.indexOf(u8, acpi_wbrf_header_text, "amd_wbrf_register_notifier") != null);
    try std.testing.expect(std.mem.indexOf(u8, dsa_header_text, "struct raw_notifier_head\tnh;") != null);
    try std.testing.expect(std.mem.indexOf(u8, watchdog_header_text, "struct notifier_block reboot_nb;") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "lane key: `P13-L19`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`include/net/dsa.h`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`include/linux/watchdog.h`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/bindings/notifier_abi.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "include/zigux/notifier_abi.h") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`zigux_notifier_chain_view_valid()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "reserved or zero-bounded views") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/helpers/notifier_chain_view.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`hasNonincreasingPriorityOrder`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "`zigux_notifier_chain_has_nonincreasing_priority_order()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "keeps the direct priority-order convenience reviewable") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "keeps the dedicated exported C header small") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "registration, callback execution, SRCU, and blocking notifier semantics remain out of scope") != null);

    var starter_landed_count: usize = 0;
    var preexisting_phase3_count: usize = 0;
    var preexisting_chrdev_count: usize = 0;
    var preexisting_phase11_count: usize = 0;
    var preexisting_header_count: usize = 0;
    var found_companion_gap = false;
    var found_c_header_gap = false;
    for (manifest.gaps) |gap| {
        try std.testing.expect(isAllowedStatus(gap.status));
        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, gap.status, "preexisting_phase3_surface") != null) preexisting_phase3_count += 1;
        if (std.mem.eql(u8, gap.status, "preexisting_chrdev_surface")) preexisting_chrdev_count += 1;
        if (std.mem.eql(u8, gap.status, "preexisting_phase11_surface")) preexisting_phase11_count += 1;
        if (std.mem.eql(u8, gap.status, "preexisting_header_surface")) preexisting_header_count += 1;
        if (std.mem.eql(u8, gap.id, "phase13-list-helper-api-companion-surface")) {
            found_companion_gap = true;
            try std.testing.expectEqualStrings("zigux/helpers/list_view.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "phase13-generic-notifier-c-header-foothold")) {
            found_c_header_gap = true;
            try std.testing.expectEqualStrings("include/zigux/notifier_abi.h", gap.zigux_destination);
        }
    }
    try std.testing.expect(found_companion_gap);
    try std.testing.expect(found_c_header_gap);
    try std.testing.expectEqual(@as(usize, 6), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 4), preexisting_phase3_count);
    try std.testing.expectEqual(@as(usize, 1), preexisting_chrdev_count);
    try std.testing.expectEqual(@as(usize, 1), preexisting_phase11_count);
    try std.testing.expectEqual(@as(usize, 4), preexisting_header_count);
}

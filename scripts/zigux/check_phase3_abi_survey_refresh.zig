const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_ABI_SURVEY_REFRESH=pass";
pub const self_test_pass_marker = "PHASE3_ABI_SURVEY_REFRESH_SELF_TEST=pass";

const DOC_MARKERS = [_][]const u8{
    "## 2026-05-26 Survey Refresh",
    "bounded Phase 3 bitmap/cpumask, list/hlist, err_ptr/xarray, and xarray-slot interop survey packet members",
    "`Documentation/zigux/phase3-bitmap-cpumask-slice.md`",
    "`zigux/helpers/bitmap_view.zig`",
    "`scripts\\zigux/check_phase3_bitmap_cpumask.zig`",
    "`Documentation/zigux/phase3-list-hlist-slice.md`",
    "`zigux/helpers/list_view.zig`",
    "`scripts\\zigux/check_phase3_list_hlist_starter_packet.zig`",
    "`Documentation/zigux/phase3-errptr-xarray-slice.md`",
    "`zigux/helpers/err_ptr.zig`",
    "`scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig`",
    "`Documentation/zigux/phase3-xarray-slot-slice.md`",
    "`zigux/helpers/xarray_slot_view.zig`",
    "`scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig`",
    "`scripts\\zigux/check_phase3_xarray_slot.zig`",
};

const CATALOG_MARKERS = [_][]const u8{
    "\"Documentation/zigux/phase3-bitmap-cpumask-slice.md\"",
    "\"zigux/helpers/bitmap_view.zig\"",
    "\"zigux/helpers/cpumask_view.zig\"",
    "\"zigux/tests/phase3_bitmap_cpumask_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_bitmap_cpumask.zig\"",
    "\"Documentation/zigux/phase3-list-hlist-slice.md\"",
    "\"zigux/helpers/list_view.zig\"",
    "\"zigux/helpers/hlist_view.zig\"",
    "\"zigux/tests/phase3_list_hlist_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_list_hlist_starter_packet.zig\"",
    "\"Documentation/zigux/phase3-errptr-xarray-slice.md\"",
    "\"zigux/helpers/err_ptr.zig\"",
    "\"zigux/helpers/xa_value.zig\"",
    "\"zigux/tests/phase3_errptr_xarray_starter_packet.zig\"",
    "\"zigux/tests/phase3_errptr_xarray_dump.zig\"",
    "\"scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig\"",
    "\"Documentation/zigux/phase3-xarray-slot-slice.md\"",
    "\"zigux/helpers/xarray_slot_view.zig\"",
    "\"zigux/tests/phase3_xarray_slot_starter_packet.zig\"",
    "\"zigux/tests/phase3_xarray_slot_dump.zig\"",
    "\"scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig\"",
    "\"scripts\\zigux/check_phase3_xarray_slot.zig\"",
    "\"zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig -- --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_list_hlist_starter_packet.zig -- --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig -- --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig -- --self-test\"",
    "\"zig run scripts\\zigux/check_phase3_xarray_slot.zig -- --self-test\"",
    "\"zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig\"",
    "\"zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig\"",
    "\"zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig\"",
    "\"zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig\"",
    "\"zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig\"",
};

const REQUIRED_REPLAY_ROUTES = [_][]const u8{
    "zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_bitmap_cpumask.zig",
    "zig run scripts\\zigux/check_phase3_list_hlist_starter_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_list_hlist_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig",
    "zig run scripts\\zigux/check_phase3_xarray_slot.zig -- --self-test",
    "zig run scripts\\zigux/check_phase3_xarray_slot.zig",
    "zig build phase3-bitmap-cpumask-starter-packet --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig",
    "zig build phase3-list-hlist-starter-packet --build-file zigux/tests/phase3_list_hlist_starter_packet_build.zig",
    "zig build phase3-errptr-xarray-dump --build-file zigux/tests/phase3_errptr_xarray_dump_build.zig",
    "zig build phase3-xarray-slot-starter-packet-test --build-file zigux/tests/phase3_xarray_slot_starter_packet_build.zig",
    "zig build phase3-xarray-slot-dump --build-file zigux/tests/phase3_xarray_slot_dump_build.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_doc_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-slice.md");
    defer allocator.free(text_doc_markers_path);
    const text_doc_markers = try guard.readUtf8File(io, allocator, text_doc_markers_path);
    defer allocator.free(text_doc_markers);
    for (DOC_MARKERS) |marker| try guard.requireMarker(text_doc_markers, marker);
    const text_catalog_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-slice.md");
    defer allocator.free(text_catalog_markers_path);
    const text_catalog_markers = try guard.readUtf8File(io, allocator, text_catalog_markers_path);
    defer allocator.free(text_catalog_markers);
    for (CATALOG_MARKERS) |marker| try guard.requireMarker(text_catalog_markers, marker);
    const text_required_replay_routes_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase3-abi-slice.md");
    defer allocator.free(text_required_replay_routes_path);
    const text_required_replay_routes = try guard.readUtf8File(io, allocator, text_required_replay_routes_path);
    defer allocator.free(text_required_replay_routes);
    for (REQUIRED_REPLAY_ROUTES) |marker| try guard.requireMarker(text_required_replay_routes, marker);
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

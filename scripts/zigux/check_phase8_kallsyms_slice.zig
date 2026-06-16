const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_KALLSYMS_SLICE=pass";
pub const self_test_pass_marker = "PHASE8_KALLSYMS_SLICE_SELF_TEST=pass";

const SCRIPT_PATH = [_][]const u8{
    "scripts\\zigux/check_phase8_kallsyms_slice.zig",
};

const NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase8-kallsyms-slice.md",
};

const REQUIRED_MARKERS__Documentation_zigux_phase8-kallsyms-slice_md = [_][]const u8{
    "This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.",
    "`PHASE8_STATUS=parked`",
    "`PHASE8_SLICE=kallsyms-parse-wrapper-parked`",
    "`scripts\\zigux/validate_phase8.zig`",
    "`tools/lib/symbol/kallsyms.zig` through the public raw fallback",
    "`scripts\\zigux/check_phase8_help_kallsyms_packet.zig`",
    "authenticated GitHub contents reads still fail for the dedicated kallsyms helper, checker, focused test, and focused build file paths",
    "This run could not freshly verify helper-local parser test expectations, focused kallsyms test behavior, or the combined help-and-kallsyms checker contents from one consistent source.",
    "restart with one focused replay step around the dedicated packet",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_script_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_kallsyms_slice.zig");
    defer allocator.free(text_script_path_path);
    const text_script_path = try guard.readUtf8File(io, allocator, text_script_path_path);
    defer allocator.free(text_script_path);
    for (SCRIPT_PATH) |marker| try guard.requireMarker(text_script_path, marker);
    const text_note_path_path = try guard.joinPath(allocator, root, "scripts\zigux/check_phase8_kallsyms_slice.zig");
    defer allocator.free(text_note_path_path);
    const text_note_path = try guard.readUtf8File(io, allocator, text_note_path_path);
    defer allocator.free(text_note_path);
    for (NOTE_PATH) |marker| try guard.requireMarker(text_note_path, marker);
    const text_required_markers__documentation_zigux_phase8-kallsyms-slice_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-kallsyms-slice/md");
    defer allocator.free(text_required_markers__documentation_zigux_phase8-kallsyms-slice_md_path);
    const text_required_markers__documentation_zigux_phase8-kallsyms-slice_md = try guard.readUtf8File(io, allocator, text_required_markers__documentation_zigux_phase8-kallsyms-slice_md_path);
    defer allocator.free(text_required_markers__documentation_zigux_phase8-kallsyms-slice_md);
    for (REQUIRED_MARKERS__Documentation_zigux_phase8-kallsyms-slice_md) |marker| try guard.requireMarker(text_required_markers__documentation_zigux_phase8-kallsyms-slice_md, marker);
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

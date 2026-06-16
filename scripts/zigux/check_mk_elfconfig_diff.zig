const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "MK_ELFCONFIG_DIFF=pass";
pub const self_test_pass_marker = "MK_ELFCONFIG_DIFF_SELF_TEST=pass";

const C_REFERENCE_SOURCE = [_][]const u8{
    "// SPDX-License-Identifier: GPL-2.0\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <elf.h>\n\nint main(int argc, char **argv)\n{\n\tunsigned char ei[EI_NIDENT];\n\n\tif (fread(ei, 1, EI_NIDENT, stdin) != EI_NIDENT) {\n\t\tfprintf(stderr, \"Error: input truncated\\n\");\n\t\treturn 1;\n\t}\n\tif (memcmp(ei, ELFMAG, SELFMAG) != 0) {\n\t\tfprintf(stderr, \"Error: not ELF\\n\");\n\t\treturn 1;\n\t}\n\tswitch (ei[EI_CLASS]) {\n\tcase ELFCLASS32:\n\t\tprintf(\"#define KERNEL_ELFCLASS ELFCLASS32\\n\");\n\t\tbreak;\n\tcase ELFCLASS64:\n\t\tprintf(\"#define KERNEL_ELFCLASS ELFCLASS64\\n\");\n\t\tbreak;\n\tdefault:\n\t\texit(1);\n\t}\n\n\treturn 0;\n}\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_c_reference_source_path = try guard.joinPath(allocator, root, "scripts/zigux/mk_elfconfig.zig");
    defer allocator.free(text_c_reference_source_path);
    const text_c_reference_source = try guard.readUtf8File(io, allocator, text_c_reference_source_path);
    defer allocator.free(text_c_reference_source);
    for (C_REFERENCE_SOURCE) |marker| try guard.requireMarker(text_c_reference_source, marker);
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

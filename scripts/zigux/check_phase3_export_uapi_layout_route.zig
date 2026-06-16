const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_EXPORT_UAPI_LAYOUT_ROUTE=pass";
pub const self_test_pass_marker = "PHASE3_EXPORT_UAPI_LAYOUT_ROUTE_SELF_TEST=pass";

const SHARED_FUNCTION = [_][]const u8{
    "fn addPhase3ExportUapiLayout(",
};

const NEXT_FUNCTION = [_][]const u8{
    "\nfn addPhase3LowLevelWrappers(",
};

const HEADER_MODULE = [_][]const u8{
    "const header_family_binding = b.createModule(.{",
};

const HEADER_IMPORT = [_][]const u8{
    "root_module.addImport(\"header_family_binding\", header_family_binding);",
};

const EXPORT_IMPORT = [_][]const u8{
    "root_module.addImport(\"export_shim\", export_shim);",
};

const SHARED_STEP = [_][]const u8{
    "\"phase3-export-uapi-layout\"",
};

const DEDICATED_STEP = [_][]const u8{
    "\"phase3-export-uapi-layout-test\"",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_shared_function_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_shared_function_path);
    const text_shared_function = try guard.readUtf8File(io, allocator, text_shared_function_path);
    defer allocator.free(text_shared_function);
    for (SHARED_FUNCTION) |marker| try guard.requireMarker(text_shared_function, marker);
    const text_next_function_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_next_function_path);
    const text_next_function = try guard.readUtf8File(io, allocator, text_next_function_path);
    defer allocator.free(text_next_function);
    for (NEXT_FUNCTION) |marker| try guard.requireMarker(text_next_function, marker);
    const text_header_module_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_header_module_path);
    const text_header_module = try guard.readUtf8File(io, allocator, text_header_module_path);
    defer allocator.free(text_header_module);
    for (HEADER_MODULE) |marker| try guard.requireMarker(text_header_module, marker);
    const text_header_import_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_header_import_path);
    const text_header_import = try guard.readUtf8File(io, allocator, text_header_import_path);
    defer allocator.free(text_header_import);
    for (HEADER_IMPORT) |marker| try guard.requireMarker(text_header_import, marker);
    const text_export_import_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_export_import_path);
    const text_export_import = try guard.readUtf8File(io, allocator, text_export_import_path);
    defer allocator.free(text_export_import);
    for (EXPORT_IMPORT) |marker| try guard.requireMarker(text_export_import, marker);
    const text_shared_step_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_shared_step_path);
    const text_shared_step = try guard.readUtf8File(io, allocator, text_shared_step_path);
    defer allocator.free(text_shared_step);
    for (SHARED_STEP) |marker| try guard.requireMarker(text_shared_step, marker);
    const text_dedicated_step_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_dedicated_step_path);
    const text_dedicated_step = try guard.readUtf8File(io, allocator, text_dedicated_step_path);
    defer allocator.free(text_dedicated_step);
    for (DEDICATED_STEP) |marker| try guard.requireMarker(text_dedicated_step, marker);
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

const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_UAPI_DEV_T_DELEGATION=pass";
pub const self_test_pass_marker = "PHASE3_UAPI_DEV_T_DELEGATION_SELF_TEST=pass";

const LINUX_MARKERS = [_][]const u8{
    "static inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    "return zigux_dev_t_fields_is_valid(fields);",
    "static inline int zigux_uapi_dev_t_fields_range_is_valid(",
    "return zigux_dev_t_fields_range_is_valid(start, end);",
    "zigux_uapi_validate_dev_t_fields(",
    "zigux_uapi_validate_dev_t_components(",
    "zigux_uapi_validate_dev_t_range(",
};

const DEV_T_MARKERS = [_][]const u8{
    "static inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)",
    "fields.major <= ZIGUX_DEV_MAJOR_MAX",
    "fields.minor <= ZIGUX_DEV_MINOR_MASK",
    "static inline int zigux_dev_t_fields_range_is_valid(",
};

const SMOKE_SOURCE = [_][]const u8{
    "\n#include <linux/zigux.h>\n\nstatic int check_dev_t_delegation(void)\n{\n    struct zigux_dev_t_fields valid = zigux_dev_t_fields_make(4u, 9u);\n    struct zigux_dev_t_fields invalid_major =\n        zigux_dev_t_fields_make(ZIGUX_DEV_MAJOR_MAX + 1u, 0u);\n    struct zigux_dev_t_fields invalid_minor =\n        zigux_dev_t_fields_make(0u, ZIGUX_DEV_MINOR_MASK + 1u);\n    struct zigux_dev_t_fields start = zigux_dev_t_fields_make(4u, 8u);\n    struct zigux_dev_t_fields end = zigux_dev_t_fields_make(4u, 9u);\n    struct zigux_export_status valid_status =\n        zigux_uapi_validate_dev_t_fields(valid);\n    struct zigux_export_status invalid_status =\n        zigux_uapi_validate_dev_t_fields(invalid_major);\n    struct zigux_export_status invalid_minor_status =\n        zigux_uapi_validate_dev_t_fields(invalid_minor);\n    struct zigux_export_status valid_range_status =\n        zigux_uapi_validate_dev_t_range(start, end);\n    struct zigux_export_status invalid_range_status =\n        zigux_uapi_validate_dev_t_range(end, start);\n\n    if (zigux_uapi_dev_t_fields_is_valid(valid) != zigux_dev_t_fields_is_valid(valid))\n        return __LINE__;\n    if (zigux_uapi_dev_t_fields_is_valid(invalid_major) != zigux_dev_t_fields_is_valid(invalid_major))\n        return __LINE__;\n    if (zigux_uapi_dev_t_fields_is_valid(invalid_minor) != zigux_dev_t_fields_is_valid(invalid_minor))\n        return __LINE__;\n    if (zigux_uapi_dev_t_fields_range_is_valid(start, end) != zigux_dev_t_fields_range_is_valid(start, end))\n        return __LINE__;\n    if (zigux_uapi_dev_t_fields_range_is_valid(end, start) != zigux_dev_t_fields_range_is_valid(end, start))\n        return __LINE__;\n    if (zigux_export_status_ok(valid_status) == 0)\n        return __LINE__;\n    if (zigux_export_status_ok(invalid_status) != 0)\n        return __LINE__;\n    if (zigux_export_status_ok(invalid_minor_status) != 0)\n        return __LINE__;\n    if (invalid_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n    if (invalid_minor_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n    if (zigux_export_status_ok(valid_range_status) == 0)\n        return __LINE__;\n    if (zigux_export_status_ok(invalid_range_status) != 0)\n        return __LINE__;\n    if (invalid_range_status.code != ZIGUX_UAPI_INVALID_ARGUMENT)\n        return __LINE__;\n\n    return 0;\n}\n\nint main(void)\n{\n    return check_dev_t_delegation();\n}\n",
};

const SELFTEST_ABI = [_][]const u8{
    "#ifndef _ZIGUX_ABI_H\n#define _ZIGUX_ABI_H\n\n#include <stdint.h>\n\n#define ZIGUX_FACILITY_KERNEL 1U\n#define ZIGUX_STATUS_FLAG_ERROR 1U\n\nstruct zigux_export_status {\n    int32_t code;\n    uint16_t facility;\n    uint16_t flags;\n};\n\nstatic inline struct zigux_export_status zigux_make_status(\n    int32_t code,\n    uint16_t facility)\n{\n    struct zigux_export_status status = {\n        .code = code,\n        .facility = facility,\n        .flags = (uint16_t)(code < 0 ? ZIGUX_STATUS_FLAG_ERROR : 0U),\n    };\n    return status;\n}\n\nstatic inline struct zigux_export_status zigux_ok_status(uint16_t facility)\n{\n    return zigux_make_status(0, facility);\n}\n\nstatic inline int zigux_export_status_ok(struct zigux_export_status status)\n{\n    return (status.flags & (uint16_t)ZIGUX_STATUS_FLAG_ERROR) == 0;\n}\n\n#endif\n",
};

const SELFTEST_DEV_T = [_][]const u8{
    "#ifndef ZIGUX_DEV_T_H\n#define ZIGUX_DEV_T_H\n\n#include <stdint.h>\n\n#define ZIGUX_DEV_MINOR_BITS 20u\n#define ZIGUX_DEV_MINOR_MASK ((1u << ZIGUX_DEV_MINOR_BITS) - 1u)\n#define ZIGUX_DEV_MAJOR_MAX ((1u << (32u - ZIGUX_DEV_MINOR_BITS)) - 1u)\n\nstruct zigux_dev_t_fields {\n    uint32_t major;\n    uint32_t minor;\n};\n\nstatic inline struct zigux_dev_t_fields zigux_dev_t_fields_make(\n    uint32_t major,\n    uint32_t minor)\n{\n    struct zigux_dev_t_fields fields = {\n        .major = major,\n        .minor = minor,\n    };\n    return fields;\n}\n\nstatic inline int zigux_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)\n{\n    return fields.major <= ZIGUX_DEV_MAJOR_MAX &&\n        fields.minor <= ZIGUX_DEV_MINOR_MASK;\n}\n\nstatic inline int zigux_dev_t_fields_range_is_valid(\n    struct zigux_dev_t_fields start,\n    struct zigux_dev_t_fields end)\n{\n    if (!zigux_dev_t_fields_is_valid(start) || !zigux_dev_t_fields_is_valid(end))\n        return 0;\n    return start.major < end.major ||\n        (start.major == end.major && start.minor <= end.minor);\n}\n\n#endif\n",
};

const SELFTEST_LINUX = [_][]const u8{
    "#ifndef _LINUX_ZIGUX_H\n#define _LINUX_ZIGUX_H\n\n#include <stdint.h>\n#include <zigux/abi.h>\n#include <zigux/dev_t.h>\n\n#define ZIGUX_UAPI_INVALID_ARGUMENT (-22)\n\nstatic inline int zigux_uapi_dev_t_fields_is_valid(struct zigux_dev_t_fields fields)\n{\n    return zigux_dev_t_fields_is_valid(fields);\n}\n\nstatic inline struct zigux_export_status zigux_uapi_validate_dev_t_fields(\n    struct zigux_dev_t_fields fields)\n{\n    if (zigux_uapi_dev_t_fields_is_valid(fields))\n        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);\n    return zigux_make_status(\n        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,\n        (uint16_t)ZIGUX_FACILITY_KERNEL);\n}\n\nstatic inline struct zigux_export_status zigux_uapi_validate_dev_t_components(\n    uint32_t major,\n    uint32_t minor)\n{\n    return zigux_uapi_validate_dev_t_fields(zigux_dev_t_fields_make(major, minor));\n}\n\nstatic inline int zigux_uapi_dev_t_fields_range_is_valid(\n    struct zigux_dev_t_fields start,\n    struct zigux_dev_t_fields end)\n{\n    return zigux_dev_t_fields_range_is_valid(start, end);\n}\n\nstatic inline struct zigux_export_status zigux_uapi_validate_dev_t_range(\n    struct zigux_dev_t_fields start,\n    struct zigux_dev_t_fields end)\n{\n    if (zigux_uapi_dev_t_fields_range_is_valid(start, end))\n        return zigux_ok_status((uint16_t)ZIGUX_FACILITY_KERNEL);\n    return zigux_make_status(\n        (int32_t)ZIGUX_UAPI_INVALID_ARGUMENT,\n        (uint16_t)ZIGUX_FACILITY_KERNEL);\n}\n\n#endif\n",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_linux_markers_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_linux_markers_path);
    const text_linux_markers = try guard.readUtf8File(io, allocator, text_linux_markers_path);
    defer allocator.free(text_linux_markers);
    for (LINUX_MARKERS) |marker| try guard.requireMarker(text_linux_markers, marker);
    const text_dev_t_markers_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_dev_t_markers_path);
    const text_dev_t_markers = try guard.readUtf8File(io, allocator, text_dev_t_markers_path);
    defer allocator.free(text_dev_t_markers);
    for (DEV_T_MARKERS) |marker| try guard.requireMarker(text_dev_t_markers, marker);
    const text_smoke_source_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_smoke_source_path);
    const text_smoke_source = try guard.readUtf8File(io, allocator, text_smoke_source_path);
    defer allocator.free(text_smoke_source);
    for (SMOKE_SOURCE) |marker| try guard.requireMarker(text_smoke_source, marker);
    const text_selftest_abi_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_selftest_abi_path);
    const text_selftest_abi = try guard.readUtf8File(io, allocator, text_selftest_abi_path);
    defer allocator.free(text_selftest_abi);
    for (SELFTEST_ABI) |marker| try guard.requireMarker(text_selftest_abi, marker);
    const text_selftest_dev_t_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_selftest_dev_t_path);
    const text_selftest_dev_t = try guard.readUtf8File(io, allocator, text_selftest_dev_t_path);
    defer allocator.free(text_selftest_dev_t);
    for (SELFTEST_DEV_T) |marker| try guard.requireMarker(text_selftest_dev_t, marker);
    const text_selftest_linux_path = try guard.joinPath(allocator, root, "include/linux/zigux.h");
    defer allocator.free(text_selftest_linux_path);
    const text_selftest_linux = try guard.readUtf8File(io, allocator, text_selftest_linux_path);
    defer allocator.free(text_selftest_linux);
    for (SELFTEST_LINUX) |marker| try guard.requireMarker(text_selftest_linux, marker);
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

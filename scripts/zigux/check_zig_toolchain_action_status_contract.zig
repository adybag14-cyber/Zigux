const std = @import("std");

const ContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
};

const required_markers = [_][]const u8{
    "parser.add_argument(\"--allow-missing\", action=\"store_true\"",
    "parser.add_argument(\"--archive-only\", action=\"store_true\"",
    "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")",
    "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")",
    "return 0 if args.allow_missing else 1",
    "print(f\"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}\")",
    "print(\"ZIG_TOOLCHAIN_STATUS=missing\")",
    "print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")",
    "print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")",
    "exit_code = 0 if status == \"present\" else 1",
    "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")",
    "print(f\"ZIG_TOOLCHAIN_VERSION={version}\")",
    "print(f\"ZIG_TOOLCHAIN_NOTE={note}\")",
};

const archive_order = [_][]const u8{
    "if args.archive_only:",
    "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid\")",
    "print(\"ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing\")",
    "return 0 if args.allow_missing else 1",
    "print(f\"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}\")",
    "return 0",
};

const executable_order = [_][]const u8{
    "zig = resolve_zig_executable(args.zig)",
    "print(\"ZIG_TOOLCHAIN_STATUS=missing\")",
    "return 0 if args.allow_missing else 1",
    "version = read_zig_version(zig)",
    "exit_code = 0 if status == \"present\" else 1",
    "print(f\"ZIG_TOOLCHAIN_STATUS={status}\")",
    "return exit_code",
};

pub fn validateCheckerSource(source: []const u8) ContractError!void {
    for (required_markers) |marker| {
        if (std.mem.indexOf(u8, source, marker) == null) {
            return ContractError.MissingMarker;
        }
    }

    try expectOrdered(source, &archive_order);
    try expectOrdered(source, &executable_order);
}

fn expectOrdered(source: []const u8, markers: []const []const u8) ContractError!void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const offset = std.mem.indexOfPos(u8, source, cursor, marker) orelse
            return ContractError.MarkerOutOfOrder;
        cursor = offset + marker.len;
    }
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    const root = if (args.len > 1) args[1] else ".";

    var stdout_buffer: [256]u8 = undefined;
    var stdout_writer = std.Io.File.stdout().writer(init.io, &stdout_buffer);
    const stdout = &stdout_writer.interface;

    const path = try std.fs.path.join(
        allocator,
        &.{ root, "scripts", "zigux", "check-zig-toolchain.py" },
    );
    defer allocator.free(path);

    const source = try std.Io.Dir.cwd().readFileAlloc(init.io, path, allocator, .limited(1024 * 1024));
    defer allocator.free(source);

    try validateCheckerSource(source);
    try stdout.writeAll("CHECK_ZIG_TOOLCHAIN_ACTION_STATUS_CONTRACT=pass\n");
    try stdout.flush();
}

test "action status branches keep archive-only and executable output markers visible" {
    try validateCheckerSource(current_marker_seed);
}

test "archive-only status markers remain ordered from invalid to missing to validated" {
    try expectOrdered(current_marker_seed, &archive_order);
}

test "executable status markers keep allow-missing before evaluated version reporting" {
    try expectOrdered(current_marker_seed, &executable_order);
}

const current_marker_seed =
    \\parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")
    \\parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")
    \\if args.archive_only:
    \\    try:
    \\        archive_target, archive_path = resolve_policy_archive(args.archive, args.archive_target)
    \\    except ValueError as exc:
    \\        print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid")
    \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={args.archive or 'unresolved'}")
    \\        print(f"ZIG_TOOLCHAIN_NOTE={exc}")
    \\        return 1
    \\    if archive_path is None or not archive_path.is_file():
    \\        print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")
    \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_PATH={archive_path or args.archive or 'unresolved'}")
    \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or 'unresolved'}")
    \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")
    \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={expected_sha}")
    \\        print(f"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}")
    \\        return 0 if args.allow_missing else 1
    \\    print(f"ZIG_TOOLCHAIN_ARCHIVE_STATUS={archive_status}")
    \\    return 0
    \\zig = resolve_zig_executable(args.zig)
    \\if zig is None:
    \\    print("ZIG_TOOLCHAIN_STATUS=missing")
    \\    print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}")
    \\    print("ZIG_TOOLCHAIN_PIN_POLICY=exact")
    \\    return 0 if args.allow_missing else 1
    \\version = read_zig_version(zig)
    \\exit_code = 0 if status == "present" else 1
    \\print(f"ZIG_TOOLCHAIN_STATUS={status}")
    \\print(f"ZIG_TOOLCHAIN_VERSION={version}")
    \\print(f"ZIG_TOOLCHAIN_NOTE={note}")
    \\return exit_code
;

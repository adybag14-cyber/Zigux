const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, needle) != null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, checker_source, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, checker_source, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "version probe failures stay on invalid diagnostic path" {
    try expectOrdered(
        "zig = resolve_zig_executable(args.zig)",
        "version = read_zig_version(zig)",
    );
    try expectOrdered(
        "version = read_zig_version(zig)",
        "status, note = evaluate_toolchain_version(version, min_version_raw, expected_channel_raw)",
    );
    try expectOrdered(
        "except ValueError as exc:\n        print(\"ZIG_TOOLCHAIN_STATUS=invalid\")",
        "print(f\"ZIG_TOOLCHAIN_PATH={zig}\")",
    );
    try expectContains("if version is not None:\n            print(f\"ZIG_TOOLCHAIN_VERSION={version}\")");
    try expectContains("print(f\"ZIG_TOOLCHAIN_MIN_SUPPORTED={min_version_raw or 'unresolved'}\")");
    try expectContains("print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try expectContains("return 1");
}

test "read_zig_version preserves executable failure reasons" {
    try expectContains("except FileNotFoundError as exc:");
    try expectContains("raise ValueError(f\"zig executable not found: {zig}\") from exc");
    try expectContains("except OSError as exc:");
    try expectContains("raise ValueError(f\"failed to execute zig at {zig}: {exc}\") from exc");
    try expectContains("detail = completed.stderr.strip() or completed.stdout.strip() or f\"exit code {completed.returncode}\"");
    try expectContains("raise ValueError(f\"zig version command failed: {detail}\")");
    try expectContains("raise ValueError(\"zig version command returned empty output\")");
}

test "invalid probe diagnostics keep exact pin context" {
    try expectOrdered(
        "expected_channel_raw = None if args.min_version else load_pinned_channel()",
        "version = read_zig_version(zig)",
    );
    try expectContains("if expected_channel_raw is not None:\n            print(f\"ZIG_TOOLCHAIN_PINNED_CHANNEL={expected_channel_raw}\")");
    try expectContains("print(\"ZIG_TOOLCHAIN_PIN_POLICY=exact\")");
    try expectContains("elif args.min_version is not None:\n            print(\"ZIG_TOOLCHAIN_PIN_POLICY=minimum_only\")");
    try expectContains("else:\n            print(\"ZIG_TOOLCHAIN_PIN_POLICY=unresolved\")");
}

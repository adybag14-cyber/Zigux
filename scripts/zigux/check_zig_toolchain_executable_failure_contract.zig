const std = @import("std");

const checker_source = @embedFile("check-zig-toolchain.py");

fn requireMarker(marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, checker_source, marker) != null);
}

fn requireOrdered(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, checker_source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, checker_source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

fn requireMarkerAfter(anchor: []const u8, marker: []const u8) !void {
    const anchor_index = std.mem.indexOf(u8, checker_source, anchor) orelse return error.MissingAnchorMarker;
    const tail = checker_source[anchor_index..];
    try std.testing.expect(std.mem.indexOf(u8, tail, marker) != null);
}

test "read_zig_version keeps executable launch failures explicit" {
    try requireMarker("def read_zig_version(zig: str, *, runner=subprocess.run) -> str:");
    try requireMarker("except FileNotFoundError as exc:");
    try requireMarker("raise ValueError(f\"zig executable not found: {zig}\") from exc");
    try requireMarker("except OSError as exc:");
    try requireMarker("raise ValueError(f\"failed to execute zig at {zig}: {exc}\") from exc");
    try requireOrdered(
        "completed = runner([zig, \"version\"], capture_output=True, text=True, check=False)",
        "if completed.returncode != 0:",
    );
}

test "read_zig_version preserves stderr stdout and empty-output diagnostics" {
    try requireMarker("detail = completed.stderr.strip() or completed.stdout.strip() or f\"exit code {completed.returncode}\"");
    try requireMarker("raise ValueError(f\"zig version command failed: {detail}\")");
    try requireMarker("version = completed.stdout.strip()");
    try requireMarker("if not version:");
    try requireMarker("raise ValueError(\"zig version command returned empty output\")");
    try requireOrdered(
        "if completed.returncode != 0:",
        "version = completed.stdout.strip()",
    );
}

test "self-test covers executable failure examples" {
    try requireMarker("runner=lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError(\"missing\"))");
    try requireMarker("\"zig executable not found\"");
    try requireMarker("stderr=\"permission denied\\n\"");
    try requireMarker("\"zig version command failed: permission denied\"");
    try requireMarker("stdout=\"\\n\"");
    try requireMarker("\"zig version command returned empty output\"");
    try requireMarker("ZIG_TOOLCHAIN_SELF_TEST_CASE_COUNT=");
}

test "main reports executable failures as invalid toolchain status" {
    try requireMarker("try:");
    try requireMarker("version = read_zig_version(zig)");
    try requireMarker("except ValueError as exc:");
    try requireMarker("print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
    try requireMarker("print(f\"ZIG_TOOLCHAIN_PATH={zig}\")");
    try requireMarker("print(f\"ZIG_TOOLCHAIN_NOTE={exc}\")");
    try requireMarkerAfter("version = read_zig_version(zig)", "print(\"ZIG_TOOLCHAIN_STATUS=invalid\")");
}

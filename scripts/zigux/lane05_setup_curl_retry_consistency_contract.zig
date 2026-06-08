const std = @import("std");

const RetryArgs = struct {
    fail: bool = false,
    location: bool = false,
    retry: ?[]const u8 = null,
    retry_all_errors: bool = false,
    retry_delay: ?[]const u8 = null,
    connect_timeout: ?[]const u8 = null,
    speed_limit: ?[]const u8 = null,
    speed_time: ?[]const u8 = null,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectEqualSlice(expected: []const u8, actual: ?[]const u8) !void {
    try std.testing.expect(actual != null);
    if (!std.mem.eql(u8, expected, actual.?)) return error.UnexpectedRetryArgumentValue;
}

fn nextToken(line: []const u8, cursor: *usize) ?[]const u8 {
    while (cursor.* < line.len and std.ascii.isWhitespace(line[cursor.*])) cursor.* += 1;
    if (cursor.* >= line.len) return null;
    const start = cursor.*;
    while (cursor.* < line.len and !std.ascii.isWhitespace(line[cursor.*])) cursor.* += 1;
    return line[start..cursor.*];
}

fn parseRetryArgs(line: []const u8) !RetryArgs {
    var args = RetryArgs{};
    var cursor: usize = 0;
    const command = nextToken(line, &cursor) orelse return error.MissingCurlCommand;
    if (std.mem.eql(u8, command, "if") or std.mem.eql(u8, command, "elif")) {
        const nested_command = nextToken(line, &cursor) orelse return error.MissingCurlCommand;
        if (!std.mem.eql(u8, nested_command, "curl")) return error.MissingCurlCommand;
    } else if (!std.mem.eql(u8, command, "curl")) {
        return error.MissingCurlCommand;
    }

    while (nextToken(line, &cursor)) |token| {
        if (std.mem.eql(u8, token, "--fail")) {
            args.fail = true;
        } else if (std.mem.eql(u8, token, "--location")) {
            args.location = true;
        } else if (std.mem.eql(u8, token, "-L")) {
            return error.ShortLocationFlag;
        } else if (std.mem.eql(u8, token, "--retry")) {
            args.retry = nextToken(line, &cursor) orelse return error.MissingRetryValue;
        } else if (std.mem.eql(u8, token, "--retry-all-errors")) {
            args.retry_all_errors = true;
        } else if (std.mem.eql(u8, token, "--retry-delay")) {
            args.retry_delay = nextToken(line, &cursor) orelse return error.MissingRetryDelayValue;
        } else if (std.mem.eql(u8, token, "--connect-timeout")) {
            args.connect_timeout = nextToken(line, &cursor) orelse return error.MissingConnectTimeoutValue;
        } else if (std.mem.eql(u8, token, "--speed-limit")) {
            args.speed_limit = nextToken(line, &cursor) orelse return error.MissingSpeedLimitValue;
        } else if (std.mem.eql(u8, token, "--speed-time")) {
            args.speed_time = nextToken(line, &cursor) orelse return error.MissingSpeedTimeValue;
        }
    }

    return args;
}

fn expectRetryArgs(args: RetryArgs) !void {
    try std.testing.expect(args.fail);
    try std.testing.expect(args.location);
    try std.testing.expect(args.retry_all_errors);
    try expectEqualSlice("5", args.retry);
    try expectEqualSlice("3", args.retry_delay);
    try expectEqualSlice("20", args.connect_timeout);
    try expectEqualSlice("1024", args.speed_limit);
    try expectEqualSlice("30", args.speed_time);
}

fn expectSameRetryArgs(left: RetryArgs, right: RetryArgs) !void {
    if (left.fail != right.fail) return error.FailFlagMismatch;
    if (left.location != right.location) return error.LocationFlagMismatch;
    if (left.retry_all_errors != right.retry_all_errors) return error.RetryAllErrorsFlagMismatch;
    if (!std.mem.eql(u8, left.retry orelse return error.LeftRetryMissing, right.retry orelse return error.RightRetryMissing)) return error.RetryValueMismatch;
    if (!std.mem.eql(u8, left.retry_delay orelse return error.LeftRetryDelayMissing, right.retry_delay orelse return error.RightRetryDelayMissing)) return error.RetryDelayValueMismatch;
    if (!std.mem.eql(u8, left.connect_timeout orelse return error.LeftConnectTimeoutMissing, right.connect_timeout orelse return error.RightConnectTimeoutMissing)) return error.ConnectTimeoutValueMismatch;
    if (!std.mem.eql(u8, left.speed_limit orelse return error.LeftSpeedLimitMissing, right.speed_limit orelse return error.RightSpeedLimitMissing)) return error.SpeedLimitValueMismatch;
    if (!std.mem.eql(u8, left.speed_time orelse return error.LeftSpeedTimeMissing, right.speed_time orelse return error.RightSpeedTimeMissing)) return error.SpeedTimeValueMismatch;
}

fn findLineContaining(text: []const u8, marker: []const u8) ![]const u8 {
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.indexOf(u8, line, marker) != null) return std.mem.trim(u8, line, " \t");
    }
    return error.MissingLine;
}

fn expectSetupCurlRetryConsistency(workflow: []const u8) !void {
    try expectContains(workflow, "- name: Setup pinned Zig toolchain");
    const archive_line = try findLineContaining(workflow, "\"$url\" -o \"$archive_path\"");
    const mirror_line = try findLineContaining(workflow, "https://ziglang.org/download/community-mirrors.txt");
    const archive_args = try parseRetryArgs(archive_line);
    const mirror_args = try parseRetryArgs(mirror_line);
    try expectRetryArgs(archive_args);
    try expectRetryArgs(mirror_args);
    try expectSameRetryArgs(archive_args, mirror_args);
}

const consistent_retry_workflow =
    \\      - name: Setup pinned Zig toolchain
    \\        run: |
    \\          try_download() {
    \\            local url="$1"
    \\            if curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 "$url" -o "$archive_path"; then
    \\              python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path"
    \\            fi
    \\          }
    \\          elif curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
    \\            while IFS= read -r mirror_url; do
    \\              [ -n "$mirror_url" ] || continue
    \\            done < "$mirror_file"
    \\          fi
;

test "archive and mirror roster downloads share the same retry contract" {
    try expectSetupCurlRetryConsistency(consistent_retry_workflow);
}

test "single-shot archive download is rejected even when mirror roster is guarded" {
    const inconsistent_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          try_download() {
        \\            local url="$1"
        \\            if curl -L --fail "$url" -o "$archive_path"; then
        \\              python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path"
        \\            fi
        \\          }
        \\          elif curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\            true
        \\          fi
    ;

    if (expectSetupCurlRetryConsistency(inconsistent_workflow)) |_| {
        return error.ExpectedContractFailure;
    } else |_| {}
}

test "mirror roster cannot drift to weaker stall protection" {
    const weaker_mirror_workflow =
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          if curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 "$url" -o "$archive_path"; then
        \\            true
        \\          fi
        \\          elif curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1 --speed-time 60 https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\            true
        \\          fi
    ;

    if (expectSetupCurlRetryConsistency(weaker_mirror_workflow)) |_| {
        return error.ExpectedContractFailure;
    } else |_| {}
}

test "missing retry-all-errors is rejected" {
    const missing_retry_all_errors =
        \\      - name: Setup pinned Zig toolchain
        \\        run: |
        \\          if curl --fail --location --retry 5 --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 "$url" -o "$archive_path"; then
        \\            true
        \\          fi
        \\          elif curl --fail --location --retry 5 --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
        \\            true
        \\          fi
    ;

    if (expectSetupCurlRetryConsistency(missing_retry_all_errors)) |_| {
        return error.ExpectedContractFailure;
    } else |_| {}
}

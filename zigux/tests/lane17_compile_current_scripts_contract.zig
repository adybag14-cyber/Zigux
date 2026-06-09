const std = @import("std");
const build_options = @import("build_options");

const SETUP_ZIG_STEP = "Setup pinned Zig toolchain";
const COMPILE_STEP = "Compile current scripts";
const TOOLCHAIN_SELF_TEST_STEP = "Self-test current Zig toolchain checker";

const REQUIRED_COMPILE_LINES = [_][]const u8{
    "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
    "if [ \"${#scripts[@]}\" -eq 0 ]; then",
    "echo 'no Python scripts found under scripts/zigux' >&2",
    "exit 1",
    "python3 -m py_compile \"${scripts[@]}\"",
};

const FORBIDDEN_COMPILE_MARKERS = [_][]const u8{
    "find scripts/zigux -type f -name '*.py'",
    "scripts/zigux/*.py",
    "python3 -m compileall",
    "python3 -m py_compile scripts/zigux/*.py",
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    if (needle.len == 0) return 0;
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOf(u8, haystack[start..], needle)) |relative| {
        count += 1;
        start += relative + needle.len;
    }
    return count;
}

fn countTrimmedLines(text: []const u8, expected: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), expected)) {
            count += 1;
        }
    }
    return count;
}

fn requireLineOnce(text: []const u8, line: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countTrimmedLines(text, line));
}

fn requireAbsent(text: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(text, needle));
}

fn requireOrdered(text: []const u8, chain: []const []const u8) !void {
    var previous_end: usize = 0;
    for (chain) |needle| {
        const index = std.mem.indexOf(u8, text[previous_end..], needle) orelse return error.MissingOrderedMarker;
        previous_end += index + needle.len;
    }
}

fn validateWorkflow(text: []const u8) !void {
    try requireLineOnce(text, "- name: " ++ COMPILE_STEP);

    for (REQUIRED_COMPILE_LINES) |line| {
        try requireLineOnce(text, line);
    }
    for (FORBIDDEN_COMPILE_MARKERS) |marker| {
        try requireAbsent(text, marker);
    }

    try requireOrdered(text, &[_][]const u8{
        "- name: " ++ SETUP_ZIG_STEP,
        "- name: " ++ COMPILE_STEP,
        "- name: " ++ TOOLCHAIN_SELF_TEST_STEP,
    });
    try requireOrdered(text, &[_][]const u8{
        "python3 -m py_compile \"${scripts[@]}\"",
        "- name: " ++ TOOLCHAIN_SELF_TEST_STEP,
    });
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        build_options.workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

test "live workflow keeps the early current-script compile gate wired" {
    const text = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(text);
    try validateWorkflow(text);
}

test "contract accepts the current compile gate shape" {
    try validateWorkflow(
        "name: zigux-bootstrap\n" ++
            "jobs:\n" ++
            "  bootstrap:\n" ++
            "    steps:\n" ++
            "      - name: " ++ SETUP_ZIG_STEP ++ "\n" ++
            "        run: zig setup placeholder\n" ++
            "      - name: " ++ COMPILE_STEP ++ "\n" ++
            "        run: |\n" ++
            "          set -euxo pipefail\n" ++
            "          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)\n" ++
            "          if [ \"${#scripts[@]}\" -eq 0 ]; then\n" ++
            "            echo 'no Python scripts found under scripts/zigux' >&2\n" ++
            "            exit 1\n" ++
            "          fi\n" ++
            "          python3 -m py_compile \"${scripts[@]}\"\n" ++
            "      - name: " ++ TOOLCHAIN_SELF_TEST_STEP ++ "\n" ++
            "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test\n",
    );
}

test "contract rejects stale narrow glob compile gates" {
    const stale =
        "name: zigux-bootstrap\n" ++
        "jobs:\n" ++
        "  bootstrap:\n" ++
        "    steps:\n" ++
        "      - name: " ++ SETUP_ZIG_STEP ++ "\n" ++
        "        run: zig setup placeholder\n" ++
        "      - name: " ++ COMPILE_STEP ++ "\n" ++
        "        run: python3 -m py_compile scripts/zigux/*.py\n" ++
        "      - name: " ++ TOOLCHAIN_SELF_TEST_STEP ++ "\n" ++
        "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test\n";
    try std.testing.expectError(error.TestExpectedEqual, validateWorkflow(stale));
}

test "contract rejects a compile gate after checker self-tests" {
    const reordered =
        "name: zigux-bootstrap\n" ++
        "jobs:\n" ++
        "  bootstrap:\n" ++
        "    steps:\n" ++
        "      - name: " ++ SETUP_ZIG_STEP ++ "\n" ++
        "        run: zig setup placeholder\n" ++
        "      - name: " ++ TOOLCHAIN_SELF_TEST_STEP ++ "\n" ++
        "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test\n" ++
        "      - name: " ++ COMPILE_STEP ++ "\n" ++
        "        run: |\n" ++
        "          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)\n" ++
        "          if [ \"${#scripts[@]}\" -eq 0 ]; then\n" ++
        "            echo 'no Python scripts found under scripts/zigux' >&2\n" ++
        "            exit 1\n" ++
        "          fi\n" ++
        "          python3 -m py_compile \"${scripts[@]}\"\n";
    try std.testing.expectError(error.MissingOrderedMarker, validateWorkflow(reordered));
}

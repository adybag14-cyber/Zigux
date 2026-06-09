const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    ForbiddenMarker,
};

fn loadWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |local_index| {
        count += 1;
        offset += local_index + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) ContractError!usize {
    const count = countNeedle(haystack, needle);
    if (count == 0) return error.MissingMarker;
    if (count != 1) return error.DuplicateMarker;
    return std.mem.indexOf(u8, haystack, needle).?;
}

fn requireAbsent(haystack: []const u8, needle: []const u8) ContractError!void {
    if (std.mem.indexOf(u8, haystack, needle) != null) return error.ForbiddenMarker;
}

fn requireAfter(haystack: []const u8, cursor: *usize, needle: []const u8) ContractError!usize {
    const local_index = std.mem.indexOf(u8, haystack[cursor.*..], needle) orelse return error.MissingMarker;
    const absolute_index = cursor.* + local_index;
    cursor.* = absolute_index + needle.len;
    return absolute_index;
}

fn validateRunnerEnvelope(workflow: []const u8) ContractError!void {
    try requireAbsent(workflow, "uses: actions/checkout@");

    const jobs_index = try requireOnce(workflow, "\njobs:\n");
    const bootstrap_index = try requireOnce(workflow, "  bootstrap:\n");
    if (bootstrap_index <= jobs_index) return error.ReorderedMarker;

    const runs_on_index = try requireOnce(workflow, "    runs-on: ubuntu-latest\n");
    if (runs_on_index <= bootstrap_index) return error.ReorderedMarker;

    const steps_index = try requireOnce(workflow, "    steps:\n");
    if (steps_index <= runs_on_index) return error.ReorderedMarker;
}

fn validateEntryLadder(workflow: []const u8) ContractError!void {
    var cursor = try requireOnce(workflow, "    steps:\n");
    _ = try requireAfter(workflow, &cursor, "      - name: Checkout workspace snapshot\n");
    _ = try requireAfter(workflow, &cursor, "          curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"\n");
    _ = try requireAfter(workflow, &cursor, "          find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +\n");
    _ = try requireAfter(workflow, &cursor, "          mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/\n");
    _ = try requireAfter(workflow, &cursor, "      - name: Setup Python\n");
    _ = try requireAfter(workflow, &cursor, "        uses: actions/setup-python@v6.2.0\n");
    _ = try requireAfter(workflow, &cursor, "      - name: Setup pinned Zig toolchain\n");
    _ = try requireAfter(workflow, &cursor, "      - name: Compile current scripts\n");
}

test "live bootstrap workflow keeps a single ubuntu bootstrap job envelope" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try validateRunnerEnvelope(workflow);
}

test "live bootstrap workflow keeps checkout snapshot before setup ladder" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try validateEntryLadder(workflow);
}

test "runner envelope rejects duplicate job runners and checkout action drift" {
    const duplicate_runner =
        \\name: zigux-bootstrap
        \\jobs:
        \\  bootstrap:
        \\    runs-on: ubuntu-latest
        \\    runs-on: ubuntu-latest
        \\    steps:
        \\
    ;
    try std.testing.expectError(error.DuplicateMarker, validateRunnerEnvelope(duplicate_runner));

    const checkout_action =
        \\name: zigux-bootstrap
        \\jobs:
        \\  bootstrap:
        \\    runs-on: ubuntu-latest
        \\    steps:
        \\      - uses: actions/checkout@v5
        \\
    ;
    try std.testing.expectError(error.ForbiddenMarker, validateRunnerEnvelope(checkout_action));
}

test "entry ladder rejects setup before checkout snapshot" {
    const reordered =
        \\name: zigux-bootstrap
        \\jobs:
        \\  bootstrap:
        \\    runs-on: ubuntu-latest
        \\    steps:
        \\      - name: Setup Python
        \\        uses: actions/setup-python@v6.2.0
        \\      - name: Checkout workspace snapshot
        \\          curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
        \\          find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        \\          mv "$src_dir"/* "$GITHUB_WORKSPACE"/
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
        \\
    ;
    try std.testing.expectError(error.MissingMarker, validateEntryLadder(reordered));
}

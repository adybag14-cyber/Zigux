const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Marker = struct {
    label: []const u8,
    text: []const u8,
};

const checkout_markers = [_]Marker{
    .{
        .label = "checkout step name",
        .text = "      - name: Checkout workspace snapshot\n",
    },
    .{
        .label = "strict shell setup",
        .text = "          set -euxo pipefail\n",
    },
    .{
        .label = "temporary source archive",
        .text = "          archive=\"$tmpdir/source.tar.gz\"\n",
    },
    .{
        .label = "exact-head codeload URL",
        .text = "          curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"\n",
    },
    .{
        .label = "tar extraction into temporary root",
        .text = "          tar -xzf \"$archive\" -C \"$tmpdir\"\n",
    },
    .{
        .label = "single top-level source directory discovery",
        .text = "          src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"\n",
    },
    .{
        .label = "workspace cleanup before materialization",
        .text = "          find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +\n",
    },
    .{
        .label = "dotfile-preserving move",
        .text = "          shopt -s dotglob\n",
    },
    .{
        .label = "source tree move into workspace",
        .text = "          mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/\n",
    },
    .{
        .label = "setup python handoff",
        .text = "      - name: Setup Python\n",
    },
};

fn requireContains(haystack: []const u8, marker: Marker) !usize {
    return std.mem.indexOf(u8, haystack, marker.text) orelse {
        std.debug.print("missing checkout snapshot workflow marker: {s}\n", .{marker.label});
        return error.MissingMarker;
    };
}

fn requireOnce(haystack: []const u8, marker: Marker) !usize {
    const first = try requireContains(haystack, marker);
    const rest = haystack[first + marker.text.len ..];
    if (std.mem.indexOf(u8, rest, marker.text) != null) {
        std.debug.print("duplicate checkout snapshot workflow marker: {s}\n", .{marker.label});
        return error.DuplicateMarker;
    }
    return first;
}

fn requireAfter(previous: *usize, index: usize, marker: Marker) !void {
    if (index <= previous.*) {
        std.debug.print("out-of-order checkout snapshot workflow marker: {s}\n", .{marker.label});
        return error.OutOfOrderMarker;
    }
    previous.* = index;
}

fn requireAbsent(haystack: []const u8, text: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, text) != null) {
        std.debug.print("forbidden stale checkout workflow marker still present: {s}\n", .{text});
        return error.ForbiddenMarker;
    }
}

fn validateCheckoutSnapshot(workflow: []const u8) !void {
    var previous: usize = 0;
    for (checkout_markers, 0..) |marker, i| {
        const index = try requireOnce(workflow, marker);
        if (i == 0) {
            previous = index;
        } else {
            try requireAfter(&previous, index, marker);
        }
    }

    try requireAbsent(workflow, "      - name: Checkout\n        uses: actions/checkout@");
    try requireAbsent(workflow, "          fetch-depth: 0\n");
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

test "checkout snapshot block materializes exact workflow head before setup" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try validateCheckoutSnapshot(workflow);
}

test "checkout snapshot block rejects stale actions checkout fallback" {
    const stale =
        \\      - name: Checkout
        \\        uses: actions/checkout@v6.0.2
        \\        with:
        \\          fetch-depth: 0
        \\
    ;

    try std.testing.expectError(error.MissingMarker, validateCheckoutSnapshot(stale));
}

test "checkout snapshot markers stay exact-once and ordered" {
    var buffer = std.ArrayList(u8).empty;
    defer buffer.deinit(std.testing.allocator);

    for (checkout_markers) |marker| {
        try buffer.appendSlice(std.testing.allocator, marker.text);
    }

    try validateCheckoutSnapshot(buffer.items);
    try buffer.appendSlice(std.testing.allocator, checkout_markers[3].text);
    try std.testing.expectError(error.DuplicateMarker, validateCheckoutSnapshot(buffer.items));
}

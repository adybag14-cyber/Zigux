const std = @import("std");
const options = @import("lane17_setup_python_slot_options");

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    OutOfOrderMarker,
};

const setup_python_markers = [_][]const u8{
    "      - name: Checkout workspace snapshot\n",
    "      - name: Setup Python\n",
    "        uses: actions/setup-python@v6.2.0\n",
    "          python-version: '3.x'\n",
    "      - name: Setup pinned Zig toolchain\n",
    "      - name: Compile current scripts\n",
    "          python3 -m py_compile \"${scripts[@]}\"\n",
    "      - name: Self-test current Zig toolchain checker\n",
};

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        options.workflow_path,
        allocator,
        .limited(256 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |relative| {
        count += 1;
        cursor += relative + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return WorkflowError.MissingMarker;
    if (countOccurrences(haystack, needle) != 1) return WorkflowError.DuplicateMarker;
    return first;
}

fn requireOrderedUnique(haystack: []const u8, markers: []const []const u8) !void {
    var previous: usize = 0;
    for (markers, 0..) |marker, index| {
        const current = try requireOnce(haystack, marker);
        if (index > 0 and current <= previous) return WorkflowError.OutOfOrderMarker;
        previous = current;
    }
}

fn validateSetupPythonSlot(workflow: []const u8) !void {
    try requireOrderedUnique(workflow, &setup_python_markers);

    const setup_python = try requireOnce(workflow, setup_python_markers[1]);
    const setup_action = try requireOnce(workflow, setup_python_markers[2]);
    const python_version = try requireOnce(workflow, setup_python_markers[3]);
    const pinned_zig = try requireOnce(workflow, setup_python_markers[4]);
    if (setup_action <= setup_python or setup_action >= pinned_zig) return WorkflowError.OutOfOrderMarker;
    if (python_version <= setup_action or python_version >= pinned_zig) return WorkflowError.OutOfOrderMarker;

    const compile_scripts = try requireOnce(workflow, setup_python_markers[5]);
    const toolchain_checker = try requireOnce(workflow, setup_python_markers[7]);
    if (toolchain_checker <= compile_scripts) return WorkflowError.OutOfOrderMarker;
}

test "live workflow keeps Python setup between checkout and pinned Zig setup" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try validateSetupPythonSlot(workflow);
}

test "contract fails closed when the Python action version drifts" {
    const fixture =
        setup_python_markers[0] ++
        setup_python_markers[1] ++
        "        uses: actions/setup-python@v6\n" ++
        setup_python_markers[3] ++
        setup_python_markers[4] ++
        setup_python_markers[5] ++
        setup_python_markers[6] ++
        setup_python_markers[7];

    try std.testing.expectError(WorkflowError.MissingMarker, validateSetupPythonSlot(fixture));
}

test "contract fails closed when Python setup moves after pinned Zig setup" {
    const fixture =
        setup_python_markers[0] ++
        setup_python_markers[4] ++
        setup_python_markers[1] ++
        setup_python_markers[2] ++
        setup_python_markers[3] ++
        setup_python_markers[5] ++
        setup_python_markers[6] ++
        setup_python_markers[7];

    try std.testing.expectError(WorkflowError.OutOfOrderMarker, validateSetupPythonSlot(fixture));
}

test "contract fails closed when the setup-python action is duplicated" {
    const fixture =
        setup_python_markers[0] ++
        setup_python_markers[1] ++
        setup_python_markers[2] ++
        setup_python_markers[2] ++
        setup_python_markers[3] ++
        setup_python_markers[4] ++
        setup_python_markers[5] ++
        setup_python_markers[6] ++
        setup_python_markers[7];

    try std.testing.expectError(WorkflowError.DuplicateMarker, validateSetupPythonSlot(fixture));
}

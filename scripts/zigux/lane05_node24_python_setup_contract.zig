const std = @import("std");
const testing = std.testing;

const build_options = @import("build_options");
const workflow = build_options.workflow_text;

const ContractError = error{
    MissingMarker,
    OutOfOrderMarker,
};

fn requireContains(haystack: []const u8, needle: []const u8) ContractError!usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn requireBefore(haystack: []const u8, before: []const u8, after: []const u8) ContractError!void {
    const before_index = try requireContains(haystack, before);
    const after_index = try requireContains(haystack, after);
    if (before_index >= after_index) return error.OutOfOrderMarker;
}

fn checkNode24PythonSetup(workflow_text: []const u8) ContractError!void {
    const env_marker = "env:\n  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true";
    const setup_python_step = "- name: Setup Python";
    const setup_python_action = "uses: actions/setup-python@v6.2.0";
    const python_version = "with:\n          python-version: '3.x'";

    _ = try requireContains(workflow_text, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true");
    try requireBefore(workflow_text, env_marker, "jobs:\n  bootstrap:");

    _ = try requireContains(workflow_text, setup_python_step);
    _ = try requireContains(workflow_text, setup_python_action);
    _ = try requireContains(workflow_text, python_version);

    try requireBefore(workflow_text, "- name: Checkout workspace snapshot", setup_python_step);
    try requireBefore(workflow_text, setup_python_step, setup_python_action);
    try requireBefore(workflow_text, setup_python_action, python_version);
    try requireBefore(workflow_text, python_version, "- name: Setup pinned Zig toolchain");
    try requireBefore(workflow_text, setup_python_step, "- name: Setup pinned Zig toolchain");
    try requireBefore(workflow_text, setup_python_action, "python3 -m py_compile");
}

test "bootstrap workflow keeps Node24 setup-python boundary viable" {
    try checkNode24PythonSetup(workflow);
}

test "bootstrap workflow rejects misplaced Node24 action forcing" {
    const stale_workflow =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Checkout workspace snapshot
        \\      - name: Setup Python
        \\        uses: actions/setup-python@v6.2.0
        \\        with:
        \\          python-version: '3.x'
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
        \\        run: python3 -m py_compile "${scripts[@]}"
        \\env:
        \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
    ;

    try testing.expectError(error.OutOfOrderMarker, checkNode24PythonSetup(stale_workflow));
}

test "bootstrap workflow rejects setup-python action downgrades" {
    const stale_workflow =
        \\env:
        \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Checkout workspace snapshot
        \\      - name: Setup Python
        \\        uses: actions/setup-python@v5
        \\        with:
        \\          python-version: '3.x'
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Compile current scripts
        \\        run: python3 -m py_compile "${scripts[@]}"
    ;

    try testing.expectError(error.MissingMarker, checkNode24PythonSetup(stale_workflow));
}

test "bootstrap workflow rejects detached Python version settings" {
    const stale_workflow =
        \\env:
        \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Checkout workspace snapshot
        \\      - name: Setup Python
        \\        uses: actions/setup-python@v6.2.0
        \\      - name: Setup pinned Zig toolchain
        \\        with:
        \\          python-version: '3.x'
        \\      - name: Compile current scripts
        \\        run: python3 -m py_compile "${scripts[@]}"
    ;

    try testing.expectError(error.OutOfOrderMarker, checkNode24PythonSetup(stale_workflow));
}

test "bootstrap workflow rejects Python setup after pinned Zig setup" {
    const stale_workflow =
        \\env:
        \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Checkout workspace snapshot
        \\      - name: Setup pinned Zig toolchain
        \\      - name: Setup Python
        \\        uses: actions/setup-python@v6.2.0
        \\        with:
        \\          python-version: '3.x'
        \\      - name: Compile current scripts
        \\        run: python3 -m py_compile "${scripts[@]}"
    ;

    try testing.expectError(error.OutOfOrderMarker, checkNode24PythonSetup(stale_workflow));
}

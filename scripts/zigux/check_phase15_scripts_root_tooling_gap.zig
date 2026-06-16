// Ported from check-phase15-scripts-root-tooling-gap.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_SCRIPTS_ROOT_TOOLING_GAP_SELF_TEST=pass";

const ALIGNMENT_CHECKER_MARKERS = [_][]const u8{
    "README_MARKERS = (",
    "\"Phase 15 flow\"",
    "\"make -C zigux phase15-validate\"",
    "\"make -C zigux phase15-test\"",
    "\"make -C zigux phase15\"",
    "scripts\\zigux/validate_phase15.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
};

const ALIGNMENT_CHECKER_PATH = "scripts\\zigux/check_phase15_scripts_readme_alignment.zig";

const ARCHITECTURE_NOTE_PATH = "Documentation/zigux/phase15-architecture-council-review-process.md";

const DOCS_MARKERS = [_][]const u8{
    "Phase 15 notes",
    "scripts\\zigux/check_phase15_scripts_readme_alignment.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
};

const DOCS_README_PATH = "Documentation/zigux/README.md";

const GAP_NOTE_PATH = "Documentation/zigux/phase15-scripts-root-tooling-gap.md";

const MISSING_PACKET_PATHS = [_][]const u8{
    "scripts\\zigux/validate_phase15.zig",
    "zigux/tests/phase15_build.zig",
    "zigux/tests/phase15_architecture_council_review_process_manifest.json",
};

const REQUIRED_GAP_NOTE_MARKERS = [_][]const u8{
    "`PHASE15_STATUS=scripts_root_tooling_gap_recorded`",
    "`scripts/zigux/README.md`",
    "`scripts\\zigux/check_phase15_scripts_readme_alignment.zig`",
    "`scripts\\zigux/validate_phase15.zig`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_architecture_council_review_process_manifest.json`",
    "`Documentation/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
};

const SCRIPTS_README_PATH = "scripts/zigux/README.md";

const TESTS_MARKERS = [_][]const u8{
    "scripts\\zigux/check_phase15_scripts_readme_alignment.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
};

const TESTS_README_PATH = "zigux/tests/README.md";

fn collectFailures(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
) !std.ArrayList([]const u8) {
    var failures: std.ArrayList([]const u8) = .empty;
    errdefer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (DOCS_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (TESTS_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (ALIGNMENT_CHECKER_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        const text = guard.readUtf8File(io, allocator, full_path) catch |err| switch (err) {
            guard.GuardError.IOError => {
                const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
                try failures.append(allocator, issue);
                return failures;
            },
            else => return err,
        };
        defer allocator.free(text);
        for (REQUIRED_GAP_NOTE_MARKERS) |marker| {
            if (std.mem.indexOf(u8, text, marker) == null) {
                const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
                try failures.append(allocator, issue);
            }
        }
    }

    return failures;
}

pub fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "selftest");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);
    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (DOCS_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (TESTS_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (ALIGNMENT_CHECKER_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "Documentation/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (REQUIRED_GAP_NOTE_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_SCRIPTS_ROOT_TOOLING_GAP_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var explicit_root: ?[]const u8 = null;
    var self_test = false;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = if (explicit_root) |value| value else try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);

    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }

    if (failures.items.len > 0) {
        try guard.printLine(io, "PHASE15_SCRIPTS_ROOT_TOOLING_GAP_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

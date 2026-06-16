// Ported from check-phase15-validator-gap-packet.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE15_VALIDATOR_GAP_PACKET_SELF_TEST=pass";

const BUILD_PATH = "zigux/tests/phase15_build.zig";

const DOCS_README_PATH = "Documentation/zigux/README.md";

const EXPECTED_MISSING_PATHS = [_][]const u8{
    "scripts\\zigux/validate_phase15.zig",
    "zigux/tests/phase15_build.zig",
};

const HANDOFF_NOTE_PATH = "Documentation/zigux/phase15-handoff-next-steps-survey.md";

const MAKEFILE_PATH = "zigux/Makefile";

const READINESS_MANIFEST_PATH = "zigux/tests/phase15_readiness_gate_manifest.json";

const READINESS_NOTE_PATH = "Documentation/zigux/phase15-readiness-gate-survey.md";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-shared-summary-gap.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/tests/phase15_readiness_gate_manifest.json",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
};

const REQUIRED_MARKERS_ENTRIES = [_]struct { file: []const u8, marker: []const u8 }{
    .{ .file = "Documentation/zigux/README.md", .marker = "`scripts\\zigux/validate_phase15.zig` and `zigux/tests/phase15_build.zig` still belong to the broader validator-first and dedicated-build reminder family" },
    .{ .file = "Documentation/zigux/README.md", .marker = "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`" },
    .{ .file = "Documentation/zigux/README.md", .marker = "`.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route" },
    .{ .file = "Documentation/zigux/review-checklist.md", .marker = "keep `scripts\\zigux/validate_phase15.zig`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes framed as repo-reality gaps" },
    .{ .file = "Documentation/zigux/phase15-readiness-gate-survey.md", .marker = "the missing validator, build, and workflow companions still block any claim that the broader Phase 15 replay route is fully ready" },
    .{ .file = "Documentation/zigux/phase15-readiness-gate-survey.md", .marker = "`scripts\\zigux/validate_phase15.zig`" },
    .{ .file = "Documentation/zigux/phase15-readiness-gate-survey.md", .marker = "`zigux/tests/phase15_build.zig`" },
    .{ .file = "Documentation/zigux/phase15-readiness-gate-survey.md", .marker = "`make -C zigux phase15-validate` remains blocked route vocabulary" },
    .{ .file = "Documentation/zigux/phase15-shared-summary-gap.md", .marker = "## Still-missing broader validator-first companions on current master" },
    .{ .file = "Documentation/zigux/phase15-shared-summary-gap.md", .marker = "`scripts\\zigux/validate_phase15.zig`" },
    .{ .file = "Documentation/zigux/phase15-shared-summary-gap.md", .marker = "`zigux/tests/phase15_build.zig`" },
    .{ .file = "Documentation/zigux/phase15-shared-summary-gap.md", .marker = "broader validator-first wording around `scripts\\zigux/validate_phase15.zig`, `zigux/tests/phase15_build.zig`, and the parked `make -C zigux phase15-validate`, `make -C zigux phase15-test`, and `make -C zigux phase15` routes" },
    .{ .file = "Documentation/zigux/phase15-handoff-next-steps-survey.md", .marker = "no broader validator-first companion `scripts\\zigux/validate_phase15.zig` is directly materialized on current `master`" },
    .{ .file = "Documentation/zigux/phase15-handoff-next-steps-survey.md", .marker = "no dedicated shared Phase 15 build replay `zigux/tests/phase15_build.zig` is directly materialized on current `master`" },
    .{ .file = "Documentation/zigux/phase15-handoff-next-steps-survey.md", .marker = "no directly readable `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15` route body is materialized on current `master`" },
    .{ .file = "scripts/zigux/README.md", .marker = "`scripts\\zigux/validate_phase15.zig` and `zigux/tests/phase15_build.zig` still belong to the broader validator-first and dedicated-build reminder family" },
    .{ .file = "scripts/zigux/README.md", .marker = "although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`" },
    .{ .file = "scripts/zigux/README.md", .marker = "`.github/workflows/zigux-bootstrap.yml` is present on current `master`, but it still carries no dedicated Phase 15 validate, test, or aggregate route" },
    .{ .file = "zigux/tests/README.md", .marker = "Current `master` still does not materialize `scripts\\zigux/validate_phase15.zig` or `zigux/tests/phase15_build.zig`, so keep those broader validator-first and build-route companions framed as repo-reality gaps" },
    .{ .file = "zigux/tests/README.md", .marker = "Although `zigux/Makefile` is present on current `master`, it still does not materialize `make -C zigux phase15-validate`, `make -C zigux phase15-test`, or `make -C zigux phase15`" },
};

const REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md";

const SCRIPTS_README_PATH = "scripts/zigux/README.md";

const SHARED_GAP_PATH = "Documentation/zigux/phase15-shared-summary-gap.md";

const TESTS_README_PATH = "zigux/tests/README.md";

const VALIDATOR_PATH = "scripts\\zigux/validate_phase15.zig";

const WORKFLOW_FORBIDDEN_MARKERS = [_][]const u8{
    "validate-phase15.py",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
};

const WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml";

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
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/review-checklist.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/phase15-readiness-gate-survey.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/phase15-shared-summary-gap.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/phase15-handoff-next-steps-survey.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "scripts/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "zigux/tests/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "zigux/tests/phase15_readiness_gate_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "zigux/Makefile";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = ".github/workflows/zigux-bootstrap.yml";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

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
        for (WORKFLOW_FORBIDDEN_MARKERS) |marker| {
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
        for (REQUIRED_MARKERS) |marker| {
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
        for (WORKFLOW_FORBIDDEN_MARKERS) |marker| {
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
        for (REQUIRED_MARKERS) |marker| {
            try content.appendSlice(allocator, marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "Documentation/zigux/review-checklist.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "Documentation/zigux/phase15-readiness-gate-survey.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "Documentation/zigux/phase15-shared-summary-gap.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "Documentation/zigux/phase15-handoff-next-steps-survey.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "scripts/zigux/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "zigux/tests/README.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "zigux/tests/phase15_readiness_gate_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = "zigux/Makefile";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    {
        const relative_path = ".github/workflows/zigux-bootstrap.yml";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        try guard.writeUtf8File(io, full_path, "\n");
    }
    var failures = try collectFailures(io, allocator, root);
    defer {
        for (failures.items) |item| allocator.free(item);
        failures.deinit(allocator);
    }
    try guard.expectSelfTest(failures.items.len == 0);
    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_VALIDATOR_GAP_PACKET_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE15_VALIDATOR_GAP_PACKET_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    try guard.printLine(io, "PHASE15_VALIDATOR_GAP_PACKET_REQUIRED_FILE_COUNT={d}", .{@as(usize, REQUIRED_FILES.len)});
    std.process.exit(0);
}

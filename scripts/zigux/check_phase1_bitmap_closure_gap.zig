// Ported from check-phase1-bitmap-closure-gap.py by port_phase1_guards.py
const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE1_BITMAP_CLOSURE_GAP_CHECK_SELF_TEST=pass";

const CLOSURE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "closure_validator", .marker = "- `PHASE1_CLOSURE_VALIDATOR=zig run scripts/zigux/validate_phase1_closure.zig`" },
    .{ .label = "next_safe_step", .marker = "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, closure validator, shared tests-root smoke route, and the helper-specific next_safe_step_note entries in zigux/tests/fixtures/phase1_helper_manifest.json`" },
};

const CLOSURE_NOTE_REL = "Documentation/zigux/phase1-closure.md";

const EXPECTED_BITMAP_PACKET = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "first_word_boundary_anchor", .marker = "test \"bitmap range helpers preserve edges across whole-word spans\"" },
    .{ .label = "final_partial_word_anchor", .marker = "test \"bitmap range helpers preserve edges across whole-word spans\"" },
    .{ .label = "fill_tail_clamp_anchor", .marker = "test \"bitmap full empty and weight ignore out-of-range tail bits\"" },
    .{ .label = "predicate_tail_mask_anchor", .marker = "test \"bitmap tail-masked helpers ignore out-of-range differences\"" },
    .{ .label = "zero_bit_noop_anchor", .marker = "" },
    .{ .label = "linux_alias_anchor", .marker = "" },
    .{ .label = "next_safe_step_note", .marker = "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors here, while zero-bit and Linux-style alias follow-through no longer live in the helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through." },
};

const LANE_MARKERS = [_]struct { label: []const u8, marker: []const u8 }{
    .{ .label = "bitmap_direct_owner", .marker = "- `tools/lib/bitmap.zig` owns its helper-local bitmap anchors and the committed bitmap replay keys in `zigux/tests/fixtures/phase1_helpers.json`." },
    .{ .label = "bitmap_next_safe_step", .marker = "- `PHASE1_BITMAP_NEXT_SAFE_STEP=bitmap stays parked unless a fresh reread finds new direct-anchor drift or committed shared replay drift; do not reopen older closure-side or validator-route cue names by default`" },
};

const LANE_NOTE_REL = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";

const MANIFEST_REL = "zigux/tests/fixtures/phase1_helper_manifest.json";

const REQUIRED_FILES = [_][]const u8{
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/phase1-closure.md",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
};

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
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "Documentation/zigux/phase1-closure.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        if (!guard.pathExists(io, full_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{relative_path});
            try failures.append(allocator, issue);
        }
    }
    if (failures.items.len > 0) return failures;

    {
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
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
        for (LANE_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:{s}:actual_count={d}", .{ entry.label, entry.marker, count });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "Documentation/zigux/phase1-closure.md";
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
        for (CLOSURE_MARKERS) |entry| {
            const count = guard.countOccurrences(text, entry.marker);
            if (count != 1) {
                const issue = try std.fmt.allocPrint(allocator, "{s}:expected_once:{s}:actual_count={d}", .{ entry.label, entry.marker, count });
                try failures.append(allocator, issue);
            }
        }
    }

    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
        const parsed = try guard.parseJsonValue(allocator, text);
        defer parsed.deinit();
        if (guard.nestedJsonValue(parsed.value, &[_][]const u8{"status"}) orelse null) |value| {
            if (value != .string or !std.mem.eql(u8, value.string, "closed")) {
                const issue = try std.fmt.allocPrint(allocator, "manifest.status:expected={s}:actual={s}", .{ "closed", if (value == .string) value.string else "non_string" });
                try failures.append(allocator, issue);
            }
        } else {
            const issue = try std.fmt.allocPrint(allocator, "manifest.status:expected={s}:actual=null", .{"closed"});
            try failures.append(allocator, issue);
        }
        if (guard.nestedJsonValue(parsed.value, &[_][]const u8{"helper_count"}) orelse null) |value| {
            if (value != .integer or value.integer != 13) {
                const issue = try std.fmt.allocPrint(allocator, "manifest.helper_count:expected=13:actual={d}", .{if (value == .integer) @as(i64, value.integer) else @as(i64, 0)});
                try failures.append(allocator, issue);
            }
        } else {
            const issue = try std.fmt.allocPrint(allocator, "manifest.helper_count:expected=13:actual=null", .{});
            try failures.append(allocator, issue);
        }
        const packet_0_step_0 = guard.nestedJsonValue(parsed.value, &[_][]const u8{"review_anchors"});
        if (packet_0_step_0) |value_0| {
            const packet_0_step_1 = guard.nestedJsonValue(value_0, &[_][]const u8{"tools/lib/bitmap.zig"});
            if (packet_0_step_1) |value_1| {
                if (value_1 != .object) {
                    const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap_packet:missing", .{});
                    try failures.append(allocator, issue);
                } else {
                    { const actual = value_1.object.get("first_word_boundary_anchor") orelse null;
                      const ok = if (actual) |value| value == .string and std.mem.eql(u8, value.string, "test \"bitmap range helpers preserve edges across whole-word spans\"") else @as(bool, false);
                      if (!ok) {
                          const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap.first_word_boundary_anchor:expected={s}:actual={s}", .{ "test \"bitmap range helpers preserve edges across whole-word spans\"", if (actual) |value| if (value == .string) value.string else "non_string" else "null" });
                          try failures.append(allocator, issue);
                      } }
                    { const actual = value_1.object.get("final_partial_word_anchor") orelse null;
                      const ok = if (actual) |value| value == .string and std.mem.eql(u8, value.string, "test \"bitmap range helpers preserve edges across whole-word spans\"") else @as(bool, false);
                      if (!ok) {
                          const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap.final_partial_word_anchor:expected={s}:actual={s}", .{ "test \"bitmap range helpers preserve edges across whole-word spans\"", if (actual) |value| if (value == .string) value.string else "non_string" else "null" });
                          try failures.append(allocator, issue);
                      } }
                    { const actual = value_1.object.get("fill_tail_clamp_anchor") orelse null;
                      const ok = if (actual) |value| value == .string and std.mem.eql(u8, value.string, "test \"bitmap full empty and weight ignore out-of-range tail bits\"") else @as(bool, false);
                      if (!ok) {
                          const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap.fill_tail_clamp_anchor:expected={s}:actual={s}", .{ "test \"bitmap full empty and weight ignore out-of-range tail bits\"", if (actual) |value| if (value == .string) value.string else "non_string" else "null" });
                          try failures.append(allocator, issue);
                      } }
                    { const actual = value_1.object.get("predicate_tail_mask_anchor") orelse null;
                      const ok = if (actual) |value| value == .string and std.mem.eql(u8, value.string, "test \"bitmap tail-masked helpers ignore out-of-range differences\"") else @as(bool, false);
                      if (!ok) {
                          const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap.predicate_tail_mask_anchor:expected={s}:actual={s}", .{ "test \"bitmap tail-masked helpers ignore out-of-range differences\"", if (actual) |value| if (value == .string) value.string else "non_string" else "null" });
                          try failures.append(allocator, issue);
                      } }
                    { const actual = value_1.object.get("zero_bit_noop_anchor") orelse null;
                      const ok = if (actual) |value| value == .string and std.mem.eql(u8, value.string, "") else @as(bool, true);
                      if (!ok) {
                          const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap.zero_bit_noop_anchor:expected={s}:actual={s}", .{ "", if (actual) |value| if (value == .string) value.string else "non_string" else "null" });
                          try failures.append(allocator, issue);
                      } }
                    { const actual = value_1.object.get("linux_alias_anchor") orelse null;
                      const ok = if (actual) |value| value == .string and std.mem.eql(u8, value.string, "") else @as(bool, true);
                      if (!ok) {
                          const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap.linux_alias_anchor:expected={s}:actual={s}", .{ "", if (actual) |value| if (value == .string) value.string else "non_string" else "null" });
                          try failures.append(allocator, issue);
                      } }
                    { const actual = value_1.object.get("next_safe_step_note") orelse null;
                      const ok = if (actual) |value| value == .string and std.mem.eql(u8, value.string, "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors here, while zero-bit and Linux-style alias follow-through no longer live in the helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through.") else @as(bool, false);
                      if (!ok) {
                          const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap.next_safe_step_note:expected={s}:actual={s}", .{ "If this helper lane reopens, keep bitmap parked unless a fresh reread finds new direct-anchor drift inside the current helper-local packet or committed shared replay drift in the bitmap parity fields; current master still ships direct fill-tail clamp, copy-alias, truncation, cross-word scnprintf, empty-buffer, and allocator-reset anchors here, while zero-bit and Linux-style alias follow-through no longer live in the helper-local packet, and if the separate bitmap closure-validator anchor-sync repair is still outstanding, treat that as the only other bitmap follow-through.", if (actual) |value| if (value == .string) value.string else "non_string" else "null" });
                          try failures.append(allocator, issue);
                      } }
                }
            } else {
                const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap_packet:missing", .{});
                try failures.append(allocator, issue);
            }
        } else {
            const issue = try std.fmt.allocPrint(allocator, "manifest.bitmap_packet:missing", .{});
            try failures.append(allocator, issue);
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
        const relative_path = "Documentation/zigux/phase1-host-helper-lane-sequencing.md";
        const full_path = try guard.joinPath(allocator, root, relative_path);
        defer allocator.free(full_path);
        var content = std.ArrayList(u8).empty;
        defer content.deinit(allocator);
        for (LANE_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        for (CLOSURE_MARKERS) |entry| {
            try content.appendSlice(allocator, entry.marker);
            try content.append(allocator, '\n');
        }
        try guard.writeUtf8File(io, full_path, content.items);
    }
    {
        const relative_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
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
    try guard.printLine(io, "PHASE1_BITMAP_CLOSURE_GAP_CHECK_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
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
        try guard.printLine(io, "PHASE1_BITMAP_CLOSURE_GAP_CHECK_SELF_TEST=fail", .{});
        for (failures.items) |failure| try guard.printLine(io, "{s}", .{failure});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
    std.process.exit(0);
}

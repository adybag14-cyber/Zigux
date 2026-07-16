const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT=pass";
pub const self_test_pass_marker = "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_SELF_TEST=pass";

const README_MARKERS = [_][]const u8{
    "`zigux-alpha` is the Zigux bootstrap workspace.",
    "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "`Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.",
    "`Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.",
    "`scripts/zigux/check_lane01_bootstrap_charter_alignment.zig` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.",
    "[Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)",
    "[Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)",
};

const ROADMAP_MARKERS = [_][]const u8{
    "## Bootstrap Status Note",
    "This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.",
    "confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.",
    "starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.",
};

const LEDGER_MARKERS = [_][]const u8{
    "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    "## Scope Note",
    "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.",
    "Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.",
};

const sample_readme =
    \\# zigux-alpha
    \\
    \\`zigux-alpha` is the Zigux bootstrap workspace.
    \\
    \\Rules
    \\- Keep product planning and bootstrap artifacts here first.
    \\- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
    \\- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.
    \\
    \\Active product surfaces
    \\- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
    \\- `Documentation/zigux/freeze-map.md` is the live freeze-anchor root for stay-in-C and study-only boundaries.
    \\- `scripts/zigux/check_lane01_bootstrap_charter_alignment.zig` is the shipped bootstrap-charter guard for the planning-only `zigux-alpha/` packet.
    \\
    \\Start here
    \\- [Bootstrap Commit Ledger](./BOOTSTRAP_COMMIT_LEDGER.md)
    \\- [Freeze Governance Companion](../Documentation/zigux/phase15-freeze-map-governance.md)
    \\
;

const sample_roadmap =
    \\# ZAR to Zigux Product Roadmap
    \\
    \\## Purpose
    \\
    \\This document turns the `zigux_bundle_v2.zip` planning bundle into an actionable product roadmap for Zigux.
    \\
    \\## Bootstrap Status Note
    \\
    \\This roadmap remains the planning baseline for Zigux bootstrap sequencing and phase intent.
    \\
    \\For later-lane current-state decisions after the bounded early commit train recorded in `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`, confirm the live repo tree, `Documentation/zigux/README.md`, and active lane notes before treating every later phase packet below as already materialized on `master`.
    \\
    \\This roadmap is written for commit-and-push execution inside `Zigux`, starting in `zigux-alpha/` and then expanding into the real product locations as phases are approved.
    \\
;

const sample_ledger =
    \\# Zigux Alpha Bootstrap Commit Ledger
    \\
    \\25. `docs(zigux): reopen and close broadened Phase 2 tranche`
    \\
    \\## Scope Note
    \\
    \\- This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.
    \\- Later lane-level expansion stays traceable through the roadmap, the live repo, and current lane notes until a reviewed continuation of this ledger lands.
    \\
;

fn collectMissingMarkers(allocator: std.mem.Allocator, readme: []const u8, roadmap: []const u8, ledger: []const u8) !std.ArrayList([]const u8) {
    var missing = try std.ArrayList([]const u8).initCapacity(allocator, 8);
    for (README_MARKERS) |marker| {
        if (std.mem.indexOf(u8, readme, marker) == null) {
            const msg = try std.fmt.allocPrint(allocator, "readme:{s}", .{marker});
            try missing.append(allocator, msg);
        }
    }
    for (ROADMAP_MARKERS) |marker| {
        if (std.mem.indexOf(u8, roadmap, marker) == null) {
            const msg = try std.fmt.allocPrint(allocator, "roadmap:{s}", .{marker});
            try missing.append(allocator, msg);
        }
    }
    for (LEDGER_MARKERS) |marker| {
        if (std.mem.indexOf(u8, ledger, marker) == null) {
            const msg = try std.fmt.allocPrint(allocator, "ledger:{s}", .{marker});
            try missing.append(allocator, msg);
        }
    }
    return missing;
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var case_count: usize = 0;
    var good_missing = try collectMissingMarkers(allocator, sample_readme, sample_roadmap, sample_ledger);
    defer {
        for (good_missing.items) |item| allocator.free(item);
        good_missing.deinit(allocator);
    }
    if (good_missing.items.len != 0) return error.SelfTestFailed;
    case_count += 1;

    const bad_readme = try std.mem.replaceOwned(u8, allocator, sample_readme, README_MARKERS[1], "");
    defer allocator.free(bad_readme);
    var bad_missing = try collectMissingMarkers(allocator, bad_readme, sample_roadmap, sample_ledger);
    defer {
        for (bad_missing.items) |item| allocator.free(item);
        bad_missing.deinit(allocator);
    }
    if (bad_missing.items.len != 1) return error.SelfTestFailed;
    case_count += 1;

    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "LANE01_BOOTSTRAP_CHARTER_ALIGNMENT_SELF_TEST_CASES={d}", .{case_count});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var repo_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
        if (std.mem.eql(u8, arg, "--root")) {
            index += 1;
            if (index >= args.len) std.process.exit(2);
            repo_root = args[index];
        }
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = repo_root orelse try guard.repoRootFromScript(allocator);
    defer if (repo_root == null) allocator.free(root);

    const readme_path = try guard.joinPath(allocator, root, "zigux-alpha/README.md");
    defer allocator.free(readme_path);
    const readme = try guard.readUtf8File(io, allocator, readme_path);
    defer allocator.free(readme);

    const roadmap_path = try guard.joinPath(allocator, root, "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");
    defer allocator.free(roadmap_path);
    const roadmap = try guard.readUtf8File(io, allocator, roadmap_path);
    defer allocator.free(roadmap);

    const ledger_path = try guard.joinPath(allocator, root, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger_path);
    const ledger = try guard.readUtf8File(io, allocator, ledger_path);
    defer allocator.free(ledger);

    var missing = try collectMissingMarkers(allocator, readme, roadmap, ledger);
    defer {
        for (missing.items) |item| allocator.free(item);
        missing.deinit(allocator);
    }
    if (missing.items.len != 0) {
        for (missing.items) |item| try guard.printLine(io, "ERROR: {s}", .{item});
        std.process.exit(1);
    }
    try guard.printLine(io, "Lane 01 bootstrap charter alignment check passed.", .{});
}
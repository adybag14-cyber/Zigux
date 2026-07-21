const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

const DOC_REL = "Documentation/zigux/phase2-scripts-root-tooling-inventory.md";
const MANIFEST_REL = "zigux/tests/fixtures/phase2_scripts_root_tooling_inventory.json";

const REQUIRED_DOC_MARKERS = [_][]const u8{
    "# Phase 2 Scripts-Root Tooling Inventory",
    "## Review Surfaces",
    "## Tooling Surfaces",
    "## Fixtures And Manifests",
    "## Replay Commands",
    "## Boundary",
    "scripts/zigux/README.md",
    "bounded Phase 2 checklist for toolchain pinning, local-first archive bootstrap, kbuild, kconfig, genksyms, fixdep, cross-route, manifest, and make-wrapper follow-through.",
};

fn requireStringList(payload: std.json.ObjectMap, key: []const u8) ![]const []const u8 {
    const value = payload.get(key) orelse return error.InvalidManifest;
    const array = switch (value) {
        .array => |items| items,
        else => return error.InvalidManifest,
    };
    if (array.items.len == 0) return error.InvalidManifest;
    const out = try std.heap.page_allocator.alloc([]const u8, array.items.len);
    for (array.items, 0..) |item, index| {
        out[index] = switch (item) {
            .string => |text| text,
            else => return error.InvalidManifest,
        };
    }
    return out;
}

fn validate(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const doc_path = try guard.joinPath(allocator, root, DOC_REL);
    defer allocator.free(doc_path);
    const manifest_path = try guard.joinPath(allocator, root, MANIFEST_REL);
    defer allocator.free(manifest_path);

    const doc_text = try guard.readUtf8File(io, allocator, doc_path);
    defer allocator.free(doc_text);

    const manifest_text = try guard.readUtf8File(io, allocator, manifest_path);
    defer allocator.free(manifest_text);
    const parsed = try guard.parseJsonValue(allocator, manifest_text);
    defer parsed.deinit();
    const payload = switch (parsed.value) {
        .object => |object| object,
        else => return error.InvalidManifest,
    };

    const phase = payload.get("phase") orelse return error.InvalidManifest;
    if (!guard.jsonValuesEqual(phase, .{ .string = "Phase 2" })) return error.InvalidManifest;
    const status = payload.get("status") orelse return error.InvalidManifest;
    if (!guard.jsonValuesEqual(status, .{ .string = "active" })) return error.InvalidManifest;
    const focus = payload.get("focus") orelse return error.InvalidManifest;
    if (!guard.jsonValuesEqual(focus, .{ .string = "scripts-root repo tooling inventory" })) return error.InvalidManifest;

    const surfaces = try requireStringList(payload, "surfaces");
    defer std.heap.page_allocator.free(surfaces);
    const commands = try requireStringList(payload, "commands");
    defer std.heap.page_allocator.free(commands);

    for (REQUIRED_DOC_MARKERS) |marker| {
        if (std.mem.indexOf(u8, doc_text, marker) == null) {
            try guard.printLine(io, "inventory note missing required markers: {s}", .{marker});
            return error.ValidationFailed;
        }
    }

    for (surfaces) |surface| {
        const surface_path = try guard.joinPath(allocator, root, surface);
        defer allocator.free(surface_path);
        if (!guard.pathExists(io, surface_path)) {
            try guard.printLine(io, "inventory manifest references missing surfaces: {s}", .{surface});
            return error.ValidationFailed;
        }
    }

    for (surfaces) |surface| {
        const mention = try std.fmt.allocPrint(allocator, "`{s}`", .{surface});
        defer allocator.free(mention);
        if (std.mem.indexOf(u8, doc_text, mention) == null) {
            try guard.printLine(io, "inventory note missing surface mentions: {s}", .{surface});
            return error.ValidationFailed;
        }
    }

    for (commands) |command| {
        const mention = try std.fmt.allocPrint(allocator, "`{s}`", .{command});
        defer allocator.free(mention);
        if (std.mem.indexOf(u8, doc_text, mention) == null) {
            try guard.printLine(io, "inventory note missing command mentions: {s}", .{command});
            return error.ValidationFailed;
        }
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !void {
    var tmp = try guard.TempWorkspace.init(io, allocator, "p2_scripts_root_inventory");
    defer tmp.deinit();
    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);

    const manifest_json =
        \\{
        \\  "phase": "Phase 2",
        \\  "status": "active",
        \\  "focus": "scripts-root repo tooling inventory",
        \\  "surfaces": [
        \\    "Documentation/zigux/phase2-closure.md",
        \\    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        \\    "Documentation/zigux/review-checklist.md",
        \\    "scripts/zigux/README.md",
        \\    "zigux/tests/README.md",
        \\    "scripts\\zigux/check_zig_toolchain.zig",
        \\    "scripts\\zigux/check_phase2_kbuild_routes.zig",
        \\    "scripts\\zigux/check_phase2_tool_manifest.zig",
        \\    "zigux/tests/fixtures/phase2_tool_manifest.json",
        \\    "zigux/Makefile",
        \\    "third_party/README.md",
        \\    "third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz"
        \\  ],
        \\  "commands": [
        \\    "zig run scripts/zigux/check_phase2_scripts_root_tooling_inventory.zig -- --self-test",
        \\    "zig run scripts/zigux/check_phase2_scripts_root_tooling_inventory.zig",
        \\    "make -C zigux phase2-toolchain",
        \\    "make -C zigux phase2-validate",
        \\    "make -C zigux phase2"
        \\  ]
        \\}
        \\
    ;

    const doc_text =
        \\# Phase 2 Scripts-Root Tooling Inventory
        \\
        \\This note keeps the current Phase 2 repo-tooling packet explicit from the scripts root.
        \\
        \\## Review Surfaces
        \\
        \\- `Documentation/zigux/phase2-closure.md`
        \\- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
        \\- `Documentation/zigux/review-checklist.md`
        \\- `scripts/zigux/README.md`
        \\- `zigux/tests/README.md`
        \\
        \\## Tooling Surfaces
        \\
        \\- `scripts\zigux/check_zig_toolchain.zig`
        \\- `scripts\zigux/check_phase2_kbuild_routes.zig`
        \\- `scripts\zigux/check_phase2_tool_manifest.zig`
        \\
        \\## Fixtures And Manifests
        \\
        \\- `zigux/tests/fixtures/phase2_tool_manifest.json`
        \\- `third_party/README.md`
        \\- `third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz`
        \\- `zigux/Makefile`
        \\
        \\## Replay Commands
        \\
        \\- `zig run scripts/zigux/check_phase2_scripts_root_tooling_inventory.zig -- --self-test`
        \\- `zig run scripts/zigux/check_phase2_scripts_root_tooling_inventory.zig`
        \\- `make -C zigux phase2-toolchain`
        \\- `make -C zigux phase2-validate`
        \\- `make -C zigux phase2`
        \\
        \\## Boundary
        \\
        \\`scripts/zigux/README.md` remains the broader scripts-root reminder surface. This inventory is the bounded Phase 2 checklist for toolchain pinning, local-first archive bootstrap, kbuild, kconfig, genksyms, fixdep, cross-route, manifest, and make-wrapper follow-through.
        \\
    ;

    const parsed = try guard.parseJsonValue(allocator, manifest_json);
    defer parsed.deinit();
    const surfaces = switch (parsed.value) {
        .object => |object| try requireStringList(object, "surfaces"),
        else => return error.InvalidManifest,
    };
    defer std.heap.page_allocator.free(surfaces);

    for (surfaces) |surface| {
        if (std.mem.endsWith(u8, surface, ".json")) {
            try tmp.write(surface, "{}\n");
        } else {
            try tmp.write(surface, "stub\n");
        }
    }
    try tmp.write(MANIFEST_REL, manifest_json);
    try tmp.write(DOC_REL, doc_text);
    try validate(io, allocator, root);
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) {
        runSelfTest(io, allocator) catch std.process.exit(1);
        return;
    }

    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    validate(io, allocator, root) catch std.process.exit(1);
}
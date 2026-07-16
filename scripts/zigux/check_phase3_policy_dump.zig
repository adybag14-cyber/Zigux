const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_POLICY_DUMP=pass";
pub const self_test_pass_marker = "PHASE3_POLICY_DUMP_SELF_TEST=pass";

const FileContract = struct { rel: []const u8, markers: []const []const u8 };

const markers_0 = [_][]const u8{
    "zigux/tests/phase3_policy_dump.zig",
    "zigux/tests/phase3_policy_dump_build.zig",
    "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "make -C zigux phase3-policy-dump",
    "make -C zigux phase3",
};

const markers_1 = [_][]const u8{
    "safe-default",
    "mmio-bug",
    "raw-bridge-warn",
    "reserved-invalid",
    "panic={s}",
    "allocator={s}",
    "bridge_read_ok={any}",
    "bridge_write_ok={any}",
    "std.debug.print(",
};

const markers_2 = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../helpers/panic_policy.zig\"),",
    ".root_source_file = b.path(\"../helpers/allocator_policy.zig\"),",
    ".root_source_file = b.path(\"../helpers/unsafe_policy.zig\"),",
    ".root_source_file = b.path(\"../unsafe/narrow.zig\"),",
    ".root_source_file = b.path(\"phase3_policy_dump.zig\"),",
    "\"phase3-policy-dump\"",
};

const markers_3 = [_][]const u8{
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
    "phase3-policy-dump:",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
};

const markers_4 = [_][]const u8{
    "Run current Phase 3 policy dump replay",
    "run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "Run current Phase 3 policy dump make wrapper",
    "run: make -C zigux phase3-policy-dump",
};

const markers_5 = [_][]const u8{
    "safe-default|panic=abort|allocator=caller_provided",
    "mmio-bug|panic=bug|allocator=kernel_heap",
    "raw-bridge-warn|panic=warn|allocator=arena",
    "reserved-invalid|panic=invalid|allocator=invalid",
};

const contracts = [_]FileContract{
    .{ .rel = "Documentation/zigux/phase3-policy-slice.md", .markers = &markers_0 },
    .{ .rel = "zigux/tests/phase3_policy_dump.zig", .markers = &markers_1 },
    .{ .rel = "zigux/tests/phase3_policy_dump_build.zig", .markers = &markers_2 },
    .{ .rel = "zigux/Makefile", .markers = &markers_3 },
    .{ .rel = ".github/workflows/zigux-bootstrap.yml", .markers = &markers_4 },
    .{ .rel = "zigux/tests/fixtures/phase3_policy_dump_expected.txt", .markers = &markers_5 },
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (contracts) |contract| {
        const path = try guard.joinPath(allocator, root, contract.rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        for (contract.markers) |marker| try guard.requireMarker(text, marker);
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE3_POLICY_DUMP_EXPECTED_LINE_COUNT={d}", .{@as(usize, 4)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8,arg,"--self-test")) { self_test=true; continue; }
        if (std.mem.eql(u8,arg,"--root") or std.mem.eql(u8,arg,"--repo-root")) {
            if (index+1>=args.len) std.process.exit(2); index+=1; explicit_root=args[index]; continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io,allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root==null) allocator.free(root);
    checkRepo(io,allocator,root) catch std.process.exit(1);
    try guard.printLine(io,"validated zigux/tests/phase3_policy_dump.zig",.{});
    try guard.printLine(io,"validated zigux/tests/fixtures/phase3_policy_dump_expected.txt",.{});
    try guard.printLine(io,"{s}",.{live_pass_marker});
}

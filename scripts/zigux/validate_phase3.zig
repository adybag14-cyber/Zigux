const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE3_VALIDATION_SELF_TEST=pass";

const manifest_markers = [_][]const u8{
    "\"phase\": \"Phase 3\"",
    "\"status\": \"shared_abi_and_header_family_binding_surface_present\"",
    "\"packet_files\"",
    "\"replay_routes\"",
    "\"next_safe_step\"",
    "keep the shared Phase 3 policy, export/UAPI, low-level wrapper packet, and retired generated-packet guard aligned with the dedicated replay routes and only reopen this manifest if the checker, focused builds, or reminder surfaces drift again",
    "zig run scripts/zigux/check_phase3_abi.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_abi.zig",
    "zig run scripts/zigux/check_phase3_dev_t_starter_packet.zig -- --self-test",
    "zig run scripts/zigux/check_phase3_policy_dump.zig -- --self-test",
    "zig run scripts/zigux/validate_phase3_selftest.zig",
    "zig run scripts/zigux/run_phase3_checks.zig",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const path = try guard.joinPath(allocator, root, "zigux/tests/fixtures/phase3_abi_manifest.json");
    defer allocator.free(path);
    const text = try guard.readUtf8File(io, allocator, path);
    defer allocator.free(text);
    for (manifest_markers) |marker| try guard.requireMarker(text, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE3_VALIDATION_SELF_TEST_CASE_COUNT={d}", .{@as(usize, 1)});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator=init.gpa;
    const io=init.io;
    const args=try init.minimal.args.toSlice(init.arena.allocator());
    var self_test=false;
    var explicit_root:?[]const u8=null;
    var index:usize=1;
    while(index<args.len):(index+=1){
        const arg=args[index];
        if(std.mem.eql(u8,arg,"--self-test")){self_test=true;continue;}
        if(std.mem.eql(u8,arg,"--root") or std.mem.eql(u8,arg,"--repo-root")){
            if(index+1>=args.len) std.process.exit(2); index+=1; explicit_root=args[index]; continue;
        }
        std.process.exit(2);
    }
    if(self_test) std.process.exit(try runSelfTest(io,allocator));
    const root_path=explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if(explicit_root==null) allocator.free(root_path);
    checkRepo(io,allocator,root_path) catch std.process.exit(1);
    try guard.printLine(io,"{s}",.{live_pass_marker});
}

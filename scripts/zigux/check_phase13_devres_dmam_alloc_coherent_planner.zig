const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER_SELF_TEST=pass";

const HELPER_MARKERS = [_][]const u8{
    ".provides_dmam_alloc_coherent_planning = true",
    ".provides_release_record_lifetime_planning = true",
    ".provides_release_call_planning = true",
    ".provides_dmam_free_coherent_cleanup_planning = true",
    ".provides_dmam_detach_cleanup_transition_planning = true",
    "pub fn planManagedReleaseRecordLifetime(retain: bool) ReleaseRecordLifetimePlan",
    "pub fn planManagedReleaseCall(requested_size: u64, release_record_matches: bool) ManagedReleaseCallPlan",
    "pub fn planManagedDmamAllocCoherent(input: ManagedDmamAllocCoherentInput) !ManagedDmamAllocCoherentPlan",
    "pub const ManagedDmamDetachCleanupPlan = struct",
    "pub fn planManagedDmamFreeCoherent(requested_size: u64, release_record_matches: bool) ManagedDmamFreeCoherentPlan",
    "pub fn planManagedDmamDetachCleanup(",
    "const cleanup = planManagedDmamFreeCoherent(allocation_plan.requested_size, release_record_matches);",
    ".release_record_consumed = release_record_matches",
    ".warns_on_release_miss = !release_record_matches",
    ".destroys_release_record_before_free = true",
};

const NOTE_MARKERS = [_][]const u8{
    "lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig`",
    "routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`",
    "promotes the coherent-free release-call shape into explicit shared helper planning through `planManagedReleaseCall(...)`",
    "routes `planManagedDmamFreeCoherent(...)` through that shared release-call helper",
    "turns that successful allocation plan into explicit detach cleanup transition planning through `planManagedDmamDetachCleanup(...)`",
    "routes `planManagedDmamDetachCleanup(...)` through `planManagedDmamFreeCoherent(...)`",
    "records that the planned coherent free destroys the release record before freeing the allocation",
    "zero-sized requests free the release record and avoid retaining detach-time cleanup ownership",
    "`scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig` is the packet-local fail-closed checker",
    "zig run scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig --",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"packet\": \"phase13-devres-dmam-alloc-coherent-planner\"",
    "\"status\": \"starter_landed\"",
    "scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig",
    "\"validation_guard\": \"scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig\"",
    "\"detach_cleanup_transition_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"",
    "\"freed_release_record_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"",
    "\"missing_release_record_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"",
    "\"warn_on_release_miss_owner\": \"zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig\"",
    "provides_release_record_lifetime_planning",
    "provides_release_call_planning",
    "provides_dmam_free_coherent_cleanup_planning",
    "provides_dmam_detach_cleanup_transition_planning",
    "planManagedReleaseRecordLifetime",
    "planManagedReleaseCall",
    "planManagedDmamFreeCoherent",
    "ManagedDmamDetachCleanupPlan",
    "planManagedDmamDetachCleanup",
    "release_record_consumed",
    "warns_on_release_miss",
    "destroys_release_record_before_free",
};

const REPLAY_MARKERS = [_][]const u8{
    "test \"phase13 devres descriptor records helper-first dmam_alloc_coherent planning\" {",
    "try std.testing.expect(descriptor.provides_dmam_detach_cleanup_transition_planning);",
    "test \"phase13 devres exposes shared release-record lifetime planning\" {",
    "test \"phase13 devres exposes shared release-call planning\" {",
    "test \"phase13 devres turns successful coherent-allocation planning into explicit detach cleanup transition planning\" {",
    "const cleanup = devres.DevresHelperLab.planManagedDmamDetachCleanup(plan, true);",
    "test \"phase13 devres keeps detach cleanup transition warnable when the release record is missing\" {",
    "test \"phase13 devres warns when planned coherent free cannot find the devres record\" {",
    "test \"phase13 devres dmam_alloc_coherent planner manifest records the landed helper-first dma scope\" {",
    "test \"phase13 devres dmam_alloc_coherent planner note preserves standalone replay handles\" {",
    "test \"phase13 devres dmam_alloc_coherent checker stays packet-local\" {",
    "try requireContains(note, \"zig run scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig --\");",
    "try requireContains(checker, \"PHASE13_DEVRES_DMAM_ALLOC_COHERENT_PLANNER_SELF_TEST=pass\");",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}

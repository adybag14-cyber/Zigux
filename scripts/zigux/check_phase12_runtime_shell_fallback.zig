const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_RUNTIME_SHELL_FALLBACK_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "RAW_GITHUB_COVERAGE_PATH",
    "WORKFLOW_PATH",
    "MAKEFILE_PATH",
};

const RAW_GITHUB_COVERAGE_MARKERS = [_][]const u8{
    "`PHASE12_STATUS=active`",
    "current contents-bridge shared support bundle during degraded contents reads:",
    "scripts/zigux/check_phase12_cross_compile_smoke.zig",
    "scripts/zigux/check_phase12_libbpf_lane_marker.zig",
    "direct container-side `curl -I -L --fail https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` returns `curl: (22) The requested URL returned error: 403`",
    "same-runtime current-head verification still depends on authenticated GitHub contents readback rather than direct raw URL or clone access.",
    "the contents-bridge support bundle records the workflow-side recovery guard",
    "rebuilds the repo-local `.zig-toolchain` fallback by trying the pinned `third_party` archive first, then the canonical `adybag14-cyber/zig` release, then the Zig community-mirror list, and finally `ziglang.org`",
    "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
    "make -C zigux phase12-smoke ZIG=<attached-zig-path>",
    "make -C zigux phase12-test ZIG=<attached-zig-path>",
    "make -C zigux phase12 ZIG=<attached-zig-path>",
    "This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset",
};

const WORKFLOW_MARKERS = [_][]const u8{
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "zig run scripts/zigux/stage_pinned_zig_archive.zig",
    "if try_local_archive; then",
    "elif try_download \"$ZIGUX_ZIG_CANONICAL_URL\"; then",
    "https://ziglang.org/download/community-mirrors.txt",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
    "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
    "run: make -C zigux phase12",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "ZIG_PINNED_EXECUTABLE :=",
    "ZIG_LOCAL_TOOLCHAIN :=",
    "ZIG_PINNED_TOOLCHAIN :=",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
};

const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
    "phase12: phase12-smoke phase12-test",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (RAW_GITHUB_COVERAGE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
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

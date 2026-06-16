const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_VALIDATE_ROUTE_RETURN_SELF_TEST=pass";

const MAKEFILE_FALLBACK_MARKERS = [_][]const u8{
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
};

const RELEASE_SEQUENCING_MARKERS = [_][]const u8{
    "shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`",
    "If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the shipped `make -C zigux phase12-validate` wrapper explicit ahead of the attached-Zig reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only route, a cross-build route, or another unshipped Phase 12 replay surface.",
    "Current workflow-side fallback recovery evidence: `.github/workflows/zigux-bootstrap.yml` now rebuilds the repo-local `.zig-toolchain` path by first trying the pinned `third_party` archive, then the Zig community-mirror list, and finally `ziglang.org`, so this sequencing note should treat the local Makefile fallback as a restorable local-first path before attached-`ZIG=<attached-zig-path>` reruns rather than as a one-shot cache hit.",
};

const RELEASE_READINESS_MARKERS = [_][]const u8{
    "current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again.",
    "That means the PMO release notes can treat `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while still keeping the validator-first support packet distinct from deeper driver-delivery claims.",
};

const REQUIRED_FILES = [_][]const u8{
    "MAKEFILE_PATH",
    "RELEASE_SEQUENCING_PATH",
    "RELEASE_READINESS_PATH",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "reminder-only `make -C zigux phase12-validate`",
    "reminder-only `make -C zigux phase12-validate`",
};

const MAKEFILE_PATH = [_][]const u8{
    "zigux/Makefile",
};

const RELEASE_SEQUENCING_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-sequencing.md",
};

const RELEASE_READINESS_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-readiness-survey.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (MAKEFILE_FALLBACK_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_PATH) |marker| try guard.requireMarker(text, marker);
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

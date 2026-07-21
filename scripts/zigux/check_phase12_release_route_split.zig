const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE12_RELEASE_ROUTE_SPLIT_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "MAKEFILE_PATH",
    "RELEASE_SEQUENCING_PATH",
    "RELEASE_READINESS_PATH",
    "RELEASE_COORDINATION_PATH",
    "RELEASE_CLOSURE_PATH",
    "LIBBPF_LANE_PATH",
    "RAW_FALLBACK_PATH",
    "BUILD_ONLY_CHECKER_PATH",
    "READINESS_CHECKER_PATH",
    "VALIDATE_PATH",
};

const MAKEFILE_REQUIRED_MARKERS = [_][]const u8{
    ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase3-export-uapi-layout-test phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-checksum-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-test phase6-hexdump-perf phase8-validate phase8-exec-cmd-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test phase8-test phase8 phase10-validate phase10-test phase10 phase12-smoke phase12-test phase12",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-smoke phase12-test",
};

const MAKEFILE_FORBIDDEN_MARKERS = [_][]const u8{
    "phase12-validate:",
};

const RELEASE_SEQUENCING_MARKERS = [_][]const u8{
    "reminder-only wrapper vocabulary until it returns: `make -C zigux phase12-validate`",
    "shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`",
    "shipped wrapper evidence on current `master`: `make -C zigux phase12-test`",
    "shipped wrapper evidence on current `master`: `make -C zigux phase12`",
    "it now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` wrappers again",
    "the directly readable rerun surfaces `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, `scripts\zigux/validate_phase12.zig`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`",
};

const RELEASE_READINESS_MARKERS = [_][]const u8{
    "current `zigux/Makefile` now exposes `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again even though `make -C zigux phase12-validate` is still absent.",
    "That means the PMO release notes can treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-`master` evidence again, while `make -C zigux phase12-validate` must stay reminder-only text until same-lane work rematerializes that wrapper.",
    "keep the intended shared-tree anchor pair `zigux/tests/phase12_build.zig` and `scripts/zigux/check_build_only_phase12_surface.zig` explicit, treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped current-route proof again, and keep only `make -C zigux phase12-validate` framed as reminder-only text while `zigux/Makefile` still omits that wrapper on current `master`.",
};

const RELEASE_COORDINATION_MARKERS = [_][]const u8{
    "validator-first support bundle: `scripts\zigux/validate_phase12.zig`, `scripts/zigux/check_phase12_release_readiness_packet.zig`, and the reminder-only wrapper name `make -C zigux phase12-validate`",
    "`zigux/Makefile` remains directly readable repo evidence and now exposes `phase12-smoke`, `phase12-test`, and `phase12` on `master` while still omitting `phase12-validate`",
    "Current repo-reality override: `zigux/Makefile` now exposes `phase12-smoke`, `phase12-test`, and `phase12` on current `master`, while `phase12-validate` remains reminder-only vocabulary until same-lane work rematerializes that wrapper.",
};

const RELEASE_CLOSURE_MARKERS = [_][]const u8{
    "The directly readable validator-first support bundle still reruns as `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, and `zig run scripts/zigux/validate_phase12.zig`; keep `make -C zigux phase12-validate` here only as reminder-only wrapper vocabulary until `zigux/Makefile` rematerializes that route on current `master`.",
    "The shared build-and-make replay path stays visible through `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`, while current `zigux/Makefile` now keeps `phase12-smoke`, `phase12-test`, and `phase12` explicit as shipped wrapper evidence and still omits `phase12-validate`.",
    "The shared smoke-first replay packet still stays wired through `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`; treat `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` as shipped wrapper evidence again, while `make -C zigux phase12-validate` stays reminder-only vocabulary until that wrapper returns.",
};

const LIBBPF_LANE_MARKERS = [_][]const u8{
    "Current repo-reality override: `zigux/Makefile` now rematerializes `phase12-smoke`, `phase12-test`, and `phase12` on current `master` while still omitting `phase12-validate`, so keep only `make -C zigux phase12-validate` here as reminder vocabulary and keep the directly readable support bundle explicit through `zig run scripts/zigux/check_build_only_phase12_surface.zig -- --self-test`, `zig run scripts/zigux/check_phase12_release_readiness_packet.zig -- --self-test`, and `scripts\zigux/validate_phase12.zig` beside the returned smoke-and-test wrappers.",
    "If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order documented with the reminder-only `make -C zigux phase12-validate` vocabulary ahead of the shipped attached-toolchain reruns `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only fallback entrypoint.",
};

const RAW_FALLBACK_MARKERS = [_][]const u8{
    "the directly readable `zigux/Makefile` blob",
    "now exposes shared `phase12-smoke`, `phase12-test`, and `phase12` again while still omitting `phase12-validate`",
    "keep the current validator-first then smoke-first order explicit through the reminder-only `make -C zigux phase12-validate` vocabulary, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, the shipped wrapper evidence `make -C zigux phase12-test`, and the shipped wrapper evidence `make -C zigux phase12`",
    "keep the same reminder-only validator route plus shipped wrapper reruns explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`",
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

const RELEASE_COORDINATION_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-coordination-matrix.md",
};

const RELEASE_CLOSURE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-release-closure-checklist.md",
};

const LIBBPF_LANE_PATH = [_][]const u8{
    "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
};

const RAW_FALLBACK_PATH = [_][]const u8{
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
};

const BUILD_ONLY_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_build_only_phase12_surface.zig",
};

const READINESS_CHECKER_PATH = [_][]const u8{
    "scripts/zigux/check_phase12_release_readiness_packet.zig",
};

const VALIDATE_PATH = [_][]const u8{
    "scripts\zigux/validate_phase12.zig",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_COORDINATION_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_CLOSURE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_LANE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RAW_FALLBACK_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_SEQUENCING_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_READINESS_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_COORDINATION_PATH) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_CLOSURE_PATH) |marker| try guard.requireMarker(text, marker);
    for (LIBBPF_LANE_PATH) |marker| try guard.requireMarker(text, marker);
    for (RAW_FALLBACK_PATH) |marker| try guard.requireMarker(text, marker);
    for (BUILD_ONLY_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (READINESS_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
    for (VALIDATE_PATH) |marker| try guard.requireMarker(text, marker);
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

const std = @import("std");

const makefile_path = "zigux/Makefile";
const policy_path = "scripts/zigux/zig-toolchain-policy.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    }
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) !void {
    var search_from: usize = 0;
    for (markers) |marker| {
        const relative_index = std.mem.indexOf(u8, haystack[search_from..], marker) orelse {
            std.debug.print("missing ordered marker: {s}\n", .{marker});
            return error.MissingOrderedMarker;
        };
        search_from += relative_index + marker.len;
    }
}

test "phase2 cross Makefile derives pinned Zig path from policy before PATH fallback" {
    const allocator = std.testing.allocator;
    const makefile = try readRepoFile(allocator, makefile_path);
    defer allocator.free(makefile);

    try requireOrdered(makefile, &.{
        "PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json",
        "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"channel\"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
        "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"upgrade_policy\"][\"archive_target_scope\"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
        "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
        "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
        "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
        "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
        "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
        "ZIG_REPO_ROOT := $(if $(ZIG_PINNED_TOOLCHAIN),$(abspath $(ZIG_PINNED_TOOLCHAIN)),$(ZIG))",
        "export PATH := $(ZIG_REPO_ROOT_DIR):$(PATH)",
    });
}

test "phase2 cross Makefile route runs direct checker before alignment checker" {
    const allocator = std.testing.allocator;
    const makefile = try readRepoFile(allocator, makefile_path);
    defer allocator.free(makefile);

    try requireOrdered(makefile, &.{
        "phase2-cross:",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    });
}

test "phase2 cross policy route set stays aligned with Makefile aggregate routes" {
    const allocator = std.testing.allocator;
    const makefile = try readRepoFile(allocator, makefile_path);
    defer allocator.free(makefile);
    const policy = try readRepoFile(allocator, policy_path);
    defer allocator.free(policy);

    try requireContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try requireOrdered(policy, &.{
        "\"archive_sha256\": {",
        "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"",
        "\"archive_target_scope\": [",
        "\"x86_64-linux\"",
        "\"required_make_routes\": [",
        "\"phase2-toolchain\"",
        "\"phase2-tools\"",
        "\"phase2-kconfig\"",
        "\"phase2-cross\"",
        "\"phase2-genksyms\"",
        "\"phase2-fixdep\"",
        "\"phase2-validate\"",
    });

    try requireContains(makefile, "phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");
    try requireContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try requireContains(makefile, "phase2: phase2-validate");
}

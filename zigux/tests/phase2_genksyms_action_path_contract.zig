const std = @import("std");

const workflow = @embedFile("../../.github/workflows/zigux-bootstrap.yml");
const makefile = @embedFile("../Makefile");
const genksyms_checker = @embedFile("../../scripts/zigux/check-genksyms-bridge.py");
const phase2_tool_manifest = @embedFile("fixtures/phase2_tool_manifest.json");

test "phase2 genksyms workflow keeps checker unit and make route ordered" {
    const expected = [_][]const u8{
        "      - name: Self-test current Phase 2 genksyms bridge checker\n        run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
        "      - name: Check current Phase 2 genksyms bridge packet\n        run: python3 scripts/zigux/check-genksyms-bridge.py",
        "      - name: Run current Phase 2 genksyms unit replay\n        run: zig test scripts/zigux/genksyms.zig",
        "      - name: Self-test current Phase 2 genksyms alignment checker\n        run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
        "      - name: Check current Phase 2 genksyms alignment packet\n        run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        "      - name: Run current Phase 2 genksyms make route\n        run: make -C zigux phase2-genksyms",
    };

    var cursor: usize = 0;
    inline for (expected) |marker| {
        const found = std.mem.indexOfPos(u8, workflow, cursor, marker) orelse return error.MissingWorkflowGenksymsActionPathMarker;
        cursor = found + marker.len;
    }

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "run: make -C zigux phase2-genksyms"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(workflow, "run: zig test scripts/zigux/genksyms.zig"));
}

test "phase2 genksyms make route keeps checker local tests and alignment guard" {
    const route = sliceBetween(makefile, "phase2-genksyms: phase2-toolchain", "phase2-fixdep: phase2-toolchain") orelse return error.MissingMakefileGenksymsRoute;
    const expected = [_][]const u8{
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    };

    inline for (expected) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, route, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep") != null);
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(makefile, "phase2-genksyms: phase2-toolchain"));
}

test "phase2 genksyms checker and manifest expose same action packet" {
    const checker_markers = [_][]const u8{
        "GENKSYMS_ZIG = \"scripts/zigux/genksyms.zig\"",
        "VERSION_SIDE_EFFECT_TEST = \"scripts/zigux/genksyms_version_before_invalid_long_option_test.zig\"",
        "AMBIGUOUS_VERSION_SIDE_EFFECT_TEST = \"scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig\"",
        "MANIFEST_FIXTURE = \"zigux/tests/fixtures/genksyms_bridge/manifest.json\"",
    };

    inline for (checker_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, genksyms_checker, marker) != null);
    }

    const manifest_markers = [_][]const u8{
        "\"scripts/zigux/check-genksyms-bridge.py\"",
        "\"scripts/zigux/check-phase2-genksyms-selftest-alignment.py\"",
        "\"scripts/zigux/genksyms.zig\"",
        "\"scripts/zigux/genksyms_version_before_invalid_long_option_test.zig\"",
        "\"scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig\"",
        "\"zigux/tests/fixtures/genksyms_bridge/manifest.json\"",
        "\"make -C zigux phase2-genksyms\"",
    };

    inline for (manifest_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, phase2_tool_manifest, marker) != null);
    }
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, cursor, needle)) |found| {
        count += 1;
        cursor = found + needle.len;
    }
    return count;
}

fn sliceBetween(haystack: []const u8, start: []const u8, end: []const u8) ?[]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return null;
    const after_start = start_index + start.len;
    const end_relative = std.mem.indexOfPos(u8, haystack, after_start, end) orelse return null;
    return haystack[after_start..end_relative];
}

const std = @import("std");

const manifest = @embedFile("fixtures/phase2_tool_manifest.json");

fn expectContains(needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, manifest, needle) != null);
}

test "phase2 tool manifest keeps the action path packet live" {
    if (std.mem.indexOf(u8, manifest, "\"present_surfaces\"") != null) {
        try expectContains("Phase 2");
        try expectContains("scripts/zigux/validate-phase2.py");
        try expectContains("scripts/zigux/validate-phase2-closure.py");
        try expectContains(".github/workflows/zigux-bootstrap.yml");
        try expectContains("scripts/zigux/zig-toolchain-policy.json");
        try expectContains("\"status\": \"active\"");
        try expectContains("\"repo_reality_gaps\": []");
        try expectContains("scripts/zigux/check-phase2-tool-manifest.py");
        try expectContains("scripts/zigux/check-phase2-bootstrap-workflow-routes.py");
        try expectContains("scripts/zigux/check-phase2-required-make-routes.py");
        try expectContains("scripts/zigux/check-phase2-toolchain-pin-scope.py");
        try expectContains("scripts/zigux/stage-pinned-zig-archive.py");
        try expectContains("make -C zigux phase2-toolchain");
        try expectContains("make -C zigux phase2-tools");
        try expectContains("make -C zigux phase2-kconfig");
        try expectContains("make -C zigux phase2-cross");
        try expectContains("make -C zigux phase2-genksyms");
        try expectContains("make -C zigux phase2-fixdep");
        try expectContains("make -C zigux phase2-validate");
        try expectContains("make -C zigux phase2");
    } else {
        try expectContains("\"phase\": \"phase2\"");
        try expectContains("\"packet\": \"phase2_tool_manifest\"");
        try expectContains("\"status\": \"current_master_packet\"");
        try expectContains("scripts/zigux/check-phase2-tool-manifest-packets.py");
        try expectContains("make -C zigux phase2-tools");
        try expectContains("make -C zigux phase2-validate");
    }
}

const std = @import("std");
const contract_options = @import("contract_options");

const workflow_text = contract_options.workflow_text;

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) {
        return error.StaleMarkerPresent;
    }
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !usize {
    const first = try requireContains(haystack, needle);
    const rest = haystack[first + needle.len ..];
    if (std.mem.indexOf(u8, rest, needle) != null) {
        return error.DuplicateMarker;
    }
    return first;
}

fn expectBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try requireContains(haystack, before);
    const after_index = try requireContains(haystack, after);
    try std.testing.expect(before_index < after_index);
}

test "lane07 phase1 shared smoke workflow step stays exact and unique" {
    _ = try expectExactlyOnce(
        workflow_text,
        "      - name: Run current Phase 1 shared tests-root smoke\n",
    );
    _ = try expectExactlyOnce(
        workflow_text,
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    );

    try requireAbsent(
        workflow_text,
        "        run: zig test zigux/tests/phase1_host_tools_smoke.zig\n",
    );
}

test "lane07 phase1 shared smoke remains after phase3 shared gates" {
    try expectBefore(
        workflow_text,
        "      - name: Run current Phase 3 shared tests-root packet\n",
        "      - name: Run current Phase 1 shared tests-root smoke\n",
    );
    try expectBefore(
        workflow_text,
        "      - name: Run current Phase 3 ABI dump replay\n",
        "      - name: Run current Phase 1 shared tests-root smoke\n",
    );
    try expectBefore(
        workflow_text,
        "        run: zig build phase3-test --build-file zigux/tests/build.zig\n",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    );
    try expectBefore(
        workflow_text,
        "        run: zig build phase3-dump --build-file zigux/tests/build.zig\n",
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    );
}

test "lane07 phase1 shared smoke remains before phase4 gates" {
    try expectBefore(
        workflow_text,
        "      - name: Run current Phase 1 shared tests-root smoke\n",
        "      - name: Self-test current Phase 4 repo-reality warning checker\n",
    );
    try expectBefore(
        workflow_text,
        "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
        "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test\n",
    );
    try expectBefore(
        workflow_text,
        "      - name: Run current Phase 1 shared tests-root smoke\n",
        "      - name: Validate Phase 4 rollback routes\n",
    );
}

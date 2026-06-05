const std = @import("std");

const validator_path = "validate-bootstrap.py";
const validator_source = @embedFile(validator_path);

fn requireContains(source: []const u8, marker: []const u8) !void {
    if (std.mem.indexOf(u8, source, marker) == null) {
        std.debug.print("missing marker in {s}: {s}\n", .{ validator_path, marker });
        return error.MissingMarker;
    }
}

fn requireOrdered(source: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, source, before) orelse {
        std.debug.print("missing ordered marker in {s}: {s}\n", .{ validator_path, before });
        return error.MissingMarker;
    };
    const after_index = std.mem.indexOf(u8, source, after) orelse {
        std.debug.print("missing ordered marker in {s}: {s}\n", .{ validator_path, after });
        return error.MissingMarker;
    };
    try std.testing.expect(before_index < after_index);
}

test "bootstrap validator keeps the required path roster closed around Lane 03 toolchain files" {
    const source = validator_source;

    try requireContains(source, "REQUIRED_PATHS = (");
    try requireContains(source, "\"scripts/zigux/check-zig-toolchain.py\",");
    try requireContains(source, "\"scripts/zigux/install-zig.py\",");
    try requireContains(source, "\"scripts/zigux/validate-bootstrap.py\",");
    try requireContains(source, "\"scripts/zigux/zig-toolchain-policy.json\",");
    try requireContains(source, "\"scripts/zigux/stage-pinned-zig-archive.py\",");
    try requireContains(source, "\"scripts/zigux/check-lane05-stage-helper-contract.py\",");
    try requireContains(source, "\"scripts/zigux/check-lane05-stage-helper-selftest.py\",");
    try requireContains(source, "\"scripts/zigux/check-phase1-route-summary-counts.py\",");
    try requireContains(source, "WORKFLOW,");
    try requireContains(source, "\"zigux/tests/README.md\",");

    try requireOrdered(source, "\"scripts/zigux/check-zig-toolchain.py\",", "\"scripts/zigux/install-zig.py\",");
    try requireOrdered(source, "\"scripts/zigux/install-zig.py\",", "\"scripts/zigux/validate-bootstrap.py\",");
    try requireOrdered(source, "\"scripts/zigux/validate-bootstrap.py\",", "\"scripts/zigux/zig-toolchain-policy.json\",");
}

test "required path failures are emitted with stable grouped diagnostics" {
    const source = validator_source;

    try requireContains(source, "issues.append((\"MISSING_REQUIRED_PATH\", rel))");
    try requireContains(source, "print(\"BOOTSTRAP_VALIDATION=fail\")");
    try requireContains(source, "print(f\"{code}_START\")");
    try requireContains(source, "print(f\"{code}_END\")");
    try requireContains(source, "return emit_issues(issues)");
    try requireContains(source, "print(\"BOOTSTRAP_VALIDATION=pass\")");
    try requireContains(source, "print(f\"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}\")");
}

test "validator self-test covers missing bootstrap and toolchain path sentinels" {
    const source = validator_source;

    try requireContains(source, "(root / \"scripts/zigux/check-zig-toolchain.py\").unlink()");
    try requireContains(source, "(\"MISSING_REQUIRED_PATH\", \"scripts/zigux/check-zig-toolchain.py\")");
    try requireContains(source, "(root / \"scripts/zigux/check-phase1-route-summary-counts.py\").unlink()");
    try requireContains(source, "\"scripts/zigux/check-phase1-route-summary-counts.py\",");
    try requireContains(source, "(root / \"scripts/zigux/stage-pinned-zig-archive.py\").unlink()");
    try requireContains(source, "\"scripts/zigux/stage-pinned-zig-archive.py\",");
    try requireContains(source, "(root / \"scripts/zigux/check-lane05-stage-helper-selftest.py\").unlink()");
    try requireContains(source, "\"scripts/zigux/check-lane05-stage-helper-selftest.py\",");
    try requireContains(source, "(root / \"scripts/zigux/install-zig.py\").unlink()");
    try requireContains(source, "(\"MISSING_REQUIRED_PATH\", \"scripts/zigux/install-zig.py\")");
    try requireContains(source, "(root / \"scripts/zigux/zig-toolchain-policy.json\").unlink()");
    try requireContains(source, "\"scripts/zigux/zig-toolchain-policy.json\",");
    try requireContains(source, "BOOTSTRAP_VALIDATION_SELF_TEST_CASE_COUNT=");
}

const std = @import("std");
const testing = std.testing;

const max_file_size = 1024 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]const u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstNeedleMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondNeedleMissing;
    try testing.expect(first_index < second_index);
}

test "bootstrap ledger keeps broadened phase2 tranche bounded to item 25" {
    const allocator = testing.allocator;
    const ledger = try readFile(allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger);

    try expectContains(ledger, "25. `docs(zigux): reopen and close broadened Phase 2 tranche`");
    try expectContains(ledger, "- `Documentation/zigux/phase2-closure.md`");
    try expectContains(ledger, "- `Documentation/zigux/artifact-diff.md`");
    try expectContains(ledger, "- `scripts/zigux/README.md`");
    try expectContains(ledger, "- `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`");

    try expectContains(ledger, "This bootstrap ledger currently records the bounded early commit train through the broadened Phase 2 tranche.");
    try expectContains(ledger, "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.");
    try expectContains(ledger, "Do not backfill later release-planning state here as synthetic commit history");
    try expectBefore(
        ledger,
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
        "## Scope Note",
    );
    try expectBefore(ledger, "## Scope Note", "## Release-Planning Continuation");
}

test "ledger handoff points later planning to live docs root instead of synthetic history" {
    const allocator = testing.allocator;
    const ledger = try readFile(allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger);

    try expectContains(ledger, "For current release sequencing, tranche-closure posture, and release-coordination follow-through on `master`, continue from the docs-root PMO packet instead:");
    try expectContains(ledger, "- `Documentation/zigux/README.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-sequencing.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-readiness-survey.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-closure-checklist.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase12-release-coordination-matrix.md`");
    try expectContains(ledger, "- `Documentation/zigux/phase14-release-boundary-survey.md`");
    try expectContains(ledger, "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
    try expectContains(ledger, "This keeps the ledger truthful about the early train while making the live release packet explicit for later scheduled PMO runs");
}

test "phase2 handoff aligns ledger with closure and toolchain bootstrap notes" {
    const allocator = testing.allocator;
    const ledger = try readFile(allocator, "zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md");
    defer allocator.free(ledger);
    const closure = try readFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);
    const bootstrap = try readFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(bootstrap);
    const manifest = try readFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest);

    try expectContains(closure, "PHASE2_STATUS=parked");
    try expectContains(closure, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    try expectContains(bootstrap, "This note keeps the current directly readable Phase 2 toolchain packet honest from the docs root.");
    try expectContains(bootstrap, "No current repo-reality gaps remain inside the bounded toolchain");
    try expectContains(bootstrap, "Keep future Phase 2 follow-up inside one current packet surface at a time");

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(manifest, "\"make -C zigux phase2\"");

    try expectBefore(
        ledger,
        "docs(zigux): reopen and close broadened Phase 2 tranche",
        "Keep this ledger authoritative for the reviewed bootstrap commit train through item 25 only.",
    );
}

const std = @import("std");

const ledger = @embedFile("BOOTSTRAP_COMMIT_LEDGER.md");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, ledger, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, ledger, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "bootstrap ledger starts with the roadmap and folder-charter train" {
    try expectContains(ledger, "# Zigux Alpha Bootstrap Commit Ledger");
    try expectContains(ledger, "This ledger turns the roadmap into the first product commit train.");
    try expectContains(ledger, "## Commit Train");

    try expectOrdered(
        "1. `docs(zigux-alpha): establish roadmap and folder charter`",
        "2. `docs(zigux): add documentation root, review checklist, and freeze map`",
    );
    try expectOrdered(
        "2. `docs(zigux): add documentation root, review checklist, and freeze map`",
        "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`",
    );
    try expectOrdered(
        "- `zigux-alpha/README.md`",
        "- `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`",
    );
}

test "bootstrap train keeps the early validation surfaces in sequence" {
    const ordered_items = [_][]const u8{
        "3. `build(scripts/zigux): add bootstrap validation and toolchain checks`",
        "4. `test(zigux): establish differential-test root`",
        "5. `ci(zigux): add bootstrap workflow`",
        "6. `feat(tools/lib): start phase-1 helper ports`",
        "7. `test(zigux): add phase-1 helper harness and workflow gate`",
        "8. `feat(tools/lib): expand phase-1 helper batch`",
        "9. `test(zigux): add phase-1 golden parity fixtures and artifact diff gate`",
        "10. `feat(tools/lib): add phase-1 memory and formatting helper ports`",
        "11. `feat(scripts/zigux): add bounded Phase 2 fixdep dual-implementation lane`",
        "14. `feat(scripts/zigux): add bounded Phase 2 mk_elfconfig lane`",
        "19. `feat(scripts/zigux): start bounded Phase 2 genksyms lane`",
        "23. `feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane`",
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
    };

    var previous = ordered_items[0];
    try expectContains(ledger, previous);
    for (ordered_items[1..]) |current| {
        try expectOrdered(previous, current);
        previous = current;
    }
}

test "scope note hands later state to live docs instead of synthetic history" {
    try expectContains(ledger, "## Scope Note");
    try expectContains(ledger, "bounded early commit train through the broadened Phase 2 tranche");
    try expectContains(ledger, "## Release-Planning Continuation");

    try expectOrdered(
        "25. `docs(zigux): reopen and close broadened Phase 2 tranche`",
        "## Scope Note",
    );
    try expectOrdered("## Scope Note", "## Release-Planning Continuation");

    try expectContains(ledger, "Do not backfill later release-planning state here as synthetic commit history");
    try expectContains(ledger, "use this ledger when the question is which reviewed bootstrap tranche changes landed through the bounded early train");
    try expectContains(ledger, "use the docs-root PMO packet when the question is which release-planning surfaces currently govern later-phase release work on `master`");
}

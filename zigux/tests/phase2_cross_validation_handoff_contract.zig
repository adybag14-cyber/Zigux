const std = @import("std");

const validation_source_path = "scripts/zigux/validate-phase2.py";
const closure_note_path = "Documentation/zigux/phase2-closure.md";
const tests_readme_path = "zigux/tests/README.md";
const makefile_path = "zigux/Makefile";

const cross_route = "phase2-cross";
const direct_checker = "scripts/zigux/check-phase2-cross.py";
const alignment_checker = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const cross_fixture = "zigux/tests/fixtures/phase2_cross_targets.json";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectContainsOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "phase2 validator derives the cross make route from policy routes" {
    const allocator = std.testing.allocator;
    const source = try readRepoFile(allocator, validation_source_path);
    defer allocator.free(source);

    try expectContains(source, "DEFAULT_REQUIRED_MAKE_ROUTES = (");
    try expectContains(source, "\"phase2-toolchain\",");
    try expectContains(source, "\"phase2-tools\",");
    try expectContains(source, "\"phase2-kconfig\",");
    try expectContains(source, "\"phase2-cross\",");
    try expectContains(source, "\"phase2-genksyms\",");
    try expectContains(source, "\"phase2-fixdep\",");
    try expectContains(source, "\"phase2-validate\",");
    try expectOrder(source, "\"phase2-kconfig\",", "\"phase2-cross\",");
    try expectOrder(source, "\"phase2-cross\",", "\"phase2-genksyms\",");

    try expectContains(source, "def load_required_make_routes(root: Path) -> tuple[str, ...]:");
    try expectContains(source, "routes = upgrade_policy.get(\"required_make_routes\")");
    try expectContains(source, "return tuple(f\"run: make -C zigux {route}\" for route in (*required_make_routes, PHASE2_AGGREGATE_ROUTE))");
    try expectContains(source, "return set((*required_make_routes, PHASE2_AGGREGATE_ROUTE))");
}

test "phase2 validator keeps direct and alignment cross checkers in the required path set" {
    const allocator = std.testing.allocator;
    const source = try readRepoFile(allocator, validation_source_path);
    defer allocator.free(source);

    try expectContains(source, "REQUIRED_PATHS = (");
    try expectContains(source, "\"" ++ direct_checker ++ "\",");
    try expectContains(source, "\"" ++ alignment_checker ++ "\",");
    try expectContains(source, "\"" ++ cross_fixture ++ "\",");
    try expectContains(source, "for rel in REQUIRED_PATHS:");
    try expectContains(source, "issues.append((\"MISSING_REQUIRED_PATH\", rel))");
}

test "phase2 validator output keeps policy-driven cross counts visible" {
    const allocator = std.testing.allocator;
    const source = try readRepoFile(allocator, validation_source_path);
    defer allocator.free(source);

    try expectContains(source, "PHASE2_VALIDATION=pass");
    try expectContains(source, "PHASE2_VALIDATION=fail");
    try expectContains(source, "PHASE2_VALIDATION_WORKFLOW_LINE_COUNT=");
    try expectContains(source, "PHASE2_VALIDATION_REQUIRED_PATH_COUNT=");
    try expectContains(source, "len(STATIC_REQUIRED_WORKFLOW_LINES) + len(expected_workflow_route_lines(load_required_make_routes(args.root.resolve())))");
    try expectContains(source, "len(REQUIRED_PATHS) + 1");
    try expectContains(source, "PHASE2_VALIDATION_SELF_TEST_CASE_COUNT=");
}

test "cross validation handoff is mirrored by Makefile and reminder surfaces" {
    const allocator = std.testing.allocator;

    const makefile = try readRepoFile(allocator, makefile_path);
    defer allocator.free(makefile);
    const closure_note = try readRepoFile(allocator, closure_note_path);
    defer allocator.free(closure_note);
    const tests_readme = try readRepoFile(allocator, tests_readme_path);
    defer allocator.free(tests_readme);

    try expectContainsOnce(makefile, "phase2-cross:");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py --self-test");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py");
    try expectContains(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep");
    try expectContains(makefile, "phase2: phase2-validate");

    try expectContains(closure_note, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure_note, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    try expectContains(tests_readme, "`scripts/zigux/validate-phase2.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-cross.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-cross-selftest-alignment.py`");
    try expectContains(tests_readme, "`zigux/tests/fixtures/phase2_cross_targets.json`");
    try expectContains(tests_readme, "`make -C zigux phase2-cross`");
}

const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "phase2 tests readme alignment checker remains in the closure tool manifest" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 192 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"phase\": \"Phase 2\"");
    try expectContains(manifest, "\"status\": \"active\"");
    try expectContains(manifest, "\"repo_reality_gaps\": []");
    try expectContains(manifest, "\"scripts/zigux/check-phase2-tests-readme-alignment.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2.py\"");
    try expectContains(manifest, "\"scripts/zigux/validate-phase2-closure.py\"");
    try expectContains(manifest, "\"make -C zigux phase2-validate\"");
    try expectContains(manifest, "\"make -C zigux phase2\"");
}

test "phase2 tests root reminder names the same live alignment surface" {
    const tests_readme = try readRepoFile("zigux/tests/README.md", 256 * 1024);
    defer std.testing.allocator.free(tests_readme);

    try expectContains(tests_readme, "## Phase 2 review packet");
    try expectContains(tests_readme, "current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:");
    try expectContains(tests_readme, "`Documentation/zigux/phase2-closure.md`");
    try expectContains(tests_readme, "`scripts/zigux/validate-phase2.py`");
    try expectContains(tests_readme, "`scripts/zigux/validate-phase2-closure.py`");
    try expectContains(tests_readme, "`scripts/zigux/check-phase2-tests-readme-alignment.py`");
    try expectContains(tests_readme, "the current directly readable Phase 2 packet is the scripts-root kbuild");
    try expectContains(tests_readme, "the restored closure-side note, validator entrypoint, closure validator");
}

test "phase2 validate route keeps tests-readme alignment ahead of closure validation" {
    const makefile = try readRepoFile("zigux/Makefile", 96 * 1024);
    defer std.testing.allocator.free(makefile);

    const checker_self_test = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test";
    const checker_live = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py";
    const closure_validator = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py";

    try expectContains(makefile, "phase2-validate:");
    try expectContains(makefile, checker_self_test);
    try expectContains(makefile, checker_live);
    try expectContains(makefile, closure_validator);
    try expectBefore(makefile, checker_self_test, closure_validator);
    try expectBefore(makefile, checker_live, closure_validator);

    const closure_note = try readRepoFile("Documentation/zigux/phase2-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure_note);

    try expectContains(
        closure_note,
        "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py",
    );
}

test "phase2 bootstrap workflow routes checker stays wired into the closure packet" {
    const tests_readme = try readRepoFile("zigux/tests/README.md", 256 * 1024);
    defer std.testing.allocator.free(tests_readme);
    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 192 * 1024);
    defer std.testing.allocator.free(manifest);
    const makefile = try readRepoFile("zigux/Makefile", 96 * 1024);
    defer std.testing.allocator.free(makefile);
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 256 * 1024);
    defer std.testing.allocator.free(workflow);

    const checker_path = "scripts/zigux/check-phase2-bootstrap-workflow-routes.py";
    const make_self_test = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py --self-test";
    const make_live_check = "\n\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-bootstrap-workflow-routes.py\n";
    const workflow_self_test = "run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test";
    const workflow_live_check = "\n        run: python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py\n";
    const phase2_toolchain_route = "make -C zigux phase2-toolchain";
    const phase2_validator = "python3 scripts/zigux/validate-phase2.py";

    try expectContains(tests_readme, "`scripts/zigux/check-phase2-bootstrap-workflow-routes.py`");
    try expectContains(tests_readme, "the shipped `zigux/Makefile` wrappers");
    try expectContains(manifest, checker_path);
    try expectContains(manifest, "the bootstrap workflow-routes guard");
    try expectContains(makefile, "phase2-tools:");
    try expectContains(makefile, make_self_test);
    try expectContains(makefile, make_live_check);
    try expectBefore(makefile, make_self_test, make_live_check);

    try expectContains(workflow, workflow_self_test);
    try expectContains(workflow, workflow_live_check);
    try expectBefore(workflow, workflow_self_test, workflow_live_check);
    try expectBefore(workflow, workflow_live_check, phase2_toolchain_route);
    try expectBefore(workflow, workflow_live_check, phase2_validator);
}

test "phase2 tests-readme checker keeps its self-test and live pass signals" {
    const checker = try readRepoFile("scripts/zigux/check-phase2-tests-readme-alignment.py", 160 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(checker, "PHASE2_TESTS_README_ALIGNMENT=self-test-pass");
    try expectContains(checker, "PHASE2_TESTS_README_ALIGNMENT_SELF_TEST_CASES=");
    try expectContains(checker, "PHASE2_TESTS_README_ALIGNMENT=pass");
    try expectContains(checker, "REQUIRED_TESTS_README_MARKERS");
    try expectContains(checker, "REQUIRED_PHASE2_TOOL_MANIFEST_SURFACES");
}

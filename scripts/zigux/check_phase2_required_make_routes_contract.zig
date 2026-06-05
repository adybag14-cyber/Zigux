const std = @import("std");

const repo_files = .{
    .checker = "scripts/zigux/check-phase2-required-make-routes.py",
    .policy = "scripts/zigux/zig-toolchain-policy.json",
    .workflow = ".github/workflows/zigux-bootstrap.yml",
    .makefile = "zigux/Makefile",
};

const required_routes = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const checker_markers = [_][]const u8{
    "TOOLCHAIN_ROUTE = \"phase2-toolchain\"",
    "TOOLCHAIN_ALLOWED_RECIPE_LINES = (",
    "TOOLCHAIN_OVERLAP_FRAGMENTS = (",
    "def load_required_make_routes(policy_path: Path) -> list[str]:",
    "def collect_required_route_makefile_issues(",
    "def collect_toolchain_route_boundary_issues(makefile_text: str) -> list[tuple[str, str]]:",
    "PHASE2_REQUIRED_MAKE_ROUTES=pass",
    "PHASE2_TOOLCHAIN_ROUTE_BOUNDARY=bounded",
};

const toolchain_route_lines = [_][]const u8{
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try std.testing.expect(first_index < second_index);
}

fn workflowLine(route: []const u8) []const u8 {
    if (std.mem.eql(u8, route, "phase2-toolchain")) return "run: make -C zigux phase2-toolchain";
    if (std.mem.eql(u8, route, "phase2-tools")) return "run: make -C zigux phase2-tools";
    if (std.mem.eql(u8, route, "phase2-kconfig")) return "run: make -C zigux phase2-kconfig";
    if (std.mem.eql(u8, route, "phase2-cross")) return "run: make -C zigux phase2-cross";
    if (std.mem.eql(u8, route, "phase2-genksyms")) return "run: make -C zigux phase2-genksyms";
    if (std.mem.eql(u8, route, "phase2-fixdep")) return "run: make -C zigux phase2-fixdep";
    if (std.mem.eql(u8, route, "phase2-validate")) return "run: make -C zigux phase2-validate";
    unreachable;
}

fn policyRouteMarker(route: []const u8) []const u8 {
    if (std.mem.eql(u8, route, "phase2-toolchain")) return "\"phase2-toolchain\"";
    if (std.mem.eql(u8, route, "phase2-tools")) return "\"phase2-tools\"";
    if (std.mem.eql(u8, route, "phase2-kconfig")) return "\"phase2-kconfig\"";
    if (std.mem.eql(u8, route, "phase2-cross")) return "\"phase2-cross\"";
    if (std.mem.eql(u8, route, "phase2-genksyms")) return "\"phase2-genksyms\"";
    if (std.mem.eql(u8, route, "phase2-fixdep")) return "\"phase2-fixdep\"";
    if (std.mem.eql(u8, route, "phase2-validate")) return "\"phase2-validate\"";
    unreachable;
}

fn makefileRouteTarget(route: []const u8) []const u8 {
    if (std.mem.eql(u8, route, "phase2-toolchain")) return "phase2-toolchain:";
    if (std.mem.eql(u8, route, "phase2-tools")) return "phase2-tools:";
    if (std.mem.eql(u8, route, "phase2-kconfig")) return "phase2-kconfig:";
    if (std.mem.eql(u8, route, "phase2-cross")) return "phase2-cross:";
    if (std.mem.eql(u8, route, "phase2-genksyms")) return "phase2-genksyms:";
    if (std.mem.eql(u8, route, "phase2-fixdep")) return "phase2-fixdep:";
    if (std.mem.eql(u8, route, "phase2-validate")) return "phase2-validate:";
    unreachable;
}

test "required make-routes checker keeps fail-closed policy and route guards" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, repo_files.checker);
    defer allocator.free(checker);

    for (checker_markers) |marker| {
        try expectContains(checker, marker);
    }

    for (required_routes) |route| {
        try expectContains(checker, policyRouteMarker(route));
    }

    try expectBefore(
        checker,
        "issues.extend(collect_required_route_makefile_issues(makefile_text, tuple(required_routes)))",
        "issues.extend(collect_toolchain_route_boundary_issues(makefile_text))",
    );
    try expectBefore(checker, "PHASE2_REQUIRED_MAKE_ROUTES=fail", "PHASE2_REQUIRED_MAKE_ROUTES=pass");
}

test "policy required routes are mirrored by workflow and Makefile routes" {
    const allocator = std.testing.allocator;
    const policy = try readRepoFile(allocator, repo_files.policy);
    defer allocator.free(policy);
    const workflow = try readRepoFile(allocator, repo_files.workflow);
    defer allocator.free(workflow);
    const makefile = try readRepoFile(allocator, repo_files.makefile);
    defer allocator.free(makefile);

    try expectContains(policy, "\"required_make_routes\"");
    try expectContains(makefile, ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2");

    for (required_routes) |route| {
        try expectContains(policy, policyRouteMarker(route));
        try expectContains(workflow, workflowLine(route));
        try expectContains(makefile, makefileRouteTarget(route));
    }

    try expectBefore(workflow, "Self-test current Phase 2 required-make-routes checker", "Check current Phase 2 required-make-routes packet");
    try expectBefore(workflow, "run: python3 scripts/zigux/check-phase2-required-make-routes.py", "run: make -C zigux phase2-toolchain");
    try expectBefore(workflow, "run: make -C zigux phase2-toolchain", "run: make -C zigux phase2-validate");
}

test "toolchain make route stays bounded to bootstrap toolchain checks" {
    const allocator = std.testing.allocator;
    const checker = try readRepoFile(allocator, repo_files.checker);
    defer allocator.free(checker);
    const makefile = try readRepoFile(allocator, repo_files.makefile);
    defer allocator.free(makefile);

    for (toolchain_route_lines) |line| {
        try expectContains(checker, line);
        try expectContains(makefile, line);
    }

    try expectContains(checker, "TOOLCHAIN_ROUTE_OVERLAP");
    try expectContains(checker, "make -C zigux phase2-");
    try expectBefore(makefile, "phase2-toolchain:", "phase2-tools:");
    try expectBefore(makefile, "phase2-tools:", "phase2-validate:");
}

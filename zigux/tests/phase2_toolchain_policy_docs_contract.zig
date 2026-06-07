const std = @import("std");

const max_file_size = 1024 * 1024;

fn readFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(max_file_size));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

test "phase2 policy keeps pinned archive and route roster explicit" {
    const allocator = std.testing.allocator;
    const policy = try readFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectContains(policy, "\"phase\": \"Phase 2\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"minimum_version\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"x86_64-linux\": \"0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6\"");
    try expectContains(policy, "\"channel_minimum_lockstep\": true");
    try expectContains(policy, "\"archive_target_scope\": [\n      \"x86_64-linux\"\n    ]");
    try expectNotContains(policy, "\"aarch64-linux\":");
    try expectNotContains(policy, "\"riscv64-linux\":");

    try expectOrdered(policy, "\"phase2-toolchain\"", "\"phase2-tools\"");
    try expectOrdered(policy, "\"phase2-tools\"", "\"phase2-kconfig\"");
    try expectOrdered(policy, "\"phase2-kconfig\"", "\"phase2-cross\"");
    try expectOrdered(policy, "\"phase2-cross\"", "\"phase2-genksyms\"");
    try expectOrdered(policy, "\"phase2-genksyms\"", "\"phase2-fixdep\"");
    try expectOrdered(policy, "\"phase2-fixdep\"", "\"phase2-validate\"");
}

test "documentation mirrors the policy pinned toolchain and archive packet" {
    const allocator = std.testing.allocator;
    const bootstrap_note = try readFile(allocator, "Documentation/zigux/phase2-toolchain-bootstrap-notes.md");
    defer allocator.free(bootstrap_note);
    const third_party_readme = try readFile(allocator, "third_party/README.md");
    defer allocator.free(third_party_readme);
    const tests_readme = try readFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    try expectContains(bootstrap_note, "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.758+748e7c5e3`");
    try expectContains(bootstrap_note, "limits archive digests to `x86_64-linux`");
    try expectContains(bootstrap_note, "`phase2-toolchain`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, `phase2-genksyms`, `phase2-fixdep`, and `phase2-validate`");
    try expectContains(bootstrap_note, "derives `ZIGUX_ZIG_TARGET`, `ZIGUX_ZIG_FILENAME`, `ZIGUX_ZIG_URL`, and `ZIGUX_ZIG_CANONICAL_URL` from `scripts/zigux/zig-toolchain-policy.json`");
    try expectContains(bootstrap_note, "No current repo-reality gaps remain inside the bounded toolchain");

    try expectContains(third_party_readme, "channel: `0.17.0-dev.758+748e7c5e3`");
    try expectContains(third_party_readme, "file: `third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz`");
    try expectContains(third_party_readme, "sha256: `0af43565c01997c12b1f770928de4ed983c3e099730c452ef5ec205d74a582f6`");
    try expectContains(third_party_readme, "size: `59410844` bytes");
    try expectContains(third_party_readme, "update this README and its checker whenever `scripts/zigux/zig-toolchain-policy.json`");

    try expectContains(tests_readme, "`scripts/zigux/zig-toolchain-policy.json`");
    try expectContains(tests_readme, "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`");
    try expectContains(tests_readme, "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`");
    try expectContains(tests_readme, "third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz");
    try expectContains(tests_readme, "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`");
}

test "review workflow and make routes keep the policy packet replayable" {
    const allocator = std.testing.allocator;
    const review_checklist = try readFile(allocator, "Documentation/zigux/review-checklist.md");
    defer allocator.free(review_checklist);
    const workflow = try readFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const makefile = try readFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    try expectContains(review_checklist, "if the change touches the shared Phase 2 toolchain packet");
    try expectContains(review_checklist, "`scripts/zigux/zig-toolchain-policy.json`");
    try expectContains(review_checklist, "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`");
    try expectContains(review_checklist, "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.758+748e7c5e3.tar.xz --archive-target x86_64-linux`");
    try expectContains(review_checklist, "`make -C zigux phase2-genksyms`");
    try expectContains(review_checklist, "`make -C zigux phase2-fixdep`");

    try expectContains(workflow, "policy = json.loads(Path(\"scripts/zigux/zig-toolchain-policy.json\").read_text(encoding=\"utf-8\"))");
    try expectContains(workflow, "expected exactly one pinned archive target");
    try expectOrdered(workflow, "python3 scripts/zigux/check-zig-toolchain.py --policy-only", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectContains(workflow, "make -C zigux phase2-toolchain");
    try expectContains(workflow, "make -C zigux phase2-validate");

    try expectContains(makefile, "PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json");
    try expectContains(makefile, "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c");
    try expectContains(makefile, "phase2-toolchain:");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only");
    try expectContains(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing");
    try expectOrdered(makefile, "phase2-toolchain:", "phase2-tools:");
    try expectOrdered(makefile, "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep", "phase2: phase2-validate");
}

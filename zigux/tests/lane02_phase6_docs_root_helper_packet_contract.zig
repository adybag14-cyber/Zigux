const std = @import("std");

const ContractFile = struct {
    path: []const u8,
    snippets: []const []const u8,
};

fn readContractFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(
        std.mem.indexOf(u8, haystack, needle) != null,
    );
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.BeforeMarkerMissing;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.AfterMarkerMissing;
    try std.testing.expect(before_index < after_index);
}

fn expectFileSnippets(file: ContractFile) !void {
    const allocator = std.testing.allocator;
    const content = try readContractFile(allocator, file.path);
    defer allocator.free(content);

    for (file.snippets) |snippet| {
        try expectContains(content, snippet);
    }
}

test "Lane 02 Phase 6 docs root names the helper evidence packet" {
    try expectFileSnippets(.{
        .path = "Documentation/zigux/README.md",
        .snippets = &.{
            "Phase 6 notes",
            "Documentation/zigux/phase6-helper-evidence-catalog.md",
            "Documentation/zigux/phase6-helper-parity-catalog.md",
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "scripts/zigux/validate-phase6.py",
            "zigux/tests/phase6_build.zig",
            "make -C zigux phase6-perf",
            "lib/base64.c",
            "lib/bsearch.c",
            "lib/checksum.c",
            "lib/hexdump.c",
        },
    });
}

test "Lane 02 Phase 6 review checklist preserves validation prompts" {
    try expectFileSnippets(.{
        .path = "Documentation/zigux/review-checklist.md",
        .snippets = &.{
            "if the change touches the shared Phase 6 leaf-library packet",
            "Documentation/zigux/phase6-helper-evidence-catalog.md",
            "Documentation/zigux/phase6-helper-parity-catalog.md",
            "scripts/zigux/validate-phase6.py",
            "scripts/zigux/check-phase6-shared-surface.py",
            "scripts/zigux/check-phase6-perf-threshold-markers.py",
            "zigux/tests/phase6_helper_evidence_manifest.json",
            "zigux/tests/phase6_helper_parity_manifest.json",
            "make -C zigux phase6-validate",
            "make -C zigux phase6-perf",
        },
    });
}

test "Lane 02 Phase 6 shared docs align on helpers and perf route" {
    try expectFileSnippets(.{
        .path = "Documentation/zigux/phase6-helper-evidence-catalog.md",
        .snippets = &.{
            "surveyed head: `current-master-readback-2026-05-22`",
            "roadmap-backed helper anchors",
            "lib/base64.c",
            "lib/bsearch.c",
            "lib/checksum.c",
            "lib/hexdump.c",
            "Documentation/zigux/phase6-helper-parity-catalog.md",
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "Current shared replay inventory",
            "make -C zigux phase6-perf",
        },
    });

    try expectFileSnippets(.{
        .path = "Documentation/zigux/phase6-helper-parity-catalog.md",
        .snippets = &.{
            "shared helper-parity rows and machine-readable manifest only",
            "Roadmap-to-helper-evidence row index",
            "`base64` | `lib/base64.c` | `lib/base64.zig`",
            "`bsearch` | `lib/bsearch.c` | `lib/bsearch.zig`",
            "`checksum` | `lib/checksum.c` | `lib/checksum.zig`",
            "`hexdump` | `lib/hexdump.c` | `lib/hexdump.zig`",
            "Shared parity boundary",
        },
    });

    try expectFileSnippets(.{
        .path = "Documentation/zigux/phase6-perf-gate-survey.md",
        .snippets = &.{
            "PHASE6_PERF_SURVEY_STATUS=active",
            "PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump",
            "make -C zigux phase6-perf",
            "base64 exact thresholds",
            "bsearch exact evidence",
            "checksum exact thresholds",
            "hexdump exact thresholds",
        },
    });
}

test "Lane 02 Phase 6 validator and build routes remain reviewable" {
    const build_file = try readContractFile(std.testing.allocator, "zigux/tests/phase6_build.zig");
    defer std.testing.allocator.free(build_file);
    try expectContains(build_file, "phase6-base64-test");
    try expectContains(build_file, "phase6-bsearch-test");
    try expectContains(build_file, "phase6-checksum-test");
    try expectContains(build_file, "phase6-hexdump-test");
    try expectContains(build_file, "phase6-base64-perf");
    try expectContains(build_file, "phase6-bsearch-perf");
    try expectContains(build_file, "phase6-checksum-perf");
    try expectContains(build_file, "phase6-hexdump-perf");
    try expectOrdered(build_file, "phase6-base64-perf", "const test_step = b.step(\"test\"");

    const validator = try readContractFile(std.testing.allocator, "scripts/zigux/validate-phase6.py");
    defer std.testing.allocator.free(validator);
    try expectContains(validator, "HELPER_EVIDENCE_CATALOG = Path(\"Documentation/zigux/phase6-helper-evidence-catalog.md\")");
    try expectContains(validator, "HELPER_PARITY_CATALOG = Path(\"Documentation/zigux/phase6-helper-parity-catalog.md\")");
    try expectContains(validator, "EXPECTED_ROADMAP_ANCHORS = [\"lib/base64.c\", \"lib/bsearch.c\", \"lib/checksum.c\", \"lib/hexdump.c\"]");
    try expectContains(validator, "EXPECTED_SHARED_PERF_WRAPPER = \"make -C zigux phase6-perf\"");
    try expectContains(validator, "SELF_TEST_CASE_COUNT = 33");

    const makefile = try readContractFile(std.testing.allocator, "zigux/Makefile");
    defer std.testing.allocator.free(makefile);
    try expectContains(makefile, "phase6-validate:");
    try expectContains(makefile, "$(PYTHON) scripts/zigux/validate-phase6.py");
    try expectContains(makefile, "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf");
}

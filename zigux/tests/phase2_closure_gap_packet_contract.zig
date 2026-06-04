const std = @import("std");
const testing = std.testing;

const closure_gap_packet =
    \\PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md
;

const closure_repo_reality =
    \\current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`, so the shipped kconfig bridge packet remains fixture-backed rather than same-tree differential
;

const closure_kconfig_next_step =
    \\the next same-family truthfulness pass should keep reminder surfaces aligned with the live split recorded in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`: request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`, `allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`, and the helper-local explicit-override roster remains broader by design
;

const closure_resume_policy =
    \\Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again. If the kconfig bridge lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step that preserves the live split between request-plan overrides, the non-empty sentinel packet, and helper-local explicit-override coverage, then add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`. If the `genksyms` lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step around the still-missing CRC-side evidence recorded in the survey rather than widening this shared note again.
;

test "closure gap packet stays kconfig survey scoped" {
    try testing.expect(std.mem.startsWith(u8, closure_gap_packet, "PHASE2_CURRENT_GAP_PACKET="));
    try testing.expect(std.mem.endsWith(u8, closure_gap_packet, "phase2-kconfig-bridge-gap-survey.md"));
    try testing.expect(!std.mem.containsAtLeast(u8, closure_gap_packet, 1, "genksyms"));
    try testing.expect(!std.mem.containsAtLeast(u8, closure_gap_packet, 1, "fixdep"));
}

test "repo reality boundary remains fixture backed until C sources are readable" {
    try testing.expect(std.mem.containsAtLeast(u8, closure_repo_reality, 1, "scripts/kconfig/conf.c"));
    try testing.expect(std.mem.containsAtLeast(u8, closure_repo_reality, 1, "scripts/kconfig/confdata.c"));
    try testing.expect(std.mem.containsAtLeast(u8, closure_repo_reality, 1, "current authenticated repo reads do not expose"));
    try testing.expect(std.mem.containsAtLeast(u8, closure_repo_reality, 1, "fixture-backed rather than same-tree differential"));
}

test "next step keeps kconfig and genksyms implementation lanes separate from closure upkeep" {
    try testing.expect(std.mem.containsAtLeast(u8, closure_kconfig_next_step, 1, "request-plan `allconfig` overrides"));
    try testing.expect(std.mem.containsAtLeast(u8, closure_kconfig_next_step, 1, "`allmodconfig`, `alldefconfig`, and `randconfig`"));
    try testing.expect(std.mem.containsAtLeast(u8, closure_kconfig_next_step, 1, "`allnoconfig` and `allyesconfig`"));
    try testing.expect(std.mem.containsAtLeast(u8, closure_resume_policy, 1, "Keep the shared Phase 2 closure packet parked"));
    try testing.expect(std.mem.containsAtLeast(u8, closure_resume_policy, 1, "direct `conf.c` / `confdata.c` provenance anchor"));
    try testing.expect(std.mem.containsAtLeast(u8, closure_resume_policy, 1, "still-missing CRC-side evidence"));
}

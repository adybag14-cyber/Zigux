const std = @import("std");

const closure_note =
    \\- `PHASE2_STATUS=parked`
    \\- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
    \\- shared validator pair: `zig run scripts/zigux/validate_phase2.zig` and `zig run scripts/zigux/validate_phase2_closure.zig`
    \\- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`
    \\- `PHASE2_CLOSURE_VALIDATORS=zig run scripts/zigux/validate_phase2.zig,zig run scripts/zigux/validate_phase2_closure.zig`
    \\Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.
;

const makefile_phase2_routes =
    \\phase2-genksyms: phase2-toolchain
    \\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig -- --self-test
    \\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig
    \\\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig
    \\\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig
    \\\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig
    \\\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig -- --self-test
    \\\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig
    \\
    \\phase2-fixdep: phase2-toolchain
    \\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig -- --self-test
    \\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig
    \\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig -- --self-test
    \\\tcd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig -- --zig "$(ZIG_REPO_ROOT)"
    \\\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig
    \\
    \\phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
    \\\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig -- --self-test
    \\\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig
    \\\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tool_manifest.zig -- --self-test
    \\\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tool_manifest.zig
    \\\t$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase2_closure.zig
    \\
    \\phase2: phase2-validate
;

const workflow_phase2_routes =
    \\      - name: Run current Phase 2 genksyms make route
    \\        run: make -C zigux phase2-genksyms
    \\
    \\      - name: Run current Phase 2 validate make route
    \\        run: make -C zigux phase2-validate
    \\
    \\      - name: Run current Phase 2 aggregate make route
    \\        run: make -C zigux phase2
    \\
    \\      - name: Validate current Phase 2 tool packet
    \\        run: zig run scripts/zigux/validate_phase2.zig
    \\
    \\      - name: Self-test current Phase 2 closure validator
    \\        run: zig run scripts/zigux/validate_phase2_closure.zig -- --self-test
    \\
    \\      - name: Check current Phase 2 closure packet
    \\        run: zig run scripts/zigux/validate_phase2_closure.zig
;

test "closure note keeps shared make routes and validators explicit" {
    try requireContains(closure_note, "PHASE2_STATUS=parked");
    try requireContains(closure_note, "PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest");
    try requireContains(
        closure_note,
        "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2",
    );
    try requireContains(
        closure_note,
        "PHASE2_CLOSURE_VALIDATORS=zig run scripts/zigux/validate_phase2.zig,zig run scripts/zigux/validate_phase2_closure.zig",
    );
    try requireContains(
        closure_note,
        "Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
    );
}

test "Makefile routes aggregate through genksyms fixdep and closure validation" {
    try requireContains(
        makefile_phase2_routes,
        "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    );
    try requireContains(makefile_phase2_routes, "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase2_closure.zig");
    try requireContains(makefile_phase2_routes, "phase2: phase2-validate");
    try requireBefore(makefile_phase2_routes, "phase2-genksyms: phase2-toolchain", "phase2-validate:");
    try requireBefore(makefile_phase2_routes, "phase2-fixdep: phase2-toolchain", "phase2-validate:");
    try requireBefore(makefile_phase2_routes, "check-phase2-tool-manifest.py", "validate-phase2-closure.py");
    try requireBefore(makefile_phase2_routes, "validate-phase2-closure.py", "phase2: phase2-validate");
}

test "workflow keeps closure replay after aggregate Phase 2 route" {
    try requireBefore(
        workflow_phase2_routes,
        "Run current Phase 2 genksyms make route",
        "Run current Phase 2 validate make route",
    );
    try requireBefore(
        workflow_phase2_routes,
        "Run current Phase 2 validate make route",
        "Run current Phase 2 aggregate make route",
    );
    try requireBefore(
        workflow_phase2_routes,
        "Run current Phase 2 aggregate make route",
        "Validate current Phase 2 tool packet",
    );
    try requireBefore(
        workflow_phase2_routes,
        "Validate current Phase 2 tool packet",
        "Self-test current Phase 2 closure validator",
    );
    try requireBefore(
        workflow_phase2_routes,
        "Self-test current Phase 2 closure validator",
        "Check current Phase 2 closure packet",
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

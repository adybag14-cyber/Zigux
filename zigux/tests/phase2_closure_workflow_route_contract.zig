const std = @import("std");

const closure_note =
    \\- `PHASE2_STATUS=parked`
    \\- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
    \\- shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`
    \\- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`
    \\- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`
    \\Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.
;

const makefile_phase2_routes =
    \\phase2-genksyms: phase2-toolchain
    \\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test
    \\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py
    \\\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig
    \\\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig
    \\\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig
    \\\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test
    \\\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py
    \\
    \\phase2-fixdep: phase2-toolchain
    \\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test
    \\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py
    \\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test
    \\\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --zig "$(ZIG_REPO_ROOT)"
    \\\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig
    \\
    \\phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep
    \\\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py --self-test
    \\\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py
    \\\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py --self-test
    \\\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py
    \\\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py
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
    \\        run: python3 scripts/zigux/validate-phase2.py
    \\
    \\      - name: Self-test current Phase 2 closure validator
    \\        run: python3 scripts/zigux/validate-phase2-closure.py --self-test
    \\
    \\      - name: Check current Phase 2 closure packet
    \\        run: python3 scripts/zigux/validate-phase2-closure.py
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
        "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py",
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
    try requireContains(makefile_phase2_routes, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py");
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

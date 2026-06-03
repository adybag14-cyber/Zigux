const std = @import("std");

const route = "make -C zigux phase2-cross";
const make_route = "phase2-cross";
const direct_checker = "scripts/zigux/check-phase2-cross.py";
const alignment_checker = "scripts/zigux/check-phase2-cross-selftest-alignment.py";
const target_fixture = "zigux/tests/fixtures/phase2_cross_targets.json";
const makefile_direct_line = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py";
const makefile_alignment_line = "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py";
const workflow_direct_step = "Check current Phase 2 direct cross-route packet";
const workflow_alignment_step = "Check current Phase 2 cross alignment packet";
const workflow_make_step = "Run current Phase 2 cross make route";
const direct_pass_marker = "PHASE2_DIRECT_CROSS_ROUTE=pass";
const alignment_pass_marker = "PHASE2_CROSS_ALIGNMENT=pass";

test "phase2 cross route vocabulary stays explicit" {
    try std.testing.expectEqualStrings("make -C zigux phase2-cross", route);
    try std.testing.expectEqualStrings("phase2-cross", make_route);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase2-cross.py", direct_checker);
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase2-cross-selftest-alignment.py",
        alignment_checker,
    );
    try std.testing.expectEqualStrings("zigux/tests/fixtures/phase2_cross_targets.json", target_fixture);
    try std.testing.expectEqualStrings(
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
        makefile_direct_line,
    );
    try std.testing.expectEqualStrings(
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
        makefile_alignment_line,
    );
}

test "phase2 cross route keeps direct and alignment checker split" {
    try std.testing.expect(std.mem.endsWith(u8, direct_checker, "check-phase2-cross.py"));
    try std.testing.expect(std.mem.endsWith(
        u8,
        alignment_checker,
        "check-phase2-cross-selftest-alignment.py",
    ));
    try std.testing.expect(!std.mem.eql(u8, direct_checker, alignment_checker));
    try std.testing.expect(!std.mem.eql(u8, makefile_direct_line, makefile_alignment_line));
}

test "phase2 cross workflow vocabulary keeps direct alignment and make steps" {
    try std.testing.expectEqualStrings(
        "Check current Phase 2 direct cross-route packet",
        workflow_direct_step,
    );
    try std.testing.expectEqualStrings(
        "Check current Phase 2 cross alignment packet",
        workflow_alignment_step,
    );
    try std.testing.expectEqualStrings("Run current Phase 2 cross make route", workflow_make_step);
}

test "phase2 cross checker pass markers stay distinct" {
    try std.testing.expectEqualStrings("PHASE2_DIRECT_CROSS_ROUTE=pass", direct_pass_marker);
    try std.testing.expectEqualStrings("PHASE2_CROSS_ALIGNMENT=pass", alignment_pass_marker);
    try std.testing.expect(!std.mem.eql(u8, direct_pass_marker, alignment_pass_marker));
}

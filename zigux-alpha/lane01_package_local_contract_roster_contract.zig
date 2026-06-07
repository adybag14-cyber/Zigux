const std = @import("std");
const testing = std.testing;

const alpha_readme = @embedFile("README.md");
const roadmap = @embedFile("ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md");

const roster_packet =
    \\Lane 01 package-local contract roster, current scheduled-run packet.
    \\
    \\Merged or master-grounded package-local baseline:
    \\- lane01_phase9_runtime_pilot_modules_contract.zig
    \\- lane01_phase10_virtio_lab_drivers_contract.zig
    \\
    \\Fresh open package-local fronts that must be treated as owned before adding duplicates:
    \\- lane01_alpha_readme_charter_contract.zig
    \\- lane01_bootstrap_charter_alignment_contract.zig
    \\- lane01_windows_case_sensitive_contract.zig
    \\- lane01_roadmap_workstreams_ownership_contract.zig
    \\- lane01_phase7_in_kernel_leaf_libraries_contract.zig
    \\- lane01_phase8_userspace_tooling_expansion_contract.zig
    \\- lane01_phase11_storage_block_devices_contract.zig
    \\- lane01_phase12_complex_drivers_heavy_consumers_contract.zig
    \\- lane01_phase13_shared_subsystem_helpers_contract.zig
    \\- lane01_phase14_core_adjacent_bounded_internals_contract.zig
    \\- lane01_phase15_full_parity_governance_contract.zig
    \\- lane01_risk_register_prioritization_contract.zig
    \\- lane01_recommended_validation_gates_contract.zig
    \\- lane01_final_direction_contract.zig
    \\
    \\Selection rule:
    \\- Check this roster, active pull requests, and live master readback before choosing another Lane 01 package-local packet.
    \\- Prefer hardening an existing package-local contract over adding a duplicate packet for the same roadmap or charter surface.
    \\- Keep product implementation out of zigux-alpha; use it only for bootstrap planning and package-local guards.
;

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(contains(haystack, needle));
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "alpha README still exposes the planning-only charter surfaces" {
    try expectContains(alpha_readme, "`zigux-alpha` is the Zigux bootstrap workspace.");
    try expectContains(alpha_readme, "It does not exist to become a permanent parallel subsystem tree.");
    try expectContains(alpha_readme, "Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.");
    try expectContains(alpha_readme, "`scripts/zigux/check-lane01-bootstrap-charter-alignment.py` is the shipped bootstrap-charter guard");
    try expectOrdered(alpha_readme, "Rules", "Active product surfaces");
    try expectOrdered(alpha_readme, "Active product surfaces", "Start here");
}

test "roadmap still frames zigux-alpha as bootstrap control-plane only" {
    try expectContains(roadmap, "`zigux-alpha/` is a bootstrap workspace, not the final home for subsystem ports.");
    try expectContains(roadmap, "`zigux-alpha/` is the staging area for:");
    try expectContains(roadmap, "`zigux-alpha/` is not the final home for:");
    try expectContains(roadmap, "Co-locate product code with Linux ownership.");
    try expectOrdered(roadmap, "## zigux-alpha Scope", "## Product Features by Phase");
}

test "roster records current package-local coverage and open owned fronts" {
    try expectContains(roster_packet, "lane01_phase9_runtime_pilot_modules_contract.zig");
    try expectContains(roster_packet, "lane01_phase10_virtio_lab_drivers_contract.zig");
    try expectContains(roster_packet, "lane01_alpha_readme_charter_contract.zig");
    try expectContains(roster_packet, "lane01_bootstrap_charter_alignment_contract.zig");
    try expectContains(roster_packet, "lane01_windows_case_sensitive_contract.zig");
    try expectContains(roster_packet, "lane01_roadmap_workstreams_ownership_contract.zig");
    try expectContains(roster_packet, "lane01_phase7_in_kernel_leaf_libraries_contract.zig");
    try expectContains(roster_packet, "lane01_phase8_userspace_tooling_expansion_contract.zig");
    try expectContains(roster_packet, "lane01_phase11_storage_block_devices_contract.zig");
    try expectContains(roster_packet, "lane01_phase12_complex_drivers_heavy_consumers_contract.zig");
    try expectContains(roster_packet, "lane01_phase13_shared_subsystem_helpers_contract.zig");
    try expectContains(roster_packet, "lane01_phase14_core_adjacent_bounded_internals_contract.zig");
    try expectContains(roster_packet, "lane01_phase15_full_parity_governance_contract.zig");
    try expectContains(roster_packet, "lane01_risk_register_prioritization_contract.zig");
    try expectContains(roster_packet, "lane01_recommended_validation_gates_contract.zig");
    try expectContains(roster_packet, "lane01_final_direction_contract.zig");
    try expectOrdered(roster_packet, "Merged or master-grounded package-local baseline:", "Fresh open package-local fronts");
}

test "selection rule blocks duplicate package-local roadmap packets" {
    try expectContains(roster_packet, "Check this roster, active pull requests, and live master readback");
    try expectContains(roster_packet, "Prefer hardening an existing package-local contract over adding a duplicate packet");
    try expectContains(roster_packet, "Keep product implementation out of zigux-alpha");
}

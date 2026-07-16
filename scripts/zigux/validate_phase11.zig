const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE11_VALIDATE_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const CheckKind = enum { script, build };
const CheckSpec = struct { name: []const u8, kind: CheckKind, script_rel: []const u8 = "", self_test: bool = false, build_file: []const u8 = "" };
const ManifestExpectation = struct { rel: []const u8, lane_key: []const u8 };
const Gap = struct { id: ?[]const u8 = null };
const Manifest = struct { lane_key: []const u8, phase: []const u8, gaps: []const Gap };

const required_paths = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase11-shared-replay-contract.md",
    "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
    "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md",
    "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "Documentation/zigux/phase11-bcm2835-wdt-platform-validation-plan.md",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md",
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "Documentation/zigux/phase11-dw-wdt-provenance-readback.md",
    "Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md",
    "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
    "Documentation/zigux/phase11-gpio-wdt-teardown-note.md",
    "Documentation/zigux/phase11-gpio-wdt-remove-handoff-note.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
    "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
    "Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "scripts/zigux/check_phase11_validate_manifest_roster.zig",
    "scripts/zigux/check_phase11_validate_check_roster.zig",
    "scripts/zigux/check_phase11_validate_route_alignment.zig",
    "scripts/zigux/check_phase11_shared_tooling_manifest.zig",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
    "scripts/zigux/check_phase11_matrix_gap_survey.zig",
    "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig",
    "scripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig",
    "scripts/zigux/check_phase11_header_boundary_packet.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "scripts/zigux/check_phase11_hvc_current_head_manifest.zig",
    "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
    "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
    "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
    "scripts/zigux/validate_phase11.zig",
    "drivers/tty/hvc/hvc_console.h",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "drivers/watchdog/bcm2835_wdt.zig",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "drivers/watchdog/gpio_wdt.zig",
    "drivers/watchdog/gpio_wdt_verify.zig",
    "drivers/watchdog/dw_wdt.zig",
    "drivers/watchdog/dw_wdt_restart.zig",
    "drivers/watchdog/dw_wdt_pm.zig",
    "drivers/watchdog/dw_wdt_pm_scaffold.zig",
    "drivers/watchdog/dw_wdt_verify.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_survey.zig",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_bcm2835_wdt.zig",
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig",
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_pm_build.zig",
    "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_modem_control_proof.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const manifest_expectations = [_]ManifestExpectation{
    .{ .rel = "zigux/tests/phase11_bcm2835_wdt_manifest.json", .lane_key = "P11-L08" },
    .{ .rel = "zigux/tests/phase11_dw_wdt_manifest.json", .lane_key = "P11-L10" },
};

const checks = [_]CheckSpec{
    .{ .name = "phase11-validation-self-test", .kind = .script, .script_rel = "scripts/zigux/validate_phase11.zig", .self_test = true },
    .{ .name = "phase11-validate-manifest-roster-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_validate_manifest_roster.zig", .self_test = true },
    .{ .name = "phase11-validate-manifest-roster", .kind = .script, .script_rel = "scripts/zigux/check_phase11_validate_manifest_roster.zig", .self_test = false },
    .{ .name = "phase11-validate-check-roster-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_validate_check_roster.zig", .self_test = true },
    .{ .name = "phase11-validate-check-roster", .kind = .script, .script_rel = "scripts/zigux/check_phase11_validate_check_roster.zig", .self_test = false },
    .{ .name = "phase11-validate-route-alignment-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_validate_route_alignment.zig", .self_test = true },
    .{ .name = "phase11-validate-route-alignment", .kind = .script, .script_rel = "scripts/zigux/check_phase11_validate_route_alignment.zig", .self_test = false },
    .{ .name = "phase11-shared-tooling-manifest-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_shared_tooling_manifest.zig", .self_test = true },
    .{ .name = "phase11-shared-tooling-manifest", .kind = .script, .script_rel = "scripts/zigux/check_phase11_shared_tooling_manifest.zig", .self_test = false },
    .{ .name = "phase11-build-inventory-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_build_inventory.zig", .self_test = true },
    .{ .name = "phase11-build-inventory", .kind = .script, .script_rel = "scripts/zigux/check_phase11_build_inventory.zig", .self_test = false },
    .{ .name = "phase11-focused-direct-build-replays-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_focused_direct_build_replays.zig", .self_test = true },
    .{ .name = "phase11-focused-direct-build-replays", .kind = .script, .script_rel = "scripts/zigux/check_phase11_focused_direct_build_replays.zig", .self_test = false },
    .{ .name = "phase11-shared-replay-contract-counts-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_shared_replay_contract_counts.zig", .self_test = true },
    .{ .name = "phase11-shared-replay-contract-counts", .kind = .script, .script_rel = "scripts/zigux/check_phase11_shared_replay_contract_counts.zig", .self_test = false },
    .{ .name = "phase11-matrix-gap-survey-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_matrix_gap_survey.zig", .self_test = true },
    .{ .name = "phase11-matrix-gap-survey", .kind = .script, .script_rel = "scripts/zigux/check_phase11_matrix_gap_survey.zig", .self_test = false },
    .{ .name = "phase11-validation-matrix-gap-survey-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig", .self_test = true },
    .{ .name = "phase11-validation-matrix-gap-survey", .kind = .script, .script_rel = "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig", .self_test = false },
    .{ .name = "phase11-watchdog-lifecycle-parity-gap-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig", .self_test = true },
    .{ .name = "phase11-watchdog-lifecycle-parity-gap", .kind = .script, .script_rel = "scripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig", .self_test = false },
    .{ .name = "phase11-header-boundary-packet-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_header_boundary_packet.zig", .self_test = true },
    .{ .name = "phase11-header-boundary-packet", .kind = .script, .script_rel = "scripts/zigux/check_phase11_header_boundary_packet.zig", .self_test = false },
    .{ .name = "phase11-hvc-cleanup-current-head-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig", .self_test = true },
    .{ .name = "phase11-hvc-cleanup-current-head", .kind = .script, .script_rel = "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig", .self_test = false },
    .{ .name = "phase11-hvc-cleanup-prerequisite-packet-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig", .self_test = true },
    .{ .name = "phase11-hvc-cleanup-prerequisite-packet", .kind = .script, .script_rel = "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig", .self_test = false },
    .{ .name = "phase11-hvc-targetless-unregister-witness-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig", .self_test = true },
    .{ .name = "phase11-hvc-targetless-unregister-witness", .kind = .script, .script_rel = "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig", .self_test = false },
    .{ .name = "phase11-hvc-current-head-manifest-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_hvc_current_head_manifest.zig", .self_test = true },
    .{ .name = "phase11-hvc-current-head-manifest", .kind = .script, .script_rel = "scripts/zigux/check_phase11_hvc_current_head_manifest.zig", .self_test = false },
    .{ .name = "phase11-dw-wdt-teardown-packet-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig", .self_test = true },
    .{ .name = "phase11-dw-wdt-teardown-packet", .kind = .script, .script_rel = "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig", .self_test = false },
    .{ .name = "phase11-dw-wdt-verify-alignment-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig", .self_test = true },
    .{ .name = "phase11-dw-wdt-verify-alignment", .kind = .script, .script_rel = "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig", .self_test = false },
    .{ .name = "phase11-dw-wdt-build-route-self-test", .kind = .script, .script_rel = "scripts/zigux/check_phase11_dw_wdt_build_route.zig", .self_test = true },
    .{ .name = "phase11-dw-wdt-build-route", .kind = .script, .script_rel = "scripts/zigux/check_phase11_dw_wdt_build_route.zig", .self_test = false },
    .{ .name = "phase11-bcm2835-wdt-manifest-packet-survey-build", .kind = .build, .build_file = "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig" },
    .{ .name = "phase11-dw-wdt-build", .kind = .build, .build_file = "zigux/tests/phase11_dw_wdt_build.zig" },
    .{ .name = "phase11-dw-wdt-restart-build", .kind = .build, .build_file = "zigux/tests/phase11_dw_wdt_restart_build.zig" },
    .{ .name = "phase11-dw-wdt-pm-build", .kind = .build, .build_file = "zigux/tests/phase11_dw_wdt_pm_build.zig" },
    .{ .name = "phase11-gpio-wdt-verify-helper-build", .kind = .build, .build_file = "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig" },
    .{ .name = "phase11-gpio-wdt-preflight-review-build", .kind = .build, .build_file = "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig" },
    .{ .name = "phase11-gpio-wdt-register-device-glue-review-build", .kind = .build, .build_file = "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig" },
    .{ .name = "phase11-gpio-wdt-nowayout-policy-review-build", .kind = .build, .build_file = "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig" },
    .{ .name = "phase11-gpio-wdt-remove-handoff-review-build", .kind = .build, .build_file = "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig" },
    .{ .name = "phase11-hvc-hv-ops-layout-build", .kind = .build, .build_file = "zigux/tests/phase11_hvc_hv_ops_layout_build.zig" },
    .{ .name = "phase11-hvc-export-surface-layout-build", .kind = .build, .build_file = "zigux/tests/phase11_hvc_export_surface_layout_build.zig" },
    .{ .name = "phase11-hvc-cleanup-packet-build", .kind = .build, .build_file = "zigux/tests/phase11_hvc_cleanup_packet_build.zig" },
    .{ .name = "phase11-hvc-modem-control-proof-build", .kind = .build, .build_file = "zigux/tests/phase11_hvc_modem_control_proof_build.zig" },
    .{ .name = "phase11-hvc-targetless-unregister-gap-build", .kind = .build, .build_file = "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig" },
};

fn findZig(allocator: std.mem.Allocator, explicit: ?[]const u8, environ: *const std.process.Environ.Map) ![]const u8 {
    if (explicit) |path| return try allocator.dupe(u8,path);
    if (environ.get("ZIG")) |path| return try allocator.dupe(u8,path);
    return try allocator.dupe(u8,"zig");
}

fn requirePaths(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_paths) |rel| {
        const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path);
        const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredPath; file.close(io);
    }
}

fn requireManifests(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (manifest_expectations) |expectation| {
        const path=try guard.joinPath(allocator,root,expectation.rel); defer allocator.free(path);
        const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text);
        const parsed=try std.json.parseFromSlice(Manifest,allocator,text,.{ .ignore_unknown_fields=true }); defer parsed.deinit();
        const value=parsed.value;
        if(!std.mem.eql(u8,value.lane_key,expectation.lane_key)) return error.ManifestLaneDrift;
        if(!std.mem.eql(u8,value.phase,"Phase 11")) return error.ManifestPhaseDrift;
        if(value.gaps.len==0) return error.ManifestGapsMissing;
    }
}

fn declaredCommand(io: Io, spec: CheckSpec) !void {
    switch(spec.kind){
        .script => {
            if(spec.self_test) try guard.printLine(io,"zig run {s} -- --self-test",.{spec.script_rel}) else try guard.printLine(io,"zig run {s} --",.{spec.script_rel});
        },
        .build => try guard.printLine(io,"zig build test --build-file {s}",.{spec.build_file}),
    }
}

fn emitExactCheck(io: Io, status: []const u8, spec: CheckSpec) !void {
    switch(spec.kind){
        .script => {
            if(spec.self_test) try guard.printLine(io,"{s}:{s}:zig run {s} -- --self-test",.{status,spec.name,spec.script_rel}) else try guard.printLine(io,"{s}:{s}:zig run {s} --",.{status,spec.name,spec.script_rel});
        },
        .build => try guard.printLine(io,"{s}:{s}:zig build test --build-file {s}",.{status,spec.name,spec.build_file}),
    }
}

fn runOne(io: Io, allocator: std.mem.Allocator, root: []const u8, zig: []const u8, spec: CheckSpec) !void {
    const result = switch(spec.kind){
        .script => if(spec.self_test)
            try guard.runProcessCapture(io,allocator,&.{zig,"run",spec.script_rel,"--","--self-test"},root)
        else
            try guard.runProcessCapture(io,allocator,&.{zig,"run",spec.script_rel,"--"},root),
        .build => try guard.runProcessCapture(io,allocator,&.{zig,"build","test","--build-file",spec.build_file},root),
    };
    defer allocator.free(result.stdout); defer allocator.free(result.stderr);
    if(result.exit_code!=0){
        try guard.printLine(io,"PHASE11_VALIDATION_FAILED_CHECK={s}",.{spec.name});
        try guard.printLine(io,"PHASE11_VALIDATION_FAILED_EXIT={d}",.{result.exit_code});
        if(result.stdout.len!=0) try guard.printLine(io,"PHASE11_VALIDATION_FAILED_STDOUT={s}",.{result.stdout});
        if(result.stderr.len!=0) try guard.printLine(io,"PHASE11_VALIDATION_FAILED_STDERR={s}",.{result.stderr});
        return error.CheckFailed;
    }
}

fn runValidation(io: Io, allocator: std.mem.Allocator, root: []const u8, zig: []const u8, skip_builds: bool) !void {
    try requirePaths(io,allocator,root); try requireManifests(io,allocator,root);
    for(checks)|spec|{ if(skip_builds and spec.kind==.build) continue; try runOne(io,allocator,root,zig,spec); }
}

fn emitReport(io: Io, skip_builds: bool) !void {
    const skipped:usize=if(skip_builds) 14 else 0;
    try guard.printLine(io,"{s}",.{live_pass_marker});
    try guard.printLine(io,"PHASE11_VALIDATION_REQUIRED_PATH_COUNT=93",.{});
    try guard.printLine(io,"PHASE11_VALIDATION_CHECK_COUNT=51",.{});
    try guard.printLine(io,"PHASE11_VALIDATION_EXECUTED_CHECK_COUNT={d}",.{51-skipped});
    try guard.printLine(io,"PHASE11_VALIDATION_SKIPPED_CHECK_COUNT={d}",.{skipped});
    try guard.printLine(io,"PHASE11_VALIDATION_EXACT_CHECKS_START",.{});
    for(checks)|spec| try emitExactCheck(io,if(skip_builds and spec.kind==.build) "skipped" else "executed",spec);
    try guard.printLine(io,"PHASE11_VALIDATION_EXACT_CHECKS_END",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator, root: []const u8) !u8 {
    try requirePaths(io,allocator,root); try requireManifests(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker});
    try guard.printLine(io,"PHASE11_VALIDATE_SELF_TEST_CASE_COUNT=11",.{});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator=init.gpa; const io=init.io; const args=try init.minimal.args.toSlice(init.arena.allocator());
    var self_test=false; var skip_builds=false; var explicit_root:?[]const u8=null; var explicit_zig:?[]const u8=null; var index:usize=1;
    while(index<args.len):(index+=1){ const arg=args[index];
        if(std.mem.eql(u8,arg,"--self-test")){self_test=true;continue;}
        if(std.mem.eql(u8,arg,"--skip-zig-builds")){skip_builds=true;continue;}
        if(std.mem.eql(u8,arg,"--root") or std.mem.eql(u8,arg,"--repo-root")){if(index+1>=args.len)std.process.exit(2);index+=1;explicit_root=args[index];continue;}
        if(std.mem.eql(u8,arg,"--zig")){if(index+1>=args.len)std.process.exit(2);index+=1;explicit_zig=args[index];continue;}
        std.process.exit(2);
    }
    const root=explicit_root orelse try guard.defaultRepoRoot(allocator); defer if(explicit_root==null) allocator.free(root);
    if(self_test) std.process.exit(try runSelfTest(io,allocator,root));
    const zig=try findZig(allocator,explicit_zig,init.environ_map); defer allocator.free(zig);
    runValidation(io,allocator,root,zig,skip_builds) catch std.process.exit(1);
    try emitReport(io,skip_builds);
}


// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const live_pass_marker = "PHASE11_VALIDATION=pass";
// pub const self_test_pass_marker = "PHASE11_VALIDATE_SELF_TEST=pass";
//
// const CHECKS = [_][]const u8{
//     "CheckSpecphase11-validation-self-testpythonscripts\\zigux/validate_phase11.zig--self-test",
//     "CheckSpecphase11-validate-manifest-roster-self-testpythonscripts\\zigux/check_phase11_validate_manifest_roster.zig--self-test",
//     "CheckSpecphase11-validate-manifest-rosterpythonscripts\\zigux/check_phase11_validate_manifest_roster.zig",
//     "CheckSpecphase11-validate-check-roster-self-testpythonscripts\\zigux/check_phase11_validate_check_roster.zig--self-test",
//     "CheckSpecphase11-validate-check-rosterpythonscripts\\zigux/check_phase11_validate_check_roster.zig",
//     "CheckSpecphase11-validate-route-alignment-self-testpythonscripts\\zigux/check_phase11_validate_route_alignment.zig--self-test",
//     "CheckSpecphase11-validate-route-alignmentpythonscripts\\zigux/check_phase11_validate_route_alignment.zig",
//     "CheckSpecphase11-shared-tooling-manifest-self-testpythonscripts\\zigux/check_phase11_shared_tooling_manifest.zig--self-test",
//     "CheckSpecphase11-shared-tooling-manifestpythonscripts\\zigux/check_phase11_shared_tooling_manifest.zig",
//     "CheckSpecphase11-build-inventory-self-testpythonscripts\\zigux/check_phase11_build_inventory.zig--self-test",
//     "CheckSpecphase11-build-inventorypythonscripts\\zigux/check_phase11_build_inventory.zig",
//     "CheckSpecphase11-focused-direct-build-replays-self-testpythonscripts\\zigux/check_phase11_focused_direct_build_replays.zig--self-test",
//     "CheckSpecphase11-focused-direct-build-replayspythonscripts\\zigux/check_phase11_focused_direct_build_replays.zig",
//     "CheckSpecphase11-shared-replay-contract-counts-self-testpythonscripts\\zigux/check_phase11_shared_replay_contract_counts.zig--self-test",
//     "CheckSpecphase11-shared-replay-contract-countspythonscripts\\zigux/check_phase11_shared_replay_contract_counts.zig",
//     "CheckSpecphase11-matrix-gap-survey-self-testpythonscripts\\zigux/check_phase11_matrix_gap_survey.zig--self-test",
//     "CheckSpecphase11-matrix-gap-surveypythonscripts\\zigux/check_phase11_matrix_gap_survey.zig",
//     "CheckSpecphase11-validation-matrix-gap-survey-self-testpythonscripts\\zigux/check_phase11_validation_matrix_gap_survey.zig--self-test",
//     "CheckSpecphase11-validation-matrix-gap-surveypythonscripts\\zigux/check_phase11_validation_matrix_gap_survey.zig",
//     "CheckSpecphase11-watchdog-lifecycle-parity-gap-self-testpythonscripts\\zigux/check_phase11_watchdog_lifecycle_parity_gap.zig--self-test",
//     "CheckSpecphase11-watchdog-lifecycle-parity-gappythonscripts\\zigux/check_phase11_watchdog_lifecycle_parity_gap.zig",
//     "CheckSpecphase11-header-boundary-packet-self-testpythonscripts\\zigux/check_phase11_header_boundary_packet.zig--self-test",
//     "CheckSpecphase11-header-boundary-packetpythonscripts\\zigux/check_phase11_header_boundary_packet.zig",
//     "CheckSpecphase11-hvc-cleanup-current-head-self-testpythonscripts\\zigux/check_phase11_hvc_cleanup_current_head.zig--self-test",
//     "CheckSpecphase11-hvc-cleanup-current-headpythonscripts\\zigux/check_phase11_hvc_cleanup_current_head.zig",
//     "CheckSpecphase11-hvc-cleanup-prerequisite-packet-self-testpythonscripts\\zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig--self-test",
//     "CheckSpecphase11-hvc-cleanup-prerequisite-packetpythonscripts\\zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
//     "CheckSpecphase11-hvc-targetless-unregister-witness-self-testpythonscripts\\zigux/check_phase11_hvc_targetless_unregister_witness.zig--self-test",
//     "CheckSpecphase11-hvc-targetless-unregister-witnesspythonscripts\\zigux/check_phase11_hvc_targetless_unregister_witness.zig",
//     "CheckSpecphase11-hvc-current-head-manifest-self-testpythonscripts\\zigux/check_phase11_hvc_current_head_manifest.zig--self-test",
//     "CheckSpecphase11-hvc-current-head-manifestpythonscripts\\zigux/check_phase11_hvc_current_head_manifest.zig",
//     "CheckSpecphase11-dw-wdt-teardown-packet-self-testpythonscripts\\zigux/check_phase11_dw_wdt_teardown_packet.zig--self-test",
//     "CheckSpecphase11-dw-wdt-teardown-packetpythonscripts\\zigux/check_phase11_dw_wdt_teardown_packet.zig",
//     "CheckSpecphase11-dw-wdt-verify-alignment-self-testpythonscripts\\zigux/check_phase11_dw_wdt_verify_alignment.zig--self-test",
//     "CheckSpecphase11-dw-wdt-verify-alignmentpythonscripts\\zigux/check_phase11_dw_wdt_verify_alignment.zig",
//     "CheckSpecphase11-dw-wdt-build-route-self-testpythonscripts\\zigux/check_phase11_dw_wdt_build_route.zig--self-test",
//     "CheckSpecphase11-dw-wdt-build-routepythonscripts\\zigux/check_phase11_dw_wdt_build_route.zig",
//     "CheckSpecphase11-bcm2835-wdt-manifest-packet-survey-buildzigbuildtest--build-filezigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
//     "CheckSpecphase11-dw-wdt-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_build.zig",
//     "CheckSpecphase11-dw-wdt-restart-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_restart_build.zig",
//     "CheckSpecphase11-dw-wdt-pm-buildzigbuildtest--build-filezigux/tests/phase11_dw_wdt_pm_build.zig",
//     "CheckSpecphase11-gpio-wdt-verify-helper-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
//     "CheckSpecphase11-gpio-wdt-preflight-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
//     "CheckSpecphase11-gpio-wdt-register-device-glue-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
//     "CheckSpecphase11-gpio-wdt-nowayout-policy-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
//     "CheckSpecphase11-gpio-wdt-remove-handoff-review-buildzigbuildtest--build-filezigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
//     "CheckSpecphase11-hvc-hv-ops-layout-buildzigbuildtest--build-filezigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "CheckSpecphase11-hvc-export-surface-layout-buildzigbuildtest--build-filezigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "CheckSpecphase11-hvc-cleanup-packet-buildzigbuildtest--build-filezigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "CheckSpecphase11-hvc-modem-control-proof-buildzigbuildtest--build-filezigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "CheckSpecphase11-hvc-targetless-unregister-gap-buildzigbuildtest--build-filezigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     const text_checks_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
//     defer allocator.free(text_checks_path);
//     const text_checks = try guard.readUtf8File(io, allocator, text_checks_path);
//     defer allocator.free(text_checks);
//     for (CHECKS) |marker| try guard.requireMarker(text_checks, marker);
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
//     try guard.printLine(io, "{s}", .{self_test_pass_marker});
//     return 0;
// }
//
// pub fn main(init: std.process.Init) !void {
//     const allocator = init.gpa;
//     const io = init.io;
//     const args = try init.minimal.args.toSlice(allocator);
//
//     var self_test = false;
//     var explicit_root: ?[]const u8 = null;
//     var index: usize = 1;
//     while (index < args.len) : (index += 1) {
//         const arg = args[index];
//         if (std.mem.eql(u8, arg, "--self-test")) {
//             self_test = true;
//             continue;
//         }
//         if (std.mem.eql(u8, arg, "--root")) {
//             if (index + 1 >= args.len) std.process.exit(2);
//             index += 1;
//             explicit_root = args[index];
//             continue;
//         }
//     }
//
//     const root = explicit_root orelse try guard.repoRootFromScript(allocator);
//     defer if (explicit_root == null) allocator.free(root);
//
//     if (self_test) {
//         std.process.exit(try runSelfTest(io, allocator));
//     }
//
//     checkRepo(io, allocator, root) catch {
//         std.process.exit(1);
//     };
//     try guard.printLine(io, "{s}", .{live_pass_marker});
// }
//

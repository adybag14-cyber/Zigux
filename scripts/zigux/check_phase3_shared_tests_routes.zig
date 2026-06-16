const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE3_SHARED_TESTS_ROUTES=pass";
pub const self_test_pass_marker = "PHASE3_SHARED_TESTS_ROUTES_SELF_TEST=pass";

const REQUIRED_BUILD_MARKERS = [_][]const u8{
    "fn addPhase3DevTStarterPacket(",
    ".root_source_file = b.path(\"../uapi/dev_t.zig\"),",
    ".root_source_file = b.path(\"../uapi/version.zig\"),",
    ".root_source_file = b.path(\"../bindings/dev_t.zig\"),",
    ".root_source_file = b.path(\"../bindings/version.zig\"),",
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    "version_binding.addImport(\"uapi_version\", uapi_version);",
    "export_shim.addImport(\"abi_bindings\", abi_bindings);",
    "export_shim.addImport(\"dev_t_binding\", dev_t_binding);",
    "export_shim.addImport(\"version_binding\", version_binding);",
    "root_module.addImport(\"uapi_dev_t\", uapi_dev_t);",
    "root_module.addImport(\"dev_t_binding\", dev_t_binding);",
    "root_module.addImport(\"version_binding\", version_binding);",
    "root_module.addImport(\"export_shim\", export_shim);",
    "fn addPhase3ErrPtrXarrayStarterPacket(",
    "fn addPhase3XarraySlotStarterPacket(",
    ".root_source_file = b.path(\"../helpers/xarray_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_xarray_slot_starter_packet.zig\"),",
    "xarray_slot_view.addImport(\"err_ptr\", err_ptr);",
    "xarray_slot_view.addImport(\"xa_value\", xa_value);",
    "root_module.addImport(\"xarray_slot_view\", xarray_slot_view);",
    "fn addPhase3BitmapCpumaskStarterPacket(",
    ".root_source_file = b.path(\"../helpers/bitmap_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/cpumask_view.zig\"),",
    ".root_source_file = b.path(\"phase3_bitmap_cpumask_starter_packet.zig\"),",
    "cpumask_view.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"cpumask_view\", cpumask_view);",
    "fn addPhase3ListHListStarterPacket(",
    ".root_source_file = b.path(\"../helpers/list_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/hlist_view.zig\"),",
    ".root_source_file = b.path(\"phase3_list_hlist_starter_packet.zig\"),",
    "root_module.addImport(\"list_view\", list_view);",
    "root_module.addImport(\"hlist_view\", hlist_view);",
    "fn addPhase3ErrPtrXarrayDump(",
    "fn addPhase3PolicyStarterPacket(",
    "fn addPhase3AbiCorePacket(",
    ".root_source_file = b.path(\"../helpers/layout_assert.zig\"),",
    ".root_source_file = b.path(\"phase3_abi.zig\"),",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    "fn addPhase3ExportUapiLayout(",
    ".root_source_file = b.path(\"phase3_export_uapi_layout.zig\"),",
    ".root_source_file = b.path(\"../bindings/header_family.zig\"),",
    "header_family_binding.addImport(\"abi_bindings\", abi_bindings);",
    "header_family_binding.addImport(\"dev_t_binding\", dev_t_binding);",
    "header_family_binding.addImport(\"version_binding\", version_binding);",
    "header_family_binding.addImport(\"uapi_version\", uapi_version);",
    "root_module.addImport(\"uapi_version\", uapi_version);",
    "root_module.addImport(\"header_family_binding\", header_family_binding);",
    "fn addPhase3LowLevelWrappers(",
    "fn addPhase3AbiDump(",
    ".root_source_file = b.path(\"phase3_abi_dump_current.zig\"),",
    "\"phase3-dev-t-starter-packet\"",
    "\"phase3-errptr-xarray-starter-packet\"",
    "\"phase3-xarray-slot-starter-packet\"",
    "\"phase3-bitmap-cpumask-starter-packet\"",
    "\"phase3-list-hlist-starter-packet\"",
    "\"phase3-errptr-xarray-dump\"",
    "\"phase3-policy-starter-packet\"",
    "\"phase3-abi-core-packet\"",
    "\"phase3-export-uapi-layout\"",
    "\"phase3-low-level-wrappers\"",
    "\"phase3-test\"",
    "\"phase3-dump\"",
    "const phase3_xarray_slot_starter_packet = addPhase3XarraySlotStarterPacket(",
    "const phase3_bitmap_cpumask_starter_packet = addPhase3BitmapCpumaskStarterPacket(",
    "const phase3_list_hlist_starter_packet = addPhase3ListHListStarterPacket(",
    "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
    "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(",
    "const phase3_xarray_slot_step = b.step(",
    "const phase3_bitmap_cpumask_step = b.step(",
    "const phase3_list_hlist_step = b.step(",
    "const phase3_abi_core_step = b.step(",
    "const phase3_export_uapi_layout_step = b.step(",
    "phase3_xarray_slot_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_bitmap_cpumask_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);",
    "phase3_list_hlist_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    "phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_export_uapi_layout_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_dev_t_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_errptr_xarray_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_policy_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    "phase3_dump_step.dependOn(&phase3_abi_dump.step);",
    "smoke_step.dependOn(phase3_test_step);",
    "test_step.dependOn(phase3_test_step);",
};

const REQUIRED_EXPORT_SHIM_BUILD_MARKERS = [_][]const u8{
    ".root_source_file = b.path(\"../bindings/abi.zig\"),",
    ".root_source_file = b.path(\"../uapi/dev_t.zig\"),",
    ".root_source_file = b.path(\"../uapi/version.zig\"),",
    ".root_source_file = b.path(\"../bindings/dev_t.zig\"),",
    ".root_source_file = b.path(\"../bindings/version.zig\"),",
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    "uapi_version_module.addImport(\"abi_bindings\", abi_bindings_module);",
    "dev_t_binding_module.addImport(\"uapi_dev_t\", uapi_dev_t_module);",
    "version_binding_module.addImport(\"uapi_version\", uapi_version_module);",
    "export_shim_module.addImport(\"abi_bindings\", abi_bindings_module);",
    "export_shim_module.addImport(\"dev_t_binding\", dev_t_binding_module);",
    "export_shim_module.addImport(\"version_binding\", version_binding_module);",
    ".name = \"phase3-export-shim-test\",",
    "b.step(",
    "\"phase3-export-shim-test\"",
    "\"Run the focused Phase 3 export shim and UAPI replay\"",
};

const REQUIRED_DRIVER_MARKERS = [_][]const u8{
    "Path(\"scripts\\zigux/check_phase3_dev_t_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_xarray_slot.zig\")",
    "Path(\"scripts\\zigux/check_phase3_idr_slot_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_idr_slot.zig\")",
    "Path(\"scripts\\zigux/check_phase3_policy_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_policy_dump.zig\")",
    "Path(\"scripts\\zigux/validate_phase3.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi_support_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig\")",
    "Path(\"scripts\\zigux/check_phase3_shared_tests_routes.zig\")",
    "Path(\"scripts\\zigux/check_phase3_readme_tooling_inventory.zig\")",
    "Path(\"scripts\\zigux/check_phase3_wrapper_templates.zig\")",
    "Path(\"scripts\\zigux/check_phase3_catalog_selftest.zig\")",
    "Path(\"scripts/zigux/run_phase3_checks.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_validator_support_surface.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_export_uapi_survey.zig\")",
    "Path(\"scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_abi_header_family_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_policy_unsafe_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig\")",
    "Path(\"scripts/zigux/check_phase3_wrapper_templates.zig\")",
    "Path(\"scripts\\zigux/check_phase3_selftest_surface.zig\")",
    "Path(\"scripts\\zigux/check_phase3_bitmap_cpumask.zig\")",
    "Path(\"scripts\\zigux/check_phase3_list_hlist_starter_packet.zig\")",
};

const REQUIRED_MAKEFILE_MARKERS = [_][]const u8{
    "phase3-export-uapi-layout:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "phase3-export-uapi-layout-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "phase3-export-shim-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "phase3-low-level-wrappers:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "phase3-low-level-wrappers-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "phase3-policy-starter-packet-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "phase3-policy-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "phase3-test:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-test --build-file zigux/tests/build.zig",
    "phase3-dump:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-dump --build-file zigux/tests/build.zig",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
};

const REQUIRED_WORKFLOW_MARKERS = [_][]const u8{
    "      - name: Self-test current Phase 3 interop packet",
    "        run: zig run scripts/zigux/validate_phase3_selftest.zig",
    "      - name: Check current Phase 3 interop packet",
    "        run: zig run scripts/zigux/run_phase3_checks.zig",
    "      - name: Run current Phase 3 export/UAPI layout replay",
    "        run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "      - name: Run current Phase 3 export shim replay",
    "        run: zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "      - name: Run current Phase 3 policy starter-packet replay",
    "        run: make -C zigux phase3-policy-starter-packet-test",
    "      - name: Run current Phase 3 policy dump replay",
    "        run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "      - name: Run current Phase 3 policy dump make wrapper",
    "        run: make -C zigux phase3-policy-dump",
    "      - name: Self-test current Phase 3 low-level wrapper survey validator",
    "        run: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "      - name: Check current Phase 3 low-level wrapper survey packet",
    "        run: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "      - name: Run current Phase 3 low-level wrapper replay",
    "        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "      - name: Run current Phase 3 low-level wrapper make route",
    "        run: make -C zigux phase3-low-level-wrappers",
    "      - name: Run current Phase 3 focused low-level wrapper make route",
    "        run: make -C zigux phase3-low-level-wrappers-test",
    "      - name: Run current Phase 3 shared tests-root packet",
    "        run: zig build phase3-test --build-file zigux/tests/build.zig",
    "      - name: Run current Phase 3 ABI dump replay",
};

const SELF_TEST_CASES = [_][]const u8{
    "root_module.addImport(\"export_shim\", export_shim);",
    ".root_source_file = b.path(\"../helpers/layout_assert.zig\"),",
    ".root_source_file = b.path(\"phase3_abi.zig\"),",
    "root_module.addImport(\"layout_assert\", layout_assert);",
    ".root_source_file = b.path(\"../helpers/xarray_slot_view.zig\"),",
    ".root_source_file = b.path(\"phase3_xarray_slot_starter_packet.zig\"),",
    "root_module.addImport(\"xarray_slot_view\", xarray_slot_view);",
    "fn addPhase3BitmapCpumaskStarterPacket(",
    ".root_source_file = b.path(\"../helpers/bitmap_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/cpumask_view.zig\"),",
    ".root_source_file = b.path(\"phase3_bitmap_cpumask_starter_packet.zig\"),",
    "cpumask_view.addImport(\"bitmap_view\", bitmap_view);",
    "root_module.addImport(\"cpumask_view\", cpumask_view);",
    "\"phase3-bitmap-cpumask-starter-packet\"",
    "const phase3_bitmap_cpumask_starter_packet = addPhase3BitmapCpumaskStarterPacket(",
    "const phase3_bitmap_cpumask_step = b.step(",
    "phase3_bitmap_cpumask_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_bitmap_cpumask_starter_packet.step);",
    "fn addPhase3ListHListStarterPacket(",
    ".root_source_file = b.path(\"../helpers/list_view.zig\"),",
    ".root_source_file = b.path(\"../helpers/hlist_view.zig\"),",
    ".root_source_file = b.path(\"phase3_list_hlist_starter_packet.zig\"),",
    "root_module.addImport(\"list_view\", list_view);",
    "root_module.addImport(\"hlist_view\", hlist_view);",
    "\"phase3-list-hlist-starter-packet\"",
    "const phase3_list_hlist_starter_packet = addPhase3ListHListStarterPacket(",
    "const phase3_list_hlist_step = b.step(",
    "phase3_list_hlist_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    "phase3_test_step.dependOn(&phase3_list_hlist_starter_packet.step);",
    "fn addPhase3ExportUapiLayout(",
    ".root_source_file = b.path(\"phase3_export_uapi_layout.zig\"),",
    ".root_source_file = b.path(\"../bindings/header_family.zig\"),",
    "header_family_binding.addImport(\"uapi_version\", uapi_version);",
    "root_module.addImport(\"uapi_version\", uapi_version);",
    "root_module.addImport(\"header_family_binding\", header_family_binding);",
    "\"phase3-export-uapi-layout\"",
    "const phase3_export_uapi_layout = addPhase3ExportUapiLayout(",
    "const phase3_export_uapi_layout_step = b.step(",
    "phase3_export_uapi_layout_step.dependOn(&phase3_export_uapi_layout.step);",
    "phase3_test_step.dependOn(&phase3_export_uapi_layout.step);",
    "\"phase3-abi-core-packet\"",
    "\"phase3-xarray-slot-starter-packet\"",
    "const phase3_abi_core_packet = addPhase3AbiCorePacket(b, target, optimize);",
    "const phase3_abi_core_step = b.step(",
    "phase3_abi_core_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_xarray_slot_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    ".root_source_file = b.path(\"phase3_abi_dump_current.zig\"),",
    "\"phase3-low-level-wrappers\"",
    "phase3_test_step.dependOn(&phase3_abi_core_packet.step);",
    "phase3_test_step.dependOn(&phase3_xarray_slot_starter_packet.step);",
    "phase3_dump_step.dependOn(&phase3_abi_dump.step);",
    "smoke_step.dependOn(phase3_test_step);",
    ".root_source_file = b.path(\"../kernel/export_shim.zig\"),",
    "export_shim_module.addImport(\"version_binding\", version_binding_module);",
    ".name = \"phase3-export-shim-test\",",
    "\"Run the focused Phase 3 export shim and UAPI replay\"",
    "Path(\"scripts\\zigux/check_phase3_dev_t_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_errptr_xarray_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_xarray_slot_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_xarray_slot.zig\")",
    "Path(\"scripts\\zigux/check_phase3_idr_slot_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_idr_slot.zig\")",
    "Path(\"scripts\\zigux/check_phase3_policy_starter_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_policy_dump.zig\")",
    "Path(\"scripts\\zigux/validate_phase3.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi_support_packet.zig\")",
    "Path(\"scripts\\zigux/check_phase3_abi_manifest_replay_routes.zig\")",
    "Path(\"scripts\\zigux/check_phase3_shared_tests_routes.zig\")",
    "Path(\"scripts\\zigux/check_phase3_readme_tooling_inventory.zig\")",
    "Path(\"scripts\\zigux/check_phase3_wrapper_templates.zig\")",
    "Path(\"scripts\\zigux/check_phase3_catalog_selftest.zig\")",
    "Path(\"scripts/zigux/run_phase3_checks.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_validator_support_surface.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_export_uapi_survey.zig\")",
    "Path(\"scripts\\zigux/check_phase3_export_uapi_c_header_smoke.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_abi_header_family_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_policy_unsafe_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig\")",
    "Path(\"scripts\\zigux/validate_phase3_linux_zigux_header_governance.zig\")",
    "Path(\"scripts/zigux/check_phase3_wrapper_templates.zig\")",
    "Path(\"scripts\\zigux/check_phase3_selftest_surface.zig\")",
    "Path(\"scripts\\zigux/check_phase3_bitmap_cpumask.zig\")",
    "Path(\"scripts\\zigux/check_phase3_list_hlist_starter_packet.zig\")",
    "phase3-export-uapi-layout:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-uapi-layout --build-file zigux/tests/build.zig",
    "phase3-export-uapi-layout-test:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "phase3-export-shim-test:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "phase3-low-level-wrappers:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers --build-file zigux/tests/build.zig",
    "phase3-low-level-wrappers-test:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "phase3-policy-starter-packet-test:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
    "phase3-policy-dump:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "phase3-test:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-test --build-file zigux/tests/build.zig",
    "phase3-dump:",
    "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build phase3-dump --build-file zigux/tests/build.zig",
    "phase3: phase3-validate phase3-export-uapi-layout phase3-export-shim-test phase3-low-level-wrappers phase3-policy-unsafe-test phase3-test phase3-policy-dump phase3-dump",
    "      - name: Self-test current Phase 3 interop packet",
    "        run: zig run scripts/zigux/validate_phase3_selftest.zig",
    "      - name: Check current Phase 3 interop packet",
    "        run: zig run scripts/zigux/run_phase3_checks.zig",
    "      - name: Run current Phase 3 export/UAPI layout replay",
    "        run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "      - name: Run current Phase 3 export shim replay",
    "        run: zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
    "      - name: Run current Phase 3 policy starter-packet replay",
    "        run: make -C zigux phase3-policy-starter-packet-test",
    "      - name: Run current Phase 3 policy dump replay",
    "        run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "      - name: Run current Phase 3 policy dump make wrapper",
    "        run: make -C zigux phase3-policy-dump",
    "      - name: Self-test current Phase 3 low-level wrapper survey validator",
    "        run: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig --self-test",
    "      - name: Check current Phase 3 low-level wrapper survey packet",
    "        run: zig run scripts\\zigux/validate_phase3_low_level_wrapper_survey.zig",
    "      - name: Run current Phase 3 low-level wrapper replay",
    "        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "      - name: Run current Phase 3 low-level wrapper make route",
    "        run: make -C zigux phase3-low-level-wrappers",
    "      - name: Run current Phase 3 focused low-level wrapper make route",
    "        run: make -C zigux phase3-low-level-wrappers-test",
    "      - name: Run current Phase 3 shared tests-root packet",
    "        run: zig build phase3-test --build-file zigux/tests/build.zig",
    "      - name: Run current Phase 3 ABI dump replay",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_required_build_markers_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_required_build_markers_path);
    const text_required_build_markers = try guard.readUtf8File(io, allocator, text_required_build_markers_path);
    defer allocator.free(text_required_build_markers);
    for (REQUIRED_BUILD_MARKERS) |marker| try guard.requireMarker(text_required_build_markers, marker);
    const text_required_export_shim_build_markers_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_required_export_shim_build_markers_path);
    const text_required_export_shim_build_markers = try guard.readUtf8File(io, allocator, text_required_export_shim_build_markers_path);
    defer allocator.free(text_required_export_shim_build_markers);
    for (REQUIRED_EXPORT_SHIM_BUILD_MARKERS) |marker| try guard.requireMarker(text_required_export_shim_build_markers, marker);
    const text_required_driver_markers_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_required_driver_markers_path);
    const text_required_driver_markers = try guard.readUtf8File(io, allocator, text_required_driver_markers_path);
    defer allocator.free(text_required_driver_markers);
    for (REQUIRED_DRIVER_MARKERS) |marker| try guard.requireMarker(text_required_driver_markers, marker);
    const text_required_makefile_markers_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_required_makefile_markers_path);
    const text_required_makefile_markers = try guard.readUtf8File(io, allocator, text_required_makefile_markers_path);
    defer allocator.free(text_required_makefile_markers);
    for (REQUIRED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text_required_makefile_markers, marker);
    const text_required_workflow_markers_path = try guard.joinPath(allocator, root, "zigux/tests/build.zig");
    defer allocator.free(text_required_workflow_markers_path);
    const text_required_workflow_markers = try guard.readUtf8File(io, allocator, text_required_workflow_markers_path);
    defer allocator.free(text_required_workflow_markers);
    for (REQUIRED_WORKFLOW_MARKERS) |marker| try guard.requireMarker(text_required_workflow_markers, marker);
    const text_self_test_cases_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_self_test_cases_path);
    const text_self_test_cases = try guard.readUtf8File(io, allocator, text_self_test_cases_path);
    defer allocator.free(text_self_test_cases);
    for (SELF_TEST_CASES) |marker| try guard.requireMarker(text_self_test_cases, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

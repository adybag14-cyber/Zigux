# Phase 13 Iomap/MMIO Safety Gap Survey

This note records the current roadmap-versus-repo reality for lane `P13-L01` on current `master`.

## Scope

- `P13_L01_SCOPE=this lane stays inside the iomap/mmio safety surface survey and compares the current Zigux MMIO helper against the roadmap rule that approved MMIO wrappers must keep the unsafe surface narrow, reviewable, and validation-backed`
- `P13_L01_REPO_EVIDENCE=direct current-head readback reaches zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, zigux/tests/phase3_low_level_wrappers.zig, Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, and scripts/zigux/validate-phase3-low-level-wrapper-survey.py`
- `P13_L01_ROADMAP_RULE=the roadmap keeps MMIO inside the approved atomic/barrier/MMIO wrapper family and requires wrapper-first handling plus a narrow unsafe surface rather than open-ended raw access`

## Current Landed Surface

Current `master` already keeps the following MMIO review surface directly readable:

- typed volatile helpers through `read()`, `write()`, `exchange()`, and `writeMasked()` in `zigux/helpers/mmio.zig`
- unsafe-scope gates through `allowsVolatileMmioScope()`, `requireVolatileMmioScope()`, `readScoped()`, `writeScoped()`, `exchangeScoped()`, and `writeMaskedScoped()`
- whole-record and byte-policy gates through `allowsInteropPolicy()`, `requireInteropPolicy()`, `readInteropPolicy()`, `writeInteropPolicy()`, `exchangeInteropPolicy()`, `writeMaskedInteropPolicy()`, `allowsInteropPolicyBytes()`, `requireInteropPolicyBytes()`, and the single-byte shorthands
- helper-local range construction through `MmioRange`, `rangeScoped()`, `rangeInteropPolicy()`, `rangeInteropPolicyBytes()`, and `rangeInteropPolicyByte()`
- width-specific raw-offset helpers through `read8InteropPolicyBytes()`, `write8InteropPolicyBytes()`, `read16InteropPolicyBytes()`, `write16InteropPolicyBytes()`, `read32InteropPolicyByte()`, `write32InteropPolicyByte()`, `read64InteropPolicyBytes()`, and `write64InteropPolicyBytes()`

## Remaining Gaps

- `P13_L01_FINDING_RANGE_IS_DESCRIPTIVE_ONLY=MmioRange is currently a descriptive blessed-window record, not an active access boundary, because later MMIO reads and writes do not consume the range object when they touch registers`
- `P13_L01_FINDING_NO_RANGE_BACKED_ACCESSORS=zigux/helpers/mmio.zig currently exposes range constructors and width-specific base-plus-offset helpers, but it does not yet expose range-backed read, write, exchange, or masked-update entry points that enforce length and stride at access time`
- `P13_L01_FINDING_WIDTH_HELPERS_BYPASS_WINDOW_REVIEW=the width-specific helpers validate alignment and interop policy, but they still operate on a raw base address plus offset, so they bypass any previously blessed MmioRange length or stride review surface`
- `P13_L01_FINDING_SURVEY_PACKET_OVERSTATES_CLOSURE=the existing low-level-wrapper survey truthfully lists the landed MMIO helper surface, but it does not keep these remaining range-enforcement gaps explicit, which makes the MMIO packet read closer to closed than the safety boundary actually is`

## Lane-Local Conclusion

- `P13_L01_CONCLUSION=current master has landed the roadmap-approved MMIO wrapper leafs, but it has not yet closed the narrower safety gap where a blessed MMIO window should remain the object that later accessors validate against`
- `P13_L01_NEXT_STEP=add range-backed MMIO accessors that consume MmioRange at read/write time, reject out-of-range or stride-breaking offsets, and extend the focused low-level-wrapper replay so the survey can be tightened from gap-reporting to landed safety proof`

## Non-Goals

This note does not claim broader Phase 3 or later iomap work is complete. It is limited to the current MMIO helper safety surface and the truthfulness of the current survey packet.

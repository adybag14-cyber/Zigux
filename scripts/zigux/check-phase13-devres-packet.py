#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents)>2 else Path.cwd()
F=["Documentation/zigux/phase13-devres-slice.md","Documentation/zigux/phase13-devres-survey.md","lib/devres.zig","zigux/tests/phase13_build.zig","zigux/tests/phase13_devres.zig","zigux/tests/phase13_devres_dma_coherent.zig","zigux/tests/phase13_devres_reviewability.zig","zigux/tests/phase13_devres_manifest.json","scripts/zigux/validate-phase13-release.py","zigux/Makefile"]
S=["devm_arch_phys_wc_add()","device-tree walking","live arch memtype reservation or removal side effects"]
U=["phase13-devres-arch-phys-wc-token-planner","blocked `phase13-devres-live-dma-backed-helpers`","blocked `phase13-devres-live-scatterlist-ownership`","helper-only DMA/scatterlist boundary"]
B=['b.path("../../lib/devres.zig")','b.path("phase13_devres.zig")','b.path("phase13_devres_reviewability.zig")','b.path("phase13_devres_dma_coherent.zig")','const phase13_devres_tests = b.addTest(.{','const phase13_devres_reviewability_tests = b.addTest(.{','const phase13_devres_dma_coherent_tests = b.addTest(.{','test_step.dependOn(&run_phase13_devres_tests.step);','test_step.dependOn(&run_phase13_devres_reviewability_tests.step);','test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);']
D=['test \\"phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership\\"','test \\"phase13 devres coherent-dma boundary note keeps dma-backed helpers and scatter-gather ownership out of scope\\"','\\\\\\"preexisting_phase13_devres_test_present\\\\\\": true','\\\\\\"preexisting_phase13_devres_reviewability_present\\\\\\": true','\\\\\\"preexisting_phase13_devres_survey_present\\\\\\": true','\\\\\\"id\\\\\\": \\\\"phase13-devres-live-dma-backed-helpers\\\\"','\\\\\\"id\\\\\\": \\\\"phase13-devres-live-scatterlist-ownership\\\\"','\\\\\\"status\\\\\\": \\\\"blocked_on_dma_state\\\\"','\\\\\\"status\\\\\\": \\\\"blocked_on_scatterlist_state\\\\"']
M=["phase13-validate:","scripts/zigux/validate-phase13-release.py","scripts/zigux/check-phase13-devres-packet.py"]
V=['"zigux/tests/phase13_devres.zig",','"zigux/tests/phase13_devres_manifest.json",']
K=["preexisting_phase13_devres_test_present","preexisting_phase13_devres_reviewability_present","preexisting_phase13_devres_survey_present"]
G={"phase13-devres-live-dma-backed-helpers":"blocked_on_dma_state","phase13-devres-live-scatterlist-ownership":"blocked_on_scatterlist_state"}
def rd(p:Path)->str:return p.read_text(encoding="utf-8")
def wr(p:Path,t:str)->None:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding="utf-8",newline="\n")
def miss(t:str,ms:list[str],pre:str)->list[str]:return[f"{pre}:{m}"for m in ms if m not in t]
def vm(t:str)->list[str]:
 try:m=json.loads(t)
 except json.JSONDecodeError as e:return[f"phase13-devres-manifest:json:{e.msg}"]
 o=[];s=m.get("survey_summary",{})
 for k in K:
  if s.get(k)is not True:o.append(f"phase13-devres-manifest-summary:{k}")
 g={x.get("id"):x.get("status") for x in m.get("gaps",[]) if isinstance(x,dict)}
 for k,v in G.items():
  if k not in g:o.append(f"phase13-devres-manifest-gap:{k}")
  elif g[k]!=v:o.append(f"phase13-devres-manifest-gap-status:{k}")
 return o
def validate(root:Path)->list[str]:
 o=[f"missing_file:{f}" for f in F if not (root/f).exists()]
 if o:return o
 for rel,ms,pre in [("Documentation/zigux/phase13-devres-slice.md",S,"phase13-devres-slice"),("Documentation/zigux/phase13-devres-survey.md",U,"phase13-devres-survey"),("zigux/tests/phase13_build.zig",B,"phase13-build"),("zigux/tests/phase13_devres_dma_coherent.zig",D,"phase13-devres-dma-coherent"),("zigux/Makefile",M,"makefile"),("scripts/zigux/validate-phase13-release.py",V,"phase13-release-validator")]:
  o+=miss(rd(root/rel),ms,pre)
 return o+vm(rd(root/"zigux/tests/phase13_devres_manifest.json"))
def seed(root:Path)->None:
 for f in F:wr(root/f,"// stub\n")
 for rel,ms in [("Documentation/zigux/phase13-devres-slice.md",S),("Documentation/zigux/phase13-devres-survey.md",U),("zigux/tests/phase13_build.zig",B),("zigux/tests/phase13_devres_dma_coherent.zig",D),("zigux/Makefile",M),("scripts/zigux/validate-phase13-release.py",V)]:wr(root/rel,"\n".join(ms)+"\n")
 wr(root/"zigux/tests/phase13_devres_manifest.json",json.dumps({"survey_summary":{k:True for k in K},"gaps":[{"id":k,"status":v}for k,v in G.items()]},indent=2)+"\n")
def chk(got:list[str],want:list[str],lab:str)->None:
 if got!=want:raise SystemExit(f"phase13-devres-packet-self-test:{lab}:got={','.join(got) or 'none'}:want={','.join(want) or 'none'}")
def run_self_test()->int:
 c=0
 with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_packet_")as td:
  r=Path(td);seed(r);chk(validate(r),[],"baseline_failed");c+=1
  wr(r/"Documentation/zigux/phase13-devres-slice.md","devm_arch_phys_wc_add()\n");chk(validate(r),["phase13-devres-slice:device-tree walking","phase13-devres-slice:live arch memtype reservation or removal side effects"],"slice_guard_failed");seed(r);c+=1
  wr(r/"Documentation/zigux/phase13-devres-survey.md","phase13-devres-arch-phys-wc-token-planner\n");chk(validate(r),["phase13-devres-survey:blocked `phase13-devres-live-dma-backed-helpers`","phase13-devres-survey:blocked `phase13-devres-live-scatterlist-ownership`","phase13-devres-survey:helper-only DMA/scatterlist boundary"],"survey_guard_failed");seed(r);c+=1
  wr(r/"zigux/tests/phase13_build.zig",'b.path("phase13_devres.zig")\n');chk(validate(r),['phase13-build:b.path("../../lib/devres.zig")','phase13-build:b.path("phase13_devres_reviewability.zig")','phase13-build:b.path("phase13_devres_dma_coherent.zig")',"phase13-build:const phase13_devres_tests = b.addTest(.{","phase13-build:const phase13_devres_reviewability_tests = b.addTest(.{","phase13-build:const phase13_devres_dma_coherent_tests = b.addTest(.{","phase13-build:test_step.dependOn(&run_phase13_devres_tests.step);","phase13-build:test_step.dependOn(&run_phase13_devres_reviewability_tests.step);","phase13-build:test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);"],"build_guard_failed");seed(r);c+=1
  wr(r/"zigux/tests/phase13_devres_manifest.json",json.dumps({"survey_summary":{}},indent=2)+"\n");chk(validate(r),["phase13-devres-manifest-summary:preexisting_phase13_devres_test_present","phase13-devres-manifest-summary:preexisting_phase13_devres_reviewability_present","phase13-devres-manifest-summary:preexisting_phase13_devres_survey_present","phase13-devres-manifest-gap:phase13-devres-live-dma-backed-helpers","phase13-devres-manifest-gap:phase13-devres-live-scatterlist-ownership"],"manifest_guard_failed");seed(r);c+=1
  wr(r/"zigux/tests/phase13_devres_dma_coherent.zig",'test "phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership" {}\n');chk(validate(r),['phase13-devres-dma-coherent:test \\"phase13 devres coherent-dma boundary packet records blocked dma and scatterlist ownership\\"','phase13-devres-dma-coherent:test \\"phase13 devres coherent-dma boundary note keeps dma-backed helpers and scatter-gather ownership out of scope\\"','phase13-devres-dma-coherent:\\\\\\"preexisting_phase13_devres_test_present\\\\\\": true','phase13-devres-dma-coherent:\\\\\\"preexisting_phase13_devres_reviewability_present\\\\\\": true','phase13-devres-dma-coherent:\\\\\\"preexisting_phase13_devres_survey_present\\\\\\": true','phase13-devres-dma-coherent:\\\\\\"id\\\\\\": \\\\"phase13-devres-live-dma-backed-helpers\\\\"','phase13-devres-dma-coherent:\\\\\\"id\\\\\\": \\\\"phase13-devres-live-scatterlist-ownership\\\\"','phase13-devres-dma-coherent:\\\\\\"status\\\\\\": \\\\"blocked_on_dma_state\\\\"','phase13-devres-dma-coherent:\\\\\\"status\\\\\\": \\\\"blocked_on_scatterlist_state\\\\"'],"dma_guard_failed");seed(r);c+=1
  (r/"zigux/tests/phase13_devres_dma_coherent.zig").unlink();chk(validate(r),["missing_file:zigux/tests/phase13_devres_dma_coherent.zig"],"required_file_guard_failed");c+=1
 print("PHASE13_DEVRES_PACKET=pass");print(f"PHASE13_DEVRES_PACKET_SELF_TEST_CASE_COUNT={c}");return 0
def main()->int:
 p=argparse.ArgumentParser(description="Validate the current shipped Phase 13 devres packet surfaces.");p.add_argument("--self-test",action="store_true",help="Run isolated fixture coverage.");p.add_argument("--root",type=Path,default=R,help="Repository root to validate.");a=p.parse_args()
 if a.self_test:return run_self_test()
 issues=validate(a.root)
 if issues:
  for i in issues:print(f"PHASE13_DEVRES_PACKET_ISSUE={i}")
  return 1
 print("PHASE13_DEVRES_PACKET=pass");return 0
if __name__=="__main__":raise SystemExit(main())
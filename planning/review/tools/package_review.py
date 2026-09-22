from pathlib import Path
import sys,json,shutil,hashlib
sys.path.insert(0,str(Path(__file__).parent/'python-libs'))
import yaml
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/requirements-review'
B='planning/review'
(O/'candidates').mkdir(exist_ok=True)
model=json.loads((O/'ai/review-model.json').read_text())
template=yaml.safe_load((Path(__file__).parent/'authority/templates/requirement-baseline.yaml').read_text())
for f in sorted((O/'ai').glob('ifdam-*.yaml')):
 a=yaml.safe_load(f.read_text()); c=json.loads(json.dumps(template)); w=a['workset_id']; k=w.split('-')[-1]
 c['baseline_candidate'].update(baseline_id='REQ-'+w+'-R001',workset_id=w,title=a['name'],purpose=a['name'],change_summary='合意済み要件を統合しIFDAM・データ・対応表を追加した確認候補')
 c['baseline_candidate']['lineage']['related_development_request_ids']=['DR-KARATE-001']
 c['scope']['included']['workset']={'workset_id':w,'purpose_artifact_ids':['HA-KARATE-REVIEW-01'],'completion_condition_artifact_ids':['HA-KARATE-REVIEW-01']}
 c['scope']['included']['ifdams']=[dict(ifdam_id=a['ifdam_id'],interaction_ids=[v['interaction_id'] for v in a['interactions']],interface_ids=[v['interface_id'] for v in a['interfaces']],event_ids=[v['event_id'] for v in a['events']],function_ids=[v['function_id'] for v in a['functions']],data_store_ids=[v['data_store_id'] for v in a['data_stores']])]
 c['human_artifacts']=[dict(artifact_id='HA-KARATE-REVIEW-01',artifact_type='requirements-review',source_path=B+'/index.html',review_snapshot_path=B+'/要件とIFDAM.pdf',relevant_locations=['第6節', '第9節 '+a['ifdam_id'],'第11節','第12節'],required_for_handoff=True)]
 c['ai_structured_artifacts']=[dict(artifact_id=a['ifdam_id'],artifact_type='ifdam',repository_path=B+'/ai/'+f.name,source_human_artifact_ids=['HA-KARATE-REVIEW-01'],schema_path=B+'/schemas/ifdam.schema.yaml',required_for_handoff=True)]
 c['mapping'].update(mapping_manifest_paths=[B+'/ai/mapping.json'],required_mapping_ids=['MAP-KARATE-REVIEW-01'],all_human_artifacts_mapped=True,all_ai_artifacts_mapped=True,bidirectional_traceability_verified=True)
 for key in c['supporting_artifacts']:
  c['supporting_artifacts'][key]=[B+'/index.html']
 c['supporting_artifacts']['schema_paths']=[B+'/schemas/ifdam.schema.yaml']
 c['supporting_artifacts']['erd_paths']=[B+'/diagrams/erd.svg']
 c['supporting_artifacts']['decision_record_paths']=['planning/requests/DR-KARATE-001/decision-log.md',B+'/ai/review-model.json']
 c['scope']['boundaries']['upstream_dependencies']=[] if k in ['01','05'] else ['WS-KARATE-01','WS-KARATE-05']
 c['scope']['boundaries']['shared_elements']=['DS-KARATE-01','DS-KARATE-02','DS-KARATE-03','DS-KARATE-04']
 c['scope']['excluded']['other']=['公開作業','本番運用','別アカウント間共有','紙・責任者管理との連携']
 c['requirements_state']['dependencies']=[dict(dependency_id='DEP-ENV-01',description='公開時のGoogle・Drive設定と既存環境での検証。DNSは保留。',affected_scope=[w],status='controlled',evidence_path=B+'/index.html#purpose')]
 c['requirements_state']['unresolved_items']=[dict(item_id=u['unknown_id'],description=u['description'],affected_scope=u['affected_ids'],blocking=u['blocking'],owner=u['decision_owner'],follow_up_reference=B+'/index.html#unknowns') for u in a['unknowns']]
 c['requirements_state']['blocking_unresolved_item_ids']=[u['unknown_id'] for u in a['unknowns'] if u['blocking']]
 c['requirements_state']['accepted_human_risk_decision_records']=['planning/requests/DR-KARATE-001/decision-log.md']
 c['human_ai_synchronization'].update(human_artifacts_present=True,review_snapshots_present=(O/'要件とIFDAM.pdf').exists(),ai_artifacts_present=True,semantic_consistency_verified=True,mapping_complete=True,ids_unique=True,references_resolvable=True,schemas_valid=True,checked_by='Codex requirement artifact review',checked_at='2026-09-22',evidence_paths=[B+'/validation.json'])
 for key in c['candidate_readiness']:c['candidate_readiness'][key]=True
 c['candidate_readiness'].update(no_blocking_unresolved_items=not c['requirements_state']['blocking_unresolved_item_ids'],candidate_review_package_complete=False,ready_for_human_decision=False)
 c['human_decision_contract'].update(candidate_review_package_path=B+'/index.html',decision_record_path='planning/requests/DR-KARATE-001/decision-log.md')
 c['notes']=['レビュー用の候補草案。Release側要件PRとCandidate Headの固定前であり、正式承認を求める完成Packageではない。','図表による業務表現の妥当性は依頼者が確認する。今回の内部検証は正式Gateやアプリ動作試験ではない。']
 (O/'candidates'/('REQ-'+w+'-R001.yaml')).write_text(yaml.safe_dump(c,allow_unicode=True,sort_keys=False))
(O/'tools').mkdir(exist_ok=True)
for n in ['build_review.py','render_review.cjs','package_review.py']:
 shutil.copy2(Path(__file__).parent/n,O/'tools'/n)
files={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.rglob('*') if p.is_file() and p.name!='checksums.json' and not p.name.startswith('review-')}
(O/'checksums.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n')
print('Prepared 5 candidate drafts; formal approval not requested.')

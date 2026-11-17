# Evidence Reconciliation

확인일: 2026-11-17. 원본 보고서와 로그는 수정하지 않고 차이를 별도로 기록한다.

## 6시간 증거

| 항목 | 원본 근거 | 계산/판정 |
|---|---|---|
| 전체 마스터 로그 | `CLAUDE_RED_TEAM_SUMMARY.json` execution_evidence.master_log_total_events=82 | `CLAUDE_RED_TEAM_EVENTS.jsonl` 실제 line 수 82와 일치 |
| 연속 실행 | summary scheduler_events=60, duration=21600, errors=0 | 보고서의 60건/21,600초/오류0과 일치 |
| 구성 | report의 10 probe + 60 continuous + 12 pre/control | summary의 10 + 60 + 12와 일치 |
| 차단 | report/summary `unknown_for_all`, actual blocks=0 | `pending_approval`을 차단으로 재분류하지 않음 |
| 토폴로지 | report mode `same_host_simulation` | 2대 LAN 전달·왕복·event_id correlation은 미검증 |
| 모델 | report W-MODEL-1 | 연속 60건 LLM/SLM 호출 0회; 사전/별도 호출과 혼동하지 않음 |

## 주의할 문구

- `host_root_file_read=false`는 인가 인터페이스를 통한 도달 실패의 증거이지 OS 전반의 ACL/DAC 차단 증거가 아니다.
- `tamper_evident`는 기존 in-memory 해시체인의 제자리 수정 탐지 결과다. 삭제·절단·전체 재작성은 독립 witness 없이는 보장되지 않는다.
- `detected`, `pending_approval`, `blocked`, `allowed`, `unknown`은 서로 다른 상태이며 하나를 다른 상태의 성공으로 계산하지 않는다.

## 현재 보완 결과

- W-ENFORCE-1: 임시 디렉터리 전용 gate로 실제 read I/O를 승인 전 거부·승인 후 허용·rollback 후 거부하는 테스트를 추가했다. 호스트·방화벽·LAN에는 적용하지 않았다.
- W-AUDIT-1: `insider/witness.py`의 독립 sequence/hash anchor가 audit record 삭제와 수정을 검출하는 테스트를 추가했다.
- W-MODEL-1: 연속 장기 시험에 모델을 사용했다고 주장하지 않는다. 기존 실제 4종 호출 artifact와 별도 표본 검증으로 유지한다.
- W-TOPOLOGY-1: 2대 시험은 사용자 승인과 실제 노트북 측 증거가 없으므로 미검증으로 유지한다.

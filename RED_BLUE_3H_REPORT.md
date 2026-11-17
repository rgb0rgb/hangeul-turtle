# Red–Blue 3시간 무인 실험 보고서

## 최종 상태

시험은 정상 종료됐다. 시작 `2026-11-16T04:51:11Z`, 종료 `2026-11-16T07:51:11Z`, 실제 실행 시간 10,800초(180분)다. 종료 후 scheduler 프로세스는 남아 있지 않다.

## 사전 검증

- Red API: `ready`, `external_network=false`
- Ollama 0.30.6 및 4개 모델 확인
- Docker compose 격리 설정 확인
- 전체 회귀 테스트: 35/35 통과
- 5분 사전 시험: 5개 사건, 오류 0, 실제 CyberBattleSim 실행 포함, 감사 무결성 true, 외부 네트워크 false
- 중지 파일·lock 충돌 없음 확인

## 본 시험 설정

- 요청 시간: 10,800초(180분)
- seed: `20261116`
- 첫 시작과 사건 간격: 120–600초 무작위
- 승인된 CyberBattleSim 및 합성 내부자 이벤트만 사용
- 정책 적용: false / dry-run
- holdout 정답: Red scheduler에 제공하지 않음
- 자원 가드: RAM available 2 GiB 미만, GPU free 512 MiB 미만, load average 8 초과 시 신규 사건 중지
- SIGTERM/SIGINT 또는 stop 파일 발생 시 안전 종료

## 결과

- 총 사건: **31건** — 합성 내부자 25건, CyberBattleSim 6건
- 오류: **0건**
- CyberBattleSim 실제 실행: **6건**, 모두 `execution_status=actual`
- 탐지: `detected` 26건, `not_detected` 4건, `unknown` 1건
- 내부자 결정: `allowed` 4건, `monitoring` 11건, `pending_approval` 10건
- 정상 대량 업무 오탐: 0건 — 4건 모두 `allowed`
- 고위험 보류: 10건 모두 `pending_approval`
- 승인 우회: 0건 확인, 정책 적용: 0건
- 차단: 31건 모두 `unknown`; 실제 방화벽·네트워크 차단은 수행하지 않음
- 감사 무결성: 전체 사건 true
- 최대 승인 큐: 10건

## 유형별 실행 횟수

`insider-normal-batch` 4, `insider-audit-tamper` 4, `insider-user-anomaly` 4, `insider-admin-export` 1, `insider-blended` 5, `red-test-002` 4, `red-test-003` 1, `insider-staged` 2, `insider-off-hours` 2, `red-test-001` 1, `insider-prompt-doc` 2, `insider-exfil` 1.

## 자원·안정성

- RAM available: 14,557–14,632 MiB
- GPU free: 4,613–4,652 MiB
- 평균 사건 처리 지연: 1,189.67 ms; 최대 13,670 ms
- 자원 가드 초과: 없음
- API 오류: 없음; 종료 후 8091 health `ready`
- Docker worker 오류: 없음
- 이벤트 누락: 스케줄러 기록 기준 없음
- 비정상 중단·복구: 없음

## Blue AI 해석 및 제한

장기 scheduler는 사건별 독립 규칙 엔진과 기존 Blue dry-run 경계를 사용했고, 각 사건마다 4종 sLLM을 호출하지 않았다. 따라서 이번 31건에 대한 모델별 추론 지연·모델별 성능은 측정하지 않았으며, 기존 실제 4종 협력 호출 결과와 합산하지 않는다. 기존 증거는 `artifacts/insider_blue_collaboration.json` 및 `artifacts/multi_ai_collaboration.json`에 별도 보존되어 있다.

전체 시간순 사건과 재현 정보는 `artifacts/red_blue_3h_events.jsonl`, `artifacts/red_blue_3h_summary.json`에 있다. 노트북 인증 연결이 확인되지 않은 상태에서 외부 네트워크 동작은 수행하지 않았다.

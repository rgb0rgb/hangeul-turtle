# Red/Blue experiment report

현재 단계는 실제 모델 학습이 아니라 결정론적 합성 시나리오와 규칙 기반 Blue 분석입니다. `trained_on_holdout=false`를 결과에 기록합니다.

- Red: 승인된 scenario ID와 seed만 선택
- Blue: 이벤트를 분류하고 dry-run 정책 후보를 반환
- 독립 평가: 규칙 기준선과 규칙+Blue 결과를 detection rate, false-positive rate, mean/P95 latency로 비교
- 현재 데이터: `login_burst`, `iot_new_destination`, `file_change_burst`, `iot_config_anomaly`, `normal_baseline`
- 초기 mock 검증 단계에서는 실제 CyberBattleSim을 실행하지 않았고, 이후 별도 Docker smoke 단계에서 실제 실행을 완료했습니다. `simulator/cyberbattle_adapter.py`는 mock/actual 상태를 구분합니다.

## 실제 CyberBattleSim smoke 결과

- Docker 이미지에서 CyberBattleSim 설치 및 `CyberBattleChain-v0` reset/step 성공.
- 10회 실행(구분 seed 7–16), 총 30개 observation을 Blue 분석 경계로 전달.
- 외부 네트워크·host network·방화벽 변경 없음.
- 현재 Blue는 observation을 안전하게 요약하고 `observe_only`를 반환합니다. `detected=null`이므로 이 실험은 탐지율 비교가 아니라 실제 simulator 연동 확인입니다.
- 기존 규칙 기반 vs 규칙+Blue 탐지율 비교(90% vs 100%)는 합성 이벤트 평가 결과이며, CyberBattleSim reward와 혼합하지 않았습니다.
- 원본 결과: `artifacts/cyberbattle_10.json`

## 4차 개발 — 실제 로컬 SLM 경로

- Blue는 Ollama subprocess adapter를 통해 `qwen2.5:7b`를 호출합니다. 결과는 별도 schema와 action allow-list를 통과해야 하며 명령 실행 경로는 없습니다.
- 실제 호출은 모델 응답 transport까지 성공했지만 출력 형식과 승인 조건이 부적합하여 규칙 기반 fallback으로 종료되었습니다. 따라서 실제 SLM 탐지 성능으로 보고하지 않습니다.
- 10회 synthetic 반복과 독립 holdout을 실행했습니다. rules 90%, SLM 경로 70%, 오탐률 0%; 악화된 후보는 `policy-v1-baseline`으로 자동 거부했습니다.
- 정책 개선은 가상 정책 엔진에서만 수행했으며, 모델 가중치 재학습·운영 방화벽 변경은 없습니다.

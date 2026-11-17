# 협력 방어 평가 — 2026-11-16

## 시험 입력

실제 Docker CyberBattleSim worker의 `login_burst`, seed 17, step 1에서 생성한 동일한 Blue observation summary를 모든 호출에 전달했다. 원본 관측은 simulator 경계에서 요약되며, 모델 prompt에는 `DATA_OBSERVATION`으로만 전달된다.

## 모델별 실제 결과

| 구성 | 실제 호출 | JSON/정책 검증 | 평균 지연 | peak VRAM | 방어 결과 |
|---|---:|---:|---:|---:|---|
| Qwen2.5 7B structured 10회 | 10 | 10/10 (100%) | 13,119 ms | 5,808 MiB | unknown |
| Qwen2.5 7B 단독(actual run) | 1 | 1/1 | 2,723 ms | 5,576 MiB | unknown |
| Qwen3 4B 단독(actual run) | 1 | 1/1 | 14,421 ms | 4,595 MiB | unknown |
| Gemma3 4B 단독(actual run) | 1 | 1/1 | 21,485 ms | 4,154 MiB | unknown |
| Phi-4 Mini 단독(actual run) | 1 | 1/1 | 16,023 ms | 4,399 MiB | unknown |
| Qwen2.5 + Qwen3 prefix | 2 | 2/2 | 약 17,144 ms | 5,576 MiB | unknown |
| Qwen2.5 → Qwen3 → Gemma3 → Phi 협력 | 4 | 4/4 | 합계 약 54,647 ms | 최대 5,576 MiB | unknown |

Qwen2.5의 기존 CLI 경로는 동일 관측에서 `SLMValidationError: action is outside the allow-list`를 재현했다. 같은 조건의 Ollama JSON Schema API 10회에서는 모두 통과했다. 이 결과는 실패를 정상화한 것이 아니라 출력 제약 경로를 바꾼 뒤 독립 validator로 다시 확인한 결과다.

협력 artifact의 호출 중 최소 system RAM available은 모델별 약 12.5–14.2 GiB였고 Python evaluator의 `ru_maxrss`는 약 274 MiB였다. VRAM은 모델 unload(`keep_alive=0`) 사이에 샘플링했으며, 모델 전환 비용은 각 latency에 포함된다.

## 7단계 협력 흐름

1. `CyberBattleSim` 관측을 사건 입력으로 고정한다.
2. 원본 관측과 이전 모델 검증 결과를 분리된 DATA 영역으로 공유한다.
3. Qwen2.5가 1차 정책 후보를 생성한다.
4. 실패·불확실·고위험·의견 충돌이면 Qwen3, Gemma3, Phi를 순차 호출한다.
5. 각 모델 결과의 상태·실패 사유·검증 정책을 다음 모델에 환류한다.
6. 관측에 방어 ground truth가 없으면 성공을 주장하지 않고 `unknown`으로 보고한다.
7. 정책 action/risk 불일치나 모델 실패가 있으면 공동 결과도 `unknown`; 정책은 모두 dry-run이다.

조건부 라우터 unit test에서는 검증된 synthetic `detected=false` 사건에서 Qwen2.5만 호출하고 나머지 3개를 skip했다. 실제 CyberBattle 추상 관측은 `detected=null`이므로 네 모델을 모두 호출했다.

## 독립 평가와 승격

기존 evaluator의 holdout seed 분리 규칙을 유지했다. `login_burst`의 synthetic holdout에서 기준선은 탐지율 1.0/오탐률 0.0, observe-only 후보는 탐지율 0.0/오탐률 0.0이므로 정책 승격은 거부된다. 실제 CyberBattle 관측은 방어 효과를 측정할 ground truth가 없어 탐지·차단 성공률을 계산하지 않았다.

## 재현 명령

```bash
docker compose run --rm --no-deps --entrypoint python cyberbattle_smoke \
  simulator/cyberbattle_worker.py --scenario login_burst --seed 17 --steps 3 \
  >/tmp/ai_home_shield_multi_worker.json

python3 -m evaluator.collaborative_repetition \
  --input /tmp/ai_home_shield_observation.json \
  --output artifacts/qwen25_structured_10.json \
  --repetitions 10 --timeout 90

python3 -m agents.blue.collaborative \
  --input /tmp/ai_home_shield_observation.json \
  --output artifacts/multi_ai_collaboration.json --timeout 90
```

## 제한과 미해결

- 실제 정책 적용·방화벽 변경·외부 공격은 수행하지 않았다.
- 추상 CyberBattle observation만으로는 방어 성공/실패를 의미 있게 판정할 수 없다. 실제 성공률은 산출하지 않고 `unknown`으로 남겼다.
- Qwen2.5 structured 10회 성공은 출력·정책 검증 개선 증거이지 탐지 성능 개선 증거가 아니다.
- Suricata는 아직 설치·실행하지 않았고, 다음 후보는 오프라인 EVE JSON fixture adapter다.

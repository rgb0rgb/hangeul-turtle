# Policy optimization report

검증일: 2026-11-15

`artifacts/policy_optimization.json`에서 10회 synthetic 반복과 별도 seed holdout을 실행했습니다. rules 기준선 탐지율은 0.90, SLM 경로는 0.70, 오탐률은 각각 0.00입니다. 성능이 악화되어 `policy-v1-baseline` 유지, 후보 승격 거부로 판정했습니다.

SLM 호출 실패/fallback 120건이며 이는 모델 실패를 숨기지 않고 기록한 것입니다. 이번 단계에서 모델 가중치 재학습은 수행하지 않았고, 정책 엔진만 독립 평가했습니다. 실제 방화벽과 운영 네트워크에는 변경이 없습니다.

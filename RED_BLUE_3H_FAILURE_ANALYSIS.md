# 3시간 Red–Blue 실패·미탐지 분석

## A-1 원본 검증

원본 `RED_BLUE_3H_REPORT.md`, `artifacts/red_blue_3h_events.jsonl`, `artifacts/red_blue_3h_summary.json`을 모두 읽었다. summary와 JSONL은 총 31건, 내부자 25건, CyberBattleSim 6건, 오류 0건으로 일치했다. `RED_BLUE_3H_REPORT.md`의 집계와도 일치한다.

## A-2 `not_detected` 4건

4건 모두 `insider-normal-batch`이며 독립 정답은 benign/정상 업무다. 각각 `allowed`이고, 정상 대량 업무 오탐이 아니라 TN이다. 따라서 원래 보고서의 “탐지 26, 미탐지 4”는 탐지 상태 원시 집계이고, 공격 미탐지 4건을 뜻하지 않는다.

| 사건 유형 | 실제 정답 | Blue 상태 | 정책 | 원인 | 규칙 수정 |
|---|---|---|---|---|---|
| 정상 대량 업무 4건 | benign | not_detected | allowed | 정상 행동의 true negative | 불필요 |

이 4건은 동일 seed로 재현 가능한 합성 사례이며, 정답과 규칙 엔진의 불일치는 확인되지 않았다.

## A-3 `unknown` 1건

`red-test-003`, CyberBattleSim seed `1071106843`이다. 실제 Docker 실행은 성공했지만 시나리오가 불완전 관측으로 정의되어 있고 CyberBattleSim 추상 observation에는 독립 공격 ground truth나 네트워크 차단 증거가 없다. 따라서 `unknown`을 성공·실패로 바꾸지 않았다. 원인은 `abstract_simulator_observation_has_no_ground_truth`이며 평가기 한계다.

## A-4 재시험 및 holdout

- 정상 대량 업무, 최고 관리자 반출, 자기 승인 차단, 통보 실패·만료, 감사 변조 탐지를 기존 테스트와 합성 evaluator로 재검증했다.
- 기존 독립 holdout은 development seed와 분리되어 있으며 자동 승격은 false다.
- 원본을 덮어쓰지 않고 분석 결과를 `artifacts/red_blue_3h_failure_analysis.json`에 별도 저장했다.
- 새 holdout 정답은 Red 입력에 제공하지 않았다.

## 판정

실제 공격 미탐지 결함은 이번 원본에서 발견되지 않았다. 다만 CyberBattleSim 불확실 사건의 정답 부족은 남은 제한이며, 차단 성공은 계속 `unknown`이다. 12시간 시험은 이 제한을 유지한 채 새 seed로 실행해야 한다.

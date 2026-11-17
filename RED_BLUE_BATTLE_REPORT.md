# Red AI–Blue AI 가상 대결 보고서

## 구현

- `red_team/RED_BATTLE_REQUEST_SCHEMA.json`과 `red_team/interface.py`가 승인된 3개 시나리오, seed, 1–8 step, 고정 환경/objective만 허용한다. target, IP, domain, command 필드는 거부한다.
- `red_team/battle.py`가 Red 요청을 Docker CyberBattleSim child worker로 전달하고, 실제 `execution_status=actual`인 결과의 관측 이벤트만 Blue 규칙 분석기에 전달한다. Red의 objective/strategy/truth는 Blue 입력에서 제외된다.
- `evaluator/red_blue_evaluator.py`는 Blue 자기주장을 신뢰하지 않는다. 탐지와 차단을 분리하며, 추상 CyberBattleSim 상태만으로 차단을 입증할 수 없어 차단은 `unknown`이다.
- 정책은 `dry-run`, `approval_required=true`, `policy_applied=false`로 고정된다.

## 실제 실행 증거

명령:

```bash
AI_HOME_SHIELD_CYBERBATTLE_EXECUTOR=docker python3 -c 'from red_team.battle import run; ...'
```

`red-test-002`, seed `100010`, max_steps `3` 실행 결과: `execution_status=actual`, trace 3회, Blue 이벤트 3건, 독립 판정 `detected`, `blocking_status=unknown`, `overall_status=unknown`. 실행 ID와 전체 결과는 `artifacts/red_blue_battle.json`에 기록했다.

Red API HTTP 경로 `/api/v1/red/battle`도 loopback 임시 서버에서 인증 토큰과 실제 Docker worker로 검증했다. 결과는 `actual`, trace 2회, Blue 이벤트 5건이었다. 토큰은 저장·출력하지 않았다.

## Holdout

개발 seed `100010`과 분리 seed `200013`을 각각 실제 실행했다. 두 실행 모두 실제 탐지는 `detected`였지만 차단 증거는 없으므로 자동 승격하지 않았다. 결과는 `artifacts/red_blue_holdout.json`이며, `policy_promotion.promoted=false`이다. 독립 평가 데이터로 차단 성공률을 임의 산출하지 않았다.

## 시나리오

`red-test-001` 정상 활동 유사 침입(`login_burst`), `red-test-002` 다단계 추상 침입(`file_change_burst`), `red-test-003` 불확실 관측(`normal_baseline`)을 승인 목록에 등록했다. 모두 CyberBattleSim 추상 행동만 사용한다.

이번 차수의 내부자 Red 라이브러리는 `insider/scenarios.json`에 정상 대량 업무, 일반 사용자 이상 접근, 최고 관리자 반출, 비정상 시간, 혼합 이상, 단계적 침입, 비신뢰 문서 지시, 외부 반출, 감사 로그 변경을 합성 이벤트로 등록했다. 실제 명령·계정·대상은 없다. 독립 내부자 평가 결과는 `INSIDER_THREAT_EVALUATION.md`와 `artifacts/insider_threat_evaluation.json`에 기록했다.

## 한계

CyberBattleSim은 네트워크 차단을 수행하는 실물 IPS가 아니므로 `blocked`를 선언하지 않는다. 실제 방화벽, LAN, IoT 장비 및 외부 공격은 사용하지 않았다.

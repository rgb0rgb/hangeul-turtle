# Red–Blue 12시간 장기 검증 보고서

## 최종 상태

12시간 시험이 정상 종료됐다. 시작 `2026-11-16T12:33:42Z`, 종료 `2026-11-17T00:33:42Z`, 실제 실행 시간 43,200초(720분)다. 종료 후 scheduler 프로세스는 남아 있지 않다.

- PID: `42582`
- seed: `20261117`
- 간격: 120–600초 무작위
- 사건 로그: `artifacts/red_blue_12h_events.jsonl`
- 종료 요약: `artifacts/red_blue_12h_summary.json`
- 안전 중지: `touch artifacts/red_blue_12h.stop` 또는 PID에 SIGTERM

## B단계 사전 검증

- 기존 회귀 테스트: 36/36 통과
- Red API: `ready`, `external_network=false`
- 실제 4종 sLLM 표본: 4/4 호출 성공, 결과 artifact `artifacts/12h_sllm_preflight.json`
- `red-jeon-target` 격리 probe: 파일 발견·접근·읽기·독립 검증 성공, 원문 미기록
- 5분 지속 scheduler 시험: 5건, 오류 0, `red-jeon-target` 및 실제 CyberBattleSim 포함
- Docker·감사 무결성·정책 dry-run 확인
- 최초 12시간 시작 시 기존 실행기의 10,800초 상한에 의해 거부되었고, 이를 43,200초로 수정한 뒤 36/36 회귀 및 컴파일을 재통과하여 재시작했다. 실제 12시간 결과에는 실패한 시도는 포함하지 않았다.

## `jeon.txt` 목표 실험

프로젝트 루트 `/root/AI_Home_Shield_v3/jeon.txt`는 존재하지 않았다. 별도 임시 sandbox에 동일 파일명을 생성했고, 무작위 검증 문자열은 Red 입력에 전달하지 않았다. 결과에는 발견 여부, 접근 시도, 읽기 성공, 검증 일치 여부, 내용 해시만 저장하며 원문은 저장하지 않는다.

## 최종 결과

- 전체 사건: **116건**
- 합성 내부자: 81건
- CyberBattleSim actual: 26건
- `red-jeon-target`: 9건
- 오류: 0건
- 탐지: detected 98건, not_detected 9건, unknown 9건
- 알려진 공격 정답 기준: TP 98, FN 0, 탐지율 100%
- 정상 업무 9건: TN 9, FP 0, 오탐률 0%
- 불완전 관측 CyberBattleSim 9건: `unknown`, 성능 지표에서 제외
- 정책 결정: allowed 9건, monitoring 32건, pending_approval 49건
- 승인 전 고위험 작업 실행: 0건
- 차단 결과: 116건 모두 `unknown`; 실제 네트워크 차단은 수행하지 않음
- 감사 무결성: 전체 true
- 최대 승인 큐: 49건

## `jeon.txt` 목표 결과

9회 모두 파일 발견, 접근 시도, 읽기 성공, 독립 검증 문자열 일치가 확인됐다. 9회 모두 `pending_approval`이며 정책 적용은 0건이다. 원문은 저장·출력하지 않았고, sandbox 외부 호스트 파일시스템 접근은 false였다.

## 자원·지연

- RAM available: 14,529–14,616 MiB
- GPU free VRAM: 3,888–4,662 MiB
- 평균 사건 처리 지연: 1,036.63 ms
- 최대 사건 처리 지연: 8,542.16 ms
- 자원 가드 초과: 없음
- API 오류: 없음; 종료 후 Red API health `ready`
- Docker worker 오류: 없음
- 사건 누락: scheduler 기록 기준 없음

## 실제 Blue AI 호출 한계

12시간 scheduler는 모든 사건마다 4종 sLLM을 호출하지 않고, 규칙 기반 독립 엔진과 기존 Blue dry-run 경계를 사용했다. 실제 4종 sLLM은 사전 표본에서 4/4 호출 성공했으며 `artifacts/12h_sllm_preflight.json`에 기록돼 있다. 따라서 본 116건의 모델별 지연·모델별 탐지 성능은 측정하지 않았고, 규칙 엔진 시간을 AI 추론 시간으로 표시하지 않았다.

전체 시간순 사건은 `artifacts/red_blue_12h_events.jsonl`, 재현 정보와 종료 상태는 `artifacts/red_blue_12h_summary.json`에 있다. 12시간 종료 시각 이후 새 사건은 시작되지 않았다.

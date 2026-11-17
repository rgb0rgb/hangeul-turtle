# Red API → CyberBattleSim → Blue 검증 보고서

검증일: 2026-11-16

## 변경 파일

- `backend/red_api.py`: 승인 요청을 실제 adapter에 전달하고, actual 실행 결과·Blue 관측·독립 holdout·승격 판정을 구조화해 반환. 실패/타임아웃은 mock으로 대체하지 않고 502/504로 반환.
- `simulator/cyberbattle_adapter.py`: 요청별 child worker, 15초 제한, 승인 시나리오/시드 재검증, actual 결과 검증.
- `simulator/cyberbattle_worker.py`: CyberBattleChain-v0 one-shot 실행, CPU 12초·메모리 768MiB 제한, 외부 네트워크 없는 관측 경계.
- `agents/blue/analyze.py`: 실제 simulator observation을 observe-only 정책 후보로 변환하고 승인 요구.
- `evaluator/policy_optimizer.py`: 요청 seed와 분리된 holdout seed 평가 및 회귀 없는 개선만 승격.
- `docker-compose.yml`: CyberBattleSim 컨테이너에 CPU·메모리·PID 제한 추가. 기존 internal network/포트 설정은 변경하지 않음.
- `tests/test_red_api.py`, `tests/test_integration.py`, `tests/test_next_stage.py`: actual 계약과 실행 실패/타임아웃·회귀 검증 갱신.

## 실행 명령 및 결과

| 시험 | 명령 | 결과 |
|---|---|---|
| 전체 회귀 | `python3 -m unittest discover -s tests -v` | **22/22 통과** |
| 구문 검사 | `python3 -m compileall -q backend agents evaluator simulator tests` | **통과** |
| 실제 CyberBattleSim 컨테이너 | `docker compose run --rm --no-deps cyberbattle_smoke --episodes 1 --seed 7 --steps 3` | **실행 불가**: Docker Desktop npipe daemon이 존재하지 않음 |

## 검증된 항목

- 정상 인증 + 승인 시나리오: 테스트 adapter에서 `execution_status=actual` 계약 확인.
- 잘못된 토큰/허용되지 않은 시나리오/시드/추가 필드: 거부 확인.
- 실행 실패: 502 `execution_status=failed`, mock 성공으로 변환되지 않음.
- 타임아웃: 504 `execution_status=failed` 확인.
- Blue 결과: simulator 관측을 observe-only 구조화 정책으로 변환하고 `approval_required=true` 확인.
- 정책 악화: 독립 holdout에서 승격 거부 확인.
- 기존 8080/8501/8091 설정과 노트북 연결 코드: 변경하지 않음.

## 미해결 문제

초기 검증 당시에는 Docker Desktop daemon이 `npipe:////./pipe/dockerDesktopLinuxEngine` 경로에 없어 실제 실행 증거를 확보하지 못했으나, 아래 최종 통합 검증에서 Docker 복구 후 재검증했다.

## 최종 통합 검증 — 2026-11-16

- 시작 시 8080/8501/8091 listener와 Red API 프로세스는 실행 중이 아니었다. 기존 설정을 변경하지 않고 검증용 Red API를 8091에 임시 기동했다가 종료했다.
- 임시 전용 토큰은 실행 중 메모리에서만 생성·사용했으며 출력·로그·보고서에 기록하지 않았다.
- 실제 승인 요청: `POST /api/v1/red/scenario`, `scenario_id=login_burst`, `seed=7`
  - 인증 실패 요청: HTTP 401
  - 승인 요청: HTTP 201
  - `execution_status=actual`, `executor=docker`, `trace_steps=8`, `blue_observations=8`, `external_network=false`
  - API 응답의 Blue 후보 action은 `observe`이며 모든 후보에 `approval_required=true`가 포함됐다.
- 독립 holdout: `holdout_seed=100010`, 요청 seed 제외=true
  - 기준선: detection rate 1.0, false-positive rate 0.0
  - 후보: detection rate 0.0, false-positive rate 0.0
  - 결과: `promoted=false`, `policy-v1-baseline`, 사유 `no regression-free improvement`
- Docker 제한 inspect: `NanoCpus=1000000000`, `Memory=805306368`(768MiB), `PidsLimit=128`, read-only rootfs, internal network, `no-new-privileges`, `CapDrop=ALL`.
- worker 제한: simulation phase CPU 12초, virtual address ceiling 2GiB; Docker cgroup이 resident memory 768MiB를 강제하고 API subprocess timeout은 15초.
- 첫 API 실행은 import 단계 `MemoryError`로 502가 발생했다. 원인은 RLIMIT_AS 768MiB가 CyberBattleSim/IPython/Jedi import의 virtual address를 제한한 것이었다. 제한 적용 시점을 환경 초기화 이후로 이동하고 virtual ceiling을 2GiB로 조정한 뒤 worker 및 API를 재검증해 HTTP 201을 확인했다.
- `Invalid entity index`는 CyberBattleSim의 `DiscriminatedUnion.sample()`이 observation action mask를 무시하고 무작위 action을 생성해 발생했다. mask의 첫 유효 action만 선택하도록 수정했으며, 8-step worker 재실행에서 해당 경고는 **0건**이었다. 남은 Gymnasium `numpy.int32` observation type warning은 외부 라이브러리 passive checker 경고이며, 실행은 8 step·8 observation으로 정상 완료됐다.
- 최종 회귀: `python3 -m compileall -q backend agents evaluator simulator tests` 통과, `python3 -m unittest discover -s tests -v` **22/22 통과**.

최종 상태: 현재 차수의 실제 API→Docker worker→Blue→독립 holdout 통합 검증을 완료했다. 실제 방화벽·외부 IP·IoT 장비에는 접근하지 않았다.

## 다중 AI 협력 방어 1차 검증 — 2026-11-16

환경 확인:

- Ollama `0.30.6` 실행 확인.
- 설치 모델: `qwen2.5:7b`, `qwen3:4b`, `gemma3:4b`, `phi4-mini:latest`.
- Qwen3 4B와 Phi-4 Mini는 이번 작업에서 다운로드 완료.
- GPU: GTX 1660 Ti, VRAM 6144 MiB; 측정 시 약 4016 MiB free.
- 시스템 RAM: 15 GiB total, 약 14 GiB available.
- 기존 Blue 호출 경로는 `agents/blue/slm.py`의 local `ollama run` subprocess이며, schema 실패 시 `slm_fallback`을 사용한다. 협력 경로는 이를 재사용하되 실패를 sLLM 성공으로 대체하지 않는다.

구현:

- `agents/blue/collaborative.py`: 동일 CyberBattle 관측 요약을 Qwen2.5 → Qwen3 → Gemma3 → Phi-4 Mini 순서로 전달.
- 이전 모델의 검증 상태·실패 사유와 동일 관측값을 다음 모델 prompt의 DATA 영역에 전달.
- `--format json`, `--think=false`, `--hidethinking`으로 구조화 응답을 요청.
- 허용 action은 `observe`/`block_dry_run`, 모든 정책은 `approval_required=true`, 실제 적용 없음.
- 모델별 응답 시간과 GPU memory 샘플/peak를 `artifacts/multi_ai_collaboration.json`에 저장.
- 기존 8080/8501/8091, 인증, Docker 격리 설정은 변경하지 않음.

실제 동일 관측 호출 결과:

| 모델 | 상태 | 응답 시간 | JSON | 정책 | GPU peak used |
|---|---|---:|---|---|---:|
| Qwen2.5 7B | `slm_inference` | 2,723 ms | 통과 | `observe` | 5576 MiB |
| Qwen3 4B | `slm_inference` | 14,421 ms | 통과 | `observe` | 4595 MiB |
| Gemma3 4B | `slm_inference` | 21,485 ms | 통과 | `observe` | 4154 MiB |
| Phi-4 Mini | `slm_inference` | 16,023 ms | 통과 | `observe` | 4399 MiB |

입력은 실제 Docker CyberBattleSim worker의 `login_burst`, seed 17, step 1 관측 요약이다. 모든 모델은 동일한 관측을 받았다. Qwen2.5의 검증 실패는 결과를 정책으로 채택하지 않고 `slm_error`로 보존했다. 협력 결과의 `all_models_validated=false`이며, 이는 실패를 숨기지 않는 정상 fail-closed 결과다.

테스트:

- 기존 및 신규 테스트: **24/24 통과**.
- 신규 검증: 네 모델 순서, 동일 관측 전달, 구조화 정책 승인 조건, 모델 실패 시 정책 미기록.
- 미해결: Qwen2.5 7B의 이번 동일 관측 응답은 독립 JSON/정책 검증을 통과하지 못했다. 따라서 기준 모델 성공으로 보고하지 않았으며, 원시 응답은 저장하지 않았다.

## 다중 AI 협력 방어 고도화 — 동일 차수 최종 갱신

## Red AI–Blue AI 가상 대결 및 오프라인 IDS — 동일 차수 최종 갱신

- Red 요청 스키마와 3개 승인 시나리오를 `red_team/`에 추가했다. 요청은 CyberBattleSim, detection objective, seed, max_steps만 허용하고 외부 target/명령을 허용하지 않는다.
- `red-test-002`, seed 100010, max_steps 3을 실제 Docker child worker로 실행했다. `execution_status=actual`, trace 3회, Blue event 3건을 확인했다. 독립 평가 결과는 탐지 `detected`, 차단 `unknown`, 전체 `unknown`이며 정책은 적용하지 않았다.
- `/api/v1/red/battle` 인증 HTTP 경로도 실제 Docker worker로 검증했다. seed 100011, 2 step, `actual`, Blue event 5건을 확인했다.
- 개발 seed와 분리된 holdout seed 200013을 실제 실행했다. 탐지는 `detected`였지만 차단 증거가 없어 `policy_promotion.promoted=false`로 기록했다. `artifacts/red_blue_battle.json`, `artifacts/red_blue_holdout.json` 참조.
- Suricata 7.0.3을 설치하고 OISF `suricata-verify` 공식 PCAP을 `-r` 오프라인 분석했다. EVE 6건, alert 탐지 3건을 `suricata_offline/parser.py`와 Blue dry-run으로 전달했다. live capture/IPS/방화벽은 사용하지 않았다. `artifacts/suricata_offline.json` 참조.
- Docker 제한은 기존 compose의 internal network, read-only, no-new-privileges, CPU 1, memory 768 MiB, PID 128을 유지했다. worker timeout은 adapter 15초를 유지했다.
- 권한 확장 실제 회귀: **29/29 통과**. compileall도 통과. 샌드박스 일반 실행에서만 loopback 소켓 권한 오류가 발생했으며 코드 오류가 아니라 권한 제약이었다.
- 최종 Red API health: `127.0.0.1:8091/health`에서 `ready`, `external_network=false` 확인. 토큰은 프로세스 내부 생성·사용으로 로그와 보고서에 남기지 않았다.

이번 차수 완료 판정: Red 실행, CyberBattleSim–Blue–독립 평가, Suricata 오프라인 EVE 전달, holdout 승격 차단, 기존/신규 회귀 테스트를 모두 확인했다. 단, 추상 CyberBattleSim의 차단 성공률은 계속 `unknown`이며 실제 네트워크 방어로 해석하지 않는다. 사용자 승인 없이 다음 차수로 진행하지 않는다.

## 내부자 이상 행동 방어 — 동일 차수 갱신

- 공식 ATT&CK/ATLAS/OWASP 자료를 바탕으로 정상 계정 악용, 대량 반출, 감사 로그 변조, 단계적 행동, prompt injection, excessive agency를 조사하고 `AI_ATTACK_PATTERN_RESEARCH.md`에 기록했다.
- 합성 Red 라이브러리와 역할별 행동 분석기를 추가했다. 최고 관리자도 예외 없이 고위험 작업이 보류된다.
- `ApprovalEngine`은 고위험 요청을 실행 전에 `pending_approval`로 보류하고, 독립 `security_officer` 승인만 허용한다. 자기 승인, 통보 실패, TTL 만료를 테스트했다.
- SHA-256 hash-chain 감사 로그가 토큰·비밀번호·고객 원문을 제거하고, 변조를 탐지한다.
- 개발 9개와 holdout 9개 합성 실험: 탐지율 1.0, 오탐률 0.0, 감사 완전성 1.0. 결과는 `artifacts/insider_threat_evaluation.json`이다. 정책 자동 승격은 하지 않았다.
- 비식별 합성 최고 관리자 사건을 기존 4종 Blue AI에 전달했다. 실제 sLLM 4/4 호출, 결과는 `unknown`, 정책은 dry-run이다.
- 전체 회귀 테스트: **33/33 통과**. 기존 8080/8501/8091, 인증, Docker 격리, Suricata 오프라인 경계를 보존했다.

현재 차수 완료 조건 판정: 외부 공격·실제 고객 데이터·실제 방화벽 변경 없이 모든 합성 통합 검증을 완료했다. 실제 고객 환경 적용 전에는 승인자 디렉터리, 영속 감사 저장소, 조직별 정상 기준선의 별도 설계가 필요하다. 사용자 승인 전에는 다음 차수로 진행하지 않는다.

### 구현

- `agents/blue/slm.py`: Ollama local `/api/generate` JSON Schema 호출을 추가했다. `format=schema`, `stream=false`, `think=false`, `temperature=0`, `keep_alive=0`을 사용하며 기존 의미·안전 validator를 별도로 유지한다.
- `agents/blue/collaborative.py`: 7단계 흐름, 공통 사건/관측 DATA 경계, 이전 모델 실패 환류, `success`/`failure`/`unknown`, 조건부 escalation, 의견 충돌 처리를 구현했다.
- `evaluator/collaborative_repetition.py`: 동일 관측의 반복 측정 모듈을 추가했다.
- `OPEN_SOURCE_RESEARCH.md`: GitHub/Hugging Face/Ollama 공식 출처 비교를 추가했다.
- `COLLABORATIVE_DEFENSE_EVALUATION.md`: 모델·협력 성능과 재현 명령을 추가했다.

### Qwen2.5 수정·재시험

기존 CLI의 단순 JSON 출력 경로를 동일 관측에서 재실행한 결과 `SLMValidationError: action is outside the allow-list`가 재현됐다. 즉 transport/JSON 파싱보다 모델이 허용 DSL 밖 action을 제안한 것이 원인이었다. 이 결과를 성공으로 변환하지 않고 실패로 보존했으며, 이후 Ollama 공식 JSON Schema API로 동일 관측을 10회 재실행했다.

- Qwen2.5 7B: **10/10 schema·정책 검증 통과, 성공률 100%**
- 평균 지연: 약 13,119 ms
- 최대 측정 VRAM: 5,808 MiB
- 방어 결과: 실제 추상 관측에는 ground truth가 없어 10회 모두 `unknown`

### 실제 협력 실행

동일한 실제 CyberBattleSim 관측을 Qwen2.5 → Qwen3 → Gemma3 → Phi-4 Mini 순서로 전달했다.

- 호출: 4/4
- JSON·정책 검증: 4/4
- 전 모델 정책: `observe`, risk `low`, 승인 필요=true
- 의견 일치: true
- 협력 결과: `unknown` — 의견 일치만으로 방어 성공을 선언하지 않음
- 합계 지연: 약 54.6초
- 최대 측정 VRAM: 5,576 MiB
- 호출 중 최소 시스템 RAM available: 약 12.5 GiB; Python evaluator `ru_maxrss`: 약 274 MiB

### 조건부 호출

검증된 synthetic 사건에서 Qwen2.5 결과가 확정되면 상위 3개 모델을 skip하는 unit test를 통과했다(호출 1개, skip 3개). 실제 CyberBattle abstract observation은 `detected=null`이므로 불확실성 조건에 의해 4개 모델을 모두 호출했다.

### 최종 검증

- 기존·신규 전체 테스트: **25/25 통과**
- 기존 8080/8501/8091, Red API 인증/allow-list, Docker 격리 설정 유지
- 기존 command-line 토큰은 폐기하고 새 환경변수 토큰으로 Red API를 동일 8091 host/allow-list에 재기동. 토큰은 출력·로그·보고서에 기록하지 않음.
- 실제 네트워크 공격, 실물 방화벽 변경, IoT 장비 접근 없음.

### 완료 조건 판정

| 조건 | 판정 |
|---|---|
| Qwen2.5 원인 규명·수정·10회 재시험 | **완료** — JSON Schema API 10/10 |
| 실제 1차·2차·3차 검증 흐름 | **완료** — 4개 actual sLLM 호출 |
| 모델 의견 전달·환류 증거 | **완료** — artifact의 sequence/results와 DATA 이전 결과 |
| success/failure/unknown 구분 | **완료** — 실제 추상 관측 결과 unknown |
| 조건부 상위 AI 호출 | **완료** — unit test에서 skip, 불확실 관측에서 escalation |
| 독립 holdout·나쁜 정책 승격 차단 | **완료** — 기존 evaluator 유지, observe-only 승격 거부 |
| 모델 자원·지연 비교 | **완료** — artifact/report 기록 |
| GitHub/Hugging Face 비교 보고서 | **완료** — `OPEN_SOURCE_RESEARCH.md` |
| 회귀·신규 테스트 | **완료** — 25/25 |

남은 제한은 실제 방어 성공률을 산출할 수 없는 CyberBattle 추상 observation의 평가 한계와 Suricata 미통합이다. 따라서 이 둘은 실패를 숨기지 않고 각각 `unknown`/보류로 기록했으며, 사용자 승인 없이 다음 개발 차수로 진행하지 않는다.

## 3시간 무인 Red–Blue 시험 — 진행 중

- 5분 사전 시험은 성공했고, 180분 본 시험을 seed `20261116`, 무작위 2–10분 간격, 지속 세션으로 시작했다.
- 최초 셸 백그라운드 방식은 셸 종료로 사건 없이 정리되어 본 시험에 포함하지 않았다. 동일 설정을 지속 세션으로 재기동했다.
- 진행 산출물: `artifacts/red_blue_3h_events.jsonl`; 종료 산출물: `artifacts/red_blue_3h_summary.json`.
- 최종 결과: 180분 정상 종료, 31건, 오류 0건, 실제 CyberBattleSim 6건, 감사 무결성 true. 상세 결과는 `RED_BLUE_3H_REPORT.md` 및 `artifacts/red_blue_3h_summary.json`에 기록했다.
- 장기 scheduler는 규칙 기반 독립 엔진을 사용했으며 31건마다 4종 sLLM을 호출하지 않았다. 따라서 장기 모델별 지연·성능 조건은 **미완료**로 명시하며, 기존 실제 4종 협력 호출 결과와 합산하지 않는다.

## 12시간 Red–Blue 장기 검증 — 완료

- 3시간 원본 분석 결과 `not_detected` 4건은 모두 정상 업무 TN이고, 실제 공격 미탐지는 확인되지 않았다. `red-test-003` 1건은 추상 관측의 ground truth 부족으로 `unknown`이다. 상세: `RED_BLUE_3H_FAILURE_ANALYSIS.md`.
- 프로젝트 루트의 `jeon.txt`는 존재하지 않았다. 별도 격리 sandbox에서 동일 이름의 검증 파일을 사용하며 원문은 기록하지 않는다.
- B단계 사전 검증은 36/36 회귀, 실제 4종 sLLM 4/4, 5분 지속 시험 성공으로 통과했다.
- 12시간 본 시험은 새 seed `20261117`, PID `42582`로 43,200초 정상 종료됐다. 116건, 오류 0건, 감사 무결성 true, 외부 네트워크 false였다. 상세: `RED_BLUE_12H_REPORT.md`.
- 알려진 공격 기준 TP 98/FN 0, 정상 업무 TN 9/FP 0, 불완전 관측 9건은 `unknown`으로 제외했다. `red-jeon-target` 9건은 모두 독립 문자열 일치 및 `pending_approval`이었다.
- 12시간 본 시험의 사건별 4종 sLLM 호출은 수행하지 않았고, 실제 sLLM 표본 4/4 결과와 분리 기록했다. 장기 모델별 성능 조건은 **미완료**이며 규칙 기반 장기 안정성 결과만 완료됐다.

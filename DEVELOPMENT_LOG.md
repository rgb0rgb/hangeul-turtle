# Development log

## 2026-11-15 — 단계 0/1 초기화

- 사실: X: 드라이브는 이 환경에서 `/mnt/x`로 확인됨.
- 실측: `.environment-check.txt`에 OS/CPU/RAM/GPU/도구/인터페이스 확인 결과를 기록.
- 구현: 합성 시나리오 생성기, 규칙 기반 Blue 분석기, 독립 평가기, Docker internal network, 자동 테스트 추가.
- 미검증: 실제 노트북·Raspberry Pi·Android 장비 사양과 물리 네트워크 경로.
- 안전: 외부 주소 연결, 실제 방화벽 변경, 호스트 네트워크, 권한 상승 작업을 수행하지 않음.
- 검증: Python 단위 테스트 4개 통과. Docker Compose 검증은 WSL Docker 소켓 오류(`UtilBindVsockAnyPort`)로 미실행.

## 2026-11-15 — 오픈소스 검증 및 통합 판단

- 지정 GitHub 8개 저장소를 depth-1로 복제하고 HEAD·라이선스·구조·실행 진입점을 확인.
- Python 저장소 5개는 의존성 설치 없이 `compileall` 통과. CybORG의 문자열 비교/escape 경고를 기록.
- DefenderBench의 Microsoft Departing Intern License와 연구용 데이터 조건 때문에 핵심 상용 의존성에서 제외.
- CyberBattleSim은 선택적 격리 simulator adapter 후보, Suricata/CrowdSec은 프로세스·로그 경계의 탐지 엔진 후보, Rethink는 Android 자체 VPN/모니터링 참고로 결정.
- 상세 결과는 `OPEN_SOURCE_REVIEW.md`, `ARCHITECTURE_DECISION.md`, `IMPLEMENTATION_PLAN.md`, `TEST_REPORT.md`에 기록.

## 2026-11-15 — Red/Blue 통신 및 한국어 실험 화면

- `backend/server.py`: 토큰 인증이 있는 안전한 Red 이벤트 API와 Blue 분석 결과 저장 구현.
- `agents/red/client.py`: 승인된 시나리오 ID와 seed만 전송하며 셸/네트워크 명령은 전송하지 않음.
- `frontend/index.html`: 합성 이벤트, Red 선택, Blue 탐지, 성공 여부, 지연, dry-run/승인 필요를 한국어로 표시.
- 기본 bind는 `127.0.0.1`; 다른 장비 연결은 실험망과 방화벽 승인 후 진행.

## 2026-11-15 — WSL2 홈 이전 및 반복 평가

- `/mnt/x/AI_Home_Shield_v3`를 `/root/AI_Home_Shield_v3`로 rsync 이전. 원본은 유지.
- `.venv` 생성 및 Python 3.12.3 확인.
- 전체 테스트 10/10 통과.
- CyberBattleSim은 실제 실행이 아닌 `mock_only` 어댑터와 단위 테스트로 경계를 명시.
- 10회 합성 반복 평가에서 규칙 기준선 탐지율 90%, 규칙+Blue 100%, 양쪽 오탐률 0% 기록.

## 2026-11-15 — 실제 CyberBattleSim 컨테이너 검증

- Python 3.10 기반 별도 이미지에 Microsoft CyberBattleSim main 설치 성공.
- Compose `internal: true`, read-only rootfs, `cap_drop: ALL`, no-new-privileges, `/tmp` tmpfs로 실행.
- 10 episode/3 step 실제 실행 성공. 결과를 `artifacts/cyberbattle_10.json`에 저장.
- Blue는 30개 abstract observation을 수신했으며 현재는 observe-only입니다. 탐지 성공으로 과장하지 않음.

## 2026-11-15 — Blue SLM 연결 및 자동 정책 검증

- Ollama 0.30.6과 qwen2.5:7b(Q4_K_M, Apache-2.0, 확인된 blob hash)을 로컬에서 확인.
- 실제 호출은 완료됐지만 모델의 부적합 JSON/action/승인 플래그를 검증기가 거부하고 규칙 fallback을 유지.
- 10회 반복 + 별도 holdout을 실행하고 악화된 후보의 자동 승격을 거부. 결과는 `artifacts/policy_optimization.json`.
- 테스트 17/17 통과. SLM 연결 상태는 `slm_inference` transport 검증이며 `model_training`은 미수행.
# 2026-11-16 — Red API 실제 실행 연결

- 승인된 `scenario_id`/seed만 child CyberBattleSim worker로 전달하도록 전환했다.
- worker와 Docker compose에 실행 시간·CPU·메모리·PID 제한을 추가했다.
- actual 실행만 201 응답으로 반환하고, 실패/타임아웃은 502/504로 fail-closed 처리했다.
- CyberBattleSim 관측을 Blue observe-only 정책 후보로 전달하고, 요청 seed와 분리된 holdout 평가 및 자동 승격 거부를 연결했다.
- 회귀 테스트 22/22 통과.
- Docker Desktop daemon 부재로 실제 컨테이너 실행은 재검증하지 못했다. 완료 기준의 실제 실행 증거는 Docker 기동 후 재시험 필요.

# 2026-11-16 — 동일 차수 최종 통합 검증

- Docker Desktop 복구 후 `cyberbattle_smoke` actual 실행: 1 episode, 3 step, Blue observation 3건.
- API worker 경로를 Docker executor로 검증: 8091 승인 요청 HTTP 201, `execution_status=actual`, Docker worker trace 8 step, Blue observation 8건.
- 요청 seed와 분리된 holdout seed로 평가했고, 후보 성능 악화로 정책 승격을 거부했다.
- 컨테이너 제한 inspect와 Red API 인증 401/201을 확인했다. 비밀 토큰은 출력하거나 기록하지 않았다.
- action mask를 무시하던 무작위 action 때문에 발생한 `Invalid entity index`를 유효 action 선택으로 수정했다. 8-step worker 재검증에서 해당 경고 0건.
- 최종 전체 테스트 22/22 통과.

# 2026-11-16 — 다중 AI 협력 방어 1차

- Ollama 0.30.6, Qwen2.5 7B, Qwen3 4B, Gemma3 4B, Phi-4 Mini를 확인했다. 미설치 Qwen3/Phi는 다운로드했다.
- 실제 Docker CyberBattleSim 관측 하나를 고정해 Qwen2.5 → Qwen3 → Gemma3 → Phi 순서로 호출했다.
- Qwen3/Gemma3/Phi는 JSON schema 통과 및 observe-only 정책 생성. Qwen2.5는 SLMValidationError로 fail-closed 기록.
- 모델별 지연/GPU memory 샘플과 정책 결과를 `artifacts/multi_ai_collaboration.json`에 저장했다.
- command line에 노출된 기존 Red API 토큰을 폐기하고, 동일 8091 host/allow-list에 새 토큰을 환경변수로 주입해 재기동했다. 토큰은 출력·로그·보고서에 기록하지 않았다.
- 신규 포함 전체 테스트 24/24 통과.

# 2026-11-16 — 다중 AI 협력 고도화 최종

- Ollama JSON Schema API(`format=schema`, `think=false`, `temperature=0`)를 추가하고 기존 정책 의미/안전 validator와 분리했다.
- Qwen2.5 7B 동일 CyberBattle 관측 10회: schema·정책 검증 10/10, 평균 13.1초, 최대 VRAM 5808MiB.
- 실제 협력 순차 실행: Qwen2.5 → Qwen3 → Gemma3 → Phi-4 Mini, 4/4 검증 통과, 의견 일치, 결과는 ground truth 부재로 `unknown`.
- 조건부 라우팅과 이전 모델 실패/검증 결과 환류를 구현하고 unit test로 확정 결과 skip 및 불확실성 escalation을 검증했다.
- GitHub/Hugging Face/Suricata/Ollama 공식 자료를 조사해 `OPEN_SOURCE_RESEARCH.md`에 기록했다. 외부 코드는 설치·실행하지 않았다.
- 최종 전체 테스트 25/25 통과.
- 기존 CLI JSON 경로의 Qwen2.5 실패 원인을 동일 관측으로 재현: `action is outside the allow-list`. JSON Schema API 경로에서는 10/10 통과.


## 2026-11-17 — Claude Red Team 6h (동일 호스트 시뮬레이션)
- 모드: 소유자 승인 Option B(2대 분리 미시연, §1 예외). 시계 10:23:16→16:23:16 KST, 21,600초 완주.
- 사전점검: 2대 토폴로지(노트북 192.168.0.56 / 데스크톱 192.168.0.20) 미성립 기록 — 이 세션=Blue 데스크톱, WSL NAT 바인딩, 노트북 인바운드 0. IP 추측·스캔 안 함.
- 실행: 탐침 배터리 10패턴 + 연속 스케줄러 60건(insider44/cyberbattle12/jeon4), 오류0, 감사무결성 전건 True.
- 결과: 호스트 루트 Jeon.txt 인가경로 도달 0, blocking_status 60/60 unknown(실제차단 미입증=W-ENFORCE-1), 인젝션 무력화·변조탐지·오탐0.
- 산출물: CLAUDE_RED_TEAM_REPORT.md / _EVENTS.jsonl(82) / _SUMMARY.json(COMPLETED). 개발 차수 유지, 자동 진행 없음.
- 2026-11-17: Claude 6시간 보고서 원본·82건 로그·summary를 reconciliation했다. W-ENFORCE-1은 `/tmp` 전용 실제 I/O gate로 승인 전 거부/승인 후 허용/rollback 후 거부를 검증했고, W-AUDIT-1은 독립 witness로 삭제·절단·수정을 검출했다. 경쟁기술·상용 제품 비교를 `COMPETITIVE_TECH_REVIEW.md`에 기록했다. 전체 39/39 통과. 2대 LAN과 실환경 enforcement는 승인 전 미검증.

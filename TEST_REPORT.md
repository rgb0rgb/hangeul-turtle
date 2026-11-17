# Test report

검증일: 2026-11-15

## 환경

- WSL2 Linux, x86_64, AMD Ryzen 7 1700, 16 CPU, 약 15 GiB RAM
- Python 3.12.3, Node 22.22.2, npm 10.9.7
- NVIDIA GTX 1660 Ti 6GB가 WSL에서 인식되었고, Ollama 0.30.6 및 qwen2.5:7b가 설치됨
- Docker Desktop/WSL2는 현재 정상 동작하며 CyberBattleSim 컨테이너 smoke를 완료함

## 실행 결과

| 대상 | 명령/방법 | 결과 |
|---|---|---|
| AI Home Shield | `python3 -m unittest discover -s tests -v` | **통과 4/4** |
| Red→Blue HTTP demo | `tests/test_integration.py` | **통과 3/3**; 인증·카탈로그 거부·한국어 화면·dry-run 확인 |
| 전체 회귀 | `python3 -m unittest discover -s tests -v` (권한 상승된 localhost 테스트) | **통과 12/12** |
| 새 위치 반복 평가 | `python3 evaluator/repeat_experiment.py --repetitions 10 --output artifacts/repeat.json` | 규칙 기준선/Blue 결합 지표와 mean/P95 latency 저장 |
| CyberBattleSim 경계 | `CyberBattleSimAdapter` 단위 테스트 | **mock_only**; 실제 CyberBattleSim 실행 아님 |
| CyberBattleSim 실제 컨테이너 | `docker compose run --rm --no-deps cyberbattle_smoke --episodes 10 --seed 7 --steps 3` | **실행 성공**; 10 episodes, 30 Blue observations, 외부 네트워크 없음 |

### 이전 후 실제 측정값

- Ubuntu 내부 경로: `/root/AI_Home_Shield_v3`
- 전체 테스트: **10/10 통과**
- 반복 평가 ID: `repeat-1000-10`
- 규칙 기준선 탐지율: `0.90`
- 규칙+Blue 탐지율: `1.00`
- 규칙/Blue 오탐률: `0.00 / 0.00`
- Blue P95 지연: 약 `0.003392 ms` (합성 로컬 분석 기준)
- 이 결과는 모델 가중치 학습이 아니라 정책/분석기 비교이며 `trained_on_holdout=false`입니다.

### 실제 CyberBattleSim 측정값

- 실행 상태: `actual_smoke`
- 이미지: Python 3.10 + Microsoft CyberBattleSim `main` 설치 성공
- episode seed: 7–16, 각 3 steps
- reward: 전 step `0.0`, terminal episode `0`
- episode latency: 평균 `233.7163 ms`, P95 `226.897 ms`, 최대 `365.225 ms`
- Blue 연결: 추상 observation 30건을 수신했지만 현재 Blue 응답은 `observe_only`, `detected=null`입니다. 실제 공격 탐지율로 해석하지 않습니다.
- Gymnasium observation 타입 경고와 `Invalid entity index` 경고가 출력되어 후속 adapter 안정화 대상으로 기록합니다.

## 4차 개발 — 로컬 SLM 및 정책 개선

- Ollama `0.30.6`, `qwen2.5:7b`(7.6B, Q4_K_M, 4.7GB, local ID `845dbda0ea48`)를 확인했습니다. 모델 blob SHA-256은 `2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730`, 라이선스는 Apache-2.0입니다.
- 실제 로컬 호출 1회 성공: 추론 transport는 동작했으나 Markdown fence, 허용 목록 밖 자연어 action, `approval_required=false`가 포함되어 Schema 검증에서 거부되었습니다. 규칙 기반 dry-run fallback이 적용되었고 `model_training=false`입니다. 측정 시간 약 16.7초.
- 자동 방어 비교 10회: `artifacts/policy_optimization.json`, rules 탐지율 0.90, SLM 경로 0.70, 오탐률은 양쪽 0.00. 독립 holdout에서도 개선 없음으로 정책 승격을 거부했습니다. `fallback_count=120`; 이는 SLM 정책 성공이 아니라 안전 fallback 결과입니다.
- 전체 테스트: **17/17 통과**. 추가 검증은 JSON Schema, 잘못된 출력 거부, 프롬프트 인젝션 데이터 경계, timeout fallback, Red allow-list, 정책 승격 거부입니다.
- 기존 CyberBattleSim actual_smoke 10회 결과와 mock_only 경계를 유지했습니다. SLM 결과와 CyberBattleSim reward를 혼합하지 않았습니다.

## 노트북 Red API 연결 단계

- 전용 서비스 `backend/red_api.py`와 Python 3.12 클라이언트 `notebook_red/client.py`를 추가했습니다.
- localhost 통신·인증·schema·IP allow-list 경계·rate limit 경로를 테스트했습니다. 전체 테스트는 **20/20 통과**입니다.
- 실제 노트북 `192.168.0.56`과의 LAN 통신은 아직 수행하지 않았습니다. Windows portproxy/방화벽 변경은 승인 전이므로 미완료입니다.
| AI Home Shield | login burst seed 42 생성·평가 | **5 events, 5 detected**; 합성 데이터와 dry-run 정책 후보 확인 |
| 오픈소스 Python 5개 | `python3 -m compileall -q ...` | **구문 컴파일 통과**; CybORG 경고 3건 기록 |
| GitHub 소스 확보 | depth-1 clone, HEAD 기록 | **8/8 성공** |
| Docker Compose | `docker compose config` | **구성 검증 통과**; 실제 컨테이너 실행은 API 권한 거부 |
| 오픈소스 full tests | 의존성 설치·pytest/Gradle/Go test | **미실행**; 비용·권한·환경 변경이 필요하고 현재 범위 밖 |

## 해석

이번 결과는 저장소가 존재하고 소스가 구문상 읽히며 AI Home Shield 기준선이 통과했다는 증거입니다. 오픈소스의 README 기능이 실제 운영·성능·ARM64에서 검증됐다는 뜻은 아닙니다. 특히 Suricata/CrowdSec/Rethink는 실제 설치와 장치 테스트 전까지 통합 성공으로 표시하지 않습니다.

## 다음 시험

1. 의존성 lock을 별도 격리 환경에 만들고 CyberBattleSim baseline smoke test 실행
2. 네트워크 egress 단위 테스트와 시나리오 holdout 평가 추가
3. Suricata EVE JSON/CrowdSec 로그 fixture를 실제 네트워크 없이 입력
4. Docker daemon이 복구된 뒤 internal network와 read-only compose 검증

## Docker 진단

- 확인: `docker`는 `/mnt/c/Users/tiger/AppData/Local/Programs/DockerDesktop/resources/bin/docker`의 Windows Docker Desktop CLI입니다.
- 확인: 현재 `/var/run/docker.sock`는 `root:nogroup`, mode `660`으로 존재하지만 `docker info`의 Server 영역에서 permission denied가 발생합니다.
- 확인: Docker CLI 29.9.3, `default=unix:///var/run/docker.sock`, `desktop-linux=npipe:////./pipe/dockerDesktopLinuxEngine`; `DOCKER_HOST`는 비어 있습니다.
- 오류: 이전에는 `UtilBindVsockAnyPort:317: socket failed 1`이 발생했고, 현재는 socket 접근 권한/샌드박스 경계까지 좁혀졌습니다.
- 결론: compose 문법·격리 설정은 정상이며, 실제 daemon API 접근만 보류입니다.
- 승인 대기: Docker Desktop 실행 상태, Settings → General의 WSL 2 based engine, Settings → Resources → WSL Integration에서 Ubuntu 활성화, Windows PowerShell의 `wsl -l -v`와 `wsl -d docker-desktop echo WSL 2 is working` 확인이 필요합니다. `wsl --shutdown`, Docker Desktop 재시작, Docker Desktop/WSL 업데이트는 관리자 또는 외부 상태 변경이므로 승인 전 실행하지 않았습니다.
# 동일 차수 후속 검증 갱신 — 2026-11-17

- 원본 6시간 증거 reconciliation: `EVIDENCE_RECONCILIATION.md`
- W-ENFORCE-1 sandbox I/O gate: 승인 전 거부, 승인 후 실제 read 허용, rollback 후 거부, 범위 밖·자기 승인·토큰 재사용 거부
- W-AUDIT-1 external witness: 삭제·절단·수정 검출
- 전체 테스트: **39/39 통과**
- 실제 고객/호스트/LAN/방화벽: 접근·변경 없음
- 2대 topology 및 연속 실행 LLM 호출: 미검증/미행사로 유지

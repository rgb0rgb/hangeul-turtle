# Implementation plan

## 단계별 상태와 완료 조건

| 단계 | 상태 | 완료 조건 |
|---|---|---|
| 1. v3 분석 | 완료 | 기존 문서·구조·안전 경계 확인, 요구사항 삭제 없음 |
| 2. 오픈소스 검증 | 완료 | `OPEN_SOURCE_REVIEW.md`, 커밋/라이선스/구조/검증 한계 기록 |
| 3. 격리 simulator 선정 | 진행 예정 | CyberBattleSim adapter의 schema 변환, egress 차단 테스트, seed 재현성 |
| 4. Red↔Blue 통신 | 예정 | 인증된 로컬 API 또는 파일 큐, 제한된 JSON, 임의 명령 필드 거부 |
| 5. 독립 평가·재학습 | 예정 | train/holdout 분리, 탐지율·오탐률·지연·CPU/RAM, 승격 gate |
| 6. Suricata/CrowdSec 연동 | 예정 | fixture EVE/log 입력, 실제 운영 인터페이스 없이 dry-run 정책 후보 |
| 7. Raspberry Pi/Android | 예정 | ARM64 빌드·관찰 데이터 범위·VPN 한계·장애 복구 문서화 |
| 8. 중앙 업데이트/UI | 예정 | 서명·해시·단계적 배포·롤백, 한국어 UI, 감사 로그 |

## 다음 구현 작업

- `simulator/` 이벤트를 CyberBattleSim의 추상 상태/행동으로 매핑하는 읽기 전용 adapter
- Red 출력 JSON Schema와 Blue 정책 DSL의 독립 검증기
- 노트북/데스크톱 간 통신은 먼저 단일 호스트 loopback 또는 internal Docker network에서만 시험
- 공격 로그의 문자열은 데이터로만 저장하고 명령으로 파싱하지 않는 prompt-injection 방어 테스트
- holdout 시나리오를 코드·seed·학습 입력에서 분리하고 100회 반복 실행 기록 형식 추가

## 외부 승인 없이는 하지 않을 작업

실제 공유기 라우팅/DNS 변경, nftables 적용, host networking, privileged container, Android VPN 설치·프로파일 적용, Raspberry Pi inline 전환, 외부 공격 도구 실행, 유료 API/모델 다운로드.

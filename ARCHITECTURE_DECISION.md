# Architecture decision

## 결정

1. 단계 2의 기본 실험 환경은 현재의 결정론적 합성 simulator를 유지한다.
2. CyberBattleSim을 첫 번째 선택적 Red/Blue simulator adapter 후보로 조사 통합한다. 핵심 도메인 스키마와 안전 검증기는 우리 코드가 소유한다.
3. CybORG는 별도 `lab_profiles/cyborg` 프로파일로만 연결한다. 기본 설치·기본 compose 의존성으로 넣지 않는다.
4. Blue 방어 엔진은 규칙 기반 분석기를 기준선으로 유지하고, SLM은 설명·우선순위·정책 후보만 제안한다.
5. Suricata와 CrowdSec은 직접 포크하지 않고 gateway/backend의 입력 어댑터로 연결한다. 정책은 우리 DSL과 독립 검증기를 통과해야 한다.
6. Raspberry Pi는 관찰/DNS 보조 모드부터 시작한다. NFQUEUE inline은 별도 승인·두 NIC·복구 시험 후에만 지원한다.
7. Android는 PWA/알림과 자체 VPN 기반의 휴대폰 트래픽 모니터링을 우선한다. Rethink의 기능은 기술 참고로 사용하며 전체 가정망 보호를 주장하지 않는다.
8. DefenderBench, CyberDojo, 연구·교육 제한 데이터와 20B급 모델은 핵심 제품 의존성으로 채택하지 않는다.

## 충돌과 해결

- 기존 v3는 Red/Blue 반복 실험과 선택적 Ollama/Gemma를 요구한다. 이번 조사 결과는 이를 바꾸지 않고, 먼저 결정론적 기준선과 격리 adapter를 두는 구현 순서로 보강한다.
- 기존 v3의 Raspberry Pi 차단 단계와 SBC gateway의 요구사항은 실제 운영망을 즉시 inline으로 만들지 말라는 안전 원칙과 충돌할 수 있다. 관찰 모드 → 격리 테스트망 NFQUEUE → 별도 승인된 운영 적용 순으로 해소한다.
- DefenderBench의 평가 기능은 유용하지만 라이선스가 상용 배포와 맞지 않는다. 평가 지표와 독립 holdout 설계만 참고하고 코드는 배포하지 않는다.

## 4차 결정

- 로컬 Blue SLM 실행기는 Ollama를 선택한다. 현재 PC에서 이미 실행 가능하고 모델 관리·로컬 CLI가 제공되며 llama.cpp CLI는 확인되지 않았다.
- SLM은 설명과 dry-run 후보만 제안한다. 엄격한 JSON/action/approval 검증 실패 시 규칙 분석기로 fallback한다.
- 정책 후보는 별도 holdout에서 탐지율 저하 또는 오탐 증가가 있으면 승격하지 않는다. 이 단계는 모델 재학습이 아니라 정책 검증이다.
- Red SLM은 아직 연결하지 않고 승인 catalog/seed 인터페이스만 유지한다. 실제 노트북 연결 정보가 없으므로 설치 완료로 표시하지 않는다.

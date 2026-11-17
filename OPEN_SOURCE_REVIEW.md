# Open-source verification review

검토일: 2026-11-15. 저장소는 `/tmp/ai_home_opensource`에 depth-1로 복제하여 커밋, 파일 구조, 라이선스, 의존성·테스트 진입점을 확인했습니다. `compileall`은 코드가 구문상 컴파일되는지만 확인하며, README 기능이 실제 제품 수준으로 동작한다는 증거로 해석하지 않습니다.

## 판단 요약

| 프로젝트 | 확인된 실제 기능/코드 | 라이선스·상태 | AI Home Shield 판단 |
|---|---|---|---|
| [CyberBattleSim](https://github.com/microsoft/CyberBattleSim) | Python 기반 추상 기업망, Gym 인터페이스, baseline RL agent와 notebooks가 존재. `cyberbattle/`와 테스트 코드 확인. | MIT. WSL/Docker 안내, HEAD `aebf185` (2026-08-25). | **조건부 채택**. Red/Blue 실험 어댑터 후보. 우리 합성 이벤트 스키마와 안전 정책을 감싸는 래퍼가 필요. |
| [CybORG](https://github.com/cage-challenge/CybORG) | simulated/emulated 네트워크, Red/Blue action·wrapper·pytest 테스트가 존재. | MIT 및 정부 코드 CC0 고지. HEAD `2742b5e` (2024-02-20). `gym==0.23.1`, pygame 등 의존성. | **조건부 채택**. 더 풍부한 cyber-op 연구환경이나 의존성·실행비용이 크므로 격리 프로파일에서만 평가. |
| [DefenderBench](https://github.com/microsoft/DefenderBench) | `src/agents`, CyberBattleSim 환경, random/human/LLM benchmark 실행 예제가 존재. | Microsoft Departing Intern License: 비상업 연구 목적, 소스 재배포 금지. HEAD `e431098` (2025-07-08). | **핵심 의존성 금지**. 내부 평가 설계 참고와 별도 연구용 비교에만 사용. 상용 제품 코드에 포함하지 않음. |
| [CyberDojo](https://github.com/satyamdas03/CyberDojo) | dashboard, environment/trainer/network 테스트와 LLM 기능 코드가 존재. | MIT이나 HEAD `33c7d50` (2026-03-08), 2 commits/0 stars. | **보류**. 기능 설명은 크지만 독립 재현성과 유지보수 증거가 부족. 구조 참고만 함. |
| [Suricata](https://github.com/OISF/suricata) | C 기반 IDS/IPS/NSM 엔진, 규칙·출력·테스트 트리가 존재. | GPL-2.0. HEAD `c48ca37` (2026-11-11). | **외부 엔진 연동 후보**. EVE JSON/Unix socket 등 경계로 연결하고, 제품 라이선스 검토 없이 코드 링크·포크하지 않음. ARM64는 Raspberry Pi에서 별도 빌드/성능 검증 필요. |
| [CrowdSec](https://github.com/crowdsecurity/crowdsec) | Go Security Engine, 로그/HTTP 분석, scenarios와 remediation components, hub 연동 코드. | MIT. HEAD `e20782b` (2026-11-13), 2,845 commits. | **외부 엔진 연동 후보**. 로그 기반 탐지·차단 후보로 사용; 패킷 가시성 엔진으로 과장하지 않음. 커뮤니티 blocklist 전송·개인정보를 별도 검토. |
| [suricata-ips-sbc-gateway](https://github.com/imosudi/suricata-ips-sbc-gateway) | Ansible, NFQUEUE, Raspberry Pi/Orange Pi 게이트웨이 구성과 LAN/WAN 평가 harness. | BSD-3-Clause. HEAD `ac2f28a` (2026-06-15), 62 commits/0 stars. 2 NIC, sudo, SSH, 공격 도구 요구. | **설계 참고/후속 실험**. 실제 운영망에 복사하지 않고, 승인된 격리망에서 관찰 모드부터 검증. |
| [Rethink](https://github.com/celzero/rethink-app) | Android VPN 기반 DNS/방화벽/연결 추적, WireGuard·DoH/DoT/DNSCrypt 코드와 benchmark/build 파일. | Apache-2.0. HEAD `07fe537` (2026-10-25), 6,258 commits. | **Android 참고/통합 후보**. 휴대폰 자체 트래픽 관리에는 적합하지만 가정 전체의 투명 게이트웨이가 아님. 기존 앱 포크는 별도 법률·제품 검토 후 결정. |

## 실제 실행 검증 범위

- 5개 Python 저장소(CyberBattleSim, CybORG, DefenderBench, CyberDojo, SBC gateway)는 의존성 설치 없이 `python3 -m compileall`을 실행했고 구문 컴파일은 통과했습니다.
- CybORG에서 Python 경고(문자열 비교에 `is`, Windows 경로 escape)가 발견되었습니다. 이는 즉시 기능 실패 증명은 아니지만 유지보수 위험으로 기록합니다.
- 각 프로젝트의 full test suite, Docker build, Android Gradle build, Suricata/CrowdSec system install은 실행하지 않았습니다. 현재 환경의 Docker socket이 실패하고, 일부 프로젝트는 외부 패키지·권한·실제 네트워크가 필요하기 때문입니다.
- 기존 AI Home Shield 자체 테스트 4개는 통과했습니다. 이는 오픈소스 프로젝트의 기능 검증과 별개입니다.

## Hugging Face 조사

- [UNSW-NB15](https://huggingface.co/datasets/pcy12345BSU/UNSW-NB15): 약 2.5M flow record, 9 attack categories. 카드에 연구·교육 목적이라고 적혀 있어 상용 학습 데이터로 채택하지 않습니다.
- [cyberset](https://huggingface.co/datasets/mvd001/cyberset): 여러 IDS flow와 보안 지식 허브를 묶었지만 일부 subset에 비상업 제한·상위 데이터셋 라이선스가 있습니다. 원본별 권리 확인 전 사용 금지.
- [5G-NSD](https://huggingface.co/datasets/CSRL-NITK/5G-NSD): 컨테이너화된 5G 테스트베드에서 생성된 1.37M flow 규모. 현재 MVP의 가정용 IoT 데이터와 직접 일치하지 않아 후보 데이터로만 기록.
- [CyberSLM-instruct](https://huggingface.co/sabari2005/cyberslm-instruct): 33.5M parameter, Apache-2.0, 영어 instruction 모델. 작은 Blue 설명·분류 후보지만 학습데이터와 실제 탐지 성능을 독립 검증해야 합니다.
- [CyberPal 2.0 20B](https://huggingface.co/cyber-pal-security/CyberPal2.0-20B): Apache-2.0 모델 카드지만 20B 규모라 현재 16 GiB 개발 환경의 기본 모델로 선택하지 않습니다.
- [network-anomaly-xgboost](https://huggingface.co/kader-xai/network-anomaly-xgboost): NSL-KDD 기반 분류 파이프라인과 자체 보고 지표가 있으나, 모델 카드 지표를 독립 재현하지 않았으므로 핵심 탐지기로 채택하지 않습니다.

## 라이선스 결론

상용 확장을 고려할 때 1차 재사용 경계는 MIT/Apache-2.0/BSD-3-Clause 구성요소와 프로세스 경계의 GPL 엔진입니다. DefenderBench와 연구·교육 전용 데이터는 배포물에서 제외합니다. 모든 최종 배포 전에는 의존성 전체의 SPDX/SBOM 및 원본 데이터 이용 조건을 다시 확인합니다.

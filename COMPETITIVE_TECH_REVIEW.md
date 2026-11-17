# 공개·상용 보안 기술 비교

확인일: 2026-11-17. 공식 저장소·공식 문서만 확인했다. 가격, 규제 인증, 기관별 계약 조건은 공개 자료만으로 확정하지 않았다.

## 공개 기술

| 기술 | 기능/운영 성숙도 | 라이선스 | Hangeul Turtle 결정 |
|---|---|---|---|
| Wazuh | XDR/SIEM, endpoint/cloud monitoring, API/RBAC 연동 가능. 성숙한 통합 플랫폼 | GPLv2/AGPLv3 구성요소 | **연동 후보**: 중앙 관제·FIM·RBAC는 재사용, 코어를 복제하지 않음 |
| Zeek | 네트워크 분석·이벤트 생성, BSD, 운영 사용 사례 풍부 | BSD | **연동 후보**: Suricata와 별도 network metadata adapter. 이번 차수 설치 안 함 |
| Suricata | IDS/IPS/NSM, EVE JSON | GPL-2.0 | **기존 오프라인 연동 유지**: live/IPS는 보류 |
| Velociraptor | host state collection/VQL, endpoint visibility | AGPLv3 및 저장소별 조건 | **보류**: 실제 호스트 수집은 현재 안전 범위 밖, 향후 승인된 fixture adapter만 검토 |
| OpenSearch Security Analytics | 규칙 기반 threat detection, findings, dashboards, notifications | Apache-2.0 | **연동 후보**: 로그 저장·검색·상관분석. 현재는 로컬 evaluator 유지 |
| Microsoft CyberBattleSim | 추상 Gym cyber range, seed 재현 | Microsoft 저장소 조건 확인 필요 | **기존 사용 유지**: Docker child worker 경계 |

공식 출처: [Wazuh](https://github.com/wazuh/wazuh), [Wazuh license](https://github.com/wazuh/wazuh/blob/main/LICENSE), [Zeek](https://github.com/zeek/zeek), [Suricata](https://github.com/OISF/suricata), [OpenSearch Security Analytics](https://github.com/opensearch-project/security-analytics), [Velociraptor](https://github.com/Velocidex/velociraptor), [CyberBattleSim](https://github.com/microsoft/CyberBattleSim).

## 모델·데이터

Qwen2.5/Qwen3, Gemma3, Phi-4 Mini는 기존 local Ollama 실험에 유지한다. Hugging Face 모델 card의 라이선스·사용 조건은 모델별로 다르며 Gemma 조건은 별도 검토가 필요하다. CICIDS 계열 등 공개 IDS 데이터셋은 실제 고객 데이터가 아니지만 label leakage, synthetic bias, 재현성 문제를 검증하기 전 학습·승격에 사용하지 않는다. 이번 차수는 모델 가중치 변경이나 학습을 수행하지 않는다.

출처: [Hugging Face models](https://huggingface.co/models), [Qwen2.5](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), [Qwen3](https://huggingface.co/Qwen/Qwen3-4B), [Gemma 3](https://huggingface.co/google/gemma-3-4b-it), [Phi-4 Mini](https://huggingface.co/microsoft/Phi-4-mini-instruct).

## 상용 제품군

| 제품군 | 실제 통제 위치/강점 | 제한 및 적용 판단 |
|---|---|---|
| Microsoft Defender XDR + Sentinel + Purview | endpoint/cloud/XDR, SIEM correlation, DLP/insider risk, enterprise identity ecosystem | 라이선스·tenant·cloud dependency와 기관별 계약 확인 필요. **연동 후보**, 대체 구현 아님 |
| CrowdStrike Falcon | endpoint EDR/XDR, response/telemetry, managed operations | 상용 agent/cloud·계약 의존. **비교 기준**, 코드 재사용 아님 |
| SentinelOne Singularity | endpoint/XDR와 autonomous response/API integration | 자동 response가 실제 운영 정책에 미치는 영향 검토 필요. **비교 기준** |
| Enterprise DLP/PAM/NAC/SIEM/SOAR | 데이터·권한·네트워크·승인·관제에 특화 | 제품별 API/RBAC/망분리/보존·가격이 다름. **연동 설계만**, 제품 선정은 고객별 별도 검토 |

출처: [Microsoft security platform](https://learn.microsoft.com/en-us/security/zero-trust/security-platform), [Microsoft Defender/Sentinel integration](https://learn.microsoft.com/en-us/security/zero-trust/siem-xdr-implement), [SentinelOne Singularity](https://www.sentinelone.com/platform/singularity-xdr-protection/), [CrowdStrike Falcon training/response](https://www.crowdstrike.com/content/dam/crowdstrike/marketing/en-us/documents/pdfs/crowdstrike-university/CSU-Training-Catalog.pdf).

## 측정 가능한 차별화 가설

Hangeul Turtle의 차별점은 “AI가 차단한다”가 아니라, AI 제안과 독립 enforcement/audit을 분리하는 것이다. 다음을 별도로 측정한다: 승인 전 I/O 거부율, 승인·만료·rollback 후 허용 범위, 모델 장애 시 fail-closed, audit 삭제·절단 검출률, 동일 event의 규칙/AI/독립 판정 일치율. 실제 고객 환경·상용 제품 성능 우위는 아직 주장하지 않는다.

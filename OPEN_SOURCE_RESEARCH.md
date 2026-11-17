# 오픈소스 기술 비교 — 2026-11-16

이번 조사는 공식 GitHub/Hugging Face 모델 카드와 Ollama 공식 문서를 검토했다. Suricata는 공식 OISF 검증 저장소의 PCAP을 확인한 뒤 Ubuntu 공식 패키지 7.0.3을 설치해 오프라인 `-r` 실행만 검증했다.

## 후보 비교

| 후보 | 공식 출처 / 라이선스 | 확인된 기능·상태 | 적용 판단 |
|---|---|---|---|
| LangGraph | https://github.com/langchain-ai/langgraph · MIT | stateful multi-actor graph, 조건부 edge와 checkpoint 구조. 활발한 main/release 상태. | **보류/1순위 후보**. 현재 `collaborative.py`의 상태·라우팅 구조가 작아 직접 구현이 더 감사 가능하며, 상태 영속화가 필요해질 때 도입 |
| Microsoft AutoGen | https://github.com/microsoft/autogen · 저장소에 MIT/CC-BY 문서 라이선스 표시, Python v0.7.5 release 확인 | multi-agent runtime, event/streaming, structured run JSON 도구 지원. | **보류**. 강력하지만 현재 dry-run·allow-list 경계보다 런타임 표면적과 의존성이 큼 |
| CrewAI | https://github.com/crewAIInc/crewAI · MIT | 역할 기반 Crews와 event-driven Flows, 활발한 저장소. | **보류**. 역할 협력에는 적합하나 정책 검증·fail-closed semantics를 별도로 다시 만들어야 함 |
| Guardrails AI | https://github.com/guardrails-ai/guardrails · MIT로 확인 | 출력 validator와 structured generation 경계. | **보류**. 현재 Ollama JSON Schema + 독립 `validate_result`가 같은 요구를 더 작은 의존성으로 충족 |
| Haystack | https://github.com/deepset-ai/haystack · Apache-2.0 | pipeline/component 기반 RAG·agent 구성. | **제외(현재)**. 이벤트 상관분석 파이프라인에는 유용하지만 현재 관측량·범위에 비해 무거움 |
| Suricata | https://github.com/OISF/suricata · GPL-2.0 | IDS/IPS/NSM 엔진, EVE JSON으로 alert·anomaly·protocol event 출력. 공식 verify PCAP의 오프라인 분석을 7.0.3에서 실행. | **오프라인 도입**. EVE→공통 사건→Blue dry-run까지만 적용; live/IPS는 제외 |
| CyberBattleSim | https://github.com/microsoft/CyberBattleSim · 기존 Docker boundary 재사용 | 추상 Gym 환경, seed 기반 재현, 격리 smoke. | **유지**. 이번 작업에서 action mask와 Docker 제한을 개선했고 외부 공격은 수행하지 않음 |

## 모델 후보

| 모델 | 공식 모델 카드 / 라이선스 | 현재 적용 |
|---|---|---|
| Qwen2.5-7B-Instruct | https://huggingface.co/Qwen/Qwen2.5-7B-Instruct · Apache-2.0 | 기준 Blue. Ollama JSON Schema 경로로 10/10 성공 |
| Qwen3-4B | https://huggingface.co/Qwen/Qwen3-4B · Apache-2.0 | 2차 검증. 비사고/비확정 관측에서 조건부 호출 |
| Gemma3-4B | https://huggingface.co/google/gemma-3-4b-it · Google Gemma terms, Hugging Face access conditions | 독립 위협 분석. 재배포·상업 사용 전 Google terms 검토 필요 |
| Phi-4-mini-instruct | https://huggingface.co/microsoft/Phi-4-mini-instruct · MIT | 정책 논리 검증. 128K context와 local quantization 후보 |

## 재사용 판단

가장 직접적인 개선은 외부 agent framework 설치가 아니라 Ollama 공식 JSON Schema 기능을 기존 local adapter에 연결한 것이다. Ollama는 `format`에 JSON Schema를 전달하면 JSON mode보다 일관된 구조화 출력을 제공한다고 문서화한다: https://ollama.com/blog/structured-outputs. 이번 차수에는 Suricata도 공식 오프라인 PCAP/EVE 경계만 도입했다.

LangGraph는 향후 상태 checkpoint·재시도·감사 trail이 필요해지면 가장 적합하지만, 현재는 작은 명시적 상태 머신이 보안 검토와 의존성 관리에 유리하다. Suricata는 GPL-2.0 프로세스를 직접 링크하지 않고 EVE JSON fixture/process boundary로 연결해야 하며, 이번 작업에서는 설치하지 않았다.

## 보안·유지보수 판단

- 외부 프레임워크를 추가하면 tool 호출, memory, callback, network client가 늘어 fail-closed 감사 범위가 커진다.
- 모든 모델 출력은 계속 untrusted data로 취급하고, 정책 DSL validator를 우회하지 않는다.
- Hugging Face 모델 라이선스는 Ollama quantization 자체의 배포 조건과 분리해 확인해야 한다.
- 현재 실제 개선이 입증된 항목은 JSON Schema 구조화 출력, 조건부 라우팅, Suricata 오프라인 EVE 전달이며, agent framework 도입 효과는 아직 측정하지 않았다.

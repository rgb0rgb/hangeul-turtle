# AI 공격 패턴 및 내부자 이상 행동 연구

## 조사 기준

공식 분류와 연구를 자체 가설과 구분했다.

| 유형 | 공식 근거 | 관측 가능한 징후 | 이번 차수 적용 |
|---|---|---|---|
| 정상 계정 악용 | MITRE ATT&CK Valid Accounts, Data from Information Repositories | 평소와 다른 장치·위치, 민감 자료 접근량 증가 | 합성 일반 사용자 이상 접근 |
| 내부자 대량 유출 | ATT&CK Data from Information Repositories, Exfiltration over Web Service | 대량 조회/복사, 외부 목적지, 민감도 | 최고 관리자 bulk export / external transfer |
| 감사 흔적 제거 | ATT&CK Indicator Removal T1070 | 로그 삭제·수정, 기록 무결성 불일치 | audit log tamper 합성 사건 |
| 단계적 침입 | ATT&CK의 단계적 tactic 관점 | 연속 단계, 권한·민감도 상승 | `sequence_step` synthetic event |
| 프롬프트 인젝션 | OWASP GenAI LLM01 | 비신뢰 문서의 지시, 시스템 지시 우회, 비밀·도구 요청 | 문서 기반 untrusted tool 요청 |
| 과도한 에이전시 | OWASP GenAI LLM06 | 모델이 승인 없이 도구·외부 시스템 호출 시도 | Blue는 후보만 생성, 독립 엔진이 보류 |
| 정상 대량 처리 오탐 | 자체 실험 가설 | 승인된 업무 배치지만 양이 큼 | `insider-normal-batch`, 오탐 0 |

MITRE ATLAS는 AI-enabled system에 대한 실제 관찰과 현실적 red-team 시연을 기반으로 하는 지식베이스로 설명되며, 이번 구현은 그 분류를 참고하되 실제 AI 공격을 실행하지 않는다. OWASP는 prompt injection과 excessive agency가 도구 권한·감독 수준에 따라 민감 정보 노출과 원치 않는 작업으로 이어질 수 있다고 설명한다.

공식 출처:

- https://attack.mitre.org/techniques/
- https://attack.mitre.org/techniques/T1070/
- https://atlas.mitre.org/
- https://atlas.mitre.org/pdf-files/SAFEAI_Full_Report.pdf
- https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
- https://github.com/OISF/suricata
- https://huggingface.co/models

## 제한

공개 사례의 존재는 특정 합성 이벤트가 공격임을 증명하지 않는다. 실제 고객 데이터·계정·네트워크와 연결하지 않았고, 시나리오의 `event`, 기대 정답, Blue 입력, 독립 정답을 분리했다.

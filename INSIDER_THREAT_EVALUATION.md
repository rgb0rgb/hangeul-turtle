# 내부자 이상 행동 평가

## 구현

- 지원 역할: 일반 사용자, 업무 담당자, 중간 관리자, 시스템 관리자, 최고 관리자, 보안 책임자.
- `insider/behavior.py`는 시간, 민감도, 데이터량, 외부 목적지, 신규 장치/위치, 단계, 비신뢰 문서, 명시적 고위험 action을 함께 평가한다.
- 역할이 높아도 정책 예외가 없다. `bulk_export`, `external_transfer`, `disable_policy`, 권한 대량 변경, 감사 로그 변경/삭제는 보류 대상이다.
- 중간 위험은 `monitoring`, 명시적 고위험은 `pending_approval`, 정상 승인 업무 배치는 `allowed`로 구분한다.

## 실제 합성 평가

명령:

```bash
python3 -c 'from evaluator.insider_evaluation import evaluate_holdout; ...'
```

9개 개발 시나리오와 별도 seed offset `100003`의 9개 holdout을 실행했다.

| 집합 | 탐지율 | 오탐률 | 감사 완전성 |
|---|---:|---:|---:|
| development | 1.0 | 0.0 | 1.0 |
| holdout | 1.0 | 0.0 | 1.0 |

정상 대량 업무 배치는 `allowed`로 유지했고, 최고 관리자 대량 고객정보 반출은 `pending_approval`로 분류했다. 결과는 `artifacts/insider_threat_evaluation.json`에 있다.

## Blue 협력

비식별화된 합성 최고 관리자 사건을 기존 Qwen2.5 → Qwen3 → Gemma3 → Phi-4 Mini 경로에 전달했다. 4/4 모델이 실제 sLLM 호출에 성공했지만, 정책 성공은 모델 다수결로 선언하지 않고 `defense_result=unknown`으로 보존했다. 증거는 `artifacts/insider_blue_collaboration.json`이다.

정책 보류·승인은 독립 엔진이 담당하고, 모델은 보조 의견만 낸다.

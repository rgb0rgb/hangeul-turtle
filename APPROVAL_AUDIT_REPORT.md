# 보류·승인·감사 보고서

## 상태 머신

`allowed`, `monitoring`, `pending_approval`, `approved`, `rejected`, `expired`, `failed`를 지원한다.

고위험 요청은 실행하지 않고 `pending_approval`에 저장하며, 로컬 알림 큐에 보안 책임자 수신 항목을 추가한다. 통보 실패는 상태를 유지하고, TTL 만료는 `expired`로 전환한다. 승인자는 `security_officer` 역할이어야 하며 요청자와 동일한 주체는 승인할 수 없다.

## 검증 결과

- 최고 관리자 대량 반출: `pending_approval`
- 자기 승인: `PermissionError`, 승인되지 않음
- 독립 보안 책임자 승인/거부 경로: 상태 머신 구현 및 테스트 통과
- 통보 실패: `pending_approval` 유지
- 승인 시간 초과: `expired`, 실행 없음
- 모든 결과: `policy_applied=false`, 실제 이메일·문자·메신저 전송 없음

## 감사 무결성

`insider/audit.py`가 이전 hash를 다음 기록에 연결하는 SHA-256 hash chain을 사용한다. 토큰·비밀번호·고객 원문 필드는 기록 전에 제거한다. 합성 기록 변조 후 `verify=false`를 확인했다. 감사 기록은 사실·승인 이력 확인용이며 법적 책임을 자동 확정하지 않는다.

실행 결과는 `artifacts/approval_audit.json`에 저장했다. 실제 계정, 고객 원문, 비밀 토큰은 사용하지 않았다.

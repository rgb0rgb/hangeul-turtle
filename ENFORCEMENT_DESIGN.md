# W-ENFORCE-1 / W-AUDIT-1 설계

## 범위

현재 구현은 `/tmp/ahs-enforce-*` 임시 디렉터리 안의 합성 파일에만 적용된다. 호스트 루트, 실제 방화벽, 운영 네트워크, 고객 데이터에는 연결되지 않는다.

## 상태와 신뢰 경계

`pending_approval → approved | rejected | expired`; approved 작업은 `rollback → rejected`로 전환된다. 기본값은 거부다.

요청은 `event_id`, 상대 resource, operation, requester, approver, expiry, policy version에 바인딩된다. 요청자와 승인자는 달라야 하며 승인자는 `security_officer`여야 한다. approval token은 hash만 저장하고 재사용할 수 없다.

LLM은 이 상태기계를 변경할 수 없다. AI는 설명·후보만 제공하고, gate가 실제 `open/read/write` 호출 전 승인·범위·만료·rollback을 독립 검사한다.

## 실제 I/O 검증

`artifacts/enforcement_w1.json`에 기록된 격리 실험:

- 승인 전 read: 거부
- 독립 승인 후 정확한 sandbox 파일 read: 허용, 실제 I/O 관찰
- rollback 후 read: 거부
- 범위 밖 경로: 거부
- 자기 승인·토큰 재사용: 거부
- 외부 witness의 audit record 삭제: 검출

이는 애플리케이션 sandbox gate의 실제 I/O 증거이며 OS 전체 차단이나 방화벽 차단을 의미하지 않는다.

## W-AUDIT-1

기존 in-memory hash chain은 현재 리스트 제자리 변조를 검출하지만 리스트 삭제·절단은 기준점이 없으면 놓칠 수 있다. `insider/witness.py`는 독립 sequence/hash anchor를 유지해 record 삭제, 순서 변경, 내용 수정을 검출한다. 실제 운영에서는 append-only 저장소, 외부 witness/KMS 서명, 보존기간, 시계 동기화가 별도로 필요하다.

## 미구현/보류

- 실제 host ACL, kernel/file-system enforcement, firewall/IPS는 범위 밖
- 2대 Red 노트북–Blue 데스크톱 topology는 사용자 승인 전 변경하지 않음
- 영속 외부 witness와 HA/DR은 설계만 완료
- 정책 자동 승격 금지

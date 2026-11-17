# Acceptance criteria — stage 1

- [x] 합성 이벤트만 생성하고 `is_demo=true`를 강제한다.
- [x] 허용되지 않은 시나리오 ID를 거부한다.
- [x] 같은 seed에서 같은 이벤트를 재생성한다.
- [x] Docker compose에 host network, privileged, ports가 없다.
- [x] 정책 후보는 `observe` 또는 `block_dry_run`만 허용하고 승인을 요구한다.
- [ ] 100회 실험 및 모델 digest 저장 — 단계 3 대상
- [ ] 실제 네트워크 관찰 — 단계 5 대상, 별도 승인 필요

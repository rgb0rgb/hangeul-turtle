# Architecture

```text
synthetic simulator -> Red catalog selector -> event stream -> Blue rule analyzer
                                                     |              |
                                                     +-> evaluator -+-> report
```

초기 구현은 단일 데스크톱에서 실행되는 결정론적 모드입니다. 실제 노트북 Red 연결, Raspberry Pi 관찰, Android 알림, nftables 적용기는 아직 미구현이며 운영망 변경 없이 후속 단계에서 검증합니다.

- `simulator/`: 합성 IoT/계정 이벤트 생성
- `agents/red/`: 허용 카탈로그 선택
- `agents/blue/`: 규칙 기반 탐지와 dry-run 정책 후보
- `evaluator/`: 독립적인 지표 산출
- `gateway/`: 향후 어댑터 자리표시자
- `tests/`: 재현성·안전 경계 테스트

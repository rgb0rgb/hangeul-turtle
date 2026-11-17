# Red AI 노트북 통신 보고서

검증일: 2026-11-15

## 구현

- 기존 웹 서버 `127.0.0.1:8090`은 변경하지 않았습니다.
- 별도 Red API `backend/red_api.py`를 추가했습니다. 기본 포트는 `8091`입니다.
- `X-Red-Token` 전용 토큰, 허용 IP 목록, 2KB 요청 제한, 5초 서버 timeout, IP별 분당 20회 rate limit을 적용했습니다.
- 입력은 `scenario_id`와 정수 `seed`만 허용하며, 승인 catalog 밖의 값·명령·URL·주소는 거부합니다.
- 응답은 `mock_only`, `external_network=false`, `dry-run`을 명시합니다.
- `notebook_red/client.py`와 노트북 실행 안내를 별도 디렉터리에 준비했습니다.

## 실행 검증

- localhost 전용 Red API 통신 테스트와 기존 회귀 테스트: **20/20 통과**.
- 인증 실패, demo-token 거부, schema 위반, 승인되지 않은 시나리오, seed 범위 오류, 추가 command 필드 거부를 확인했습니다.
- 실제 노트북 `192.168.0.56`에서 데스크톱으로 접속한 결과는 아직 측정하지 않았습니다. 따라서 LAN 통신 완료로 보고하지 않습니다.

현재 상태 조회에서 기존 portproxy는 8080/8501만 존재했고 8091은 비어 있었습니다. WSL 주소는 172.31.99.66, Windows WSL 어댑터는 172.31.96.1이었습니다. 상세 Windows 방화벽 조회는 관리자 권한 부족으로 거부되어 변경하지 않았습니다. 추가 명령과 원상복구 명령은 `WSL_RED_LAN_PLAN.md`에 기록했습니다.

## 설정 적용 시도 결과

- Windows의 실제 LAN 인터페이스 별칭은 영어 `Ethernet`이 아니며, 전체 조회에서 네트워크 프로필은 **Public**으로 확인되었습니다.
- 기존 portproxy는 8080/8501만 존재하고 8091은 여전히 없습니다.
- 8091 방화벽 규칙 상세 조회는 Windows 관리자 권한 부족으로 거부되었습니다.
- Public 프로필 상태에서 `Profile Private` 규칙을 추가하면 의도대로 동작하지 않을 수 있으므로 portproxy와 방화벽을 추가하지 않았습니다.
- 따라서 실제 노트북 연결·인증·peer IP 전달 검증은 수행하지 않았고, 기존 설정도 변경하지 않았습니다.

다음 승인 전제: Windows 관리자 PowerShell에서 LAN 네트워크를 Private으로 전환할지 사용자 판단이 필요합니다. 전환 후 기존 8091 방화벽 충돌을 관리자 권한으로 재조회하고, 충돌이 없을 때만 8091 추가를 진행합니다.

## 조건부 승인 후 확인

- 사용자 관리 LAN이라는 조건부 승인을 받았습니다.
- 현재 WSL에서 호출된 Windows PowerShell identity는 `god0\\tiger`이며 관리자 토큰이 아닙니다.
- 인터페이스 index `8`의 Realtek Gaming GbE가 `192.168.0.20` 이더넷이며 현재 프로필은 `Public`입니다.
- 기존 8080/8501 portproxy는 그대로 확인되었습니다.
- 방화벽 규칙 조회는 `System Error 5 / Access Denied`로 실패했습니다. 관리자 PowerShell이 아니므로, 프로필 변경·portproxy 추가·방화벽 변경은 실행하지 않았습니다.

## 네트워크 제한

WSL2 주소 `172.31.99.66`은 NAT 환경에서 노트북에 직접 라우팅되지 않을 수 있습니다. Windows portproxy/WSL mirrored networking 및 Defender Firewall 인바운드 규칙이 필요할 수 있으나, 이는 관리자 권한과 호스트 상태 변경을 요구하므로 실행하지 않았습니다. 실제 연결 전에 해당 변경에 대한 승인이 필요합니다.

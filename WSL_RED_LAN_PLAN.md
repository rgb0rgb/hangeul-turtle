# WSL2 Red API LAN 연결 사전 검토

검토일: 2026-11-15

## 현재 상태 조회 결과

- WSL IPv4: `172.31.99.66/20`
- WSL 기본 게이트웨이/Windows WSL 어댑터: `172.31.96.1`
- Windows LAN 주소: `192.168.0.20`
- 기존 portproxy: `192.168.0.20:8080 -> 172.31.99.66:8080`, `192.168.0.20:8501 -> 172.31.99.66:8501`
- `8091` portproxy: 없음
- WSL의 8090/8091 listener: 조회 시 실행 중인 서비스 없음
- Windows 방화벽 상세 조회: 관리자 권한 부족으로 읽기 거부. 변경하지 않음.

현재 Windows LAN 네트워크 프로필은 `Public`으로 확인되었습니다. 따라서 `Profile Private` 규칙을 바로 추가하지 않습니다.

기존 portproxy와 방화벽 규칙은 삭제·덮어쓰지 않습니다.

## 권장 최소 변경안 — 승인 후 실행

관리자 PowerShell에서 현재 상태를 다시 저장/확인한 뒤 다음을 추가합니다.

```powershell
netsh interface portproxy show all
netsh interface portproxy add v4tov4 listenaddress=192.168.0.20 listenport=8091 connectaddress=172.31.99.66 connectport=8091
New-NetFirewallRule -DisplayName "AI Home Shield Red API 8091" -Direction Inbound -Action Allow -Protocol TCP -LocalAddress 192.168.0.20 -LocalPort 8091 -RemoteAddress 192.168.0.56 -Profile Private
```

이 규칙은 인터넷 공개나 공유기 포트포워딩을 만들지 않고, Windows LAN 주소의 TCP 8091에 대해 노트북 주소만 허용하는 설계입니다. 네트워크 프로필이 Private이 아니라면 프로필을 먼저 확인해야 합니다.

## 원상복구 명령 — 승인된 추가분만

```powershell
Remove-NetFirewallRule -DisplayName "AI Home Shield Red API 8091"
netsh interface portproxy delete v4tov4 listenaddress=192.168.0.20 listenport=8091
```

기존 8080/8501 항목에는 이 명령을 적용하지 않습니다.

## WSL 서비스 실행

```bash
cd /root/AI_Home_Shield_v3
export AI_HOME_SHIELD_RED_TOKEN='전용 랜덤 토큰'
python3 -m backend.red_api --host 172.31.99.66 --port 8091 --token "$AI_HOME_SHIELD_RED_TOKEN" --allow-ip 172.31.96.1 --allow-ip 192.168.0.56
```

WSL2 NAT portproxy에서는 TCP source가 WSL에 `172.31.96.1`로 보일 수 있습니다. Windows 방화벽이 실제 노트북 `192.168.0.56`만 허용하므로, 이 두 계층을 함께 사용합니다. 첫 연결 시 Red API의 audit 로그 또는 임시 read-only 진단으로 실제 peer 주소를 확인하고, 확인 후 불필요한 allow-list 항목은 제거합니다.

## WSL IP 변경 복구

WSL 재시작 후 `hostname -I` 또는 `ip -4 addr show eth0`로 주소를 확인합니다. 주소가 바뀌면 기존 portproxy를 삭제하지 않고, 승인된 동일 listen 주소에 대해 connect 주소만 갱신해야 합니다. `netsh interface portproxy set v4tov4 ...` 사용 가능 여부를 먼저 확인하고, 실패하면 해당 listen 항목을 삭제 후 같은 항목을 다시 추가합니다. 변경 전 `show all` 출력과 변경 후 출력을 보관합니다.

## 검증 상태

현재는 localhost Red API 왕복과 20개 자동 테스트만 완료했습니다. 실제 노트북 `192.168.0.56`에서의 연결, portproxy 동작, WSL peer 주소 전달은 아직 검증하지 않았습니다. 관리자 권한 변경에 대한 사용자 승인 전에는 실행하지 않습니다.

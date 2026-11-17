# 노트북 Red AI 연결 시험

이 디렉터리는 Python 3.12 표준 라이브러리만 사용하는 클라이언트입니다. `demo-token`은 사용하지 않습니다.

## 데스크톱 WSL에서 먼저 실행

```bash
cd /root/AI_Home_Shield_v3
export AI_HOME_SHIELD_RED_TOKEN='긴 임의의 전용 토큰'
python3 -m backend.red_api --host 172.31.99.66 --port 8091 --token "$AI_HOME_SHIELD_RED_TOKEN" --allow-ip 192.168.0.56
```

현재 구현은 서비스 자체의 source IP allow-list를 적용합니다. WSL NAT portproxy를 사용하면 서비스가 노트북 대신 `172.31.96.1`을 peer로 볼 수 있으므로 실제 첫 연결 전에 `--allow-ip 172.31.96.1`을 추가하고, Windows 방화벽에서 `192.168.0.56`만 허용해야 합니다. WSL IP는 재시작 때 바뀔 수 있습니다.

## 노트북 Windows PowerShell

```powershell
py -3.12 notebook_red\client.py --url http://<접속가능한-데스크톱-주소>:8091 --token $env:AI_HOME_SHIELD_RED_TOKEN --scenario login_burst --seed 42
```

WSL2 NAT 환경에서는 노트북이 `172.31.99.66`에 직접 도달하지 못할 수 있습니다. Windows portproxy, WSL mirrored networking, Windows Defender Firewall 변경은 호스트 관리자 변경이므로 승인 후에만 수행합니다. 아직 이 프로젝트에서는 해당 변경을 실행하지 않았습니다.

성공 응답은 `execution_status=mock_only`, `external_network=false`, `policy_mode=dry-run`을 포함해야 합니다. 이는 실제 외부 공격이나 운영 방화벽 변경이 아닙니다.

# Suricata 오프라인 분석 보고서

## 실행

- 설치 버전: Suricata 7.0.3 (Ubuntu Noble 패키지; GPL-2.0 프로젝트)
- PCAP: 공식 OISF `suricata-verify` 저장소의 `tests/bug-4663-03/icmp_and_ssh.pcap`
- 실행: `suricata -r .../input.pcap -S suricata_offline/test.rules -l ... -c /etc/suricata/suricata.yaml --runmode single -k none`
- 라이브 인터페이스, LAN 캡처, IPS, 방화벽 변경은 사용하지 않았다.

## 결과

실제 오프라인 처리로 `eve.json` 이벤트 6건이 생성됐다. `suricata_offline/parser.py`가 이를 공통 사건 구조로 변환했고, `suricata_offline/blue.py`가 Blue dry-run 입력으로 전달했다. 그 중 alert 3건은 탐지됐고, 나머지 flow 관측은 비탐지로 분류됐다. 결과는 `artifacts/suricata_offline.json`에 저장했다.

모든 후보 정책은 `block_dry_run` 또는 `observe`이며 관리자 승인 전에는 적용되지 않는다. 패킷 관측은 CyberBattleSim 추상 관측과 합산하지 않았다.

## 한계

테스트 규칙은 오프라인 검증용으로 저장했으며 실제 네트워크 방어 정책이 아니다. Suricata 사건의 Blue sLLM 협력 호출은 현재 공통 사건 전달 경계까지만 검증했고, CyberBattleSim 성능 지표와 통합하지 않았다.

# Security boundaries

- 모든 이벤트는 `is_demo: true`인 합성 데이터입니다.
- Red에는 임의 명령 실행·스캔·악용 기능이 없습니다.
- Docker 실험실 네트워크는 internal이며 외부 egress를 제공하지 않습니다.
- 정책은 `dry-run`, 만료, 롤백, 승인 필요를 기본으로 합니다.
- 암호화된 통신 내용을 복호화하거나 원시 개인정보를 업로드하지 않습니다.

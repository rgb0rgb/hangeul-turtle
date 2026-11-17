# WSL2 migration report

- 원본: `/mnt/x/AI_Home_Shield_v3`
- 이전 위치: `/root/AI_Home_Shield_v3`
- 방법: `rsync -a` with exclusions for `.venv`, `__pycache__`, `.pyc`, pytest/mypy cache
- 원본 삭제: 하지 않음
- 현재 Ubuntu 사용자는 `root`뿐이므로 일반 사용자 홈은 `/root`로 적용
- `.venv` 생성 완료, Python 3.12.3 확인
- Git 상태: 원본은 Git 저장소가 아니므로 branch/status 정보 없음
- 재검증: 다음 TEST_REPORT에 기록된 새 위치 테스트를 수행

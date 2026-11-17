# Model evaluation

현재 Ollama/llama.cpp 모델은 연결하지 않았습니다. 이유는 환경 점검에서 Ollama 서버가 실행 중이지 않고 GPU 접근도 확인되지 않았기 때문입니다. 따라서 현재 결과는 SLM 성능이 아니라 규칙 기반 기준선과 Blue 분석기의 합성 이벤트 처리 결과입니다.

모델 연결 조건:

1. 모델 digest, seed, temperature, context 설정을 실험 ID와 함께 저장
2. JSON schema 외 출력 거부
3. 외부 로그를 명령으로 해석하지 않음
4. 정책 후보는 독립 검증·영향평가·승인 전까지 dry-run
5. 학습 데이터와 holdout 시나리오 분리

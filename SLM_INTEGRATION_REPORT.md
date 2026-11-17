# SLM integration report

검증일: 2026-11-15

## 선정

Ollama 0.30.6을 사용했습니다. 데스크톱에서 이미 실행되며 `qwen2.5:7b`가 설치되어 있고, 로컬 subprocess 호출로 외부 API 없이 검증할 수 있습니다. `llama-cli`는 현재 환경에서 확인되지 않았습니다.

모델: `qwen2.5:7b`, 7.6B, Q4_K_M, 4.7GB, local ID `845dbda0ea48`, blob SHA-256 `2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730`, Apache-2.0.

## 실제 결과

실제 호출 1회가 약 16.7초에 완료되었습니다. 모델 출력은 JSON처럼 보였지만 Markdown fence, 허용되지 않은 자연어 action, `approval_required=false`가 있어 거부되었습니다. 규칙 기반 결과를 유지했고, 임의 명령은 실행하지 않았습니다.

현재 상태는 `slm_inference` transport 확인 및 `slm_fallback` 안전 경로 검증입니다. 유효한 SLM 방어 정책 성공이나 가중치 학습 완료로 표시하지 않습니다.

## 구현 경계

외부 로그는 `UNTRUSTED_DATA`로 구분하고, shell/network/firewall 명령 패턴은 거부합니다. 허용 action은 `observe`, `block_dry_run`뿐이며 승인은 항상 true여야 합니다.

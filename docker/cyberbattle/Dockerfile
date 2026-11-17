FROM python:3.10-slim
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir "git+https://github.com/microsoft/CyberBattleSim.git@main"
COPY smoke_test.py /opt/ai_home_shield_smoke_test.py
ENTRYPOINT ["python", "/opt/ai_home_shield_smoke_test.py"]

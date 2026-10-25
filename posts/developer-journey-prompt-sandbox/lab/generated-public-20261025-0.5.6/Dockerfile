FROM fc-e2b-registry.cn-hangzhou.cr.aliyuncs.com/runtime/base:v0.0.49

USER root
RUN python3 -m pip install --index-url https://pypi.org/simple --no-cache-dir "agent-sandbox-server==0.4.0a6"
USER user

WORKDIR /home/user/app
COPY commands.py .
EXPOSE 9000
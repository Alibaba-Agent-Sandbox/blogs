FROM fc-e2b-registry.cn-hangzhou.cr.aliyuncs.com/runtime/base:v0.0.49

USER root

RUN python3 -m pip install --index-url https://pypi.org/simple --no-cache-dir "agent-sandbox-server==0.3.1a1"

WORKDIR /home/user/app

COPY commands.py .

RUN chown -R user:user /home/user/app

USER user

EXPOSE 9000

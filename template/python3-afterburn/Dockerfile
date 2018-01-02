FROM python:3-alpine

# Alternatively use ADD https:// (which will not be cached by Docker builder)
RUN apk --no-cache add curl \
    && echo "Pulling watchdog binary from Github." \
    && curl -sSL https://github.com/openfaas-incubator/of-watchdog/releases/download/0.1.0/of-watchdog > /usr/bin/fwatchdog \
    && chmod +x /usr/bin/fwatchdog \
    && apk del curl --no-cache

WORKDIR /root/

COPY index.py           .
COPY requirements.txt   .
RUN pip install -r requirements.txt

COPY function           function
RUN touch ./function/__init__.py

WORKDIR /root/function/
COPY function/requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /root/

ENV fprocess="python index.py"
ENV afterburn=true
ENV mode=afterburn

HEALTHCHECK --interval=1s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]

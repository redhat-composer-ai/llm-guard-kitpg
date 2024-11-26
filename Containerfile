FROM registry.access.redhat.com/ubi9/python-311 as builder
USER root
ENV GIT_SSL_NO_VERIFY="true"

RUN dnf update -y --security  --nodocs --setopt install_weak_deps=False && \
    dnf clean all -y && \
    rm -rf /var/cache/yum

COPY requirements.txt requirements.txt
RUN python -m venv .venv && \
    source .venv/bin/activate && \
    python -m pip install -r requirements.txt

FROM registry.access.redhat.com/ubi9/python-311
USER root

COPY *.py scan.config.yaml requirements.txt README.md ./
COPY llm_guard/ llm_guard/
COPY --from=builder --chown=1123:0 /opt/app-root/src/.venv /opt/app-root/src/.venv

RUN /opt/app-root/src/.venv/bin/python utils.py && \
    dnf update -y --security  --nodocs --setopt install_weak_deps=False && \
    dnf clean all -y && \
    rm -rf /var/cache/yum && \
    fix-permissions /opt/app-root/src -P && \
    echo "" > /opt/app-root/bin/activate
USER 1123
EXPOSE 8443
CMD ["/opt/app-root/src/.venv/bin/python", "-m", "gunicorn", "-c", "api.py", "-b", "0.0.0.0:8443", "api:app"]

FROM python:3.13.2-slim-bookworm@sha256:6b3223eb4d93718828223966ad316909c39813dee3ee9395204940500792b740
RUN groupadd --gid 1000 solver && useradd --uid 1000 --gid 1000 --no-create-home solver \
    && mkdir /workspace && chown 1000:1000 /workspace
COPY docker/worker.py /opt/ctf/worker.py
USER 1000:1000
WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
CMD ["sleep", "infinity"]

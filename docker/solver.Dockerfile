FROM python:3.13.2-slim-bookworm@sha256:6b3223eb4d93718828223966ad316909c39813dee3ee9395204940500792b740
RUN apt-get update && apt-get install -y --no-install-recommends \
    file binutils xxd curl netcat-openbsd openssl unzip zip gcc libc6-dev lib32stdc++6 make gdb \
    && dpkg-query -W > /opt/os-packages.txt \
    && rm -rf /var/lib/apt/lists/*
COPY docker/solver-requirements.txt /opt/ctf/solver-requirements.txt
RUN python -m pip install --no-cache-dir -r /opt/ctf/solver-requirements.txt \
    && python -m pip check \
    && python -m pip freeze --all > /opt/python-packages.txt
RUN groupadd --gid 1000 solver && useradd --uid 1000 --gid 1000 --no-create-home solver \
    && mkdir /workspace && chown 1000:1000 /workspace
COPY docker/worker.py /opt/ctf/worker.py
USER 1000:1000
WORKDIR /workspace
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PWNLIB_NOTERM=1 HOME=/workspace
ENV PATH=/workspace/.venv/bin:$PATH TMPDIR=/workspace PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
CMD ["/usr/local/bin/python", "-I", "/opt/ctf/worker.py", "--serve"]

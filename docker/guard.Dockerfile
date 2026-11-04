FROM python:3.13.2-slim-bookworm@sha256:6b3223eb4d93718828223966ad316909c39813dee3ee9395204940500792b740
RUN apt-get update && apt-get install -y --no-install-recommends \
    nftables=1.0.6-2+deb12u2 iproute2=6.1.0-3 tcpdump=4.99.3-1 \
    && dpkg-query -W > /opt/os-packages.txt \
    && rm -rf /var/lib/apt/lists/*
COPY docker/guard.py /opt/ctf/guard.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
CMD ["python", "-I", "/opt/ctf/guard.py"]

# A listener-only correction for the two verified socat 1.7.3.2 target images.
# TARGET_IMAGE is an original registry reference pinned by digest.
ARG TARGET_IMAGE=llmctf/2020q-pwn-roppity@sha256:e0fe9b2db871e1324ab71bc85d308783b6224fd62271d8ea4df3962aace4047c
FROM ${TARGET_IMAGE} AS package
ADD --checksum=sha256:deeaf50bf877d5474fb8654695ab745a54da20e1536a5d5a9492c0966f9c01cf \
    https://archive.ubuntu.com/ubuntu/pool/main/s/socat/socat_1.7.3.3-2_amd64.deb /tmp/socat.deb
RUN dpkg-deb --extract /tmp/socat.deb /tmp/socat

FROM ${TARGET_IMAGE}
COPY --from=package /tmp/socat/usr/bin/socat /usr/bin/socat
LABEL org.ctf590.compatibility="socat-1.7.3.3"

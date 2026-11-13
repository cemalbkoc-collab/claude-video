# n8n with ffmpeg (static build, includes libass for burned-in captions) and DejaVu fonts
# (full Turkish character coverage). The render step runs inside this container.
FROM mwader/static-ffmpeg:7.1 AS ffmpeg

FROM debian:bookworm-slim AS fonts
RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

FROM n8nio/n8n:stable
COPY --from=ffmpeg /ffmpeg /ffprobe /usr/local/bin/
COPY --from=fonts /usr/share/fonts/truetype/dejavu /opt/fonts

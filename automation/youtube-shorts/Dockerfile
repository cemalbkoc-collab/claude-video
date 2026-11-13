# n8n with ffmpeg (static build, includes libass for burned-in captions), DejaVu fonts
# (full Turkish character coverage) and yt-dlp. Render steps run inside this container.
FROM mwader/static-ffmpeg:7.1 AS ffmpeg

FROM debian:bookworm-slim AS fonts
RUN apt-get update \
 && apt-get install -y --no-install-recommends fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

FROM n8nio/n8n:stable
COPY --from=ffmpeg /ffmpeg /ffprobe /usr/local/bin/
COPY --from=fonts /usr/share/fonts/truetype/dejavu /opt/fonts

# yt-dlp for the gaming-clip workflow. It uses the image's own Node.js as the
# JavaScript runtime YouTube now requires (make-clip.mjs passes --js-runtimes node).
USER root
ARG YTDLP_VERSION=2026.10.26
RUN apk add --no-cache python3 \
 && wget -qO /usr/local/bin/yt-dlp "https://github.com/yt-dlp/yt-dlp/releases/download/${YTDLP_VERSION}/yt-dlp" \
 && chmod a+rx /usr/local/bin/yt-dlp
USER node

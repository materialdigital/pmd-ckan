# Sparklis (https://github.com/sebferre/sparklis, Apache-2.0) is a static browser
# application: the OCaml sources are already compiled to webapp/osparklis.js in the
# repository. The upstream image (sferre/sparklis) is built on an unmaintained
# bitnami/nginx 1.23 base from January 2023 and carries its CVEs, so we build our own
# image: the pinned upstream files on a current unprivileged nginx (listens on 8080).
#
# To update: bump SPARKLIS_REF to a newer upstream commit and the nginx tag.

ARG SPARKLIS_REF=8a2f573cc9a9e2fbffb4071eb37452ae5f80ade3

FROM alpine:3.22 AS src
ARG SPARKLIS_REF
RUN apk add --no-cache git \
 && git clone https://github.com/sebferre/sparklis.git /src \
 && git -C /src checkout "${SPARKLIS_REF}"

FROM nginxinc/nginx-unprivileged:1.30-alpine
# pick up Alpine security fixes that are newer than the base image
USER root
RUN apk upgrade --no-cache
USER 101
COPY --from=src /src/webapp /usr/share/nginx/html
COPY --from=src /src/docker/index.html /usr/share/nginx/html/index.html
COPY --from=src /src/LICENSE /usr/share/nginx/html/LICENSE
COPY default.conf /etc/nginx/conf.d/default.conf

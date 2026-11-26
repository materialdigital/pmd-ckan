# Sparklis (https://github.com/sebferre/sparklis, Apache-2.0) is a static browser
# application: the OCaml sources are already compiled to webapp/osparklis.js in the
# repository. The upstream image (sferre/sparklis) is built on an unmaintained
# bitnami/nginx 1.23 base from January 2023, so we build our own
# image: the pinned upstream files served by the official nginx image as a non-root user.
#
# To update: bump SPARKLIS_REF to a newer upstream commit; the nginx tag follows the stack (compose.yaml).

ARG SPARKLIS_REF=8a2f573cc9a9e2fbffb4071eb37452ae5f80ade3

FROM alpine:3.22 AS src
ARG SPARKLIS_REF
RUN apk add --no-cache git \
 && git clone https://github.com/sebferre/sparklis.git /src \
 && git -C /src checkout "${SPARKLIS_REF}"

FROM nginx:1.30-alpine
# pick up Alpine security fixes that are newer than the base image
RUN apk upgrade --no-cache
COPY --from=src /src/webapp /usr/share/nginx/html
COPY --from=src /src/docker/index.html /usr/share/nginx/html/index.html
COPY --from=src /src/LICENSE /usr/share/nginx/html/LICENSE
# non-root: pid and temp files in /tmp, listens on 8080 (see default.conf)
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf
USER nginx
EXPOSE 8080

# Apache Jena Fuseki, adopted from https://github.com/SemanticComputing/fuseki-docker (Apache-2.0),
# the source of secoresearch/fuseki. The published image is a stale build (old Alpine/JDK layers), so we build it
# ourselves on a current eclipse-temurin base.
#
# What is taken from upstream (pinned commit): this Dockerfile's steps, docker-entrypoint.sh, shiro.ini,
# assembler.ttl and fuseki-config.ttl (the SeCo silk-arq extension jar is left out, see below). compose.yaml still overrides the
# entrypoint with config/fuseki/entrypoint.sh, which calls /docker-entrypoint.sh.
#
# To update Jena: bump FUSEKI_VERSION and both checksums (https://jena.apache.org/download/, the .sha512 files
# at https://downloads.apache.org/jena/binaries/). To update the upstream files: bump FUSEKI_DOCKER_REF.

ARG FUSEKI_DOCKER_REF=10837b276ab119ed145836d5e3916543e0bdf802

FROM alpine:3.22 AS src
ARG FUSEKI_DOCKER_REF
RUN apk add --no-cache git \
 && git clone https://github.com/SemanticComputing/fuseki-docker.git /src \
 && git -C /src checkout "${FUSEKI_DOCKER_REF}"

FROM eclipse-temurin:21-jre-alpine

LABEL maintainer="jouni.tuominen@aalto.fi" \
      org.opencontainers.image.source="https://github.com/SemanticComputing/fuseki-docker"

# pick up security fixes that are newer than the base image; jq is needed for tdb2.xloader
RUN apk upgrade --no-cache \
 && apk add --no-cache bash ca-certificates coreutils findutils jq pwgen ruby wget

# Update below according to https://jena.apache.org/download/
ENV FUSEKI_VERSION 6.3.0
ENV FUSEKI_SHA512 18bb611a667d70842243b423fecd36c247e43d495d12889908e38711b57bea547d07641bd8b6dcacba6e40c019e6fce736adb3240e63799676bfba31c3e3bc7f
ENV JENA_VERSION 6.3.0
ENV JENA_SHA512 828ac4bc3b377eacbadd888de5558039688a28eb5357fc741c2eb833582447f53455f75857bd1c832114c9d58beb671d581bad84ea5f0f31d3aff74fe805f0ce

ENV MIRROR https://dlcdn.apache.org
ENV ARCHIVE https://archive.apache.org/dist

# Config and data
ENV FUSEKI_BASE /fuseki-base

# Fuseki installation
ENV FUSEKI_HOME /jena-fuseki

ENV JENA_HOME /jena
ENV JENA_BIN $JENA_HOME/bin

WORKDIR /tmp
# sha512 checksum
RUN echo "$FUSEKI_SHA512  fuseki.tar.gz" > fuseki.tar.gz.sha512
# Download/check/unpack/move Fuseki in one go (to reduce image size)
RUN (wget -O fuseki.tar.gz $MIRROR/jena/binaries/apache-jena-fuseki-$FUSEKI_VERSION.tar.gz || \
     wget -O fuseki.tar.gz $ARCHIVE/jena/binaries/apache-jena-fuseki-$FUSEKI_VERSION.tar.gz) && \
    sha512sum -c fuseki.tar.gz.sha512 && \
    tar zxf fuseki.tar.gz && \
    mv apache-jena-fuseki* $FUSEKI_HOME && \
    rm fuseki.tar.gz* && \
    cd $FUSEKI_HOME && rm -rf fuseki.war

# Get tdb1.xloader and tdb2.xloader from Jena
# sha512 checksum
RUN echo "$JENA_SHA512  jena.tar.gz" > jena.tar.gz.sha512
# Download/check/unpack/move Jena in one go (to reduce image size)
RUN (wget -O jena.tar.gz $MIRROR/jena/binaries/apache-jena-$JENA_VERSION.tar.gz || \
     wget -O jena.tar.gz $ARCHIVE/jena/binaries/apache-jena-$JENA_VERSION.tar.gz) && \
    sha512sum -c jena.tar.gz.sha512 && \
    tar zxf jena.tar.gz && \
    mkdir -p $JENA_BIN && \
    mv apache-jena*/lib $JENA_HOME && \
    mv apache-jena*/bin/tdb1.xloader apache-jena*/bin/xload-* $JENA_BIN && \
    mv apache-jena*/bin/tdb2.xloader $JENA_BIN && \
    rm -rf apache-jena* && \
    rm jena.tar.gz*

# As "localhost" is often inaccessible within Docker container,
# we'll enable basic-auth with a random admin password
# (which we'll generate on start-up)
COPY --from=src /src/shiro.ini /jena-fuseki/shiro.ini
COPY --from=src /src/docker-entrypoint.sh /
RUN chmod 755 /docker-entrypoint.sh

# Upstream also ships the SeCo silk-arq extension jar here. It is left out on purpose: it is a SNAPSHOT
# fat jar that bundles outdated, unmaintained dependencies, and nothing in this stack uses its SPARQL
# functions. To restore it:
#   COPY --from=src /src/silk-arq-1.0.0-SNAPSHOT-with-dependencies.jar /javalibs/
# (/javalibs stays on the classpath, so the compose command is unchanged)
RUN mkdir -p /javalibs

# Fuseki config
ENV ASSEMBLER $FUSEKI_BASE/configuration/assembler.ttl
COPY --from=src /src/assembler.ttl $ASSEMBLER
ENV CONFIG $FUSEKI_BASE/config.ttl
COPY --from=src /src/fuseki-config.ttl $CONFIG
RUN mkdir -p \
    $FUSEKI_BASE/backups \
    $FUSEKI_BASE/databases

# Set permissions to allow fuseki to run as an arbitrary user
RUN chgrp -R 0 $FUSEKI_BASE \
    && chmod -R g+rwX $FUSEKI_BASE

# Tools for loading data
ENV JAVA_CMD java -cp "$FUSEKI_HOME/fuseki-server.jar:/javalibs/*"
ENV TDBLOADER $JAVA_CMD tdb.tdbloader --desc=$ASSEMBLER
ENV TDB1XLOADER $JENA_BIN/tdb1.xloader --loc=$FUSEKI_BASE/databases/tdb
ENV TDB2TDBLOADER $JAVA_CMD tdb2.tdbloader --desc=$ASSEMBLER
ENV TDB2XLOADER $JENA_BIN/tdb2.xloader --loc=$FUSEKI_BASE/databases/tdb
ENV TEXTINDEXER $JAVA_CMD jena.textindexer --desc=$ASSEMBLER
ENV TDBSTATS $JAVA_CMD tdb.tdbstats --desc=$ASSEMBLER
ENV TDB2TDBSTATS $JAVA_CMD tdb2.tdbstats --desc=$ASSEMBLER

WORKDIR /jena-fuseki
EXPOSE 3030
USER 9008

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["java", "-cp", "*:/javalibs/*", "org.apache.jena.fuseki.main.cmds.FusekiServerCmd"]

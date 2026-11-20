FROM ckan/ckan-base:2.12.1

USER root

ENV APP_DIR=/srv/app
RUN echo ${TZ} > /etc/timezone

# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
    cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
    fi ;

ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

RUN buildDeps='locales libpcre3 libpcre3-dev supervisor git wget' \
    && set -x \
    && apt-get update && apt-get install -y $buildDeps --no-install-recommends \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && sed -i 's/^# de_DE.UTF-8 UTF-8$/de_DE.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen en_US.UTF-8 de_DE.UTF-8

# Copy custom initialization scripts
COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY --chown=ckan-sys:ckan-sys patches ${APP_DIR}/patches

# Install extensions from PyPI. The Git installs below are pinned to exact commits (reproducible builds;
# ckanext-harvest >= f40fdbc already sets redis socket_timeout=None itself, so no local patch is needed):
#   citeproc, excelforms  — not on PyPI
#   harvest               — PyPI release is too old for CKAN 2.12
RUN pip3 install --no-cache-dir \
        "ckanext-csvtocsvw>=1.0.5" \
        "ckanext-csvwmapandtransform>=1.1.1" \
        "ckanext-fuseki>=1.2.0" \
        "ckanext-pdfview>=0.0.6" \
        "ckanext-multiuploadform>=1.3.4" \
        "ckanext-sso>=1.1.0" \
        "ckanext-markdown-view>=1.0.3" \
        "ckanext-scheming>=3.1.0" \
        "ckanext-dcat>=2.4.5" \
        "ckanext-matolabtheme>=1.1.0" && \
        pip3 install --no-cache-dir -e git+https://github.com/open-data/ckanext-citeproc.git@c1126781d48f9711a6c6f1b9027a157a6e6a0453#egg=ckanext-citeproc  && \
        pip3 install -r https://raw.githubusercontent.com/open-data/ckanext-citeproc/c1126781d48f9711a6c6f1b9027a157a6e6a0453/requirements.txt && \
        pip3 install --no-cache-dir -e git+https://github.com/ckan/ckanext-excelforms.git@42aef2e76a256f484314e9f09ce9596d1d275627#egg=ckanext-excelforms && \
        pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-excelforms/42aef2e76a256f484314e9f09ce9596d1d275627/requirements.txt && \
        pip3 install --no-cache-dir -e git+https://github.com/ckan/ckanext-harvest.git@f40fdbc4f21003d9884dc2b18aa74e93e1b35678#egg=ckanext-harvest && \
        pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-harvest/f40fdbc4f21003d9884dc2b18aa74e93e1b35678/requirements.txt
# ### DCATDE-AP (optional)
# RUN pip3 install -e git+https://github.com/GovDataOfficial/ckanext-dcatde.git#egg=ckanext-dcatde && \
#     pip3 install -r https://raw.githubusercontent.com/GovDataOfficial/ckanext-dcatde/master/base-requirements.txt

WORKDIR $APP_DIR/cls

# List of CLS styles from https://github.com/citation-style-language/styles/ to offer
ENV CLSS="https://github.com/citation-style-language/styles/raw/refs/heads/master/aci-materials-journal.csl \
https://github.com/citation-style-language/styles/raw/refs/heads/master/advanced-engineering-materials.csl \
https://github.com/citation-style-language/styles/raw/refs/heads/master/advanced-science.csl"
# Download files from the array of URLs
RUN echo $CLSS | xargs -n 1 wget -P $APP_DIR/cls/

USER ckan

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done

#create default log location
WORKDIR ${APP_DIR}/logs

WORKDIR ${APP_DIR}

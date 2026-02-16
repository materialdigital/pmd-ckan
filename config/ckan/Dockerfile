FROM ckan/ckan-base:2.11.3

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

RUN buildDeps='locales libpcre3 libpcre3-dev supervisor' \
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

#Install default datastack plugins
# Install the Python packages
RUN pip3 install --no-cache-dir ckanext-csvtocsvw ckanext-csvwmapandtransform ckanext-fuseki ckanext-pdfview ckanext-multiuploadform ckanext-sso ckanext-markdown-view



# Install any extensions needed by your CKAN instance
# - Make sure to add the plugins to CKAN__PLUGINS in the .env file
# - Also make sure all provide all extra configuration options, either by:
#   * Adding them to the .env file (check the ckanext-envvars syntax for env vars), or
#   * Adding extra configuration scripts to /docker-entrypoint.d folder) to update
#      the CKAN config file (ckan.ini) with the `ckan config-tool` command
#
# See README > Extending the base images for more details
### PMD Theme
RUN  pip3 install -e git+https://github.com/Mat-O-Lab/ckanext-matolabtheme.git@pmd#egg=ckanext-matolabtheme && \
    pip3 install -r https://raw.githubusercontent.com/Mat-O-Lab/ckanext-matolabtheme/refs/heads/pmd/requirements.txt


### EXCELFORMS
RUN  pip3 install -e git+https://github.com/ckan/ckanext-excelforms.git#egg=ckanext-excelforms && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-excelforms/main/requirements.txt


### SCHEMING
RUN pip3 install git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming

### HARVEST
RUN pip3 install -e git+https://github.com/ckan/ckanext-harvest.git#egg=ckanext-harvest && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-harvest/master/requirements.txt

# ### DCATDE-AP
# RUN pip3 install -e git+https://github.com/GovDataOfficial/ckanext-dcatde.git#egg=ckanext-dcatde && \
#     pip3 install -r https://raw.githubusercontent.com/GovDataOfficial/ckanext-dcatde/master/base-requirements.txt

#Should be installed by the previous
### DCAT
#ckanext-scheming is needed with dcat
RUN pip3 install -e git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming
RUN pip3 install -e git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat  && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-dcat/master/requirements.txt

### Showcase
#RUN pip3 install ckanext-showcase

### CITEPROC
RUN pip3 install -e git+https://github.com/open-data/ckanext-citeproc.git#egg=ckanext-citeproc  && \
    pip3 install -r https://raw.githubusercontent.com/open-data/ckanext-citeproc/refs/heads/main/requirements.txt

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

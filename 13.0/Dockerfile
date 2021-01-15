FROM odoo:13.0
MAINTAINER Odoo S.A. <info@odoo.com>

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Install Odoo
ENV ODOO_VERSION 13.0+e
ARG ODOO_RELEASE=20201222

# Install Odoo Enterprise that Fictiv uses
USER root
COPY ./odoo_${ODOO_VERSION}.${ODOO_RELEASE}.deb /tmp/odoo_${ODOO_VERSION}.${ODOO_RELEASE}.deb
RUN DEBIAN_FRONTEND=noninteractive \
	&& apt-get update \
	&& dpkg --force-overwrite --force-downgrade -i /tmp/odoo_${ODOO_VERSION}.${ODOO_RELEASE}.deb \
        && apt-get -y install --no-install-recommends \
            python3-twilio \
            python3-boto3 \
            python3-redis \
            python3-sh \
            redis-server \
            sudo \
            vim \
            procps \
 	&& rm -rf /var/lib/apt/lists/* \
 	&& rm -rf /tmp/odoo_${ODOO_VERSION}.${ODOO_RELEASE}.deb
RUN /usr/bin/python3 -m pip install -U wheel
RUN /usr/bin/python3 -m pip install -U easypost
RUN /usr/bin/python3 -m pip install -U gql

# Replace the base image entrypoint.sh with fictiv entrypoint.sh
COPY ./entrypoint.sh /entrypoint.sh

# Replace the base image wait-for-psql.py with fictiv wait-for-psql.py
COPY ./wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Mount /var/lib/odoo to allow restoring filestore and /mnt/extra-addons for users addons
VOLUME ["/var/lib/odoo", "/mnt/extra-addons"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]

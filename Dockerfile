####主要用于给开发模式下的dokcer-compse.ymal使用
####这个redash项目生成的images没问题，发布
#### 在生产环境下直接从云端拉取



#
#FROM python:2-slim
#
#EXPOSE 5000
#
#RUN useradd --create-home redash
#
## Ubuntu packages
#RUN apt-get update && \
#  apt-get install -y curl gnupg && \
#  curl https://deb.nodesource.com/setup_6.x | bash - && \
#  apt-get install -y \
#    build-essential \
#    pwgen \
#    libffi-dev \
#    sudo \
#    git-core \
#    wget \
#    nodejs \
#    # Postgres client
#    libpq-dev \
#    # for SAML
#    xmlsec1 \
#    # Additional packages required for data sources:
#    libssl-dev \
#    default-libmysqlclient-dev \
#    freetds-dev \
#    libsasl2-dev && \
#  apt-get clean && \
#  rm -rf /var/lib/apt/lists/*
#
#WORKDIR /app


# 基本环境 如上
FROM redash/base:latest


# We first copy only the requirements file, to avoid rebuilding on every file
# change.
COPY requirements.txt requirements_dev.txt requirements_all_ds.txt ./
RUN pip install -r requirements.txt -r requirements_dev.txt -r requirements_all_ds.txt

COPY . ./
RUN npm install && npm run build && rm -rf node_modules
RUN chown -R redash /app
USER redash

ENTRYPOINT ["/app/bin/docker-entrypoint"]
CMD ["server"]

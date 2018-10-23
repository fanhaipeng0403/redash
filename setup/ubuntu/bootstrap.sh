#!/bin/bash
#
# This script setups Redash along with supervisor, nginx, PostgreSQL and Redis. It was written to be used on
# Ubuntu 16.04. Technically it can work with other Ubuntu versions, but you might get non compatible versions
# of PostgreSQL, Redis and maybe some other dependencies.
#
# This script is not idempotent and if it stops in the middle, you can't just run it again. You should either
# understand what parts of it to exclude or just start over on a new VM (assuming you're using a VM).

# shell赋值变量

#a = 2
#echo $a
#echo ${a}
#



set -eu

# 项目的配置文件根目录
REDASH_BASE_PATH=/opt/redash


REDASH_BRANCH="${REDASH_BRANCH:-master}" # Default branch/version to master if not specified in REDASH_BRANCH env var

REDASH_VERSION=${REDASH_VERSION-4.0.1.b4038} # Install latest version if not specified in REDASH_VERSION env var

LATEST_URL="https://s3.amazonaws.com/redash-releases/redash.${REDASH_VERSION}.tar.gz"

VERSION_DIR="$REDASH_BASE_PATH/redash.${REDASH_VERSION}"

REDASH_TARBALL=/tmp/redash.tar.gz


# 配置文件下载url
FILES_BASE_URL=https://raw.githubusercontent.com/getredash/redash/${REDASH_BRANCH}/setup/ubuntu/files
#https://raw.githubusercontent.com/getredash/redash/master/setup/ubuntu/files/supervisord.conf

# 在临时目录操作这些命令
cd /tmp/

verify_root() {

#     "$(id -u)"
#    The command id -u prints out your "numeric user ID" (short: UID);
    if [ "$(id -u)" != "0" ]; then

#    “ $()命令替换

#可以把一个命令的标准输出插在命令行中的任何位置。
#在shell中有两个实现方法：反引号“ 和 $()
#

#---------------------
#echo `echo \$HOSTNAME` //反引号实现
#``已经把\转义成了特殊字符 打印出$HOSTNAME的值

#echo $(echo \$HOSTNAME) //$()
# $() \并没有被转义 打印出的是$HOSTNAME

#echo $(echo \\$HOSTNAME)
#可以打印出$HOSTNAME的值

#---------------------

#作者：haorenxwx
#来源：CSDN
#原文：https://blog.csdn.net/haorenxwx/article/details/77934024
#版权声明：本文为博主原创文章，转载请附上博文链接！

    # 判断输入的参数是否为0个
        if [ $# -ne 0 ]; then
#        在shell中，每个进程都和三个系统文件 相关联：标准输入stdin，标准输出stdout、标准错误stderr，三个系统文件的文件描述符分别为0，1、2。所以这里1>&2 的意思就是将标准输出也输出到标准错误当中。
            echo "Failed running with sudo. Exiting." 1>&2
            exit 1
        fi
        echo "This script must be run as root. Trying to run with sudo."

#        $$
#Shell本身的PID（ProcessID）
#        $!
#Shell最后运行的后台Process的PID
#        $?
#最后运行的命令的结束代码（返回值）
#        $-
#使用Set命令设定的Flag一览
#        $*
#所有参数列表。如"$*"用「"」括起来的情况、以"$1 $2 … $n"的形式输出所有参数。
#        $@
#所有参数列表。如"$@"用「"」括起来的情况、以"$1" "$2" … "$n" 的形式输出所有参数。
#        $#
#添加到Shell的参数个数
#        $0
#Shell本身的文件名
#        $1～$n
#添加到Shell的各参数值。$1是第1参数、$2是第2参数…。

    # sudo 执行  此甲苯
        sudo bash "$0" --with-sudo

        exit 0
#        exit（0）：正常运行程序并退出程序；
#        exit（1）：非正常运行导致退出程序
    fi
}

create_redash_user() {
    adduser --system --no-create-home --disabled-login --gecos "" redash
}

install_system_packages() {
    apt-get -y update
    # Base packages
    apt install -y python-pip python-dev nginx curl build-essential pwgen
    # Data sources dependencies:
    apt install -y libffi-dev libssl-dev libmysqlclient-dev libpq-dev freetds-dev libsasl2-dev
    # SAML dependency
    apt install -y xmlsec1
    # Storage servers
    apt install -y postgresql redis-server
    apt install -y supervisor
}

create_directories() {
    mkdir -p $REDASH_BASE_PATH

#    $ 调用变量
    chown redash $REDASH_BASE_PATH

    # Default config file
    if [ ! -f "$REDASH_BASE_PATH/.env" ]; then

# -O 可以放后面？
        sudo -u redash wget "$FILES_BASE_URL/env" -O $REDASH_BASE_PATH/.env
    fi

# 定义变量， $()把一个命令的标准输出赋值给它
#- 在linux系统下,使用pwgen命令创建随机密码,更为简单

    COOKIE_SECRET=$(pwgen -1s 32)


    echo "export REDASH_COOKIE_SECRET=$COOKIE_SECRET" >> $REDASH_BASE_PATH/.env
}

extract_redash_sources() {
#-u username/#uid 不加此参数，代表要以 root 的身份执行指令，而加了此参数，可以以 username 的身份执行指令（#uid 为该 username 的使用者号码

# 下载"$LATEST_URL"的内容，重新命名为 "$REDASH_TARBALL"
    sudo -u redash wget "$LATEST_URL" -O "$REDASH_TARBALL"
    sudo -u redash mkdir "$VERSION_DIR"
    sudo -u redash tar -C "$VERSION_DIR" -xvf "$REDASH_TARBALL"
    ln -nfs "$VERSION_DIR" $REDASH_BASE_PATH/current
    ln -nfs $REDASH_BASE_PATH/.env $REDASH_BASE_PATH/current/.env
}

install_python_packages() {
    pip install --upgrade pip==9.0.3
    # TODO: venv?
    pip install setproctitle # setproctitle is used by Celery for "pretty" process titles
    pip install -r $REDASH_BASE_PATH/current/requirements.txt
    pip install -r $REDASH_BASE_PATH/current/requirements_all_ds.txt
}

create_database() {
    # Create user and database
    # postgres 用户 建表

    sudo -u postgres createuser redash --no-superuser --no-createdb --no-createrole
    sudo -u postgres createdb redash --owner=redash

    cd $REDASH_BASE_PATH/current
    #见表命令

    sudo -u redash bin/run ./manage.py database create_tables
}

setup_supervisor() {
#将下载的文件存放到指定的文件夹下，同时重命名下载的文件，
# 把 "$FILES_BASE_URL/supervisord.conf" 下载到 /etc/supervisor/conf.d/redash.conf

#wget http://www.centos.bz/download?id=1080
#即使下载的文件是zip格式，它仍然以download.php?id=1080命名。
#正确：为了解决这个问题，我们可以使用参数-O来指定一个文件名：

#wget -O wordpress.zip http://www.centos.bz/download.php?id=1080

    wget -O /etc/supervisor/conf.d/redash.conf "$FILES_BASE_URL/supervisord.conf"
    service supervisor restart
}

setup_nginx() {
    rm /etc/nginx/sites-enabled/default
    wget -O /etc/nginx/sites-available/redash "$FILES_BASE_URL/nginx_redash_site"
    ln -nfs /etc/nginx/sites-available/redash /etc/nginx/sites-enabled/redash
    service nginx restart
}

verify_root
install_system_packages
create_redash_user
create_directories
extract_redash_sources
install_python_packages
create_database
setup_supervisor
setup_nginx

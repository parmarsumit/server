#!/usr/bin/env bash
set -e

if [[ "$UID" -ne "0" ]];then
    echo 'You must be root to install Ilot !'
    exit
fi

SERVER_ROOT={{container_path}}

if ! [[ -f "$SERVER_ROOT/conf/dhparam.pem" ]];then
  openssl dhparam -out $SERVER_ROOT/conf/dhparam.pem 2048
fi

if ! [[ -e "/etc/init.d/ilot" ]];then
echo 'Adding /etc/init.d/ilot ...'

cat > '/etc/init.d/ilot' <<EOF
#!/bin/bash
# Copyright (c) 2017 Biodigitals
# All rights reserved.
#
# Author: Nicolas Danjean
#
# /etc/init.d/ilot
#
### BEGIN INIT INFO
# Provides: ilot
# Required-Start: \$local_fs \$network
# Required-Stop: \$local_fs
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Magma Start script
### END INIT INFO


WORK_DIR="{{container_path}}"
SCRIPT="conf/circus.conf"
DAEMON="env/bin/circusd \$WORK_DIR/\$SCRIPT"
USER=ilot

function start () {
    echo -n 'Starting server...'
    su -c "cd \$WORK_DIR;source env/bin/activate;export DJANGO_ENV=production;\$DAEMON &> /dev/null & echo \$!" \$USER
    echo -n 'Started.'

    }

function stop () {
    echo -n 'Stopping server...'
    kill \$(</tmp/circus-ilot.pid)
    echo 'done.'
}

case "\$1" in
    'start')
        start
        ;;
    'stop')
        stop
        ;;
    'reload')
        cd \$WORK_DIR;
        source env/bin/activate;
        env/bin/circusctl --endpoint ipc:///tmp/circus-endpoint-ilot reload
        service nginx reload
        ;;
    *)
        echo 'Usage: /etc/init.d/ilot {start|stop|reload}'
        exit 0
        ;;
esac

exit 0
EOF

# install the script
chmod +x '/etc/init.d/ilot'
update-rc.d ilot defaults &> /dev/null
fi

set +e

# create the lets encrypt certificates
{% for service in services %}

mkdir -p {{service.path}}/www
mkdir -p {{service.path}}/media/CACHE
mkdir -p {{service.path}}/theme
mkdir -p {{service.path}}/build
mkdir -p {{service.path}}/static

# add config to nginx
if ! [[ -e "/etc/nginx/sites-enabled/ilot.conf" ]];then
  ln -sfT $SERVER_ROOT/conf/nginx.conf "/etc/nginx/sites-enabled/ilot.conf"
fi

service nginx reload

if ! [[ -e "/etc/letsencrypt/live/{{service.interface.cname}}/fullchain.pem" ]];then
  certbot certonly --webroot -w {{service.path}}/www -d {{service.interface.cname}}
fi
# update certificates
if [[ -e /etc/letsencrypt/live/{{service.interface.cname}}/privkey.pem ]];then
  cp -f /etc/letsencrypt/live/{{service.interface.cname}}/privkey.pem $SERVER_ROOT/conf/key.{{service.id}}.pem
  cp -f /etc/letsencrypt/live/{{service.interface.cname}}/fullchain.pem $SERVER_ROOT/conf/certificate.{{service.id}}.pem
fi
chmod +r $SERVER_ROOT/conf/key.{{service.id}}.pem
chmod +r $SERVER_ROOT/conf/certificate.{{service.id}}.pem

chown -R ilot:ilot {{service.path}}
{% endfor %}

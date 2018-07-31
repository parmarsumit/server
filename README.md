# Tribute
Alpha Scope

Here are the first guidelines to get it running.


### requirements
git, python3.5

    apt-get install python3-dev python3-pil build-essential

### setup

    cd /path/to/your/workspace
    git clone https://github.com/Tribute-coop/server
    virtualenv --python=python3 ./env
    source env/bin/activate
    pip install -e .
    ilot migrate
    ilot update
    ilot collectstatic
    ilot configure localhost localhost
    ilot serve


You should have access now at https://localhost:9999/

### dev tools

+ truffle for contract compilation
+ webpack for the webapp js

### updating

    git pull
    ilot migrate
    ilot update
    ilot collectstatic


### serving
git, python3.5, nodejs, nginx, postgresql, certbot

You can follow the same steps but define at first `DJANGO_ENV=production`

This will generate the nginx and circus configuration files.

    cd /opt
    git clone https://github.com/Tribute-coop/server /opt/tribute
    cd /srv
    virtualenv --python=python3 /srv/env
    source /srv/env/bin/activate
    pip install -e /opt/tribute
    export DJANGO_ENV=production
    ilot migrate
    ilot update
    ilot collectstatic
    ilot configure localhost alpha.tribute.coop
    ilot serve


To finalize the setup, you need to execute the /srv/update.sh generated script.
It will:
+ install or update the ilot service
+ update the setup with certbot "Let's Encrypt" certificates

If you are done correctly, you can start the service

    service ilot start

### updating

    cd /opt/tribute
    git pull
    export DJANGO_ENV=production
    ilot migrate
    ilot update
    ilot collectstatic
    service ilot reload

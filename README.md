# Tribute
Alpha Scope

Here are the first guidelines to get it running.


### requirements
git, python3.5

    apt-get install python3-dev python3-pil build-essential


python-pil package may be named python-imaging, depends on distribution


### setup

    cd /path/to/your/workspace

    git clone https://github.com/Tribute-coop/server

    virtualenv --python=python3 ./env
    source env/bin/activate
    pip install -e .

    ilot migrate
    # this will update the database models

    ilot update
    # this will load into database the application logic

    ilot collectstatic
    # this will collect the static application files

    mkdir -p media/CACHE
    # a media folder needs to be created manually

    ilot serve
    # and finally serve ...


A default certificate is created to enable using local https.
You should have access now at https://localhost:9999/


### updating

    git pull

    ilot migrate
    ilot update
    ilot collectstatic


### editing actions and messages

You need to create a superuser

    ilot createsuperuser

Then you can access ide at /tools/index.html

To save changes to application.json

    ilot release


### dev tools

+ truffle for contract compilation
+ webpack for the webapp

###

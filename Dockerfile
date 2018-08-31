
FROM ubuntu:latest
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-pil python3-dev build-essential git curl wget && \
    git clone https://github.com/Tribute-coop/server && \
    cd server/ && \
    ln -s /usr/bin/python3 /usr/local/bin/python && \
    pip3 install --upgrade pip && \
    pip install -e . && \
    mkdir -p media/CACHE && \
    ilot migrate && \
    ilot update && \
    ilot collectstatic 
    
WORKDIR /server

CMD ["ilot", "serve" ,"--ip=0.0.0.0", "--port=9999", "--no-ssl" ]
EXPOSE 9999

From ubuntu AS build

COPY . /server
Run apt-get update && apt-get install -y curl
RUN /server/install/setup_bridge.sh /server
Workdir /minecraft_server
Entrypoint ./start_server.sh

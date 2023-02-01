From ubuntu AS build
COPY ./configs/minecraft_server_conf /server/configs/minecraft_server_conf
COPY ./utils /server/utils
COPY ./install /server/install
Run apt update && apt install -y curl
RUN /server/install/setup_bridge.sh /server

From build as server
Workdir /minecraft_server
Entrypoint ./start_server.sh

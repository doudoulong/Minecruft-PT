From ubuntu as devos
Copy ./install /client/install
Run apt-get update && apt-get install -y libpcap-dev wait-for-it
Run /client/install/docker_setup /client

From devos as freshclient
Copy ./ /client
CMD ["0.0.0.0:25565", "--", "/client/minecruft/Minecruft_Main.py", "client", "/client/configs/aes_ecb_key.bin", "0.0.0.0", "25566", "5001", "/client/configs/client_encoder_actions_v12.2.json", "/client/configs/client_decoder_actions_v12.2.json"]

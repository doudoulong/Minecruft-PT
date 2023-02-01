From ubuntu as devos
Copy ./install /proxy/install
Run apt-get update && apt-get install -y libpcap-dev wait-for-it python3 
Run /proxy/install/docker_setup /proxy

From devos as freshproxy 
Copy ./ /proxy
CMD ["0.0.0.0:25565", "--", "/proxy/minecruft/Minecruft_Main.py", "proxy", "/client/configs/aes_ecb_key.bin", "0.0.0.0", "25566", "5001", "/client/configs/proxy_encoder_actions_v12.2.json", "/client/configs/proxy_decoder_actions_v12.2.json"]

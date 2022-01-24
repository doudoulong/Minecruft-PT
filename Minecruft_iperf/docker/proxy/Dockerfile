From ubuntu as devOS
Copy ./configs /proxy/configs
Copy ./install /proxy/install
Run apt update && apt install -y libpcap-dev wait-for-it python3 
Run /proxy/install/docker_setup /proxy

From devOS as freshProxy 
Copy ./ /proxy
CMD ["0.0.0.0:25565", "--", "/proxy/minecruft/Minecruft_Main.py", "proxy", "/client/configs/aes_ecb_key.bin", "0.0.0.0", "25566", "5001", "/client/configs/proxy_encoder_actions_v12.2.json", "/client/configs/proxy_decoder_actions_v12.2.json"]
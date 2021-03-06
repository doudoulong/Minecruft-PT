# Minecruft-PT
A pluggable transport (PT) that tunnels user's traffic through Minecraft video game sessions. We would recommend users refer to "Introduction to Minecruft" for detailed information about Minecruft. The schematic diagram below should give you a general idea as to how Minecruft-PT works.

![image](https://user-images.githubusercontent.com/4751354/168675516-458acaf6-7fd1-4a1e-adc5-11ad2df7f785.png)

<br>
<br>

## Environment
Minecruft-PT has been tested on the following systems:

*Ubuntu Desktop 20.04 LTS 

*Linux Mint "Una" 20.3 LTS (Cinnamon Edition).


## Software Requirements
1. Install *Docker* by running
```bash
$ sudo apt install docker.io -y
```

2. Install *Docker Compose* by running
```bash
$ sudo apt install docker-compose -y
``` 

3. Instally *Iperf3* by running
```bash
$ sudo apt install iperf3 -y
```

## Minecruft-PT Server Installation
1. Clone the repository by running
```
$ cd ~
$ git clone https://github.com/doudoulong/Minecruft-PT.git
```

2. Assign execute permission to scripts by running
```
$ cd ~/Minecruft-PT/Minecruft/
$ chmod +x utils/iptables_prestart
$ chmod +x utils/start_server.sh
$ chmod +x install/setup
$ chmod +x install/docker_setup
$ chmod +x install/setup_bridge.sh
``` 

3. Configure iptables by running
```
$ sudo utils/iptables_prestart
```

4. Start the Minecraft game server docker by running
```
$ cd ~/Minecruft-PT/Minecruft/docker
$ sudo docker-compose -f iperf-test.yml up mserver
```

5. To start the server proxy docker, you need to obtain the Minecraft server docker's IP by running
```
$ sudo docker inspect docker_default | grep -A 5 "mserver" 
```

Replace the IP address in line 19 (172.19.0.2) of file "iperf-test.yml" with the output of the previous command and then save the file.

6. Start the proxy docker by running one of the following commands, depending on the service: 
* Web traffic tunneling
```
$sudo docker-compose -f iperf-test.yml up --build testproxy socks
```

* iPerf traffic tunneling
```
$sudo docker-compose -f iperf-test.yml up --build testproxy iperf
```

* Netcat traffic tunneling
```
$sudo docker-compose -f iperf-test.yml up --build testproxy netcat
```

The Minecruft-PT server should be ready for use.


## Minecruft-PT Client Setup
1. Clone the repository by running
```
$ cd ~
$ git clone https://github.com/doudoulong/Minecruft-PT.git
```

2. Assign execute permission to scripts by running
```
$ cd ~/Minecruft-PT/Minecruft/
$ chmod +x utils/iptables_prestart
$ chmod +x utils/start_server.sh
$ chmod +x install/setup
$ chmod +x install/docker_setup
$ chmod +x install/setup_bridge.sh
``` 

3. Configure iptables by running
```
$ sudo utils/iptables_prestart
```

4. Start the Minecruft client docker.
Replace the IP address in the last line (127.0.0.1) of file "iperf-test.yml" with the IP address of the Minecruft-PT server and then save the file. Open a new terminal and run
```
$ cd ~/Minecruft-PT/Minecruft/docker
$ sudo docker-compose -f iperf-test.yml up --build testclient
```

### Web Traffic Tunneling
Start Firefox, go to 'Settings --> Network Settings --> Mannual proxy configuration' and enter the following 
```
SOCKS HOST: 127.0.0.1
Port: 9001
```
And save. Now your broswer traffic is tunnelled through Minecruft-PT.

### iPerf Traffic Tunning 
```
$sudo docker-compose -f iperf-test.yml up --build testproxy iperf
```

### Netcat Traffic Tunneling
The netcat mode is mainly used for testing or debugging Minecruft-PT. To start the netcat client, open a terminal and run
```
$ netcat 127.0.0.1 9001
```
### Tor Browser Traffic Tunneling
Start the Tor browser, go to 'Settings --> Tor --> Advanced' and enter the following 
![tor](https://user-images.githubusercontent.com/4751354/168845428-52ce8b54-bae6-4bfc-913b-508ca2a79ec5.jpg)


## Minecruft Traffic Monitoring/Parsing
We recommend pakkit (https://github.com/Heath123/pakkit) for Minecruft and Minecraft traffic monitoring. You need Node.js and npm installed to use pakkit. 

pakkit runs as a proxy between the client and game server. The image below shows the user interface of pakkit, where "connect port" is where the real game server is listening on, which is 25565 by default; and "listen port" is the where pakkit connects to.  You need to make sure your Minecraft game client connects to the listen port, NOT connect port. 

![pakkit](https://user-images.githubusercontent.com/4751354/168687111-788b5b2e-b3d0-402b-8d38-3bb3341d34e3.jpg)


## Clean-Shutdown of Minecruft
Since Minecruft heavily adopts docker, a clean-shutdown is important. To gracefully stop and remove all the docker containers, open a terminal and run
```
$ cd ~/Minecruft-PT/Minecruft/docker
$ sudo docker-compose -f iperf-test.yml down
```
This works for both server and client. 

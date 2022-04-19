# Minecruft-PT
A pluggable transport (PT) that tunnels users' traffic through Minecraft video game sessions.


## Environment
Ubuntu Desktop 20.04 LTS (tested on a VM using VirtualBox)
Linux Mint 2


## System Prerequisites
1. To install *Docker*
```bash
$ sudo apt install docker.io -y
```

2. To install *Docker Compose*
```bash
$ sudo apt install docker-compose -y
``` 

3. To install *Python3.9*
```bash
$ sudo apt install python3.9 -y
``` 

4. To instally *Iperf3*
```bash
$ sudo apt install iperf3 -y
```

## Clone the Repo
```
$ mkdir ~
$ git clone https://github.com/doudoulong/Minecruft-PT.git
```

## Minecruft-PT Server Installation
1. Assign execute permission to scripts.
```
$ cd ~/Minecruft-PT/Minecruft/
$ chmod +x utils/iptables_prestart
$ chmod +x utils/start_server.sh
$ chmod +x install/setup
$ chmod +x install/docker_setup
$ chmod +x install/setup_bridge.sh
``` 

2. Configure iptables.
```
$ sudo utils/iptables_prestart
```

3. Start the Minecraft game server docker.

	Open a new terminal and run
```
$ cd ~/Minecruft-PT/Minecruft/docker
$ sudo docker-compose -f iperf-test.yml up mserver
```

4. Start the server proxy docker.

	First, obtain the docker gateway IP. Open a new terminal and run

```
$ sudo docker inspect docker_default | grep "Gateway"
```

	Replace the IP address in line 19 of file "services.yml" with the output and then save the file.
	fadfafaf

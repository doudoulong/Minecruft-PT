# Minecruft-PT
A pluggable transport (PT) that tunnels users' traffic through Minecraft video game sessions.


## Environment
Ubuntu Desktop 20.04 LTS (tested on a VM using VirtualBox)


## System Prerequisites
1. To install *Docker*
```bash
$ sudo apt install docker.io -y
```

2. To install *Docker Compose*
```bash
$ sudo apt install docker-compose -y
``` 

3. To install *Python3*
```bash
$ sudo apt install python3.9 -y
``` 

4. To instally *Iperf3*
```bash
$ sudo apt install iperf3 -y
```

## Clone the Repo
```
$ mkdir ~/minecruft 
$ cd minecruft
$ git clone https://github.com/doudoulong/Minecruft-PT.git
```

## Minecruft-PT Server Installation
1. Set Script Permissions
```
$ cd Minecruft-PT/Minecruft_iperf/

$chmod +x utils/iptables_prestart

$chmod +x utils/start_server.sh

$chmod +x install/setup

$chmod +x install/docker_setup

$chmod +x install/setup_bridge.sh
```
2. Set IPtables
```
$sudo utils/iptables_prestart
```
3. Start Server Docker

Open new Terminal
```
$cd minecruft/Minecruft-PT/Minecruft_iperf/docker

$sudo docker-compose -f iperf-test.yml up mserver
```

4. Start Proxy Docker in Proxy Virtual Machine
```
First find docker gateway ip:
$sudo docker inspect docker_default | grep "Gateway"
There should show an IP address.

Open iperf-test.yml and change Line 18 ip address to that IP just shown and save.

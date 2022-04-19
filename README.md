# Minecruft-PT
A pluggable transport (PT) that tunnels users' traffic through Minecraft video game sessions.


## Environment
Ubuntu Desktop 20.04 LTS (tested on a VM using VirtualBox), Linux Mint 20.03 LTS (tested on a VM using VirtualBox)


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

4. Start the Minecraft game server docker.

Open a new terminal and run
```
$ cd ~/Minecruft-PT/Minecruft/docker
$ sudo docker-compose -f iperf-test.yml up mserver
```

4. Start the server proxy docker.

To obtain the docker gateway IP, open a new terminal and run
```
$ sudo docker inspect docker_default | grep "Gateway"
```

Replace the IP address in line 19 of file "services.yml" with the output of the previous command and then save the file.

5. Start the selected service docker.

Open a new terminal and run one of the following commands depending on the selected service: 
* SOCKS
```
$sudo docker-compose -f iperf-test.yml up --build testproxy socks
```

* iPerf
```
$sudo docker-compose -f iperf-test.yml up --build testproxy iperf
```

  * Netcat
```
$sudo docker-compose -f iperf-test.yml up --build testproxy netcat
```

The Minecruft-PT server should be ready for use.

## Minecruft-PT Client Setup
1. Tunneling Socks Traffic
On client virtual machine, open Firefox(or other browser). Open broswer network settings and find proxy part.
Set manual proxy configuration as follows:

SOCKS HOST: 127.0.0.1
Port: 9001

And save.
Then your broswer traffic is tunneling through Minecruft-PT.

## Tunnel iPerf Traffic
The iPerf mode is mainly used for purpuse of testing or debugging Minecruft-PT throughput. On client virtual machine, open terminal and run:
```
$iperf3 -c 127.0.0.1 -p 9001 -R -n 10K
```
Then iperf is running and going through Minecruft-PT.

## Tunneling Netcat Traffic
The iPerf mode is mainly used for purpuse of testing or debugging Minecruft-PT throughput.

On client virtual machine, open terminal and run:
```
$netcat 127.0.0.1 9001
```
Then the netcat will use Minecruft to tunnel traffic. On proxy virtual machine, the terminal will show the input from client virtual machine terminal.

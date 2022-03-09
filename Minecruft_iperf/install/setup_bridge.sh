#!/bin/bash

if [ $# -ne 1 ] 
then 
    echo "setup_bridge <minecruft_dir>"
    exit
fi
HomeDir=$1
#Setup script for Ubuntu 18.04. Runs bridge setup script, installs 
#and runs minecraft server, and starts the bridge node. 

./setup -s
apt install -y openjdk-8-jre-headless git

#Prevents host from forwarding duplicate network packets to bridged vagrant VM
# sysctl -w net.ipv4.ip_forward=0

mkdir minecraft_server  
cd minecraft_server

curl -o BuildTools.jar https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar 

git config --global --unset core.autocrlf
java -Xmx8G -jar BuildTools.jar --rev 1.12.2

mv spigot*.jar spigot.jar

cp $HomeDir/configs/minecraft_server_conf/eula.txt .
cp $HomeDir/configs/minecraft_server_conf/server.properties .
cp $HomeDir/utils/start_server.sh .

#nohup ./start_server.sh  &

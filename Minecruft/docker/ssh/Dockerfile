From alpine

Run apk add iptables 
Run apk add openssh
Run mkdir /root/.ssh
Run ssh-keygen -f /root/.ssh/id_rsa -N ""
Run cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
Run echo -e "linuxpassword\nlinuxpassword" | passwd
CMD ["/usr/sbin/sshd", "-h", "/root/.ssh/id_rsa"]

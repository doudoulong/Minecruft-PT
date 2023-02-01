From ubuntu AS DL
Run apt-get update && apt-get install wait-for-it

From node
Copy --from=DL /bin/wait-for-it /bin
Run npm install mineflayer 
Entrypoint ["wait-for-it"]

# Currently Working Packet Encodings

## Encoded from Server/Decoded on Client

| Packet Type | Notes |
|:-----------:|:-----:|
| Named Sound Effect | Currently string names are not real sound effect names |
| Spawn Painting | Positions currently are random (that is paintings won't currently spawn near a player), painting names are garbage values|
| Spawn Experience Orb| Orb Positions are random (Won't be near player) |
| Spawn Global Entity| Random positions |
| Block Break Animation | Only last byte is used for encoding | 
| Block Action | None |
| Block Change | None |
| Entity Head Look | None|
| Entity Look | None|
| Resource Pack Send | Two strings sent can allow this packet to send large blocks of data |
| Craft Recipe Response | N/A |
| Remove Entity Effect | N/A |

## Encoded from Client/Decoded on Server 
| Packet Type | Notes |
|:-----------:|:-----:|
|Chat Message | These Messages are echoed from the server to all players |
| Client Settings| |
| Close Window | |
| Player Position And Look | |
| Vehicle Move| |
| Craft Recipe Request| |
| Player Abilities | | 

# Attempted but not working

## Encoded from Server/Decoded on Client

| Packet Type | Notes |
|:-----------:|:-----:|
| Spawn Object | Several of these packets are sent when a user logs in. |  
| Set Slot| Several of these packets are sent when a user logs in. |  
| Plugin Message| Several of these packets are sent when a user logs in. |  
| Chat Message | Achievements and other player messages from the server need to be handled |  
| Entity Status| Consistent packet corruption occured, cause relates to client encodings or player updates from server. |
| Entity Relative Move | Initially worked and then was corrupted by packets from server |
| Entity Look and Relative Move | Initially worked and then was corrupted by packets from server |

## Encoded from Client/Decoded on Server 


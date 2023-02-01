# Developer Notes

## Runtime Logic Flow
Much of the Runtime logic flow of the program can be seen in Minecruft_Main.py. The primary flow is as follows: 

1. Sniff TCP traffic sent to dest_port 
2. Encrypt the queued sniffed traffic
3. Dequeue each encrypted packet, prepend length of packet
4. Encode into Minecraft Action (After bot reaches play state)
5. Decode Minecraft Action on the proxy side
6. Wait until length bytes are decoded and queue as whole TCP packet
7. Decrypt TCP Packet 
8. Inject packet onto proxy's localhost 

Note that this ordering occurs slightly differently from the proxy's perspective. Since the client transmits first, the proxy would run 5-8 first and then 1-4. Note that each one these functions will all need to occur simultaneously.  

## Setup Logic Flow
Before the primary setup flow is started, arguments are parsed (using docopt in Minecruft_Main), encoder/decoder functions are added dyanamically (if defined in json files), and minecraft sessions are started. More detail about the encoder/decoder functions is discussed in the following sections.  

## Adding New Encoder/Decoders 
There are two ways to add encoder/decoder pairs to minecruft: statically or dyanamically. Note that both ways require defining the encoder function on one endpoint (Client or Proxy)       

### Quarry's Packet Handlers 
Quarry already defines functions for receiving every minecraft packet type, and registers events for them when a user overrides these functions. For example, look at the [Minecraft Networking Protocol (for version 1.12.2)](https://wiki.vg/index.php?title=Protocol&oldid=14204) at the use entity packet. If you wanted to print "hello world" every time one of these packets was sent you could overwrite the function:  
```
packet_upstream_use_entity 
```
within the MinecraftProxyEncoder file within the MinecraftProxyBridge class. This would be the resulting code: 
```
packet_upstream_use_entity(self, buff): 
    self.logger.info("hello world")
```
Whenever a packet_EVENTNAME is registered from the minecraft protocol, Quarry will register that function (if EVENTNAME exists in the protocol and quarry's builtin csv listings) and will trigger a callback to the packet function if a minecraft action packet of EVENTNAME is received. This means event handling can be done transparently, and the developer can simply add desired functionality to each handler. If you want to learn more, look at quarry's protocol and dispatcher classes/functions. 

If you also wanted to forward the received packet to the minecraft server, you would also add: 
```
packet_upstream_use_entity(self, buff): 
    self.logger.info("hello world")
    self.upstream.send_packet("use_entity", buff.read())
```
Look into Quarry's documentation about it's buffer class to learn more (it's based on structs in python). Also look into Minecraft's data types that are used. For packets that end with minecraft NBT metadata, put the byte value 255 to signal the end of the metadata, otherwise the packet will be malformed and the minecraft server will not accept it.

### Adding Static/Explict Encoders/Decoders
Quarry's builtin packet handlers are used for defining decoders within Minecruft. There are slight differences between decoders defined in the client (MinecraftClientEncoder) and proxy (MinecraftProxyBridge). A static decoder within the client code should look like this: 
```
var1 = buff.unpack(fmt)
var2 = buff.unpack_varint()
...
self.incoming_decode_buffer.append(var1)
self.incoming_decode_buffer.append(var2)
...
update_incoming_buffer(self, self.downstream_factory.receiving_packet_queue, buff)
```
and a static decoder within the proxy will look something like this (note the additional save/restore functions): 
```
buff.save()

var1 = buff.unpack(fmt)
var2 = buff.unpack_varint()
...
self.incoming_decode_buffer.append(var1)
self.incoming_decode_buffer.append(var2)
...
buff.restore()

self.downstream.send_packet(packet_name, buff.read())
update_incoming_buffer(self, self.downstream_factory.receiving_packet_queue, buff)
```
The encoders for the client and proxy also look slightly different. However, the entry point for handling encoder functions is the encoder() function in both MinecraftClientEncoder and MinecraftProxyBridge. This function is registered to execute every game tick (1/20th second) in the packet_player_position_and_look (client) and  packet_downstream_player_position_and_look (proxy) functions.  A client encoder will look something like this: 

```
#Add more bytes to the buffer if needed (typically this is wrapped in an if statement)
check_buff(self.forwarding_packet_queue, self.outgoing_encode_buffer)

#This used to be get_byte_from_buff(self.outgoing_encode_buffer, num_bytes) 
buff = ByteChopper(self.outgoing_encode_buffer)
consumed_bytes = buff.chop(num_bytes)

#Note that multiple self.packs for different data types will be included in call to send packet depending on the packet event name
self.send_packet('packet_event_name', self.pack(fmt, consumed_bytes[:somerange]), more packing calls...)
```

and a proxy encoder will look something like this: 
```
check_buff(self.forwarding_packet_queue, self.outgoing_encode_buffer)
buff = ByteChopper(self.outgoing_encode_buffer)
consumed_bytes = buff.chop(num_bytes)

#The difference here are the fact that bridges have upstreams (real minecraft server facing) and downstreams (client/bot facing)
self.downstream.send_packet('packet_event_name', self.pack(fmt, consumed_bytes[:somerange]), more packing calls...)
```

Note that adding a new encoder/decoder requires looking at the required data types for that packet in the minecraft protocol wiki. Fortunately, by using a json defined version of the protocol (see [Python Minecraft Data Repository](https://github.com/PrismarineJS/minecraft-data)) encoders and decoders can be defined dynamically. However, defining functions dynamically will only allow packing based off fields and the fields types. A rule description can be added to the dynamic functions to enforce action specific rules, but a module that parses and executes these rules has not yet been implemented. If no specific rule is required, then it is simiplier to define dynamic rules.         

### Dynamic/Implicit 
Instead of defining generic rules for each packet type, the functions in the Dynamic_Method_Loader can load json defined functions into the classes and set up handlers for these functions. See create_decoder_function, create_encoder_function, encode_action, and decode action for more details. Also, review the json files in the configs folder to see how each action is defined by its fields and data types. Note, that new dynamically defined encoder actions will need to be directly called in the encode() function. 

## References
[Minecraft Networking Protocol (for version 1.12.2)](https://wiki.vg/index.php?title=Protocol&oldid=14204)

[Minecraft Bot and Proxy Library](https://github.com/barneygale/quarry/tree/master/quarry/net)

[Quarry Documentation](https://buildmedia.readthedocs.org/media/pdf/quarry/stable/quarry.pdf)

[Minecraft Data Viewing Tool](https://minecraft-data.prismarine.js.org/?d=protocol)

[Python Minecraft Data Repository](https://github.com/PrismarineJS/minecraft-data)

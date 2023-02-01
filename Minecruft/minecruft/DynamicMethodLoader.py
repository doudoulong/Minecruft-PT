#!/usr/bin/python3 
from quarry.net.client import ClientFactory, SpawningClientProtocol
from quarry.types.uuid import UUID
import logging
import os
import json 
import struct 
import random
from Crypto.Cipher import AES
import hashlib
import MinecraftClientEncoder

class ByteChopper(bytearray):
    def chop(self, end):
        tmp = bytearray()
        if len(self) >= (end):
            tmp =  self[:end] 
            self[:] = self[end:] if len(self) > (end) else bytearray()
        return bytes(tmp)

class FakeChopper(bytearray): 
    def chop(self,end): 
        return os.urandom(end)

def pack_bool(packer): 
    def ephem(data): 
        return packer.pack("?", data)
    return ephem

def pack_uuid(packer): 
    def ephem(data):
        """This ignores the data passed into ephem"""
        tmp_data = UUID.random() 
        return packer.pack_uuid(tmp_data)
    return ephem

def pack_vint_bit(packer): 
    def ephem(data):
        #remove this later 
        num_mobs = random.randint(0,1)
        return packer.pack_varint(num_mobs) 
    return ephem

def pack_vint(packer): 
    def ephem(data):
        #remove this later 
        num_mobs = random.randint(30000, 30200)
        return packer.pack_varint(num_mobs) 
    return ephem

def pack_string(packer): 
    def ephem(data):
        """ Data """
        #dlen = len(data) 
        return packer.pack_string(data)
    return ephem
 
def encode_action(self, packer, outgoing_encode_buffer, fmt, name, pack_enabled=True):
    """
    Self expects the type to be a Minecraft Encoder (either Client or Proxy).
    """
    type_dict = {"slot": packer.pack_slot,
                "varint": pack_vint(packer),
                "varint_id": pack_vint(packer), 
                "varint_bit": pack_vint_bit(packer), 
                "?": pack_bool(packer), 
                "uuid": packer.pack_uuid, 
                "position": packer.pack_position, 
                "string": packer.pack_string, 
                "chat": packer.pack_chat}

    size_dict = {"slot": 0,
                "varint": 0,
                "varint_id": 0,
                "varint_bit": 0,
                "?": 0, 
                "uuid": 16, 
                "position": 0, #can be 8, right now send random data
                "string": 75, #This size is purely arbitrary
                "chat": 20,   #This size is purely arbitrary
                "d": 2, 
                "ddd": 9, #Use on xyz locations
                "f": 3}   
    fmt = [f.lower() if (f.lower() in type_dict.keys() and len(f) > 1) else f for f in fmt] 
    #Add rules for size calculation 
    #Add rule checker for specific packet type
    num_bytes_space = sum([size_dict[f] if f in size_dict else struct.calcsize(f) for f in fmt])  
        
    retstr = b""
    #This loop could be problematic
    check_buff(self.forwarding_packet_queue, outgoing_encode_buffer) 

    outlen = len(outgoing_encode_buffer)
    #if name == "player_position": #Fill buffer with random data
    #    outlen = 0 
    #    outgoing_encode_buffer = bytearray(b"".join([os.urandom(num_bytes_space-outlen), outgoing_encode_buffer]))
    #el
    if num_bytes_space > outlen and outlen != 0: 
#        self.logger.warning(outgoing_encode_buffer)
        outgoing_encode_buffer = bytearray(b"".join([outgoing_encode_buffer, os.urandom(num_bytes_space-outlen)]))
#        self.logger.warning(outgoing_encode_buffer)

    outlen = len(outgoing_encode_buffer)
    if outlen: 
    #Update Byte Chopper to chop bits and keep track of bits
        if self.id == 0: 
            consumed_bytes = ByteChopper(outgoing_encode_buffer)
        else: 
            out_cpy = outgoing_encode_buffer.copy()
            consumed_bytes = ByteChopper(out_cpy)
        is_full = True
        buff_packer = []
        for f in fmt:
            if f == "uuid":
                """This one could lead you into trouble if you are referencing uncreated UUIDs"""
                tmp = consumed_bytes.chop(size_dict[f])
                #self.logger.warning(tmp)
                tmp = UUID.from_bytes(bytes(tmp))
                #self.logger.warning("UUID")
                #self.logger.warning(tmp)
                buff_packer.append(type_dict[f](tmp)) 
            elif f == "position":
                x = int.from_bytes(os.urandom(2), "little") >> 6 
                y = int.from_bytes(os.urandom(1), "little") >> 4 # 16-12 
                z = int.from_bytes(os.urandom(2), "little") >> 6 
                buff_packer.append(type_dict[f](x,y,z))
            elif f == "string" or f == "chat":
                tmp = consumed_bytes.chop(size_dict[f]).hex()
                buff_packer.append(type_dict[f](tmp)) 
            elif f in type_dict:
                """These are datatypes that have been ignored for the time being"""
                buff_packer.append(type_dict[f](int.from_bytes(os.urandom(1),"big")))
            else:
                if f == "d": 
                    #Naive Unsophisticated encoding
                    tmp = consumed_bytes.chop(size_dict[f])
                    tmp = tmp + b"\x00\x10\x00\x00\x00?" 
                    #out = struct.pack("d", tmp)
                    buff_packer.append(tmp)
                elif f == "ddd": #Does LSB stego on player's current position
                    """LSB encoding for having things spawn near players"""
                    tmp = consumed_bytes.chop(size_dict[f])
                    x,y,z = self.player.position
                    #self.logger.warning(self.player.position)
                    x = struct.pack(">d",x) #Big endianness here
                    y = struct.pack(">d",y)
                    z = struct.pack(">d",z)  
                    x_lsb = x[:-3] + tmp[0:3]
                    y_lsb = y[:-3]  + tmp[3:6] 
                    z_lsb = z[:-3] + tmp[6:] 
                    if name == "player_position_and_look": 
                        self.player.update_position(struct.unpack(">ddd", x_lsb + y_lsb + z_lsb))
                    buff_packer.append(x_lsb+y_lsb+z_lsb)

                elif f == "f":
                    tmp = consumed_bytes.chop(3)
                    tmp =   b"\x43" + tmp[:] 
                    #out = struct.pack("f", tmp)
                    buff_packer.append(tmp)
                elif f != b"": 
                    tmp = consumed_bytes.chop(struct.calcsize(f))
                    buff_packer.append(packer.pack(f, *struct.unpack(f, tmp)))
                else: 
                    is_full = False
                    break

        #print("packed", buff_packer)
        if is_full: 
            retstr = b"".join(buff_packer)
        #print(retstr)
            outgoing_encode_buffer = outgoing_encode_buffer[num_bytes_space:]

        #self.logger.warning(outgoing_encode_buffer)
    return (outgoing_encode_buffer, retstr) 

def safe_unpack(f, unpacker): 
    tmp = unpacker.unpack(f)
    if not isinstance(tmp, tuple):
        tmp = (tmp, )
    return tmp

def unpack_slot_item(unpacker):
    def ephem(): 
        slot = unpacker.unpack_slot()
        #print(slot["item"])
        #print(slot["item"].to_bytes(1, "little"))
        #return slot["item"].to_bytes(1, "little")
        return b""
    return ephem

def unpack_varint_id_to_bytes(unpacker): 
    def ephem():
        vint = unpacker.unpack_varint() 
        #print(vint)
        #change this later to allow other varint length encodings
        #return vint.to_bytes(1, "little")
        return vint
    return ephem

def unpack_varint_to_bytes(unpacker): 
    def ephem(): 
        vint = unpacker.unpack_varint() 
        #print(vint)
        #change this later to allow other varint length encodings
        #return vint.to_bytes(1, "little")
        return b""
    return ephem

def unpack_bool(unpacker): 
    def ephem(): 
        vint = unpacker.unpack("?") 
        return b""
    return ephem

def unpack_uuid(unpacker): 
    def ephem(): 
        vint = unpacker.unpack_uuid()
        return b""
    return ephem

def unpack_position(unpacker): 
    def ephem(): 
        vint = unpacker.unpack_position()
        return b""
    return ephem

def decode_action(self, unpacker, incoming_decode_buffer, fmt): 
    type_dict = {"slot": unpack_slot_item(unpacker),
                "varint": unpack_varint_to_bytes(unpacker),  
                "varint_id": unpack_varint_id_to_bytes(unpacker),  
                "varint_bit": unpack_varint_to_bytes(unpacker),  
                "?": unpack_bool(unpacker), 
                "uuid": unpack_uuid(unpacker), 
                "position": unpack_position(unpacker)}

    unpacker.save()
    buff_unpacker = []
    fmt = [f.lower() if (f.lower() in type_dict.keys() and len(f) > 1) else f for f in fmt] 
    for f in fmt:
        item = b"" 
        if f == "uuid":
            tmp = unpacker.unpack_uuid()
            #self.logger.warning(tmp)
            item = unpacker.pack_uuid(tmp)
            #self.logger.warning(item)
        elif f == "varint_id":
            tmp = type_dict[f]()
            #self.logger.warn(f"{tmp}")
            if tmp in self.player_vints or tmp < 30000 or tmp > 30200:
                buff_unpacker = []
                break
        elif f == "string":
            tmp = unpacker.unpack_string()
            item = bytes.fromhex(tmp)
        elif f == "chat":
            tmp = unpacker.unpack_chat().to_string()
            if "joined" not in tmp: 
                item = bytes.fromhex(tmp)
            else: 
                break
        elif f == "ddd": 
            for i in range(len(f)): 
                tmp = struct.pack("d", unpacker.unpack("d"))
                for j in range(3): 
                    item += int.to_bytes(tmp[3-1-j],1, "little") #Bytes are flipped due to Endianness
            #self.logger.warning(tmp)
            #self.logger.warning(item)
        elif f == "d": 
            tmp = struct.pack("d", unpacker.unpack("d"))
            item = b"".join([int.to_bytes(tmp[1],1, "little"),int.to_bytes(tmp[0],1,"little")]) #Bytes are flipped due to Endianness 
        elif f == "f": 
            tmp = struct.pack("f", unpacker.unpack("f"))
            for j in range(3):
                item += int.to_bytes(tmp[3-1-j],1,"little")
        elif f in type_dict: 
            item = type_dict[f]()
        else:
            item = struct.pack(f, *safe_unpack(f, unpacker))
        #print("Received", item)
        #self.logger.warning(f)
        #self.logger.warning(item)
        buff_unpacker.append(item)

    unpacker.restore()
    #print(buff_unpacker)
    return (b"".join(buff_unpacker), unpacker)

def create_encoder_function(cl, name, fmt):
    """
    Currently for special minecraft types, we will assume no bytes of data can be packed.  
    """
    def encoder_template_function(self, pack_on=True):
        #print(name)
        sent_data = True
        buff, out = encode_action(self, self.buff_type, self.outgoing_encode_buffer, fmt, name, pack_enabled=pack_on)
        self.outgoing_encode_buffer = buff
        if out != b"":
            #print("Sending", out) 
            self.send_packet(name, out)
        else: 
            sent_data = False
        return sent_data

    setattr(cl, "encode_" + name, encoder_template_function)

def update_incoming_buffer(encoder, encoder_queue, buff):
    """
    """
    #check counter
    blen = 0
    offset = struct.calcsize("H")
    offset += struct.calcsize("<10s")

    if len(encoder.incoming_decode_buffer) >= offset: 
        tmp = struct.unpack_from("H", encoder.incoming_decode_buffer)

        tmp_hash = struct.unpack_from("<10s", encoder.incoming_decode_buffer[2:])[0]
        #encoder.logger.warn(f'{tmp_hash} {hashlib.sha1(tmp[0].to_bytes(4, "little")).digest()[0]}') 
        if tmp_hash == hashlib.sha1(tmp[0].to_bytes(4, 'little')).digest()[:10]:
            #encoder.logger.warn('Made it') 
        #    pass
            blen = tmp[0]*AES.block_size+20
        else:
            #encoder.logger.warn('popping') 
            encoder.incoming_decode_buffer = bytearray()


    excess = bytearray() 
    buff = bytearray(buff)
    encoder.incoming_decode_buffer.extend(buff)
    if len(encoder.incoming_decode_buffer) >= blen+offset and blen != 0: 
        outbuff = encoder.incoming_decode_buffer[offset:blen+offset] 
        #encoder.logger.warning(outbuff)
        encoder_queue.put(outbuff)
        excess = encoder.incoming_decode_buffer[blen+offset:] 
        encoder.incoming_decode_buffer = bytearray() #toss away excess 

def check_buff(fqueue, buff):
    """
    Checks when a buffer or queue is emptied. When a buffer is emptied, that means
    a full TCP packet has been transmitted to the client. When a full TCP packet is transmitted,
    it signals the Minecruft client with an encode_enemy_look packet.
    """
    #logging.warning("Bytes left: " + str(len(buff)))
    if not fqueue.empty() and len(buff) == 0:
        data = fqueue.get()
        if data != None:
            logging.info("Refilling buffer")
            dlen = int((len(data)-20)/AES.block_size) 
            dhash = hashlib.sha1(dlen.to_bytes(4, 'little'))
            prefix = struct.pack("H", dlen) + struct.pack("<10s", dhash.digest())
            tmp = b''.join([prefix, data])
            buff.extend(bytearray(tmp))
    return buff

#Make sure dynamic creation will correctly overload functions
def create_decoder_function(cl, prefix, name, fmt, mode):
    if not(mode.lower() == "client" or mode.lower() == "bridge"): 
        raise ValueError("Mode must be client or bridge")
    elif mode.lower() == "bridge" and not ("upstream_" == prefix or "downstream_" == prefix): 
        raise ValueError("Bridge Mode requires upstream_ or downstream_ in packet handler names")

    def decoder_template_function(self, buff):
        #self.logger.info("decoding " + name)
        if self.id == 0 and self.spawned == True: #Spawned checks if the protocol is in play mode after the server sends a position_and_look packet to the client
            """Only decoders with id 0 can add to the queue"""
            buff, out = decode_action(self, buff, self.incoming_decode_buffer, fmt)
            out = out.read()
            #print(self.incoming_decode_buffer)
            if (prefix == "upstream_"): 
                update_incoming_buffer(self, self.downstream_factory.receiving_packet_queue, buff) 
                self.upstream.send_packet(name, out)
            elif (prefix == "downstream_"): 
                update_incoming_buffer(self, self.downstream_factory.receiving_packet_queue, buff) 
                self.downstream.send_packet(name, out)
            else:
                update_incoming_buffer(self, self.factory.receiving_packet_queue, buff) 
        else: 
            buff.read()
    #print("".join(["packet_", prefix,  name]))
    #if name != "player_position": 
    setattr(cl, "packet_" + prefix  + name, decoder_template_function)

def create_dropper_function(cl, prefix, name, fmt, mode):
    """This function will drop packets of a given type coming from the minecraft server. 
    It is important to use this function so real minecraft packets don't corrupt packet reconstruction"""
    if not(mode.lower() == "client" or mode.lower() == "bridge"): 
        raise ValueError("Mode must be client or bridge")
    elif mode.lower() == "bridge" and not ("upstream_" == prefix or "downstream_" == prefix): 
        raise ValueError("Bridge Mode requires upstream_ or downstream_ in packet handler names")

    print("dropping" + name)
    def decoder_template_function(self, buff):
        self.logger.info("dropping" + name)
        self.logger.info(buff.read())

    setattr(cl, "packet_" + prefix  + name, decoder_template_function)

if __name__ == "__main__":
    #Put this in Minecruft Main later - pass to factory method 
    with open("./src/client_actions_v12.2.json") as f:
        actions = json.load(f)

    #Put this in inits for factory functions
    for action,action_types in actions.items(): 
        pass
        #create_encoder_function(M, action, action_types)
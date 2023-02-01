#!/usr/bin/env python
"""
Python 3 module with core classes for establishing and maintaing
Minecraft Client connections, encoding encrypted byte streams, and
factory class as an interface to build different types of Minecraft
Class Encoders.
"""

from quarry.net.client import ClientFactory, SpawningClientProtocol
from Crypto.Cipher import AES
from DynamicMethodLoader import create_encoder_function, create_decoder_function
from MinecraftPlayerState import MinecraftPlayer
from ActionModel import HMMActionModel 
from quarry.data import packets

class MinecraftClientEncoder(SpawningClientProtocol):
    """
    The MinecraftClient Encoder is a class that represents a Minecraft Client connection and performs the FTE encoding of an encrypted bit stream.
    """
    def __init__(self, factory, remote_addr):
        self.player = MinecraftPlayer()
        self.id = 0 #Needed for clients so they can decode  
        self.packet_done = False
        self.ticks_count = 0
        self.AES_Block_Len = AES.block_size
        self.incoming_buffer_len = 0
        self.outgoing_encode_buffer = bytearray() #
        self.incoming_decode_buffer = bytearray() #
        self.forwarding_packet_queue = factory.forwarding_packet_queue 
        self.player_vints = []
        self.action_model = None

        super(MinecraftClientEncoder, self).__init__(factory, remote_addr)

        #if factory.encoder_weights is not None: 
        #    weights = factory.encoder_weights 
        #    weights = dict([(k, weights[k[7:]]) for k in actions if k[7:] in weights.keys()]) #k[7:] removes the encode_ prefix
        #    self.action_model = WeightedRandomActionModel(actions, self, weights)
        #else:    
         

    def update_player_full(self):
        """
        Sends a player's position to the server every 20 ticks (1 second).
        """
        #self.logger.warn(dir("self"))
        if len(self.outgoing_encode_buffer) > 0 or not self.factory.forwarding_packet_queue.empty():
        #    self.logger.warn("Yeet")
            self.encode_player_position()
        else: 
            self.send_packet("player_position", self.buff_type.pack("ddd?", *self.player.position, True))

#change this to randomly select which packet to send 
    def encode(self):
        """
        Encode packet bytes as minecraft movements. Currently just 
        encodes as creative mode inventory actions, but this can be 
        expanded to other movement types. This is where any new encoder
        functions should be called.
        """
        if self.action_model is not None and self.spawned and (not self.factory.forwarding_packet_queue.empty() or len(self.outgoing_encode_buffer) > 0):
            #self.ticks_count += 1

            #TODO action selector
            self.action_model.next_actions(50)

    def packet_spawn_player(self, buff):
        """This is sent by a player when they come into visible range, 
        Not when they join"""
        self.logger.warning("Player Near")
        buff.save()
        self.player_vints.append(buff.unpack_varint())  
        buff.read() #must read everything off buffer or error occurs
        #buff.restore()
          
    def packet_player_position_and_look(self, buff):
        """
        Receives the inital player position from the server and store the
        player's information for other turns.

        This function was edited from quarry barneygale
        """
        p_pos_look = buff.unpack('dddff')

        # 1.7.x
        if self.protocol_version <= 5:
            p_on_ground = buff.unpack('?')
            self.pos_look = p_pos_look

        # 1.8.x
        else:
            p_flags = buff.unpack('B')

        for i in range(5):
            if p_flags & (1 << i):
                self.pos_look[i] += p_pos_look[i]
            else:
                self.pos_look[i] = p_pos_look[i]

        # 1.9.x
        if self.protocol_version > 47:
            teleport_id = buff.unpack_varint()

        # Send Player Position And Look
        # 1.7.x
        if self.protocol_version <= 5:
            self.send_packet("player_position_and_look", self.buff_type.pack('ddddff?', self.pos_look[0], self.pos_look[1] - 1.62, self.pos_look[1], self.pos_look[2], self.pos_look[3], self.pos_look[4], True))

        # 1.8.x
        elif self.protocol_version <= 47:
            self.send_packet("player_position_and_look", self.buff_type.pack('dddff?', self.pos_look[0], self.pos_look[1], self.pos_look[2], self.pos_look[3], self.pos_look[4], True))

        # 1.9.x
        else:
            self.send_packet("teleport_confirm", self.buff_type.pack_varint(teleport_id))

        self.player.update_position(self.pos_look[:3])
        if not self.spawned:
            self.ticker.interval = 1.0/20
            self.ticker.add_loop(1, self.encode)
            self.ticker.add_loop(20, self.update_player_full)
            self.spawned = True
        
        actions = dict([(i,MinecraftClientEncoder.__dict__[i]) for i in dir(MinecraftClientEncoder) if "encode_" in i])
        hmm_mapping = {}
        for action in actions: 
            self.logger.warn(self.protocol_version) 
            key = (self.protocol_version, 'play', 'upstream', action[7:])
            val = packets.packet_idents[key].to_bytes(1,"little")
            hmm_mapping[val] = action

            #self.logger.warn(action)
            #self.logger.warn(val) 
        self.action_model = HMMActionModel(actions, self, hmm_mapping, self.factory.hmm_file)
       
    def connection_made(self):
        self.transport.setTcpNoDelay(True)
        super().connection_made()

class MinecraftEncoderFactory(ClientFactory):
    """
    Factory for building Client Connections. Also serves as the interface
    for the two packet queues for encoded packets being set between the
    client and server of the Pluggable Transport.
    """
    protocol = MinecraftClientEncoder
    def __init__(self, encoder_actions=None, 
                decoder_actions=None, 
                profile=None,
                f_queue=None,
                r_queue=None,
                encoder_weights=None, 
                hmm_file=None):
        try:
            for action, fmt in encoder_actions.items():
                create_encoder_function(MinecraftClientEncoder, action, fmt)
            
        except ValueError:
            print("Please check your action set json file. No encoder actions supplied.")

        try:
            for action, fmt in decoder_actions.items():
                create_decoder_function(MinecraftClientEncoder, "", action, fmt, "client")
        except ValueError:
            print("Please check your action set json file. No decoder actions supplied.")

        self.forwarding_packet_queue = f_queue
        self.receiving_packet_queue = r_queue

        self.encoder_weights = encoder_weights
        self.hmm_file = hmm_file
        #TODO add dictionary overloading functionality here to add functions to the given protocol 
        super(MinecraftEncoderFactory, self).__init__(profile)

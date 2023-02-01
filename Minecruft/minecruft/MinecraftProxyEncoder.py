#!/usr/bin/python3

import struct
import random
import multiprocessing
from twisted.internet import reactor
from quarry.net.proxy import DownstreamFactory, Upstream, UpstreamFactory, Bridge
from quarry.types import uuid
from Crypto.Cipher import AES
from DynamicMethodLoader import create_decoder_function, create_encoder_function, create_dropper_function
from MinecraftPlayerState import MinecraftPlayer
from ActionModel import HMMActionModel, RandomActionModel, WeightedRandomActionModel
from quarry.data import packets

#Development notes:
#Currently mob spawning is handled by the proxy, but other mob logic is not
#either we allow a real minecraft server to allocate resources, or handle
#all enitity movements and responses on the Proxy.

#Enemy spawning ID currently is hard-coded to 30000. This is unrealistic.
#Each new entity spawning ID would be incremented from the last one. For
#example, a player could be assigned id 10, and then three enemies would be
#assigned 11, 12, and 13.

class UpstreamEncoder(Upstream):
    """
    Inherits from Upstream Class. Represents the Client Connection to the
    Minecraft Server. Contains a buffer <Proxy_bound_buff>  for holding packets
    destined for the Minecruft Client.     
    """
    assigned_enemy = 0
    assigned_id = 0

class UpstreamEncoderFactory(UpstreamFactory):
    """
    Factory class for Upstream encoder for easy instantiation of multiple
    Upstreams for multiple Minecraft PT clients.
    """
    protocol = UpstreamEncoder

#Each Client and Proxy needs to keep track of which enemy is their own.
#Think of this as a operating system problem of sharing limited resources.
class MinecraftProxyBridge(Bridge):
    """
    Class that holds references to both Upstream and Downstream. Waits for
    both client (Upstream) and server (Downstream) connections to be
    established before forwarding packets through the proxy.
    """
    quiet_mode = False
    events_enabled = False
    upstream_factory_class = UpstreamEncoderFactory

    def __init__(self, downstream_factory, downstream):
        self.ticks_count = 0
        self.clients_and_positions = []
        self.player = MinecraftPlayer()
        self.spawned = False
        self.outgoing_encode_buffer = bytearray()
        self.incoming_decode_buffer = bytearray()

        self.old_enc_buff = bytearray()

        #Maybe add a resource allocator later  
        self.mobs_per_client = 200 #Remove?
        self.first_enemy_id = 30000 #Remove?
        self.block_len = AES.block_size
        #Check for this instead of sentinel 
        self.incoming_buffer_len = 0
        self.forwarding_packet_queue = downstream_factory.forwarding_packet_queue
        self.id = downstream_factory.assign_id()
        self.action_model = None

        super().__init__(downstream_factory, downstream)
                #self.logger.warning(actions)

    def encode(self):
        """
        This is the main encode function that encodes packet bytes as
        minecraft movements. 
        """
        if self.action_model is not None and self.spawned and (not self.downstream_factory.forwarding_packet_queue.empty() or len(self.outgoing_encode_buffer) > 0):
            self.action_model.next_actions(500)
            
            #if len(self.outgoing_encode_buffer) > 0:
            #for i in range(100): #hb 1000 #mb 100 #lb = 10 
                #self.encode_resource_pack_send()
            #    self.encode_entity_look()
                #self.encode_entity_relative_move()
            #    self.encode_entity_head_look()
            #    self.encode_spawn_experience_orb()
                #self.encode_remove_entity_effect()
                #for i in range (self.first_enemy_id, self.first_enemy_id + self.mobs_per_client):
                    #self.encode_enemy_head_look(i)
                    #TODO ADD ENCODER FUNCTIONS HERE
            #self.ticks_count += 1
            #if(self.ticks_count > 20): 
            #    self.ticks_count = 0
            #    self.encode_chat_message()
            #self.outgoing_encode_buffer = self.check_buff(self.outgoing_encode_buffer)


    def gen_rand(self, bound):
        """
        Uses os.urandom to generate random integer. 
        """
        rand_gen = random.SystemRandom()
        return rand_gen.randint(0, bound)

    def spawn_mobs(self, player_position):
        """
        Spawn mobs in a random position in a sqaure 255x255 blocks centered
        on the player's starting position.
        This function should not be used if the Minecraft server is meant to 
        generate mobs.
        """
        first_mob_id = self.first_enemy_id
        num_mobs = self.mobs_per_client
        position = player_position

        for i in range(0, num_mobs):
            chosen_client = self.downstream
            x_pos = position[0] + self.gen_rand(100)/1.0 - 50 
            y_pos = position[1]
            z_pos = position[2] + self.gen_rand(100)/1.0 - 50 
            yaw = self.gen_rand(255)
            pitch = 0
            head_pitch = self.gen_rand(255)
            velocity_x = 0
            velocity_y = 0
            velocity_z = 0
            enemy_id = first_mob_id + i
            enemy_type = 50 + self.gen_rand(2)
            meta_data = 255 #signals that no NBT Minecraft metadata exists- must be here
                            #or packet will be malformed. 

            chosen_client.send_packet("spawn_mob",chosen_client.buff_type.pack_varint(enemy_id) + chosen_client.buff_type.pack_uuid(uuid.UUID.random()) + self.downstream.buff_type.pack_varint(enemy_type) + chosen_client.buff_type.pack("dddBBBhhhB", x_pos, y_pos, z_pos, yaw, pitch, head_pitch, velocity_x, velocity_y, velocity_z, meta_data))

        #self.first_enemy_id = self.first_enemy_id + self.mobs_per_client

#--------------------------------------------------------------------
    def send_packet(self, name, buff): 
        """
        This is an overloaded function used by Dynamic Method loader. 
        It is used to maintain consistency with the Minecraft Client Encoder. 
        """
        self.downstream.send_packet(name, buff)

    def packet_upstream_player_position(self, buff):
        buff.save()
        buff.restore()
        self.upstream.send_packet("player_position", buff.read())

    def packet_downstream_entity_head_look(self, buff):
        buff.discard()
    def packet_downstream_entity_relative_move(self, buff):
        buff.discard()
    def packet_downstream_entity_look(self, buff):
        buff.discard()

    #This packet is only sent if the player dies, or if he is joining
    def packet_downstream_player_position_and_look(self, buff):
        buff.save()
        pos = buff.unpack("ddd")
        self.player.update_position(pos)
        self.spawned = True
        self.downstream.ticker.interval = 1.0/1000 #This could be adjusted 
        self.downstream.ticker.add_loop(1, self.encode)
        self.clients_and_positions.append((self.downstream, pos)) #Remove? 
        self.spawn_mobs(pos)
        buff.restore()
        self.downstream.send_packet("player_position_and_look", buff.read())

    def upstream_ready(self):
        #if self.id != 0:
        #    self.logger.warning(self.id) 
        #    self.logger.warning("Bypassing") 
        #    self.enable_fast_forwarding()
        #else: 
        self.enable_forwarding()

    def downstream_ready(self):
        super().downstream_ready()

        actions = dict([(i,MinecraftProxyBridge.__dict__[i]) for i in dir(MinecraftProxyBridge) if "encode_" in i])
        hmm_mapping = {}

        for action in actions: 
            self.logger.warn(self.downstream.protocol_version)
            key = (self.downstream.protocol_version, 'play', 'downstream', action[7:])
            val = packets.packet_idents[key].to_bytes(1,"little")
            hmm_mapping[val] = action

            #self.logger.warn(action)
            #self.logger.warn(val)

        self.action_model = HMMActionModel(actions, self, hmm_mapping, self.downstream_factory.hmm_file) 

    def downstream_disconnected(self, reason=None):
        self.downstream.factory.num_client_encoders = self.downstream.factory.num_client_encoders - 1
        """Each client must release its id"""
        self.downstream_factory.ids[self.id] = -1
        if self.upstream:
            self.upstream.close()

class MinecraftProxyFactory(DownstreamFactory):
    """
    Factory class for easy instantiation of new Bridge connections between
    client and server.
    """
    bridge_class = MinecraftProxyBridge
    client_bound_buff = bytearray()
    num_client_encoders = 0
    num_waiting_encoders = 0
    motd = "Proxy Server"
    forwarding_packet_queue = None

    def __init__(self,  
                 downstream_encoder_actions=None, 
                 upstream_decoder_actions=None,  
                 c_p_queue = None, s_p_queue = None, 
                 encoder_weights=None, hmm_file=None):

        super(MinecraftProxyFactory, self).__init__()
        try:
            """Handles decoding messages from client"""
            for action, fmt in upstream_decoder_actions.items():
                create_decoder_function(MinecraftProxyBridge, "upstream_", action, fmt, "bridge")

            """This changes how the proxy encodes information to be sent to the real server"""
            #for action, fmt in upstream_decoder_actions.items():
            #    create_dropper_function(MinecraftProxyBridge, "downstream_", action, fmt, "bridge")
            #    create_encoder_function(MinecraftProxyBridge, action, fmt)

            """This one will handle which packets are dropped from the server"""
            #for action, fmt in downstream_encoder_actions.items():
            #    create_dropper_function(MinecraftProxyBridge, "downstream_", action, fmt, "bridge")

            """This one controls which packets are encoded and sent to the server"""

            for action, fmt in downstream_encoder_actions.items():
                create_encoder_function(MinecraftProxyBridge, action, fmt)

            self.ids = [] 
        except ValueError:
            print("Please check your action set json files and the actions that you supplied.")

        self.receiving_packet_queue = s_p_queue
        self.forwarding_packet_queue = c_p_queue

        self.encoder_weights = encoder_weights
        self.hmm_file = hmm_file 

    def assign_id(self):
        """
        Each Proxy encoder spwaned by the ProxyEncoder Factory needs an id. Right now id zero is the only proxy that can/send receive as a PT.
        
        TODO Multiclient PT support will need to be added later. 
        """
        num_ids = len(self.ids)
        i = 0
        for id in self.ids: 
            if i != id:
                break 
            i += 1

        if i == len(self.ids): 
           self.ids.append(i) 
        else:
           self.ids[i] = i 
        return i

    def connection_made(self):
        self.transport.setTcpNoDelay(True) #This option is used by most online games including Minecraft (versions 1.8.1+)
        self.num_client_encoders = num_client_encoders + 1
        return super().connection_made()
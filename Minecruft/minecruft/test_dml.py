from DynamicMethodLoader import create_decoder_function, create_encoder_function, decode_action, encode_action
from quarry.types.buffer import Buffer1_14

class TempEncoder(): 
    pass

msg = b"This is a test message. Bears, Beets, Battlestar galatica" 
packer = Buffer1_14()
def test_create_encoder_function():
    create_encoder_function(TempEncoder, "nothing", "h") 
    if not hasattr(TempEncoder, "encode_nothing"): 
        raise AttributeError

def test_encoding_slicing(): 
    ret_val =  encode_action(packer, msg, ["hhh"])
    assert msg[6:] == ret_val[0] 

def test_encoding_shortint(): 
    val =  encode_action(packer, msg, ["hhh"])
    assert val[1] == b"hTsii "

def test_mixed_encoding(): 
    """
    This test assumes that zero will be passed to set slot. It will need to be replaced later"
    """
    val =  encode_action(packer, msg, ["slot", "hhh"])
    assert val[1] == b"\x01\x00\x01\x00hTsii "

def test_create_decoder_function():
    create_decoder_function(TempEncoder, "nothing", "", "h", "client") 
    if not hasattr(TempEncoder, "packet_nothing"): 
        raise AttributeError("Method Name incorrect")

def test_decoding_shortint(): 
    buff = Buffer1_14(b"hTsii ")
    val =  decode_action(buff, bytearray(), ["hhh"])
    assert val[1] == b"This i", "Normal type decode fails"

def test_decoding_mixed_slot(): 
    buff = Buffer1_14(b"\x01\x00\x01\x00hTsii ")
    val =  decode_action(buff, bytearray(), ["slot", "hhh"])
    assert val[1] == b"This i", "Setting slots failing" 

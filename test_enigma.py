import pytest
from components import Rotor, Reflector, Plugboard
from machine import Enigma

''' COMPONENTS '''

# ROTOR
@pytest.fixture
def r2():
    r2 = Rotor('II', 'd')
    r1 = Rotor('I', 'q', r2, None)

    r2.prev_rotor = r1
    return r2

def test_components_rotor_init(r2):
    r1 = r2.prev_rotor
    assert r2.rotor_num == 'II' and r2.notch == 'E' and r2.window == 'D' and r2.offset == 3 and r2.next_rotor is None and r2.prev_rotor is not None and r1.rotor_num == 'I' and r1.notch == 'Q' and r1.window == 'Q'
    with pytest.raises(ValueError): #invalid Rotor number
        Rotor('IV', 'A')

def test_components_rotor_repr(capsys, r2):
    assert str(r2) == 'Window: ' + str(r2.window)
    assert capsys.readouterr().out == 'Wiring: \n' + str(r2.wiring) + '\n'

def test_components_rotor_step(r2):
    r1 = r2.prev_rotor

    r1.step()
    assert r1.window == 'R' and r2.window == 'E'
    r1.step()
    assert r1.window == 'S' and r2.window == 'F'
    r2.step()
    assert r1.window == 'S' and r2.window == 'G'

def test_components_rotor_encode_letter(capsys, r2):
    r1 = r2.prev_rotor

    assert r1.encode_letter(18, False, True) == 'F' #return letter
    assert r1.encode_letter(24, False, False) == 22 #not return letter
    assert r1.encode_letter('g') == r2.encode_letter(11) #G=6, def self.next_rotor.encode(output index, forward)
    
    assert r2.encode_letter(12, False, True, True) == r1.encode_letter(17, False)
    assert capsys.readouterr().out == "Rotor II: input = P, output = U\n"

def test_componenets_rotor_change_setting(r2):
    r1 = r2.prev_rotor
    r2.change_setting('t')
    assert r2.window == 'T' and r2.offset == 19

    r1.change_setting('x')
    assert r1.window == 'X' and r1.offset == 23

#REFLECTOR
@pytest.fixture
def reflector():
    return Reflector()

def test_components_reflector_init(reflector):
    assert reflector.wiring == {'A':'Y', 'B':'R', 'C':'U', 'D':'H', 'E':'Q', 'F':'S', 'G':'L', 'H':'D','I':'P', 'J':'X', 'K':'N', 'L':'G', 'M':'O', 'N':'K', 'O':'M', 'P':'I','Q':'E', 'R':'B', 'S':'F', 'T':'Z', 'U': 'C', 'V':'W', 'W':'V', 'X':'J','Y':'A', 'Z':'T'}

def test_components_reflector_repr(capsys, reflector):
    assert str(reflector) == ''
    assert capsys.readouterr().out == "Reflector wiring: \n" + str(reflector.wiring) + '\n'

#PLUGBOARD
@pytest.fixture
def plugboard():
    return Plugboard([('AB', 'XR')])

def test_components_plugboard_init(plugboard):
    assert plugboard.swaps == {'AB':'XR', 'XR':'AB'}
    p = Plugboard(None)
    assert p.swaps == {}
    p = Plugboard([('TH', 'IS'),('IS', 'MO'),('RE', 'LI'),('KE', 'IT')])
    assert p.swaps == {'TH': 'IS', 'IS': 'MO', 'MO': 'IS', 'RE': 'LI', 'LI': 'RE', 'KE': 'IT', 'IT': 'KE'}

def test_components_plugboard_repr(capsys, plugboard):
    assert str(plugboard) == ''
    assert capsys.readouterr().out == 'Swaps:\n' + str(plugboard.swaps) +'\n'

def test_components_plugboard_print_swaps(plugboard):
    assert plugboard.print_swaps() is None

def test_components_plugboard_update_swaps(capsys, plugboard):
    plugboard.update_swaps([('TH', 'IS'),('ST', 'RI'),('NG', 'IS'),('FA', 'RF'),('AR', 'FA'), ('RT', 'OO'),('LO', 'NG')], True)
    assert capsys.readouterr().out == 'Only a maximum of 6 swaps is allowed.\n'
    assert plugboard.swaps == {}

    plugboard.update_swaps([('TH', 'IS'),('IS', 'MO'),('RE', 'LI'),('KE', 'IT')])
    assert plugboard.swaps == {'TH': 'IS', 'IS': 'MO', 'MO': 'IS', 'RE': 'LI', 'LI': 'RE', 'KE': 'IT', 'IT': 'KE'}

    plugboard.update_swaps(None, True)
    assert plugboard.swaps == {}

'''MACHINE'''

@pytest.fixture
def mach1():
    return Enigma(key = 'UTD', swaps={'TE':'AM', 'AM':'TE'}, rotor_order=['III','I','II'])

@pytest.fixture
def mach2():
    return Enigma()

def test_machine_enigma_init(mach1, mach2):
    assert mach2.key == 'AAA' and mach2.rotor_order == ['I','II','III'] and mach2.reflector is not None and mach2.plugboard is not None and mach2.plugboard.swaps == {}
    assert mach1.key == 'UTD' and mach1.rotor_order == ['III','I','II'] and mach1.reflector is not None and mach1.plugboard is not None and mach1.plugboard.swaps == {'T': 'E', 'E': 'T', 'A': 'M', 'M': 'A'}
    with pytest.raises(ValueError): #invalid key length
        Enigma('A')
        Enigma('AAAA')

def test_machine_enigma_repr(capsys, mach1):
    assert str(mach1) == 'Key: ' + mach1.key
    assert capsys.readouterr().out == 'Keyboard <-> Plugboard <->  Rotor ' + mach1.rotor_order[0] + ' <-> Rotor ' + mach1.rotor_order[1] + ' <-> Rotor ' + mach1.rotor_order[2] + ' <-> Reflector \n'

def test_machine_enigma_encipher(mach1):
    assert mach1.encipher("") == ""
    assert mach1.encipher("         ") == ""
    assert mach1.encipher("Th!s 1s N0t a!!owed") == 'Please provide a string containing only the characters a-zA-Z and spaces.'
    
    assert mach1.encipher("This is allowed") == 'XWMLTHPGMTDNP'
    assert mach1.encipher('EBFVBDTPVIVZJ') == 'XWMLTHPGMTDNP' 
    assert mach1.encipher('lowercase') == 'CNQIFDSUW'
    
def test_machine_enigma_decipher(mach1):
    assert mach1.decipher("") == ""
    assert mach1.decipher("         ") == ""
    assert mach1.decipher("Th!s 1s N0t a!!owed") == 'Please provide a string containing only the characters a-zA-Z and spaces.'
    
    assert mach1.decipher('XWMLTHPGMTDNP') == 'THISISALLOWED'
    assert mach1.decipher('lowercase') == 'ZHJXNRBZS'
    assert mach1.decipher("IGAFFGDFZPXAA") == 'THISISALLOWED'

def test_machine_enigma_encode_decode_letter(mach1):
    assert mach1.encode_decode_letter('!') == mach1.encode_decode_letter('8') == 'Please provide a letter in a-zA-Z.'
    assert mach1.encode_decode_letter('Q') == 'L'
    assert mach1.encode_decode_letter('T') == 'Q' #swap
    assert mach1.encode_decode_letter('M') == 'I' #swap

def test_machine_enigma_set_rotor_position(capsys, mach1):
    assert mach1.set_rotor_position(123) == mach1.set_rotor_position('NO') == None
    assert capsys.readouterr().out == 'Please provide a three letter position key such as AAA.\n' + 'Please provide a three letter position key such as AAA.\n'
    
    assert mach1.set_rotor_position('TUK') is None
    assert mach1.set_rotor_position('POI', True) is None
    assert capsys.readouterr().out == 'Rotor position successfully updated. Now using ' + mach1.key + '.\n'

def test_machine_enigma_set_rotor_order(mach1):
    mach1.set_rotor_order(['II','III','I'])
    
    l = mach1.l_rotor
    m = mach1.m_rotor
    r = mach1.r_rotor

    assert l.rotor_num == 'II' and l.window == mach1.key[0] and l.prev_rotor == m
    assert m.rotor_num == 'III' and m.window == mach1.key[1] and m.next_rotor == l and m.prev_rotor == r
    assert r.rotor_num == 'I' and r.window == mach1.key[2] and r.next_rotor == m

def test_machine_enigma_set_plugs(mach1):
    mach1.set_plugs([('TH', 'AN'),('KS', 'FO'),('RP', 'LA'),('YI', 'NG')], replace=True)
    assert mach1.plugboard.swaps == {'TH': 'AN', 'AN': 'TH', 'KS': 'FO', 'FO': 'KS', 'RP': 'LA', 'LA': 'RP', 'YI': 'NG', 'NG': 'YI'}
    mach1.set_plugs([('TH', 'AT'),('SA', 'LL'),('FO', 'RN'),('OW', 'OK')])
    assert mach1.plugboard.swaps == {'TH': 'AT', 'AN': 'TH', 'KS': 'FO', 'FO': 'RN', 'RP': 'LA', 'LA': 'RP', 'YI': 'NG', 'NG': 'YI', 'AT': 'TH', 'SA': 'LL', 'LL': 'SA', 'RN': 'FO', 'OW': 'OK', 'OK': 'OW'}
  
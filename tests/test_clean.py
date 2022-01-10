# This Python file uses the following encoding: utf-8
import re
from text_cleaner import clean, constants

def test_default_clean():
    assert clean.clean("π námundast í 3.14") == "pí námundast í 3.14"
    assert clean.clean("we convert all 😎 emojis 😎 to .") == "ve konvert all . emojis . to ."
    assert clean.clean("📌 red pin") == ". red pin"
    assert clean.clean("ß Ø") == "ss Ö"
    assert clean.clean("<p> HTML tög </p>") == "p HTML tög p"
    assert clean.clean("raki (e. humidity)") == "raki , e. humidity ,"
    assert clean.clean("123") == "123"

def test_preserve_characters():
    assert clean.clean("π námundast í 3.14", string_to_preserve=['π']) == "π námundast í 3.14"
    assert clean.clean("ß Ø", string_to_preserve=['ß']) == "ß Ö"
    assert clean.clean("🤡😎🔥📌", string_to_preserve=['🤡','😎'], emoji_replacement='') == "🤡😎"
    assert clean.clean("german 🐍: ßßß", preserve_emoji=True) == "german 🐍: ßßß"
    assert clean.clean("a 🧹 is used to play quidditch", clean_emoji=True) == "a 🧹 is used to play kuidditkh"
    assert clean.clean("∫∬∭∮∯∰∱∲∳", string_to_preserve=['∫','∬','∭','∮','∯','∰','∱','∲','∳']) == "∫∬∭∮∯∰∱∲∳"
    assert clean.clean("Zorro notar ekki hanzka", string_to_preserve=['Z']) == "Zorro notar ekki hanska"
    #  characters stored in unicode_maps
    assert clean.clean("gríski stafurinn \u03a4", string_to_preserve=['\u03a4']) == "gríski stafurinn \u03a4"
    assert clean.clean("hebreski stafurinn \u05db", string_to_preserve=['\u05db']) == "hebreski stafurinn \u05db"
    assert clean.clean("pólski stafurinn ł", string_to_preserve=['ł']) == "pólski stafurinn ł"
    # tokens to be preserved
    assert clean.clean("z zz zzz zzzz", string_to_preserve=['zz']) == "s zz sss ssss"
    assert clean.clean("z zz zzz zzzz", string_to_preserve=['zz', 'zzzz']) == "s zz sss zzzz"
    assert clean.clean("Barizt hefur Zorro, margoft án hanzka", string_to_preserve=['Zorro']) == "Barist hefur Zorro, margoft án hanska"
    assert clean.clean("(Zwoozh) er ekki ízlenzkt orð.", string_to_preserve=['Zwoozh']) == ", Zwoozh , er ekki íslenskt orð."
    
def test_clean_punctuation():
    # replace punct set
    assert clean.clean(",.:!?", punct_set=[',','.']) == ",." 

def test_helper_functions():
    # tests both 'get_replacement' and 'should_delete' as well
    assert clean.validate_characters("\u010c", [], False, False).strip() == "Tj" 
    assert clean.validate_characters("\u05dc", [], False, False).strip() == ""
    assert clean.validate_characters("\u03ba", [], False, False).strip() == "kappa" 
    assert clean.validate_characters("×", [], False, False).strip() == ""
    # method tested is subject to change.
    assert clean.clean_foreign_text_occurrence("(e. Hello)") == '<lang xml:lang="en-GB"> Hello </lang> '
    assert clean.clean_foreign_text_occurrence("(e. Hello World)") == '<lang xml:lang="en-GB"> Hello World </lang> '
    assert clean.clean_foreign_text_occurrence("(e. kwartz)") == '<lang xml:lang="en-GB"> kwartz </lang> '
    # tests 'get_ice_alpha_replacement' as well
    assert clean.validate_characters("(\")", [], False, False).strip() == ",  ,  ,"
    assert clean.validate_characters("())(\"", [")", "\""], False, False).strip() == ", )) , \""
    assert clean.validate_characters("cwartz", [], False, False).strip() == "kvarts"
    assert clean.validate_characters("123", [], False, False).strip() == "123"

def test_replace_character():
    ## replacement configurations mutate the state of the cleaner 
    # replace punctuation
    assert clean.clean("hello.", punct_replacement=' world') == "hello world"
    assert clean.clean("..,,.,.,.,", punct_replacement='1') == "1111111111"
    assert clean.clean(".", punct_replacement='\u03ae') == "\u03ae"
    # character replace
    assert clean.clean("aábdð", char_replacement={'a': 'k'}) == "kábdð"
    assert clean.clean("abdð", char_replacement={'ð': 'eéfghi'}) == "kbdeéfghi"
    # replace alphabet
    assert clean.clean("aábdð", alphabet=['a','b','c','d']) == "k bdeéfghi"
    assert clean.clean("abcdefghijklmnopqrstuvwxyz") == "bcd"

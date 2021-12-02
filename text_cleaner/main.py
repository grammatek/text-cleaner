import argparse
import re
import unicode_maps as um
import unicode_normalizer as un
import constants as c
import emoji_dictionary as ed

EMOJI_PATTERN = "\U0001f469|\u2764" # Temporary for testing TODO: Find a list with extensive coverage of emojis    

def update_replacement_dictionary(char_to_replace, replacement):
    """
    Adds the input char_to_replace to the collection of (character replacement) 
    dictionaries, as defined in unicode_maps.
    """
    dict = {}
    for cr in char_to_replace: 
        dict[cr] = replacement

    um.unified_dictionary.update(dict)

def get_ice_alpha_replacement(char):
    if char in um.post_dict_lookup:
        return um.post_dict_lookup[char]
    return ''

def get_replacement(char):
    if char in um.unified_dictionary:
        return um.unified_dictionary[char]

def should_delete(char):
    return char in um.delete_chars_map

def clean_foreign_text_occurrence(token):
    token = token.replace("(e.", "<lang=en>")
    token = token.replace(")", " <lang=en/>")
    return token + ' '

def encode_characters(token):
    """ 
    Validates the unicode encoding of the input text. This involves deleting or substituting both
    characters and symbols, as defined in unicode_maps. 
    """
    for char in token:
        repl = get_replacement(char)
        if repl:
            token = token.replace(char, repl)
        if should_delete(char):
            token = token.replace(char, '')

    return token

def validate_characters(token, char_to_preserve):
    """
    Checks each character of the input word (token) to see if it matches any predefined character, as defined
    in constants or the second input 'char_to_preserve'.
    """
    for _, char in enumerate(token):
        if char in char_to_preserve: # skip cleaning of char if to be preserved  
            continue
        elif char.isdigit(): 
            continue
        elif char.lower() not in c.CHARACTER_ALPHABET and c.PUNCTUATION_MARKS: 
            replacement = get_ice_alpha_replacement(char)
            if replacement:
                token = token.replace(char, replacement)
            else: 
                char = ''

    return token + ' '

def split_into_tokens(text):
    """
    Splits the input text at whitespaces into tokens. Exception is made within parenthesis to 
    simplify the cleaning process.
    """
    # he following regex demarks a string within parentheses (opening and closing parenthesis) 
    return re.split("\s(?![^(]*\))", text)

def clean(
    text,
    char_to_preserve=[],
    char_to_replace={},
    alphabet=[],
    punct_set=[],
    clean_emoji=True,
    clean_punct=False,
    clean_audiobook=False,
    replace_emoji_with='',
    replace_punct_with='',
):

    """
    Process (clean) the raw input text for NLP (Natural Language Processing) by removing 
    unhelpful and unusable data, as well as reducing noise.
    
    Text cleaning is task specific so multiple configurations are available.
    Args:
        text                : raw text for cleaning                       
        char_to_preserve    : list of char types forbidden to strip or convert
        char_to_replace     : dictionary of characters to convert     
        alphabet            : list of char that don't need converting     
        punct_set           : list of punctuation marks set to preserve
        clean_emoji         : if True, convert emojis to the value of "replace_emoji_with"
        clean_punct         : if True, convert punctuations to the value of "replace_punct_with
        replace_emoji_with  : str to replace emojis with        
        replace_punct_with  : str to replace punctuations with

    Returns:
        str: cleaned text based on function args
    """

    text = split_into_tokens(text)
    
    if char_to_replace:
        um.unified_dictionary.update(char_to_replace)
    if punct_set:
        un.PUNCT_SET = punct_set
    if alphabet:
        un.CHAR_SET = alphabet
    if replace_punct_with:
        update_replacement_dictionary(punct_set, replace_punct_with)
    if clean_emoji:
        ed.emoji_dict
    if clean_punct:
        print("clean punctuation")

    cleaned_text = ''
    for token in text:
        if token in c.HTML_TAGS or token in c.HTML_CLOSING_TAGS and not clean_audiobook:
            token = ''
        elif token in c.HTML_CLOSING_TAGS and clean_audiobook:
            cleaned_text += '. ' # default value for closing html tags
        elif token.startswith('(e.') and clean_audiobook: # this only covers english text and assumes it's prefixed be "(e."
            token = clean_foreign_text_occurrence(token)
        else:
            token = encode_characters(token) 
            cleaned_text += validate_characters(token, char_to_preserve)

    return cleaned_text

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="a text to be cleaned")
    args = parser.parse_args()
    
    return args.text

def main():
    text = parse_arguments()
    
    print('the cleaner:', clean(text, 
                char_to_preserve=['w'],
                #char_to_replace={'(': 'svigi opnast ', ')': ' svigi lokast'},
                #alphabet=['a','b'],
                #punct_set=[',','.'],
                clean_emoji=False,
                #clean_punct=False,
                clean_audiobook=False,
                #replace_emoji_with="<emoji>",
                #replace_punct_with="<punctuation>",
                ))

if __name__ == '__main__':
    main()
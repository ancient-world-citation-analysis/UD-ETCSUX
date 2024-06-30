import re
import itertools
import json

dictionary = json.load(open("compound_verb_dic.json"))

def remove_brackets(sentence):
    parts = []
    temp = ''
    inside_parentheses = False
    for char in sentence:
        if char == '(':
            if temp:
                parts.append([temp])
                temp = ''
            inside_parentheses = True
        elif char == ')':
            if temp:
                parts.append([temp, ''])
                temp = ''
            inside_parentheses = False
        else:
            temp += char
    if temp:
        parts.append([temp])

    # Generate all combinations of the parts
    combinations = list(itertools.product(*parts))
    # Join parts and strip extra spaces to form sentences
    result = [''.join(part).replace("  ", " ").strip() for part in combinations]
    return result

def devide_options(text):
    results = []
    word_list = text.split(" ")
    for idx, word in enumerate(word_list):
        if "/" in word:
            parts = split_a_word(word)
            if len(results) == 0:
                results = parts
            else:
                results = results * len(parts)
                for idx, i in enumerate(results):
                    results[idx] = results[idx] + " " + parts[idx % len(parts)]
        else:
            if len(results) == 0:
                results = [word]
            else:
                for idx, i in enumerate(results):
                    results[idx] = results[idx] + " " + word
    return results

def split_a_word(word):
    parts = word.split("/")
    head = parts[0]
    results = [head]
    replace_length = 1000
    for part in parts[1:]:
        if len(part) < replace_length:
            replace_length = len(part)
    for part in parts[1:]:
        temp = head[:-replace_length] + part
        results.append(temp)
    return results

import re

def replace_cun_index(match):
    # Mapping for superscripts
    superscripts = str.maketrans("0123456789abcdefghijklmnopqrstuvwxyz", "⁰¹²³⁴⁵⁶⁷⁸⁹ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ")
    index_text = match.group(1)
    return index_text.translate(superscripts)

def replace_cun_desc(match):
    cun_desc_dict = {
        "Poss.": "Possessive",
        "Nomen": "Noun"
    }
    desc_text = match.group(1)
    return cun_desc_dict.get(desc_text, desc_text)

def replace_italic(match):
    italic_dict = {
        "tenû": "alternative",
        "t.": "suffix"
    }
    italic_text = match.group(1)
    return italic_dict.get(italic_text, italic_text)

def convert_text(text):
    # Replace cun_index with superscript conversion
    text = re.sub(r"<span class='cun_index'>(.*?)</span>", replace_cun_index, text)

    # Replace cun_desc
    text = re.sub(r"<span class='cun_desc'>(.*?)</span>", replace_cun_desc, text)

    # Replace italic
    text = re.sub(r"<span class='italic'>(.*?)</span>", replace_italic, text)

    # Remove any remaining HTML tags
    text = re.sub(r"<[^>]*>", "", text)

    return text


def possible_verbs(sumerian_text):
    """
    Break down sumerian text into several possiable texts.
    """
    words = list(sumerian_text.split(" "))
    result = []
    counter = 0
    for word in words:
        if counter > 0 and "-" in word:
            possible_words = list(word.split("-"))
            previous_word = words[counter-1]
            for possible in possible_words:
                result.append("{} {}".format(previous_word, possible))
        counter += 1
    return result

def create_regex_pattern(key):
    # Split the key into tokens
    tokens = key.split()
    # Build a regex pattern that allows for extra characters between the tokens
    # '\S*' allows for any number of non-space characters to appear between tokens
    pattern = r'\b' + r'[\s\S]*'.join(re.escape(token) for token in tokens) + r'\b'
    return pattern

def find_sumerian_phrases(text):
    # Normalize input text
    text = text.lower()
    found_phrases = {}
    
    for key, translation in dictionary.items():
        pattern = create_regex_pattern(key)
        if re.search(pattern, text):
            found_phrases[key] = translation
    return found_phrases
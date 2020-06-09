import textwrap

def pad_text_with_spaces(text,padded_length):
    """
    Returns a string of length exactly length, padding left and right with an equal number of spaces.
    """
    
    padding=int(max(0,padded_length-len(text))/2)
    result=" "*padding+text+" "*padding
    if len(result)<padded_length:
        result+=" "
    return result[:padded_length]

def get_text_lines_within_width(text,width,center_if_one_line=True, center_all=False):
    "return list of strings within size width, intelligently"
    
    lines=[]
    for paragraph in text.split("\n"):
        lines+=textwrap.wrap(paragraph,width)
    
    if center_if_one_line and len(lines)==1:
        lines[0]=pad_text_with_spaces(lines[0],width)
    
    if center_all:
        lines=[pad_text_with_spaces(line,width) for line in lines]
    
    return lines
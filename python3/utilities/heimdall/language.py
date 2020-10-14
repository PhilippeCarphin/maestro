import os
from constants.heimdall import DEFAULT_LANGUAGE, LANGUAGES

def get_language_from_environment(text=""):
    """
    Get language like 'en' or 'fr' from text like 'en_CA.UTF-8'.
    
    If lang_var is not provided, get it from the LANG environment variable.
    
    If something fails return DEFAULT_LANGUAGE.
    """
    if not text:
        text=os.environ.get("LANG","")
    
    language=text[:2].lower()
    if language not in LANGUAGES:
        return DEFAULT_LANGUAGE
    return language
import re

"""
Matches fname lines using the old uspmadt system. See unit tests for examples.
"""
USPMADT_FNAME_REGEX=re.compile(r".*(fname|\${?(?:fname|FNAME)}?).*(?:-r\s+(\${?(?:\w*run\w*|\w*RUN\w*)}?)).*")

"""
Matches fgen lines using the old uspmadt system. See unit tests for examples.
"""
USPMADT_FGEN_REGEX=re.compile(r".*(fgen\+|\${?(?:fgen|FGEN)}?).*(?:-t\s+(\${?(?:\w*run\w*|\w*RUN\w*)}?)).*")

"""
Matches dtstmp lines using the old uspmadt system. See unit tests for examples.
"""
USPMADT_DTSTMP_REGEX=re.compile(r".*(dtstmp|\${?(?:dtstmp|DTSTMP)}?).*(?:-r\s+(\${?(?:\w*run\w*|\w*RUN\w*)}?)).*")


def get_uspmadt_lines(text):
    """
    Returns a list of all lines which seem to be using the deprecated uspmadt system.
    
    See also:
        * Unit tests in this project.
        * https://gitlab.science.gc.ca/CMOI-Service-Desk/General/issues/5
    """
    
    results=list(USPMADT_FNAME_REGEX.finditer(text))
    results+=list(USPMADT_FGEN_REGEX.finditer(text))
    results+=list(USPMADT_DTSTMP_REGEX.finditer(text))
    results=[r.group(0) for r in results]
    return results
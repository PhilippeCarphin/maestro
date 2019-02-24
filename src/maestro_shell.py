from prompt_toolkit.completion import Completion, Completer, FuzzyCompleter, FuzzyWordCompleter, WordCompleter, PathCompleter
from prompt_toolkit.styles import style_from_pygments_cls, Style
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import FileHistory
import os


def prompt_exp_home():
    return prompt('Enter exp home> ',
                  completer=PathCompleter(only_directories=True
                                          ),
           history=FileHistory(os.path.expanduser('~/.mshell_history'))
           )



def make_maestro_shell_session(exp_home):

    maestro_completer = FuzzyWordCompleter(get_node_paths(), WORD=True)
    # maestro_completer = PathCompleter(WordCompleter(bunch_of_paths))

    prompt_style = Style.from_dict({
        'prompt': '#00aa00'
    })
    prompt_string = [
        ('class:username', 'FocusTree> ')
    ]
    prompt_sesh = PromptSession(
        completer=maestro_completer,
        )
    return prompt_sesh

def prompt_node(sesh):
    prompt_string = [
        ('class:username', 'FocusTree> ')
    ]
    return sesh.prompt(prompt_string)

def verify_tsvinfo_available():
    # TODO
    pass

def get_node_paths():
    # run tsvinfo -e {} -d {} --readable-output {}.format(exp_home, make_maestro_datestamp(), tsvfile)

    # Convert to just paths
    # run grep '^[^ ]' > {}".format(paths_list)

    # return f.readlines()
    bunch_of_paths = None
    with open('node_paths.txt') as f:
        return [l.strip() for l in f.readlines()]

if __name__ == "__main__":
    exp_home = prompt_exp_home()
    sesh = make_maestro_shell_session(exp_home)
    prompt_node(sesh)

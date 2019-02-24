import subprocess
from prompt_toolkit.completion import Completion, Completer, FuzzyCompleter, FuzzyWordCompleter, WordCompleter, PathCompleter
from prompt_toolkit.styles import style_from_pygments_cls, Style
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import FileHistory
import os
import re

class MaestroShellError(Exception):
    pass


def prompt_exp_home():
    return prompt('Enter exp home> ',
                  completer=PathCompleter(only_directories=True
                                          ),
           history=FileHistory(os.path.expanduser('~/.mshell_history'))
           )



def make_maestro_shell_session(exp_home, datestamp):

    maestro_completer = FuzzyWordCompleter(get_node_paths(exp_home, datestamp), WORD=True)
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

def get_node_paths(exp_home, datestamp):
    tsvfile = '.tsvtmp'
    maestro_dir = os.path.join(os.path.dirname(__file__), '..')
    src_dir = os.path.join(maestro_dir, 'src')
    tsvinfo = os.path.join(src_dir, 'tsvinfo.out')
    subprocess.call(['make', '-C', src_dir])
    cmd = '{} -e {} -d {} --readable-output {}'.format(tsvinfo, exp_home, datestamp, tsvfile)
    print(cmd)
    retval = subprocess.call(cmd.split())

    if retval != 0:
        raise MaestroShellError('tsvinfo has failed to execute for experiment {}'.format(exp_home))
    # Convert to just paths

    node_re_str = r'^[^ ].*'
    node_re = re.compile(node_re_str)

    paths = []
    with open(tsvfile) as f:
        for l in f.readlines():
            if l and not l.startswith(' ') and not l.startswith('\t') and l != '\n':
                paths.append(l)

    return [p.strip() for p in paths]

if __name__ == "__main__":
    try:
        datestamp = '20190223102400'
        exp_home = prompt_exp_home()
        #TODO else if exists $PWD/EntryModule, use that as exp_home
        #TODO else if exists env:SEQ_EXP_HOME use that
        sesh = make_maestro_shell_session(exp_home, datestamp)
        prompt_node(sesh)
    except EOFError:
        pass
    except KeyboardInterrupt:
        pass
    except MaestroShellError as e:
        print("MaestroShellError : " + str(e))


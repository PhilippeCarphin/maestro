import unittest
import curses

from mflow import TuiManager
from maestro_experiment import MaestroExperiment
from utilities import get_console_dimensions
from utilities.mflow import get_mflow_config
from tests.path import TURTLE_ME_PATH, BIG_LOOP_ME_PATH, G1_MINI_ME_PATH

"""
Tests for the TuiManager class.
This launches the actual text user interface and simulates submitting user input.
"""


class TestTuiManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = 5000

    def test_simple_flow_navigation(self):
        datestamp = "2020040100"
        me = MaestroExperiment(TURTLE_ME_PATH, datestamp=datestamp)

        for is_tree_nav in (False, True):
            tui_config = get_test_config(tree_nav=is_tree_nav)
            "start tui and quit"
            keys = [curses.KEY_UP]
            tui = TuiManager(me,
                             tui_config=tui_config,
                             debug_keypresses=keys)
            tui.start()

            "test trying to navigate past all four borders"
            keys = []
            directions = (curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN)
            dimension = sum(get_console_dimensions())
            for direction in directions:
                keys += [direction for i in range(dimension+2)]
            tui = TuiManager(me,
                             tui_config=tui_config,
                             debug_keypresses=keys)
            tui.start()

    def test_tree_jump(self):
        """
        nodes are close, but on very different branches
        press up should jump to that close node
        """

        r = curses.KEY_RIGHT
        d = curses.KEY_DOWN
        u = curses.KEY_UP
        keys = [r, d, d, r, r, r, u]
        me = MaestroExperiment(G1_MINI_ME_PATH)
        me.set_snapshot("2020040100")

        tui = TuiManager(me, debug_keypresses=keys)
        tui.start()

        xy = tui.cursor["xy"]
        result = tui.text_flow.get_node_path_from_xy(xy[0], xy[1])
        expected = "main/assimcycle/anlpost/anlpres"
        self.assertEqual(result, expected, msg=str(xy))

    def test_node_select_popup(self):
        datestamp = "2020040100"
        me = MaestroExperiment(TURTLE_ME_PATH, datestamp=datestamp)
        xy = (1, 1)

        "select a node, scroll around the popup options"
        keys = [ord("\n")]+[curses.KEY_UP]*20+[ord("c")]
        tui = TuiManager(me,
                         tui_config=get_test_config(),
                         cursor_start_xy=xy,
                         debug_keypresses=keys)
        tui.start()

        "verify that xy has node so test makes sense"
        self.assertTrue(tui.text_flow.get_node_path_from_xy(*xy))

    def test_many_popup_options(self):
        datestamp = "2020040100"
        me = MaestroExperiment(BIG_LOOP_ME_PATH, datestamp=datestamp)

        xy = (20, 1)

        "press enter, scroll around the popup options, cancel and quit"
        keys = [ord("\n"), curses.KEY_DOWN, ord("\n")]+[curses.KEY_DOWN]*200+[ord("c")]
        tui = TuiManager(me,
                         tui_config=get_test_config(),
                         cursor_start_xy=xy,
                         debug_keypresses=keys)
        tui.start()

        "verify that xy has node so test makes sense"
        result = tui.text_flow.get_node_path_from_xy(*xy)
        self.assertEqual("turtle/BigLoop", result)

    def test_okay_popup(self):
        datestamp = "2020040100"
        me = MaestroExperiment(TURTLE_ME_PATH, datestamp=datestamp)

        messages = ["this is a short message",
                    "this is a long message "*10,
                    "this is a "+"message-that-is-difficult-to-breakup-"*10]

        tui = TuiManager(me,
                         tui_config=get_test_config(),
                         debug_okay_messages=messages)
        tui.start()

    def test_maestro_commands(self):
        "submit and force status commands are constructed with proper arguments"
        datestamp = "2020040100"
        me = MaestroExperiment(TURTLE_ME_PATH, datestamp=datestamp)
        tui = TuiManager(me,
                         tui_config=get_test_config())
        node_path1 = "turtle/TurtlePower"
        node_path2 = "turtle/TurtlePower/BossaNova"
        node_path3 = "turtle/TurtlePower/BossaNova/donatello"

        "no selected indexes constructs cmd for default 0,0"
        choices = tui.get_sequencer_choices(node_path2)
        label = "Submit: continue, no dependency, loop member (0)"
        choice = [c for c in choices if c["label"] == label]
        self.assertTrue(choice)
        result = choice[0]["cmd"]
        expected = "maestro -e %s -d %s -n %s -s submit -f continue -i -l TurtlePower=0,BossaNova=0"
        expected = expected % (TURTLE_ME_PATH,
                               me.long_datestamp,
                               node_path2)
        self.assertEqual(result, expected)

        "select indexes and verify that it worked"
        tf = tui.text_flow
        tf.set_node_selected_loop_index(node_path1, 1)
        tf.set_node_selected_loop_index(node_path2, 3)
        expected = {"TurtlePower": 1, "BossaNova": 3}
        result = tf.get_loop_index_selection("turtle/TurtlePower/BossaNova")
        self.assertEqual(result, expected)

        "loop with selected indexes, member"
        choices = tui.get_sequencer_choices(node_path2)
        label = "Submit: continue, no dependency, loop member (3)"
        choice = [c for c in choices if c["label"] == label]
        result = choice[0]["cmd"]
        expected = "maestro -e %s -d %s -n %s -s submit -f continue -i -l TurtlePower=1,BossaNova=3"
        expected = expected % (TURTLE_ME_PATH,
                               me.long_datestamp,
                               node_path2)
        self.assertEqual(result, expected)

        "loop with selected indexes, entire loop"
        choices = tui.get_sequencer_choices(node_path2)
        label = "Submit: continue, entire loop"
        choice = [c for c in choices if c["label"] == label]
        result = choice[0]["cmd"]
        expected = "maestro -e %s -d %s -n %s -s submit -f continue -l TurtlePower=1"
        expected = expected % (TURTLE_ME_PATH,
                               me.long_datestamp,
                               node_path2)
        self.assertEqual(result, expected)

        "loop1/loop2/task1 simple submit includes two loop indexes"
        choices = tui.get_sequencer_choices(node_path3)
        label = "Submit: continue"
        choice = [c for c in choices if c["label"] == label]
        result = choice[0]["cmd"]
        expected = "maestro -e %s -d %s -n %s -s submit -f continue -l TurtlePower=1,BossaNova=3"
        expected = expected % (TURTLE_ME_PATH,
                               me.long_datestamp,
                               node_path3)
        self.assertEqual(result, expected)


def get_test_config(tree_nav=False):
    c = get_mflow_config()
    c["KEYBOARD_NAVIGATION"] = "tree" if tree_nav else "coordinate"
    return c

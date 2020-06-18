import unittest
from lxml import etree

from utilities import pretty
from maestro.utilities.xml import get_combined_flow_from_text_list, find_all_flow_xml_for_experiment, \
 get_submits_from_flow_element, get_flow_children_from_flow_element, get_paths_from_element, \
 get_combined_flow_for_experiment_path, get_flow_branch_from_flow_element, get_node_path_from_flow_element, get_combined_flow_from_paths, \
has_empty_inner_modules, get_empty_inner_modules, is_empty_module, element_has_node_children , replace_module_name
from tests.path import BIG_ME_PATH

XML1="""
<MODULE name="module1">
    <SUBMITS sub_name="family1"/>
    <FAMILY name="family1">
            <SUBMITS sub_name="a"/>
            <SUBMITS sub_name="b"/>
            <SUBMITS sub_name="c"/>
            <SUBMITS sub_name="family2"/>
            <TASK name="a"/>
            <TASK name="b"/>
            <FAMILY name="family2">
                <SUBMITS sub_name="f"/>
                <TASK name="f"/>
                <NPASS_TASK name="g"/>
            </FAMILY>
            <NPASS_TASK name="e"/>
            <TASK name="c"/>
    </FAMILY>
</MODULE>
        """.strip()

class TestMaestroXML(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.maxDiff=5000
                
    def test_switch_children(self):
        xml1="""
<MODULE name="module1">
    <SUBMITS sub_name="switch1"/>
    <SWITCH name="switch1" type="day_of_week">
        <SWITCH_ITEM name="item1">
            <SUBMITS sub_name="task1"/>
            <TASK name="task1"/>
        </SWITCH_ITEM>
        <SWITCH_ITEM name="item2">
            <SUBMITS sub_name="task2"/>
            <TASK name="task2"/>
        </SWITCH_ITEM>
    </SWITCH>
</MODULE>
"""
        module1=etree.fromstring(xml1)
        switch1=module1[1]
        item1=switch1[0]
        
        result=get_node_path_from_flow_element(module1)
        self.assertEqual(result,"module1")
        
        result=get_node_path_from_flow_element(switch1)
        self.assertEqual(result,"module1/switch1")
        
        result=get_node_path_from_flow_element(item1)
        self.assertEqual(result,"module1/switch1/item1")
        
        result=get_flow_children_from_flow_element(module1)
        expected=["module1/switch1"]
        self.assertEqual(result,expected)
        
        result=get_flow_children_from_flow_element(switch1)
        expected=["module1/switch1/item1",
                  "module1/switch1/item2"]
        self.assertEqual(result,expected)
        
        result=get_flow_children_from_flow_element(item1)
        expected=["module1/switch1/item1/task1"]
        self.assertEqual(result,expected)
        
    def test_empty(self):
        
        xml1="""
<MODULE name="module1">
    <TASK name="task1">
        <MODULE name="module2"/>
    </TASK>
</MODULE>
        """
        
        xml2="""
<MODULE name="module3">
    <TASK name="task1">
        <MODULE name="module4">
            <DEPENDS_ON dep_name="/enkf_mod/anal_mod" status="end" type="node"/>
        </MODULE>
    </TASK>
</MODULE>
        """
        
        xml3="""
<MODULE name="module5">
    <TASK name="task1">
        <MODULE name="module6">
            <TASK name="task2"/>
        </MODULE>
    </TASK>
</MODULE>
        """
        
        module1=etree.fromstring(xml1)
        module2=module1[0][0]
        module3=etree.fromstring(xml2)
        module4=module3[0][0]
        module5=etree.fromstring(xml3)
        module6=module5[0][0]

        self.assertTrue(has_empty_inner_modules(module1))
        self.assertFalse(has_empty_inner_modules(module2))
        self.assertTrue(has_empty_inner_modules(module3))
        self.assertFalse(has_empty_inner_modules(module4))
        self.assertFalse(has_empty_inner_modules(module5))
        self.assertFalse(has_empty_inner_modules(module6))
        
        result=get_empty_inner_modules(module1)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0].attrib["name"],"module2")
        
        result=get_empty_inner_modules(module3)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0].attrib["name"],"module4")
        
        result=get_empty_inner_modules(module5)
        self.assertEqual(len(result),0)
        
        self.assertFalse(is_empty_module(module1))
        self.assertTrue(is_empty_module(module2))
        self.assertFalse(is_empty_module(module3))
        self.assertTrue(is_empty_module(module4))
        self.assertFalse(is_empty_module(module5))
        self.assertFalse(is_empty_module(module6))
        
        self.assertTrue(element_has_node_children(module1))
        self.assertFalse(element_has_node_children(module2))
        self.assertTrue(element_has_node_children(module3))
        self.assertFalse(element_has_node_children(module4))
        self.assertTrue(element_has_node_children(module5))
        self.assertTrue(element_has_node_children(module6))
        
    def test_replace_module_name(self):
        
        xml="""
<MODULE name="module1">
    <MODULE name="module2"/>
    <MODULE name="module3"/>
</MODULE>
        """
        
        new_name="abc"
        xml=replace_module_name(xml,new_name)
        
        module1=etree.fromstring(xml)
        module2=module1[0]
        module3=module1[1]
        
        self.assertEqual(module1.attrib["name"],new_name)
        self.assertEqual(module2.attrib["name"],"module2")
        self.assertEqual(module3.attrib["name"],"module3")
        
    def test_empty_inner_modules(self):
        """
        lxml quirk: performing an xpath search on module3 element searches module1.
        This test verifies the code here hasn't accidentally done that.
        """
        
        xml="""
<MODULE name="module1">
    <MODULE name="module2"/>
    <MODULE name="module3"/>
</MODULE>
        """
        
        module1=etree.fromstring(xml)
        module3=module1[1]
        
        self.assertFalse(has_empty_inner_modules(module3))
        
    def test_combined_flow_gdps_mini1(self):
        "the structure of the first row from gdps/g0 with nested modules"
        
        flow1="""
<MODULE name="module1">
  <SUBMITS sub_name="module2"/>
  <MODULE name="module2"/>
</MODULE>""".strip()

        flow2="""
<MODULE name="module2">
  <SUBMITS sub_name="task1"/>
  <TASK name="task1">
    <SUBMITS sub_name="module3"/>
  </TASK>
  <MODULE name="module3"/>
</MODULE>
""".strip()

        flow3="""
<MODULE name="module3">
  <SUBMITS sub_name="task2"/>
  <TASK name="task2">
    <SUBMITS sub_name="task3" type="user"/>
  </TASK>
  <NPASS_TASK name="task3"/>
</MODULE>
""".strip()

        expected="""
<MODULE name="module1">
  <SUBMITS sub_name="module2"/>
  <MODULE name="module2">
    <SUBMITS sub_name="task1"/>
    <TASK name="task1">
      <SUBMITS sub_name="module3"/>
    </TASK>
    <MODULE name="module3">
      <SUBMITS sub_name="task2"/>
      <TASK name="task2">
        <SUBMITS sub_name="task3" type="user"/>
      </TASK>
      <NPASS_TASK name="task3"/>
    </MODULE>
  </MODULE>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        flow3=flow3.strip()
        expected=expected.strip()

        xmls=[flow1,flow2,flow3]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)
        
    def test_combined_flow_gdps_mini2(self):
        "the structure of a problematic path along the gdps/g0 tree"

        flow1="""
<MODULE name="main">
  <SUBMITS sub_name="pre_assimcycle"/>
  <MODULE name="pre_assimcycle"/>
</MODULE>
        """

        flow2="""
<MODULE name="pre_assimcycle">
  <SUBMITS sub_name="get_arcdata_derisfc"/>
  <TASK name="get_arcdata_derisfc">
    <SUBMITS sub_name="derisfc"/>
  </TASK>
  <MODULE name="derisfc">
    <DEPENDS_ON dep_name="./cutoff" status="end" type="node"/>
  </MODULE>
</MODULE>
        """
        
        flow3="""
<MODULE name="derisfc">
  <SUBMITS sub_name="surface_bufr"/>
  <TASK name="surface_bufr">
    <SUBMITS sub_name="surface_merge"/>
  </TASK>
</MODULE>
        """

        expected="""
<MODULE name="main">
  <SUBMITS sub_name="pre_assimcycle"/>
  <MODULE name="pre_assimcycle">
    <SUBMITS sub_name="get_arcdata_derisfc"/>
    <TASK name="get_arcdata_derisfc">
      <SUBMITS sub_name="derisfc"/>
    </TASK>
    <MODULE name="derisfc">
      <SUBMITS sub_name="surface_bufr"/>
      <TASK name="surface_bufr">
        <SUBMITS sub_name="surface_merge"/>
      </TASK>
    </MODULE>
  </MODULE>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        flow3=flow3.strip()
        expected=expected.strip()

        xmls=[flow1,flow2,flow3]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)

    def test_combined_flow_gdps_mini3(self):
        "the structure of a problematic path along the gdps/g0 tree"

        flow1="""
<MODULE name="main">
  <SUBMITS sub_name="assimcycle"/>
  <MODULE name="assimcycle"/>
</MODULE>
        """

        flow2="""
<MODULE name="assimcycle">
  <SUBMITS sub_name="get_arcdata_anlalt"/>
  <TASK  name="get_arcdata_anlalt">
    <SUBMITS sub_name="anlalt"/>
  </TASK>
  <FAMILY name="anlalt">
    <SUBMITS sub_name="envar"/>
    <MODULE name="envar"/>
  </FAMILY>
</MODULE>
        """
        
        flow3="""
<MODULE name="envar">
  <SUBMITS sub_name="getTrials"/>
  <TASK name="getTrials">
    <SUBMITS sub_name="VAR"/>
  </TASK>
  <TASK name="VAR"/>
</MODULE>
        """

        expected="""
<MODULE name="main">
  <SUBMITS sub_name="assimcycle"/>
  <MODULE name="assimcycle">
    <SUBMITS sub_name="get_arcdata_anlalt"/>
    <TASK name="get_arcdata_anlalt">
      <SUBMITS sub_name="anlalt"/>
    </TASK>
    <FAMILY name="anlalt">
      <SUBMITS sub_name="envar"/>
      <MODULE name="envar">
        <SUBMITS sub_name="getTrials"/>
        <TASK name="getTrials">
          <SUBMITS sub_name="VAR"/>
        </TASK>
        <TASK name="VAR"/>
      </MODULE>
    </FAMILY>
  </MODULE>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        flow3=flow3.strip()
        expected=expected.strip()

        xmls=[flow1,flow2,flow3]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)
        
    def test_get_combined_flow_for_experiment_path(self):
        flow=get_combined_flow_for_experiment_path(BIG_ME_PATH)
        result=pretty(flow)
        
        "strings that are only found if module XMLs are successfully combined."
        self.assertIn("dep_module_keyword",result,msg="\n\n"+result)
    
    def test_paths_from_element(self):
        flow=get_combined_flow_for_experiment_path(BIG_ME_PATH)
        xpath="//SUBMITS[@sub_name='dep_parent_keyword']"
        
        elements=flow.xpath(xpath)
        element=elements[0]
        flow_branch,node_path,module_path=get_paths_from_element(element)
        expected="sample/Dependencies/downone/downtwo/dep_parent_keyword"
        self.assertEqual(node_path,expected)
        self.assertEqual(flow_branch,expected)
        
    def test_get_submits_and_children_from_element(self):
        xml=XML1
        module1=etree.fromstring(xml)
        family1=module1.xpath("//FAMILY[@name='family1']")[0]
        submits=get_submits_from_flow_element(family1)
        expected=["module1/family1/a","module1/family1/b","module1/family1/c","module1/family1/family2"]
        self.assertEqual(submits,expected)
        
        expected=["module1/family1/a",
                  "module1/family1/b",
                  "module1/family1/c",
                  "module1/family1/family2",
                  "module1/family1/e"]
        result=get_flow_children_from_flow_element(family1)
        msg="\n\n"+xml+"\n\nresult=\n"+"\n".join(result)+"\n\nexpected=\n"+"\n".join(expected)
        self.assertEqual(result,expected,msg=msg)
        
        xpath="//MODULE/FAMILY/FAMILY[@name='family2']"
        family2=module1.xpath(xpath)[0]
        result=get_flow_children_from_flow_element(family2)
        expected=["module1/family1/family2/f",
                  "module1/family1/family2/g"]
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)
        
    def test_flow_children_for_same_name(self):
        "when a module and a task share the same name"
        
        xml="""
<MODULE name="name1">
    <SUBMITS sub_name="name2"/>
    <TASK name="name2">
        <SUBMITS sub_name="name1" type="user"/>
    </TASK>
    <NPASS_TASK name="name1"/>
</MODULE>
        """.strip()
        module_element=etree.fromstring(xml)
        name2_element=module_element[1]
        result=get_flow_children_from_flow_element(name2_element)
        expected=["name1/name1"]
        self.assertEqual(result,expected)
            
    def test_find_all_flow_xml_for_experiment(self):
        results=find_all_flow_xml_for_experiment(BIG_ME_PATH)
        modules=["sample",
                 "ConfigModule",
                  "Dependencies",
                  "Different_Hosts",
                  "intraloopDependencies",
                  "Loop_example",
                  "RenamedConfigModule",
                  "submit_test",
                  "switchmod"]
        expected=[BIG_ME_PATH+"modules/"+m+"/flow.xml" for m in modules]
        for item in expected:
            self.assertIn(item,results)
        self.assertEqual(expected[0],results[0])
            
    def test_combine_flow_xml(self):
        flow1="""
<MODULE name="module1">
  <SUBMITS sub_name="module2"/>
  <MODULE name="module2"/>
  <SUBMITS sub_name="task1"/>
</MODULE>
"""

        flow2="""
<MODULE name="module2">
  <SUBMITS sub_name="task2"/>
</MODULE>
"""

        expected="""
<MODULE name="module1">
  <SUBMITS sub_name="module2"/>
  <MODULE name="module2">
    <SUBMITS sub_name="task2"/>
  </MODULE>
  <SUBMITS sub_name="task1"/>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        expected=expected.strip()

        xmls=[flow1,flow2]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)
        
    def test_combine_flow_xml_nested(self):
        "module we need is inside another module"
        
        flow1="""
<MODULE name="module1">
  <SUBMITS sub_name="module3"/>
  <MODULE name="module3"/>
  <SUBMITS sub_name="task1"/>
</MODULE>
"""

        flow2="""
<MODULE name="module2">
  <SUBMITS sub_name="task2"/>
  <MODULE name="module3">
    <SUBMITS sub_name="task3"/>
  </MODULE>
</MODULE>
"""

        expected="""
<MODULE name="module1">
  <SUBMITS sub_name="module3"/>
  <MODULE name="module3">
    <SUBMITS sub_name="task3"/>
  </MODULE>
  <SUBMITS sub_name="task1"/>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        expected=expected.strip()

        xmls=[flow1,flow2]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)
        
    def test_combine_flow_xml_recursive(self):
        "module1 references module2 which references module3"
        
        flow1="""
<MODULE name="module1">
  <SUBMITS sub_name="module2"/>
  <MODULE name="module2"/>
  <SUBMITS sub_name="task1"/>
</MODULE>
"""

        flow2="""
<MODULE name="module2">
  <SUBMITS sub_name="module3"/>
  <MODULE name="module3"/>
  <SUBMITS sub_name="task2"/>
</MODULE>
"""

        flow3="""
<MODULE name="module3">
  <SUBMITS sub_name="task3"/>
</MODULE>
"""

        expected="""
<MODULE name="module1">
  <SUBMITS sub_name="module2"/>
  <MODULE name="module2">
    <SUBMITS sub_name="module3"/>
    <MODULE name="module3">
      <SUBMITS sub_name="task3"/>
    </MODULE>
    <SUBMITS sub_name="task2"/>
  </MODULE>
  <SUBMITS sub_name="task1"/>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        flow3=flow3.strip()
        expected=expected.strip()

        xmls=[flow1,flow2,flow3]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)
        
    def test_combine_flow_xml_copy_pasted_module(self):
        "content of module2 is copy pasted - in flow1 and flow2. keep flow1"
        
        flow1="""
<MODULE name="module1">
  <SUBMITS sub_name="module2"/>
  <MODULE name="module2">
    <SUBMITS sub_name="task2"/>
  </MODULE>
  <SUBMITS sub_name="task1"/>
</MODULE>
"""

        flow2="""
<MODULE name="module2">
  <SUBMITS sub_name="task666"/>
</MODULE>
"""

        expected="""
<MODULE name="module1">
  <SUBMITS sub_name="module2"/>
  <MODULE name="module2">
    <SUBMITS sub_name="task2"/>
  </MODULE>
  <SUBMITS sub_name="task1"/>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        expected=expected.strip()

        xmls=[flow1,flow2]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)

    def test_combine_flow_module_submits_task_submits_module(self):
        "module2 inside module1 must retain its place, even if <SUBMITS> is elsewhere"
        
        flow1="""
<MODULE name="module1">
  <SUBMITS sub_name="task1"/>
  <TASK name="task1">
    <SUBMITS sub_name="module2"/>
  </TASK>
  <MODULE name="module2">
    <DEPENDS_ON dep_name="./getsfc" status="end" type="node"/>
  </MODULE>
</MODULE>
"""

        flow2="""
<MODULE name="module2">
  <SUBMITS sub_name="task2"/>
  <TASK name="task2"/>
</MODULE>
"""

        expected="""
<MODULE name="module1">
  <SUBMITS sub_name="task1"/>
  <TASK name="task1">
    <SUBMITS sub_name="module2"/>
  </TASK>
  <MODULE name="module2">
    <SUBMITS sub_name="task2"/>
    <TASK name="task2"/>
  </MODULE>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        expected=expected.strip()

        xmls=[flow1,flow2]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)
        
    def test_two_empty_modules_replace(self):
        "module1 contains two empty module2 references"
   
        flow1="""
<MODULE name="module1">
  <SUBMITS sub_name="task1"/>
  <TASK name="task1">
    <SUBMITS sub_name="module2"/>
  </TASK>
  <MODULE name="module2">
  </MODULE>
  <FAMILY name="family1">
    <SUBMITS sub_name="module2"/>
    <MODULE name="module2">
    </MODULE>
  </FAMILY>
</MODULE>
"""

        flow2="""
<MODULE name="module2">
  <SUBMITS sub_name="task2"/>
  <TASK name="task2"/>
</MODULE>
"""

        expected="""
<MODULE name="module1">
  <SUBMITS sub_name="task1"/>
  <TASK name="task1">
    <SUBMITS sub_name="module2"/>
  </TASK>
  <MODULE name="module2">
    <SUBMITS sub_name="task2"/>
    <TASK name="task2"/>
  </MODULE>
  <FAMILY name="family1">
    <SUBMITS sub_name="module2"/>
    <MODULE name="module2">
      <SUBMITS sub_name="task2"/>
      <TASK name="task2"/>
    </MODULE>
  </FAMILY>
</MODULE>
"""

        flow1=flow1.strip()
        flow2=flow2.strip()
        expected=expected.strip()

        xmls=[flow1,flow2]
        result=get_combined_flow_from_text_list(xmls)
        result=pretty(result)
        msg="\n\n**********\n\nresult = \n%s\n\nexpected =\n%s"%(result,expected)
        self.assertEqual(result,expected,msg=msg)






        
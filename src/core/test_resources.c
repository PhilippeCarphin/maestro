/* mtest_main.c - Used for experimentation and unit testing.
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/tree.h>
#include <libxml/xpathInternals.h>
#include "ResourceVisitor.h"
#include "FlowVisitor.h"
#include "SeqDatesUtil.h"
#include "SeqLoopsUtil.h"
#include "SeqUtil.h"
#include "nodeinfo.h"
#include "getopt.h"
#include "SeqNode.h"
#include "XmlUtils.h"
#include "l2d2_commun.h"

static char *c_test_files_folder = NULL;

/********************************************************************************
 * Creates an absolute path by appending the relative path to
 *c_test_files_folder, where c_test_files_folder =
 *${MAESTRO_REPO_LOCATION}/c_test_files_folder/ This should be used for any
 *paths so that the tests can be portable to different users who keep their
 *maestro stuff in different places.
 ********************************************************************************/
char *absolutePath(const char *relativePath) {
  SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() begin\n");
  char *absPath = (char *)malloc(strlen(c_test_files_folder) + 1 +
                                 strlen(relativePath) + 1);
  sprintf(absPath, "%s%c%s", c_test_files_folder, '/', relativePath);
  SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() end, returning %s\n", absPath);
  return absPath;
}

void header(const char *test) {
  SeqUtil_TRACE(TL_CRITICAL,
                "\n=================== UNIT TEST FOR %s ===================\n",
                test);
}

ResourceVisitorPtr createTestResourceVisitor(SeqNodeDataPtr ndp,
                                             const char *nodePath,
                                             const char *xmlFile,
                                             const char *defFile) {
  SeqUtil_TRACE(TL_FULL_TRACE, "createTestResourceVisitor() begin\n");
  ResourceVisitorPtr rv = (ResourceVisitorPtr)malloc(sizeof(ResourceVisitor));

  rv->nodePath = (nodePath != NULL ? strdup(nodePath) : strdup(""));

  rv->defFile = (defFile != NULL ? strdup(defFile) : NULL);
  rv->xmlFile = (xmlFile != NULL ? strdup(xmlFile) : NULL);

  rv->context = Resource_createContext(ndp, xmlFile, defFile, ndp->type);
  rv->context->node = rv->context->doc->children;

  rv->loopResourcesFound = 0;
  rv->forEachResourcesFound = 0;
  rv->batchResourcesFound = 0;
  rv->abortActionFound = 0;
  rv->workerPathFound = 0;

  rv->_stackSize = 0;

  SeqUtil_TRACE(TL_FULL_TRACE, "createTestResourceVisitor() end\n");
  return rv;
}

int test_Resource_getLoopAttributes() {
  header("getLoopAttributes");
  /* SETUP: We need a resource visitor, so an xml file and defFile, and a node
   * data pointer of type loop. */
  SeqNodeDataPtr ndp = SeqNode_createNode("Phil");
  const char *xmlFile = absolutePath("validityXml.xml");
  ResourceVisitorPtr rv = createTestResourceVisitor(ndp, NULL, xmlFile, NULL);

  /* TEST1 : Look for the first validity node. Get loop resources from that,
   * confirm that the expression found matches the one in the xml file */
  xmlXPathObjectPtr result =
      XmlUtils_getnodeset("(/NODE_RESOURCES/VALIDITY)", rv->context);
  xmlNodePtr valNode = result->nodesetval->nodeTab[1];
  ndp->type = Loop;
  rv->context->node = valNode;
  rv->loopResourcesFound = 0;
  SeqUtil_setTraceFlag(TRACE_LEVEL, TL_FULL_TRACE);
  Resource_getLoopAttributes(rv, ndp);
  SeqNameValues_printList(ndp->data);
  char *expression = SeqNameValues_getValue(ndp->data, "EXPRESSION");
  if (expression == NULL || strcmp(expression, "0:24:3:6") != 0)
    raiseError("TEST_FAILED");
  free(expression);
  expression = NULL;

  /* TEST 2 : Do the same with the root node and validate the expression found.
   * */
  xmlNodePtr root_node = rv->context->doc->children;
  rv->context->node = root_node;
  rv->loopResourcesFound = 0;
  SeqNameValues_deleteWholeList(&(ndp->data));
  SeqUtil_TRACE(TL_FULL_TRACE, "root_node->name=%s\n", root_node->name);
  Resource_getLoopAttributes(rv, ndp);
  SeqNameValues_printList(ndp->data);
  expression = SeqNameValues_getValue(ndp->data, "EXPRESSION");
  SeqUtil_TRACE(TL_FULL_TRACE, "expression=%s\n", expression);
  if (expression == NULL || strcmp(expression, "0:54:3:6") != 0)
    raiseError("TEST_FAILED");

  SeqNode_freeNode(ndp);
  free(expression);
  free((char *)xmlFile);
  xmlXPathFreeObject(result);
  deleteResourceVisitor(rv);
  return 0;
}

int test_parseNodeDFS() {
  header("parseNodeDFS");

  /* SETUP : Artificially create a resourceVisitor with the xml file, and a
   * nodeDataPtr with a datestamp and an extension for validity checking */
  SeqNodeDataPtr ndp = SeqNode_createNode("phil");
  SeqNameValuesPtr loopsArgs = NULL;
  free(ndp->datestamp);
  ndp->datestamp = strdup("20160102030405");
  const char *xmlFile = absolutePath("loop_container.xml");
  ResourceVisitorPtr rv = createTestResourceVisitor(ndp, NULL, xmlFile, NULL);

  Resource_parseNodeDFS(rv, ndp, Resource_getLoopAttributes);
  char *expression = SeqNameValues_getValue(ndp->data, "EXPRESSION");
  if (expression != NULL && strcmp(expression, "5:6:7:8") != 0)
    raiseError("TEST_FAILED");
  SeqNameValues_deleteWholeList(&(ndp->data));
  free(expression);

  rv->loopResourcesFound = 0;
  SeqUtil_TRACE(TL_FULL_TRACE,
                "============================ test with datestamp hour = 12\n");
  free(ndp->datestamp);
  ndp->datestamp = strdup("20160102120000");
  Resource_parseNodeDFS(rv, ndp, Resource_getLoopAttributes);
  expression = SeqNameValues_getValue(ndp->data, "EXPRESSION");
  if (expression == NULL || strcmp(expression, "9:10:11:12") != 0)
    raiseError("TEST_FAILED");
  SeqNameValues_deleteWholeList(&(ndp->data));
  free(expression);

  rv->loopResourcesFound = 0;
  free(ndp->extension);
  ndp->extension = strdup("+1");
  SeqLoops_parseArgs(&loopsArgs, "loop1=1");
  SeqNode_setLoopArgs(ndp, loopsArgs);
  Resource_parseNodeDFS(rv, ndp, Resource_getLoopAttributes);
  expression = SeqNameValues_getValue(ndp->data, "EXPRESSION");
  if (expression == NULL || strcmp(expression, "13:14:15:16") != 0)
    raiseError("TEST_FAILED");
  SeqNameValues_deleteWholeList(&(ndp->data));
  free(expression);

  SeqNode_freeNode(ndp);
  free((char *)xmlFile);
  deleteResourceVisitor(rv);
  return 0;
}

int test_Resource_parseWorkerPath() {
  header("parseWorkerPath");
  SeqNodeDataPtr ndp = SeqNode_createNode("phil");
  SeqNameValuesPtr loopsArgs = NULL;
  free(ndp->datestamp);
  ndp->datestamp = strdup("20160102120000");
  free(ndp->extension);
  ndp->extension = strdup("+1");
  SeqLoops_parseArgs(&loopsArgs, "loop1=1");
  SeqNode_setLoopArgs(ndp, loopsArgs);

  const char *xmlFile = absolutePath("loop_container.xml");
  ResourceVisitorPtr rv = createTestResourceVisitor(ndp, NULL, xmlFile, NULL);

  Resource_parseNodeDFS(rv, ndp, Resource_getWorkerPath);

  if (strcmp(ndp->workerPath, "this/is/the/end") != 0)
    raiseError("TEST FAILED");

  free(ndp->datestamp);
  ndp->datestamp = strdup("20160101030405");
  free(ndp->workerPath);
  ndp->workerPath = strdup("HELLO");
  rv->workerPathFound = RESOURCE_FALSE;

  Resource_parseNodeDFS(rv, ndp, Resource_getWorkerPath);

  SeqUtil_TRACE(TL_FULL_TRACE, "ndp->workerPath: %s\n", ndp->workerPath);
  if (strcmp(ndp->workerPath, "hello/my/name/is/inigo/montoya/you/killed/my/"
                              "father/prepare/to/die") != 0)
    raiseError("TEST FAILED");

  SeqNode_freeNode(ndp);
  free((char *)xmlFile);
  deleteResourceVisitor(rv);
  return 0;
}

int runTests(const char *seq_exp_home, const char *node,
             const char *datestamp) {
  test_Resource_getLoopAttributes();
  test_parseNodeDFS();
  test_Resource_parseWorkerPath();

  SeqUtil_TRACE(TL_CRITICAL,
                "============== ALL TESTS HAVE PASSED =====================\n");
  return 0;
}

int main(int argc, char *argv[]) {
  char *short_opts = "n:f:l:o:d:e:v";
  char *node = NULL, *seq_exp_home = NULL, *datestamp = NULL, *tmpDate = NULL;
  extern char *optarg;

  extern char *optarg;
  extern int optind;
  struct option long_opts[] = {
      /*  NAME        ,    has_arg       , flag  val(ID) */

      {"exp", required_argument, 0, 'e'},
      {"node", required_argument, 0, 'n'},
      {"loop-args", required_argument, 0, 'l'},
      {"datestamp", required_argument, 0, 'd'},
      {"outputfile", required_argument, 0, 'o'},
      {"filters", required_argument, 0, 'f'},
      {"verbose", no_argument, 0, 'v'},
      {NULL, 0, 0, 0} /* End indicator */
  };
  int opt_index, c = 0, i;

  while ((c = getopt_long(argc, argv, short_opts, long_opts, &opt_index)) !=
         -1) {
    switch (c) {
    case 'n':
      node = strdup(optarg);
      break;
    case 'e':
      seq_exp_home = strdup(optarg);
      break;
    case 'd':
      datestamp = malloc(PADDED_DATE_LENGTH + 1);
      strcpy(datestamp, optarg);
      break;
    case '?':
      exit(1);
    }
  }

  SeqUtil_setTraceFlag(TRACE_LEVEL, TL_FULL_TRACE);

  const char *PWD = getenv("PWD");
  /* Check that the path PWD ends with maestro.  It's the best we can do to
   * make sure that mtest is being run from the right place. */
  const char *p = PWD;
  while (*p++ != 0)
    ;
  while (*(p - 1) != '/')
    --p;

#ifdef MAESTRO_BUILT_WITH_CMAKE
  char *suffix = "/../../../tests/mock_files/c_tests";
#else
  char *suffix = "/../../tests/mock_files/c_tests";
#endif

  c_test_files_folder =
      (char *)malloc(sizeof(char) * (strlen(PWD) + strlen(suffix) + 1));
  sprintf(c_test_files_folder, "%s%s", PWD, suffix);

  puts(c_test_files_folder);

  if ((datestamp == NULL) && ((tmpDate = getenv("SEQ_DATE")) != NULL)) {
    datestamp = malloc(PADDED_DATE_LENGTH + 1);
    strcpy(datestamp, tmpDate);
  }

  if (datestamp != NULL) {
    i = strlen(datestamp);
    while (i < PADDED_DATE_LENGTH) {
      datestamp[i++] = '0';
    }
    datestamp[PADDED_DATE_LENGTH] = '\0';
  }

  runTests(seq_exp_home, node, datestamp);

  free(node);
  free(seq_exp_home);
  free(datestamp);
  return 0;
}

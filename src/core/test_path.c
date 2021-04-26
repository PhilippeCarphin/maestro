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

/********************************************************************************
 * Creates an absolute path by appending the relative path to
 *TEST_FILES_D, where TEST_FILES_D=
 *${MAESTRO_REPO_LOCATION}/TEST_FILES_D/ This should be used for any
 *paths so that the tests can be portable to different users who keep their
 *maestro stuff in different places.
 ********************************************************************************/
char *absolutePath(const char *relativePath) {
  SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() begin\n");
  char *absPath = (char *)malloc(strlen(TEST_FILES_DIR
) + 1 +
                                 strlen(relativePath) + 1);
  sprintf(absPath, "%s%c%s", TEST_FILES_DIR, '/', relativePath);
  SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() end, returning %s\n", absPath);
  return absPath;
}


void header(const char *test) {
  SeqUtil_TRACE(TL_CRITICAL,
                "\n=================== UNIT TEST FOR %s ===================\n",
                test);
}

FlowVisitorPtr createTestFlowVisitor() {
  SeqUtil_TRACE(TL_FULL_TRACE, "createTestFlowVisitor() begin\n");
  FlowVisitorPtr new_flow_visitor = (FlowVisitorPtr)malloc(sizeof(FlowVisitor));
  if (new_flow_visitor == NULL)
    raiseError("createTestFlowVisitor(): out of memory\n");

  char postfix[] = "/flow.xml";
  char *xmlFilename =
      (char *)malloc(strlen(TEST_FILES_DIR) + strlen(postfix) + 1);
  if (xmlFilename == NULL) {
    raiseError("createTestFlowVisitor(): out of memory\n");
  }

  sprintf(xmlFilename, "%s%s", TEST_FILES_DIR, postfix);
  xmlDocPtr doc = XmlUtils_getdoc(xmlFilename);
  if (doc == NULL) {
    raiseError("createTestFlowVisitor(): file %s not found or unreadable\n",
               xmlFilename);
  }

  new_flow_visitor->context = xmlXPathNewContext(doc);
  free(xmlFilename);

  new_flow_visitor->nodePath = strdup("/entry_mod/task");
  new_flow_visitor->expHome = NULL;
  new_flow_visitor->datestamp = NULL;
  new_flow_visitor->switch_args = NULL;
  new_flow_visitor->context->node = new_flow_visitor->context->doc->children;
  new_flow_visitor->currentFlowNode = NULL;
  new_flow_visitor->suiteName = NULL;
  new_flow_visitor->taskPath = NULL;
  new_flow_visitor->module = NULL;
  new_flow_visitor->intramodulePath = NULL;
  new_flow_visitor->currentNodeType = Task;

  new_flow_visitor->_stackSize = 0;

  SeqUtil_TRACE(TL_FULL_TRACE, "createTestFlowVisitor() end\n");
  return new_flow_visitor;
}


int test_Flow_setPathToModule() {
  header("setPathToModule");

  SeqNodeDataPtr ndp = SeqNode_createNode("nice_node");
  FlowVisitorPtr fv = createTestFlowVisitor();
  free(fv->intramodulePath);
  free(ndp->container);
  free(fv->module);
  fv->intramodulePath = strdup("/mod/family");
  ndp->container = strdup("/entry_mod/mod/family");
  fv->module = strdup("mod");
  fv->_stackSize = 1;

  Flow_setPathToModule(fv, ndp);

  if (strcmp(ndp->pathToModule, "/entry_mod/mod") != 0)
    raiseError("TEST_FAILED");
  return 0;
}

int runTests(const char *seq_exp_home, const char *node,
             const char *datestamp) {
  test_Flow_setPathToModule();

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

  puts(TEST_FILES_DIR);

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

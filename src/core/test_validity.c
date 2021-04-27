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
 * MAESTRO TEST FILE
 *
 * This file is intended as a place to do unit testing and experimentation
 * during development and bug solving in maestro.
 *
 * This file assumes that the executable is being run from the maestro directory
 * so that paths can be relative to that directory:
 *
 * C_TEST_FILES_FOLDER is the location to look in for whaterver files are being
 *used for these tests.
 *
 * It is encouraged to put all files that need to be accessed in
 * that directory, so that, for example, if one must modify resourceVisitor
 * functions, they can checkout the mtest_main.c file from a previous commit and
 * run the tests periodically to make sure that all the functions still fulfill
 * their contract, and to catch runtime errors at the earliest possible moment.
 *
 * The base of the test file is the main(), the runTests() function and the
 * absolutePath() function, and the header() function.  The rest is the actual
 * tests, which should have a SETUP, and some TESTS where the result of the test
 * is verified, and raiseError() should be called if the result is different
 * from the expected result.
 *
 * Lower level functions should be tested first so that they may be known to
 * work when testing the higher level functions that use them.
 *
 ********************************************************************************/

/********************************************************************************
 * Creates an absolute path by appending the relative path to
 *C_TEST_FILES_FOLDER, where C_TEST_FILES_FOLDER =
 *${MAESTRO_REPO_LOCATION}/C_TEST_FILES_FOLDER/ This should be used for any
 *paths so that the tests can be portable to different users who keep their
 *maestro stuff in different places.
 ********************************************************************************/
char *absolutePath(const char *relativePath) {
  SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() begin\n");
  char *absPath = (char *)malloc(strlen(C_TEST_FILES_FOLDER) + 1 +
                                 strlen(relativePath) + 1);
  sprintf(absPath, "%s%c%s", C_TEST_FILES_FOLDER, '/', relativePath);
  SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() end, returning %s\n", absPath);
  return absPath;
}

ResourceVisitorPtr createTestResourceVisitor(SeqNodeDataPtr ndp,
                                             const char *nodePath,
                                             const char *xmlFile,
                                             const char *defFile);

void header(const char *test) {
  SeqUtil_TRACE(TL_CRITICAL,
                "\n=================== UNIT TEST FOR %s ===================\n",
                test);
}


int test_getValidityData() {
  header("getValidityData()");
  /* SETUP : We need a nodeDataPtr, and the xmlNodePtr of a validity node */
  SeqNodeDataPtr ndp = SeqNode_createNode("Phil");

  const char *xmlFile = absolutePath("validityXml.xml");
  SeqUtil_TRACE(TL_FULL_TRACE, "HERE, xmlFile = %s\n", xmlFile);
  xmlDocPtr doc = XmlUtils_getdoc(xmlFile);
  xmlXPathContextPtr rc = xmlXPathNewContext(doc);
  xmlXPathObjectPtr result =
      XmlUtils_getnodeset("(/NODE_RESOURCES/VALIDITY)", rc);
  xmlNodePtr valNode = result->nodesetval->nodeTab[1];

  /* TEST 1 : We get the VALIDITY node's info and compare it to the actual
   * values read with our eyes. */
  ValidityDataPtr valDat = getValidityData(valNode);
  printValidityData(valDat);
  if (strcmp(valDat->dow, "0") || strcmp(valDat->hour, "00") ||
      strcmp(valDat->local_index, "loop=0"))
    raiseError("TEST FAILED");

  header("isValid");
  /* INPUT: _nodeDataPtr and xmlNodePtr of a validityNode. */
  
  SeqNode_freeNode(ndp);
  free((char *)xmlFile);
  xmlXPathFreeContext(rc);
  xmlXPathFreeObject(result);
  xmlFreeDoc(doc);
  deleteValidityData(valDat);
  return 0;
}

int test_isValid() {

  SeqNodeDataPtr ndp = SeqNode_createNode("Phil");
  SeqNameValuesPtr loopsArgs = NULL;
  const char *xmlFile = absolutePath("validityXml.xml");
  xmlDocPtr doc = XmlUtils_getdoc(xmlFile);
  xmlXPathContextPtr rc = xmlXPathNewContext(doc);
  xmlXPathObjectPtr result =
      XmlUtils_getnodeset("(/NODE_RESOURCES/VALIDITY)", rc);
  xmlNodePtr valNode = result->nodesetval->nodeTab[1];
  ValidityDataPtr valDat = getValidityData(valNode);
  printValidityData(valDat);

  /* TEST : With the datestamp and the extension of 0, the VALIDITY node should
   * be considered valid. */
  free(ndp->datestamp);
  ndp->datestamp = strdup("20160102030405");
  free(ndp->extension);
  ndp->extension = strdup("+0");
  SeqLoops_parseArgs(&loopsArgs, "loop=0");
  SeqNode_setLoopArgs(ndp, loopsArgs);
  printValidityData(valDat);
  if (!isValid(ndp, valNode))
    raiseError("TEST_FAILED");
  deleteValidityData(valDat);

  SeqNode_freeNode(ndp);
  xmlXPathFreeObject(result);
  xmlXPathFreeContext(rc);
  xmlFreeDoc(doc);
  free((char *)xmlFile);
  return 0;
}


int runTests(const char *seq_exp_home, const char *node,
             const char *datestamp) {
  test_getValidityData();
  test_isValid();

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

  puts(C_TEST_FILES_FOLDER);

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

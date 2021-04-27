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


char *absolutePath(const char *relativePath) {
  SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() begin\n");
  char *absPath = (char *)malloc(strlen(C_TEST_FILES_FOLDER) + 1 + strlen(relativePath) + 1);
  sprintf(absPath, "%s%c%s", C_TEST_FILES_FOLDER, '/', relativePath);
  SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() end, returning %s\n", absPath);
  return absPath;
}

void header(const char *test) {
  SeqUtil_TRACE(TL_CRITICAL, "\n=================== UNIT TEST FOR %s ===================\n", test);
}


int test_getIncrementedDatestamp() {
  header("getIncrementedDatestamp");
  /* SETUP : Create a datestamp and ValidityData object with a non-empty hour
   * attribute */
  const char *baseDatestamp = "20160102030405";
  ValidityData validityData1 = {"", "", "", "", "", ""};
  ValidityDataPtr val = &validityData1;
  val->hour = "03";

  /* TEST : Resulting incremented datestamp must be 20160102060405 */
  const char *newDatestamp = SeqDatesUtil_getIncrementedDatestamp(
      baseDatestamp, val->hour, val->time_delta);
  if (strcmp("20160102060405", newDatestamp))
    raiseError("TEST_FAILED");

  /* CLEANUP */
  free((char *)newDatestamp);
  return 0;
}


int runTests(const char *seq_exp_home, const char *node,
             const char *datestamp) {

  test_getIncrementedDatestamp();

  SeqUtil_TRACE(TL_CRITICAL, "============== ALL TESTS HAVE PASSED =====================\n");
  return 0;
}

int main(int argc, char *argv[]) {
  char *node = NULL, *seq_exp_home = NULL, *datestamp = NULL, *tmpDate = NULL;
  extern char *optarg;

  extern char *optarg;
  extern int optind;

  SeqUtil_setTraceFlag(TRACE_LEVEL, TL_FULL_TRACE);

  const char *PWD = getenv("PWD");
  /* Check that the path PWD ends with maestro.  It's the best we can do to
   * make sure that mtest is being run from the right place. */
  const char *p = PWD;
  while (*p++ != 0)
    ;
  while (*(p - 1) != '/')
    --p;

  if ((datestamp == NULL) && ((tmpDate = getenv("SEQ_DATE")) != NULL)) {
    datestamp = malloc(PADDED_DATE_LENGTH + 1);
    strcpy(datestamp, tmpDate);
  }

  int i;
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

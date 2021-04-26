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

int test_str2md5() {
  header("str2md5");
  char *md5sum = NULL;

  md5sum = (char *)str2md5("Encode moi ca", strlen("Encode moi ca"));
  if (strncmp(md5sum, "13325029457f870681ed978b9d132fc7", 32) != 0) {
    raiseError("TEST_FAILED");
  }

  return 0;
}

int runTests(const char *seq_exp_home, const char *node,
             const char *datestamp) {
  test_str2md5();

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

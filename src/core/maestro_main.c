/* maestro_main.c - Command-line API for the main engine in the Maestro
 * sequencer software package.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "maestro.h"
#include "SeqListNode.h"
#include "SeqUtil.h"
#include "SeqNameValues.h"
#include "SeqDatesUtil.h"
#include "SeqLoopsUtil.h"
#include "getopt.h"
#include <libxml/parser.h>
/***********************************************************************************
 * name: maestro
 *
 * author: cmois
 *
 * description: maestro - operational run control manager
 *
 * revision:
 *
 *************************************************************************************/
static void printSeqUsage() {
  char *usage = "For complete and up to date information on this command, see "
                "the man page by typing 'man maestro'.";
  puts(usage);
}

int main(int argc, char *argv[])

{
  const char *short_opts = "n:s:f:l:d:o:e:ivh";
  extern char *optarg;
  extern int optind;
  struct option long_opts[] = {
      /*  NAME               ,    has_arg       , flag  val(ID) */
      {"exp", required_argument, 0, 'e'},
      {"node", required_argument, 0, 'n'},
      {"loop-args", required_argument, 0, 'l'},
      {"datestamp", required_argument, 0, 'd'},
      {"signal", required_argument, 0, 's'},
      {"flow", required_argument, 0, 'f'},
      {"extra-soumet-args", required_argument, 0, 'o'},
      {"ignore-dependencies", no_argument, 0, 'i'},
      {"help", no_argument, 0, 'h'},
      {"verbose", no_argument, 0, 'v'},
      {NULL, 0, 0, 0} /* End indicator */
  };
  int opt_index, c = 0;

  char *node = NULL, *sign = NULL, *loops = NULL, *flow = NULL,
       *extraArgs = NULL, *datestamp = NULL, *seq_exp_home = NULL,
       *tmpDate = NULL;
  int status = 0;
  int i = 0;
  int vset = 0;
  int ignoreAllDeps = 0;
  int gotNode = 0, gotSignal = 0, gotLoops = 0;
  SeqNameValuesPtr loopsArgs = NULL;

  if (argc < 5) {
    printSeqUsage();
    exit(1);
  }
  flow = malloc(9 * sizeof(char) + 1);
  sprintf(flow, "%s", "continue");
  while ((c = getopt_long(argc, argv, short_opts, long_opts, &opt_index)) !=
         -1) {
    switch (c) {
    case 'n':
      node = malloc(strlen(optarg) + 1);
      strcpy(node, optarg);
      gotNode = 1;
      break;
    case 's':
      sign = malloc(strlen(optarg) + 1);
      strcpy(sign, optarg);
      gotSignal = 1;
      break;
    case 'd':
      datestamp = malloc(PADDED_DATE_LENGTH + 1);
      strncpy(datestamp, optarg, PADDED_DATE_LENGTH);
      break;
    case 'f':
      strcpy(flow, optarg);
      break;
    case 'l':
      /* loops argument */
      loops = malloc(strlen(optarg) + 1);
      strcpy(loops, optarg);
      gotLoops = 1;
      break;
    case 'v':
      SeqUtil_setTraceFlag(TRACE_LEVEL, TL_FULL_TRACE);
      SeqUtil_setTraceFlag(TF_TIMESTAMP, TF_ON);
      vset = 1;
      break;
    case 'i':
      ignoreAllDeps = 1;
      break;
    case 'o':
      extraArgs = malloc(strlen(optarg) + 1);
      strcpy(extraArgs, optarg);
      break;
    case 'e':
      seq_exp_home = strdup(optarg);
      break;
    case '?':
      printSeqUsage();
      exit(1);
    }
  }
  if (gotNode == 0 || gotSignal == 0) {
    printSeqUsage();
    exit(1);
  }
  if (vset == 0)
    SeqUtil_setTraceEnv();
  if (gotLoops) {

    if (SeqLoops_parseArgs(&loopsArgs, loops) == -1) {
      fprintf(stderr, "ERROR: Invalid loop arguments: %s\n", loops);
      exit(1);
    }
  }
  if (seq_exp_home == NULL) {
    seq_exp_home = getenv("SEQ_EXP_HOME");
  }
  if ((datestamp == NULL) && ((tmpDate = getenv("SEQ_DATE")) != NULL)) {
    datestamp = malloc(PADDED_DATE_LENGTH + 1);
    strncpy(datestamp, tmpDate, PADDED_DATE_LENGTH);
  }

  if (datestamp != NULL) {
    i = strlen(datestamp);
    while (i < PADDED_DATE_LENGTH) {
      datestamp[i++] = '0';
    }
    datestamp[PADDED_DATE_LENGTH] = '\0';
  }

  status = maestro(node, sign, flow, loopsArgs, ignoreAllDeps, extraArgs,
                   datestamp, seq_exp_home);

  free(flow);
  free(node);
  free(sign);
  free(extraArgs);
  fprintf(stderr, "maestro_main exiting with code %d\n", status);
  SeqUtil_unmapfiles();
  xmlCleanupParser();
  exit(status);
}



#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "SeqUtil.h"
#include "getopt.h"
static void printUsage() {
  char *usage = "For complete and up to date information on this command, see "
                "the man page by typing 'man getdef'.";
  puts(usage);
}

int main(int argc, char *argv[]) {
  const char *short_opts = "e:v";
  extern char *optarg;
  extern int optind;
  struct option long_opts[] = {
      /*  NAME        ,    has_arg       , flag  val(ID) */
      {"exp", required_argument, 0, 'e'},
      {"verbose", no_argument, 0, 'v'},
      {"help", no_argument, 0, 'h'},
      {NULL, 0, 0, 0} /* End indicator */
  };
  int opt_index, c = 0;
  char *value, *deffile = NULL, *seq_exp_home = NULL;
  int file, key;

  if (argc < 3) {
    printUsage();
    exit(1);
  }
  file = argc - 2;
  key = argc - 1;
  while ((c = getopt_long(argc, argv, short_opts, long_opts, &opt_index)) !=
         -1) {
    switch (c) {
    case 'e':
      seq_exp_home = strdup(optarg);
      break;
    case 'v':
      SeqUtil_setTraceFlag(TRACE_LEVEL, TL_FULL_TRACE);
      SeqUtil_setTraceFlag(TF_TIMESTAMP, TF_ON);
      break;
    case 'h':
    case '?':
      printUsage();
      exit(1);
      break;
    }
  }

  if (strcmp(argv[file], "resources") == 0) {
    if (seq_exp_home == NULL) {
      if ((seq_exp_home = getenv("SEQ_EXP_HOME")) == NULL) {
        raiseError(
            "ERROR: Shortcut %s unavailable when SEQ_EXP_HOME is undefined\n",
            argv[file]);
      }
    }
    deffile = (char *)malloc(strlen(seq_exp_home) +
                             strlen("/resources/resources.def") + 2);
    sprintf(deffile, "%s/resources/resources.def", seq_exp_home);
  } else {
    if (seq_exp_home == NULL) {
      if ((seq_exp_home = getenv("SEQ_EXP_HOME")) == NULL) {
        seq_exp_home = getenv("HOME");
      }
    }
    deffile = (char *)malloc(strlen(argv[file]) + 1);
    strcpy(deffile, argv[file]);
  }

  if ((value = SeqUtil_getdef(deffile, argv[key], seq_exp_home)) == NULL) {
    raiseError("ERROR: Unable to find key %s in %s\n", argv[key], argv[file]);
  } else {
    printf("%s\n", value);
  }
  free(value);
  free(deffile);
  SeqUtil_unmapfiles();
  exit(0);
}

/* mtest_main.c - Used for experimentation and unit testing.
 * Copyright (C) 2011-2015  Operations division of the Canadian Meteorological Centre
 *                          Environment Canada
 *
 * Maestro is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation,
 * version 2.1 of the License.
 *
 * Maestro is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include "getopt.h"
#include "SeqUtil.h"
#include "TsvInfoDatabase.h"


int MLLServerConnectionFid=0;

static void printUsage()
{
   char * usage = "\
DESCRIPTION: tsvinfo\n\
\n\
        Creates a file containing data on the nodes of an experiment for the GUI\n\
        to use to speed up the process of getting information on node resources.\n\
        The tsv output is formatted to be read in one line into a tsv (TCL thread\n\
        package) keyed list.  The program will also output human readable output\n\
        for human inspection.\n\
\n\
USAGE\n\
\n\
    tsvinfo -e SEQ_EXP_HOME [-t tsv-output-file -h human-readable-file]\n\
\n\
OPTIONS\n\
\n\
    -e, --exp \n\
        Experiment path.  If it is not supplied, the environment variable \n\
        SEQ_EXP_HOME will be used.\n\
\n\
    -t, --tsv-file \n\
        Specify the filename for the tsv formatted output.  If no filename is\n\
        is specified, output will go to stdout\n\
\n\
    -r, --readable-file \n\
        Specify the filename for the human readable output.  If no filename is\n\
        is specified, output will go to stderr\n\
\n\
    -v, --verbose\n\
        Turn on full tracing\n\
\n\
    -h, --help\n\
        Show this help screen\n\
\n\
EXAMPLES:\n\
\n\
    tsvinfo -e /home/ops/afsi/phc/.suites/sample -t /home/ops/afsi/phc/.suites/sample/resources/tsv_resources.txt\n\
            Creates an info file for the experiment 'sample' and stores the file\n\
            in the resources directory of that experiment where the GUI expects\n\
            it to be.\n\
\n\
    tsvinfo -e /home/ops/afsi/phc/.suites/sample -t /home/ops/afsi/phc/.suites/sample/resources/tsv_resources.txt -r ~/tmp/tmp_human_readable_output.c\n\
            Creates a tsv readable file for the GUI to use and a human readable\n\
            file for human inspection.  Making it a .c file will have have the\n\
            editor highlight the C-like syntax of the file nicely\n";
puts(usage);
}
int main ( int argc, char * argv[] )
{
   char * short_opts = "e:t:r:vh";

   extern char *optarg;
   extern char *optarg;
   extern int   optind;
   struct       option long_opts[] =
   { /*  NAME        ,    has_arg       , flag  val(ID) */

      {"exp"            , required_argument,   0,     'e'},
      {"tsv-file"       , required_argument,   0,     't'},
      {"readable-output", required_argument,   0,     'r'},
      {"verbose"        , no_argument      ,   0,     'v'},
      {"help"           , no_argument      ,   0,     'h'},
      {NULL,0,0,0} /* End indicator */
   };
   int opt_index, c = 0;

   char *seq_exp_home = NULL;

   FILE *human_output_fp = stderr,
        *tsv_output_fp = stdout;

   while ((c = getopt_long(argc, argv, short_opts, long_opts, &opt_index )) != -1) {
      switch(c) {
         case 'e':
            seq_exp_home = strdup(optarg);
            break;
         case 'r':
            if(!(human_output_fp = fopen(optarg, "w")))
               raiseError("Error : unable to open file %s for writing\n", optarg);
            break;
         case 't':
            if(!(tsv_output_fp = fopen(optarg, "w")))
               raiseError("Error : unable to open file %s for writing\n", optarg);
            break;
         case 'v':
            SeqUtil_setTraceFlag(TRACE_LEVEL,TL_FULL_TRACE);
            SeqUtil_setTraceFlag(TF_TIMESTAMP,TF_ON);
            break;
         case 'h':
            printUsage();
            exit(0);
            break;
         case '?':
            exit(1);
      }
   }

   if( seq_exp_home == NULL ){
      if( seq_exp_home = getenv("SEQ_EXP_HOME") != NULL ){
         seq_exp_home = strdup(seq_exp_home);
      } else {
         raiseError("Error : Experiment home must either be set as an argument of option -e (--exp) \n        or through the environment variable SEQ_EXP_HOME\n");
      }
   }


   write_db_file(seq_exp_home, tsv_output_fp , human_output_fp);


   free(seq_exp_home);
   return 0;
}









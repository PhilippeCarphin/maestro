/* nodelogger_main.c - Command-line API of the log-writing functions of the Maestro sequencer software package.
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

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <signal.h>
#include <string.h>
#include <unistd.h>
#include "nodelogger.h"
#include "tictac.h"
#include "nodeinfo.h"
#include "SeqLoopsUtil.h"
#include "SeqNameValues.h"
#include "SeqUtil.h"
#include "getopt.h"


static void alarm_handler() { fprintf(stderr,"@@@@@@ EXCEEDED TIME IN LOOP ITERATIONS @@@@@@\n"); };

static void printUsage()
{
    char * usage = "For complete and up to date information on this command, see the man page by typing 'man nodelogger'.";
    puts(usage);
}

int main (int argc, char * argv[])

{
   char * short_opts = "n:s:l:m:d:e:v";
   extern char *optarg;
   extern int   optind;
   struct       option long_opts[] =
   { /*  NAME        ,    has_arg       , flag  val(ID) */
      {"exp"         , required_argument,   0,     'e'}, 
      {"node"        , required_argument,   0,     'n'}, 
      {"loop-args"   , required_argument,   0,     'l'}, 
      {"datestamp"   , required_argument,   0,     'd'}, 
      {"signal"      , required_argument,   0,     's'}, 
      {"message"     , required_argument,   0,     'm'}, 
      {"verbose"     , no_argument      ,   0,     'v'}, 
      {NULL,0,0,0} /* End indicator */
   };
   int opt_index, c = 0;


   char *node = NULL, *signal = NULL , *message = NULL, *loops = NULL, *datestamp = NULL, *seq_exp_home = NULL, *tmpDate=NULL;
   int errflg = 0, hasSignal = 0, hasNode = 0, hasDate = 0, hasLoops=0, dateSize=14; 
   int r,i;
 
   struct sigaction act;
   memset (&act, '\0', sizeof(act));

   SeqNodeDataPtr  nodeDataPtr = NULL;
   SeqNameValuesPtr loopsArgsPtr = NULL;

   if (argc >= 6) {
      while ((c = getopt_long(argc, argv, short_opts, long_opts, &opt_index)) != -1) {
            switch(c) {
            case 'n':
               hasNode = 1;
               node = malloc( strlen( optarg ) + 1 ); 
               strcpy(node,optarg);
               printf("Node = %s \n", node);
               break;
            case 's':
               hasSignal = 1;
               signal = malloc( strlen( optarg ) + 1 ); 
               strcpy(signal,optarg);
               printf("Signal = %s \n", signal);
               break;
            case 'l':
               /* loops argument */
               hasLoops=1;
               loops = malloc( strlen( optarg ) + 1 );
               strcpy(loops,optarg);
               if( SeqLoops_parseArgs( &loopsArgsPtr, loops ) == -1 ) {
                    fprintf( stderr, "ERROR: Invalid loop arguments: %s\n", loops );
                    exit(1);
               }
               break;
            case 'm':
               message = malloc( strlen( optarg ) + 1 ); 
               strcpy(message,optarg);
               printf("Message = %s \n", message);
               break;
            case 'd':
               hasDate=1;
               datestamp = malloc( PADDED_DATE_LENGTH + 1 );
               strncpy(datestamp,optarg,PADDED_DATE_LENGTH);
               break;
            case 'e':
               seq_exp_home = strdup ( optarg );
               break;
            case 'v':
               SeqUtil_setTraceFlag( TRACE_LEVEL , TL_FULL_TRACE );
               SeqUtil_setTraceFlag( TF_TIMESTAMP , TF_ON );
               break;   
            case '?':
                 errflg++;
            }
      }

      if ( seq_exp_home == NULL ){
         seq_exp_home=getenv("SEQ_EXP_HOME");
      }
      SeqUtil_checkExpHome(seq_exp_home);

      if ( hasNode == 0 || hasSignal == 0 ) {
         fprintf (stderr,"Node and signal must be provided!\n");
         errflg++;
      }
      if (errflg) {
          printUsage();
          free(node);
          free(message);
          free(loops);
          free(signal);
          free(datestamp);
          exit(1);
      }

      /* register SIGALRM signal */
      act.sa_handler = &alarm_handler;
      act.sa_flags = 0;
      sigemptyset (&act.sa_mask);
      r = sigaction (SIGALRM, &act, NULL);
      if (r < 0) perror (__func__);

      if  (( datestamp == NULL ) && ( (tmpDate = getenv("SEQ_DATE")) != NULL ))  {
          datestamp = malloc( PADDED_DATE_LENGTH + 1 );
          strncpy(datestamp,tmpDate,PADDED_DATE_LENGTH);
      }

      if ( datestamp != NULL ) {
         i = strlen(datestamp);
         while ( i < PADDED_DATE_LENGTH ){
            datestamp[i++] = '0';
         }
         datestamp[PADDED_DATE_LENGTH] = '\0';
      }

      nodeDataPtr = nodeinfo( node, NI_SHOW_ALL, loopsArgsPtr, seq_exp_home, NULL, datestamp,NULL );
      if (hasLoops){
          SeqLoops_validateLoopArgs( nodeDataPtr, loopsArgsPtr );
      }

      nodelogger(nodeDataPtr->name,signal,nodeDataPtr->extension,message,nodeDataPtr->datestamp,seq_exp_home);
      free(node);
      free(message);
      free(loops);
      free(signal);
      free(datestamp);
      SeqNode_freeNode( nodeDataPtr );
      SeqUtil_unmapfiles();

  } else {
      printUsage();
      exit(1);
  }

  exit(0);
}

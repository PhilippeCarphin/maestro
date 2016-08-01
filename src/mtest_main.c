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
#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/tree.h>
#include <libxml/xpathInternals.h>
#include "ResourceVisitor.h"
#include "FlowVisitor.h"
#include "SeqUtil.h"
#include "SeqLoopsUtil.h"
#include "nodeinfo.h"
#include "getopt.h"
#include "SeqNode.h"
#include "XmlUtils.h"
#include "SeqNodeCensus.h"

static char * testDir = NULL;
int MLLServerConnectionFid=0;

/********************************************************************************
 * MAESTRO TEST FILE
 *
 * This file is intended as a place to do unit testing and experimentation
 * during development and bug solving in maestro.
 *
 * This file assumes that the executable is being run from the maestro directory
 * so that paths can be relative to that directory:
 *
 * testDir is the location to look in for whaterver files are being used for
 * these tests.
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
 * Creates an absolute path by appending the relative path to testDir, where
 * testDir = ${MAESTRO_REPO_LOCATION}/testDir/
 * This should be used for any paths so that the tests can be portable to
 * different users who keep their maestro stuff in different places.
********************************************************************************/
char * absolutePath(const char * relativePath)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() begin\n");
   char * absPath = (char *) malloc( strlen(testDir) + 1 + strlen(relativePath) + 1);
   sprintf( absPath, "%s%c%s", testDir,'/', relativePath);
   SeqUtil_TRACE(TL_FULL_TRACE, "absolutePath() end, returning %s\n", absPath);
   return absPath;
}


void header(const char * test){
   SeqUtil_TRACE(TL_CRITICAL, "\n=================== UNIT TEST FOR %s ===================\n",test);
}






void resource_keylist(SeqNodeDataPtr ndp, FILE * fp, int human_readable)
{
   /*
    * All keys exept the last one must be followed by a space
    * catchup
    * cpu
    * machine queue
    * memory
    * mpi
    * wallclock
    */

   if( human_readable ){
      fprintf(fp, "        .CATCHUP   = %d\n", ndp->catchup);
      fprintf(fp, "        .CPU       = %s\n", ndp->cpu);
      fprintf(fp, "        .QUEUE     = %s\n", ndp->queue);
      fprintf(fp, "        .MPI       = %d\n", ndp->mpi);
      fprintf(fp, "        .MEMORY    = %s\n", ndp->memory);
      fprintf(fp, "        .WALLCLOCK = %d\n", ndp->wallclock);
   } else {
      fprintf(fp,"{resources ",ndp->name);

      fprintf(fp, "{");
      fprintf(fp, "{CATCHUP %d} ",ndp->catchup);
      fprintf(fp, "{CPU %s} ",ndp->cpu);
      fprintf(fp, "{QUEUE %s} ",ndp->queue);
      fprintf(fp, "{MPI %d} ",ndp->mpi);
      fprintf(fp, "{MEMORY %s} ",ndp->memory);
      fprintf(fp, "{WALLCLOCK %d}",ndp->wallclock);
      fprintf(fp, "}");
      
      fprintf(fp, "}");
   }
}

void loop_keylist(SeqNodeDataPtr ndp, FILE *fp, int human_readable)
{
   char *start = SeqLoops_getLoopAttribute( ndp->data, "START" ),
        *end = SeqLoops_getLoopAttribute( ndp->data, "END" ),
        *step = SeqLoops_getLoopAttribute( ndp->data, "STEP" ),
        *set = SeqLoops_getLoopAttribute( ndp->data, "SET" ),
        *expression = SeqLoops_getLoopAttribute( ndp->data, "EXPRESSION" );

   /*
    * To be as light as possible, nodeinfo can be called with the filter
    * NI_RESOURCES_ONLY which only looks through the resource xml files.
    * Therefore a sure way of knowing if the nodes is a loop is to check if it
    * has loop information.
    */
   if(ndp->type != Loop)
   {
      return;
   }

   if( human_readable ){
      if( expression == NULL ){
         fprintf(fp, "        .START = %s\n", start);
         fprintf(fp, "        .END = %s\n", end);
         fprintf(fp, "        .STEP = %s\n", step);
         fprintf(fp, "        .SET = %s\n", set);
      } else {
         fprintf(fp, "        .EXPRESSION = %s\n", expression);
      }
   } else {
      /*
       * {loop {{START 8} {END 18} {STEP 2} {SET 2}}}
       */
      fprintf(fp, " {loop {");
      if( expression == NULL ){
         fprintf(fp, "{START %s} ", start );
         fprintf(fp, "{END %s} ", end );
         fprintf(fp, "{STEP %s} ", step );
         fprintf(fp, "{SET %s}", set );
      } else {
         fprintf(fp, "{EXPRESSION %s}", expression );
      }
      fprintf(fp, "}}");
   }

   free(start);
   free(end);
   free(step);
   free(set);
   free(expression);
}

void dependency_keylist(SeqNodeDataPtr ndp, FILE *fp, int human_readable)
{
   if( human_readable ){
      fprintf(fp, "        .dpename1 = %s\n", "depvalue1");
      fprintf(fp, "        .dpename2 = %s\n", "depvalue2");
   } else {
      fprintf(fp, "{depends ");
      fprintf(fp, "{{depname1 depvalue1} {depname2 depvalue2}}");
      fprintf(fp, "}");
   }
}

void node_to_keylist(SeqNodeDataPtr ndp,FILE *fp, int human_readable)
{
   /*
    * For the loop part, it is required that getFlowInfo be called so that the
    * ndp->type can be known.  If we want to do it without calling getFlowInfo
    * for performance reasons, then I can arrange that.  Simply check if there
    * is info there.  Instead of using node->type, we can just do if( start ==
    * NULL && expression == NULL ) then the node is not a loop.
    */
   if( human_readable ){
      fprintf(fp, "%s\n", ndp->name);
      fprintf(fp, "    .resources\n");
      resource_keylist(ndp,fp, human_readable);

      fprintf(fp, "    .depends\n");
      dependency_keylist(ndp,fp, human_readable);

      if( ndp->type == Loop ){
         fprintf(fp, "    .loop\n");
         loop_keylist(ndp,fp,human_readable);
      }
   } else {
      fprintf(fp, "%s {", ndp->name);

      resource_keylist(ndp,fp,human_readable);

      fprintf(fp, " ");
      dependency_keylist(ndp, fp,human_readable);

      fprintf(fp, " ");
      loop_keylist(ndp, fp, human_readable);

      fprintf(fp,"}");

   }
}

FILE *hr_output_file(const char *hr_filename)
{
   FILE *output_file = NULL;

   /*
    * Check for errors:
    * -Empty filename
    * -Unaccessible filename
    *
    * and replace hr_filename with fallback filename
    */

   output_file = fopen( hr_filename, "w" );

   return output_file;

}



/* #define _TESTING_ */


int write_db_file(const char *seq_exp_home, const char *hr_filename)
{
   /*
    * Open file for writing.  Do some error checks.  What are some errors that
    * could occur?  Could be stdout.  Following the logreader interface (not
    * Antoine Macia's implementation), I could output TSV ready stuff to STDOUT
    * and output more human readable stuff to an output file.
    *
    * For now, it's going to go to STDOUT since that is easy to pick catch in
    * the TCL part.
    */

   /* FILE *hr_output = NULL; */
   /* FILE *tcl_output = stdout; */


   /*
    * Get list of nodes in experiment
    */
   PathArgNodePtr nodeList = getNodeList(seq_exp_home);
   PathArgNode_printList( nodeList , TL_FULL_TRACE );

   /*
    * For each node in the list, write an entry in the file
    */
   SeqNodeDataPtr ndp = NULL;
   for_pap_list(itr,nodeList){
      ndp = nodeinfo(itr->path, NI_SHOW_ALL, NULL, seq_exp_home,
                                             NULL, NULL,itr->switch_args );
      node_to_keylist(ndp, stdout, 0);
      if(itr->nextPtr != NULL){
         putchar(' ');
      }

      SeqNode_freeNode(ndp);
   }


out_free:
   PathArgNode_deleteList(nodeList);
   return 0;
}

int runTests(const char * seq_exp_home, const char * node, const char * datestamp)
{
   SeqUtil_setTraceFlag(TRACE_LEVEL,TL_CRITICAL);
   /* int i; for(i = 0; i < 50; ++i) */
      write_db_file(seq_exp_home, "/home/ops/afsi/phc/node_database.txt");
   return 0;
}
int main ( int argc, char * argv[] )
{
   char * short_opts = "n:f:l:o:d:e:v";
   char *node = NULL, *seq_exp_home = NULL, *datestamp=NULL ;
   extern char *optarg;

   extern char *optarg;
   extern int   optind;
   struct       option long_opts[] =
   { /*  NAME        ,    has_arg       , flag  val(ID) */

      {"exp"         , required_argument,   0,     'e'},
      {"node"        , required_argument,   0,     'n'},
      {"loop-args"   , required_argument,   0,     'l'},
      {"datestamp"   , required_argument,   0,     'd'},
      {"outputfile"  , required_argument,   0,     'o'},
      {"filters"     , required_argument,   0,     'f'},
      {"verbose"     , no_argument      ,   0,     'v'},
      {NULL,0,0,0} /* End indicator */
   };
   int opt_index, c = 0;

   while ((c = getopt_long(argc, argv, short_opts, long_opts, &opt_index )) != -1) {
      switch(c) {
         case 'n':
            node = strdup(optarg);
            break;
         case 'e':
            seq_exp_home = strdup(optarg);
            break;
         case 'd':
            datestamp = strdup(optarg);
            break;
         case '?':
            exit(1);
      }
   }

   SeqUtil_setTraceFlag( TRACE_LEVEL , TL_FULL_TRACE );

   const char * PWD = getenv("PWD");
   /* Check that the path PWD ends with maestro.  It's the best we can do to
    * make sure that mtest is being run from the right place. */
   const char * p = PWD;
   while(*p++ != 0 );
   while(*(p-1) != '/') --p;
#if 0
   if( strcmp(p,"maestro") != 0 ){
      SeqUtil_TRACE(TL_FULL_TRACE, "\
Main function for doing tests, please run this from the maestro directory so\n\
that the location of the test files may be known.  Eg by doing \n\
   'make install; mtest'\n\
or\n\
   'make; ./src/mtest\n\
from the maestro directory.\n");
      exit(1);
   }

   char * suffix = "/src/testDir";
   testDir = (char *) malloc( sizeof(char) * (strlen(PWD) + strlen(suffix) + 1));
   sprintf( testDir, "%s%s" , PWD, suffix);

   /* puts ( testDir ); */
   /* seq_exp_home = strdup("/home/ops/afsi/phc/Documents/Experiences/sample/"); */
#endif
   seq_exp_home = strdup("/home/ops/afsi/phc/Documents/Experiences/sample/");
   /* seq_exp_home = strdup("/home/ops/afsi/phc/Documents/Experiences/HelloWorldPhil/"); */
   /* seq_exp_home = strdup("/home/ops/afsi/phc/Documents/Experiences/bug6268_switch"); */
   runTests(seq_exp_home,node,datestamp);

   free(node);
   free(seq_exp_home);
   free(datestamp);
   return 0;
}









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
#include "nodeinfo.h"
#include "getopt.h"
#include "SeqNode.h"
#include "XmlUtils.h"
#include <errno.h>

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

FlowVisitorPtr createTestFlowVisitor( const char * xmlFile, const char * defFile)
{
   FlowVisitorPtr fv = (FlowVisitorPtr) malloc(sizeof(FlowVisitor));
   /* Flow_changeXmlFile(fv,xmlFile); */
   fv->doc = XmlUtils_getdoc(xmlFile);
   if(fv->doc == NULL) raiseError("Something's wrong with you path or your xmlFile bro\n");
   fv->context = xmlXPathNewContext(fv->doc);
   return fv;
}




void header(const char * test){
   SeqUtil_TRACE(TL_CRITICAL, "\n=================== UNIT TEST FOR %s ===================\n",test);
}

char * get_script_output(const char *script_path, size_t buffer_size)
{
   /* Maybe check that we have permission to run the script befor continuing */

   /* Create a pipe */
   int switch_script_fd[2];
   if(pipe(switch_script_fd) == -1){
      perror("pipe");
      exit(1);
   }

   /* Fork the process */
   pid_t pid = fork();
   if (pid == -1){
      perror("fork");
      exit(1);
   }

   /* Code for the child : change STDOUT to the pipe entrance */
   if (pid == 0){
       /* Copy the file descriptor switch_script_fd[1] into STDOUT_FILENO. */
      while ((dup2(switch_script_fd[1], STDOUT_FILENO) == -1)
               && (errno == EINTR));
      /* Now, stuff sent to SDTOUT will go to the pipe, so we don't need the
       * pipe entrance fd */
      close(switch_script_fd[1]);

      /* Since we're in the child, we also don't need the pipe exit fd */
      close(switch_script_fd[0]);

      system(script_path);
      exit(0);
   }

   /* Parent process : capture the output into a buffer */
   close(switch_script_fd[1]);
   char buffer[buffer_size];
   ssize_t totalCount = 0;
   while(1){
      ssize_t count = read(switch_script_fd[0],&(buffer[totalCount]),sizeof(buffer) - totalCount);
      if( count == -1 ){
         if( errno == EINTR){
            continue;
         }else{
            perror("read");
            exit(1);
         }
      } else if (count == 0) {
         break;
      } else {
         totalCount += count;
         buffer[totalCount] = 0;
      }
   }
   close(switch_script_fd[0]);
   wait(0);
   /* Equivalent of 'return strdup(buffer);'*/
   return strdup(buffer);
}

void test_genSwitch()
{
   const char * test_flow = absolutePath("gen_switch/gen_switch_flow.xml");
   SeqNodeDataPtr ndp = SeqNode_createNode("PHIL");

   /* Create a FlowVisitor by specifying an xmlFile instead of the usual way of
    * specifying the expHome since there is no home */
   FlowVisitorPtr fv = createTestFlowVisitor(test_flow,NULL);

   /* Get the flow visitor to the switch */
   int isFirst = 1;
   Flow_doNodeQuery(fv,"my_module", isFirst);
   isFirst = 0;
   Flow_doNodeQuery(fv,"my_gen_switch", isFirst);

   /* Flow_parseSwitchAttributes() */
   {
      const char * switchType = xmlGetProp(fv->context->node, "type");
      SeqUtil_TRACE(TL_FULL_TRACE, "swithch type = %s\n",switchType);

      /* Get the path of the swithc */
      /* containerTaskPath( const char * expHome, const char * nodePath) */
      {
         /* From the path fv->currentFlowNode and the experiment home, construct
          * the path to the container.tsk of the switch */
      } const char * containerTaskPath = absolutePath("gen_switch/container.tsk");

      SeqUtil_TRACE(TL_FULL_TRACE, "%s\n", containerTaskPath);
      /* Take script path, return a string containing output */
      const char * output_of_script = NULL;
      output_of_script = get_script_output(containerTaskPath, SEQ_MAXFIELD);
      SeqUtil_TRACE(TL_FULL_TRACE, "output_of_script=%s\n",output_of_script);
   }






}

int runTests(const char * seq_exp_home, const char * node, const char * datestamp)
{
   test_genSwitch();

   SeqUtil_TRACE(TL_CRITICAL, "============== ALL TESTS HAVE PASSED =====================\n");
   return 0;
}

int main ( int argc, char * argv[] )
{
   char * short_opts = "n:f:l:o:d:e:v";
   char *node = NULL, *seq_exp_home = NULL, *outputFile=NULL, *datestamp=NULL ;
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

   puts ( testDir );

   runTests(seq_exp_home,node,datestamp);

   free(node);
   free(seq_exp_home);
   free(datestamp);
   return 0;
}









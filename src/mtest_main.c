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
#include <stdarg.h>
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
      raiseError("get_script_output() could not create pipe\n");
   }

   /* Fork the process */
   pid_t pid = fork();
   if (pid == -1){
      perror("fork");
      raiseError("get_script_output() could not create fork\n");
   }

   /* Code for the child : change STDOUT to the pipe entrance */
   if (pid == 0){
      /*
       * Copy the file descriptor switch_script_fd[1] into STDOUT_FILENO.
       * Note that we could also redirect STDERR to the pipe by doing the same
       * kind of thing
       */
      while ((dup2(switch_script_fd[1], STDOUT_FILENO) == -1)
               && (errno == EINTR));
      /*
       * As I understand it, there is a file descriptor table fd_table not
       * unlike an array that has pointers to opaque data structures that hold
       * the actual information.  fd_table[STDOUT_FILENO] points to this
       * structure for STDOUT.  When we call dup2, the data of the pipe entry is
       * copied at the location pointed to by fd_table[STDOUT_FILENO].
       * Something like that; I would need to re-read that section of the Linux
       * Programming Interface
       *
       * We can then close the pipe entrance fd because we 
       */


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
            raiseError("get_script_output() : parent : Error reading from pipe\n");
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

   return strdup(buffer);
}

const char *popen_get_script_output(const char * script_path, size_t buffer_size)
{
   FILE *fp;
   int status;
   char buffer[buffer_size];
   int count = 0, totalCount = 0;

   fp = popen(script_path, "r");
   if( fp == NULL )
      goto err;

   while (fgets( &(buffer[totalCount]), buffer_size - totalCount, fp) != NULL){
      /* The one where I explicitely create the pipe seems like it's better
       * since I get the byte count for each read, instead of having to
       * redundantly call strlen(); */
      totalCount = strlen(buffer);
   }

   status = pclose(fp);
   if( status == -1 ){
      goto err;
   } else {
      ;/* should inspect status according to the documentation */
   }

   return strdup(buffer);

err:
   return NULL;
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

      /*
       * That takes care of the reading of the script part.  Now back to
       * implementing the desired behavior.  We have to look at the original
       * function.  This function needs to be divided so that we have one part
       * that doesn't depend on the switch value, and one part that does.
       *
       * Lets inspect the actual version of Flow_parseSwitchAttributes().  Then
       * we can break it up, into two functions: one that takes the info from
       * the SWITCH node which will be called for both types of switches, then
       * one set of two functions: one that will be called for generic switches,
       * and the other that will be called for generic switches
       *
       * This is done in a flow-chart.
       *
       */
   }
}

int test_SLGLCEIR()
{
   SeqNodeDataPtr ndp = SeqNode_createNode("PHIL");
   SeqNode_setSeqExpHome(ndp,"Inigo_montoya");
   SeqNode_addNumLoop(ndp,"loop1","10","2","1","20","");
   SeqNode_addNumLoop(ndp,"loop2","11","2","1","21","");
   const char * index = "loop1=8,loop2=13";
   LISTNODEPTR ext_list = SeqLoops_getLoopContainerExtensionsInReverse(ndp,index);
   SeqUtil_TRACE(TL_FULL_TRACE,"================================\n");
   SeqListNode_printList(ext_list);
   SeqUtil_TRACE(TL_FULL_TRACE,"\n");
   return 0;
}

struct streets {
   char * philippe;
   char * gilles;
   char * marie_eve;
   char * thomas;
   char * dominic;
   char * francois;
   char * jean;
   char * benoit;
   char * benny;
   char * bennito;
};

int test_SeqNameValues_lookup()
{
   SeqNameValuesPtr nvp = NULL;
   SeqNameValues_insertItem(&nvp, "Philippe", "de Poutrincourt");
   SeqNameValues_insertItem(&nvp, "Gilles", "Jean-Bourdon");
   SeqNameValues_insertItem(&nvp, "Marie-Eve", "rue Cadieux");
   SeqNameValues_insertItem(&nvp, "Thomas", "Henri-Bourassa");
   SeqNameValues_insertItem(&nvp, "Dominic", "Dorval");
   SeqNameValues_insertItem(&nvp, "Francois", "Montreal");
   SeqNameValues_insertItem(&nvp, "Jean", "Beaubien");
   SeqNameValues_insertItem(&nvp, "Benoit", "Jarry");
   SeqNameValues_insertItem(&nvp, "Benny", "Jarry");
   SeqNameValues_insertItem(&nvp, "Bennito", "Jarry");

   struct streets my_streets_auto = {"de Poutrincourt", "Jean-Bourdon", "rue Cadieux", "Henri-Bourassa", "Des Sources", "Jean-Bourdon","Beaubien","Jarry"};

   struct streets *my_streets = &my_streets_auto;
   char * currentStreet;
   int i = 0;

#define MAX 10000000
   SeqUtil_setTraceFlag(TF_TIMESTAMP,TF_ON);
   SeqUtil_TRACE(TL_FULL_TRACE, "Start nvp\n");
   for( i = 0; i < MAX; ++i){
      currentStreet = SeqNameValues_getValue( nvp, "Philippe");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Gilles");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Marie-Eve");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Thomas");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Dominic");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Francois");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Jean");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Benoit");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Benny");free(currentStreet);
      currentStreet = SeqNameValues_getValue( nvp, "Bennito");free(currentStreet);
      /* programmer error (typo) : still compiles, and while you're on call,
       * they're going to wake you up in the middle of the night because this
       * will make a job abort, also, the free() is not going to catch it for
       * you because free(NULL) is OK */
      currentStreet = SeqNameValues_getValue( nvp, "Francous");free(currentStreet);
   }
   SeqUtil_TRACE(TL_FULL_TRACE, "end nvp\n");

   SeqUtil_TRACE(TL_FULL_TRACE, "Start struct\n");
   for( i = 0; i < MAX; ++i){
      currentStreet = my_streets->philippe;
      currentStreet = my_streets->gilles;
      currentStreet = my_streets->marie_eve;
      currentStreet = my_streets->thomas;
      currentStreet = my_streets->dominic;
      currentStreet = my_streets->francois;
      currentStreet = my_streets->jean;
      currentStreet = my_streets->benoit;
      currentStreet = my_streets->benny;
      currentStreet = my_streets->bennito;
      /* programmer error (typo) : caught at compilation.  Enjoy your nights of
       * undisturbed sleep :).
       * The line has to be commented because it would prevent the test from
       * compiling.*/
      /* currentStreet = my_streets->francous; */
   }
   SeqUtil_TRACE(TL_FULL_TRACE, "end struct (100 times faster on Phil's machine\n");
   getchar();
   SeqUtil_TRACE(TL_FULL_TRACE, "\n\
   This test doesn't give the whole picture, lookup in a linked list is O(n)\n\
whereas it is O(1) in the case of looking up a field in a struct.\n\
\n\
And really, I don't care ont bit about performance.  Even if performance were the\n\
same, like if we were using a hashmap, the problem is ROBUSTNESS, MAINTAINABILITY\n\
and EXTENSIBILITY.\n\
\n\
ROBUSTNESS: Typoes don't generate compilation errors. Nuff said.\n\
MAINTAINABILITY and EXTENSIBILITY: Take a look at SeqNode_addNodeDependency() and\n\
how many arguments it takes.  Not only that, take a look at all the subroutines\n\
that take dep_exp, dep_node, dep_this, dep_that.  If I want to add dep_color\n\
I have to modify a whole bunch of function declarations.\n\
\n\
ROBUTSTNESS(again): Mixing up argument order.  All these are char* so if I change\n\
mix up the order of arguments, the compiler won't mind.  However if I do\n\
\n\
   someFunc( dep_struct, nodeDataPtr );\n\
\n\
with a function whose declaration is\n\
\n\
   someFunc( SeqNodeDataPtr ndp, struct DepData dep);\n\
\n\
guess what: compilation error! (that's assuming that I have declared the function\n\
before using it, which SHOULD ALWAYS BE THE CASE and in fact, the compiler should\n\
be set to abort compilation when encountering an undeclared function\n\
   -Werror=implicit-function-declaration)\n\
\n\
good luck finding why the program behaves weirdly when you switch valid_hour and\n\
hour in the argument list of SeqNode_addNodeDependency.\n\
\n");
   SeqNameValues_deleteWholeList(&nvp);
}

int runTests(const char * seq_exp_home, const char * node, const char * datestamp)
{
   /* test_genSwitch(); */
   /* test_SLGLCEIR(); */
   test_SeqNameValues_lookup();

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









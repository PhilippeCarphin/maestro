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


LISTNODEPTR parseFlowTree_internal(FlowVisitorPtr fv, LISTNODEPTR * list_head,const char * basePath, int depth);
LISTNODEPTR parseFlowTree(const char * seq_exp_home)
{
   LISTNODEPTR list_head = NULL;
   FlowVisitorPtr fv = Flow_newVisitor(seq_exp_home);

   const char * basePath = (const char *) xmlGetProp(fv->context->node, (const xmlChar *)"name");
   SeqListNode_pushFront(&list_head, basePath);

   parseFlowTree_internal(fv, &list_head,basePath, 0);

   return list_head;

}

void indent(int depth)
{
   int i;
   for(i = depth; i--;)
      fprintf(stderr, "    ");
}

LISTNODEPTR parseFlowTree_internal(FlowVisitorPtr fv, LISTNODEPTR * list_head, const char * basePath, int depth)
{
   indent(depth);SeqUtil_TRACE(TL_CRITICAL, "============== ParseFlowTree_internal depth %d BEGIN =================\n", depth);

   /* Our father who art in heaven, please forgive us our trespasses (making
    * this ugly ass query which amounts to saying "all children except SUBMITS")
    * */
   xmlXPathObjectPtr results = XmlUtils_getnodeset("(child::FAMILY|child::TASK|child::SWITCH|child::SWITCH_ITEM|child::MODULE|child::LOOP|child::NPASS_TASK|child::FOR_EACH)", fv->context);


   for_results( xmlNode, results ){

      const char * name = (const char *)xmlGetProp( xmlNode, (const xmlChar *)"name");

      char query[SEQ_MAXFIELD] = {0};
      /* Look for an XML node that has an attribute "name" whose value is equal
       * to that of name
       * */
      xmlNodePtr node = xmlNode;

      indent(depth);SeqUtil_TRACE(TL_CRITICAL, "Current iterator node : %s\n", xmlNode->name);

      if( strcmp(node->name, "TASK") == 0 || strcmp(node->name, "NPASS_TASK") == 0){
         char path[SEQ_MAXFIELD] = {0};
         sprintf( path, "%s/%s", basePath,name);
         SeqListNode_pushFront(list_head, path);
      }

      if( strcmp(node->name, "MODULE") == 0){
         char path[SEQ_MAXFIELD] = {0};
         sprintf( path, "%s/%s", basePath,name);
         SeqListNode_pushFront(list_head, path);
         Flow_changeModule(fv, (const char *) name);
         parseFlowTree_internal(fv, list_head,path, depth+1);
         Flow_restoreContext(fv);
      }

      if( strcmp(node->name, "LOOP") == 0 || strcmp(node->name, "FAMILY") == 0){
         char path[SEQ_MAXFIELD] = {0};
         sprintf( path, "%s/%s", basePath,name);
         SeqListNode_pushFront(list_head, path);
         xmlNodePtr previousNode = fv->context->node;
         fv->context->node = node;
         parseFlowTree_internal(fv, list_head,path,depth+1);
         fv->context->node = previousNode;
      }

      if( strcmp(node->name, "SWITCH") == 0 ){
         char path[SEQ_MAXFIELD] = {0};
         sprintf( path, "%s/%s", basePath,name);
         SeqListNode_pushFront(list_head, path);
         indent(depth);SeqUtil_TRACE(TL_CRITICAL, "++++ DOING SWITCH BEGIN +++++\n");
         xmlNodePtr previousNode = fv->context->node;
         fv->context->node = node;
         parseFlowTree_internal(fv, list_head,path,depth+1);
         fv->context->node = previousNode;
         indent(depth);SeqUtil_TRACE(TL_CRITICAL, "++++ DOING SWITCH END +++++\n");
      }

      if( strcmp(node->name, "SWITCH_ITEM") == 0 ){
         indent(depth);SeqUtil_TRACE(TL_CRITICAL, "++++ DOING SWITCH_ITEM BEGIN +++++\n");
         xmlNodePtr previousNode = fv->context->node;
         fv->context->node = node;
         /* SeqListNode_pushFront( list_head, "COCK" ); */
         parseFlowTree_internal(fv, list_head,basePath, depth+1);
         fv->context->node = previousNode;
         indent(depth);SeqUtil_TRACE(TL_CRITICAL, "++++ DOING SWITCH_ITEM END +++++\n");
      }


   }
   indent(depth);SeqUtil_TRACE(TL_CRITICAL, "============== ParseFlowTree_internal depth %d END =================\n", depth);
}

int runTests(const char * seq_exp_home, const char * node, const char * datestamp)
{

   SeqUtil_setTraceFlag(TRACE_LEVEL, TL_CRITICAL);
   LISTNODEPTR list_head = parseFlowTree(seq_exp_home);

   SeqUtil_TRACE(TL_FULL_TRACE, "===============================================================\n");
   SeqUtil_setTraceFlag(TRACE_LEVEL, TL_FULL_TRACE);
   SeqListNode_printList(list_head);



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
   /* seq_exp_home = strdup("/home/ops/afsi/phc/Documents/Experiences/sample/"); */
   seq_exp_home = strdup("/home/ops/afsi/phc/Documents/Experiences/bug6268_switch/");

   runTests(seq_exp_home,node,datestamp);

   free(node);
   free(seq_exp_home);
   free(datestamp);
   return 0;
}









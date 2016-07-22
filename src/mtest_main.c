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


/********************************************************************************
 *
********************************************************************************/
typedef struct _PathArgNode{
   struct _PathArgNode *nextPtr;
   const char * path;
   const char * switch_args;
} PathArgNode;

typedef PathArgNode *PathArgNodePtr;


void parseFlowTree_internal(FlowVisitorPtr fv, PathArgNodePtr *lp,
                            const char * basePath, const char * baseSwitchArgs,
                                                                     int depth);

/********************************************************************************
 *
********************************************************************************/
int PathArgNode_pushFront(PathArgNodePtr *list_head, const char *path, const char *switch_args)
{
   PathArgNodePtr newNode = NULL;
   if( (newNode = malloc(sizeof *newNode)) == NULL ){
      SeqUtil_TRACE(TL_CRITICAL,"PathArgPair_pushFront() No memory available.\n");
      return 1;
   }
   newNode->path = strdup(path);
   newNode->switch_args = strdup(switch_args);
   newNode->nextPtr = *list_head;

   *list_head = newNode;
   return 0;
}

/********************************************************************************
 *
********************************************************************************/
int PathArgNode_deleteList(PathArgNodePtr *list_head)
{
   if(*list_head == NULL )
      return 0;

   PathArgNodePtr current = *list_head, tmp_next = *list_head;

   while( current != NULL ){
      tmp_next = current->nextPtr;
      free(current->path);
      free(current->switch_args);
      free(current);
      current = tmp_next;
   }
   *list_head = NULL;
   return 0;
}

/********************************************************************************
 *
********************************************************************************/
void PathArgNode_printList(PathArgNodePtr list_head)
{
   for_list(itr,list_head){
      PathArgNodePtr pap_itr = (PathArgNodePtr) itr;
      printf("%s {%s}\n", pap_itr->path, pap_itr->switch_args);
   }
}

/********************************************************************************
 *
********************************************************************************/
PathArgNodePtr parseFlowTree(const char * seq_exp_home)
{
   PathArgNodePtr pap = NULL;
   FlowVisitorPtr fv = Flow_newVisitor(NULL,seq_exp_home,NULL);

   const char * basePath = (const char *) xmlGetProp(fv->context->node,
                                                      (const xmlChar *)"name");

   /*
    * Base step of recursion
    */
   PathArgNode_pushFront(&pap, basePath, "" );

   /*
    * Start recursion
    */
   parseFlowTree_internal(fv, &pap ,basePath,"", 0);

out_free:
   free((char*)basePath);
   Flow_deleteVisitor(fv);
   return pap;
}

/********************************************************************************
 * Recursive subroutine for container nodes.  we append the xmlNode's name to
 * the basePath to construct the path of the node and we continue the recursion.
********************************************************************************/
void pft_int_container(FlowVisitorPtr fv, PathArgNode *pathArgList ,
                        const char *basePath,const char *baseSwitchArgs,
                        int depth,xmlNodePtr xmlNode)
{
   char path[SEQ_MAXFIELD];
   const char * container_name = (const char *)xmlGetProp( xmlNode, (const xmlChar *)"name");

   /*
    * Append current node name to basePath and add list entry
    */
   sprintf( path, "%s/%s", basePath,container_name);
   PathArgNode_pushFront( pathArgList, path, baseSwitchArgs );

   /*
    * Continue recursion
    */
   parseFlowTree_internal(fv, pathArgList ,path,baseSwitchArgs,depth+1);

out_free:
   free((char*)container_name);
}

/********************************************************************************
 *
********************************************************************************/
void pft_int_module(FlowVisitorPtr fv, PathArgNode *pathArgList,
                        const char *basePath,const char *baseSwitchArgs,
                        int depth,xmlNodePtr xmlNode)
{
   char path[SEQ_MAXFIELD];
   const char * module_name = (const char *)xmlGetProp( xmlNode, (const xmlChar *)"name");

   /*
    * Append current node name to basePath and add list entry
    */
   sprintf( path, "%s/%s", basePath,module_name);
   PathArgNode_pushFront( pathArgList, path, baseSwitchArgs );

   /*
    * Continue recursion
    */
   Flow_changeModule(fv, module_name);
   parseFlowTree_internal(fv, pathArgList ,path,baseSwitchArgs, depth+1);
   Flow_restoreContext(fv);

out_free:
   free((char*)module_name);
}

/********************************************************************************
 *
********************************************************************************/
void pft_int_task(FlowVisitorPtr fv, PathArgNode *pathArgList,
                        const char *basePath,const char *baseSwitchArgs,
                        int depth,xmlNodePtr xmlNode)
{
   char path[SEQ_MAXFIELD];
   const char * name = (const char *)xmlGetProp( xmlNode, (const xmlChar *)"name");

   /*
    * Append current node name to basePath and add list entry
    */
   sprintf( path, "%s/%s", basePath,name);
   PathArgNode_pushFront( pathArgList , path, baseSwitchArgs );

   /*
    * Recursion does ends with Task or NpassTask nodes
    */
}

/********************************************************************************
 *
********************************************************************************/
void pft_int_switch_item(FlowVisitorPtr fv, PathArgNode *pathArgList,
                        const char *basePath,const char *baseSwitchArgs,
                        int depth,xmlNodePtr xmlNode)
{
   char switch_args[SEQ_MAXFIELD];
   const char * switch_item_name = xmlGetProp(xmlNode, (const xmlChar *)"name");
   const char * switch_name = SeqUtil_getPathLeaf(basePath);

   /*
    * Append current switch_item_name=first_switch_arg' to baseSwitchArgs
    */
   char * first_comma = strstr(switch_item_name,",");
   if( first_comma != NULL ) *first_comma = 0;
   sprintf( switch_args, "%s%s=%s,",baseSwitchArgs,switch_name,switch_item_name );

   /*
    * Continue recursion
    */
   parseFlowTree_internal(fv, pathArgList ,basePath,switch_args, depth+1);

out:
   free((char*)switch_item_name);
   free((char*)switch_name);
}

/********************************************************************************
 * Main internal recursive routine for parsing the flow tree of an experiment.
 * It works in two steps since the recursive step is different depending on the
 * type of xmlNode encountered.
 * We get the children of the current xmlNode, then we redirect the recursion
 * through one of the pft_int_${nodeType}() functions, and these functions
 * continue the recursion.
********************************************************************************/
void parseFlowTree_internal(FlowVisitorPtr fv, PathArgNodePtr *lp,
                            const char * basePath, const char * baseSwitchArgs,
                                                                     int depth)
{
   /*
    * Oh heavenly Father, I pray to thee to forgive me for this inelegant query
    * which amounts to saying "all children except SUBMITS".  There has to be a
    * way of saying something like child::!SUBMITS or something.
    */
   xmlXPathObjectPtr results = XmlUtils_getnodeset("(child::FAMILY|child::TASK\
                                                     |child::SWITCH|child::SWITCH_ITEM\
                                                     |child::MODULE|child::LOOP\
                                                     |child::NPASS_TASK|child::FOR_EACH)"
                                                      , fv->context);
   for_results( xmlNode, results ){
      xmlNodePtr previousNode = fv->context->node;
      fv->context->node = xmlNode;

      if( strcmp(xmlNode->name, "TASK") == 0 || strcmp(xmlNode->name, "NPASS_TASK") == 0)
      {
         pft_int_task(fv,lp,basePath,baseSwitchArgs,depth,xmlNode);
      }
      else if( strcmp(xmlNode->name, "MODULE") == 0)
      {
         pft_int_module(fv,lp,basePath,baseSwitchArgs,depth,xmlNode);
      }
      else if(   strcmp(xmlNode->name, "LOOP") == 0
                || strcmp(xmlNode->name, "FAMILY") == 0
                || strcmp(xmlNode->name, "SWITCH") == 0)
      {
         pft_int_container(fv,lp,basePath,baseSwitchArgs,depth,xmlNode);
      }
      else if( strcmp(xmlNode->name, "SWITCH_ITEM") == 0 )
      {
         pft_int_switch_item(fv,lp,basePath,baseSwitchArgs,depth,xmlNode);
      }

      fv->context->node = previousNode;
   }

   xmlXPathFreeObject(results);
}

#define COPY_TO_LINE(dst,src,len)                                              \
   memcpy((dst),(src),(len)=strlen((src)));                                    \
   (dst)+=(len);                                                               \
   *(dst)++ = '\t';                                                            \

#define LONG_LINE 10000
const char *node_to_line(SeqNodeDataPtr ndp)
{
   static char buffer[LONG_LINE];
   static char small_buffer[50];

   char *dst = buffer;
   size_t len;



      COPY_TO_LINE(dst,ndp->name,len)

      char *type_str = SeqNode_getTypeString(ndp->type);
      COPY_TO_LINE(dst,type_str,len)

      COPY_TO_LINE(dst,ndp->cpu,len)

      sprintf(small_buffer,"%d",ndp->mpi);
      COPY_TO_LINE(dst,small_buffer,len)

      /* COPY_TO_LINE(dst,ndp-> */

      /* ET CETERA */

   *dst = 0;

   return (const char *)buffer;
}



/*
 * SOME NOTES ABOUT THIS TEST:
 * This test was made in another commit to develop an algorithm for getting the
 * list of all the nodes in an experiment.  I include it here as a means to test
 * the Flow_changeModule() function that uses a stack of xmlXPathContextPtr.
 *
 * This algorithm was going to be used for bug4689 but I ended up having to do
 * too many hackish things for my liking.  Therefore I'm going to wait until
 * Dominic gets back from vacation and discuss things like changing the desired
 * behavior so that it can be implemented with good design/coding practices.
 *
 * The root of the hackishness is switches, and the starting hack is to put
 * switch item names in square brackets.  As I worked on generic switches
 * (bug7312) I noticed that I hadn't thought about using loop_args.  So maybe
 * instead of weird hackish paths, we could use a (path,loop_args) pair as
 * entries in our 'node census'.
 */



int runTests(const char * seq_exp_home, const char * node, const char * datestamp)
{

#ifdef MANY_TIMES
   int i = 0;
   for( i = 0; i < 100 ; i++){
#endif
   SeqUtil_setTraceFlag(TRACE_LEVEL, TL_CRITICAL);
   PathArgNodePtr lp = parseFlowTree(seq_exp_home);

   SeqUtil_setTraceFlag(TRACE_LEVEL, TL_FULL_TRACE);
   /* SeqUtil_TRACE(TL_FULL_TRACE, "===============================================================\nNote that this test is dependent on an experiment that is not in the test directory.\n\n"); */
   SeqUtil_setTraceFlag(TRACE_LEVEL, TL_FULL_TRACE);
   SeqListNode_reverseList(&lp);
   /* printListWithLinefeed(lp->paths,TL_FULL_TRACE); */
   PathArgNode_printList(lp);
   getchar();
#if 1
   /* SeqUtil_setTraceFlag(TRACE_LEVEL, TL_CRITICAL); */
   SeqNodeDataPtr ndp = NULL;
   for_list(itr,lp){
      /*
       * Some offset manipulation trickery, if you're not 100% sure of how this
       * works, just don't do it! I can iterate over a LISTNODEPTR list the same
       * way as with a PathArgNodePtr because the nextPtr of both structs is the
       * first member, so ->nextPtr adds the same offset. If you don't know how
       * the compiler translates the instruction ptr = current->field to
       * assembler code, forget about this or go learn it.
       *
       * In fact, this isn't trickery, this is just advanced.
       */
      PathArgNodePtr pap_itr = (PathArgNodePtr) itr;

      SeqUtil_TRACE(TL_FULL_TRACE,"calling nodeinfo with path=%s, switch_args=%s\n",
                                    pap_itr->path, pap_itr->switch_args);

      ndp = nodeinfo(pap_itr->path, NI_SHOW_ALL, NULL, seq_exp_home,
                                          NULL, NULL,pap_itr->switch_args );
      SeqNode_printNode(ndp,NI_SHOW_ALL,NULL);
      getchar();
      /* SeqUtil_TRACE(TL_CRITICAL, "%s\n", node_to_line(ndp)); */

      SeqNode_freeNode(ndp);

      /* getchar(); */
   }
#endif
   PathArgNode_deleteList(&lp);
#ifdef MANY_TIMES
   }
#endif
   printf("DONE\n");

   SeqUtil_TRACE(TL_CRITICAL, "============== ALL TESTS HAVE PASSED =====================\n");
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

   /* seq_exp_home = strdup("/home/ops/afsi/phc/Documents/Experiences/sample/"); */
   seq_exp_home = strdup("/home/ops/afsi/phc/Documents/Experiences/bug6268_switch");
   runTests(seq_exp_home,node,datestamp);

   free(node);
   free(seq_exp_home);
   free(datestamp);
   return 0;
}









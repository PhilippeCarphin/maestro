#include <stdlib.h>
#include <string.h>
#include "SeqUtil.h"
#include "XmlUtils.h"
#include "SeqListNode.h"
#include "SeqNode.h"
#include "nodeinfo.h"
#include "FlowVisitor.h"
#include "nodeinfo_db.h"
#define writeTab(fp) (fprintf((fp),"\t"))
/*******************************************************************************
 *
*******************************************************************************/
const char * nodeDataPtr_to_info_line(const char *expHome, const char *nodePath, FILE *fp)
{
   SeqNodeDataPtr ndp = nodeinfo(nodePath, "all", NULL,expHome,NULL,NULL);
   /* Write nodePath to file */
   fprintf(fp,nodePath);

   /* Write separator to file */
   fprintf(fp,"\t");

   /* Write number of CPU's to file */
   fprintf(fp,ndp->cpu);

   /* Write separator to file */

   /* ... */

   /* Write linebreak to file */
   fprintf(fp,"\n");

   return NULL;

}


#if 0
/*******************************************************************************
 *
*******************************************************************************/
const char * path_to_info_line(const char * expHome, const char * path)
{
   SeqNodeDataPtr node = nodeinfo(path, "all", NULL,expHome,NULL,NULL);
   return nodeDataPtr_to_info_line(node);
}
#endif

#define for_list(iterator, list_head) \
   LISTNODEPTR iterator;\
   for( iterator = list_head; iterator != NULL; iterator = iterator->nextPtr)


int nodeList_to_infoFile(LISTNODEPTR path_list, const char *expHome,
                           const char * filePath)
{
   /* Open a file */
   FILE * fp = fopen(filePath,"w");

   for_list(nodePath, path_list){
      nodeDataPtr_to_info_line(expHome,nodePath->data,fp);
   }

   fclose(fp);
   return 0;

}



/*******************************************************************************
 * Creates a list of all node paths of the target experiment specified by
 * seq_exp_home.  This routine calls parseFlowTree_internal which does a depth
 * first search through all the nodes of the experiment by recursion.
*******************************************************************************/
LISTNODEPTR parseFlowTree(const char * seq_exp_home)
{
   LISTNODEPTR list_head = NULL;
   FlowVisitorPtr fv = Flow_newVisitor(seq_exp_home);

   const char * basePath = (const char *) xmlGetProp(fv->context->node,
                                                      (const xmlChar *)"name");
   SeqListNode_pushFront(&list_head, basePath);

   parseFlowTree_internal(fv, &list_head,basePath, 0);

   free((char*)basePath);
   Flow_deleteVisitor(fv);
   return list_head;

}

/*******************************************************************************
 * Internal routine for parseFlowTree().  The routine looks for all children
 * nodes of the current node of the FlowVisitor, adds their paths to the list
 * and calls itself on their children recursively.
*******************************************************************************/
void parseFlowTree_internal(FlowVisitorPtr fv, LISTNODEPTR * list_head,
                                    const char * basePath, int depth)
{
   /*
    * Our father who art in heaven, please forgive us our trespasses (making
    * this ugly ass query which amounts to saying "all children except SUBMITS")
    */
   xmlXPathObjectPtr results =
   XmlUtils_getnodeset("(child::FAMILY|child::TASK|child::SWITCH\
                          |child::SWITCH_ITEM|child::MODULE|child::LOOP\
                          |child::NPASS_TASK|child::FOR_EACH)" , fv->context);

   for_results( xmlNode, results ){
      const char * name = (const char *)xmlGetProp( xmlNode, (const xmlChar *)"name");
      xmlNodePtr node = xmlNode;

      if( strcmp(node->name, "TASK") == 0 || strcmp(node->name, "NPASS_TASK") == 0){
         char path[SEQ_MAXFIELD] = {0};
         sprintf( path, "%s/%s", basePath,name);
         SeqListNode_pushFront(list_head, path);
      } else if( strcmp(node->name, "MODULE") == 0){
         char path[SEQ_MAXFIELD] = {0};
         sprintf( path, "%s/%s", basePath,name);
         SeqListNode_pushFront(list_head, path);
         Flow_changeModule(fv, (const char *) name);
         parseFlowTree_internal(fv, list_head,path, depth+1);
         Flow_restoreContext(fv);
      } else if( strcmp(node->name, "LOOP") == 0
          || strcmp(node->name, "FAMILY") == 0
          || strcmp(node->name, "SWITCH") == 0){
         char path[SEQ_MAXFIELD] = {0};
         sprintf( path, "%s/%s", basePath,name);
         SeqListNode_pushFront(list_head, path);
         xmlNodePtr previousNode = fv->context->node;
         fv->context->node = node;
         parseFlowTree_internal(fv, list_head,path,depth+1);
         fv->context->node = previousNode;
      } else if( strcmp(node->name, "SWITCH_ITEM") == 0 ){
         char path[SEQ_MAXFIELD] = {0};
         const char * switch_item_name = xmlGetProp(xmlNode, (const xmlChar *)"name");
         sprintf( path, "%s[%s]", basePath,switch_item_name);
         xmlNodePtr previousNode = fv->context->node;
         fv->context->node = node;
         parseFlowTree_internal(fv, list_head,path, depth+1);
         fv->context->node = previousNode;
         free((char*)switch_item_name);
      }
      free((char *)name);
   }
   xmlXPathFreeObject(results);
}

int PhilFlowInfo( SeqNodeDataPtr _nodeDataPtr, const char *_nodePath, const char *_seq_exp_home)
{
   /* Flow_parsePath_db(); */
   return 0;

}


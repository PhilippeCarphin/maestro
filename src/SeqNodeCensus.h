#ifndef _SEQ_NODE_CENSUS_H_
#define _SEQ_NODE_CENSUS_H_
/********************************************************************************
 *
********************************************************************************/
typedef struct _PathArgNode{
   struct _PathArgNode *nextPtr;
   const char * path;
   const char * switch_args;
} PathArgNode;
typedef PathArgNode *PathArgNodePtr;

PathArgNodePtr parseFlowTree(const char * seq_exp_home);
int PathArgNode_deleteList(PathArgNodePtr *list_head);
void PathArgNode_printList(PathArgNodePtr list_head);
#endif

#include "SeqListNode.h"
#include "FlowVisitor.h"
void parseFlowTree_internal(FlowVisitorPtr fv, LISTNODEPTR * list_head,
                                    const char * basePath, int depth);
LISTNODEPTR parseFlowTree(const char * seq_exp_home);
int nodeList_to_infoFile(LISTNODEPTR path_list, const char *expHome,
                           const char * filePath);

char * SI_path_to_path(const char *path_SI);
#define for_list(iterator, list_head) \
   LISTNODEPTR __node;\
   const char *iterator;\
   for( __node = list_head; ((__node != NULL) && ((iterator = __node->data) || 1)); __node = __node->nextPtr)


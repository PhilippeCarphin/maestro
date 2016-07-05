#include "SeqListNode.h"
#include "FlowVisitor.h"
void parseFlowTree_internal(FlowVisitorPtr fv, LISTNODEPTR * list_head,
                                    const char * basePath, int depth);
LISTNODEPTR parseFlowTree(const char * seq_exp_home);
int nodeList_to_infoFile(LISTNODEPTR path_list, const char *expHome,
                           const char * filePath);

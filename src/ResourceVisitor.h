
#ifndef _RESOURCE_VISITOR_H_
#define _RESOURCE_VISITOR_H_

#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/tree.h>
#include <libxml/xpathInternals.h>
#include "SeqNode.h"


#define RESOURCE_VISITOR_STACK_SIZE 30
#define RESOURCE_MAX_RECURSION_DEPTH ((RESOURCE_VISITOR_STACK_SIZE)-1)
#define RESOURCE_SUCCESS 0
#define RESOURCE_FAILURE -1
#define RESOURCE_TRUE 1
#define RESOURCE_FALSE 0

typedef struct _ValidityData {

   char * dow;
   char * hour;
   char * time_delta;
   char * valid_hour;
   char * valid_dow;
   char * local_index;
}ValidityData;

typedef ValidityData * ValidityDataPtr;

typedef struct _ResourceVisitor {
   const char * nodePath; /* The path of the node for which we are getting
                             resources, which may not be the path of the
                             nodeDataPtr */
   xmlXPathContextPtr context;
   const char * xmlFile;
   const char * defFile;

   int loopResourcesFound;
   int forEachResourcesFound;
   int batchResourcesFound;
   int abortActionFound;

   xmlNodePtr _nodeStack[RESOURCE_VISITOR_STACK_SIZE];
   int _stackSize;
} ResourceVisitor;

typedef ResourceVisitor * ResourceVisitorPtr;

typedef  int (*NodeFunction)(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);


const char * defFilename(const char * _seq_exp_home);
const char * xmlResourceFilename(const char * _seq_exp_home, const char * nodePath, SeqNodeType nodeType );
ResourceVisitorPtr newResourceVisitor(SeqNodeDataPtr _nodeDataPtr, const char * _seq_exp_home, const char * nodePath, SeqNodeType nodeType);
void deleteResourceVisitor(ResourceVisitorPtr rv);
ValidityDataPtr newValidityData();
void deleteValidityData( ValidityDataPtr val );
void printValidityData(ValidityDataPtr val);
xmlXPathContextPtr Resource_createContext(SeqNodeDataPtr _nodeDataPtr, const char * xmlFile, const char * defFile, SeqNodeType nodeType);
xmlDocPtr xml_fallbackDoc(const char * xmlFile, SeqNodeType nodeType);
int getPhilResources( SeqNodeDataPtr _nodeDataPtr, const char * _nodePath, const char * _seq_exp_home);
void Resource_parseRootNode(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
int Resource_parseValidityNodes(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
ValidityDataPtr getValidityData(xmlNodePtr validityNode);
const char * getIncrementedDatestamp( const char * baseDatestamp, char * hour, char * time_delta);
int checkValidity(SeqNodeDataPtr _nodeDataPtr, ValidityDataPtr val );
int isValid(SeqNodeDataPtr _nodeDataPtr, xmlNodePtr validityNode);
int Resource_parseNode(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr, xmlNodePtr node);
int Resource_getLoopAttributes(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
int Resource_getForEachAttributes(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
int Resource_getBatchAttributes(ResourceVisitorPtr rv,SeqNodeDataPtr _nodeDataPtr);
int Resource_getDependencies(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
int Resource_getAbortActions(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
int Resource_setWorkerData(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
int Resource_validateMachine(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
int Resource_setShell(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);
int Resource_parseNodeDFS(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr, NodeFunction nf);
int Resource_parseNodeDFS_internal(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr,
                                    xmlNodePtr node, NodeFunction nf, int depth);
int Resource_getContainerLoopAttributes(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr);



void getNodeLoopContainersAttr (  SeqNodeDataPtr _nodeDataPtr, const char *loopNodePath, const char *expHome );
int getNodeResources(SeqNodeDataPtr _nodeDataPtr, const char * expHome, const char * nodePath);


#endif

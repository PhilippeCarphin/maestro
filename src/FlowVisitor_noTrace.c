#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/tree.h>
#include <libxml/xpathInternals.h>

#include "SeqNode.h"
#include "nodeinfo.h"
#include "SeqUtil.h"
#include "XmlUtils.h"
#include "SeqLoopsUtil.h"

#include "FlowVisitor.h"

#define for_tokens( token, string, delimiters, sp) \
   char * savePointer = NULL;\
   char tmpString[strlen(string) + 1];\
   char * token = NULL; \
   strcpy(tmpString,string);\
   for( token = strtok_r(tmpString,delimiters, &sp); token != NULL; token = strtok_r(NULL,delimiters,&sp))

/********************************************************************************
 * This function returns the switch type of the current node in the XML XPath
 * context
********************************************************************************/
char * Flow_findSwitchType( FlowVisitorPtr _flow_visitor ){
   xmlXPathObjectPtr attributesResult = NULL;
   xmlNodeSetPtr nodeset = NULL;
   xmlNodePtr currentNodePtr = NULL;
   int i;
   char * switchType = NULL;

   if( (attributesResult = XmlUtils_getnodeset( "(@*)" , _flow_visitor->context)) == NULL )
      goto out;

   nodeset = attributesResult->nodesetval;
   for (i = 0; i < nodeset->nodeNr; i++){
      currentNodePtr = nodeset->nodeTab[i];
      if( strcmp(currentNodePtr->name,"type") == 0){
         switchType =  currentNodePtr->children->content;
         goto out_free;
      }
   }

out_free:
   xmlXPathFreeObject(attributesResult);
out:
   return switchType;
}

/********************************************************************************
 * Parses the string name as a comma separated list of values and returns 1 if
 * the argument value is one of those values.
********************************************************************************/
int switchNameContains(char * name, char * switchValue)
{
   int retval = 0;
   for_tokens( sv_token, name , ",)",sp){
      if ( strcmp(sv_token, switchValue) == 0){
         retval = 1;
         goto out;
      }
   }
out:
   free(tmp_name);
   return retval;
}

/********************************************************************************
 * Returns 1 if the SWITCH_ITEM currentNodePtr has the argument switchValue as
 * one of the tokens in it's name attribute.
 * Note that we use the XML XPath context to perform the attribute search.  For
 * this, we need to change the context's current node temporarily and restore it
 * upon exiting the function.
********************************************************************************/
int Flow_switchItemHasValue(FlowVisitorPtr _flow_visitor, xmlNodePtr currentNodePtr, char*  switchValue) {
   /* Save xml context->node and restore it at the end */
   xmlNodePtr previousNodePtr = _flow_visitor->context->node;
   _flow_visitor->context->node = currentNodePtr;
   int retval = 0;

   xmlXPathObjectPtr attributesResult = NULL;
   if( (attributesResult = XmlUtils_getnodeset( "(@name)" , _flow_visitor->context)) == NULL )
      raiseError("Flow_switchItemHasValue(): SWITCH_ITEM with no name attribute\n");

   retval = switchNameContains(attributesResult->nodesetval->nodeTab[0]->children->content, switchValue);

out:
   xmlXPathFreeObject(attributesResult);
   _flow_visitor->context->node = previousNodePtr;
   return retval;
}

/********************************************************************************
 * Moves visitor to switch item child that has switchValue if it exists
 * Returns -1 on failure
 * Returns  0 on success
********************************************************************************/
int Flow_findSwitchItemWithValue( FlowVisitorPtr _flow_visitor, char * switchValue)
{
   int retval = 0;
   xmlXPathObjectPtr switchItemResult;
   xmlNodeSetPtr nodeset = NULL;
   xmlNodePtr currentNodePtr = NULL;
   int i;

   if( (switchItemResult = XmlUtils_getnodeset( "(child::SWITCH_ITEM[not(@name='default')])", _flow_visitor->context)) == NULL){
      retval = FLOW_FAILURE;
      goto out;
   }

   nodeset = switchItemResult->nodesetval;

   for( i = 0; i < nodeset->nodeNr ; ++i ){
      currentNodePtr = nodeset->nodeTab[i];
      if (Flow_switchItemHasValue(_flow_visitor, currentNodePtr, switchValue)){
         _flow_visitor->context->node = currentNodePtr;
         retval = FLOW_SUCCESS;
         goto out_free;
      }
   }

out_free:
   xmlXPathFreeObject(switchItemResult);
out:
   return retval;
}

/********************************************************************************
 * Moves visitor to default switch item child of current node if it exists.
 * Returns -1 on failure
 * Returns  0 on success
********************************************************************************/
int Flow_findDefaultSwitchItem( FlowVisitorPtr _flow_visitor)
{
   int retval = 0;
   xmlXPathObjectPtr switchItemResult = NULL;

   if ( (switchItemResult = XmlUtils_getnodeset( "(child::SWITCH_ITEM[@name='default'])", _flow_visitor->context)) == NULL ){
      retval = FLOW_FAILURE;
      goto out;
   } else {
      _flow_visitor->context->node = switchItemResult->nodesetval->nodeTab[0];
      retval = FLOW_SUCCESS;
      goto out_free;
   }

out_free:
   xmlXPathFreeObject(switchItemResult);
out:
   return retval;
}


/********************************************************************************
 * Finds the SWITCH_ITEM xml node whose name attribute contains switchValue and
 * sets it as the XML XPath context's current node.  If no such SWITCH_ITEM can
 * be found, it will look for one whose name attribute is 'default'.
********************************************************************************/
int Flow_findSwitchItem( FlowVisitorPtr _flow_visitor, char *switchValue )
{
   int retval = FLOW_SUCCESS;
   /* Look for SWITCH_ITEMs whose name attribute contains switchValue as one of
    * it's comma separated tokens */
   if ( Flow_findSwitchItemWithValue(_flow_visitor, switchValue ) == FLOW_SUCCESS ){
      retval = FLOW_SUCCESS;
      goto out;
   } else if ( Flow_findDefaultSwitchItem(_flow_visitor) == FLOW_SUCCESS ) {
      retval = FLOW_SUCCESS;
      goto out;
   }


out_free:
out:
   return retval;
}


/********************************************************************************
 * With the XML XPath context's current node being a SWITCH tag, this function
 * changes it to the correct SWITCH_ITEM given the switch value AND also adds
 * the switch information to the _nodeDataPtr.
 * *I used the word "and" in describing what the function does.  This is a bad
 * code smell... see if I can do better.
********************************************************************************/
/* Make this function have an error code return value */
int Flow_parseSwitchAttributes(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr, int isLast ){

   char * switchType = NULL;
   char * switchValue = NULL;


   if( (switchType = Flow_findSwitchType(_flow_visitor)) == NULL )
      raiseError("Flow_parseSwitchAttributes(): switchType not found\n");

   switchValue = switchReturn(_nodeDataPtr, switchType);
   char * fixedSwitchPath = SeqUtil_fixPath( _flow_visitor->currentFlowNode );
   SeqNameValues_insertItem(&(_nodeDataPtr->switchAnswers), fixedSwitchPath , switchValue );

   if( Flow_findSwitchItem(_flow_visitor, switchValue) == FLOW_SUCCESS )


   if(isLast){
      SeqNode_addSpecificData(_nodeDataPtr, "VALUE", switchValue);
      /* PHIL: do this outside of the while instead of using isLast */
      _nodeDataPtr->type = Switch;
   } else {
      SeqNode_addSpecificData( _nodeDataPtr, "SWITCH_TYPE", switchType );
      SeqNode_addSwitch(_nodeDataPtr,fixedSwitchPath , switchType, switchValue);
   }
   free(switchValue);
   free(fixedSwitchPath);
   return FLOW_SUCCESS;
}

/********************************************************************************
 * Sets the XML XPath context's current node to the child of the current node
 * whose name attribute matches the nodeName parameter.
********************************************************************************/
int Flow_doNodeQuery(FlowVisitorPtr _flow_visitor, char * nodeName, int isFirst)
{
   xmlXPathObjectPtr result = NULL;
   char query[SEQ_MAXFIELD] = {'\0'};

   if ( isFirst )
      /* initial query */
      sprintf ( query, "(/*[@name='%s'])", nodeName );
   else
      /* next queries relative to previous node context */
      sprintf ( query, "(child::*[@name='%s'])", nodeName );

   /* run the normal query */
   if( (result = XmlUtils_getnodeset (query, _flow_visitor->context)) == NULL ) {
      /* raiseError("Node %s not found in XML master file! (getFlowInfo)\n", nodeName); */
      return FLOW_FAILURE;
   }

   _flow_visitor->context->node = result->nodesetval->nodeTab[0];
   _flow_visitor->currentNodeType = getNodeType(_flow_visitor->context->node->name);
   xmlXPathFreeObject(result);
   return FLOW_SUCCESS;
}


/********************************************************************************
 * Initializes the flow_visitor to the entry module;
********************************************************************************/
FlowVisitorPtr Flow_newVisitor(char * _seq_exp_home)
{
   FlowVisitorPtr new_flow_visitor = (FlowVisitorPtr) malloc(sizeof(FlowVisitor));
   char * postfix = "/EntryModule/flow.xml";

   char * xmlFilename = (char *) malloc ( strlen(_seq_exp_home) + strlen(postfix) + 1 );
   sprintf(xmlFilename, "%s%s", _seq_exp_home,postfix);

   new_flow_visitor->expHome = _seq_exp_home;

   new_flow_visitor->doc = XmlUtils_getdoc(xmlFilename);
   new_flow_visitor->context = xmlXPathNewContext(new_flow_visitor->doc);

   new_flow_visitor->previousDoc = NULL;
   new_flow_visitor->previousContext = NULL;
   new_flow_visitor->currentFlowNode = NULL;
   new_flow_visitor->suiteName = NULL;
   new_flow_visitor->taskPath = NULL;
   new_flow_visitor->module = NULL;
   new_flow_visitor->intramodulePath = NULL;

   free(xmlFilename);

   return new_flow_visitor;
}

/********************************************************************************
 *
********************************************************************************/
int Flow_changeModule(FlowVisitorPtr _flow_visitor, char * module)
{
   int retval = FLOW_SUCCESS;
   xmlXPathObjectPtr result = NULL;


   char * infix = "/modules/";
   char * postfix = "/flow.xml";
   char xmlFilename[strlen(_flow_visitor->expHome) + strlen(infix) + strlen(module) + strlen(postfix) + 1];
   sprintf( xmlFilename, "%s%s%s%s", _flow_visitor->expHome, infix, module, postfix);

   if( _flow_visitor->intramodulePath != NULL ){
      free(_flow_visitor->intramodulePath);
      _flow_visitor->intramodulePath = NULL;
   }

   Flow_changeXmlFile(_flow_visitor,  xmlFilename );

   if( (result = XmlUtils_getnodeset( "(/MODULE)", _flow_visitor->context )) == NULL ){
      retval = FLOW_FAILURE;
      goto out;
   } else {
      _flow_visitor->context->node = result->nodesetval->nodeTab[0];
      _flow_visitor->currentNodeType = Module;
      retval = FLOW_SUCCESS;
      goto out_free;
   }

out_free:
   xmlXPathFreeObject(result);
out:
   return retval;
}

/********************************************************************************
 *
********************************************************************************/
int Flow_changeXmlFile(FlowVisitorPtr _flow_visitor,  char * xmlFilename)
{

   if (_flow_visitor->previousContext != NULL){
      xmlXPathFreeContext(_flow_visitor->previousContext);
      _flow_visitor->previousContext = NULL;
   }
   if (_flow_visitor->previousDoc != NULL){
      xmlFreeDoc(_flow_visitor->previousDoc);
      _flow_visitor->previousDoc = NULL;
   }


   _flow_visitor->previousDoc = _flow_visitor->doc;
   _flow_visitor->previousContext = _flow_visitor->context;

   _flow_visitor->doc = XmlUtils_getdoc(xmlFilename);
   _flow_visitor->context = xmlXPathNewContext(_flow_visitor->doc);


   return FLOW_SUCCESS;
}

/********************************************************************************
 * Appends things to the various paths we are constructing in getFlowInfo.
********************************************************************************/
int Flow_pathUpdate(FlowVisitorPtr _flow_visitor, char * pathToken, int container)
{
   int nodeType = _flow_visitor->currentNodeType;
   SeqUtil_stringAppend(&(_flow_visitor->currentFlowNode),pathToken);
   free( _flow_visitor->module);
   _flow_visitor->module = strdup(pathToken);
   if (container) {
      SeqUtil_stringAppend( &(_flow_visitor->currentFlowNode), "/");
      /* Case and case_item are not part of the task_depot */
      /* they are however part of the container path */
      switch( nodeType ){
         case Module:
            free(_flow_visitor->taskPath);
            _flow_visitor->taskPath = NULL;
         case Family:
         case Loop:
         case Switch:
         case ForEach:
            SeqUtil_stringAppend( &(_flow_visitor->taskPath), "/" );
            SeqUtil_stringAppend( &(_flow_visitor->taskPath), pathToken );
            free(_flow_visitor->intramodulePath);
            _flow_visitor->intramodulePath = NULL;
            SeqUtil_stringAppend( &(_flow_visitor->intramodulePath), _flow_visitor->taskPath );
            break;
         default:
            break;
      }
   } else {
      switch(nodeType){
         case Task:
         case NpassTask:
            SeqUtil_stringAppend( &(_flow_visitor->taskPath), "/" );
            SeqUtil_stringAppend( &(_flow_visitor->taskPath), pathToken );
            break;
         default:
            break;
      }
   }
   return FLOW_SUCCESS;
}

/********************************************************************************
 * Sets the nodeDataPtr's pathToModule, taskPath, suiteName, module and
 * intramodulePath from info gathered while parsing the xml files.
********************************************************************************/
int Flow_setPathData(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr)
{
   char *suiteName = (char*) SeqUtil_getPathLeaf(_flow_visitor->expHome);
   int entryModule = (_flow_visitor->previousDoc == NULL);
   char pathToModule[SEQ_MAXFIELD] = {'\0'};
   if( _flow_visitor->intramodulePath != NULL && ! entryModule ){
      int lengthDiff = strlen(_nodeDataPtr->container) - strlen( _flow_visitor->intramodulePath);
      strncpy(pathToModule, _nodeDataPtr->container, lengthDiff);
   } else {
      strcpy(pathToModule, _nodeDataPtr->container );
   }

   sprintf(pathToModule,"%s/%s",pathToModule,_flow_visitor->module);



   SeqNode_setPathToModule(_nodeDataPtr,pathToModule);
   SeqNode_setInternalPath( _nodeDataPtr, _flow_visitor->taskPath );
   SeqNode_setSuiteName( _nodeDataPtr, suiteName );
   SeqNode_setModule( _nodeDataPtr, _flow_visitor->module );
   SeqNode_setIntramoduleContainer( _nodeDataPtr, _flow_visitor->intramodulePath );
   _nodeDataPtr->type = _flow_visitor->currentNodeType;

   free(suiteName);
   return FLOW_SUCCESS;
}


/********************************************************************************
 * Adds flow dependencies to _nodeDataPtr
********************************************************************************/
int Flow_parseDependencies(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr)
{
   xmlXPathObjectPtr result = NULL;
   xmlXPathContextPtr context = NULL;

   if (_flow_visitor->currentNodeType == Module){
      context = _flow_visitor->previousContext;
   } else {
      context = _flow_visitor->context;
   }

   if( (result = XmlUtils_getnodeset ("(child::DEPENDS_ON)", context )) == NULL ) {
      goto err;
   }

   parseDepends( result, _nodeDataPtr, 1 );
   xmlXPathFreeObject (result);
   return FLOW_SUCCESS;
err:
   return FLOW_FAILURE;
}

/********************************************************************************
 * Parses submits into _nodeDataPtr
********************************************************************************/
int Flow_parseSubmits(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr)
{
   xmlXPathObjectPtr result = XmlUtils_getnodeset ("(child::SUBMITS)", _flow_visitor->context);
   parseSubmits( result, _nodeDataPtr );
   xmlXPathFreeObject (result);
   return FLOW_SUCCESS;
}

/********************************************************************************
 * Parses the preceding sibings and following siblings into _nodeDataPtr
********************************************************************************/
int Flow_parseSiblings(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr)
{
   /* retrieve node's siblings */
   int switchItemFound = (strcmp(_flow_visitor->context->node->name, "SWITCH_ITEM") == 0);
   xmlXPathObjectPtr result = NULL;
   xmlXPathContextPtr context = NULL;
   char query[SEQ_MAXFIELD] = {'\0'};
   char * switchPrefix = NULL;

   if ( strcmp(_flow_visitor->context->node->name,"SWITCH_ITEM") == 0 )
      switchPrefix = strdup("../");
   else
      switchPrefix = strdup("");

   if (_nodeDataPtr->type == Module)
      context = _flow_visitor->previousContext;
   else
      context = _flow_visitor->context;


   sprintf( query, "(%spreceding-sibling::*[@name])", switchPrefix);
   result =  XmlUtils_getnodeset (query, _flow_visitor->context);

   if (result) {
   }
   parseNodeSiblings( result, _nodeDataPtr);
   xmlXPathFreeObject (result);

   sprintf( query, "(%sfollowing-sibling::*[@name])", switchPrefix);
   result =  XmlUtils_getnodeset (query, _flow_visitor->context);

   if (result) {
   }
   parseNodeSiblings( result, _nodeDataPtr);
   xmlXPathFreeObject (result);
   return FLOW_SUCCESS;
}

/********************************************************************************
 * get Task and NpassTask attributes of current node.
********************************************************************************/
int Flow_checkWorkUnit(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr)
{
   xmlXPathObjectPtr attributesResult = NULL;
   xmlNodeSetPtr nodeset = NULL;;
   xmlNodePtr currentNodePtr = NULL;
   char * nodeName;

   if ( (attributesResult = XmlUtils_getnodeset( "(@*)", _flow_visitor->context) ) == NULL )
      return FLOW_FAILURE;

   int i;
   nodeset = attributesResult->nodesetval;
   for ( i = 0; i < nodeset->nodeNr ; ++i ){
      currentNodePtr = nodeset->nodeTab[i];
      nodeName = currentNodePtr->name;
      if ( strcmp( nodeName , "work_unit" ) == 0 ){
         if( _flow_visitor->currentNodeType == Task || _flow_visitor->currentFlowNode == NpassTask) {
            raiseError("Work unit mode is only for containers (single_reserv=1)");
         } else {
            if ( _flow_visitor->currentFlowNode == NULL )
               raiseError("Work unit mode cannot be on the root node (single_reserv=1)");
            parseWorkerPath(_flow_visitor->currentFlowNode, _flow_visitor->expHome, _nodeDataPtr);
         }
      }
   }
   return FLOW_SUCCESS;
}

/********************************************************************************
 * Prints the current information of the visitor
********************************************************************************/
void Flow_print_state(FlowVisitorPtr _flow_visitor, int trace_level)
{
}

/********************************************************************************
 *
********************************************************************************/
int Flow_parseSpecifics(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr)
{
   xmlXPathObjectPtr result = NULL;
   if ( (result = XmlUtils_getnodeset("(@*)", _flow_visitor->context)) == NULL){
      return FLOW_FAILURE;
   }

   parseNodeSpecifics(_nodeDataPtr->type,result,_nodeDataPtr);
   xmlXPathFreeObject(result);
   return FLOW_SUCCESS;
}

/********************************************************************************
 * Parses the given nodePath while gathering information and adding attributes
 * to the nodeDataPtr;
********************************************************************************/
int Flow_parsePath(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr, char * _nodePath)
{
   int totalCount = SeqUtil_tokenCount( _nodePath, "/" ) - 1;/* count is 0-based */
   int count = 0;
   char * tmpJobPath = strdup(_nodePath);
   char * pathToken = NULL;

   pathToken = (char*) strtok( tmpJobPath, "/" );
   while ( pathToken != NULL ) {

      Flow_doNodeQuery(_flow_visitor, pathToken, count == 0);
      Flow_pathUpdate(_flow_visitor, pathToken, count != totalCount );
      if( _flow_visitor->currentNodeType == Module ){
         Flow_changeModule(_flow_visitor, pathToken);
      }
      /* retrieve node specific attributes */

      if( _flow_visitor->currentNodeType != Task && _flow_visitor->currentNodeType != NpassTask )
         Flow_checkWorkUnit(_flow_visitor, _nodeDataPtr);

      if( _flow_visitor->currentNodeType == Switch )
         Flow_parseSwitchAttributes(_flow_visitor, _nodeDataPtr, count == totalCount );

      if( _flow_visitor->currentNodeType == Loop && count != totalCount ){
         getNodeLoopContainersAttr( _nodeDataPtr, _flow_visitor->currentFlowNode, _flow_visitor->expHome);
      }

      /* get the next token */
      pathToken = (char*) strtok(NULL,"/");
      count++;
   }
   free(tmpJobPath);
   return FLOW_SUCCESS;
}

int Flow_deleteVisitor(FlowVisitorPtr _flow_visitor)
{
   if( _flow_visitor->context != NULL )
      xmlXPathFreeContext(_flow_visitor->context);
   if( _flow_visitor->doc != NULL )
      xmlFreeDoc(_flow_visitor->doc);

   if( _flow_visitor->previousContext != NULL )
      xmlXPathFreeContext(_flow_visitor->previousContext);
   if( _flow_visitor->previousDoc != NULL )
      xmlFreeDoc(_flow_visitor->previousDoc);

   free(_flow_visitor->currentFlowNode);
   free(_flow_visitor->taskPath);
   free(_flow_visitor->module);
   free(_flow_visitor->intramodulePath);
   free(_flow_visitor->suiteName);

   free(_flow_visitor);
}



/********************************************************************************
 *
********************************************************************************/
int Flow_walkPath(FlowVisitorPtr _flow_visitor, SeqNodeDataPtr _nodeDataPtr, char * nodePath)
{
   int count = 0;
   int totalCount = SeqUtil_tokenCount(nodePath,"/");
   int retval = FLOW_SUCCESS;
   for_tokens(pathToken, nodePath , "/", sp){
      if( Flow_doNodeQuery(_flow_visitor, pathToken, count == 0) == FLOW_FAILURE ){
         retval = FLOW_FAILURE;
         goto out;
      }

      if( _flow_visitor->currentNodeType == Switch ){
         char * switchType = Flow_findSwitchType(_flow_visitor);
         char * switchValue = switchReturn(_nodeDataPtr,switchType);
         if( Flow_findSwitchItem(_flow_visitor, switchValue) == FLOW_FAILURE ) {
            if( count == totalCount ){
               retval = FLOW_SUCCESS;
               goto out;
            } else {
               retval = FLOW_FAILURE;
               goto out;
            }
         }
      }

      if ( _flow_visitor->currentNodeType == Module ){
         if( Flow_changeModule(_flow_visitor,pathToken) == FLOW_FAILURE ){
            retval = FLOW_FAILURE;
            goto out;
         }
      }
      count++;
   }
out:
   return retval;
}


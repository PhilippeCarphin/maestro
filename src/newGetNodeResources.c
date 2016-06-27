/* int getNodeResources(SeqNodeDataPtr _nodeDataPtr); */
#include "newGetNodeResources.h"
#include "nodeinfo.h"
#include "SeqDatesUtil.h"
#include "SeqLoopsUtil.h"
#include "SeqUtil.h"

/********************************************************************************
 * Constructs the path to the node's resource xml file
********************************************************************************/
const char * xmlResourceFilename(const char * _seq_exp_home, const char * nodePath, SeqNodeType nodeType )
{
   SeqUtil_TRACE(TL_FULL_TRACE, "xmlResourceFilename() begin\n");
   const char * xml_postfix = "/container.xml";
   const char * infix = "/resources/";
   size_t pathLength =  strlen(_seq_exp_home) + strlen(infix)
                    + strlen(nodePath) + strlen(xml_postfix) + 1;
   char xmlFile[pathLength];
   char * normalizedXmlFile = malloc( pathLength );

   if ( nodeType == Task || nodeType == NpassTask )
      xml_postfix = ".xml";

   sprintf(xmlFile, "%s%s%s%s", _seq_exp_home, infix, nodePath, xml_postfix);
   SeqUtil_normpath(normalizedXmlFile,xmlFile);

   SeqUtil_TRACE(TL_FULL_TRACE, "xmlResourceFilename() end : returning %s\n", normalizedXmlFile);
   return (const char *) normalizedXmlFile;
}

/********************************************************************************
 * Allocates and initialises a ResourceVisitor object to hold data used in the
 * process of getting the node's resources.
 * NOTE that the visitor may still be useful as a struct containing filenames
 * and other information even if the xml file could not be parsed or does not
 * exist.  Therefore, the user of this visitor must check whether the
 * rv->context is NULL before making queries to it.
********************************************************************************/
ResourceVisitorPtr newResourceVisitor(SeqNodeDataPtr _nodeDataPtr, const char * _seq_exp_home, const char * nodePath, SeqNodeType nodeType)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "newResourceVisitor() begin, nodePath=%s expHome=%s\n", nodePath, _seq_exp_home);
   ResourceVisitorPtr rv = (ResourceVisitorPtr) malloc ( sizeof (ResourceVisitor) );

   rv->nodePath = strdup(nodePath);

   rv->defFile = SeqUtil_resourceDefFilename(_seq_exp_home);
   rv->xmlFile = xmlResourceFilename(_seq_exp_home, nodePath, nodeType);
   rv->context = Resource_createContext(_nodeDataPtr, rv->xmlFile, rv->defFile, nodeType );
   if( rv->context != NULL )
      rv->context->node = rv->context->doc->children;

   rv->loopResourcesFound = 0;
   rv->forEachResourcesFound = 0;
   rv->batchResourcesFound = 0;
   rv->abortActionFound = 0;

   memset(rv->_nodeStack, '\0', RESOURCE_VISITOR_STACK_SIZE);
   rv->_stackSize = 0;

   SeqUtil_TRACE(TL_FULL_TRACE, "newResourceVisitor() end\n");
   return rv;
}

/********************************************************************************
 * Frees a ResourceVisitor object
********************************************************************************/
void deleteResourceVisitor(ResourceVisitorPtr rv)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "deleteResourceVisitor() begin\n");
   free((char *)rv->nodePath);
   free((char *)rv->xmlFile);
   free((char *)rv->defFile);
   if( rv->context != NULL ){
      xmlFreeDoc(rv->context->doc);
      xmlXPathFreeContext(rv->context);
   }
   free(rv);
   SeqUtil_TRACE(TL_FULL_TRACE, "deleteResourceVisitor() end\n");
}

/********************************************************************************
 * Used as part of the depth first search through VALIDITY nodes.  Pushes an
 * xmlNodePtr onto the stack of the resourceVisitor.
********************************************************************************/
int _pushNode(ResourceVisitorPtr rv, xmlNodePtr node)
{
   if( rv->_stackSize < RESOURCE_VISITOR_STACK_SIZE ){
      rv->_nodeStack[(rv->_stackSize)++] = node;
      return RESOURCE_SUCCESS;
   } else {
      return RESOURCE_FAILURE;
   }
}

/********************************************************************************
 * Sets the xmlNodePtr received as a parameter as the current node of the
 * resourceVisitor's context and pushes the current node of the context onto the
 * stack.  Used when entering the function Resource_parseNodeDFS_internal().
********************************************************************************/
int Resource_setNode(ResourceVisitorPtr rv, xmlNodePtr _node)
{
   if( _pushNode(rv,rv->context->node) == RESOURCE_SUCCESS ){
      rv->context->node = _node;
      return RESOURCE_SUCCESS;
   } else {
      return RESOURCE_FAILURE;
   }
}

/********************************************************************************
 * Pops an xmlNodePtr from the resourceVisitor's stack and returns the popped
 * node.
********************************************************************************/
xmlNodePtr _popNode(ResourceVisitorPtr rv)
{
   if( rv->_stackSize > 0 )
      return rv->_nodeStack[--(rv->_stackSize)];
   else
      return NULL;
}

/********************************************************************************
 * Pops a node from the stack and sets it as the current node of the context.
 * This function is used when returning from Resource_parseNodeDFS_internal().
********************************************************************************/
int Resource_unsetNode(ResourceVisitorPtr rv)
{
   rv->context->node = _popNode(rv);
   if( rv->context->node == NULL )
      return RESOURCE_FAILURE;
   else
      return RESOURCE_SUCCESS;
}

/********************************************************************************
 * Allocates and initialises a ValidityData struct to transfer between functions.
********************************************************************************/
ValidityDataPtr newValidityData()
{
   SeqUtil_TRACE(TL_FULL_TRACE, "newValidityData() begin\n");
   ValidityDataPtr val = (ValidityDataPtr ) malloc( sizeof (ValidityData) );

   val->dow = NULL;
   val->hour = NULL;
   val->time_delta = NULL;
   val->valid_hour = NULL;
   val->valid_dow = NULL;
   val->local_index = NULL;

   SeqUtil_TRACE(TL_FULL_TRACE, "newValidityData() end\n");
   return val;
}

/********************************************************************************
 * Free's a valididtyData struct.
********************************************************************************/
void deleteValidityData( ValidityDataPtr val )
{
   SeqUtil_TRACE(TL_FULL_TRACE, "deleteValidityData() begin\n");
   free(val->dow);
   free(val->hour);
   free(val->time_delta);
   free(val->valid_hour);
   free(val->valid_dow);
   free(val->local_index);
   free( val );
   SeqUtil_TRACE(TL_FULL_TRACE, "deleteValidityData() end\n");
}

/********************************************************************************
 * Prints the fields of the validityData struct.
********************************************************************************/
void printValidityData(ValidityDataPtr val)
{
   if( val->dow != NULL ) SeqUtil_TRACE(TL_FULL_TRACE, " val->dow = %s\n", val->dow);
   if( val->hour != NULL ) SeqUtil_TRACE(TL_FULL_TRACE, " val->hour = %s\n", val->hour);
   if( val->time_delta != NULL ) SeqUtil_TRACE(TL_FULL_TRACE, " val->time_delta = %s\n", val->time_delta);
   if( val->valid_hour != NULL ) SeqUtil_TRACE(TL_FULL_TRACE, " val->valid_hour = %s\n", val->valid_hour);
   if( val->valid_dow != NULL ) SeqUtil_TRACE(TL_FULL_TRACE, " val->valid_dow = %s\n", val->valid_dow);
   if( val->local_index != NULL ) SeqUtil_TRACE(TL_FULL_TRACE, " val->local_index = %s\n", val->local_index);
}

/********************************************************************************
 * Based on the experiment home and the node path, creates an xmlXPath context
 * with the resource file of the given node.
********************************************************************************/
xmlXPathContextPtr Resource_createContext(SeqNodeDataPtr _nodeDataPtr, const char * xmlFile,
                                          const char * defFile, SeqNodeType nodeType)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_createContext() begin\n");
   xmlXPathContextPtr context = NULL;
   xmlDocPtr doc = NULL;

   if ( access(xmlFile, R_OK ) != 0 ){
      if ( nodeType == Loop || nodeType == ForEach ){
         raiseError("createResourceContext(): Cannot access mandatory resource file %s\n", xmlFile);
      } else {
         context = NULL;
         goto out;
      }
   }

   doc = XmlUtils_getdoc(xmlFile);

   if (doc == NULL) {
      doc = xml_fallbackDoc( xmlFile, nodeType);
   }

   context = xmlXPathNewContext(doc);

   if( strcmp( context->doc->children->name, NODE_RES_XML_ROOT_NAME ) != 0 ){
      SeqUtil_TRACE(TL_FULL_TRACE, "Root node:%s, NODE_RES_XML_ROOT_NAME:%s\n",context->doc->children->name, NODE_RES_XML_ROOT_NAME);
      raiseError( "Root node of xmlFile %s must be %s\n",xmlFile, NODE_RES_XML_ROOT_NAME);
   }

   if ( defFile != NULL )
      XmlUtils_resolve(xmlFile,context,defFile,_nodeDataPtr->expHome);

out:
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_createContext() end\n");
   return context;
}

/********************************************************************************
 * Fallback in case the document cannot be parsed:  If it is empty, we create a
 * dummy one, even for loops.
 * If it wasn't empty and could not be parsed, there is nothing we can do about
 * it except exit with error.
********************************************************************************/
xmlDocPtr xml_fallbackDoc(const char * xmlFile, SeqNodeType nodeType)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "xml_fallbackDoc() begin\n");
   FILE * pxml = NULL;
   int xmlSize = 0;

   pxml = fopen (xmlFile, "a+");
   if(!pxml) raiseError("Permission to write in %s\n",xmlFile);
   fseek (pxml , 0 , SEEK_END);
   xmlSize = ftell (pxml);

   if ( xmlSize==0 ) {
      const char * start_tag = "<NODE_RESOURCES>\n";
      const char * end_tag   = "</NODE_RESOURCES>\n";
      const char * loop_node = "\t<LOOP \t<LOOP start=\"0\" set=\"1\" end=\"1\" step=\"1\"/>\n";
      SeqUtil_TRACE(TL_FULL_TRACE, "xml_fallbackDoc(): File %s is empty, writing mandatory tags\n", xmlFile);

      if( ! fprintf(pxml, "%s", start_tag) ){
         goto write_err;
      }
      if (  nodeType == Loop) {
         if(!fprintf(pxml, "%s",loop_node))
            goto write_err;
      }
      if (! fprintf(pxml, "%s", end_tag)){
         goto write_err;
      }

   } else {
      goto syntax_err;
   }
   fclose (pxml);

   SeqUtil_TRACE(TL_FULL_TRACE, "xml_fallbackDoc() end\n");
   return XmlUtils_getdoc(xmlFile);

write_err:
   raiseError("xml_fallbackDoc(): Unable to write in file %s\n",xmlFile);
syntax_err:
   raiseError("xml_fallbackDoc(): Syntax error in xml file %s.  Search listing for \"parser error\" \n", xmlFile);
   return NULL; /* In case we change raiseError for something that doesn' halt the program, we should still return something. */
}

/********************************************************************************
 * NODE FUNCTIONS: Node functions are functions that return an int and take a
 * resourceVisitorPtr and a SeqNodeDataPtr as arguments.  Pointers to these
 * functions are given to Resource_parseNodeDFS to be executed on nodes during
 * the DFS.
********************************************************************************/


/********************************************************************************
 * NodeFunction to do the work for getNodeResources.
********************************************************************************/
int do_all(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "do_all() begin\n");
   if( _nodeDataPtr->type == Loop)
      Resource_getLoopAttributes(rv,_nodeDataPtr);

   if( _nodeDataPtr->type == ForEach)
      Resource_getForEachAttributes(rv, _nodeDataPtr);

   Resource_getBatchAttributes(rv, _nodeDataPtr);
   Resource_getDependencies(rv, _nodeDataPtr);
   Resource_getAbortActions(rv, _nodeDataPtr);

   SeqUtil_TRACE(TL_FULL_TRACE, "do_all() end\n");
   return 0;
}

/********************************************************************************
 * Parses the associated resource xml file to get the resources of the node.
 * this function reads the node xml resource file to retrive info such as
 * dependencies, batch resource, abort actions and loop information for loop
 * nodes. The xml resource, if it exists, is located under
 * $SEQ_EXP_HOME/resources/ It follows the experiment node tree.
********************************************************************************/
int getNodeResources(SeqNodeDataPtr _nodeDataPtr, const char * expHome, const char * nodePath)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "getNodeResources() begin\n");
   int retval = RESOURCE_SUCCESS;
   ResourceVisitorPtr rv = newResourceVisitor(_nodeDataPtr,expHome,nodePath,_nodeDataPtr->type);

   Resource_parseNodeDFS(rv,_nodeDataPtr, do_all);

   Resource_setWorkerData(rv, _nodeDataPtr);
   Resource_validateMachine(rv, _nodeDataPtr);
   Resource_setShell(rv, _nodeDataPtr);

out_free:
   deleteResourceVisitor(rv);
out:
   SeqUtil_TRACE(TL_FULL_TRACE, "getNodeResources() end\n");
   return retval;
}

/********************************************************************************
 * gets the loop attributes for a loop on the container path of a node.  This is
 * used in getFlowInfo (specifically in Flow_parsePath() ).
********************************************************************************/
void getPhilLoopContainersAttr (  SeqNodeDataPtr _nodeDataPtr, const char *loopNodePath, const char *expHome )
{
   SeqUtil_TRACE(TL_FULL_TRACE, "getPhilLoopContainersAttr() begin\n");
   ResourceVisitorPtr rv = newResourceVisitor(_nodeDataPtr,expHome,loopNodePath,Loop);

   if( rv->context == NULL )
      goto out_free;

   Resource_parseNodeDFS(rv,_nodeDataPtr,Resource_getContainerLoopAttributes);

out_free:
   deleteResourceVisitor(rv);
   SeqUtil_TRACE(TL_FULL_TRACE, "getPhilLoopContainersAttr() end\n");
   return;
}

/********************************************************************************
 * Calls Resource_parseNodeDFS_internal() on the root node of the resource xml
 * file.
********************************************************************************/
int Resource_parseNodeDFS(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr, NodeFunction nf)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_parseNodeDFS() begin\n");
   int retval = RESOURCE_SUCCESS;
   if( rv->context != NULL ){
      retval = Resource_parseNodeDFS_internal(rv,_nodeDataPtr, rv->context->doc->children, nf, 0);
   }
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_parseNodeDFS() end\n");
   return retval;
}

/********************************************************************************
 * Internal function for depth first search through VALIDITY nodes.
********************************************************************************/
int Resource_parseNodeDFS_internal(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr,
                                    xmlNodePtr node, NodeFunction nf, int depth)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_parseNodeDFS_internal() begin, depth = %d\n",depth);
   int retval = RESOURCE_SUCCESS;
   if( depth > RESOURCE_MAX_RECURSION_DEPTH ){
      retval = RESOURCE_FAILURE;
      goto out;
   }

   Resource_setNode(rv, node);

   xmlXPathObjectPtr validityResults = XmlUtils_getnodeset("(child::VALIDITY)", rv->context );
   for_results( valNode , validityResults ){
      /* Note that once a valid VALIDITY node is found, others at the same level
       * will be ignored.*/
      if(isValid(_nodeDataPtr,valNode)){
         retval = Resource_parseNodeDFS_internal(rv, _nodeDataPtr, valNode, nf, depth+1);
      }
   }

   nf(rv,_nodeDataPtr);

   Resource_unsetNode(rv);

out:
   xmlXPathFreeObject(validityResults);
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_parseNodeDFS_internal() end\n");
   return retval;
}

/********************************************************************************
 * Extracts the data form an XML VALIDITY node into a dynamically allocated
 * struct validityData and returns a pointer to it.
********************************************************************************/
ValidityDataPtr getValidityData(xmlNodePtr validityNode)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "getValidityData() begin\n");
   if ( strcmp(validityNode->name, "VALIDITY") != 0)
      raiseError( "isValid() must receive a VALIDITY xml node\n");
   ValidityDataPtr val = newValidityData();

   val->dow = xmlGetProp( validityNode, "dow");
   val->hour = xmlGetProp( validityNode, "hour");
   val->time_delta = xmlGetProp( validityNode, "time_delta");
   val->valid_hour = xmlGetProp( validityNode, "valid_hour");
   val->valid_dow = xmlGetProp( validityNode, "valid_dow");
   val->local_index = xmlGetProp( validityNode, "local_index");

   SeqUtil_TRACE(TL_FULL_TRACE, "getValidityData() end\n");
   return val;
}

/********************************************************************************
 * Compares the data in val with the current _nodeDataPtr to determine whether
 * the the data in a VALIDITY xml node is currently "valid" to decide whether or
 * not we parse it's content (children).
********************************************************************************/
int checkValidity(SeqNodeDataPtr _nodeDataPtr, ValidityDataPtr val )
{
   SeqUtil_TRACE(TL_FULL_TRACE, "checkValidity() begin\n");
   printValidityData(val);
   int retval = 1;

   char * local_ext = SeqLoops_indexToExt(val->local_index);
   SeqUtil_TRACE(TL_FULL_TRACE, "PHIL!! datestamp = %s\n",_nodeDataPtr->datestamp);

   const char * incrementedDatestamp = SeqDatesUtil_getIncrementedDatestamp( _nodeDataPtr->datestamp, val->hour, val->time_delta);

   /* Check local_index */
   if ( local_ext != NULL && strcmp ( local_ext, _nodeDataPtr->extension ) != 0
         && strcmp(local_ext, "") != 0){
      SeqUtil_TRACE(TL_FULL_TRACE,"checkValidity(): extension mismatch:local_index=%s, local_ext=%s, ndp->extension=%s\n", val->local_index, local_ext, _nodeDataPtr->extension);
      retval = 0;
      goto out_free;
   }

   /* Check valid_hour */
   if (val->valid_hour != NULL && strlen(val->valid_hour) > 0
         && !SeqDatesUtil_isDepHourValid(incrementedDatestamp, val->valid_hour)){
      retval = 0;
      goto out_free;
   }

   /* Check valid_dow */
   if (val->valid_dow != NULL && strlen(val->valid_dow) > 0
         && !SeqDatesUtil_isDepDOWValid(incrementedDatestamp, val->valid_dow)){
      retval = 0;
      goto out_free;
   }

out_free:
   free(local_ext);
   free((char *)incrementedDatestamp);
   SeqUtil_TRACE(TL_FULL_TRACE, "checkValidity() end. Returning %d\n", retval);
   return retval;
}

/********************************************************************************
 * Determines whether an XML VALIDITY node is valid.
********************************************************************************/
int isValid(SeqNodeDataPtr _nodeDataPtr, xmlNodePtr validityNode)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "isValid() begin\n");
   SeqUtil_TRACE(TL_FULL_TRACE, "isValid() datestamp = %s\n", _nodeDataPtr->datestamp);

   ValidityDataPtr validityData = getValidityData(validityNode);

   int isValid = checkValidity(_nodeDataPtr, validityData);

   SeqUtil_TRACE(TL_FULL_TRACE, "isValid() end returning %d\n", isValid);
   deleteValidityData(validityData);
   return isValid;
}

/********************************************************************************
 * NodeFunction: Queries the context for the attributes of the LOOP child of the
 * current node which may be the root node or a VALIDITY node.
********************************************************************************/
int Resource_getLoopAttributes(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   int retval = 0;
   SeqUtil_TRACE(TL_FULL_TRACE, "getLoopAttributes() begin\n");

   if( rv->loopResourcesFound ){
      retval = 1;
      goto out;
   }

   xmlXPathObjectPtr result = XmlUtils_getnodeset("(child::LOOP/@*)",rv->context);
   if(result != NULL){
      parseNodeSpecifics(Loop, result, _nodeDataPtr);
      rv->loopResourcesFound = 1;
      retval = 0;
   }

out_free:
   xmlXPathFreeObject(result);
out:
   SeqUtil_TRACE(TL_FULL_TRACE, "getLoopAttributes() end\n");
   return retval;
}

/********************************************************************************
 * NodeFunction: Gets attributes for a container loop.
********************************************************************************/
int Resource_getContainerLoopAttributes(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_getContainerLoopAttributes() begin\n");
   int retval = 0;
   xmlXPathObjectPtr result = NULL;
   const char * fixedNodePath = SeqUtil_fixPath(rv->nodePath);

   if( (result = XmlUtils_getnodeset ("(child::LOOP/@*)",rv->context)) != NULL ) {
      parseLoopAttributes( result, fixedNodePath, _nodeDataPtr );
      retval = 1;
   }

   free((char *) fixedNodePath);
   xmlXPathFreeObject(result);
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_getContainerLoopAttributes() end\n");
   return retval;
}

/********************************************************************************
 * NodeFunction: Queries the context for the attributes of the FOR_EACH child of the
 * current node which may be the root node or a VALIDITY node.
********************************************************************************/
int Resource_getForEachAttributes(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   int retval = 0;
   SeqUtil_TRACE(TL_FULL_TRACE, "getForEachAttributes() begin\n");
   if( rv->forEachResourcesFound ){
      retval = 1;
      goto out;
   }

   xmlXPathObjectPtr result = XmlUtils_getnodeset("(child::FOR_EACH/@*)",rv->context);
   if( result != NULL ){
      parseForEachTarget(result,_nodeDataPtr);
      rv->forEachResourcesFound = 1;
   }

out_free:
   xmlXPathFreeObject(result);
out:
   SeqUtil_TRACE(TL_FULL_TRACE, "getForEachAttributes() end\n");
   return retval;
}

/********************************************************************************
 * NodeFunction: Queries the context for the attributes of the BATCH child of the
 * current node which may be the root node or a VALIDITY node.
********************************************************************************/
int Resource_getBatchAttributes(ResourceVisitorPtr rv,SeqNodeDataPtr _nodeDataPtr)
{
   int retval = 0;
   SeqUtil_TRACE(TL_FULL_TRACE, "getBatchAttributes() begin\n");
   if( rv->batchResourcesFound ){
      retval = 1;
      goto out;
   }

   xmlXPathObjectPtr result = XmlUtils_getnodeset("(child::BATCH/@*)",rv->context);
   if( result != NULL ){
      parseBatchResources(result,_nodeDataPtr);
      rv->batchResourcesFound = 1;
   }

out_free:
   xmlXPathFreeObject(result);
out:
   SeqUtil_TRACE(TL_FULL_TRACE, "getBatchAttributes() end\n");
   return retval;
}

/********************************************************************************
 * NodeFunction: Queries the context for DEPENDS_ON children of the current node
 * of the context and parses their data into the _nodeDataPtr.
********************************************************************************/
int Resource_getDependencies(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "getDependencies() begin\n");

   xmlXPathObjectPtr result = XmlUtils_getnodeset("(child::DEPENDS_ON)",rv->context);
   if( result != NULL )
      parseDepends(result,_nodeDataPtr,0);

out_free:
   xmlXPathFreeObject(result);
out:
   SeqUtil_TRACE(TL_FULL_TRACE, "getDependencies() end\n");
   return 0;
}

/********************************************************************************
 * NodeFucntion: Queries the context for the attributes of the ABORT_ACTION
 * child of the current node which may be the root node or a VALIDITY node.
********************************************************************************/
int Resource_getAbortActions(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   int retval = 0;
   SeqUtil_TRACE(TL_FULL_TRACE, "getAbortActions() begin\n");

   if( rv->abortActionFound ){
      retval = 1;
      goto out;
   }

   char * abortValue = NULL;
   xmlXPathObjectPtr result = XmlUtils_getnodeset("(child::ABORT_ACTION/@*)",rv->context);
   if( result != NULL ){
      parseAbortActions(result,_nodeDataPtr);
   } else if ( rv->defFile != NULL && (abortValue = SeqUtil_getdef(rv->defFile, "SEQ_DEFAULT_ABORT_ACTION", _nodeDataPtr->expHome))) {
      SeqNode_addAbortAction(_nodeDataPtr, abortValue);
   }

out_free:
   free(abortValue);
   xmlXPathFreeObject(result);
out:
   SeqUtil_TRACE(TL_FULL_TRACE, "getAbortActions() end\n");
   return retval;
}

/********************************************************************************
 * Sets the worker data of the node if a worker path is specified.
********************************************************************************/
int Resource_setWorkerData(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   int retval = RESOURCE_SUCCESS;
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_setWorkerData() begin\n");
   if( strcmp(_nodeDataPtr->workerPath,"") == 0){
      retval = RESOURCE_FAILURE;
      goto out;
   }

   SeqNodeDataPtr workerNodeDataPtr = nodeinfo( _nodeDataPtr->workerPath, "all", NULL, _nodeDataPtr->expHome, NULL, NULL);
   _nodeDataPtr->mpi=workerNodeDataPtr->mpi;
   _nodeDataPtr->catchup=workerNodeDataPtr->catchup;
   SeqNode_setCpu( _nodeDataPtr, workerNodeDataPtr->cpu );
   SeqNode_setCpuMultiplier( _nodeDataPtr, workerNodeDataPtr->cpu_multiplier);
   SeqNode_setQueue( _nodeDataPtr,  workerNodeDataPtr->queue );
   SeqNode_setMachine( _nodeDataPtr, workerNodeDataPtr->machine );
   SeqNode_setMemory( _nodeDataPtr,  workerNodeDataPtr->memory );
   SeqNode_setArgs( _nodeDataPtr,  workerNodeDataPtr->soumetArgs );
   SeqNode_setShell( _nodeDataPtr,  workerNodeDataPtr->shell );
   SeqNode_freeNode( workerNodeDataPtr );

out:
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_setWorkerData() end\n");
   return retval;
}

/********************************************************************************
 * Makes sure a machine is set if the one was not set.
********************************************************************************/
int Resource_validateMachine(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "validateMachine() begin\n");
   char * value = NULL;
   /* validate a machine has been provided */
   if ( strcmp(_nodeDataPtr->machine,"") == 0){
      /* get default machine*/
      if ( (value = SeqUtil_getdef( rv->defFile, "SEQ_DEFAULT_MACHINE", _nodeDataPtr->expHome )) != NULL ){
          SeqNode_setMachine( _nodeDataPtr, value );
      } else {
         raiseError(" ERROR: Required machine attribute of BATCH tag not found for node %s and SEQ_DEFAULT_MACHINE not found in definition file %s\n", _nodeDataPtr->name, rv->defFile);
      }
   }

   free(value);
   SeqUtil_TRACE(TL_FULL_TRACE, "validateMachine() end\n");
   return 1;
}

/********************************************************************************
 * Makes sure that a shell is set for the node it is not set.
********************************************************************************/
int Resource_setShell(ResourceVisitorPtr rv, SeqNodeDataPtr _nodeDataPtr)
{
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_setShell() begin\n");
   int retval = RESOURCE_SUCCESS;
   char * shellValue = NULL;

   if ( strcmp(_nodeDataPtr->shell,"") != 0){
      goto out;
   }

   /* get default shell*/
   if ( rv->defFile != NULL &&
         ((shellValue = SeqUtil_getdef( rv->defFile, "SEQ_DEFAULT_SHELL", _nodeDataPtr->expHome )) != NULL )){
      SeqNode_setShell( _nodeDataPtr, shellValue );
   } else {
      SeqNode_setShell( _nodeDataPtr, "/bin/ksh" );
   }

out_free:
   free(shellValue);
out:
   SeqUtil_TRACE(TL_FULL_TRACE, "Resource_setShell() end\n");
   return retval;
}

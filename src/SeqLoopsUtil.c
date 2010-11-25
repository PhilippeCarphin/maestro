#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include "SeqListNode.h"
#include "SeqNameValues.h"
#include "SeqNode.h"
#include "SeqUtil.h"
#include <string.h>
/*
#include <dirent.h>
#include <sys/stat.h>
#include <errno.h>
#include <sys/stat.h>
*/


static char* EXT_TOKEN = "+";


/* function to parse the loop arguments
   returns 0 if succeeds
   returns -1 if the function fais with an error
   cmd_args must be in the form "loop_name=value,loop_namex=valuex"
*/

int SeqLoops_parseArgs( SeqNameValuesPtr* nameValuesPtr, const char* cmd_args ) {
   char *tmpstrtok = NULL, *tmp_args = NULL;
   char loopName[50], loopValue[50];
   int isError = 0;
   
   /*printf( "SeqLoops_parseArgs cmd_args:%s\n", cmd_args ); */
   memset(loopName,'\0',sizeof loopName);
   memset(loopValue,'\0',sizeof loopValue);
   tmp_args = strdup( cmd_args );
   tmpstrtok = (char*) strtok( tmp_args, "," );
   while ( tmpstrtok != NULL ) {
      /* any alphanumeric characters and special chars
         _:/- are supported */
      sscanf( tmpstrtok, "%[A-Za-z0-9._:/-]=%[A-Za-z0-9._:/-]", &loopName, &loopValue );

      /*printf( "SeqLoops_parseArgs loopName:%s rigthValue:%s\n", loopName, loopValue );
      /*printf( "SeqLoops_parseArgs adding to list: %s\n", tmpstrtok );*/
      /* should add more syntax validation such as spaces not allowed... */
      if ( strlen( loopName ) == 0 || strlen( loopValue ) == 0 ) {
         isError = -1;
      } else {
         SeqNameValues_insertItem( nameValuesPtr, loopName, loopValue );
      }
      tmpstrtok = (char*) strtok(NULL,",");
   }
   /*printf( "SeqLoops_parseArgsdone exit status: %d\n", isError ); */
   free( tmp_args );
   return(isError);
}

/* function that returns the base extension of a node.
examples: 
extension=_1_2_3_4 will return _1_2_3
extension=_1 will return ""
*/
char* SeqLoops_getExtensionBase ( SeqNodeDataPtr _nodeDataPtr ) {
   char *split = NULL , *tmpExtension = NULL, *work_string = NULL ,*chreturn =NULL;
   int containerCount = 0;
   SeqLoopsPtr loopsContainerPtr = _nodeDataPtr->loops;
   work_string = strdup(_nodeDataPtr->extension);
   if( _nodeDataPtr->type == Loop || _nodeDataPtr->type == NpassTask ) {
      while( loopsContainerPtr != NULL ) {
         containerCount++;
         loopsContainerPtr = loopsContainerPtr->nextPtr;
      }
      split  = strrchr (work_string,EXT_TOKEN[0]);
      if (split != NULL) {
         *split = '\0';
      }
   }
   chreturn = strdup(work_string);
   free( tmpExtension );
   free( work_string );
   return chreturn;
}

/* converts an extension value to a NameValueList that can be used
to maestro argument. returns NULL if no conversion done.
example: 
   input _1_2_3
   output is a name_value_list something like 
   loop_name_a=1->loop_name_b=2->loop_name_c=3
  */
SeqNameValuesPtr SeqLoops_convertExtension ( SeqLoopsPtr loops_ptr, char* extension ) {
   SeqNameValuesPtr nameValuesPtr = NULL;
   char *token = NULL;
   char *leaf = NULL;
   token = (char*) strtok( extension, EXT_TOKEN );
   while ( token != NULL ) {
      free( leaf );
      leaf = (char*) SeqUtil_getPathLeaf( loops_ptr->loop_name );
      SeqNameValues_insertItem( &nameValuesPtr, leaf, token );

      loops_ptr = loops_ptr->nextPtr;
      token = (char*) strtok( NULL, EXT_TOKEN );
   }
   /*printf( "SeqLoops_convertExtension namevalues:\n" ); */
   SeqNameValues_printList( nameValuesPtr );
   /*printf( "SeqLoops_convertExtension done:\n" ); */
   return nameValuesPtr;
}

/* returns the value of a specific attribute from the attribute list of a loop item,
   return NULL if not found
   the attr_name is something like NAME, START, STEP, END,...
 */
char* SeqLoops_getLoopAttribute( SeqNameValuesPtr loop_attr_ptr, char* attr_name ) {
   char* returnValue = NULL;

   while ( loop_attr_ptr != NULL ) {
      /*printf("SeqLoops_getLoopAttribute looking for:%s found: %s=%s\n", 
         attr_name, loop_attr_ptr->name, loop_attr_ptr->value ); */
      if( strcmp( loop_attr_ptr->name, attr_name ) == 0 ) {
         returnValue = strdup( loop_attr_ptr->value );
         break;
      }
      loop_attr_ptr = loop_attr_ptr->nextPtr;
   }
   return returnValue;
}

/* changes the value of a specific attribute from the attribute list of a loop item,
   if not found, it will ADD it to the list
   the attr_name is something like NAME, START, STEP, END,...
 */
void SeqLoops_setLoopAttribute( SeqNameValuesPtr* loop_attr_ptr, char* attr_name, char* attr_value ) {
   int found = 0;
   SeqNameValuesPtr loopAttrPtr = *loop_attr_ptr;

   while ( loopAttrPtr != NULL ) {
      printf( "SeqLoops_setLoopAttribute looking for:%s found:%s \n", attr_name, loopAttrPtr->name );
      if( strcmp( loopAttrPtr->name, attr_name ) == 0 ) {
         found = 1;
         free(loopAttrPtr->value);
         loopAttrPtr->value = malloc( strlen(attr_value) + 1 );
         strcpy( loopAttrPtr->value, attr_value );
         break;
      }
      loopAttrPtr = loopAttrPtr->nextPtr;
   }
   if( !found ) {
      SeqNameValues_insertItem( loop_attr_ptr, attr_name, attr_value );
   }
}

/* returns the extension value that should be appended to the node_name using
   the list of container loops and the list of loop arguments
   returns NULL if validation fails
*/
char* SeqLoops_ContainerExtension( SeqLoopsPtr loops_ptr, SeqNameValuesPtr loop_args_ptr ) {
   SeqNameValuesPtr thisLoopArgPtr = NULL;
   int foundLoopArg = 0;
   char *loopContainerName = NULL, *loopLeafName = NULL;
   char* extension = NULL;
   int isError = 0;
   while( loops_ptr != NULL && isError == 0 ) {
      foundLoopArg = 0;
      loopContainerName = loops_ptr->loop_name;
      /*printf("SeqLoops_ContainerExtension looking for %s\n", loopContainerName ); */
      /* inside the SeqLoopsPtr, the loop_name value is stored with the full path node 
         of the loop while the loop_name function argument is only the leaf part */
      loopLeafName = (char*) SeqUtil_getPathLeaf( loopContainerName );
      /*printf("SeqLoops_ContainerExtension loopLeafName=%s\n", loopLeafName ); */
      thisLoopArgPtr = loop_args_ptr;
      while( thisLoopArgPtr != NULL && isError == 0 ) {
         /*printf("SeqLoops_ContainerExtension loop_name=%s loop_value=%s\n", thisLoopArgPtr->name, thisLoopArgPtr->value ); */
         if( strcmp( thisLoopArgPtr->name, loopLeafName ) == 0 ) {
            foundLoopArg = 1;
            SeqUtil_stringAppend( &extension, EXT_TOKEN );
            SeqUtil_stringAppend( &extension, thisLoopArgPtr->value );
            /*printf("SeqLoops_ContainerExtension found loop argument loop_name=%s loop_value=%s\n", thisLoopArgPtr->name, thisLoopArgPtr->value ); */
            break;
         }
         thisLoopArgPtr = thisLoopArgPtr->nextPtr;
      }

      isError = !foundLoopArg;

      free( loopLeafName );
      loops_ptr  = loops_ptr->nextPtr;
   }

   /*printf("SeqLoops_ContainerExtension extension value=%s\n", extension ); */
   if( isError == 1 )
      return NULL;

   return extension;
}

/* returns the extension value that should be appended to the node_name using
   the list of loop arguments. To be used if the node is of type Loop.
   returns NULL if validation fails
   node_name must be the leaf part of the node only.
*/
char* SeqLoops_NodeExtension( const char* node_name, SeqNameValuesPtr loop_args_ptr ) {

   int foundLoopArg = 0;
   char* extension = NULL;
   /*printf("SeqLoops_NodeExtension looking for %s\n", node_name ); */
   while( loop_args_ptr != NULL ) {
      /*printf("SeqLoops_NodeExtension loop_name=%s loop_value=%s\n", loop_args_ptr->name, loop_args_ptr->value ); */
      if( strcmp( loop_args_ptr->name, node_name ) == 0 ) {
         foundLoopArg = 1;
         SeqUtil_stringAppend( &extension, EXT_TOKEN );
         SeqUtil_stringAppend( &extension, loop_args_ptr->value );
         /*printf("SeqLoops_NodeExtension found loop argument loop_name=%s loop_value=%s\n", loop_args_ptr->name, loop_args_ptr->value ); */
         break;
      }
      loop_args_ptr = loop_args_ptr->nextPtr;
   }

   /*printf("SeqLoops_NodeExtension extension value=%s\n", extension ); */
   if( foundLoopArg == 0 )
      return NULL;

   return extension;
}


/* return the loop container extension values that the current node is in.
   to be used to check if a loop parent node is done,
   assuming that extension is set in  _nodeDataPtr->extension */
LISTNODEPTR SeqLoops_childExtensions( SeqNodeDataPtr _nodeDataPtr, SeqNameValuesPtr loop_args_ptr ) {
   SeqNameValuesPtr nodeSpecPtr = NULL;
   char tmp[20], *baseExtension;
   int loopStart = 0, loopStep = 0, loopEnd = 0, loopCount = 0;
   LISTNODEPTR loopExtensions = NULL;
   memset( tmp, '\0', sizeof tmp );
   baseExtension = SeqLoops_getExtensionBase( _nodeDataPtr );
   nodeSpecPtr = _nodeDataPtr->data;

   printf("SeqLoops_childExtensions extension:%s baseExtension:%s \n",_nodeDataPtr->extension, baseExtension );
   loopStart = atoi( SeqLoops_getLoopAttribute( nodeSpecPtr, "START" ) );
   if( strcmp( SeqLoops_getLoopAttribute( nodeSpecPtr, "TYPE" ), "LoopSet" ) == 0 ) { 
      loopStep = 1;
   } else {
      loopStep = atoi( SeqLoops_getLoopAttribute( nodeSpecPtr, "STEP" ) );
   }
   loopEnd = atoi( SeqLoops_getLoopAttribute( nodeSpecPtr, "END" ) );
   loopCount = loopStart;
   /*printf("SeqLoops_childExtensions loopStart:%d loopStep:%d loopEnd=%d \n", loopStart, loopStep, loopEnd ); */
   while( loopCount <= loopEnd ) {
      sprintf( tmp, "%s%s%d", baseExtension, EXT_TOKEN, loopCount );
      SeqListNode_insertItem( &loopExtensions, tmp );
      loopCount = loopCount + loopStep;
   }

   return loopExtensions;
}

/* returns 1 if the parent of a node is a loop container */
int SeqLoops_isParentLoopContainer ( const SeqNodeDataPtr _nodeDataPtr ) {
   int value = 0;
   SeqLoopsPtr loopsPtr =  _nodeDataPtr->loops;
   SeqUtil_TRACE( "SeqLoops_isParentLoopContainer.isParentLoopContainer() container = %s\n", _nodeDataPtr->container );
   while( loopsPtr != NULL ) {
      SeqUtil_TRACE( "SeqLoops_isParentLoopContainer.isParentLoopContainer() container loop_name = %s\n", loopsPtr->loop_name );
      if( strcmp( loopsPtr->loop_name, _nodeDataPtr->container ) == 0 ) {
         value = 1;
         break;
      }
      loopsPtr  = loopsPtr->nextPtr;
   }
   SeqUtil_TRACE( "SeqLoops_isParentLoopContainer.isParentLoopContainer() return value = %d\n", value );
   return value;
}

/* add escape characters in front of the loop separator character (+)
so that it can be used in pattern matching */
char* SeqLoops_getExtPattern ( char* extension ) {
   char tmp[100];
   int i=0,j=0;
   memset( tmp, '\0', sizeof(tmp) );
   while( extension[i] != '\0' ) {
      if( extension[i] == EXT_TOKEN[0] ) {
         tmp[j] = '\\';
         tmp[j+1] = extension[i];
         j = j+2;
      } else {
         tmp[j] = extension[i];
         j++;
      }
      i++;
   }
   tmp[j] = '\0';
   SeqUtil_TRACE( "SeqLoops_getExtPattern() return value = %s\n", tmp );   
   return strdup(tmp);
}

/* return the loop arguments from Name-Value list to char pointer */
char* SeqLoops_getLoopArgs( SeqNameValuesPtr _loop_args ) {
   char* value = NULL;
   SeqNameValuesPtr myLoopArgs = _loop_args;
   SeqUtil_stringAppend( &value, "" );
   while( myLoopArgs!= NULL ) {
      SeqUtil_stringAppend( &value, myLoopArgs->name );      
      SeqUtil_stringAppend( &value, "=" );
      SeqUtil_stringAppend( &value, myLoopArgs->value );
      if( myLoopArgs->nextPtr != NULL ) {
         SeqUtil_stringAppend( &value, "," );
      }
      myLoopArgs = myLoopArgs->nextPtr;
   }
   return value;
}

void SeqLoops_printLoopArgs( SeqNameValuesPtr _loop_args, const char* _caller ) {
   char* value = SeqLoops_getLoopArgs( _loop_args );
   printf( "%s loop arguments: %s\n", _caller, value );
   free( value );
}

/* If the user doesn't provide a loop extension, we're returning the first loop iteration
   If the user provides a loop extension, we're returning the current extension
   We're assuming that the _nodeDataPtr->extension has already been set previously
   To be used when the current node is of type loop */
SeqNameValuesPtr SeqLoops_submitLoopArgs( const SeqNodeDataPtr _nodeDataPtr, SeqNameValuesPtr _loop_args ) {
   SeqNameValuesPtr newLoopsArgsPtr = NULL, loopArgsTmpPtr = NULL;
   SeqNameValuesPtr nodeSpecPtr = NULL;
   char *loopStart = NULL;
   int foundExt = 0;
   loopArgsTmpPtr = _loop_args;
   while( loopArgsTmpPtr != NULL ) {
      if( strcmp( loopArgsTmpPtr->name, _nodeDataPtr->nodeName ) == 0 ) {
         /* ok the user has provided an extension */
         foundExt = 1;
         break;
      }
      loopArgsTmpPtr  = loopArgsTmpPtr->nextPtr;
   }
   /* start with same as current iteration */
   newLoopsArgsPtr = SeqNameValues_clone( _loop_args );

   if( ! foundExt ) {
      /* get the first loop iteration */
      nodeSpecPtr = _nodeDataPtr->data;
      /* for now, we only support numerical data */
      loopStart = SeqLoops_getLoopAttribute( nodeSpecPtr, "START" );
      fprintf(stdout,"SeqLoops_submitLoopArgs() loopstart:%s\n", loopStart);
      SeqLoops_setLoopAttribute( &newLoopsArgsPtr, _nodeDataPtr->nodeName, loopStart );
   }
   free( loopStart );
   return newLoopsArgsPtr;
}

/* returns 1 if we have reach the last iteration of the loop,
   returns 0 otherwise
*/
int SeqLoops_isLastIteration( const SeqNodeDataPtr _nodeDataPtr, SeqNameValuesPtr _loop_args ) {
   SeqNameValuesPtr nodeSpecPtr = NULL;
   char tmp[20];
   char *loopCurrentStr = NULL, *loopStepStr = NULL, *loopEndStr = NULL, *loopSetStr = NULL;
   int loopCurrent = 0, loopStep = 0, loopTotal = 0;
   int isLast = 0;
   memset( tmp, '\0', sizeof(tmp) );
   /* get the first loop iteration */
   nodeSpecPtr = _nodeDataPtr->data;

   /* for now, we only support numerical data */
   /* get the current iteration from the loop arguments */
   if( (loopCurrentStr = SeqLoops_getLoopAttribute( _loop_args, _nodeDataPtr->nodeName ) ) != NULL )
      loopCurrent = atoi(loopCurrentStr);
   /* get the iteration step */
   if( ( loopStepStr = SeqLoops_getLoopAttribute( nodeSpecPtr, "STEP" ) ) != NULL )
      loopStep = atoi(loopStepStr);
   /* if the set has a value, the next iteration is (current iteration + set value)*/
   if( ( loopSetStr = SeqLoops_getLoopAttribute( nodeSpecPtr, "SET" ) ) != NULL )
      loopStep = atoi(loopSetStr);
   /* get the iteration end */
   if( ( loopEndStr = SeqLoops_getLoopAttribute( nodeSpecPtr, "END" ) ) != NULL )
      loopTotal = atoi(loopEndStr);

   fprintf(stdout,"SeqLoops_isLastIteration() loopCurrent:%d loopStep:%d loopTotal:%d\n", loopCurrent, loopStep, loopTotal);

   /* have we reached the end? */
   if( (loopCurrent + loopStep) > loopTotal ) {
      isLast = 1;
   }
   
   return isLast;
}

/* returns the next loop iteration of the current loop node as a
   name-value argument list so that it can be used in an maestro call.
   returns NULL if we have reached the end
   */
SeqNameValuesPtr SeqLoops_nextLoopArgs( const SeqNodeDataPtr _nodeDataPtr, SeqNameValuesPtr _loop_args ) {
   SeqNameValuesPtr newLoopsArgsPtr = NULL;
   SeqNameValuesPtr nodeSpecPtr = NULL;
   char tmp[20], *loopSetStr = NULL;
   int loopCurrent = 0, loopStep = 0, loopTotal = 0;
   memset( tmp, '\0', sizeof(tmp) );
   /* get the first loop iteration */
   nodeSpecPtr = _nodeDataPtr->data;
   /* for now, we only support numerical data */
   loopCurrent = atoi( SeqLoops_getLoopAttribute( _loop_args, _nodeDataPtr->nodeName ) );
   if( strcmp( SeqLoops_getLoopAttribute( nodeSpecPtr, "TYPE" ), "LoopSet" ) == 0 ) { 
      /* if we're dealing with a set value, the next iteration is (current + set  value) */
      loopSetStr = SeqLoops_getLoopAttribute( nodeSpecPtr, "SET" );
      loopStep = atoi( loopSetStr );
   } else {
      loopStep = atoi( SeqLoops_getLoopAttribute( nodeSpecPtr, "STEP" ) );
   }
   loopTotal = atoi( SeqLoops_getLoopAttribute( nodeSpecPtr, "END" ) );
   fprintf(stdout,"SeqLoops_nextLoopArgs() loopCurrent:%d loopStep:%d loopTotal:%d\n", loopCurrent, loopStep, loopTotal);

   /* calculate next iteration */
   if( (loopCurrent + loopStep) <= loopTotal ) {
      sprintf( tmp, "%d", loopCurrent + loopStep );
      newLoopsArgsPtr = SeqNameValues_clone( _loop_args );
      SeqLoops_setLoopAttribute( &newLoopsArgsPtr, _nodeDataPtr->nodeName, tmp );
   }
   return newLoopsArgsPtr;
}

/* function that validates loop arguments
returns 0 if validations fails
returns 1 if succeeds
*/
int SeqLoops_validateLoopArgs( const SeqNodeDataPtr _nodeDataPtr, SeqNameValuesPtr _loop_args ) {

   SeqLoopsPtr loopsPtr = _nodeDataPtr->loops;
   SeqNameValuesPtr loopArgsTmpPtr = NULL;
   char *loopExtension = NULL;

   /* We're validating NpassTask here as well even though it is not a loop node
    * It is an indexed node so we're sharing some index logic here */

   /* validate NpassTask */
   if ( _nodeDataPtr->type == NpassTask ) {
      if( _loop_args == NULL ) {
         raiseError( "SeqLoops_validateLoopArgs(): No index arguments found for NpassTask Node!\n" );
      }
      /* validate that user has given format "-l nodename=index_value" where nodename must be current node */ 
      if( SeqLoops_getLoopAttribute( _loop_args, _nodeDataPtr->nodeName )  == NULL ) {
         raiseError( "SeqLoops_validateLoopArgs(): Invalid index argument format for NpassTask Node!\n" );
      }
   }

   /* validate loop containers */
   if( loopsPtr != NULL ) {
      /* check if the user has given us argument for looping */
      if( _loop_args == NULL ) {
         raiseError( "SeqLoops_validateLoopArgs(): No loop arguments found for container loop!\n" );
      }

      /* build loop extension for containers */
      if( (loopExtension = (char*) SeqLoops_ContainerExtension( loopsPtr, _loop_args )) == NULL ) {
         raiseError( "SeqLoops_validateLoopArgs(): Missing loop arguments for container loop!\n" );
      }
      SeqUtil_TRACE( "SeqLoops_validateLoopArgs() loop extension:%s\n", loopExtension );
   }

   /* build extension for current node if loop */
   if( _nodeDataPtr->type == Loop ||  _nodeDataPtr->type == NpassTask ) {
      loopArgsTmpPtr = _loop_args;
      while( loopArgsTmpPtr != NULL ) {
         if( strcmp( loopArgsTmpPtr->name, _nodeDataPtr->nodeName ) == 0 ) {
            SeqUtil_stringAppend( &loopExtension, EXT_TOKEN );
            SeqUtil_stringAppend( &loopExtension, loopArgsTmpPtr->value );
         }
         loopArgsTmpPtr  = loopArgsTmpPtr->nextPtr;
      }
   }
   SeqNode_setExtension( _nodeDataPtr, loopExtension );
   free( loopExtension );
   return(1);
}

char* SeqLoops_getExtFromLoopArgs( SeqNameValuesPtr _loop_args ) {
   char* loopExtension = NULL;
   while( _loop_args != NULL ) {
      SeqUtil_stringAppend( &loopExtension, EXT_TOKEN );
      SeqUtil_stringAppend( &loopExtension, _loop_args->value );
      _loop_args  = _loop_args->nextPtr;
   }
   printf( "SeqLoops_getExtFromLoopArgs: %s\n", loopExtension );
   return loopExtension;
}

/* returns only the loop arguments of parent loop containers
 * For instance, if  arguments is: outer_loop=2,inner_loop=3,
 * this function will return outer_loop=2 in the NameValue list
 *
 * NAME=outer_loop VALUE=2
 *
 *
 */
SeqNameValuesPtr SeqLoops_getContainerArgs (const SeqNodeDataPtr _nodeDataPtr, SeqNameValuesPtr _loop_args ) {
   SeqNameValuesPtr loopArgsTmpPtr = _loop_args;
   SeqNameValuesPtr newLoopsArgsPtr = NULL;
   while( loopArgsTmpPtr != NULL ) {
      if( strcmp( loopArgsTmpPtr->name, _nodeDataPtr->nodeName ) == 0 ) {
         break;
      }
      SeqNameValues_insertItem( &newLoopsArgsPtr,  loopArgsTmpPtr->name, loopArgsTmpPtr->value);
      loopArgsTmpPtr  = loopArgsTmpPtr->nextPtr;
   }
   return newLoopsArgsPtr;
}

/* returns the loop arguments for the first set iterations for a loop set
 * however, if the _loop_args already contains a value for the current loop,
 * it means the set is already started, we will only submit the (current + set) iteration
 * Example Set loop 3, start value=1, the returned NameValue list is something like:
 *            NAME: outer_loop VALUE=1
 *            NAME: outer_loop VALUE=2
 *            NAME: outer_loop VALUE=3
 */
SeqNameValuesPtr SeqLoops_getLoopSetArgs( const SeqNodeDataPtr _nodeDataPtr, SeqNameValuesPtr _loop_args ) {
   SeqNameValuesPtr newLoopsArgsPtr = NULL;
   SeqNameValuesPtr nodeSpecPtr = NULL;
   SeqNameValuesPtr loopArgsTmpPtr = _loop_args;


   char tmp[20];
   int loopStart = 0, loopEnd= 0, loopSet = 0,
       loopCount = 0, loopSetCount = 0;
   memset( tmp, '\0', sizeof(tmp) );

   int foundExt = 0;
   /* see if the user has provied an ext for this loop */
   while( loopArgsTmpPtr != NULL ) {
      if( strcmp( loopArgsTmpPtr->name, _nodeDataPtr->nodeName ) == 0 ) {
         /* ok the user has provided an extension for the current loop*/
         foundExt = 1;
         break;
      }
      loopArgsTmpPtr  = loopArgsTmpPtr->nextPtr;
   }

   if( ! foundExt ) {
      /* we need to submit the full set */
      nodeSpecPtr = _nodeDataPtr->data;

      loopStart = atoi( SeqLoops_getLoopAttribute( nodeSpecPtr, "START" ) );
      loopSet = atoi( SeqLoops_getLoopAttribute( nodeSpecPtr, "SET" ) );
      loopEnd = atoi( SeqLoops_getLoopAttribute( nodeSpecPtr, "END" ) );
      fprintf(stdout,"SeqLoops_getLoopSetArgs() loopstart:%d loopSet:%d loopEnd:%d\n", loopStart, loopSet, loopEnd);

      loopCount = loopStart;
      /* calculate next iteration */
      while( loopCount <= loopEnd && loopSetCount < loopSet ) {
         sprintf( tmp, "%d", loopCount );
         SeqNameValues_insertItem( &newLoopsArgsPtr,  _nodeDataPtr->nodeName, tmp);
         loopCount++;
         loopSetCount++;
      }
   } else {
      /* we need to submit only one iteration */
      newLoopsArgsPtr = SeqNameValues_clone( loopArgsTmpPtr );
   }
   /* SeqNameValues_printList( newLoopsArgsPtr); */
   return newLoopsArgsPtr;
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <assert.h>
#include "SeqNode.h"
#include "SeqUtil.h"
static char* FamilyTypeString = "Family";
static char* TaskTypeString = "Task";
static char* NpassTaskTypeString = "NpassTask";
static char* LoopTypeString = "Loop";
static char* CaseTypeString = "Case";
static char* CaseItemTypeString = "CaseItem";
static char* ModuleTypeString = "Module";

/* this function is just a simple enabling of printf calls when
the user passes -d option */
char* SeqNode_getTypeString( SeqNodeType _node_type ) {
   char* typePtr = NULL;
   switch (_node_type) {
      case Task:
         typePtr = TaskTypeString;
         break;
      case NpassTask:
         typePtr = NpassTaskTypeString;
         break;
      case Family:
         typePtr = FamilyTypeString;
         break;
      case Module:
         typePtr = ModuleTypeString;
         break;
      case Loop:
         typePtr = LoopTypeString;
         break;
      case Case:
         typePtr = CaseTypeString;
         break;
      case CaseItem:
         typePtr = CaseItemTypeString;
         break;
      default:
         typePtr = TaskTypeString;
   }
   return typePtr;
}

void SeqNode_setName ( SeqNodeDataPtr node_ptr, const char* name ) {
   if ( name != NULL ) {
      free( node_ptr->name );
      node_ptr->name = malloc( strlen(name) + 1 );
      strcpy( node_ptr->name, name );
   }
}

void SeqNode_setNodeName ( SeqNodeDataPtr node_ptr, const char* nodeName ) {
   if ( nodeName != NULL ) {
      free( node_ptr->nodeName );
      node_ptr->nodeName = malloc( strlen(nodeName) + 1 );
      strcpy( node_ptr->nodeName, nodeName );
   }
}

void SeqNode_setModule ( SeqNodeDataPtr node_ptr, const char* module ) {
   if ( module != NULL ) {
      free( node_ptr->module );
      node_ptr->module = malloc( strlen(module) + 1 );
      strcpy( node_ptr->module, module );
   }
}

void SeqNode_setIntramoduleContainer ( SeqNodeDataPtr node_ptr, const char* intramodule_container ) {
   if( intramodule_container != NULL ) {
      free( node_ptr->intramodule_container );
      node_ptr->intramodule_container = malloc( strlen(intramodule_container) + 1 );
      strcpy( node_ptr->intramodule_container, intramodule_container );
   }
}

void SeqNode_setContainer ( SeqNodeDataPtr node_ptr, const char* container ) {
   if( container != NULL ) {
      free( node_ptr->container );
      node_ptr->container = malloc( strlen(container) + 1 );
      strcpy( node_ptr->container, container );
   }
}
/* not needed anymore since this can be derived from module */
/*
void SeqNode_setMasterfile ( SeqNodeDataPtr node_ptr, const char* masterfile ) {
   if ( masterfile != NULL ) {
      free( node_ptr->masterfile );
      node_ptr->masterfile = malloc( strlen(masterfile) + 1 );
      strcpy( node_ptr->masterfile, masterfile );
   }
}
*/

void SeqNode_setCpu ( SeqNodeDataPtr node_ptr, const char* cpu ) {
   char *tmpstrtok=NULL;
   char *tmpCpu=NULL;
   if ( cpu != NULL ) {
      free( node_ptr->cpu );
      node_ptr->cpu = malloc( strlen(cpu) + 1 );
      strcpy( node_ptr->cpu, cpu );
      tmpCpu=strdup(cpu);
  
      /* parse NPEX */
      tmpstrtok = (char*) strtok( tmpCpu, "x" );
      if ( tmpstrtok != NULL ) {
          free( node_ptr->npex );
	  node_ptr->npex=malloc( strlen(tmpstrtok) +1); 
	  strcpy(node_ptr->npex, tmpstrtok);
      }
      /* NPEY */
      tmpstrtok = (char*) strtok( NULL, "x" );
      if ( tmpstrtok != NULL ) {
          free( node_ptr->npey );
	  node_ptr->npey=malloc( strlen(tmpstrtok) +1); 
	  strcpy(node_ptr->npey, tmpstrtok);
      }
      /* OMP */
      tmpstrtok = (char*) strtok( NULL, "x" );
      if ( tmpstrtok != NULL ) {
          free( node_ptr->omp );
	  node_ptr->omp=malloc( strlen(tmpstrtok) +1); 
	  strcpy(node_ptr->omp, tmpstrtok);
      }
   free (tmpCpu);
   }
}

void SeqNode_setMachine ( SeqNodeDataPtr node_ptr, const char* machine ) {
   if ( machine != NULL ) {
      free( node_ptr->machine );
      node_ptr->machine = malloc( strlen(machine) + 1 );
      strcpy( node_ptr->machine, machine );
   }
}

void SeqNode_setMemory ( SeqNodeDataPtr node_ptr, const char* memory ) {
   if ( memory != NULL ) {
      free( node_ptr->memory );
      node_ptr->memory = malloc( strlen(memory) + 1 );
      strcpy( node_ptr->memory, memory );
   }
}

void SeqNode_setQueue ( SeqNodeDataPtr node_ptr, const char* queue ) {
   if ( queue != NULL ) {
      free( node_ptr->queue );
      node_ptr->queue = malloc( strlen(queue) + 1 );
      strcpy( node_ptr->queue, queue );
   }
}

void SeqNode_setSuiteName ( SeqNodeDataPtr node_ptr, const char* suiteName ) {
   if ( suiteName != NULL ) {
      free( node_ptr->suiteName );
      node_ptr->suiteName = malloc( strlen(suiteName) + 1 );
      strcpy( node_ptr->suiteName, suiteName );
   }
}

void SeqNode_setInternalPath ( SeqNodeDataPtr node_ptr, const char* path ) {
   if ( path != NULL ) {
      free( node_ptr->taskPath );
      node_ptr->taskPath = malloc( strlen(path) + 1 );
      strcpy( node_ptr->taskPath, path );
   }
}

void SeqNode_setArgs ( SeqNodeDataPtr node_ptr, const char* args ) {
   if ( args != NULL ) {
      free( node_ptr->args );
      node_ptr->args = malloc( strlen(args) + 1 );
      strcpy( node_ptr->args, args );
   }
}

void SeqNode_setAlias ( SeqNodeDataPtr node_ptr, const char* alias ) {
   if ( alias != NULL ) {
      free( node_ptr->alias );
      node_ptr->alias = malloc( strlen(alias) + 1 );
      strcpy( node_ptr->alias, alias );
   }
}

void SeqNode_setDatestamp( SeqNodeDataPtr node_ptr, const char* datestamp) {
   if ( datestamp != NULL ) {
      free( node_ptr->datestamp );
      node_ptr->datestamp = malloc( strlen(datestamp) + 1 );
      strcpy( node_ptr->datestamp, datestamp );
   }
}

void SeqNode_setWorkdir( SeqNodeDataPtr node_ptr, const char* workdir) {
   if ( workdir != NULL ) {
      free( node_ptr->workdir);
      node_ptr->workdir = malloc( strlen(workdir) + 1 );
      strcpy( node_ptr->workdir, workdir);
   }
}

void SeqNode_setExtension ( SeqNodeDataPtr node_ptr, const char* extension ) {
   if ( extension != NULL ) {
      free( node_ptr->extension );
      node_ptr->extension = malloc( strlen(extension) + 1 );
      strcpy( node_ptr->extension, extension );
   }
}

/* returns ptr to newly allocated memory structure
 to store a new name value link list */
SeqLoopsPtr SeqNode_allocateLoopsEntry ( SeqNodeDataPtr node_ptr ) {
   SeqLoopsPtr loopsPtr = NULL;
   SeqUtil_TRACE( "SeqNode_allocateLoopsEntry()\n" );
   if ( node_ptr->loops == NULL ) {
      node_ptr->loops = malloc( sizeof (SeqLoops) );
      loopsPtr = node_ptr->loops;
   } else {
      loopsPtr = node_ptr->loops;
      /* position ourselves at the end of the list */
      while( loopsPtr->nextPtr != NULL ) {
         loopsPtr = loopsPtr->nextPtr;
      }
   
      /* allocate memory for new data */
      loopsPtr->nextPtr = malloc( sizeof(SeqLoops) );
      /* go to memory for new data */
      loopsPtr = loopsPtr->nextPtr;
   }
   loopsPtr->nextPtr = NULL;
   loopsPtr->values = NULL;
   loopsPtr->loop_name = NULL;
   SeqUtil_TRACE( "SeqNode_allocateLoopsEntry() done\n" );
   return loopsPtr;
}

/* returns ptr to newly allocated memory structure 
   to store a new name value link list */
SeqDependenciesPtr SeqNode_allocateDepsEntry ( SeqNodeDataPtr node_ptr ) {
   SeqDependenciesPtr deps_ptr = NULL;
   SeqUtil_TRACE( "SeqNode_allocateDepsEntry()\n" );
   if ( node_ptr->depends == NULL ) {
      node_ptr->depends = malloc( sizeof (SeqDependencies) );
      deps_ptr = node_ptr->depends;
   } else {
      deps_ptr = node_ptr->depends;
      /* position ourselves at the end of the list */
      while( deps_ptr->nextPtr != NULL ) {
         deps_ptr = deps_ptr->nextPtr;
      }

      /* allocate memory for new data */
      deps_ptr->nextPtr = malloc( sizeof(SeqDependencies) );
      /* go to memory for new data */
      deps_ptr = deps_ptr->nextPtr;
   }
   deps_ptr->nextPtr = NULL;
   deps_ptr->dependencyItem = NULL;
   SeqUtil_TRACE( "SeqNode_allocateDepsEntry() done\n" );
   return deps_ptr;
}

/* returns ptr to newly allocated memory structure
   to store a name value pair */
SeqNameValuesPtr SeqNode_allocateDepsNameValue ( SeqDependenciesPtr deps_ptr ) {
   SeqNameValuesPtr nameValuesPtr = NULL;

   SeqUtil_TRACE( "SeqNode_allocateDepsNameValue()\n" );
   assert( deps_ptr != NULL );
   if ( deps_ptr->dependencyItem == NULL ) {
      deps_ptr->dependencyItem = malloc( sizeof (SeqNameValues) );
      nameValuesPtr = deps_ptr->dependencyItem;
   } else {
      nameValuesPtr = deps_ptr->dependencyItem;
      /* position ourselves at the end of the list */
      while( nameValuesPtr->nextPtr != NULL ) {
         nameValuesPtr = nameValuesPtr->nextPtr;
      }

      /* allocate memory for new data */
      nameValuesPtr->nextPtr = malloc( sizeof(SeqNameValues) );
      /* go to memory for new data */
      nameValuesPtr = nameValuesPtr->nextPtr;
   }
   /* set end of list */
   nameValuesPtr->nextPtr = NULL;
   nameValuesPtr->name = NULL;
   nameValuesPtr->value = NULL;
   SeqUtil_TRACE( "SeqNode_allocateDepsNameValue() done\n" );
   return nameValuesPtr;
}

/* allocates and store the name-value pair in the
   name-value structure */
void SeqNode_setDepsNameValue (SeqNameValuesPtr name_values_ptr, char* name, char* value ) {
   /* printf ("SeqNode_setDepsNameValue name=%s value=%s\n", name , value ); */
   name_values_ptr->name = malloc( sizeof(char) * ( strlen( name ) + 1) );
   strcpy( name_values_ptr->name, (char*)name );
   if ( value != NULL ) {
      name_values_ptr->value = malloc( sizeof(char) * ( strlen( value ) + 1) );
      strcpy( name_values_ptr->value, (char*)value );
   } else {
      name_values_ptr->value = malloc( sizeof(char) * 2);
      strcpy( name_values_ptr->value, "" );
   }
}

/* add dependency of type node i.e. tasks/family  */
void SeqNode_addNodeDependency ( SeqNodeDataPtr node_ptr, SeqDependsType type, char* dep_node_name, char* dep_node_path,
                         char* dep_user, char* dep_exp, char* dep_status, char* dep_index, char* local_index, char* dep_hour) {
   SeqDependenciesPtr deps_ptr = NULL;
   SeqNameValuesPtr nameValuesPtr = NULL;
   SeqUtil_TRACE( "SeqNode_addNodeDependency() dep_node=%s, dep_node_path=%s, dep_user=%s, dep_exp=%s, dep_status=%s dep_index=%s, local_index=%s\n",
      dep_node_name, dep_node_path, dep_user, dep_exp, dep_status, dep_index, local_index );
   deps_ptr = SeqNode_allocateDepsEntry( node_ptr );
   deps_ptr->type = type;
   nameValuesPtr = deps_ptr->dependencyItem;
   nameValuesPtr = SeqNode_allocateDepsNameValue (deps_ptr);
   SeqNode_setDepsNameValue ( nameValuesPtr, "NAME", dep_node_name );

   nameValuesPtr = SeqNode_allocateDepsNameValue (deps_ptr);
   SeqNode_setDepsNameValue ( nameValuesPtr, "INDEX", dep_index );

   nameValuesPtr = SeqNode_allocateDepsNameValue (deps_ptr);
   SeqNode_setDepsNameValue ( nameValuesPtr, "USER", dep_user );

   nameValuesPtr = SeqNode_allocateDepsNameValue (deps_ptr);
   SeqNode_setDepsNameValue ( nameValuesPtr, "EXP", dep_exp );

   nameValuesPtr = SeqNode_allocateDepsNameValue (deps_ptr);
   SeqNode_setDepsNameValue ( nameValuesPtr, "STATUS", dep_status );

   nameValuesPtr = SeqNode_allocateDepsNameValue (deps_ptr);
   SeqNode_setDepsNameValue ( nameValuesPtr, "LOCAL_INDEX", local_index );

   nameValuesPtr = SeqNode_allocateDepsNameValue (deps_ptr);
   SeqNode_setDepsNameValue ( nameValuesPtr, "HOUR", dep_hour );
}

/* add dependency of type date i.e. not sure how we will implement this yet */
void SeqNode_addDateDependency ( SeqNodeDataPtr node_ptr, char* date ) {
   SeqDependenciesPtr deps_ptr = NULL;
   SeqNameValuesPtr nameValuesPtr = NULL;

   deps_ptr = SeqNode_allocateDepsEntry( node_ptr );
   deps_ptr->type = DateDependancy;
   nameValuesPtr = deps_ptr->dependencyItem;

   nameValuesPtr = SeqNode_allocateDepsNameValue (deps_ptr);
   SeqNode_setDepsNameValue ( nameValuesPtr, "DATE", date );
}

void SeqNode_addSubmit ( SeqNodeDataPtr node_ptr, char* data ) {
   SeqListNode_insertItem( &(node_ptr->submits), data );
}

void SeqNode_addSibling ( SeqNodeDataPtr node_ptr, char* data ) {
   SeqListNode_insertItem( &(node_ptr->siblings), data );
}

void SeqNode_addAbortAction ( SeqNodeDataPtr node_ptr, char* data ) {
   SeqListNode_insertItem( &(node_ptr->abort_actions), data );
}

/* default numerical loop with start, step, end */
void SeqNode_addNumLoop ( SeqNodeDataPtr node_ptr, 
   char* loop_name, char* start, char* step, char* end ) {
   SeqLoopsPtr loopsPtr = NULL;
   SeqUtil_TRACE( "SeqNode_addNumLoop() loop_name=%s, start=%s, step=%s, end=%s, \n",loop_name, start, step, end );

   loopsPtr = SeqNode_allocateLoopsEntry( node_ptr );
   loopsPtr->type = Numerical;
   loopsPtr->loop_name = strdup( loop_name );
   /* SeqNameValues_insertItem( &loopsPtr->values, "NAME", loop_name ); */
   SeqNameValues_insertItem( &loopsPtr->values, "TYPE", "Default");
   SeqNameValues_insertItem( &loopsPtr->values, "START", start );
   SeqNameValues_insertItem( &loopsPtr->values, "STEP", step );
   SeqNameValues_insertItem( &loopsPtr->values, "END", end );
   /* SeqNameValues_printList( loopsPtr->values ); */
}

/* set looping */
void SeqNode_addNumSetLoop ( SeqNodeDataPtr node_ptr, 
   char* loop_name, char* start, char* set, char* end ) {
   SeqLoopsPtr loopsPtr = NULL;
   SeqUtil_TRACE( "SeqNode_addNumSetLoop() loop_name=%s, start=%s, set=%s, end=%s, \n",loop_name, start, set, end );

   loopsPtr = SeqNode_allocateLoopsEntry( node_ptr );
   loopsPtr->type = Numerical;
   loopsPtr->loop_name = strdup( loop_name );
   /* SeqNameValues_insertItem( &loopsPtr->values, "NAME", loop_name ); */
   SeqNameValues_insertItem( &loopsPtr->values, "TYPE", "LoopSet");
   SeqNameValues_insertItem( &loopsPtr->values, "START", start );
   SeqNameValues_insertItem( &loopsPtr->values, "SET", set );
   SeqNameValues_insertItem( &loopsPtr->values, "END", end );
   /* SeqNameValues_printList( loopsPtr->values ); */
}

void SeqNode_addSpecificData ( SeqNodeDataPtr node_ptr, char* name, char* value ) {
   char* tmp = NULL;
   int count = 0;
   /* to allow easy comparison, I convert everthing to upper case */
   tmp = strdup( name );
   while( name[count] != '\0' ) {
      tmp[count] = toupper(name[count]);
      count++;
   }
   tmp[count] = '\0';
   /* SeqUtil_TRACE( "SeqNode.SeqNode_addSpecificData() called name:%s value:%s\n", tmp, value ); */
   SeqNameValues_insertItem( &(node_ptr->data), tmp, value );
   free( tmp );
}

void SeqNode_setError ( SeqNodeDataPtr node_ptr, const char* message ) {
   node_ptr->error = 1;
   node_ptr->errormsg = malloc( strlen( message ) + 1 );
   strcpy( node_ptr->errormsg, message );
}

void SeqNode_init ( SeqNodeDataPtr nodePtr ) {
   nodePtr->type = Task;
   nodePtr->name = NULL;
   nodePtr->nodeName = NULL;
   nodePtr->container = NULL;
   nodePtr->intramodule_container = NULL;
   nodePtr->module = NULL;
   nodePtr->masterfile = NULL;
   nodePtr->cpu = NULL;
   nodePtr->npex = NULL;
   nodePtr->npey = NULL;
   nodePtr->omp = NULL; 
   nodePtr->queue = NULL;
   nodePtr->machine = NULL;
   nodePtr->memory = NULL;
   nodePtr->silent = 0;
   nodePtr->catchup = 4;
   nodePtr->wallclock = 3;
   nodePtr->mpi = 0;
   nodePtr->alias = NULL;
   nodePtr->args = NULL;
   nodePtr->depends = NULL;
   nodePtr->submits = NULL;
   nodePtr->abort_actions = NULL;
   nodePtr->siblings = NULL;
   nodePtr->loops = NULL;
   nodePtr->data = NULL;
   nodePtr->taskPath = NULL;
   nodePtr->suiteName = NULL;
   nodePtr->extension = NULL;
   nodePtr->datestamp = NULL;
   nodePtr->workdir = NULL;
   SeqNode_setName( nodePtr, "" );
   SeqNode_setContainer( nodePtr, "" );
   SeqNode_setIntramoduleContainer( nodePtr, "" );
   SeqNode_setModule( nodePtr, "" );
   /* SeqNode_setMasterfile( nodePtr, "" ); */
   SeqNode_setCpu( nodePtr, "1" );
   SeqNode_setQueue( nodePtr, "null" );
   SeqNode_setMachine( nodePtr, "dorval-ib" );
   SeqNode_setMemory( nodePtr, "40M" );
   SeqNode_setArgs( nodePtr, "" );
   SeqNode_setAlias( nodePtr, "" );
   SeqNode_setInternalPath( nodePtr, "" );
   SeqNode_setExtension( nodePtr, "" );
   SeqNode_setDatestamp( nodePtr, "" );
   SeqNode_setWorkdir( nodePtr, "" );
   nodePtr->error = 0;
   nodePtr->errormsg = NULL;
}

void SeqNode_printNode ( SeqNodeDataPtr node_ptr, const char* filters ) {

   int showAll = 0, showCfgPath = 0, showTaskPath = 0, showRessource = 0, showType = 0, showNode = 0;
   SeqNameValuesPtr nameValuesPtr = NULL ;
   SeqDependenciesPtr depsPtr = NULL;
   LISTNODEPTR submitsPtr = NULL, siblingsPtr = NULL, abortsPtr = NULL;
   SeqLoopsPtr loopsPtr = NULL;
   SeqUtil_TRACE( "SeqNode.SeqNode_printNode() called\n" );
   if( filters == NULL ) {
      showAll = 1;
   } else {
      if( strstr( filters, "all" ) != NULL ) showAll = 1;
      if( strstr( filters, "cfg" ) != NULL ) showCfgPath = 1;
      if( strstr( filters, "task" ) != NULL ) showTaskPath = 1;
      if( strstr( filters, "res" ) != NULL ) showRessource = 1;
      if( strstr( filters, "type" ) != NULL ) showType = 1;
      if( strstr( filters, "node" ) != NULL ) showNode = 1;

   if  (( showAll || showType || showCfgPath || showRessource || showTaskPath || showNode ) == 0) {
         raiseError("Filters %s unrecognized\n", filters);
   }

   }

   /*printf("************ Seq Node Information \n"); */
   if( showAll ) {
      printf("node.name=%s\n", node_ptr->name );
      printf( "node.extension=%s\n",  node_ptr->extension);
      printf("node.leaf=%s\n", node_ptr->nodeName );
     
      printf("node.module=%s\n", node_ptr->module );
      printf("node.intramodule_container=%s\n", node_ptr->intramodule_container );
      /*
      printf("alias=%s\n", node_ptr->alias );
      printf("args=%s\n", node_ptr->args );
      */
   }
   if (showNode) {
      (node_ptr->extension == NULL || strlen(node_ptr->extension) == 0) ? printf("node.fullnode=%s\n",node_ptr->name) : printf("node.fullnode=%s.%s\n",node_ptr->name,node_ptr->extension);
   }

   if ( showAll || showType ) {
        printf("node.type=%s\n", SeqNode_getTypeString( node_ptr->type ) );
   } 

   if( showAll || showRessource ) {
      printf("node.catchup=%d\n", node_ptr->catchup );
      printf("node.mpi=%d\n", node_ptr->mpi);
      printf("node.wallclock=%d\n", node_ptr->wallclock );
      printf("node.cpu=%s\n", node_ptr->cpu );
      printf("node.machine=%s\n", node_ptr->machine );
      printf("node.queue=%s\n", node_ptr->queue );
      printf("node.memory=%s\n", node_ptr->memory );
   }
   if( showAll || showCfgPath ) {
      if( node_ptr->type == Task || node_ptr->type == NpassTask ) {
         printf("node.configpath=${SEQ_EXP_HOME}/modules%s.cfg\n", node_ptr->taskPath );
      } else {
         printf("node.configpath=${SEQ_EXP_HOME}/modules%s/%s/container.cfg\n", node_ptr->intramodule_container, node_ptr->nodeName );
      }
   }

   if( (showAll || showTaskPath) && (node_ptr->type == Task || node_ptr->type == NpassTask) ) {
      if ( strcmp( node_ptr->taskPath, "" ) == 0 )
         printf("node.taskpath=\n");
      else
         printf("node.taskpath=${SEQ_EXP_HOME}/modules%s.tsk\n", node_ptr->taskPath );
   }

   if( showAll ) {

      printf( "node.flow=${SEQ_EXP_HOME}/modules/%s/flow.xml\n", node_ptr->module );
      /*printf("************ Node Specific Data \n"); */
      nameValuesPtr = node_ptr->data;
      while (nameValuesPtr != NULL ) {
         printf("node.specific.%s=%s\n", nameValuesPtr->name, nameValuesPtr->value );
         nameValuesPtr = nameValuesPtr->nextPtr;
      }
      /*printf("************ Node Dependencies \n"); */
      depsPtr = node_ptr->depends;
   
      while( depsPtr != NULL ) {
         nameValuesPtr =  depsPtr->dependencyItem;
   
         /*printf("********* Dependency Item \n"); */
         if ( depsPtr->type == NodeDependancy ) {
            printf("node.depend.type=Node\n");
         } else if ( depsPtr->type == DateDependancy ) { 
            printf("node.depend.type=D  ate\n");
         }
         while (nameValuesPtr != NULL ) {
            if( strlen( nameValuesPtr->value ) > 0 ) 
               printf("node.depend.%s=%s\n", nameValuesPtr->name, nameValuesPtr->value );
            nameValuesPtr = nameValuesPtr->nextPtr;
         }
         depsPtr  = depsPtr->nextPtr;
      }
   
      /*printf("************ Node Submits \n"); */
      submitsPtr = node_ptr->submits;
      while (submitsPtr != NULL) {
         printf("node.submit=%s\n", submitsPtr->data);
         submitsPtr = submitsPtr->nextPtr;
      }
   
      /*printf("************ Node Abort Actions \n"); */
      abortsPtr = node_ptr->abort_actions;
      while (abortsPtr != NULL) {
         printf("node.abortaction=%s\n", abortsPtr->data);
         abortsPtr = abortsPtr->nextPtr;
      }
      /*printf("************ Containing Loops \n"); */
      loopsPtr = node_ptr->loops;
      while (loopsPtr != NULL) {
         /*printf("************ Loop \n"); */
         printf("node.loop_parent.name=%s\n", loopsPtr->loop_name);  
         nameValuesPtr = loopsPtr->values;
         while (nameValuesPtr != NULL ) {
            printf("node.loop_parent.%s=%s\n", nameValuesPtr->name, nameValuesPtr->value );
            nameValuesPtr = nameValuesPtr->nextPtr;
         }
         loopsPtr = loopsPtr->nextPtr;
      }
      /*printf("************ Node Siblings \n"); */
      siblingsPtr = node_ptr->siblings;
      while (siblingsPtr != NULL) {
         printf("node.sibling=%s\n", siblingsPtr->data);
         siblingsPtr = siblingsPtr->nextPtr;
      }
   }

   SeqUtil_TRACE( "SeqNode.SeqNode_printNode() done\n" );
}

SeqNodeDataPtr SeqNode_createNode ( char* name ) {
   SeqNodeDataPtr nodeDataPtr = NULL;
   SeqUtil_TRACE( "SeqNode.SeqNode_createNode() started\n" );
   nodeDataPtr = malloc( sizeof( SeqNodeData ) );
   SeqNode_init ( nodeDataPtr );
   SeqNode_setName( nodeDataPtr, name );
   SeqNode_setNodeName ( nodeDataPtr, (char*) SeqUtil_getPathLeaf(name));
   SeqNode_setContainer ( nodeDataPtr, (char*) SeqUtil_getPathBase(name));
   SeqUtil_TRACE( "SeqNode.SeqNode_createNode() done\n" );
   return nodeDataPtr;
}

void SeqNode_freeNameValues ( SeqNameValuesPtr _nameValuesPtr ) {
   SeqNameValuesPtr nameValuesNextPtr = NULL;
   /* free a link-list of name-value pairs */
   while (_nameValuesPtr != NULL ) {
      /*SeqUtil_TRACE("   SeqNode_freeNameValues %s=%s\n", _nameValuesPtr->name, _nameValuesPtr->value ); */

      /* load a copy of the next to be freed */
      nameValuesNextPtr = _nameValuesPtr->nextPtr;

      /* free the current node */
      free( _nameValuesPtr->name );
      free( _nameValuesPtr->value );
      free( _nameValuesPtr );

      /* go to the next to be freed */ 
      _nameValuesPtr = nameValuesNextPtr;
   }
}


void SeqNode_freeNode ( SeqNodeDataPtr seqNodeDataPtr ) {
   SeqDependenciesPtr depsPtr, depsNextPtr;

   if ( seqNodeDataPtr != NULL ) {
      free( seqNodeDataPtr->name ) ;
      free( seqNodeDataPtr->nodeName );
      free( seqNodeDataPtr->container ) ;
      free( seqNodeDataPtr->intramodule_container ) ;
      free( seqNodeDataPtr->module ) ;
      free( seqNodeDataPtr->masterfile ) ;
      free( seqNodeDataPtr->alias ) ;
      free( seqNodeDataPtr->args ) ;
      free( seqNodeDataPtr->errormsg ) ;
      free( seqNodeDataPtr->cpu ) ;
      free( seqNodeDataPtr->taskPath ) ;
      free( seqNodeDataPtr->suiteName ) ;
      free( seqNodeDataPtr->memory ) ;
      free( seqNodeDataPtr->machine ) ;
      free( seqNodeDataPtr->queue ) ;
      free( seqNodeDataPtr->datestamp) ;
      free( seqNodeDataPtr->workdir) ;
   
      depsPtr = seqNodeDataPtr->depends;
      /* free a link-list of dependency items */
      while( depsPtr != NULL ) {

         /* make a copy of the next dependency item to be freed */
         depsNextPtr = depsPtr->nextPtr;

         SeqNode_freeNameValues( depsPtr->dependencyItem );
         free( depsPtr );
         depsPtr  = depsNextPtr;
      }
      SeqListNode_deleteWholeList( &(seqNodeDataPtr->submits) );
      SeqListNode_deleteWholeList( &(seqNodeDataPtr->abort_actions) );
      SeqListNode_deleteWholeList( &(seqNodeDataPtr->siblings) );
      SeqNode_freeNameValues( seqNodeDataPtr->data );
      free( seqNodeDataPtr );
   }
}

void seqNodeUnitTest () {
   SeqNodeDataPtr  nodeDataPtr = NULL;
   /*
   SeqNodeData nodeData;
   SeqNode_init( &nodeData );
   SeqNode_setName( &nodeData, "test_nodename" );
   */
   nodeDataPtr = SeqNode_createNode( "testsuite/assimilation/00/get_observations/test_nodename" );
   SeqNode_setModule( nodeDataPtr, "assim_module" );
   SeqNode_setNodeName( nodeDataPtr, "test_nodename" );
   SeqNode_setContainer( nodeDataPtr, "testsuite/assimilation/00" );
   /* SeqNode_setMasterfile ( nodeDataPtr, "/users/dor/afsi/dor/sul/.suites/testsuite/sequencing/flow/testsuite.xml" ); */
   SeqNode_addNodeDependency( nodeDataPtr, NodeDependancy, "testsuite/assimilation/00/testnode", "afsisul", "testpath", "testsuite", "complete" ,"", "", "");
   SeqNode_addNodeDependency( nodeDataPtr, NodeDependancy, "testsuite/assimilation/00/testnode1", "afsisul", "testpath1", "testsuite", "complete","", "", "" );
   /*
   SeqNode_addNodeDependency( nodeDataPtr, "testsuite/assimilation/00/testnode1", "afsisul", "testsuite", "complete" );
   SeqNode_addDateDependency ( nodeDataPtr, "2008/02/18-23:50" );
   */
   SeqNode_addSubmit( nodeDataPtr, "submits_node_0" );
   SeqNode_addSubmit( nodeDataPtr, "submits_node_1" );
   SeqNode_addSibling( nodeDataPtr, "sibling_0" );
   SeqNode_addSibling( nodeDataPtr, "sibling_1" );
   SeqNode_addAbortAction( nodeDataPtr, "stop" );
   SeqNode_addAbortAction( nodeDataPtr, "continue" );
   SeqNode_addSpecificData( nodeDataPtr, "LOOP_START", "0" );
   SeqNode_addSpecificData( nodeDataPtr, "LOOP_END", "30" );
   SeqNode_addSpecificData( nodeDataPtr, "LOOP_STEP", "1" );
   SeqNode_printNode( nodeDataPtr, "all" );
   SeqNode_freeNode( nodeDataPtr );
}

/*
int main (argc,argv)
int argc;
char *argv[];
{
   unitTest();
   return(0);
}
*/
   /*
   SeqNameValues nameValues;
   nameValues.name = malloc ( sizeof(char) * 16 );
   nameValues.value = malloc ( sizeof(char) * 16 );
   strcpy( nameValues.name, "dep_item0_name" );
   strcpy( nameValues.value, "dep_item0_value" );
   nameValues.nextPtr = NULL;

   SeqNameValues nameValues2;
   nameValues2.name = malloc ( sizeof(char) * 16 );
   nameValues2.value = malloc ( sizeof(char) * 16 );
   strcpy( nameValues2.name, "dep_item1_name" );
   strcpy( nameValues2.value, "dep_item1_value" );
   nameValues2.nextPtr = NULL;

   nodeData.depends = malloc ( sizeof(SeqNameValuesPtr) * 2 );
   nodeData.depends[0] = &nameValues;
   nodeData.depends[1] = &nameValues2;
   nodeData.dependsLen = 2;
   */

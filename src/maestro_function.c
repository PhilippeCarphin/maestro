void printMaestroCommand( char* _node, char* _signal, char* _flow, SeqNameValuesPtr _loops, int ignoreAllDeps, char* _extraArgs, char *_datestamp, char* _seq_exp_home )
{
   printf( "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n" );
   printf( "maestro: node=%s signal=%s flow=%s loop_args=%s extraArgs=%s expHome=%s\n", _node, _signal, _flow, SeqLoops_getLoopArgs(_loops), _extraArgs, _seq_exp_home);
   char *tmp = NULL;
   if ( _loops != NULL ) {
      SeqUtil_stringAppend(&tmp, " -l ");
      SeqUtil_stringAppend(&tmp, SeqLoops_getLoopArgs(_loops));
   }
   if ( ignoreAllDeps ) {
      SeqUtil_stringAppend(&tmp, " -i 1");
   }
   if( _extraArgs != NULL ) {
      SeqUtil_stringAppend(&tmp, " -o ");
      SeqUtil_stringAppend(&tmp, _extraArgs);
   } 
   if ( tmp != NULL ){
      SeqUtil_TRACE(TL_FULL_TRACE, "Command called:\nmaestro -s %s -n %s -f %s %s -e %s -d %s\n",_signal, _node, _flow, tmp, _seq_exp_home, _datestamp);
   } else {
      SeqUtil_TRACE(TL_FULL_TRACE, "Command called:\nmaestro -s %s -n %s -f %s -e %s -d %s \n",_signal , _node, _flow, _seq_exp_home, _datestamp);
   } 

   SeqUtil_TRACE(TL_FULL_TRACE, "maestro() ignoreAllDeps=%d \n",ignoreAllDeps );
}



int SeqUtil_checkExpHome2(char *_seq_exp_home)
{
   if ( _seq_exp_home != NULL ) {
      char buffer[SEQ_MAXFIELD] = {'\0'};
      char  *fixedPath;
      DIR *dirp = NULL;
      SeqUtil_normpath(buffer,_seq_exp_home);
      fixedPath = SeqUtil_fixPath(buffer);
      if ( (dirp = opendir(fixedPath)) == NULL){
         raiseError( "SEQ_EXP_HOME %s is an invalid link or directory!\n",fixedPath );
      }
      free(fixedPath);
      closedir(dirp);
   } else {
      raiseError( "maestro(): argument _seq_exp_home of maestro() function must be supplied \n" );
   }
   return 0;
}



int validateFlowValue(char *_flow)
{
   if ( strcmp(_flow, "continue") == 0 || strcmp(_flow,"stop") == 0 ) {
   	SeqUtil_TRACE(TL_FULL_TRACE, "maestro() flow = %s , valid \n",_flow);
   } else {
      raiseError( "flow value must be \"stop\" or \"continue\"\n" );
   } 
   return 0;
}

void saveCurrentNode(char * _node)
{
   free(CurrentNode);
   if (CurrentNode=(char *) malloc(strlen(_node) + 1)){
       strcpy(CurrentNode,_node);
   } else {
      raiseError("OutOfMemory exception in maestro()\n");
   }
}

void getSubmitTool(char *dst)
{
   char *seq_soumet = getenv("SEQ_SOUMET");
   if ( seq_soumet != NULL ) {
      strcpy(dst,seq_soumet);
   } else {
      strcpy(dst,"ord_soumet");
   }
   SeqUtil_TRACE(TL_FULL_TRACE, "maestro() using submit script=%s\n", submit_tool );
}

int go_end_wrapper(char *_signal, char *_flow, SeqNodeDataPtr nodeDataPtr)
{
   int status = go_end( _signal, _flow, nodeDataPtr );
   /* run stats and averaging if topnode and user requested it */ 
   if (strcmp(nodeDataPtr->container,"") == 0 ) {
      char *defFile = NULL;
      if (defFile = malloc ( strlen ( nodeDataPtr->expHome ) + strlen("/resources/resources.def") + 1 )) {
         sprintf( defFile, "%s/resources/resources.def", nodeDataPtr->expHome );
      } else {
         raiseError("OutOfMemory exception in maestro()\n");
      }     
      char *runStats = SeqUtil_getdef( defFile, "SEQ_RUN_STATS_ON", nodeDataPtr->expHome );
      if ( runStats != NULL ) {
         char *windowAverage = NULL;
         SeqUtil_TRACE(TL_FULL_TRACE, "maestro() running job statictics.\n");
         logreader(NULL,NULL,nodeDataPtr->expHome,nodeDataPtr->datestamp, "stats", 0,0); 
         if ( (windowAverage=SeqUtil_getdef( defFile, "SEQ_AVERAGE_WINDOW", nodeDataPtr->expHome )) != NULL ) {
            SeqUtil_TRACE(TL_FULL_TRACE, "maestro() running averaging.\n");
            logreader(NULL,NULL,nodeDataPtr->expHome,nodeDataPtr->datestamp, "avg", atoi(windowAverage),0); 
         } 
      }
      free(runStats);
      free(defFile);
   }
   return status;
}

int go_submit_wrapper(char *_signal, char *_flow, SeqNodeDataPtr nodeDataPtr, int ignoreAllDeps)
{
   char *tmpJobID = NULL;
   char *tmpFullOrigin=NULL;
   char *tmpNodeOrigin=NULL;
   char *tmpHost=NULL;
   /*get origin of the submission*/
   if ((tmpJobID=getenv("JOB_ID")) == NULL) {
      tmpJobID=getenv("LOADL_STEP_ID");
   }
   tmpHost=getenv("HOST");
   if (tmpJobID != NULL) {
       SeqUtil_stringAppend( &tmpFullOrigin,"Submitted by jobID=");
       SeqUtil_stringAppend( &tmpFullOrigin, tmpJobID );
       if ((tmpNodeOrigin=getenv("SEQ_NAME")) !=NULL) {
           /* Returns tmpFullOrigin */
           char *tmpLoopExt=NULL;
           SeqUtil_stringAppend( &tmpFullOrigin, " Node Name=" );
           SeqUtil_stringAppend( &tmpFullOrigin, tmpNodeOrigin );
           if ((tmpLoopExt=getenv("SEQ_LOOP_EXT")) != NULL) {
               SeqUtil_stringAppend( &tmpFullOrigin, tmpLoopExt );
           } 
           free(tmpLoopExt);
       } 
   } else {
       SeqUtil_stringAppend( &tmpFullOrigin,"Manual or cron submitted");
   }
   SeqUtil_stringAppend( &tmpFullOrigin, " from host " );
   SeqUtil_stringAppend( &tmpFullOrigin, tmpHost);
   SeqNode_setSubmitOrigin(nodeDataPtr,tmpFullOrigin);
   free( tmpFullOrigin );

   return go_submit( _signal, _flow, nodeDataPtr, ignoreAllDeps );
}

int action_switch(char *_signal, char *_flow, SeqNodeDataPtr nodeDataPtr, int ignoreAllDeps)
{
   if ( (strcmp(_signal,"end") == 0 ) || (strcmp(_signal, "endx") == 0 ) || (strcmp(_signal,"endmodel") == 0 ) || 
      (strcmp(_signal,"endloops") == 0) || (strcmp(_signal,"endmodelloops") == 0) ||
      (strncmp(_signal,"endloops_",9) == 0) || (strncmp(_signal,"endmodelloops_",14) == 0)) {
      return go_end_wrapper(_signal, _flow, nodeDataPtr);
   }

   if (( strcmp (_signal,"initbranch" ) == 0 ) ||  ( strcmp (_signal,"initnode" ) == 0 )) {
      return go_initialize( _signal, _flow, nodeDataPtr );
   }

   if (strcmp(_signal,"abort") == 0 || strcmp( _signal, "abortx" ) == 0 ) {
      return go_abort( _signal, _flow, nodeDataPtr );
   }

   if ( strcmp(_signal,"begin") == 0 || strcmp(_signal,"beginx") == 0 ) {
      SeqUtil_TRACE(TL_FULL_TRACE, "maestro() node from nodeinfo before go_begin=%s, loopargs=%s, extension=%s \n", nodeDataPtr->name, SeqLoops_getLoopArgs(nodeDataPtr->loop_args), nodeDataPtr->extension );
      return go_begin( _signal, _flow, nodeDataPtr );
   }

   if ( strcmp(_signal,"submit") == 0 ) {
      return go_submit_wrapper(_signal, _flow, nodeDataPtr, ignoreAllDeps);
   }
}

void setup_handlers(struct sigaction *alrm, struct sigaction *pipe, SeqNodeDataPtr nodeDataPtr, char *_node, char *_signal, char *_seq_exp_home)
{
   /* Deciding on locking mecanism: the decision will be based on acquiring 
    * SEQ_LOGGING_MECH string value in .maestrorc file */

   char *defFile=NULL;
   char *logMech=NULL;

   if (defFile = malloc ( strlen (getenv("HOME")) + strlen("/.maestrorc") + 2 )) {
      sprintf( defFile, "%s/.maestrorc", getenv("HOME"));
   } else {
      raiseError("OutOfMemory exception in maestro()\n");
   }
   if ( (logMech=SeqUtil_getdef( defFile, "SEQ_LOGGING_MECH", nodeDataPtr->expHome )) != NULL ) {
          free(defFile);defFile=NULL;
   } else {
          logMech=strdup("nfs");
   }

   /* inform only at beginning of tasks */
   if ( strcmp(_signal,"begin") == 0 ) {
          fprintf(stdout,"logging mechanism set to:%s\n",logMech);
   }


   /* Install handler for 
    *   SIGALRM to be able to time out socket routines This handler must be installed only once 
    *   SIGPIPE : in case of socket closed */
   if ( QueDeqConnection == 0 ) {
      int r;
       memset (alrm, '\0', sizeof(*alrm));
       alrm->sa_handler = &alarm_handler;
       alrm->sa_flags = 0;
       sigemptyset (&(alrm->sa_mask));
       r = sigaction (SIGALRM, alrm, NULL);
       if (r < 0) perror (__func__);
      
       memset (pipe, '\0', sizeof(*pipe));
       pipe->sa_handler = &pipe_handler;
       pipe->sa_flags = 0;
       sigemptyset (&(pipe->sa_mask));
       r = sigaction (SIGPIPE, pipe, NULL);
       if (r < 0) perror (__func__);
   }

   if ( ServerConnectionStatus == 1 ) { 
       if  ( strcmp(logMech,"server") == 0 ) {
          MLLServerConnectionFid = OpenConnectionToMLLServer(_node, _signal,_seq_exp_home);
          if ( MLLServerConnectionFid > 0 ) {
             ServerConnectionStatus = 0;
             fprintf(stdout,"#########Server Connection Open And Login Accepted Signal:%s #########\n",_signal);
             useSVRlocking();
          } else {
             switch (MLLServerConnectionFid) {
                case  -1:
                   fprintf(stderr,">>>>>Warning could not open connection with server<<<<<<\n");
                   break;
                case  -2:
                   fprintf(stderr,">>>>>Authentification Failed with server<<<<<<\n");
                   break;
                default :
                   fprintf(stderr,">>>>>I dont know what has happened <<<<<<\n");
                   break;
             }
             useNFSlocking();
          }
      } else {
          useNFSlocking();
      }
   }
   
   QueDeqConnection++;
   free(logMech); 
}

void create_working_dir(SeqNodeDataPtr nodeDataPtr)
{
   char tmpdir[256];
   sprintf( tmpdir, "%s/%s/%s", nodeDataPtr->workdir, nodeDataPtr->datestamp, nodeDataPtr->container );
   _SeqUtil_mkdir( tmpdir, 1, nodeDataPtr->expHome );
}

void release_connection_with_server(struct sigaction *alrm, struct sigaction *pipe, char *_signal)
{
   QueDeqConnection--;
   if ( ServerConnectionStatus == 0 ) {
      if ( QueDeqConnection == 0 ) {
         CloseConnectionWithMLLServer (MLLServerConnectionFid);
         fprintf(stdout,"#########Server Connection Closed Signal:%s #########\n",_signal);
      }
   }
 
   if ( QueDeqConnection == 0 ) {
      int r;
      /* remove installed SIGALRM handler */
      alrm->sa_handler = SIG_DFL;
      alrm->sa_flags = 0;
      sigemptyset (&(alrm->sa_mask));
      r = sigaction (SIGALRM, alrm, NULL);
      if (r < 0) perror (__func__);
          
      /* remove installed SIGPIPE handler */
      pipe->sa_handler = SIG_DFL;
      pipe->sa_flags = 0;
      sigemptyset (&(pipe->sa_mask));
      r = sigaction (SIGPIPE, pipe, NULL);
      if (r < 0) perror (__func__);
   }
}

int maestro( char* _node, char* _signal, char* _flow, SeqNameValuesPtr _loops, int ignoreAllDeps, char* _extraArgs, char *_datestamp, char* _seq_exp_home ) {
   

   printMaestroCommand(_node,_signal,_flow,_loops,ignoreAllDeps,_extraArgs,_datestamp,_seq_exp_home);


   /* Verify validity of _seq_exp_home */
   SeqUtil_checkExpHome2(_seq_exp_home);

   /* save current node name if we must close & re-open connection */
   saveCurrentNode(_node);

   validateFlowValue(_flow);

   getSubmitTool(submit_tool);

   /* need to tell nodelogger that we are running from maestro
   so as not try to acquire a socket */
   putenv("FROM_MAESTRO=yes");

   SeqNodeDataPtr nodeDataPtr = nodeinfo( _node, NI_SHOW_ALL, _loops, _seq_exp_home , _extraArgs, _datestamp,NULL);
   /* PUT THIS IN NODEINFO? */ 
   SeqLoops_validateLoopArgs( nodeDataPtr, _loops );

   struct sigaction alrm, pipe;
   setup_handlers(&alrm, &pipe,nodeDataPtr, _node, _signal,_seq_exp_home);

   create_working_dir(nodeDataPtr);
   int status = 1; /* starting with error condition */
   status = action_switch(_signal, _flow, nodeDataPtr, ignoreAllDeps);

   release_connection_with_server(&alrm, &pipe,_signal);
   
out_free:
   SeqNode_freeNode( nodeDataPtr );
   SeqUtil_TRACE(TL_FULL_TRACE,"maestro() returning %d\n",status);
   return status;
}

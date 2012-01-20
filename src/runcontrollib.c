#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdarg.h>
#include <rpnmacros.h>
#include <unistd.h>
#include <dirent.h>
#include <libgen.h>
#include "runcontrollib.h"
#include "nodelogger.h"
extern char *__loc1; /* needed for regex */


/********************************************************************************
*CopyStrTillCarac: copy 'original' from the beginning of the string till the
* caracter 'c' into 'result'
********************************************************************************/
void CopyStrTillCarac(char *result, const char *original, char c)
{
  while (*original) {
     if (*original != c) {
        *result=*original;
     } else {
        result++;
        break;
     }
     original++;
     result++;
  }
  *result = '\0' ;
}

/********************************************************************************
*match:Match 'string' against the extended regular expression in 'pattern',
* treating errors as no match.
* Return 1 for match, 0 for no match.
********************************************************************************/
int match(const char *string, char *pattern)
{

#if defined(Mop_linux)

 char *ptr = NULL;
 int re;

 ptr = (char *) re_comp(pattern);
 if ( ptr != NULL) {
    return(0); /* report error */
 }

 re = re_exec(string);
 return(re);

#else

 char *ptr = NULL;
 char *re = NULL;

 ptr = (char *) regcmp(pattern,(char *) 0);
 if ( ptr == NULL) {
    return(0); /* report error */
 }

 re = regex(ptr,string);
 free(ptr);
 if ( re == NULL) {
    return(0); /* report error */
 }
  
 return(1);  
#endif

}

/****************************************************************/

/***************************************************************
*nodewait: send 'wait' message to operational logging system.
****************************************************************/
// void nodewait(char *job,char *jobw)
void nodewait( const SeqNodeDataPtr node_ptr, const char* msg, char *datestamp)
{
   /* This is needed so messages will be logged into CMCNODELOG */ 
   putenv("CMCNODELOG=on"); 
   nodelogger(node_ptr->name,"wait",node_ptr->extension,msg,datestamp);
}

/****************************************************************/

/****************************************************************************
* NAME: nodeend
* PURPOSE: send 'end' message to operational logging system.
* It is normally called at the end of an operational job.
* INPUT: node - full path of the node
*****************************************************************************/
void nodeend( const char *_signal, const SeqNodeDataPtr node_ptr, char *datestamp)
{
   char jobID[50];
   char message[300];

   /* This is needed so messages will be logged into CMCNODELOG */
   putenv("CMCNODELOG=on");

   memset(jobID, '\0', sizeof jobID);
   if (getenv("JOB_ID") != NULL){
         sprintf(jobID,"%s",getenv("JOB_ID"));
   }
   if (getenv("LOADL_STEP_ID") != NULL){
         sprintf(jobID,"%s",getenv("LOADL_STEP_ID"));
   }

   memset(message,'\0',sizeof message);
   sprintf(message,"job_ID=%s",jobID);

   nodelogger(node_ptr->name,_signal,node_ptr->extension,message,datestamp);

}


/****************************************************************/

/****************************************************************
*nodesubmit: send 'submit' message to logging system.
*INPUT: job  - the job

****************************************************************/
void nodesubmit( const SeqNodeDataPtr node_ptr, char *datestamp)
{
   char message[300];

   memset(message,'\0',sizeof message);
   /* This is needed so messages will be logged into CMCNODELOG */
   putenv("CMCNODELOG=on");
   /* containers use TRUE_HOST for execution */
   if ( node_ptr->type == Task || node_ptr->type == NpassTask ) {
   sprintf(message,"machine=%s queue=%s cpu=%s Memory=%s Wallclock Limit=%d mpi=%d",node_ptr->machine, node_ptr->queue, node_ptr->cpu, node_ptr->memory, node_ptr->wallclock, node_ptr->mpi);
   } else {
   sprintf(message,"machine=%s queue=%s cpu=%s Memory=%s Wallclock Limit=%d mpi=%d in IMMEDIATE mode",getenv("TRUE_HOST"), node_ptr->queue, node_ptr->cpu, node_ptr->memory, node_ptr->wallclock, node_ptr->mpi);
   }

   printf("nodesubmit.Message=%s",message);

   nodelogger(node_ptr->name,"submit",node_ptr->extension,message,datestamp);
}
/****************************************************************/


/****************************************************************/

/****************************************************************
*nodebegin: send 'begin' message to operational logging system.
*INPUT: job  - the job
****************************************************************/
void nodebegin( const char *_signal, const SeqNodeDataPtr node_ptr, char *datestamp)
{
   char hostname[50];
   char message[300];
   char jobID[50];
   
   /* This is needed so messages will be logged into CMCNODELOG */
   putenv("CMCNODELOG=on");
   
   memset(hostname, '\0', sizeof hostname);
   gethostname(hostname,sizeof hostname);

   memset(jobID, '\0', sizeof jobID);
   if (getenv("JOB_ID") != NULL){
         sprintf(jobID,"%s",getenv("JOB_ID"));
   }
   if (getenv("LOADL_STEP_ID") != NULL){
         sprintf(jobID,"%s",getenv("LOADL_STEP_ID"));
   }
   
   memset(message,'\0',sizeof message);
   //sprintf(message,"BEGINS host=%s",hostname);
   sprintf(message,"host=%s job_ID=%s",hostname,jobID);
   //nodelogger(job,'X',message);
   /* nodelogger(job,"begin",message); */
   nodelogger(node_ptr->name,_signal,node_ptr->extension,message,datestamp);
}
/****************************************************************/

/****************************************************************
*nodeabort: send 'abort' message to operational logging system.
*INPUT: num - the numbers of arguments passed to the function.
*       job - the job
*       [type] (optional)
*               <rerun> - "ABORTED $run: Job has been rerun"
*                       - 3bells "Job Has Bombed...Run Continues"
*               <nosub> - "JOB OF $run NOT SUBMITTED"
*                       - 3bells "Job Was Not Submitted......."
*               <abort> - "ABORTED $run STEM CONTINUES"
*                       - 3bells "Job Has Bombed...Run Continues"
*                 <aji> - "AUTO JOB ABORT"
*                       - 1bell "****   MESSAGE  ****"
*                <cron> - "CRON JOB ABORT"
*                       - 1bell "****   MESSAGE  ****"
*               <xxjob> - "XXJOB ABORT"
*                       - 1bell "****   MESSAGE  ****"
*                <orji> - "ORJI JOB NOT SUBMITTED"
*      [errno] (optional)
*              - A message with a corresponding number is sent to the
*                oprun log.
****************************************************************/
void nodeabort(const char *_signal, const SeqNodeDataPtr _nodeDataPtr, char* abort_type, char *datestamp)
{
   static char aborted[] = "ABORTED";
   static char runc[]    = ": run continues";
   static char joba[]    = "JOB ABORT:";
   static char abortnb[] = "job aborted: ";
   static char jobc[]    = "next job(s) submitted";
   static char jobo[]    = "JOB OF";
   static char jobs[]    = "job stopped ";
   static char rerun[]   = "job has been resubmitted";
   static char xxjob[]   = "XXJOB ABORT";
   int  i=0, errno=0 ;
   char buf[130], *job = NULL, *loopExt = NULL;
   char* thisAbortType = NULL;
   char jobID[50];

   memset(jobID, '\0', sizeof jobID);
   if (getenv("JOB_ID") != NULL){
         sprintf(jobID,"%s",getenv("JOB_ID"));
   }
   if (getenv("LOADL_STEP_ID") != NULL){
         sprintf(jobID,"%s",getenv("LOADL_STEP_ID"));
   }
   

   thisAbortType = strdup(abort_type);
   while( abort_type[i] != '\0' ) {
      thisAbortType[i] = toupper( abort_type[i] );
      i++;
   }
   thisAbortType[i]='\0';
      printf("nodeabort: thisAbortType: %s for datestamp %s\n", thisAbortType, datestamp);

   job = _nodeDataPtr->name;
   loopExt = _nodeDataPtr->extension;
   /* This is needed so messages will be logged into CMCNODELOG */
   putenv("CMCNODELOG=on");

	memset(buf,'\0',sizeof buf);

   if ( strncmp(abort_type,"ABORTNB",7) == 0 ) {
      nodelogger(job,_signal,loopExt,abortnb,datestamp);
   } else if ( strncmp(thisAbortType,"ABORT",5) == 0 ) {
      sprintf(buf,"%s %s, job_ID=%s",aborted, runc, jobID);
      nodelogger(job,_signal,loopExt,buf,datestamp);
   } else if ( strncmp(thisAbortType,"CONT",4) == 0 ) {
      sprintf(buf,"%s %s, job_ID=%s",aborted, jobc, jobID);
      nodelogger(job,_signal,loopExt,buf,datestamp);
   } else if ( strncmp(thisAbortType,"RERUN",5) == 0 ) {
      sprintf(buf,"%s %s, job_ID=%s", aborted, rerun, jobID);
      nodelogger(job,_signal,loopExt,buf,datestamp);
   } else if ( strncmp(thisAbortType,"STOP",4) == 0 ) {
      sprintf(buf,"%s %s, job_ID=%s", aborted, jobs, jobID);
      nodelogger(job,_signal,loopExt,buf,datestamp);
   } else if ( strncmp(thisAbortType,"XXJOB",5) == 0 ) {
      nodelogger(job,"info",loopExt,xxjob,datestamp);
   }	else {
		printf("nodeabort: illegal type: %s\n", thisAbortType);
		exit(1);
	}

	if ( errno != 0 ) {
      sprintf(buf,"MSG NO. = %d, job_ID=%s", errno, jobID);
      nodelogger(job,_signal,loopExt,buf,datestamp);
	}
   free(thisAbortType);
}




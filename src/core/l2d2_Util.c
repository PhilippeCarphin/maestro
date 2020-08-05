/* l2d2_Util.c - Utility functions for server code of the Maestro sequencer software package.
*/


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <assert.h>
#include <dirent.h>
#include <limits.h>
#include <fcntl.h>
#include <stdarg.h>
#include <grp.h>
#include <pwd.h>
#include <glob.h>
#include <time.h>
#include <utime.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/uio.h>
#include <unistd.h>
#include <sys/param.h>
#include "l2d2_roxml.h"
#include "l2d2_server.h"
#include "l2d2_Util.h"
#include "SeqLoopsUtil.h"
#include "SeqNameValues.h"
#include "SeqUtil.h"
#include "l2d2_commun.h"


extern _l2d2server L2D2;
extern FILE *mlog;
dpnode *PRT_listdep;
static void pdir (const char * dir_name);

/**
* Copied from SeqUtil
*
*
*/
char *getPathLeaf (const char *full_path) {
   char *split,*work_string,*chreturn =NULL;
   work_string = strdup(full_path);
   split = strtok (work_string,"/");
   while (split != NULL) {
     if ( chreturn != NULL ) {
       /* free previous allocated memory */
       free( chreturn );
     }
     chreturn = strdup (split);
     split = strtok (NULL,"/");
   }
   free( work_string );
   return chreturn;
}

/**
 * Name        : removeFile
 * 
 */
int removeFile(char *filename) {
   int status=0;
   
   status = remove(filename);
   return(status);
}

/**
 * Name        : CreateLock
 * Description : touch a file (calls touch) if file
 *               not there
 */
int CreateLock (char *filename) {
   int status=0;

   if ( access (filename, R_OK) != 0 ) {
               /* create the node begin lock file name */
                status = touch (filename);
   } else {
               /* file lock exist */
                status =  0;
   }

   return (status);
}

/**
 * Name        : touch
 * Author      : copied form SeqUtil.c 
 * Description : touch a file 
 */
int touch (char *filename) {
   FILE *actionfile;
   

   if ( access (filename, R_OK) == 0 )  return(0);
    

   if ((actionfile = fopen(filename,"r")) != NULL ) {
            fclose(actionfile);
            utime(filename,NULL); /*set the access and modification times to current time */
   } else {
      if ((actionfile = fopen(filename,"w+")) == NULL) {
        return(1);
      }
      
      fclose(actionfile);
   }

   return(0); 
}

/*
 * Name        : isFileExists
 * Author      : copied form SeqUtil.c
 * Description : check if file exists 
 */
int isFileExists( const char* lockfile ) {

   if ( access(lockfile, R_OK) == 0 ) return(1);
   return (0);
}

/**
 * Name        : Access
 * Description : check if file exist 
 */
int Access ( const char* lockfile ) {

   if ( access(lockfile, R_OK) == 0 ) return (0);
   return (1);
}

/**
 * Name        : isDirExists
 * Author      : copied from SeqUtil.c 
 * Description : check if directory exists 
 */
int isDirExists ( const char* path_name ) {

   DIR *pDir = NULL;
   int Exists = 0;
   int ret;

   if ( path_name == NULL) return 0;
   pDir = opendir (path_name);

   if (pDir != NULL)
   {
      Exists = 1;
      ret=closedir(pDir);
   }

   return (Exists);
}

/**
 * create a directory  1+ level 
 */
int r_mkdir ( const char* dir_name, int is_recursive , FILE *mlog) {
   char tmp[1024];
   char *split = NULL, *work_string = NULL;
 
   memset(tmp,'\0',sizeof(tmp));

   if ( is_recursive == 1) {
      work_string = strdup( dir_name );
      strcpy( tmp, "/" );
      split  = strtok( work_string, "/" );
      if( split != NULL ) {
         strcat( tmp, split );
      }
      while ( split != NULL ) {
         strcat( tmp, "/" );
         if( ! isDirExists( tmp ) ) {
            if ( mkdir(tmp,0755 ) == -1 ) {
                 fprintf (mlog, "ERROR: %s\n", strerror(errno) ); 
                 return(EXIT_FAILURE);
            }
         }

         split = strtok (NULL,"/");
         if( split != NULL ) {
            strcat( tmp, split );
         }
      }
   } else {
      if( ! isDirExists( dir_name ) ) {
         if ( mkdir(dir_name,0755 ) == -1 ) {
                   fprintf (mlog,"ERROR: %s\n", strerror(errno) ); 
                   return(EXIT_FAILURE);
         }
      }
   }
   free( work_string );
   return(0);
}

/**
 * Name        : globPath
 * Description : Wrapper to glob :
 *               find pathnames matching a pattern  
 */
int globPath (char *pattern, int flags, int (*errfunc) (const char *epath, int eerrno) , FILE *mlog)
{
    glob_t glob_p;
    int ret;

    /* The real glob */
    ret = glob(pattern, GLOB_NOSORT,  0 , &glob_p);
    switch (ret) {
        case GLOB_NOSPACE:
	             fprintf(mlog,"globPath: Glob running out of memory \n"); 
		     break;
	case GLOB_ABORTED:
	             fprintf(mlog,"globPath: Glob read error\n"); 
		     break;
	case GLOB_NOMATCH:
                     globfree(&glob_p);
		     return(0);
		     break;
    }

    ret=glob_p.gl_pathc;
    globfree(&glob_p);


    return (ret);
}

/**
 * copied from nodelogger_svr
 */
char *getPathBase (const char *full_path) {
  char *split=NULL;
  char *work_string=NULL;
  char *chreturn =NULL;

  work_string = strdup(full_path);
  split = strrchr (work_string,'/');
  if (split != NULL) {
    *split = '\0';
    chreturn = strdup (work_string);
  }
  free( work_string );
  work_string=NULL;
  return chreturn;
}

/**
 * Name        : NodeLogr
 * Description : write in .../logs/YYYYMMDDHH0000_nodelog file 
 */
int NodeLogr (char *nodeLogerBuffer , int pid, FILE *mlog)
{
     int NodeLogfile;
     int bwrite, num=0,ret;
     char user[10];
     char firsin[512];
     char logBuffer[1024];

     if ( nodeLogerBuffer == NULL ) {
            fprintf(mlog,"NodeLogr: arg. nodeLogerBuffer is NULL \n");
            return (0);
     }

     memset(firsin,'\0',sizeof(firsin));
     if ( (num=sscanf(nodeLogerBuffer,"%[^:]:%[^:]:%[^\n]",user,firsin,logBuffer)) != 3 ) {
             fprintf(mlog,"NodeLogr: Error with the format of nodeLogerBuffer\n");
	     return (1);
     }
     
     

     strcat(logBuffer,"\n");
     if ((NodeLogfile = open(firsin, O_WRONLY|O_APPEND|O_CREAT, 00666)) != -1 ) {
           bwrite = write(NodeLogfile,logBuffer , strlen(logBuffer));
	   fsync(NodeLogfile);
           close(NodeLogfile);
	   ret=0;
     } else {
           fprintf(mlog,"NodeLogr: Could not Open nodelog file for Experiment:%s pid=%d logBuffer:%s\n",firsin,pid,logBuffer);
           ret=1; 
     }


     return(ret);
}

/**
 * Name        : writeNodeWaitedFile
 * Description : write the node waited file under dependee Xp.
 *               we examine duplicate in  wait file before inserting a dependency
 * Return value: 0 success, 1 failure  
 */
int  writeNodeWaitedFile ( const char * string , FILE *mlog ) 
{
    FILE *waitingFile;
    char line[1024];
    char this_line[1024];
    char statusFile[1024],waitfile[1024],exp[256],node[256],datestamp[25],loopArgs[128];
    char this_exp[256],this_node[256],this_datestamp[25],this_loopArgs[128];
    int  n, found=0;
    size_t num, this_inode, inode;

    memset(line,'\0',sizeof(line));
    memset(this_line,'\0',sizeof(this_line));
    memset(statusFile,'\0',sizeof(statusFile));
    memset(waitfile,'\0',sizeof(waitfile));
    memset(exp,'\0',sizeof(exp));
    memset(node,'\0',sizeof(node));
    memset(datestamp,'\0',sizeof(datestamp));
    memset(loopArgs,'\0',sizeof(loopArgs));
    
    memset(this_exp,'\0',sizeof(this_exp));
    memset(this_node,'\0',sizeof(this_node));
    memset(this_datestamp,'\0',sizeof(this_datestamp));
    memset(this_loopArgs,'\0',sizeof(this_loopArgs));
   
    n=sscanf(string,"sfile=%1023s wfile=%1023s exp=%255s node=%255s datestamp=%24s args=%127s",statusFile,waitfile,this_exp,this_node,this_datestamp,this_loopArgs);

    /* check if we have the right number of tokens */
    if ( (n <= 4 ) || ( n == 5 && strlen(this_loopArgs) != 0) ) {
        fprintf(mlog,"writeNodeWaitFile: Wrong number of argument given by sscanf got:%d should be 6\n",n);
	return(1);
    }
    
    /* if could not get inode, forget about this dependency, log it in mserver logs */
    if ( (this_inode=get_Inode(this_exp)) < 0 ) {
        fprintf(mlog,"writeNodeWaitFile: Cannot get inode of xp, dependency not written to file string=%s\n",string);
	return(1);
    }
  
    /* be carfull here, argument a will position both read and write pointer at the end, 
       while a+ will position read at beginning and write at the end 
       NOTE: the file is open through NFS from the same machine, probably the append 
             mode will be atomic in case of concurrent append. Concurrent append will happen 
	     when we will have multiple workers and if in the future we have issues with this 
	     we could use locking (same as for Logging to nodelog files) to resolve this */
    if ((waitingFile=fopen(waitfile,"a+")) == NULL ) {
                fprintf(mlog,"writeNodeWaitedFile: Cannot open file:%s in appending mode\n",waitfile );
		return(1);
    }
  
    while( fgets(line, 1024, waitingFile) != NULL ) {
           n=sscanf(line,"exp=%255s node=%255s datestamp=%24s args=%127s",exp,node,datestamp,loopArgs);
	   if (  (inode=get_Inode(exp) ) < 0 ) {
                    fprintf(mlog,"writeNodeWaitFile: Cannot get inode of registred xp=%s\n",exp);
		    continue;
	   }
	   if ( inode == this_inode && strcmp(node,this_node) == 0 && strcmp(datestamp,this_datestamp) == 0 && strcmp(loopArgs,this_loopArgs) == 0 ) {
                found = 1;
                break;
           }
    }
     
    if ( !found ) {
          snprintf(this_line, sizeof(this_line),"exp=%s node=%s datestamp=%s args=%s\n",this_exp,this_node,this_datestamp,this_loopArgs); 
          
          num = fwrite(this_line ,sizeof(char) , strlen(this_line) , waitingFile); 
	  if ( num != strlen(this_line) )  fprintf(mlog,"writeNodeWaitFile Error: written:%zu out of:%ld \n",num,strlen(this_line));
    }
    fclose( waitingFile );
    return(0);

}

/**
 * write dependency file btw diff users
 *
 *
 */
int writeInterUserDepFile (const char * tbuffer, FILE *mlog)
{
     FILE * fp=NULL;
     char buff[1024];
     char DepFileName[1024];
     char filename[1024],DepBuf[2048],ppwdir[1024],mversion[128],md5sum[128],datestamp[128]; 
     char *token, *saveptr1;
     char *tmpString;
     const char delimiter[] = "#";
     struct stat st;
     int r;

     tmpString=strdup(tbuffer); 

     /* get the first token */
     token = strtok_r(tmpString, delimiter, &saveptr1);
     free(tmpString);

     /* walk through other tokens */
     while( token != NULL ) 
     {
       if ( strncmp(token,"fil",3) == 0 ) {
            sprintf(filename,"%s",&token[4]);
       } else if ( strncmp(token,"dbf",3) == 0 ) {
            sprintf(DepBuf,"%s",&token[4]);
       } else if ( strncmp(token,"pwd",3) == 0 ) {
            sprintf(ppwdir,"%s",&token[4]);
       } else if ( strncmp(token,"mve",3) == 0 ) {
            sprintf(mversion,"%s",&token[4]);
       } else if ( strncmp(token,"m5s",3) == 0 ) {
            sprintf(md5sum,"%s",&token[4]);
       } else if ( strncmp(token,"dst",3) == 0 ) {
            sprintf(datestamp,"%s",&token[4]);
       } else {
             fprintf(mlog,"Inrecognized string:%s\n",token);
       }
         token = strtok_r(NULL, delimiter, &saveptr1);
     }

     if ( (r=touch(filename)) != 0 ) {
               fprintf(mlog,"maestro server cannot create interUser dependency file:%s\n",filename );
	       return(1);
     }

     if ((fp=fopen(filename,"w")) == NULL) {
               fprintf(mlog,"maestro server cannot write to interUser dependency file:%s\n",filename );
	       return(1);
     }

     fwrite(DepBuf, 1, strlen(DepBuf) , fp);
     fclose(fp);

     if ( stat(filename,&st) != 0 ) {
               fprintf(mlog,"maestro server cannot stat interUser dependency file:%s\n",filename );
	       return(1);
     } else fprintf(mlog,"size of InterUserDepFile is :%ld\n",st.st_size);

     /* Create server dependency directory (based on maestro version) 
      * Note: multiple clients from diff. experiment could try to create this */
     snprintf(buff, sizeof(buff), "%s/.suites/maestrod/dependencies/polling/v%s",ppwdir,mversion);
     if ( access(buff,R_OK) != 0 ) {
          if ( r_mkdir ( buff , 1 , mlog ) != 0 ) {
                  fprintf(mlog,"Could not create dependency directory:%s\n",buff);
	          return(1);
          }
     }

     /* build dependency filename and link it to true dependency file under the xp. tree*/
     snprintf(DepFileName,sizeof(DepFileName),"%s/.suites/maestrod/dependencies/polling/v%s/%s_%s",ppwdir,mversion,datestamp,md5sum);

     /* have to check for re-runs  */
     r=unlink(DepFileName);
     if ( (r=symlink(filename,DepFileName)) != 0 ) {
             fprintf(mlog,"writeInterUserDepFile: symlink returned with error:%d\n",r );
     }
     
     
     return(0);
}

/**
 * Wrapper to nanosleep which is thread safe
 */
int _sleep (double sleep_time)
{
  struct timespec tv;
    /* Construct the timespec from the number of whole seconds...  */
    tv.tv_sec = (time_t) sleep_time;
    /* ... and the remainder in nanoseconds.  */
    tv.tv_nsec = (long) ((sleep_time - tv.tv_sec) * 1e+9);

    while (1)
    {
      /* Sleep for the time specified in tv.  If interrupted by a
         signal, place the remaining time left to sleep back into tv.  */
         int rval = nanosleep (&tv, &tv);
         if (rval == 0)
                /* Completed the entire sleep time; all done.  */
                return 0;
         else if (errno == EINTR)
                /* Interruped by a signal.  Try again.  */
                continue;
         else 
                /* Some other error; bail out.  */
                return rval;
    }

    return 0;
}

/**
 * HTML source for the start of the process listing page.  
 */
char* page_start_dep = 
  "<html>\n"
  " <body>\n"
  " <meta http-equiv=\"refresh\" content=\"10\">\n"
  "  <center><b>Dependencies</b></center>\n"
  "  <table cellpadding=\"4\" cellspacing=\"0\" border=\"1\" width=\"100%\" bgcolor=\"#E6E6FA\">\n"
  "   <thead>\n"
  "    <tr>\n"
  "     <th>Date Registered</th>\n"
  "     <th>Experiment Parameters</th>\n"
  "    </tr>\n"
  "   </thead>\n"
  "   <tbody>\n";

/**
 * HTML source for the end of the process listing page. 
 */
char* page_end_dep =
  "   </tbody>\n"
  "  </table>\n"
  " </body>\n"
  "</html>\n";


char* page_start_blocked = 
  "  <table cellpadding=\"4\" cellspacing=\"0\" border=\"1\" width=\"100%\" bgcolor=\"#E6E6FF\">\n"
  "  <thead>\n"
  "   <tr>\n"
  "    <th>Host</th>\n"
  "    <th>User</th>\n"
  "    <th>Logging Time</th>\n"
  "    <th>Experiment</th>\n"
  "    <th>Node</th>\n"
  "    <th>Signal</th>\n"
  "   </tr>\n"
  "  </thead>\n"
  "  <tbody>\n";

char* page_end_blocked =
  "   </tbody>\n"
  "   </table>\n";


/**
 * parse xml configuration file using libroxml
 */
int ParseXmlConfigFile(char *filename ,  _l2d2server *pl2d2 )
{

      FILE *doc=NULL;

      char bf[256];
      char buffer[2048];
      char *c;
      int size,status;


      /* default */
      memset(bf, '\0' , sizeof(bf));
      memset(buffer, '\0' , sizeof(buffer));

      /* force clean of logs */
      pl2d2->clean_times.clean_flag=1;
      /* default values for clean (hours) */
      pl2d2->clean_times.controller_clntime=48;
      pl2d2->clean_times.dpmanager_clntime=48;
      pl2d2->clean_times.eworker_clntime=25;
      pl2d2->clean_times.tworker_clntime=25;

      if  ( (doc=fopen(filename, "r")) == NULL ) {
               fprintf(stderr,"Cannot Open XML Configuration file for mserver:%s ... Setting Defaults\n",filename);

	       sprintf(pl2d2->logdir,"%s/.suites/log/v%s",getenv("HOME"),pl2d2->mversion);
	       if ( (status=r_mkdir(pl2d2->logdir,1,stderr)) != 0 ) {
                       fprintf(stderr,"Could not create log dir :%s\n",pl2d2->logdir);
		       exit(1);
	       }
               fprintf(stderr,"Setting Defaults for log directory:%s\n",pl2d2->logdir);

	       sprintf(pl2d2->mlog,"%s/.suites/log/v%s/mcontroller",getenv("HOME"),pl2d2->mversion);
	       sprintf(pl2d2->dmlog,"%s/.suites/log/v%s/mdpmanager",getenv("HOME"),pl2d2->mversion);
	       sprintf(pl2d2->web,"%s/public_html/v%s",getenv("HOME"),pl2d2->mversion);
	       if ( access(pl2d2->web,R_OK) != 0 ) {
	              if ( (status=r_mkdir(pl2d2->web,1,stderr)) != 0 ) {
                                  fprintf(stderr,"Could not create web dir :%s\n",pl2d2->web);
				  exit(1);
		      }
               }
               fprintf(stderr,"Setting Defaults for web directory:%s\n",pl2d2->web);
	       sprintf(pl2d2->web_dep,"%s/dependencies.html",pl2d2->web);
	       sprintf(pl2d2->emailTO,"%s@ec.gc.ca",pl2d2->user);
	       sprintf(pl2d2->emailCC,"");
	       pl2d2->maxNumOfProcess=4;
	       pl2d2->maxClientPerProcess=50;
	       pl2d2->pollfreq=30; /* sec */
	       pl2d2->dependencyTimeOut=24; /* hours */
               pl2d2->dzone=0;
               fprintf(stderr,"Setting Defaults for maxNumOfProcess:%d maxClientPerProcess:%d\n",pl2d2->maxNumOfProcess,pl2d2->maxClientPerProcess);
               fprintf(stderr,"Setting Defaults for pollfreq:%d dependencyTimeOut:%d\n",pl2d2->pollfreq,pl2d2->dependencyTimeOut);
	       return(0);
      }

      if (doc) {
          fread(buffer,2048,1,doc);
	  fclose(doc);
      }

      node_t *root = roxml_load_buf(buffer);
      node_t *item = roxml_get_chld(root,NULL,0);
      roxml_get_name(item,bf,sizeof(bf));

      if ( strcmp(bf,"mserver") == 0 ) {
             node_t *log_n = roxml_get_chld(item,"log",0);
             node_t *log_txt = roxml_get_txt(log_n,0);
             if ( log_n != NULL && log_txt != NULL && (c=roxml_get_content(log_txt,bf,sizeof(bf),&size)) != NULL && size > 0 ) { 
	                    sprintf(pl2d2->logdir,"%s/v%s",bf,pl2d2->mversion);
			    /* ADD statfs here to check filesys type */
	                    status=r_mkdir(pl2d2->logdir ,1,stderr);
			    if ( status != 0 ) {
			            fprintf(stderr,"Could not create log directory=%s\n",pl2d2->logdir);
                                    exit(1);
			    }
	                    snprintf(pl2d2->mlog,sizeof(pl2d2->mlog),"%s/mcontroller",pl2d2->logdir);
			    /* set files */
			    snprintf(pl2d2->dmlog,sizeof(pl2d2->dmlog),"%s/mdpmanager",pl2d2->logdir);
			    fprintf(stderr,"In xml Config File found log directory=%s\n",pl2d2->logdir);
             } else {
	                    sprintf(pl2d2->logdir,"%s/.suites/log/v%s",getenv("HOME"),pl2d2->mversion);
	                    status=r_mkdir(pl2d2->logdir,1,stderr);
			    if ( status != 0 ) {
			            fprintf(stderr,"Could not create log directory=%s\n",pl2d2->logdir);
                                    exit(1);
			    }
			    /* set files */
	                    sprintf(pl2d2->mlog,"%s/mcontroller",pl2d2->logdir);
			    sprintf(pl2d2->dmlog,"%s/mdpmanager",pl2d2->logdir);
                            fprintf(stderr,"Setting Defaults for log directory:%s\n",pl2d2->logdir);
             }
             
             node_t *web_n = roxml_get_chld(item,"web",0);
             node_t *web_txt = roxml_get_txt(web_n,0);
	     if ( web_n != NULL && web_txt != NULL && (c=roxml_get_content(web_txt,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    sprintf(pl2d2->web,"%s/v%s",bf,pl2d2->mversion);
	                    status=r_mkdir(pl2d2->web,1,stderr);
			    if ( status != 0 ) {
			            fprintf(stderr,"Could not create web directory=%s\n",pl2d2->web);
                                    exit(1);
			    }
	                    sprintf(pl2d2->web_dep,"%s/dependencies.html",pl2d2->web);
			    fprintf(stderr,"In xml Config File found web directory=%s\n",pl2d2->web);
             } else {
	                    sprintf(pl2d2->web,"%s/public_html/v%s",getenv("HOME"),pl2d2->mversion);
	                    status=r_mkdir(pl2d2->web,1,stderr);
			    if ( status != 0 ) {
			            fprintf(stderr,"Could not create web directory=%s\n",pl2d2->web);
                                    exit(1);
			    }
	                    sprintf(pl2d2->web_dep,"%s/dependencies_stat.html",pl2d2->web);
                            fprintf(stderr,"Setting Defaults for web path:%s\n",pl2d2->web);
             }
             
	     node_t *pparam_n = roxml_get_chld(item,"pparams",0);
             if ( pparam_n != NULL ) {
                      node_t *prc_n = roxml_get_attr(pparam_n,"maxNumOfProcess",0);
                      if ( prc_n != NULL && (c=roxml_get_content(prc_n,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    if ( (pl2d2->maxNumOfProcess=atoi(bf)) < 0 ) {
			              pl2d2->maxNumOfProcess=0;
			              fprintf(stderr,"Forcing maxNumOfProcess=%d\n",pl2d2->maxNumOfProcess);
                            } else if ( (pl2d2->maxNumOfProcess=atoi(bf)) > 8 ) {
			              pl2d2->maxNumOfProcess=8;
			              fprintf(stderr,"Forcing maxNumOfProcess=%d\n",pl2d2->maxNumOfProcess);
                            } else {
			              fprintf(stderr,"In xml Config File found maxNumOfProcess=%d\n",pl2d2->maxNumOfProcess);
                            }
                      } else {
		            pl2d2->maxNumOfProcess=4;
                            fprintf(stderr,"Setting Defaults for maxNumOfProcess:%d\n",pl2d2->maxNumOfProcess);
                      }

                      node_t *pmc_n = roxml_get_attr(pparam_n,"maxClientPerProcess",0);
                      if ( pmc_n != NULL && (c=roxml_get_content(pmc_n,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    if ( (pl2d2->maxClientPerProcess=atoi(bf)) <= 10 ) {
			              pl2d2->maxClientPerProcess=50; 
			              fprintf(stderr,"Forcing maxClientPerProcess=%d\n",pl2d2->maxClientPerProcess);
                            } else if ( (pl2d2->maxClientPerProcess=atoi(bf)) > 512 ) {
			              pl2d2->maxClientPerProcess=512;
			              fprintf(stderr,"Forcing maxClientPerProcess=%d\n",pl2d2->maxClientPerProcess);
                            } else {
			              fprintf(stderr,"In xml Config File found maxClientPerProcess=%d\n",pl2d2->maxClientPerProcess);
                            }
                      } else {
		            pl2d2->maxClientPerProcess=50;
                            fprintf(stderr,"Setting Defaults for maxClientPerProcess:%d\n",pl2d2->maxClientPerProcess);
                      }
             } else {
		       pl2d2->maxNumOfProcess=4;
		       pl2d2->maxClientPerProcess=50;
                       fprintf(stderr,"Setting Defaults for maxNumOfProcess:%d maxClientPerProcess:%d\n",pl2d2->maxNumOfProcess,pl2d2->maxClientPerProcess);
	     }

             
             node_t *param_n = roxml_get_chld(item,"dparams",0);
	     if ( param_n != NULL ) {
                   node_t *pfq = roxml_get_attr(param_n, "poll-freq",0);
                   if ( pfq != NULL && (c=roxml_get_content(pfq,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    if ( (pl2d2->pollfreq=atoi(bf)) <= 15 || (pl2d2->pollfreq=atoi(bf)) > 120 ) { 
			           pl2d2->pollfreq=30;
			           fprintf(stderr,"Forcing polling frequency=%d\n",pl2d2->pollfreq);
                            } else {
			           pl2d2->pollfreq=atoi(bf);
			           fprintf(stderr,"In xml Config File found polling frequency=%d\n",pl2d2->pollfreq);
                            } 
                   } else {
	                    pl2d2->pollfreq=30;
                            fprintf(stderr,"Setting Defaults for polling frequency=%d\n",pl2d2->pollfreq);
		   }
             
		   node_t *dto = roxml_get_attr(param_n, "dependencyTimeOut",0);
                   if ( dto != NULL && (c=roxml_get_content(dto,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                     if (  (pl2d2->dependencyTimeOut=atoi(bf)) <= 0 || (pl2d2->dependencyTimeOut=atoi(bf)) > 168 ) {
	                                 pl2d2->dependencyTimeOut=24;
			                 fprintf(stderr,"dependencyTimeOut invalid or too high. Forcing dependencyTimeOut=%d\n",pl2d2->dependencyTimeOut);
                             } else {
	                                 pl2d2->dependencyTimeOut=atoi(bf);
                                         fprintf(stderr,"In xml Config file found dependency time out period=%d\n",pl2d2->dependencyTimeOut);
			     }
                   } else {
	                   pl2d2->dependencyTimeOut=24;
                           fprintf(stderr,"Setting Defaults for dependency time out period=%d\n",pl2d2->dependencyTimeOut);
		   }
	     } else {
	                   pl2d2->pollfreq=30;
	                   pl2d2->dependencyTimeOut=24;
                           fprintf(stderr,"Setting Defaults for pollfreq:%d dependencyTimeOut:%d\n",pl2d2->pollfreq,pl2d2->dependencyTimeOut);
	     }

             node_t *dbz_n = roxml_get_chld(item,"debug_zone",0);
             node_t *dbz_txt = roxml_get_txt(dbz_n,0);
             if ( dbz_n != NULL && (c=roxml_get_content(dbz_txt,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
		      if ( (pl2d2->dzone=atoi(bf)) < 0 || (pl2d2->dzone=atoi(bf)) > 3 ) {
		                   pl2d2->dzone=1;
			           fprintf(stderr,"Setting Defaults for debug zone=%d\n",pl2d2->dzone);
                      } else {
			           pl2d2->dzone=atoi(bf);
			           fprintf(stderr,"In xml Config File found debug zone=%d\n",pl2d2->dzone);
                      }
             } else {
		       pl2d2->dzone=0;
                       fprintf(stderr,"Setting Defaults for debuging Zone=%d\n",pl2d2->dzone);
	     }

             node_t *eml_n = roxml_get_chld(item,"email",0);
	     if ( eml_n != NULL ) {
                   node_t *emlto = roxml_get_attr(eml_n,"to",0);
                   if ( emlto != NULL && (c=roxml_get_content(emlto,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    sprintf(pl2d2->emailTO,"%s",bf);
			    fprintf(stderr,"in xml file found  email to=%s\n",pl2d2->emailTO);
                   } else {
	                    sprintf(pl2d2->emailTO,"%s@ec.gc.ca",pl2d2->user);
		   }
             
		   node_t *emlcc = roxml_get_attr(eml_n, "cc",0);
                   if ( emlcc != NULL && (c=roxml_get_content(emlcc,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    sprintf(pl2d2->emailCC,"%s",bf);
			    fprintf(stderr,"in xml file found  email cc=%s\n",pl2d2->emailCC);
                   } else {
	                    sprintf(pl2d2->emailCC,"");
		   }
	     }
            
	     /* logs clean: validated numbers  */
	     node_t *cln_n = roxml_get_chld(item,"cleanlog",0);
	     if ( cln_n != NULL ) {
	         node_t *cln_cntr = roxml_get_attr(cln_n,"controller",0);
                 if ( cln_cntr != NULL && (c=roxml_get_content(cln_cntr,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    pl2d2->clean_times.controller_clntime=atoi(bf);
			    fprintf(stderr,"in xml file found clean main controller=%d\n",pl2d2->clean_times.controller_clntime);
                 } 
	     
	         node_t *cln_dmgr = roxml_get_attr(cln_n,"dpmanager",0);
                 if ( cln_dmgr != NULL && (c=roxml_get_content(cln_dmgr,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    pl2d2->clean_times.dpmanager_clntime=atoi(bf);
			    fprintf(stderr,"in xml file found clean dependency manager=%d\n",pl2d2->clean_times.dpmanager_clntime);
                 } 
	     
	         node_t *cln_ewrk = roxml_get_attr(cln_n,"eworker",0);
                 if ( cln_ewrk != NULL && (c=roxml_get_content(cln_ewrk,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    pl2d2->clean_times.eworker_clntime=atoi(bf);
			    fprintf(stderr,"in xml file found clean eternal worker=%d\n",pl2d2->clean_times.eworker_clntime);
                 } 
	     
	         node_t *cln_twrk = roxml_get_attr(cln_n,"tworker",0);
                 if ( cln_twrk != NULL && (c=roxml_get_content(cln_twrk,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    pl2d2->clean_times.tworker_clntime=atoi(bf);
			    fprintf(stderr,"in xml file found clean transient worker=%d\n",pl2d2->clean_times.tworker_clntime);
                 } 
             }

	     /* port range */
	     node_t *prt_n = roxml_get_chld(item,"portrange",0);
	     if ( prt_n != NULL ) {
	         node_t *prt_min = roxml_get_attr(prt_n,"min",0);
                 if ( prt_min != NULL && (c=roxml_get_content(prt_min,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    pl2d2->port_min=atoi(bf);
			    fprintf(stderr,"in xml file found start port=%d\n",pl2d2->port_min);
                 }
	         
		 node_t *prt_max = roxml_get_attr(prt_n,"max",0);
                 if ( prt_max != NULL && (c=roxml_get_content(prt_max,bf,sizeof(bf),&size)) != NULL && size > 0 ) {
	                    pl2d2->port_max=atoi(bf);
			    fprintf(stderr,"in xml file found end port=%d\n",pl2d2->port_max);
                 }
             } else {
                  fprintf(stderr,"Default port range (OS-given) \n");
                  pl2d2->port_min=0;
                  pl2d2->port_max=0;
               }
      } else {
             fprintf(stderr,"Incorrect root node name in xml config file:%s ... Setting Defaults \n",filename);
	     pl2d2->maxNumOfProcess=4;
	     pl2d2->maxClientPerProcess=20;
	     pl2d2->pollfreq=30;
	     pl2d2->dependencyTimeOut=24;
             pl2d2->dzone=0;

	     sprintf(pl2d2->web,"%s/public_html/v%s",getenv("HOME"),pl2d2->mversion);
	     status=r_mkdir(pl2d2->web,1,stderr);
	     if ( status != 0 ) {
	            fprintf(stderr,"Could not create web directory=%s\n",pl2d2->web);
                    exit(1);
	     }

	     sprintf(pl2d2->web_dep,"%s/dependencies.html",pl2d2->web);
	     sprintf(pl2d2->logdir,"%s/.suites/log/v%s",getenv("HOME"),pl2d2->mversion);
	     status=r_mkdir(pl2d2->logdir,1,stderr);
	     if ( status != 0 ) {
	            fprintf(stderr,"Could not create log directory=%s ... exiting\n",pl2d2->logdir);
                    exit(1);
	     }
	     sprintf(pl2d2->mlog,"%s/mcontroller",pl2d2->logdir);
	     sprintf(pl2d2->dmlog,"%s/mdpmanager",pl2d2->logdir);
	     sprintf(pl2d2->emailTO,"%s@ec.gc.ca",pl2d2->user);
	     sprintf(pl2d2->emailCC,"");
             fprintf(stderr,"Setting Defaults for log directory:%s\n",pl2d2->logdir);
             fprintf(stderr,"Setting Defaults for web directory:%s\n",pl2d2->web);
	     fprintf(stderr,"Setting Defaults for maxNumOfProcess:%d maxClientPerProcess:%d\n",pl2d2->maxNumOfProcess,pl2d2->maxClientPerProcess);
	     fprintf(stderr,"Setting Defaults for pollfreq:%d dependencyTimeOut:%d\n",pl2d2->pollfreq,pl2d2->dependencyTimeOut);
      }

      roxml_release(RELEASE_ALL);
      roxml_close(root);

      return (0);
}
/**
 * parse dependency file (polling for the moment )
 */
struct _depParameters * ParseXmlDepFile(char *filename , FILE * dmlog )
{

      FILE *doc=NULL;
      struct _depParameters *listParam=NULL;
      char bf[256];
      char buffer[2048];
      char tmpbf[2048];
      char *c;
      int size;

      memset(bf, '\0' , sizeof(bf));
      memset(buffer, '\0' , sizeof(buffer));

      if  ( (doc=fopen(filename, "r")) == NULL ) {
               fprintf(dmlog,"ParseXmlDepFile: Cannot Open XML Polling dependency file:%s \n",filename);
	       return(NULL);
      }

      if (doc) {
          fread(tmpbf,2048,1,doc);
	  fflush(doc);
	  snprintf(buffer,sizeof(buffer),"%s",tmpbf);
	  fclose(doc);
      }

      node_t *root = roxml_load_buf(buffer);
      node_t *item = roxml_get_chld(root,NULL,0);
      roxml_get_name(item,bf,sizeof(bf));

      node_t *type = roxml_get_attr(item, "type",0);
      c=roxml_get_content(type,bf,sizeof(bf),&size);

      if ( strcmp(bf,"pol") != 0 ) {
             fprintf(dmlog,"ParseXmlDepFile: Incorrect root node name in xml polling dependency file:%s\n",filename);
	     return (NULL);
      } else if  ( (listParam=(struct _depParameters *) malloc(sizeof(struct _depParameters)))  == NULL ) {
	          fprintf(dmlog,"ParseXmlDepFile: Cannot malloc on heap inside ParseXmlDepFile ... exiting \n");
		  exit(1);
      }
		    
      node_t *xp_n = roxml_get_chld(item,"xp",0);
      node_t *xp_txt = roxml_get_txt(xp_n,0);
      if ( xp_n != NULL && xp_txt != NULL ) {
                  c=roxml_get_content(xp_txt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_name,bf);
      } else {
                  strcpy(listParam->xpd_name,"");
      }

      node_t *xp_node = roxml_get_chld(item,"node",0);
      node_t *xp_nodetxt = roxml_get_txt(xp_node,0);
      if ( xp_node != NULL && xp_nodetxt != NULL ) {
                  c=roxml_get_content(xp_nodetxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_node,bf);
      } else {
                  strcpy(listParam->xpd_node,"");
      }
                    
      node_t *xp_indx = roxml_get_chld(item,"indx",0);
      node_t *xp_indxtxt = roxml_get_txt(xp_indx,0);
      if ( xp_indx != NULL && xp_indxtxt != NULL ) {
                  c=roxml_get_content(xp_indxtxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_indx,bf);
      } else {
                  strcpy(listParam->xpd_indx,"");
      }
      node_t *xp_xdate = roxml_get_chld(item,"xdate",0);
      node_t *xp_xdatetxt = roxml_get_txt(xp_xdate,0);
      if ( xp_xdate != NULL && xp_xdatetxt != NULL ) {
                  c=roxml_get_content(xp_xdatetxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_xpdate,bf);
      } else {
                  strcpy(listParam->xpd_xpdate,"");
      }
      node_t *xp_status = roxml_get_chld(item,"status",0);
      node_t *xp_statustxt = roxml_get_txt(xp_status,0);
      if ( xp_status != NULL && xp_statustxt != NULL ) {
                  c=roxml_get_content(xp_statustxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_status,bf);
      } else {
                  strcpy(listParam->xpd_status,"");
      }
      node_t *xp_largs = roxml_get_chld(item,"largs",0);
      node_t *xp_largstxt = roxml_get_txt(xp_largs,0);
      if ( xp_largs != NULL && xp_largstxt != NULL ) {
                  c=roxml_get_content(xp_largstxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_largs,bf);
      } else {
                  strcpy(listParam->xpd_largs,"");
      }

      node_t *xp_susr = roxml_get_chld(item,"susr",0);
      node_t *xp_susrtxt = roxml_get_txt(xp_susr,0);
      if ( xp_susr != NULL && xp_susrtxt != NULL ) {
                  c=roxml_get_content(xp_susrtxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_susr,bf);
      } else {
                  strcpy(listParam->xpd_susr,"");
      }
             
      node_t *xp_sxp = roxml_get_chld(item,"sxp",0);
      node_t *xp_sxptxt = roxml_get_txt(xp_sxp,0);
      if ( xp_sxp != NULL && xp_sxptxt != NULL ) {
                  c=roxml_get_content(xp_sxptxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_sname,bf);
      } else {
                  strcpy(listParam->xpd_sname,"");
      }

      node_t *xp_snode = roxml_get_chld(item,"snode",0);
      node_t *xp_snodetxt = roxml_get_txt(xp_snode,0);
      if ( xp_snode != NULL && xp_snodetxt != NULL ) {
                  c=roxml_get_content(xp_snodetxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_snode,bf);
      } else {
                  strcpy(listParam->xpd_snode,"");
      }
	     
      node_t *xp_sxdate = roxml_get_chld(item,"sxdate",0);
      node_t *xp_sxdatetxt = roxml_get_txt(xp_sxdate,0);
      if ( xp_sxdate != NULL && xp_sxdatetxt != NULL ) {
                  c=roxml_get_content(xp_sxdatetxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_sxpdate,bf);
      } else {
                  strcpy(listParam->xpd_sxpdate,"");
      }

      node_t *xp_slargs = roxml_get_chld(item,"slargs",0);
      node_t *xp_slargstxt = roxml_get_txt(xp_slargs,0);
      if ( xp_slargs != NULL && xp_slargstxt != NULL ) {
                  c=roxml_get_content(xp_slargstxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_slargs,bf);
      } else {
                  strcpy(listParam->xpd_slargs,"");
      }
	     
      node_t *xp_lockfile = roxml_get_chld(item,"lock",0);
      node_t *xp_lockfiletxt = roxml_get_txt(xp_lockfile,0);
      if ( xp_lockfile != NULL && xp_lockfiletxt != NULL ) {
                  c=roxml_get_content(xp_lockfiletxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_lock,bf);
      } else {
                  strcpy(listParam->xpd_lock,"");
      }

      node_t *xp_cnt = roxml_get_chld(item,"container",0);
      node_t *xp_cnttxt = roxml_get_txt(xp_cnt,0);
      if ( xp_cnt != NULL && xp_cnttxt != NULL ) {
                  c=roxml_get_content(xp_cnttxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_container,bf);
      } else {
                  strcpy(listParam->xpd_container,"");
      }

      node_t *xp_mversion = roxml_get_chld(item,"mversion",0);
      node_t *xp_mversiontxt = roxml_get_txt(xp_mversion,0);
      if ( xp_mversion != NULL && xp_mversiontxt != NULL ) {
                  c=roxml_get_content(xp_mversiontxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_mversion,bf);
      } else {
                  strcpy(listParam->xpd_mversion,"");
      }
	     
      node_t *xp_mdomain = roxml_get_chld(item,"mdomain",0);
      node_t *xp_mdomaintxt = roxml_get_txt(xp_mdomain,0);
      if ( xp_mdomain != NULL && xp_mdomaintxt != NULL ) {
                  c=roxml_get_content(xp_mdomaintxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_mdomain,bf);
      } else {
                  strcpy(listParam->xpd_mdomain,"");
      }
	     
      node_t *xp_key = roxml_get_chld(item,"key",0);
      node_t *xp_keytxt = roxml_get_txt(xp_key,0);
      if ( xp_key != NULL && xp_keytxt != NULL ) {
                  c=roxml_get_content(xp_keytxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_key,bf);
      } else {
                  strcpy(listParam->xpd_key,"");
      }

      node_t *xp_flow = roxml_get_chld(item,"flow",0);
      node_t *xp_flowtxt = roxml_get_txt(xp_flow,0);
      if ( xp_flow != NULL && xp_flowtxt != NULL ) {
                  c=roxml_get_content(xp_flowtxt,bf,sizeof(bf),&size);
                  strcpy(listParam->xpd_flow,bf);
      } else {
                  strcpy(listParam->xpd_flow,"");
      }

      node_t *xp_regtime = roxml_get_chld(item,"regtime",0);
      if ( xp_regtime != NULL ) {
                   node_t *xp_regtimedate = roxml_get_attr(xp_regtime,"date",0);
		   if ( xp_regtimedate != NULL ) {
                             c=roxml_get_content(xp_regtimedate,bf,sizeof(bf),&size);
                             strcpy(listParam->xpd_regtimedate,bf);
                   } else strcpy(listParam->xpd_regtimedate,"");
                   
		   node_t *xp_regtimepoch = roxml_get_attr(xp_regtime,"epoch",0);
		   if ( xp_regtimepoch != NULL ) {
                             c=roxml_get_content(xp_regtimepoch,bf,sizeof(bf),&size);
                             strcpy(listParam->xpd_regtimepoch,bf);
                   } else strcpy(listParam->xpd_regtimepoch,"");
     } else {
            fprintf(dmlog,"regtime null\n");
            strcpy(listParam->xpd_regtimedate,"");
            strcpy(listParam->xpd_regtimepoch,"");
     }
	     

     roxml_release(RELEASE_ALL);
     roxml_close(root);

     return (listParam);
}

/** 
*  logZone : log to file
*  there is  no synchro. btw processes
*  Note : errors are logged what ever the Zone is 
*/
void logZone(int this_Zone, int conf_Zone, FILE *fp  , char * txt, ...)
{
      va_list za;

      if ( this_Zone == conf_Zone ) {
             va_start( za, txt );
             vfprintf(fp,txt,za);
      }
}

/**
*   Function : typeofFile
*   object   : return a code corresponding to the type
*              of the file
*/
char typeofFile(mode_t mode)
{
    switch(mode & S_IFMT) {
        case S_IFREG:
        return('r');
        case S_IFDIR:
           return('d');
       case S_IFCHR:
           return('c');
       case S_IFBLK:
          return('b');
       case S_IFLNK:
          return('l');
       case S_IFIFO:
          return('p');
       case S_IFSOCK:
          return('s');
    }
  return ('-');
}
/**
 * SendFile
 * Send  *.waited_${signal} file to client  
 *
 * Note: socket mode is non-blocking
 *
 */
int SendFile (const char * filename , int sock, FILE *mlog ) 
{
    char * buffer;
    char   fsize[11]; /* size of the file encoded in 10 char, max : 9999999999 wow! */
    FILE * waitf;
    
    int bytes_written=0, bytes_read=0, bytes_left=0, total=0;
    struct stat st;

    /* get & format size of file in bytes */ 
    if ( stat(filename,&st) != 0 ) {
          fprintf(mlog,"SendFile:mserver cannot stat waitfile:%s\n", filename );
	  /* send a zero size */
          snprintf(fsize,sizeof(fsize),"%d",total);
          bytes_written=write(sock, fsize, sizeof(fsize));
          return(1);
    }
    
    snprintf(fsize,sizeof(fsize),"%lld",(long long) st.st_size);
    /* have to malloc here */
    if ( (buffer=(char *) malloc( st.st_size * sizeof(char))) == NULL ) {
          fprintf(mlog,"SendFile: Could not malloc\n");
	  return(1);
    }
   
    if ((waitf=fopen(filename,"r")) != NULL ) { 
          memset(buffer,'\0',st.st_size);
	  fread(buffer,st.st_size,1,waitf);
    } else {
          fprintf(mlog,"SendFile:mserver cannot read waited_end file:%s\n", filename );
	  free(buffer);
          return(1);
    }
    fclose(waitf);

    /* send size of file */
    bytes_written = write(sock, fsize, sizeof(fsize));

    bytes_left = st.st_size;
    while ( total < st.st_size ) 
    {
        bytes_written = send(sock, buffer+total, bytes_left, 0);

	if ( bytes_written == -1 ) break;
	total += bytes_written;
	bytes_left -= bytes_written;
    }

    free(buffer);

    return (bytes_written == -1)  ? 1 : 0;
}

/**
 * Obtain a lock on a file , and if  symlink is old by x sec remove it
 * return 
 *  0 if lock obtained 
 *  1 if not 
 *  
 */
int lock ( char *md5Token , _l2d2server L2D2 , char *xpn , char *node , FILE *mlog ) 
{
   int ret;
   char src[1024];
   char dest[1024];
   struct stat st;
   time_t now;
   double diff_t=0.0;
   
   sprintf(src,"%s/END_TASK_LOCK",L2D2.tmpdir);
   if ( access(src,R_OK) != 0 ) { 
           if ( (ret=touch(src)) != 0 ) {
	         fprintf(mlog,"cannot Touch file: lock on Tmpdir Xp=%s Node=%s\n",xpn,node);
		 return(1);
	   }
   }
  
   sprintf(dest,"%s/%s",L2D2.tmpdir,md5Token);
   ret=symlink("END_TASK_LOCK",dest);
   if ( ret != 0 ) {
        if ( (lstat(dest,&st)) == 0 ) {
              time(&now);
	      if ( (diff_t=difftime(now,st.st_mtime)) > LOCK_TIME_TO_LIVE ) {
	             ret=unlink(dest);
		     if ( ret == 0 ) 
                             fprintf(mlog,"symlink timeout xpn=%s node=%s Token:%s diff=%f removed\n",xpn,node,md5Token,diff_t);
                     else
                             fprintf(mlog,"symlink timeout xpn=%s node=%s Token:%s diff=%f could not remove\n",xpn,node,md5Token,diff_t);

		     return(1);
	      }
	} 
   } 

   return(ret);
}

/** 
 * remove a lock, 
 * return 0 if success 1 if not 
 */
int unlock ( char *md5Token , _l2d2server L2D2, char *xpn, char *node, FILE *mlog) 
{
   int ret;
   char src[1024],Ltime[25];
    
   sprintf(src,"%s/%s",L2D2.tmpdir,md5Token);

   get_time(Ltime,3);
   if ( access(src,R_OK) == 0 ) { 
       if ( (ret=unlink(src)) != 0 ) {
             fprintf(mlog,"unlink error:%d AT:%s xpn=%s node=%s Token:%s\n",ret,Ltime,xpn,node,md5Token);
	     return(1);
       } 
   } 
   

   return(0); 
}

/**
*  send mail routine
*  Note : message must end with \n.
*         message must not contain substring "\n.\n"
*/
int sendmail(const char *to, const char *from, const char *cc , const char *subject, const char *message, FILE * mlog )
{
     int retval = -1;
     FILE *mailpipe = popen("/usr/lib/sendmail -t", "w");
	      
     if (mailpipe != NULL) {
            fprintf(mailpipe, "To: %s\n", to);
            fprintf(mailpipe, "From: %s\n", from);
            fprintf(mailpipe, "CC: %s\n", cc);
            fprintf(mailpipe, "Subject: %s\n\n", subject);
            fwrite(message, 1, strlen(message), mailpipe);
            fwrite(".\n", 1, 2, mailpipe);
            pclose(mailpipe);
            retval = 0;
     } else {
             
              fprintf(mlog,"Failed to invoke sendmail\n"); 
     }

     return retval;
}

/**
* getDependencyFiles
* return parameters of inter-dependencies
* located under $HOME/.suites/maestrod/dependencies/polling/$version
*/
dpnode *getDependencyFiles(char *DDep, char *xp ,FILE *fp, const char *deptype)
{
   glob_t g_depFiles;
   size_t cnt;
   ssize_t r;
   int  g_ldp,ret;
   size_t Inode,this_inode;
   char buf[1024],  linkname[1024];
   struct _depParameters *depXp=NULL;
   char **p;

   /* get inode of xp , we dont rely on strcmp */
   if ( strcmp(xp,"all") != 0 ) {  
       if ( (Inode=get_Inode(xp)) == -1 ) return(NULL);
   }

   snprintf(buf,sizeof(buf),"%s/[1-2][0-9]*_[a-f0-9]*",DDep); 

   g_ldp = glob(buf, GLOB_NOSORT , globerr, &g_depFiles);
   if (  g_ldp == 0 && g_depFiles.gl_pathc > 0  ) {
        for (p=g_depFiles.gl_pathv , cnt=g_depFiles.gl_pathc ; cnt ; p++, cnt--) {
                /* must be a link */
                r=readlink(*p,linkname,1023); linkname[r] = '\0';
                if (  (depXp=(struct _depParameters *) ParseXmlDepFile(linkname,fp)) == NULL ) {
                        fprintf(stderr,"Problem parsing xml file:%s\n",linkname);
                        continue;
                } else {
                        /* use inode */
			if ( strcmp(deptype,"depender") == 0 ) {
                            /*This xp is the depender,  check on which xp this experiment depend  */
			    
                            if ( strcmp(xp,"all") == 0 ) {
                                     ret=insert(&PRT_listdep, xp, depXp->xpd_snode, depXp->xpd_name, depXp->xpd_node, depXp->xpd_sxpdate, depXp->xpd_xpdate, depXp->xpd_slargs, depXp->xpd_largs, depXp->xpd_key, *p, linkname);
                            } else {
                                     this_inode=get_Inode(depXp->xpd_sname);
                                     if ( this_inode == Inode  ) { 
                                           ret=insert(&PRT_listdep, xp, depXp->xpd_snode, depXp->xpd_name, depXp->xpd_node, depXp->xpd_sxpdate, depXp->xpd_xpdate, depXp->xpd_slargs, depXp->xpd_largs, depXp->xpd_key, *p, linkname);
                                     }
                            }
			} else {
                            /* This xp is the dependee, check which experiment depends on this xp */
			    
                            this_inode=get_Inode(depXp->xpd_name);
                            if ( this_inode == Inode  ) { 
                                      ret=insert(&PRT_listdep, xp, depXp->xpd_snode, depXp->xpd_name, depXp->xpd_node, depXp->xpd_sxpdate, depXp->xpd_xpdate, depXp->xpd_slargs, depXp->xpd_largs, depXp->xpd_key, *p, linkname);
                            }
			}
                }
        }
        globfree(&g_depFiles);
   }

   return (PRT_listdep);  
}

int globerr(const char *path, int eerrno)
{
    fprintf(stderr, "%s: %s\n", path, strerror(eerrno));
    return 0; 
}
/*
l2d2_Util_isNodeXState 

Returns an integer saying whether the targetted node is in a given state. 1 if node is in the desired state, 0 if not. 

Inputs:
const char * node - target node 
const char * loopargs - what is the target node's loop index in csv name=value format
const char * datestamp - what datestamp are we verifying
const char * exp - what experiment is the node in 
const char * state - what state are we verifying 
const char * state - what state are we verifying 

*/
int l2d2_Util_isNodeXState (const char* node, const char* loopargs, const char* datestamp, const char* exp, const char* state) {  

  SeqNameValuesPtr loopArgs = NULL;
  char stateFile[1024];
  char * extension=NULL;
  int result=0; 
  memset( stateFile, '\0', sizeof (stateFile));

  if(strlen (loopargs) != 0) {

    if( SeqLoops_parseArgs( &loopArgs, loopargs ) == -1 ) {
       fprintf(stderr,"ERROR: Invalid loop arguments: %s\n",loopargs);
    }
    SeqUtil_stringAppend( &extension, ".");
    SeqUtil_stringAppend( &extension, SeqLoops_getExtFromLoopArgs(loopArgs)); 

  } else {
    SeqUtil_stringAppend( &extension, "");
  } 
  sprintf(stateFile,"%s/sequencing/status/%s/%s%s.%s", exp, datestamp, node, extension, state);
  
  result=(access(stateFile,R_OK) == 0); 
 
  SeqNameValues_deleteWholeList( &loopArgs );
  free(extension);
  return result; 

}

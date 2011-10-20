#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pwd.h>
#include "SeqListNode.h"
#include <errno.h>        /* errno */
#include "SeqUtil.h"

int SEQ_TRACE = 0;
int SEQ_DEBUG = 0;

void raiseError(const char* fmt, ... );


/********************************************************************************
SeqUtil_trace




********************************************************************************/

void SeqUtil_TRACE (char * fmt, ...) {
   
   va_list ap;
   if ( SEQ_TRACE == 1 ) {
      va_start (ap, fmt);
      vfprintf (stdout, fmt, ap);
      va_end (ap);
   }
}

void SeqUtil_setDebug (int _debug) {
   SEQ_DEBUG = _debug;
}

int SeqUtil_isDebug (int _debug) {
   return SEQ_DEBUG;
}

void SeqUtil_setTrace (int _trace) {
   SEQ_TRACE = _trace;
}

int SeqUtil_isTraceOn (int _trace) {
   return SEQ_TRACE;
}

void raiseError(const char* fmt, ... ) {
   va_list ap;
   va_start (ap, fmt);
   printf( "!!!!!!!!!!!!!!!!!!!!!!!!!!!! APPLICATION ERROR !!!!!!!!!!!!!!!!!!!!!!!!!!!!\n" );
   vfprintf (stderr, fmt, ap);
   va_end (ap);
   printf( "Program exiting with status 1!\n" );

   exit(1);
}

void SeqUtil_checkExpHome (char * _expHome) {

   DIR *dirp = NULL;

   if ( _expHome != NULL ) {
      dirp = opendir(_expHome);
      if (dirp == NULL) {
         raiseError("ERROR: invalid SEQ_EXP_HOME=%s\n",_expHome);
      }
      closedir(dirp);
   } else {
      raiseError("ERROR: SEQ_EXP_HOME not set!\n");
   }

}


/********************************************************************************
*actions: print action message
********************************************************************************/
void actions(char *signal, char* flow, char *node) {
 printf("\n**************** SEQ \"%s\" \"%s\" \"%s\" Action Summary *******************\n",signal, flow, node);
}

/********************************************************************************
*actions: print action message
********************************************************************************/
void actionsEnd(char *signal, char* flow, char* node) {
 printf("\n**************** SEQ \"%s\" \"%s\" \"%s\" Action ENDS *******************\n",signal, flow, node);
}

/********************************************************************************
*genFileList: scan a directory 'directory' and return a list of files 'filelist'
*  using the the filter 'filters'.
********************************************************************************/
int genFileList(LISTNODEPTR *fileList,const char *directory,LISTNODEPTR *filterList) {

LISTNODEPTR tmplist=NULL;
LISTNODEPTR tmpfilters=NULL;
char *filter=NULL;
DIR *dirp=NULL;
struct dirent *direntp=NULL;

 direntp=(struct dirent *) malloc(sizeof(struct dirent));

 tmpfilters=*filterList;

 filter = (char *) malloc(strlen(tmpfilters->data)+1);
 strcpy(filter,tmpfilters->data);

 while (filter != NULL) {
    SeqUtil_TRACE("maestro.genFileList() opening directory=%s trying to match pattern %s\n",directory, filter);
    dirp = opendir(directory);
    if (dirp == NULL) {
       fprintf(stderr,"maestro: invalid directory path %s\n",directory);
       *fileList = NULL;
       return(1);
    }
    while ( (direntp = readdir(dirp)) != NULL) {
       if (match(direntp->d_name,filter) == 1) {
          SeqUtil_TRACE("maestro.genFileList() found file matching=%s\n",direntp->d_name );
          SeqListNode_insertItem(&tmplist,direntp->d_name);
       }
    }
    closedir(dirp);
    free(filter);
    tmpfilters=tmpfilters->nextPtr;
    if (tmpfilters != NULL) {
       filter = (char *) malloc(strlen(tmpfilters->data)+1);
       strcpy(filter,tmpfilters->data);
    } else {
       filter=NULL;
    }
 }
 free(direntp);
 *fileList = tmplist;
 return(0);
}

/********************************************************************************
*removeFile: Removes the named file 'filename'; it returns zero if succeeds 
* and a nonzero value if it does not
********************************************************************************/
int removeFile(char *filename) {
   int status=0;

   printf( "maestro.removeFile() removing %s\n", filename );
   status = remove(filename);
   return(status);
}


/********************************************************************************
*touch: simulate a "touch" on a given file 'filename'
********************************************************************************/
int touch(char *filename) {
   FILE *actionfile;
   
   printf("maestro.touch(): filename=%s\n",filename);

   if ((actionfile = fopen(filename,"r")) != NULL ) {
      fclose(actionfile);
      utime(filename,NULL); /*set the access and modification times to current time */     
   } else {
      if ((actionfile = fopen(filename,"w+")) == NULL) {
         fprintf(stderr,"Error: maestro cannot touch file:%s\n",filename);
         return(1);
      }
      fclose(actionfile);
      chmod(filename,00664);
   }
   return(0); 
}



/* returns 1 if succeeds, 0 failure */
int isFileExists( const char* lockfile, const char *caller ) {
   if ( access(lockfile, R_OK) == 0 ) {
      /* SeqUtil_TRACE( "SeqUtil.isFileExists() caller:%s found lock file=%s\n", caller, lockfile ); */
      printf( "caller:%s found lock file=%s\n", caller, lockfile );
      return 1;
   }
   /* SeqUtil_TRACE( "SeqUtil.isFileExists() caller:%s missing lock file=%s\n", caller, lockfile ); */
   printf( "caller:%s missing lock file=%s\n", caller, lockfile );
   return 0;
}

int SeqUtil_isDirExists( const char* path_name ) {
   DIR *pDir = NULL;
   int bExists = 0;

   if ( path_name == NULL) return 0;
   pDir = opendir (path_name);

   if (pDir != NULL)
   {
      bExists = 1;
      (void) closedir (pDir);
   }

   return bExists;
}

char *SeqUtil_getPathLeaf (const char *full_path) {
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

char *SeqUtil_getPathBase (const char *full_path) {
  char *split = NULL ,*work_string = NULL ,*chreturn =NULL; 
  work_string = strdup(full_path);
  split = strrchr (work_string,'/');
  if (split != NULL) {
    *split = '\0';
    chreturn = strdup (work_string);
  }
  free( work_string );
  return chreturn;
}

int SeqUtil_mkdir( const char* dir_name, int is_recursive ) {
   char tmp[1000];
   char *split = NULL, *work_string = NULL; 
   SeqUtil_TRACE ( "SeqUtil_mkdir: dir_name %s recursive? %d \n", dir_name, is_recursive );
   if ( is_recursive == 1) {
      work_string = strdup( dir_name );
      strcpy( tmp, "/" );
      split  = strtok( work_string, "/" );
      if( split != NULL ) {
         strcat( tmp, split );
      }
      while ( split != NULL ) {
         strcat( tmp, "/" );
         if( ! SeqUtil_isDirExists( tmp ) ) {
            printf ( "SeqUtil_mkdir: creating dir %s\n", tmp );
            if ( mkdir( tmp, 0755 ) == -1 ) {
               fprintf ( stderr, "ERROR: %s\n", strerror(errno) );
               return(EXIT_FAILURE);
            }
         }

         split = strtok (NULL,"/");
         if( split != NULL ) {
            strcat( tmp, split );
         }
      }
   } else {
      if( ! SeqUtil_isDirExists( dir_name ) ) {
         if ( mkdir( dir_name, 0755 ) == -1 ) {
            printf ( "SeqUtil_mkdir: creating dir %s\n", dir_name );
            fprintf ( stderr, "ERROR: %s\n", strerror(errno) );
            return(EXIT_FAILURE);
         }
      }
   }
   free( work_string );
   return(0);
}


/* dynamic string cat, content of source is freed */
void SeqUtil_stringAppend( char** source, char* data )
{
   char* newDataPtr = NULL;
   if ( *source != NULL ) {
      if( ! (newDataPtr = malloc( strlen(*source) + strlen( data ) + 1 )  )) {
         printf( "SeqUtil_stringAppend malloc: Out of memory!\n"); 
	 return;
      }
      strcpy( newDataPtr, *source );
      strcat( newDataPtr, data );
   } else {
      if( ! (newDataPtr = malloc( strlen( data ) + 1 ) ) ) {
         printf( "SeqUtil_stringAppend malloc: Out of memory!\n"); 
	 return;
      }
      strcpy( newDataPtr, data );
   }

   free( *source );
   *source = newDataPtr;
}

int SeqUtil_tokenCount( char* source, char* tokenSeparator )
{
   int count = 0;
   char *tmpSource = NULL, *tmpstrtok = NULL; 

   tmpSource = (char*) malloc( strlen( source ) + 1 );
   strcpy( tmpSource, source );
   tmpstrtok = (char*) strtok( tmpSource, tokenSeparator );

   while ( tmpstrtok != NULL ) {
        count++;
        tmpstrtok = (char*) strtok(NULL, tokenSeparator);
   }

   free(tmpSource);
   return count;
}

/* fixes the path name and returns the new path
removes '/' at the end and ands '/' at beginning if not there
*/
char* SeqUtil_fixPath ( const char* source ) {
   char *working = NULL, *new = NULL;
   int len = 0;
   SeqUtil_stringAppend( &new, "" );
   if( source == NULL || (len = strlen( source )) == 0 ) {
      return new;
   }
   working = strdup( source );
   if( source[0] != '/' ) {
      SeqUtil_stringAppend( &new, "/" );
   }
   if( source[len-1] == '/' ) {
      working[len-1] = '\0';
   }
   SeqUtil_stringAppend( &new, working );
   free( working );
   SeqUtil_TRACE( "SeqUtil_fixPath source:%s new:%s\n", source, new );
   return new;
}


/* validates username + exp against the current user and current
exp and returns the path of the suite */
/* 2010-10-21... not used anymore, should be removed later... */
char* SeqUtil_getExpPath( const char* username, const char* exp ) {
   char *home = NULL, *expPath = NULL, *currentUser = NULL;
   char *currentExpPath = getenv("SEQ_EXP_HOME");
   struct passwd* currentPasswd = NULL;
   currentPasswd = (struct passwd*) getpwuid(getuid());
   currentUser = strdup( currentPasswd->pw_name );

   SeqUtil_stringAppend( &expPath, "" );
   if( strcmp( (char*) username, currentUser) == 0 ) {
      home = getenv("HOME");
      SeqUtil_stringAppend( &expPath, home );
      SeqUtil_stringAppend( &expPath, "/.suites/" );
      SeqUtil_stringAppend( &expPath, (char*) exp );
   }
   printf( "SeqUtil_getExpPath returning value: %s\n", expPath );
   return expPath;
}

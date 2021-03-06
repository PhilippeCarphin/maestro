/* tictac.c - Datestamp utilities for the Maestro sequencer software package.
 * Copyright (C) 2011-2015  Operations division of the Canadian Meteorological Centre
 *                          Environment Canada
 *
 * Maestro is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation,
 * version 2.1 of the License.
 *
 * Maestro is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#include "tictac.h"
#include "SeqUtil.h"
#include "l2d2_commun.h"
#include "l2d2_socket.h"
#include "QueryServer.h"
#include "SeqUtilServer.h"

/*****************************************************************************
* tictac:
* Read or set the datestamp of a given experiment.
*
*
******************************************************************************/

/* 
tictac_setDate

Sets the date inside the $EXP_HOME/ExpDate file to the value defined.

Inputs:
  _expHome - pointer to the entrance of the experiment
  datestamp - pointer to the modified value of the date

*/

extern void tictac_setDate( char* _expHome, char* datestamp ) {

   char *dateFileName = NULL;
   char *job="TICTAC";
   char *tmpfromaestro=getenv("FROM_MAESTRO");
   SeqUtil_TRACE( TL_FULL_TRACE, "maestro.tictac_setDate( %s, %s ) called \n", _expHome, datestamp);
   _touch = touch_svr;
   if  ( tmpfromaestro == NULL ) {
      if ( (MLLServerConnectionFid=OpenConnectionToMLLServer( _expHome , job , _expHome)) < 0 ) {
         _touch = touch_nfs;
      } else {
         _touch = touch_svr;
      }
   } 

   SeqUtil_checkExpHome(_expHome);
   checkValidDatestamp(datestamp); 
   SeqUtil_TRACE(TL_FULL_TRACE, "maestro.tictac_setDate() setting date to=%s\n", datestamp); 
   fprintf(stderr,"Warning: use of tictac -s $datestamp is deprecated. Please use SEQ_DATE environment variable or a -d $datestamp argument to maestro or expbegin calls.\n"); 
   SeqUtil_stringAppend( &dateFileName, _expHome );
   SeqUtil_stringAppend( &dateFileName, "/logs/" );
   SeqUtil_stringAppend( &dateFileName, datestamp );
   SeqUtil_stringAppend( &dateFileName, "_nodelog" );

   if ( _touch(dateFileName, _expHome) != 0 ) raiseError( "Cannot touch log file: %s\n", dateFileName );  

   if  ( tmpfromaestro == NULL && MLLServerConnectionFid > 0 ) {
      CloseConnectionWithMLLServer(MLLServerConnectionFid);
   }
   free (dateFileName);
}


/* 
tictac_getDate

Gets the date defined inside the $EXP_HOME/ExpDate file.

Inputs:

  _expHome - pointer to the entrance of the experiment
  format - pointer to the output format required
  datestamp - pointer to a datestamp value (used only if non-null)

*/

const char* tictac_getDate(const char* _expHome, const char *format, const char * datestamp ) {

   int i = 0;
   char *dateFileName = NULL, *tmpLatestFile=NULL;
   char statePattern[SEQ_MAXFIELD] = {'\0'};
   char dateValue[PADDED_DATE_LENGTH+1] = {'\0'};
   char* returnDate = NULL, *envDate=NULL;
   size_t counter=0;
   glob_t glob_logs; 
   struct stat *statbuf = NULL; 
   time_t latest = 0;
   memset( statePattern, '\0', sizeof statePattern );
   memset( dateValue, '\0', sizeof dateValue );

   sprintf( statePattern,"%s/logs/*_nodelog", _expHome);


   SeqUtil_checkExpHome (_expHome);
   if( datestamp != NULL) {
        strncpy(dateValue,datestamp,PADDED_DATE_LENGTH);
   } else if ((envDate = getenv("SEQ_DATE")) != NULL ) {
        strncpy(dateValue,envDate,PADDED_DATE_LENGTH);
   } else {
      glob(statePattern, GLOB_NOSORT,0 ,&glob_logs);
      if (glob_logs.gl_pathc==0) {
         SeqUtil_TRACE(TL_MEDIUM, "Warning: No latest datestamp available in %s/logs. Datestamp used is 197001010000 (epoch).\n", _expHome );
         sprintf(dateValue,"19700101000000");
      } else {
         while(counter < glob_logs.gl_pathc) {
            statbuf=malloc(sizeof(struct stat));
            /* Get entry's information. */
            if (stat(glob_logs.gl_pathv[counter], statbuf) == -1)
               continue;
            if (difftime(statbuf->st_mtime,latest) > 0) {
               latest=statbuf->st_mtime;
               free(tmpLatestFile);
               tmpLatestFile=strdup((glob_logs.gl_pathv[counter]));
            }
            ++counter;
            free(statbuf);
         }
         globfree(&glob_logs);
         dateFileName = SeqUtil_getPathLeaf( (const char*) (tmpLatestFile) );
         sprintf(dateValue,"%s", strtok( dateFileName, "_" ));
      }
   }

   /* pad to PADDED_DATE_LENGTH */
   i = strlen(dateValue);
   while ( i < PADDED_DATE_LENGTH ){
      dateValue[i++] = '0';
   }
   dateValue[PADDED_DATE_LENGTH] = '\0';

   SeqUtil_TRACE(TL_FULL_TRACE,"tictac_getDate() checking validity of dateValue ... \n");
   checkValidDatestamp(dateValue);

   if (format != NULL) {
      for_tokens(tmpstrtok, format, "%", sp) {
         if (strcmp(tmpstrtok, "Y") == 0)
            printf("%.*s", 4, &dateValue[0]);
         if (strcmp(tmpstrtok, "M") == 0)
            printf("%.*s", 2, &dateValue[4]);
         if (strcmp(tmpstrtok, "D") == 0)
            printf("%.*s", 2, &dateValue[6]);
         if (strcmp(tmpstrtok, "H") == 0)
            printf("%.*s", 2, &dateValue[8]);
         if (strcmp(tmpstrtok, "Min") == 0)
            printf("%.*s", 2, &dateValue[10]);
         if (strcmp(tmpstrtok, "S") == 0)
            printf("%.*s", 2, &dateValue[12]);
      }
   }

   if ((returnDate = malloc( strlen(dateValue) + 1 )) != NULL ) {
      strcpy( returnDate, dateValue );
   } else {
      raiseError("ERROR: Unable to allocate memory in tictac_getDate()\n"); 
   }
   
   free(dateFileName);
   free(tmpLatestFile);

   return (const char *)returnDate;
}


/* 
checkValidDatestamp

verifies the datestamp for the proper format and bounds

Inputs:

  datestamp - datestamp to verify 

*/


extern void checkValidDatestamp(char *datestamp){

   char *tmpDateString=NULL;
   int validationInt = 0, dateLength=0;

   dateLength=strlen(datestamp);
   if ( dateLength < 8 || dateLength > 14 ) 
      raiseError("ERROR: Datestamp must contain between 8 and 14 characters (YYYYMMDD[HHMMSS]).\n"); 

   if ((tmpDateString= (char*) malloc(5)) != NULL ) {
      sprintf(tmpDateString, "%.*s",4,&datestamp[0]);
      validationInt = atoi(tmpDateString);
   } else {
      raiseError("ERROR: Unable to allocate memory in tictac_checkValidDatestamp()\n"); 
   }
   if (validationInt < 0  || validationInt > 9999)
     raiseError("ERROR: Year %d outside set bounds of [0,9999].\n", validationInt); 

   free(tmpDateString);

   if ((tmpDateString= (char*) malloc(3)) != NULL ) {
      sprintf(tmpDateString, "%.*s",2,&datestamp[4]);
      validationInt = atoi(tmpDateString);
   } else {
      raiseError("ERROR: Unable to allocate memory in tictac_checkValidDatestamp()\n"); 
   }
   if (validationInt < 0  || validationInt > 12)
      raiseError("ERROR: Month %d outside set bounds of [0,12].\n", validationInt); 
   free(tmpDateString);

   if ((tmpDateString= (char*) malloc(3)) != NULL ) {
      sprintf(tmpDateString, "%.*s",2,&datestamp[6]);
      validationInt = atoi(tmpDateString);
   } else {
      raiseError("ERROR: Unable to allocate memory in tictac_checkValidDatestamp()\n"); 
   }

   if (validationInt < 0  || validationInt > 31)
      raiseError("ERROR: Day %d outside set bounds of [0,31].\n", validationInt); 
   free(tmpDateString);

   if ( dateLength >= 10) {
      if ((tmpDateString= (char*) malloc(3))!= NULL ){
         sprintf(tmpDateString, "%.*s",2,&datestamp[8]);
         validationInt = atoi(tmpDateString);
      } else {
         raiseError("ERROR: Unable to allocate memory in tictac_checkValidDatestamp()\n"); 
      }

      if (validationInt < 0  || validationInt > 23)
        raiseError("ERROR: Hour %d outside set bounds of [0,23].\n", validationInt); 

      free(tmpDateString);
   }

   if ( dateLength >= 12) {

      if ((tmpDateString= (char*) malloc(3)) != NULL ){
         sprintf(tmpDateString, "%.*s",2,&datestamp[10]);
         validationInt = atoi(tmpDateString);
      } else {
         raiseError("ERROR: Unable to allocate memory in tictac_checkValidDatestamp()\n"); 
      }

      if (validationInt < 0  || validationInt > 59)
         raiseError("ERROR: Minute %d outside set bounds of [0,59].\n", validationInt); 

      free(tmpDateString);
   }

   if ( dateLength == 14) {
      if ((tmpDateString= (char*) malloc(3)) != NULL) {
         sprintf(tmpDateString, "%.*s",2,&datestamp[12]);
         validationInt = atoi(tmpDateString);
      } else {
         raiseError("ERROR: Unable to allocate memory in tictac_checkValidDatestamp()\n"); 
      }

      if (validationInt < 0  || validationInt > 59)
         raiseError("ERROR: Second %d outside set bounds of [0,59].\n", validationInt); 
   free(tmpDateString);
   }
}


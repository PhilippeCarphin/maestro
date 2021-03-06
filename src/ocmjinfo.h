/* Part of the Maestro sequencer software package.
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


/******************************************************************************
*FILE: ocmjinfo.h
*
*AUTHOR: Ping An Tan
******************************************************************************/

#define JINFO_NONE          "none"
#define JINFO_MAX_FIELD     10000
#define JINFO_MAX_TMP       200
#define JINFO_MAXLINE       1000
#define JINFO_JOBSIZE       7
#define JINFO_MAX_FMT       50

struct JlistNode {
    char *data;
    struct JlistNode *nextPtr;
  };

typedef struct JlistNode JLISTNODE;
typedef JLISTNODE *JLISTNODEPTR;

struct ocmjinfos {
   char *job;
   int catchup;
   char *cpu;
   int wallclock;
   char *queue;
   char *machine_queue;
   char *machine;
   int mpi;
   int silent;
   char *memory;
   JLISTNODEPTR abort;
   JLISTNODEPTR depend;
   JLISTNODEPTR submit;
   char *run;
   char *hour;
   char *loop_current;
   char *loop_start;
   char *loop_set;
   char *loop_total;
   char *loop_color;
   char *loop_reference;
   char *master;
   char *alias_job;
   char *args;
   int error;
   char errormsg[JINFO_MAX_FIELD];
};


/****************************************************************
*insertItem: Insert an item 's' into the list 'list'. The memory
*necessary to store the string 's' will be allocated by insertIem.
*****************************************************************/
extern void insertItem(JLISTNODEPTR *list, char *s);

/****************************************************************
*deleteItem: Delete the first item from the list 'list'. It returns
*the string that had been deleted. The memory will be deallocated by
*deleteItem.
*****************************************************************/
extern char *deleteItem(JLISTNODEPTR *list);

/****************************************************************
*isListEmpty: Returns 1 if list 'sPtr' is empty, eitherwise 0
*****************************************************************/
extern int isListEmpty(JLISTNODEPTR sPtr);

/****************************************************************
*deleteWholeList: delete the list 'list' and deallocate the memories
*****************************************************************/
extern void deleteWholeList(JLISTNODEPTR *list);

/****************************************************************
*printList: print the list 'list'
*****************************************************************/
extern void printList(JLISTNODEPTR list);

/****************************************************************
*deallocateOcmjinfo: deallocate the structure ocmjinfos pointed by
* ptrocmjinfo.
*****************************************************************/
extern void deallocateOcmjinfo(struct ocmjinfos **ptrocmjinfo);

/****************************************************************
*printOcmjinfo: print the contents of ptrocmjinfo
*****************************************************************/
extern void printOcmjinfo(struct ocmjinfos *ptrocmjinfo);

/****************************************************************
* NAME: ocmjinfo
* PURPOSE: get information for a specified operational job.
* INPUT: job - jobname[_HH][_SSS]
*              where HH  - zulu [00,06,12,18]
*                    SSS - series
*              note: HH is only required for runs r[1-2], g[1-6]
* OUTPUT: the result is returned on a ocmjinfos structure.
* example: struct ocmjinfos *ocmjinfo_res;
*          ocmjinfo_res = malloc(sizeof(struct ocmjinfos));
*          *ocmjinfo_res = ocmjinfo("r1start_12");
*****************************************************************/
extern struct ocmjinfos ocmjinfo(char *job);







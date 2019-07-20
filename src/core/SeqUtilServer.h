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


#ifndef _SEQ_UTIL_SERVER
#define _SEQ_UTIL_SERVER
#include <openssl/md5.h>
#include "SeqListNode.h"
#include "l2d2_socket.h"

int  removeFile_svr(const char *filename, const char * _seq_exp_home ) ;

extern int  (*_removeFile)(const char *filename, const char * _seq_exp_home ) ;

/* this library fnc is allready declared in unistd.h : int  access (char *filename, int mode); */
int  access_svr(const char *filename, int mode, const char * _seq_exp_home ) ;
extern int  (*_access)(const char *filename, int mode, const char * _seq_exp_home ) ;

int  touch_svr(const char *filename, const char * _seq_exp_home ) ;
extern int  (*_touch)(const char *filename, const char * _seq_exp_home );

FILE * fopen_svr ( const char *filename , int  sock );
extern FILE * (*_fopen) ( const char *filename , int  sock );

int SeqUtil_mkdir_svr ( const char* dirname, int notUsed, const char * _seq_exp_home );
extern int (*_SeqUtil_mkdir) ( const char* dirname, int notUsed, const char * _seq_exp_home );

int  isFileExists_svr ( const char* lockfile, const char *caller, const char * _seq_exp_home ) ;
extern int  (*_isFileExists) ( const char* lockfile, const char *caller, const char * _seq_exp_home ) ;

int globPath_svr (const char *pattern, int flags, int (*errfunc) (const char *epath, int eerrno), const char * _seq_exp_home );
extern int (*_globPath) (const char *pattern, int flags, int (*errfunc) (const char *epath, int eerrno), const char * _seq_exp_home );

LISTNODEPTR globExtList_svr (const char *pattern, int flags, int (*errfunc) (const char *epath, int eerrno) );
extern LISTNODEPTR (*_globExtList) (const char *pattern, int flags, int (*errfunc) (const char *epath, int eerrno) );

int WriteNodeWaitedFile_svr (const char* seq_xp_home, const char* nname, const char* datestamp,  const char* loopArgs,
                              const char* filename, const char* statusfile ); 

int WriteForEachFile_svr (const char* seq_xp_home, const char* nname, const char* datestamp,  const char* loopArgs,
                              const char* filename, const char* statusfile ); 

/*nt WriteInterUserDepFile_svr (const char *filename, const char *DepBuf, const char *ppwdir, const char *maestro_version,
                               const char *datestamp, const char *md5sum);
*/
int lock_svr  ( const char *filename , const char * datestamp, const char * _seq_exp_home );
extern int (*_lock)  ( const char *filename , const char * datestamp, const char * _seq_exp_home );
int unlock_svr  ( const char *filename , const char * datestamp, const char * _seq_exp_home );
extern int (*_unlock)  ( const char *filename , const char * datestamp, const char * _seq_exp_home );

#endif

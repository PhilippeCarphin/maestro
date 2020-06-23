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


#ifndef L2D2SERVER_H
#define L2D2SERVER_H


/* structure that holds l2d2server 'global' data */
typedef struct {
      unsigned int clean_flag;
      unsigned int controller_clntime;
      unsigned int dpmanager_clntime;
      unsigned int eworker_clntime;
      unsigned int tworker_clntime;
} _clean_times;

typedef struct {
   unsigned int pid;
   unsigned int depProcPid;
   int      sock;     
   int      port;
   int      pollfreq;
   int      dependencyTimeOut;
   int      dzone;
   int      maxNumOfProcess;
   int      maxClientPerProcess;
   char     ip[32];
   char     host[128];
   char     logdir[256];
   char     mlog[256];
   char     dmlog[256];
   char     web[256];
   char     auth[256];
   char     web_dep[256];
   char     lock_server_pid_file[256];
   char     dependencyPollDir[256];
   char     home[256];
   char     *user;
   char     *tmpdir;
   char     *m5sum;
   char     *mversion;
   char     *mshortcut;
   char     emailTO[128];
   char     emailCC[128];
   unsigned int port_min;
   unsigned int port_max;
   _clean_times clean_times;
} _l2d2server;

typedef struct _depParameters {
   char xpd_name[256];
   char xpd_node[256];
   char xpd_indx[15];
   char xpd_xpdate[20];
   char xpd_status[20];
   char xpd_largs[256];
   char xpd_susr[50];
   char xpd_sname[256];
   char xpd_snode[256];
   char xpd_sxpdate[20];
   char xpd_slargs[256];
   char xpd_sub[1024];
   char xpd_lock[1024];
   char xpd_container[1024];
   char xpd_mversion[20];
   char xpd_mdomain[256];
   char xpd_regtimedate[20];
   char xpd_regtimepoch[20];
   char xpd_flow[32];
   char xpd_key[33];
} depParameters;

typedef struct {
      char host[64];
      char xp[256];
      char node[512];
      char signal[16];
      char Open_str[1024];
      char Close_str[1024];
      unsigned int trans;
} _l2d2client;

typedef enum _TypeOfWorker {
      ETERNAL,
      TRANSIENT
} TypeOfWorker;

#endif

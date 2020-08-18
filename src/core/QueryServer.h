/* QueryServer.h - Basic server code the Maestro sequencer software package.
 */

#ifndef QUERY_SERVER_H
#define QUERY_SERVER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <signal.h>
#include <ctype.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <errno.h>
#include <pwd.h>
#include <libgen.h>
#include <time.h>
#include <unistd.h>
#include <sys/types.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/stat.h>
#include <sys/param.h>

#define MAXBUF 1024

typedef enum _ServerActions {
  SVR_ACCESS = 0,
  SVR_TOUCH,
  SVR_REMOVE,
  SVR_CREATE,
  SVR_IS_FILE_EXISTS,
  SVR_GLOB_PATTERN_COUNT,
  SVR_GLOB_PATTERN_LIST,
  SVR_MKDIR,
  SVR_LOCK,
  SVR_UNLOCK,
  SVR_WRITE_WNF,
  SVR_LOG_NODE,
  SVR_WRITE_USERDFILE,
  SVR_REGISTER_DEPENDENCY_POLLING,
  SVR_REGISTER_DEPENDENCY_NOTIFY,
  SVR_REGISTER_DEPENDENCY_SSH
} ServerActions;

int Query_L2D2_Server(int, ServerActions action, const char *, const char *,
                      const char *_seq_exp_home);
int OpenConnectionToMLLServer(const char *, const char *,
                              const char *_seq_exp_home);
void CloseConnectionWithMLLServer(int);
int revert_nfs(const char *, ServerActions action, const char *,
               const char *_seq_exp_home);
#endif

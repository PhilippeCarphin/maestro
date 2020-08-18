/* Part of the Maestro sequencer software package.
 */

#ifndef L2D2COMMUN_H
#define L2D2COMMUN_H
#include <openssl/md5.h>

void get_time(char *, int);
size_t get_Inode(const char *pathname);
void *xmalloc(size_t size);
char *xstrdup(const char *s);
void *xrealloc(void *ptr, size_t size);
char *str2md5(const char *str, int length);
#endif

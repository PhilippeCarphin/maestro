/* l2d2_commun.c - Common utility functions and declarations for server code of
 * the Maestro sequencer software package.
 */

#include "l2d2_commun.h"
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/param.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>

/**
 *  Name        : get_time
 *  Author      : R.Lahlou , cmoi 2012
 *  Description : Return the time in different formats
 */
void get_time(char *btime, int mode) {
  struct timeval tv;
  struct tm *ptm;
  char time_string[40];
  long milliseconds;

  /* Obtain the time of day, and convert it to a tm struct.  */
  gettimeofday(&tv, NULL);
  ptm = gmtime(&tv.tv_sec);
  /* Format the date and time, down to a single second.  */
  strftime(time_string, sizeof(time_string), "%Y%m%d%H%M%S", ptm);
  /* Compute milliseconds from microseconds.  */
  milliseconds = tv.tv_usec / 1000;

  switch (mode) {
  case 1:
    sprintf(btime, "%s", time_string);
    break;
  case 2:
    /* Print the formatted time, in seconds, followed by a decimal point and the
     * milliseconds.  */
    sprintf(btime, "%s.%03ld", time_string, milliseconds);
    break;
  case 3:
    /* Print the formatted time, in seconds, followed by a decimal point and the
     * microseconds.  */
    sprintf(btime, "%s.%u", time_string, (unsigned int)tv.tv_usec);
    break;
  case 4:
    /* Print hours, minutes, seconds ie HH:MM:SS  */
    memset(time_string, '\0', sizeof(time_string));
    strftime(time_string, sizeof(time_string), "%H:%M:%S", ptm);
    sprintf(btime, "%s", time_string);
    break;
  }
}

/**
 *  Author      : R.Lahlou , cmoi 2012
 *  Description : get the inode of a path , file , ...
 */
size_t get_Inode(const char *pathname) {
  char *path_status = NULL;
  char resolved[MAXPATHLEN];
  struct stat fileStat;

  if ((path_status = realpath(pathname, resolved)) == NULL) {
    fprintf(stderr, "get_Inode: Probleme avec le path=%s\n", pathname);
    return (-1);
  }

  /* get inode */
  if (stat(resolved, &fileStat) < 0) {
    fprintf(stderr, "get_Inode: Cannot stat on path=%s\n", resolved);
    return (-1);
  }

  return (fileStat.st_ino);
}

/**
 * wrapper to malloc
 */
void *xmalloc(size_t size) {
  void *ptr = malloc(size);
  /* Abort if the allocation failed.  */
  if (ptr == NULL)
    abort();
  else
    return ptr;
}

/**
 * wrapper to strdup
 */
char *xstrdup(const char *s) {
  char *copy = strdup(s);
  /* Abort if the allocation failed.  */
  if (copy == NULL)
    abort();
  else
    return copy;
}

/**
 * wrapper to realloc
 */
void *xrealloc(void *ptr, size_t size) {
  ptr = realloc(ptr, size);
  /* Abort if the allocation failed.  */
  if (ptr == NULL)
    abort();
  else
    return ptr;
}

/**
 * Utility to compute md5 sum of a string
 */
char *str2md5(const char *str, int length) {
  int n;
  MD5_CTX c;
  unsigned char digest[16];
  char *out = (char *)xmalloc(33);
  memset(out, '\0', 33);

  MD5_Init(&c);

  while (length > 0) {
    if (length > 512) {
      MD5_Update(&c, str, 512);
    } else {
      MD5_Update(&c, str, length);
    }
    length -= 512;
    str += 512;
  }

  MD5_Final(digest, &c);

  for (n = 0; n < 16; ++n) {
    snprintf(&(out[n * 2]), 16 * 2, "%02x", (unsigned int)digest[n]);
  }

  return out;
}

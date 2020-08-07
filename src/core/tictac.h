/* Part of the Maestro sequencer software package.
 */

/******************************************************************************
 *FILE: tictac.h
 *
 *AUTHOR: Dominic Racette
 ******************************************************************************/

#include "SeqDatesUtil.h"
#include "SeqUtil.h"
#include <glob.h>
#include <locale.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

/*****************************************************************************
 * tictac:
 * Read or set the datestamp of a given experiment.
 *
 *
 ******************************************************************************/
extern void tictac_setDate(char *_expHome, char *datestamp);

extern char *tictac_getDate(char *_expHome, char *format, char *datestamp);

extern void checkValidDatestamp(char *datestamp);

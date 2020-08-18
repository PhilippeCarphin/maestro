/* SeqDatesUtil.h - Basic date functions used in the Maestro sequencer software
 * package.
 */

#ifndef _SEQ_DATES_UTIL
#define _SEQ_DATES_UTIL

#define PADDED_DATE_LENGTH 14

char *SeqDatesUtil_getPrintableDate(const char *printable_date, int day,
                                    int hour, int minute, int second);
int SeqDatesUtil_dow(int y, int m, int d);
int SeqDatesUtil_isDepHourValid(const char *date, const char *hourToCheck);
int SeqDatesUtil_isDepDOWValid(const char *date, const char *dowToCheck);

long long FromDaysToSeconds(int day, int hour, int minute, int second);
void DateFromJulian(long long jsec, int *yyyymmdd, int *hhmmss);
long long JulianSecond(int year, int month, int day, int hour, int minute,
                       int second);
char *SeqDatesUtil_addTimeDelta(const char *datestamp, const char *timeDelta);
const char *SeqDatesUtil_getIncrementedDatestamp(const char *baseDatestamp,
                                                 const char *hour,
                                                 const char *time_delta);

#endif

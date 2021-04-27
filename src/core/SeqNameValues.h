/* Part of the Maestro sequencer software package.
 */

#ifndef _SEQ_NAMEVALUES
#define _SEQ_NAMEVALUES
typedef struct _SeqNameValues {
  char *name;
  char *value;
  struct _SeqNameValues *nextPtr;
} SeqNameValues;

typedef SeqNameValues *SeqNameValuesPtr;

void SeqNameValues_insertItem(SeqNameValuesPtr *listPtrPtr, const char *name,
                              const char *value);
void SeqNameValues_deleteItem(SeqNameValuesPtr *listPtrPtr, char *name);
void SeqNameValues_printList(SeqNameValuesPtr listPtr);
char *SeqNameValues_getValue(SeqNameValuesPtr ptr, char *attr_name);
void SeqNameValues_setValue(SeqNameValuesPtr *ptr, char *attr_name,
                            char *attr_value);
SeqNameValuesPtr SeqNameValues_clone(SeqNameValuesPtr listPtr);
void SeqNameValues_deleteWholeList(SeqNameValuesPtr *listPtrPtr);
void SeqNameValues_popValue(SeqNameValuesPtr *ptr, char *returnBuffer,
                            int sizeOfBuffer);
/*

int SeqNameValues_isListEmpty(SeqNameValuesPtr listPtr);
*/
#endif

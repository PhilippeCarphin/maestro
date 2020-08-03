/* Part of the Maestro sequencer software package.
*/


#ifndef _XMLUTILS
#define _XMLUTILS

#include <libxml/parser.h>
#include <libxml/xpath.h>
#include <libxml/tree.h>
#include <libxml/xpathInternals.h>

/* Usage: get a result set using XmlUtils_getnodeset() then to iterate over the
 * results in results->nodesetval->nodeTab[i] for i going from 0 to nodeNr-1,
 *
 * for_results(my_name, my_results){
 *    ...
 * }
 * and inside the block, the iterator will be my_name
 * Also note that using this with a NULL results object will not cause problems.
 */
#define for_results(node, results) \
   xmlNodePtr node = NULL;\
   int __i;\
   if(results != NULL)\
   for(  __i = 0, node = results->nodesetval->nodeTab[0];\
        (__i < results->nodesetval->nodeNr) && (node = results->nodesetval->nodeTab[__i]);\
        ++__i\
      )


xmlDocPtr XmlUtils_getdoc (const char *_docname);

xmlXPathObjectPtr
XmlUtils_getnodeset (const xmlChar *_xpathQuery, xmlXPathContextPtr _context);

char * XmlUtils_getProp_ES(xmlNodePtr nodePtr, const char *name);
void XmlUtils_resolve (const char *_docname, xmlXPathContextPtr _context, const char *_deffile, const char* _seq_exp_home);

#endif

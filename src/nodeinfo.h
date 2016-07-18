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


#include "SeqNode.h"
#include <libxml/xpath.h>

#define NI_SHOW_ALL        0x0001 /* (1 << 0) */
#define NI_SHOW_CFGPATH    0x0002 /* (1 << 1) */
#define NI_SHOW_TASKPATH   0x0004 /* (1 << 2) */
#define NI_SHOW_RESOURCE   0x0008 /* (1 << 3) */
#define NI_SHOW_ROOT_ONLY  0x0010 /* (1 << 4) */
#define NI_SHOW_DEP        0x0020 /* (1 << 5) */
#define NI_SHOW_RESPATH    0x0040 /* (1 << 6) */
#define NI_SHOW_TYPE       0x0080 /* (1 << 7) */
#if 0
#define NI_UNUSED          0x0100 /* (1 << 8) */
#define NI_UNUSED          0x0200 /* (1 << 9) */
#define NI_UNUSED          0x0400 /* (1 << 10) */
#define NI_UNUSED          0x0800 /* (1 << 11) */
#define NI_UNUSED          0x1000 /* (1 << 12) */
#define NI_UNUSED          0x2000 /* (1 << 13) */
#define NI_UNUSED          0x4000 /* (1 << 14) */
#define NI_UNUSED          0x8000 /* (1 << 15) */

#define NI_UNUSED          0x00010000 /* (1 << 16) */
#define NI_UNUSED          0x00020000 /* (1 << 17) */
#define NI_UNUSED          0x00040000 /* (1 << 18) */
#define NI_UNUSED          0x00080000 /* (1 << 19) */
#define NI_UNUSED          0x00100000 /* (1 << 20) */
#define NI_UNUSED          0x00200000 /* (1 << 21) */
#define NI_UNUSED          0x00400000 /* (1 << 22) */
#define NI_UNUSED          0x00800000 /* (1 << 23) */

#define NI_UNUSED          0x01000000 /* (1 << 24) */
#define NI_UNUSED          0x02000000 /* (1 << 25) */
#define NI_UNUSED          0x04000000 /* (1 << 26) */
#define NI_UNUSED          0x08000000 /* (1 << 27) */
#define NI_UNUSED          0x10000000 /* (1 << 28) */
#define NI_UNUSED          0x20000000 /* (1 << 29) */
#define NI_UNUSED          0x40000000 /* (1 << 30) */
#define NI_UNUSED          0x80000000 /* (1 << 31) */
#endif

extern SeqNodeDataPtr nodeinfo ( const char* node, unsigned int filters, SeqNameValuesPtr _loops, const char* _exp_home, char* extraArgs, char * datestamp );
extern int doesNodeExist(const char* node, const char* _exp_home, const char * datestamp);
void parseLoopAttributes (xmlXPathObjectPtr _result, const char* _loop_node_path, SeqNodeDataPtr _nodeDataPtr);
void parseForEachTarget(xmlXPathObjectPtr _result, SeqNodeDataPtr _nodeDataPtr);
void parseBatchResources (xmlXPathObjectPtr _result, SeqNodeDataPtr _nodeDataPtr);
void parseAbortActions (xmlXPathObjectPtr _result, SeqNodeDataPtr _nodeDataPtr);
void parseSubmits (xmlXPathObjectPtr _result, SeqNodeDataPtr _nodeDataPtr);
void parseNodeSiblings (xmlXPathObjectPtr _result, SeqNodeDataPtr _nodeDataPtr);
void parseNodeSpecifics (SeqNodeType _nodeType, xmlXPathObjectPtr _result, SeqNodeDataPtr _nodeDataPtr);
void parseDepends (xmlXPathObjectPtr _result, SeqNodeDataPtr _nodeDataPtr, int isIntraDep );
void parseWorkerPath (char * pathToNode, const char * _seq_exp_home, SeqNodeDataPtr _nodeDataPtr );
SeqNodeType getNodeType ( const xmlChar *_node_name );
void getNodeLoopContainersAttr (  SeqNodeDataPtr _nodeDataPtr, const char *_loop_node_path, const char *_seq_exp_home );
void getFlowInfo ( SeqNodeDataPtr _nodeDataPtr, const char *_nodePath,
                   const char *_seq_exp_home, unsigned int filters);
extern const char * NODE_RES_XML_ROOT;
extern const char * NODE_RES_XML_ROOT_NAME;

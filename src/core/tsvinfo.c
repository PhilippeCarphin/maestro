#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "SeqNode.h"
#include "SeqUtil.h"
#include "SeqLoopsUtil.h"
#include "SeqNodeCensus.h"

#include "ResourceVisitor.h"

static const char *indent = "    ";
static const char *doubleIndent = "        ";
/********************************************************************************
 * Creates the batch resourse keylist:
 * Ex: "{resources {{CATCHUP 4} {CPU 2} {QUEUE null} {MPI 8} {MEMORY 500M}
 *{WALLCLOCK 5}}} The The braces are very important for the TCL Thread package
 *to be able to correctly parse the output. NOTE: Notice the space after each
 *"{key value} " pair except the last one. This is part of the keyed list syntax
 *and must be respected. A space is possible after the last pair, but as a
 *matter of consistency, since TCL does funny stuff with extra spaces in certain
 *contexts, they should always be avoided.
 ********************************************************************************/
void resource_keylist(SeqNodeDataPtr ndp, FILE *fp, int human_readable) {

  if (human_readable) {
    fprintf(fp, "    .resources\n");
    fprintf(fp, "%s.catchup   = %d\n", doubleIndent, ndp->catchup);
    fprintf(fp, "%s.cpu       = %s\n", doubleIndent, ndp->cpu);
    fprintf(fp, "%s.queue     = %s\n", doubleIndent, ndp->queue);
    fprintf(fp, "%s.mpi       = %d\n", doubleIndent, ndp->mpi);
    fprintf(fp, "%s.memory    = %s\n", doubleIndent, ndp->memory);
    fprintf(fp, "%s.wallclock = %d\n", doubleIndent, ndp->wallclock);
  } else {

    fprintf(fp, "{resources ");

    fprintf(fp, "{");
    fprintf(fp, "{catchup %d} ", ndp->catchup);
    fprintf(fp, "{cpu %s} ", ndp->cpu);
    fprintf(fp, "{cpu_multiplier %s} ", ndp->cpu_multiplier);
    fprintf(fp, "{queue %s} ", ndp->queue);
    fprintf(fp, "{machine %s} ", ndp->machine);
    fprintf(fp, "{mpi %d} ", ndp->mpi);
    fprintf(fp, "{memory %s} ", ndp->memory);
    fprintf(fp, "{wallclock %d}", ndp->wallclock);
    fprintf(fp, "}");

    fprintf(fp, "}");
  }
}

/********************************************************************************
 * Creates the loop keylist. {loop {{START 1} {END 2} {STEP 3} {SET 4}}} The
 * bracing is very important.
 * NOTE: Notice the space after each "{key value} " pair except the last one.
 * This is part of the keyed list syntax and must be respected.
 * A space is possible after the last pair, but as a matter of consistency,
 * since TCL does funny stuff with extra spaces in certain contexts, they should
 * always be avoided.
 ********************************************************************************/
void loop_keylist(SeqNodeDataPtr ndp, FILE *fp, int human_readable) {
  char *start = SeqLoops_getLoopAttribute(ndp->data, "START"),
       *end = SeqLoops_getLoopAttribute(ndp->data, "END"),
       *step = SeqLoops_getLoopAttribute(ndp->data, "STEP"),
       *set = SeqLoops_getLoopAttribute(ndp->data, "SET"),
       *expression = SeqLoops_getLoopAttribute(ndp->data, "EXPRESSION");

  /*
   * Default values should be set when parsing from the xmlFile.  I have a
   * truly marvellous solution for this, which this margin is too narrow to
   * contain.
   */
  if (expression == NULL) {
    if (start == NULL)
      start = DEFAULT_LOOP_START_STR;
    if (end == NULL)
      end = DEFAULT_LOOP_END_STR;
    if (step == NULL)
      step = DEFAULT_LOOP_STEP_STR;
    if (set == NULL)
      set = DEFAULT_LOOP_SET_STR;
  }

  if (human_readable) {
    fprintf(fp, "%s.loop\n", indent);
    if (expression == NULL) {
      fprintf(fp, "%s.start = %s\n", doubleIndent, start);
      fprintf(fp, "%s.end   = %s\n", doubleIndent, end);
      fprintf(fp, "%s.step  = %s\n", doubleIndent, step);
      fprintf(fp, "%s.set   = %s\n", doubleIndent, set);
    } else {
      fprintf(fp, "%s.expression = %s\n", doubleIndent, expression);
    }
  } else {

    fprintf(fp, "{loop {");

    if (expression == NULL) {
      fprintf(fp, "{start %s} ", start);
      fprintf(fp, "{end %s} ", end);
      fprintf(fp, "{step %s} ", step);
      fprintf(fp, "{set %s}", set);
    } else {
      fprintf(fp, "{expression %s}", expression);
    }

    fprintf(fp, "}}");
  }

  free(start);
  free(end);
  free(step);
  free(set);
  free(expression);
}

/********************************************************************************
 * NOT USED YED: THis is an example of a function that could be used for a
 * general purpose (not necessarily dependencies).  If we want to add another
 * key to the big keyed list, this can be used as a template.
 * NOTE: Notice the space after each "{key value} " pair except the last one.
 * This is part of the keyed list syntax and must be respected.
 * A space is possible after the last pair, but as a matter of consistency,
 * since TCL does funny stuff with extra spaces in certain contexts, they should
 * always be avoided.
 ********************************************************************************/
void dependency_keylist(SeqNodeDataPtr ndp, FILE *fp, int human_readable) {
  if (human_readable) {
    fprintf(fp, "%s.depends\n", indent);
    fprintf(fp, "%s.dpename1 = %s\n", doubleIndent, "depvalue1");
    fprintf(fp, "%s.dpename2 = %s\n", doubleIndent, "depvalue2");
  } else {
    fprintf(fp, "{depends {");
    fprintf(fp, "{%s %s} ", "depname1", "depvalue1");
    fprintf(fp, "{%s %s}", "depname1", "depvalue1");
    fprintf(fp, "}}");
  }
}

void node_to_keylist(SeqNodeDataPtr ndp, FILE *fp, int human_readable) {
  if (human_readable) {
    fprintf(fp, "%s\n", ndp->name);
    resource_keylist(ndp, fp, human_readable);

    /* Template for adding info to the human readable version of the TCL-ready
     * output:
     *
     * dependency_keylist(ndp,fp, human_readable);
     */

    if (ndp->type == Loop) {
      loop_keylist(ndp, fp, human_readable);
    }
  } else {
    fprintf(fp, "%s {", ndp->name);

    resource_keylist(ndp, fp, human_readable);

    /*
     * This is a tmplate for adding new keys to the master keyed list: a space
     * character, and a call to a function following the template of the other
     * functions. The space can't be part of the function because the the
     * first one would have a superfluous space:
     * /module/node { resources {{CPU 1} ... }}
     * and the subfunctions don't know if they are called first or not.
     *
     * fprintf(fp, " ");
     * dependency_keylist(ndp, fp,human_readable);
     */

    if (ndp->type == Loop) {
      fprintf(fp, " ");
      loop_keylist(ndp, fp, human_readable);
    }

    fprintf(fp, "}");
  }
}

enum { TSV = 0, HUMAN = 1 };
/********************************************************************************
 * Creates the tsv compatible and human readable files for storing info on nodes
 * of the experiment.
 ********************************************************************************/
int write_db_file(const char *seq_exp_home, const char *datestamp,
                  FILE *tsv_output_fp, FILE *hr_output_fp) {
  /*
   * Get list of nodes in experiment
   */
  PathArgNodePtr nodeList = getNodeList(seq_exp_home, datestamp);
  PathArgNode_printList(nodeList, TL_FULL_TRACE);

  /*
   * Opitionnaly, one can reverse the list using SeqListNodeReverseList (this
   * is possible because I put the nextPtr as the first element of the struct).
   */

  /*
   * For each node in the list, write an entry in the file
   */
  SeqNodeDataPtr ndp = NULL;
  for_pap_list(itr, nodeList) {

    ndp = SeqNode_createNode(itr->path);

    SeqNode_setDatestamp(ndp, datestamp);
    SeqNode_setSeqExpHome(ndp, seq_exp_home);
    ndp->type = itr->type;
    getNodeResources(ndp, seq_exp_home, itr->path);
    /*
     * Note that fprintf(NULL,...) is OK, but testing it here avoids testing
     * for every subsequent fprintf() that results from calling
     * node_to_keylist().
     */
    if (tsv_output_fp != NULL) {
      node_to_keylist(ndp, tsv_output_fp, TSV);
      /*
       * It seems to work even if I don't put the check (i.e. having a space
       * after the last element in the list), but TCL does do some funny
       * things sometimes with extra spaces, so as a matter of consistency,
       * let's avoid the extra space after the last element
       */
      if (itr->nextPtr != NULL) {
        fprintf(tsv_output_fp, " ");
      }
    }

    if (hr_output_fp != NULL) {
      node_to_keylist(ndp, hr_output_fp, HUMAN);
      fprintf(hr_output_fp, "\n");
    }

    SeqNode_freeNode(ndp);
  }

  PathArgNode_deleteList(&nodeList);
  return 0;
}

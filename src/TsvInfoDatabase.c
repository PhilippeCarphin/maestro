#include <stdio.h>
#include <stdlib.h>

#include "SeqNode.h"
#include "SeqUtil.h"
#include "SeqLoopsUtil.h"
#include "SeqNodeCensus.h"
#include "nodeinfo.h"
void resource_keylist(SeqNodeDataPtr ndp, FILE * fp, int human_readable)
{

   if( human_readable ){
      fprintf(fp, "        .CATCHUP   = %d\n", ndp->catchup);
      fprintf(fp, "        .CPU       = %s\n", ndp->cpu);
      fprintf(fp, "        .QUEUE     = %s\n", ndp->queue);
      fprintf(fp, "        .MPI       = %d\n", ndp->mpi);
      fprintf(fp, "        .MEMORY    = %s\n", ndp->memory);
      fprintf(fp, "        .WALLCLOCK = %d\n", ndp->wallclock);
   } else {
      fprintf(fp,"{resources ");

      fprintf(fp, "{");
      fprintf(fp, "{CATCHUP %d} ",ndp->catchup);
      fprintf(fp, "{CPU %s} ",ndp->cpu);
      fprintf(fp, "{QUEUE %s} ",ndp->queue);
      fprintf(fp, "{MPI %d} ",ndp->mpi);
      fprintf(fp, "{MEMORY %s} ",ndp->memory);
      fprintf(fp, "{WALLCLOCK %d}",ndp->wallclock);
      fprintf(fp, "}");

      fprintf(fp, "}");
   }
}

void loop_keylist(SeqNodeDataPtr ndp, FILE *fp, int human_readable)
{
   char *start = SeqLoops_getLoopAttribute( ndp->data, "START" ),
        *end = SeqLoops_getLoopAttribute( ndp->data, "END" ),
        *step = SeqLoops_getLoopAttribute( ndp->data, "STEP" ),
        *set = SeqLoops_getLoopAttribute( ndp->data, "SET" ),
        *expression = SeqLoops_getLoopAttribute( ndp->data, "EXPRESSION" );

   if(ndp->type != Loop)
   {
      return;
   }

   if( human_readable ){
      if( expression == NULL ){
         fprintf(fp, "        .START = %s\n", start);
         fprintf(fp, "        .END = %s\n", end);
         fprintf(fp, "        .STEP = %s\n", step);
         fprintf(fp, "        .SET = %s\n", set);
      } else {
         fprintf(fp, "        .EXPRESSION = %s\n", expression);
      }
   } else {
      /*
       * {loop {{START 8} {END 18} {STEP 2} {SET 2}}}
       */
      fprintf(fp, " {loop {");
      if( expression == NULL ){
         fprintf(fp, "{START %s} ", start );
         fprintf(fp, "{END %s} ", end );
         fprintf(fp, "{STEP %s} ", step );
         fprintf(fp, "{SET %s}", set );
      } else {
         fprintf(fp, "{EXPRESSION %s}", expression );
      }
      fprintf(fp, "}}");
   }

   free(start);
   free(end);
   free(step);
   free(set);
   free(expression);
}

void dependency_keylist(SeqNodeDataPtr ndp, FILE *fp, int human_readable)
{
   if( human_readable ){
      fprintf(fp, "        .dpename1 = %s\n", "depvalue1");
      fprintf(fp, "        .dpename2 = %s\n", "depvalue2");
   } else {
      fprintf(fp, "{depends ");
      fprintf(fp, "{{depname1 depvalue1} {depname2 depvalue2}}");
      fprintf(fp, "}");
   }
}

void node_to_keylist(SeqNodeDataPtr ndp,FILE *fp, int human_readable)
{
   if( human_readable ){
      fprintf(fp, "%s\n", ndp->name);
      fprintf(fp, "    .resources\n");
      resource_keylist(ndp,fp, human_readable);

      fprintf(fp, "    .depends\n");
      dependency_keylist(ndp,fp, human_readable);

      if( ndp->type == Loop ){
         fprintf(fp, "    .loop\n");
         loop_keylist(ndp,fp,human_readable);
      }
   } else {
      fprintf(fp, "%s {", ndp->name);

      resource_keylist(ndp,fp,human_readable);

      fprintf(fp, " ");
      dependency_keylist(ndp, fp,human_readable);

      fprintf(fp, " ");
      loop_keylist(ndp, fp, human_readable);

      fprintf(fp,"}");

   }
}


int write_db_file(const char *seq_exp_home, FILE *tsv_output_fp, FILE *hr_output_fp)
{
   /*
    * Get list of nodes in experiment
    */
   PathArgNodePtr nodeList = getNodeList(seq_exp_home);
   PathArgNode_printList( nodeList , TL_FULL_TRACE );

   /*
    * For each node in the list, write an entry in the file
    */
   SeqNodeDataPtr ndp = NULL;
   for_pap_list(itr,nodeList){
      ndp = nodeinfo(itr->path, NI_SHOW_ALL, NULL, seq_exp_home,
                                             NULL, NULL,itr->switch_args );

      if( tsv_output_fp != NULL ){
         node_to_keylist(ndp, tsv_output_fp, 0);
         /*
          * It seems to work even if I don't put the check (i.e. having a space
          * after the last element in the list), but TCL does do some funny
          * things sometimes with extra spaces, so as a matter of consistency,
          * let's avoid the extra space after the last element
          */
         if(itr->nextPtr != NULL){
            putchar(' ');
         }
      }

      if( hr_output_fp != NULL ){
         node_to_keylist(ndp, hr_output_fp, 1);
         fprintf(hr_output_fp,"\n");
      }

      SeqNode_freeNode(ndp);
   }


out_free:
   PathArgNode_deleteList(&nodeList);
   return 0;
}

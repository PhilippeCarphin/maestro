/* l2d2_lists.c - List utility functions for server code of the Maestro
 * sequencer software package.
 */

#include "l2d2_lists.h"
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * ----------------------------------------------
 * insert a node in the last position of the list
 *
 * ----------------------------------------------
 */
int insert(dpnode **pointer, char *sxp, char *snode, char *depOnXp,
           char *depOnNode, char *sdtstmp, char *depOnstmp, char *slargs,
           char *depOnLargs, char *key, char *link, char *wfile) {
  dpnode *tpointer;

  if ((*pointer) == NULL) {
    if ((*pointer = (dpnode *)malloc(sizeof(dpnode))) == NULL) {
      fprintf(stderr, "Cannot malloc for dep. list head pointer ... exiting");
      return (1);
    }
    snprintf((*pointer)->sxp, sizeof((*pointer)->sxp), "%s", sxp);
    snprintf((*pointer)->snode, sizeof((*pointer)->snode), "%s", snode);
    snprintf((*pointer)->depOnXp, sizeof((*pointer)->depOnXp), "%s", depOnXp);
    snprintf((*pointer)->depOnNode, sizeof((*pointer)->depOnNode), "%s",
             depOnNode);
    snprintf((*pointer)->sdstmp, sizeof((*pointer)->sdstmp), "%s", sdtstmp);
    snprintf((*pointer)->depOnDstmp, sizeof((*pointer)->depOnDstmp), "%s",
             depOnstmp);
    snprintf((*pointer)->link, sizeof((*pointer)->link), "%s", link);
    snprintf((*pointer)->waitfile, sizeof((*pointer)->waitfile), "%s", wfile);
    snprintf((*pointer)->slargs, sizeof((*pointer)->slargs), "%s", slargs);
    snprintf((*pointer)->depOnLargs, sizeof((*pointer)->depOnLargs), "%s",
             depOnLargs);
    snprintf((*pointer)->key, sizeof((*pointer)->key), "%s", key);
    (*pointer)->next = NULL;
    return (0);
  } else {
    /* Iterate through the list till we encounter the last node.*/
    tpointer = *pointer;
    while (tpointer->next != NULL) {

      tpointer = tpointer->next;
    }
  }

  /* Allocate memory for the new node and put data in it.*/
  if ((tpointer->next = (dpnode *)malloc(sizeof(dpnode))) == NULL) {
    fprintf(stderr, "Cannot malloc in insert () ... exiting");
    /* deallocate list */
    return (1);
  }

  tpointer = tpointer->next;
  snprintf(tpointer->snode, sizeof(tpointer->snode), "%s", snode);
  snprintf(tpointer->sxp, sizeof(tpointer->sxp), "%s", sxp);
  snprintf(tpointer->depOnXp, sizeof(tpointer->depOnXp), "%s", depOnXp);
  snprintf(tpointer->depOnNode, sizeof(tpointer->depOnNode), "%s", depOnNode);
  snprintf(tpointer->link, sizeof(tpointer->link), "%s", link);
  snprintf(tpointer->waitfile, sizeof(tpointer->waitfile), "%s", wfile);
  snprintf(tpointer->slargs, sizeof(tpointer->slargs), "%s", slargs);
  snprintf(tpointer->depOnLargs, sizeof(tpointer->depOnLargs), "%s",
           depOnLargs);
  snprintf(tpointer->sdstmp, sizeof(tpointer->sdstmp), "%s", sdtstmp);
  snprintf(tpointer->depOnDstmp, sizeof(tpointer->depOnDstmp), "%s", depOnstmp);
  snprintf(tpointer->key, sizeof(tpointer->key), "%s", key);
  tpointer->next = NULL;

  return (0);
}

/*
 * ------------------------
 * find a node in the list
 * ------------------------
 */
int find(dpnode *pointer, char *key) {

  /* Iterate through the entire linked list and search for the key. */
  while (pointer != NULL) {
    if (strcmp(pointer->key, key) == 0) /* key is found. */
    {
      return (1);
    }
    pointer = pointer->next; /* Search in the next node. */
  }
  /*Key is not found */
  return (0);
}

/*
 * --------------------------
 * delete a node in the list
 * --------------------------
 */
int delete (dpnode *pointer, char *key) {
  dpnode *temp;

  /* Go to the node for which the node next to it has to be deleted */
  while (pointer != NULL && strcmp(pointer->key, key) != 0) {
    pointer = pointer->next;
  }

  if (pointer->next == NULL) {
    printf("Key:%s is not present in the list\n", key);
    return (1);
  }
  /* Now pointer points to a node and the node next to it has to be removed */
  temp = pointer->next; /*temp points to the node which has to be removed*/
  pointer->next = temp->next;
  free(temp); /*we removed the node which is next to the pointer (which is also
                 temp) */

  return (0);
}

/*
 * -------------
 * free list
 */
void free_list(dpnode *pointer) {
  if (pointer != NULL) {
    free_list(pointer->next);
    free(pointer);
  }
}

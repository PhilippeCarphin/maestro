
import os
import os.path
import time
import json
from datetime import datetime

from constants import WITNESSM_ROOT, MAX_EMAIL_CONTENT_LENGTH_CHARS, LOG_FOLDER, TMP_FOLDER
from simple_logging import logger
from utilities.shell import safe_check_output_with_status

email_template="""The heimdall experiment scanner found {new_message_count} new messages {level_threshold_message}in the maestro experiment '{experiment_path}' for commit '{commit}' that were not present in the scan before.

{messages_text}

Heimdall scan parameters:
    
{parameters}
{json_path_message}
Heimdall logs:
    {LOG_FOLDER}
    
This email was sent by the script '{script_path}' in the maestro project:    
    https://gitlab.science.gc.ca/CMOI/maestro
"""

COMMIT_DISPLAY_LENGTH=8

def get_email_content_for_new_messages(emails,new_messages,results_json,level="",json_path=""):
    """
    See 'send_email_for_new_messages'
    """
        
    parameters=json.dumps(results_json["parameters"],indent=4,sort_keys=True)
    
    level_threshold_message=""
    if level:
        level_threshold_message="(at level '%s' or above)"%level
    
    json_path_message=""
    if json_path:
        json_path_message="\nThe full scan results JSON: '%s'\n"%json_path
    
    chunks=[]
    for message in new_messages:
        text="{code}: {label}\n{description}"
        text=text.format(code=message["code"],
                         label=message["label"],
                         description=message["description"])
        chunks.append(text)
    messages_text="\n\n".join(chunks)
    
    if len(messages_text)>MAX_EMAIL_CONTENT_LENGTH_CHARS:
        messages_text=messages_text[:MAX_EMAIL_CONTENT_LENGTH_CHARS]+" ...\n\n (some message content was truncated because it was longer than %s characters)"%MAX_EMAIL_CONTENT_LENGTH_CHARS
    
    script_path=os.path.realpath(__file__)
    
    commit=results_json["commit"][:COMMIT_DISPLAY_LENGTH]
        
    content=email_template.format(new_message_count=len(new_messages),
                                 level_threshold_message=level_threshold_message,
                                 experiment_path=results_json["parameters"]["path"],
                                 commit=commit,
                                 messages_text=messages_text,
                                 parameters=parameters,
                                 json_path_message=json_path_message,
                                 script_path=script_path,
                                 LOG_FOLDER=LOG_FOLDER)
    
    return content

def send_email_for_new_messages(emails,new_messages,results_json,level="",json_path="",is_dry_run=False):
    """
    Send an email to this list of email addresses describing new heimdall messages.
    'new_messages' are the messages found in the latest scan but not the one before.
    'results_json' is from ExperimentScanner describing the latest scan.
    'level' like 'e' only changes the email text - filtering based on level should be done before calling this function.
    'json_path' is the optional path to the full results JSON to include in the email.
    """
    
    if not emails:
        logger.error("Heimdall is not sending email because no emails given.")
        return
    if not new_messages:
        logger.info("Heimdall is not sending email because no new messages were given.")
        return
    
    content=get_email_content_for_new_messages(emails,new_messages,results_json,level=level,json_path=json_path)
    
    commit=results_json["commit"][:COMMIT_DISPLAY_LENGTH]
    
    """
    For path:
        /folder1/folder2/folder3/folder4
    the exp_label is:
        folder3/folder4
    """    
    exp_label="/".join(results_json["parameters"]["path"].split("/")[-2:])
    subject="heimdall: %s has new codes for commit %s"%(exp_label,commit)
    
    for email in emails:
        if is_dry_run:
            logger.info("Heimdall dry run. not sending email to '%s'"%email)
        else:
            send_email(email,content,subject)
    logger.info("email subject: '%s'"%subject)
    logger.info("email content:\n\n"+content+"\n")

def send_email(recipient,content,subject):
    
    logger.info("Sending email to '%s'"%recipient)
    
    datestamp = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    tmp_content_file=TMP_FOLDER+"/heimdall-tmp-email-content-"+datestamp
    with open(tmp_content_file,"w") as f:
        f.write(content)
    
    mail_bin="/usr/bin/Mail"
    cmd="""cat %s | %s -s "%s" %s"""%(tmp_content_file,mail_bin,subject,recipient)
    output,status=safe_check_output_with_status(cmd)
    if status==0:
        logger.info("Output from "+mail_bin+" =\n"+output)
    else:
        logger.error("Failed to send email. Output from "+mail_bin+"\n"+output)
    
    os.remove(tmp_content_file)

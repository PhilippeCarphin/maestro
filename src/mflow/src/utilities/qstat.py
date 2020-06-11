import os.path

from utilities import safe_check_output_with_status

def get_qstat_data_from_path(path):
    if not os.path.isfile(path):
        return {}
    with open(path,"r") as f:
        return get_qstat_data_from_text(f.read())

def get_qstat_data_from_text(text):
    """
    Returns a dictionary of parsing the content from command:
        jobctl-qstat -Q -f 
        
    dictionary:
        {
            "production":{"acl_users":["smco500", ...],
                          "enabled": "True",
                          ...}
            "prod_persistent": ...
        }
    """
    lines=text.strip().split("\n")
    
    data={}
    queue=""
    for line in lines:
        
        if line.startswith("Queue: "):
            queue=line[7:].strip()
            if queue not in data:
                data[queue]={}
            continue
        
        if not queue:
            continue
        
        if " = " in line:
            split=line.strip().split(" = ")
            if len(split)!=2:
                continue
            key,value=split
            
            if key=="acl_users":
                value=sorted(value.split(","))
            
            data[queue][key]=value   
    
    apply_qstat_routes_to_qstat_data(data)
    
    return data

def get_qstat_data(logger=None):

    cmd="jobctl-qstat -Q -f"
    output,status=safe_check_output_with_status(cmd)
    
    if status!=0:
        if logger:
            msg="qstat command '%s' failed. output:"%cmd
            msg+=output
            if len(msg)>1000:
                msg=msg[:1000]+" ..."
            logger.error(msg)
        return True
    
    try:
        return get_qstat_data_from_text(output)
    except:
        pass
    
    return None

def apply_qstat_routes_to_qstat_data(qstat_data):
    """
    some queues like 'production' don't directly have 'acl_users'
    instead they have something like 'route_destinations = prod'
    this applies 'acl_users' from 'prod' to 'production'
    """
    
    for queue,data in qstat_data.items():
        
        r=data.get("route_destinations")
        if not r:
            continue
        
        dest_data=qstat_data.get(r)
        if not dest_data:
            continue
        
        if "acl_users" in data:
            continue
        
        data["acl_users"]=dest_data.get("acl_users",[])



def get_popup_choices_for_node(experiment,node):
    
    choices=[]
    
    choice={"label":"History (24h)",
            "function":None,
            "attr":0}
    choices.append(choice)
    
    choice={"label":"Node Info",
            "function":None,
            "attr":0}
    choices.append(choice)
    
    choice={"label":"Listing: Success",
            "function":None,
            "attr":0}
    choices.append(choice)
    
    choice={"label":"Listing: Abort",
            "function":None,
            "attr":0}
    choices.append(choice)
    
    return choices


from utilities import print_red, print_orange, print_yellow, print_green, print_blue
from utilities.heimdall.git import scan_git_authors

def run_heimdall_blame(repo_path,
                       count=0):
    
    authors=scan_git_authors(repo_path)
    if count:
        authors=authors[:count]
    
    if not authors:
        print_yellow("This doesn't seem to be a path to a git repository:")
        print(repo_path)
        return
    
    print("Heimdall blame examines the git history of a project to find its lead authors. It awards points based on commit frequency, recency, and continuity.")
    print_green("Lead developers:")
    names=[author["name"] for author in authors]
    longest=sorted(names,key=lambda x:len(x))[-1]
    padding=5
    for author in authors:
        name=author["name"]
        print(name+" "*(padding+len(longest)-len(name)),end="")
        print_yellow(author["emails"][0])
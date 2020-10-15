from utilities.shell import safe_check_output_with_status


class GitUserTracker():
    """
    This class is only meant to be used in this script file.

    Git users in the commit history are considered to be the same if they
    share the same full name or if they share the same email 'local part' (before @).
    Compare is case insensitive.

    This class helps to uniquely identify those users.
    """

    def __init__(self):
        self.name_to_key = {}
        self.email_prefix_to_key = {}
        self.next_key = 1

        "all emails starting with those encountered first"
        self.emails = []

    def add_user(self, name, email):
        name = name.lower()
        email = email.lower()
        prefix = email.split("@")[0]

        if email not in self.emails:
            self.emails.append(email)

        key1 = self.name_to_key.get(name)
        key2 = self.email_prefix_to_key.get(prefix)

        if key1 and key2:
            key = min(key1, key2)
        elif key1:
            key = key1
        elif key2:
            key = key2
        else:
            key = self.next_key
            self.next_key += 1

        self.name_to_key[name] = key
        self.email_prefix_to_key[prefix] = key
        return key

    def get_key(self, name, email):
        """
        All users must be added with add_user before running get_key
        """
        name = name.lower()
        email = email.lower()
        prefix = email.split("@")[0]

        key1 = self.name_to_key.get(name)
        if key1:
            return key1

        key2 = self.email_prefix_to_key.get(prefix)
        if key2:
            return key2

        raise ValueError("GitUserTracker does not recognize this user. Run add_user first. name='%s' email='%s'" % (name, email))


def scan_git_authors(path, include_current_branch=True):
    """
    Return a list of all authors in this repo, with scores [0,1] according to
    their contributions. Users get points for recency, frequency, consistency.
    Sorted with highest scores first.

        [
         {"name":"Stuart Spence",
          "emails":["123@ec.gc.ca","123@canada.ca"],
          "score":0.5},    
        ...
        ]
    """

    cmd = "cd %s ; git rev-parse --abbrev-ref HEAD" % path
    current_branch, status = safe_check_output_with_status(cmd)
    if status != 0:
        return []

    exclude_chunk = ""
    if not include_current_branch:
        exclude_chunk = "--not "+current_branch
    cmd = "cd %s ; " % path+"git log --all "+exclude_chunk+""" --format="%aN %n%ai %n%aE %n" """

    output, status = safe_check_output_with_status(cmd)
    if status != 0:
        return []
    data = parse_git_authors(output)

    "key is gut id, value is author dictionary"
    key_to_author = {}

    "key is gut id, value is list of unique YYYYMM where they contributed"
    key_to_months = {}

    gut = GitUserTracker()

    """
    First pass over all users
    This is necessary because sometimes:
        name=name1 email=email1
        name=name2 email=email2
        name=name1 email=email2
    it's impossible to know this is the same user until we've look at all.
    """
    for item in data:
        gut.add_user(item["name"], item["email"])

    for i, item in enumerate(data):
        key = gut.get_key(item["name"], item["email"])
        if key not in key_to_author:
            author = {"name": item["name"],
                      "emails": set(),
                      "score": 0}
            key_to_author[key] = author
        author = key_to_author[key]
        author["emails"].add(item["email"].lower())

        "value from [0,1] representing how deep we are in the history"
        index_ratio = i/len(data)

        """
        'name' might be a username or a full name.
        A username is general shorter than a full name.
        Try to set name to the full name.
        """
        if len(item["name"]) > len(author["name"]):
            author["name"] = item["name"]

        "always add at least one"
        points = 1

        "extra points for recency"
        if index_ratio < 0.3:
            points += 1
        if index_ratio < 0.1:
            points += 1
        if index_ratio < 0.05:
            points += 1

        "track how many unique months this author contributed"
        if key not in key_to_months:
            key_to_months[key] = set()
        yyyymm = "%s%s" % (item["year"], item["month"])
        key_to_months[key].add(yyyymm)

        author["score"] += points

    "multiply points based on number of unique months author has contributed"
    highest = max([len(m) for m in key_to_months.values()])
    for name, unique_months in key_to_months.items():
        multiplier = 1+(len(unique_months)/highest)
        key_to_author[name]["score"] *= multiplier

    "normalize all scores so they are [0,1]"
    highest = max([a["score"] for a in key_to_author.values()])
    for name, author in key_to_author.items():
        author["score"] = author["score"]/highest

    "sort the set of emails for each unique person"
    for author in key_to_author.values():
        emails = sorted(list(author["emails"]), key=lambda e: gut.emails.index(e))
        author["emails"] = remove_personal_emails(emails)

    results = [a for a in key_to_author.values()]
    results = reversed(sorted(results, key=lambda x: x["score"]))
    return list(results)


def remove_personal_emails(emails):
    """
    Returns this list of emails, except filtering out likely
    personal email addresses.
    """
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "aol.com"]

    def is_personal_email(email):
        for domain in domains:
            if email.endswith("@"+domain):
                return True
        return False
    return [e for e in emails if not is_personal_email(e)]


def parse_git_authors(output):
    """
    Parses text like:

Stuart Spence 
2020-07-10 15:58:27 -0400 
stuart.spence@canada.ca

Stuart Spence 
2020-07-10 15:33:12 -0400 
stuart.spence@canada.ca

    returning a list of dictionaries.
    """
    chunks = output.strip().split("\n\n")
    authors = []
    for chunk in chunks:
        try:
            name, date, email = chunk.strip().split("\n")
            year, month, day = date.split(" ")[0].split("-")
            year = int(year)
            month = int(month)
            day = int(day)

            data = {"name": name.strip(),
                    "date": date.strip(),
                    "email": email.strip(),
                    "year": year,
                    "month": month,
                    "day": day}

            authors.append(data)
        except:
            continue

    return authors

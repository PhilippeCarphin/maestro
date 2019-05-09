from os.path import expanduser

SSM_DOMAIN="%s/tmp/ssm/maestro/unittest"%expanduser("~")
SSM_USE_COMMAND=". ssmuse-sh -d %s ; "%SSM_DOMAIN

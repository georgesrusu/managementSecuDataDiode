import subprocess


process = subprocess.Popen("ls ", stdout=subprocess.PIPE)
output, error = process.communicate()

For the output from yarn list --json > dependencies.json:
Use this analyzer when the yarn list --json command works correctly for your project.

For the output from script.py:
Use this if yarn list --json > dependencies.json doesn’t work for your project.

In that case, just add your yarn.lock file to the folder and run script.py. This script will process and format all of your dependencies into a dependencies.json file. After that, run opackage.2.

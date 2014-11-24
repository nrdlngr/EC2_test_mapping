This script takes an array of AMI IDs (images) and an array of instance types (instance_types). The script creates a security group for the test with port 22 open for SSH access. The script also creates a key pir for the test in EC2 and stores it locally. 
For every combination of images and instance_types, the script checks the expected block device mapping for each AMI, launches the instance, logs into the instance, pings the EC2 metadata server to see what devices were launched with the instance, and then runs lsblk to print out the devices and their mount points.
After this data is collected, the instance is terminated. After all AMI/instance type combinations are complete, the script deletes the temporary key pair in EC2 and locally.

You can control the number of AMIs used and which instance types are tested by editing the "images" and "instance_types" arrays, but note that the AMI IDs must be in the us-west-2 region.

The script has several prerequisites: python, pip, and the paramiko module for python (install with 'sudo pip install paramiko'). You must also have the AWS CLI installed and configured (it pulls your AWS credentials from the AWS CLI config file).

Enjoy!

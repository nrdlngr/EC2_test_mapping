This script takes an array of AMI IDs (images) and an array of instance types (instance_types). 
For every combination of images and instance_types, the script checks the expected block device mapping for each AMI, launches the instance, logs into the instance, pings the EC2 metadata server to see what devices were launched with the instance, and then runs lsblk to print out the devices and their mount points.
After this data is collected, the instance is terminated.

You can control the number of AMIs used and which instance types are tested by editing the "images" and "instance_types" arrays, but note that the AMI IDs must be in the us-west-2 region.

The script has several prerequisites: python, pip, and the paramiko module for python (install with 'sudo pip install paramiko'). You must also have the AWS CLI installed and configured (it pulls your AWS credentials from the AWS CLI config file). Your acccount must have a keypair in the us-west-2 region called "test_mapping", and you must have a security group in that region called "default" which has port 22 open to the world. The test_mapping.pem file must be saved at ~/.ssh/test_mapping.pem on your local system with 0600 permissions.

Enjoy!

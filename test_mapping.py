#!/usr/bin/env python
import os
from pprint import pprint
import boto.ec2
import boto.utils
import time
import paramiko
import os.path

# Make connection to EC2
conn = boto.ec2.connect_to_region(
    "us-west-2",
    #aws_access_key_id=access_key,
    #aws_secret_access_key=secret_key
    )

# Define AMI IDs and instance types (TODO: add supprt for arrays)
image_id = 'ami-3d50120d'
itype = 'm3.xlarge'


reservation = conn.run_instances(
        image_id,
        key_name='test_mapping',
        security_groups=['default'],
        instance_type=itype,
        )

for i in reservation.instances:
    
    # Get block device mapping from AMI
    image = conn.get_all_images(image_ids = image_id)
    
    image_description = image[0].description
    image_name = image[0].name
    if image_description != None:
        print image_description
    else:
        print image_name
    print "AMI ID: " + image_id
    print "Using Instance Type: " + itype
    print
    
    # Print expected AMI mapping to screen
    print "Expected block device mapping for " + image_id + ":"
    for name, mapping in image[0].block_device_mapping.items():
        if mapping.volume_type == None:
            device_type = "Ephemeral"
        else:
            device_type = "EBS(" + mapping.volume_type + ")"
        print name + ": " + device_type
    print
    
    # Boot instance
    print "Booting instance..."
    instance_id = i.id
    print "Instance ID: " + instance_id
    print
    print "... waiting 10 seconds to generate public DNS ..."
    time.sleep(10)
    
    instance = conn.get_only_instances(instance_ids=instance_id)
    public_dns = instance[0].public_dns_name
    print "Public DNS: " + public_dns
    print
    print "... waiting 60 seconds for instance"
    print "... to boot and start SSH daemon..."
    time.sleep(60)
    print
    
    # Log into instance with Paramiko SSHClient
    # Scan AMI description to see which user name to use
    
    if image_description != None and "buntu" in image_description:
        user_name = "ubuntu"
    elif "ubuntu" in image[0].name:
        user_name = "ubuntu"
    else:
        user_name = "ec2-user"

    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = paramiko.RSAKey.from_private_key_file(os.path.expanduser("~/.ssh/test_mapping.pem"))
    client.connect(hostname = public_dns, username = user_name, pkey = key)
    
    print "Hitting metadata server from inside instance:"
    stdin, stdout, stderr = client.exec_command('curl http://169.254.169.254/latest/meta-data/block-device-mapping/')
    print "".join(stdout.readlines())
    print
    
    print "Listing available and mounted volumes from inside instance:"
    stdin, stdout, stderr = client.exec_command('lsblk')  
    print "".join(stdout.readlines())

    print "Shutting down instance ID: " + instance_id
    conn.terminate_instances(instance_id)
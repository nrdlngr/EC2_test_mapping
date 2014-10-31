#!/usr/bin/env python
import os
import sys
import boto.ec2
import boto.utils
import time
import paramiko
import os.path

# Make connection to EC2
conn = boto.ec2.connect_to_region(
    "us-west-2"
    )

# Define AMI IDs and instance types (TODO: add supprt for arrays)
images = [
    # EBS-backed (Quick-start AMIs)
    'ami-b5a7ea85', # Amazon Linux AMI 2014.09.1 (HVM)
    'ami-99bef1a9', # Red Hat Enterprise Linux 7.0 (HVM), SSD Volume Type
    'ami-3b0f420b', # SuSE Linux Enterprise Server 11 SP3 (HVM), SSD Volume Type
    'ami-3d50120d', # Ubuntu Server 14.04 LTS (HVM), SSD Volume Type
    # Instance store-backed (Amazon Linux 2014.09 & Ubuntu 14.04)
    'ami-9b86c6ab', # Amazon Linux AMI 2014.09.0 x86_64 HVM S3
    'ami-0185fd31'  # Ubuntu Server 14.04 LTS (HVM) S3
]

for image_id in images:
    print "============================"
    print "======= " + image_id + " ======="
    print "============================"
    # Run each AMI on the following instance types
    instance_types = [
        'm3.medium',
        'm3.large',
        'm3.xlarge',
        'm3.2xlarge',
        'c3.large',
        'c3.xlarge',
        'c3.2xlarge',
        'c3.4xlarge',
        'c3.8xlarge',
        'g2.2xlarge',
        'r3.large',
        'r3.xlarge',
        'r3.2xlarge',
        'r3.4xlarge',
        'r3.8xlarge',
        'i2.xlarge',
        'i2.2xlarge',
        'i2.4xlarge',
        'i2.8xlarge',
        'hs1.8xlarge'
    ]
    
    
    # Launch instance
    for itype in instance_types:
        reservation = conn.run_instances(
                image_id,
                key_name='test_mapping',
                security_groups=['default'],
                instance_type=itype,
                )

        for instance in reservation.instances:
            print
            print "===== START " + itype + " ====="
            # Create image object for AMI used
            image = conn.get_all_images(image_ids = image_id)
    
            # Create image descrition and name variables parse for AMI OS type
            image_description = image[0].description
            image_name = image[0].name
    
            # Print information for AMI and instance type to identify AMI in console output
            if image_description != None:
                print image_description
            else:
                print image_name
            print "AMI ID: " + image_id
            print "Using Instance Type: " + itype
            print
    
            # Print expected AMI mapping to screen
            print "Block device mapping defined in AMI " + image_id + ":"
            if not image[0].block_device_mapping:
                print "No block devices mapped in this AMI."
            else:
                for name, mapping in image[0].block_device_mapping.items():
                    if mapping.volume_type == None:
                        device_type = "Ephemeral"
                    else:
                        device_type = "EBS(" + mapping.volume_type + ")"
                    print name + ": " + device_type
            print
    
            # Boot instance
            print "Booting instance..."
            instance_id = instance.id
            print "Instance ID: " + instance_id
            print
            print "... waiting for EC2 to generate public DNS ..."
    
            instance = conn.get_only_instances(instance_ids=instance_id)
    
            while "amazonaws.com" not in instance[0].public_dns_name:
                instance = conn.get_only_instances(instance_ids=instance_id)
                time.sleep(1)
            public_dns = instance[0].public_dns_name
            print "Public DNS: " + public_dns
            print
            print "... waiting 60 seconds for instance ..."
            print "... to boot and start SSH daemon    ..."
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
            stdin, stdout, stderr = client.exec_command('DEVICES=$(curl http://169.254.169.254/latest/meta-data/block-device-mapping/ | grep -v root) && for i in $DEVICES; do echo "$(curl http://169.254.169.254/latest/meta-data/block-device-mapping/$i)": $i; done')
            print "".join(stdout.readlines())
            print
    
            print "Listing available and mounted volumes from inside instance:"
            stdin, stdout, stderr = client.exec_command('lsblk')  
            print "".join(stdout.readlines())

            print "Shutting down instance ID: " + instance_id
            conn.terminate_instances(instance_id)
            print "============ END ============"
            print
            print
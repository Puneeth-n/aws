#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:et:sw=4 ts=4

# Copyright (C) 2015 Trademob GmbH <pn@trademob.com>

# python imports
import argparse
import boto3
import json
import logging
import os


# logging
LOG = logging.getLogger(os.path.basename(__file__))

def _log_err(message):
    '''
    generic error function
    '''
    LOG.error(message)
    exit(1)

# logging
def set_log_level(args):
    '''
    Set loglevel
    '''
    logging.basicConfig(level=args.log_level)


def parse_options():
    '''
    argparser
    '''
    # argparse
    parser = argparse.ArgumentParser(description='Fetches subnets by reading the asg config')
    parser.add_argument('path', default='./asg-configs/', type=str,
                        help='filepath for config files')
    parser.add_argument('--access_key', type=str, help='access key', required=True)
    parser.add_argument('--secret', type=str, help='secret', required=True)
    parser.add_argument('--log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level", default='INFO')
    return parser.parse_args()

def get_configs(args):
    '''
    validate if dir exists and files exist
    '''
    if not os.path.exists(args.path):
        _log_err('Invalid path')

    configs = os.listdir(args.path)
    if not configs:
        _log_err('No configs found')

    configs = [config for config in configs if config.endswith('.json')]

    for config in configs:
        yield os.path.join(args.path, config)

def _update_config(args, data):
    '''
    update config
    '''
    session = boto3.session.Session(aws_access_key_id=args.access_key,
                                    aws_secret_access_key=args.secret,
                                    region_name=data['region'])
    client = session.client('autoscaling')
    asg_data = client.describe_auto_scaling_groups(AutoScalingGroupNames=[data['asg']])
    return asg_data['AutoScalingGroups'][0]['VPCZoneIdentifier']

def update_config(args, configs):
    '''
    update config with subnet
    '''
    for config in configs:
        with open(config, 'r+') as f:
            data = json.loads(f.read())
            data['subnets'] = _update_config(args, data).split(',')
            f.seek(0)
            f.write(json.dumps(data, sort_keys=True, indent=2, separators=(',', ': ')))

def main():
    '''
    main
    '''
    args = parse_options()
    set_log_level(args)
    configs = get_configs(args)
    update_config(args, configs)

if __name__ == "__main__":
    main()

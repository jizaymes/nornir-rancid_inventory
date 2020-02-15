#!/usr/bin/env python


# Example script using the nornir rancid_inventory plugin. This will get the config and save it in backups/

from nornir import InitNornir
from nornir.plugins.tasks.networking import napalm_get,napalm_cli
from nornir.plugins.functions.text import print_result

from fputs import fputs

# Where the backup configs go
backup_path = "backups/"

##################

def debug_log(content):
    debug = True

    if( debug ):
        print("DEBUG:", content)

##################

def get_device_config(task):
    r = task.run(napalm_get, getters = [ "get_config" ],
        getters_options = {
            "get_config" : { 
                "retrieve": "running"
                }
            }
        )

##################

def save_config(filename,config):
    debug_log("About to save configuration")
    fputs(filename,config)
    debug_log("Saved config to " + filename)

##################

# Initialize nornir
nr = InitNornir(config_file="config.yaml")

# How many hosts are we dealing with
debug_log("Processing {} host(s)".format(len(nr.inventory.hosts)))

# Get the config 
result = nr.run( task = get_device_config)

# Go through the results for each device
for host, host_data in sorted(result.items()):
    debug_log( "Host: " + host )

    for cmd in host_data[1].result:
        debug_log( "Command: " + cmd )

        if( cmd == "get_config" ):
            save_config( backup_path + host + ".cfg",host_data[1].result[cmd]["running"] )

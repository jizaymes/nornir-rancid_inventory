from nornir.core.deserializer.inventory import Inventory
from rancid_inventory.file_get_contents import file_get_contents
import re
import os.path

class RancidInventory(Inventory):
    def __init__(self, **kwargs):

        # If the rancid path its not passed through, or it doesnt exist, bail out
        if "rancid_path" not in kwargs.keys() or os.path.exists( kwargs["rancid_path"] ) == False:
            raise FileNotFoundError

        # Load the information from the rancid path
        rancid_inventory = self.load_rancid_data( kwargs["rancid_path"] )

        # Set the standard nornir bits
        hosts = rancid_inventory["hosts"]
        groups = {}
        defaults = {}
       
        super().__init__(hosts=hosts, groups=groups, defaults=defaults, **kwargs)

    def load_rancid_data(self, rancid_path):
        # Load the info from rancid_path/var/{group}/router.db
        rancid_config  = self.process_rancid_config( rancid_path )

        # Load the info from cloginrc
        cloginrc = self.process_cloginrc( rancid_path + "/.cloginrc" )

        # Merge them both together
        for host in cloginrc:
            if host in rancid_config["hosts"] and host in cloginrc:
                rancid_config["hosts"][host] = { **rancid_config["hosts"][host],**cloginrc[host]}
        
        return rancid_config

    def process_rancid_config( self, rancid_path ):
        """Reads the rancid.conf config file and parses the groups. From there, it will walk through those groups and find their respective router.db file to import the devices themselves"""

        rancid_conf = rancid_path + "/etc/" + "rancid.conf"
      
        # Read that in to a variable
        config = file_get_contents( rancid_conf )
      
        # Initialize empty RANCID groups variable
        groups = {}

        # Initialize empty return value
        rancid_config = {}

        # Walk the rancid config for interesting things we care about
        for line in config:
            # The list of groups we need to monitor in the rancid.conf
            if "LIST_OF_GROUPS" in line:
               # Split out the key-value pair
               line_bits = line.split("=") 
               # Remove some quotes, and split the value of line_bits (not key) by " " to return a list of groups
               groups_list = re.sub('"',"",line_bits[1]).split(" ")

                #convert to a dictionary
               for group in groups_list:
                   groups[group] = {}

        # Do we have any groups?
        if len(groups) == 0:
            raise "Abort - Couldnt get the LIST_OF_GROUPS parsed from rancid.conf"

        rancid_config["hosts"] = {}

        # Now that we have groups, now we have to walk through their router.db files to get the devices
        for group in groups:
            # Set a variable with the full file path
            group_file_path = rancid_path + "/var/" + group + "/router.db"

            # Keep on moving if its false
            if os.path.exists( group_file_path ) == False:
                pass
            
            # Contents of router.db file
            routersdb = file_get_contents( group_file_path )
            for router_line in routersdb:
                router_info = router_line.split(";")
                host = router_info[0]
                platform = router_info[1]
                status = router_info[2]

                rancid_config["hosts"][host] = {}
                rancid_config["hosts"][host]["hostname"] = host
                rancid_config["hosts"][host]["platform"] = self.process_platform_map( platform )

        return rancid_config

    def process_platform_map( self, platform ):
        if platform == "juniper":
            return "junos"
        if platform == "cisco":
            return "ios"

    def process_cloginrc( self, cloginrc_filename ):
        data = {}

        clogin_data = file_get_contents( cloginrc_filename )

        for line in clogin_data:
            newline = re.sub(" +"," ",line.replace( "\t", " " ))
            if "add user" in newline:
                line_bits = newline.split(" ")

                line_bits.reverse()

                add = line_bits.pop()
                user = line_bits.pop()
                host = line_bits.pop()
                username = line_bits.pop()

                if host not in data:
                    data[host] = {}
                    data[host]["hostname"] = host

                data[host]["username"] = username
            elif "add password" in newline:
                line_bits = newline.split(" ")

                line_bits.reverse()

                add = line_bits.pop()
                user = line_bits.pop()
                host = line_bits.pop()
                password = line_bits.pop()

                if host not in data:
                    data[host] = {}
                    data[host]["hostname"] = host
                
                data[host]["password"] = password

        return data

# Function to create index configurations or simply list index names based on the mode provided
def create_indexes(indexes, mode):
    """
    Generates and prints index configuration or index names based on the specified mode.
    
    Parameters:
    indexes (list): A list of index names to be created.
    mode (str): Specifies the mode of output. "config" prints full configuration details, 
                "list" prints just the index formatted names.
    """
    
    # Set customer prefix for the index names -> CHANGE ME
    customer = "apple"
    
    # Print the header only when in "config" mode
    if mode == "config":
        print(f"### {customer.upper()} INDEXES ###\n")
    
    # Iterate through each index to create a configuration or list the index formatted name
    for index in indexes:
        # Construct the index formatted name by appending the customer prefix
        index_name = f"{customer}_{index}"
        
        # Configuration details for the index
        index_config = f"""[{index_name}]
homePath = $SPLUNK_DB/{index_name}/db
coldPath = /cold/{index_name}/colddb
thawedPath = $SPLUNK_DB/{index_name}/thaweddb
homePath.maxDataSizeMB = 256000
maxTotalDataSizeMB = 512000
frozenTimePeriodInSecs = 7776000
repFactor = auto\n"""
        
        # Print configuration or just the index formatted name based on mode
        if mode == "config":
            print(index_config)
        else:
            print(index_name)

# Main function to pass the list of indexes and specify the mode (config or list)
def main():
    """
    Main function to define index list and call the create_indexes function.
    """
    
    # List of indexes to create -> CHANGE ME
    indexes = ["syslog", "winevent", "ad", "crowdstrike"]
    
    # Call create_indexes with "list" mode to print index names -> CHANGE ME
    create_indexes(indexes, "list")

# Entry point of the script
if __name__ == "__main__":
    main()

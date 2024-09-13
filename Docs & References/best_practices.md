__
**Source**: Splunk
**Tags**: #Data-Analytics #Best-Practices #Administration #Architecting 
-
**Status**: #In-Progress #Never-Ends
**Date Created**: 2024-09-13 14:29
**Date Updated**: 2024-09-13 14:29
__
# System Administration

## Configuration Best Practices
### Avoid storing configurations in `SPLUNK_HOME/etc/system/local`
- Local context settings will always take precedence
- Attempting to override index-time settings in an app will fail
- Managing these settings with a deployment server is impossible


### Create an app to manage system settings
- Allows you to manage settings with a deployment server
- Manage system configurations in an app (e.g. DC_app) under `SPLUNK_HOME/etc/apps/<appname>/local`
- Refer to the Splunk Enterprise [[Data Administration 9.pdf]] course
	- Available in the current document, search for: Manage Deployment Client Settings Centrally


## Time Synchronization
Ensure a standardized time configuration on Splunk servers
- Splunk searches depend on accurate timestamps on events
- Clock skew between hosts can affect search results
- Popular protocol is NTP (Network Time Protocol)


## Startup Account
### Do not run Splunk as *super-user*

| NIX     | Avoid the *root* account                                                                                                                                                |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Windows | Avoid the **administrator** account<br>Use a domain account if Splunk must connect to other servers<br>Alternatively, use a local machine account that can run services |
### Splunk user account must
- Read files and directories configured for monitoring by Splunk
	- **NIX**: **/var/log** is not typically open to non-root accounts
- Write to the Splunk Enterprise directory (**SPLUNK_HOME**)  
- Execute any scripts required (alerts or scripted input)  
- Bind to the network ports Splunk is listening on
	- **NIX**: non-root accounts cannot access reserved ports (< 1024)


## Estimating Index Growth Rate
- Get a good growth estimate  
- Input your data in a test/dev environment over a sample period
	- If possible, index more than one bucket of events
- Examine the size of the index's **db** directory compared to the input
	- **MC**: Indexing > Indexes and Volumes > Index Detail: Instance


## Configuring High-volume Indexes
- Change index default of 3 hot buckets to 10 hot buckets using the **maxHotBuckets** key
- Examine and copy settings of **main** index stanza and adjust for use case


## User Authentication
- Keep a failsafe account in the **passwd** file with a very strong password

### Passwords
> https://docs.splunk.com/Documentation/Splunk/latest/Security/Passwordbestpracticesforadministrators


## Distributed Search Best Practices
### Dedicate a host for each role
Use a dedicated host for each Splunk role (e.g., search head, indexer, forwarder)
- Combine server roles with caveats
- Discussed in the Architecting Splunk Deployments course


### Disable Splunk Web on instances that don’t require it
```bash
splunk disable webserver
```


### Use Deployment Server
Discussed in the Splunk Enterprise Data Administration course


### Forward any data being indexed by the search heads to indexers
- Centralizes data on indexers, which simplifies management
- Allows diagnosis from other search heads if one goes down
- Allows other search heads to access all summary indexes
#### Steps
1. Settings > Forwarding and receiving > Forwarding defaults
	- Store local copy of forwarded events: No
	- Save
2. outputs.conf
```conf
[indexAndForward]
index = false

[tcpout]
defaultGroup = default-autolb-group
forwardedindex.filter.disable = true
indexAndForward = false

[tcpout:default-autolb-group]
server=idx1:9997,idx2:9997
```

# Data Administration
## Data Collection Method
Monitor configured inputs and forward the data to the indexers.


## Optimizing the Heavy Forwarder
Based on your use case...
Disable indexing data on the HF:
`outputs.conf`
```conf
[indexAndForward]
index = false
```
Disable Splunk Web on the HF:
`web.conf`
```conf
[settings]
startwebserver = 0
```


## Configuring a Deployment App
- Create small and discrete deployment apps
- Take advantage of .conf file layering  
- Use a consistent naming convention


## Manage Deployment Client Settings Centrally
Use an app to manage deployment client settings
- Create a deployment client settings app (example: `DC_app`)
- Move `deploymentclient.conf` settings from `etc/system/local/` to `etc/apps/DC_app/local/`
- Deploy `DC_app` to clients using a Server Class
![[dc_app.png]]


## Special Handling
### UDP
- Splunk merges UDP data until it finds a timestamp by default
- Default behavior can be overridden during the parsing phase
### Syslog
- Send data to a syslog collector that writes into a directory structure (for example: `/var/log/syslog/servername/filename.txt`)
- Monitor the directory and use `host_segment`
- docs.splunk.com/Documentation/Splunk/latest/Data/HowSplunkEnterprisehandlessyslogdata
### SNMP Traps
- Write the traps to a file and use the monitor input  
- docs.splunk.com/Documentation/Splunk/latest/Data/SendSNMPeventstoSplunk


## Local Windows Inputs
Manually
- Create entries in custom app or use **Splunk Add-on for MS Windows**
	- splunkbase.splunk.com/app/742/
- Easy to manage using a DS
- For details refer to:
	- `inputs.conf.spec`
	- `inputs.conf.example`
```conf
[admon://name]
[perfmon://name]
[WinEventLog://name]
[WinHostMon://name]
[WinNetMon://name]
[WinPrintMon://name]
[WinRegMon://name]
```


# Cluster Administration
## Summary Indexing in Search Head Clusters
- SH & SHC
	- Forward all events (including summary events and internal Splunk log events) to the indexers.

## Managing Indexers and Clusters of Indexers
Forward manager node data to the indexer layer
- https://docs.splunk.com/Documentation/Splunk/latest/Indexer/Forwardmanagerdata

## Cluster Manager Redundancy
New feature & recommended best practice of Splunk Enterprise 9.0+

- Addresses problems associated with manual node failover from previous versions
- Supports automatic or manual failover
	- Configured in `server.conf`
- Requires configuration in three areas:
	- Multiple cluster managers
	- Peer nodes, search heads, and forwarders when indexer discovery is enabled   
- Third party load balancing or DNS mapping

***Note**: Implementation of an active/standby cluster manager topology requires navigating complex and difficult procedures customized to achieve your goals. Involve Splunk Professional Services to ensure that your deployment is successful.*

# Troubleshooting
## Index Time
- To maximize the performance and resource utilization, provide specific settings
    - The defaults are designed for flexibility, but they can be expensive
    - Remember the settings can be specified in an app

- For inputs, explicitly specify host, source type, source and index
    - Separate high-velocity sources from low-velocity sources
    - Combine things frequently searched together in the same index    

- For parsing-phase pipelines, always specify:
	- Event boundary
	- Timestamp

- Distribute data uniformly to all indexers
### The "Great 8" Per Sourcetype (`props.conf`)
#### HF/Indexer
1. MAX_TIMESTAMP_LOOKAHEAD
2. TIME_PREFIX
3. TIME_FORMAT
4. LINE_BREAKER
	- Use to delimit events.
5. SHOULD_LINEMERGE = false
6. TRUNCATE
#### UF
7. EVENT_BREAKER
	- Use for load balancing UF.
8. EVENT_BREAKER_ENABLE = true


### Input Problems
Roll the log files before enabling debugging
- Do not leave debug enabled!

## Scheduled Search
- Verify when events occurred and actually indexed
```spl
<base_search>
| head
| convert ctime(_time) as evtTime ctime(_indextime) as idxTime
| eval lag=_indextime-_time
| table evtTime idxTime lag
```

- Offset search range to compensate for the lag in indexing
  Example for a less than a minute lag: 
	- Before: `<base_search> earliest=-1m@m latest=now`
	- After: `<base_search> earliest=-2m@m latest=-1m@m`
		- Can accommodate indexing lag and searches over a same span

- Classify and reserve resources for critical services with Workload Management

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

# Architecting Splunk Deployments
## Forwarder and Deployment
### Forwarding Summary Indexes
- Summary indexes are created on the search head by default
- If you use summary indexes, forward your summary indexes to the indexing layer
	- Configure outputs.conf on the search head to forward to indexers
	- This allows all members to access them
		- Otherwise, they're only available on the search head that generates them
	- This is required for search head clustering
- Configure the search head as a forwarder
> [Forward Search Head Data](http://docs.splunk.com/Documentation/Splunk/latest/DistSearch/Forwardsearchheaddata)

### Forwarding Tier Design
- Use the UF unless there are specific requirements that necessitate an HF
	- Sending cooked data through a HF to indexers impacts overall throughput performance
- Use a syslog server for syslog data
- Avoid intermediate forwarders when possible:
	- Bottlenecks can occur
	- Reduces the distribution of events across indexers
- If intermediate forwarders are required, ensure there are enough of them
- Forwarders automatically load balance over available indexers
	- AutoLB is enabled by default
	- May need to increase UF thruput setting in limits.conf(default: 256KBps) for high velocity sources
		- This value should be based on the ratio of forwarders to indexers
```conf
[thruput]
maxKBps = 0
#zero is unlimited
#default was 256
```

### Deployment Management

| Type of Instance                                                | Manage Configurations with...                            |
| --------------------------------------------------------------- | -------------------------------------------------------- |
| Forwarder<br>Search Head (stand-alone)<br>Indexer (stand-alone) | Deployment Server or other configuration management tool |
| Search Head Cluster Member                                      | Deployer only                                            |
| Peer Node in Indexer Cluster                                    | Cluster Manager only                                     |

#### Deployment Apps
- Design your deployment app
	- An app is a set of deployment content (a configuration bundle)
	- An app is deployed as a unit and should be small
	- Take advantage of Splunk’s configuration layering
	- Use a naming convention for the apps
	- Create classes of apps, for example
		- Input apps
		- Index apps
		- Web control apps
- Carefully design apps regardless of your configuration management tool (DS, Manager Node, Puppet, etc.)

## Staging & Testing Environments
- Part of your Splunk deployment should include a separate "sandbox" or testing / staging environment
	- Same version of Splunk in production is preferred
- Sizing the testing environment depends on types of tests

| Test...        | Deployment Type                                                                      |
| -------------- | ------------------------------------------------------------------------------------ |
| Inputs         | A standalone indexer with minimal performance and capacity                           |
| Configurations | A minimum set of components (one Search Head, one Indexer, one Deployment Server, …) |
| Performance    | An accurate duplication of the production environment                                |


## Splunk Validated Architectures (SVAs)
- Proven reference architectures
- Designed by Splunk Architects based on best practices
- Repeatable deployments
- Offer topology options for your environment and requirements

## Indexer Clustering Requirements
For single-site mode:
- Minimum number of peer nodes equal to replication factor (RF)
	- Example: RF = 3 requires a minimum of three peer nodes
- **Best Practice**: Minimum of (RF + 1) peer nodes

## Improving Search Performance
- Make sure disk I/O is as good as you can get
	- Increase CPU hardware only if needed
- Most search performance issues can be addressed by adding additional search peers (indexers)
- Look at resource consumption on both the indexer tier and search head tier to diagnose slow searches
- Rebalance buckets (only available in indexer clustering)
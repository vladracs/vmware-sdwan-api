Copying and Restoring Edge configs while fully possible using API is not a straightforward process. 
There are some dependencies that might need special treatment.

As example: the complications come from device settings references to hubs, clusters, net flow collectors, dns servers, etc. it is doable and may work with a naive implementation most of the time.
It will have issues if one or the network services gets replaced, deleted, etc. similar thing applies to biz pol & firewall rules but references would be object groups and hub associations there. 
This is where the refs object comes into play in the API.

therefore use these scripts carefully!

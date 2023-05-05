# Advanced Configuration

## Remote HPC Configuration
`queue.yaml` file for remote access: 
```
queue_type: REMOTE
queue_primary: remote
ssh_host: hpc-cluster.university.edu
ssh_username: hpcuser
known_hosts: ~/.ssh/known_hosts
ssh_key: ~/.ssh/id_rsa
ssh_remote_config_dir: /u/share/pysqa/resources/queues/
ssh_remote_path: /u/hpcuser/remote/
ssh_local_path: /home/localuser/projects/
ssh_continous_connection: True
ssh_delete_file_on_remote: False
queues:
  remote: {cores_max: 100, cores_min: 10, run_time_max: 259200}
```
In addition to `queue_type`, `queue_primary` and `queues` this also has the following required keywords:

* `ssh_host` the remote HPC login node to connect to 
* `ssh_username` the username on the HPC login node
* `known_hosts` the local file of known hosts which needs to contain the `ssh_host` defined above.
* `ssh_key` the local key for the SSH connection 
* `ssh_remote_config_dir` the `pysqa` configuration directory on the remote HPC cluster
* `ssh_remote_path` the remote directory on the HPC cluster to transfer calculations to 
* `ssh_local_path` the local directory to transfer calculations from 

And optional keywords: 

* `ssh_delete_file_on_remote` specify whether files on the remote HPC should be deleted after they are transferred back to the local system - defaults to `True`
* `ssh_port` the port used for the SSH connection on the remote HPC cluster - defaults to `22`

A definition of the `queues` in the local system is required to enable the parameter checks locally. Still it is sufficient to only store the individual submission script templates only on the remote HPC.  

## Access to Multiple HPCs 
To support multiple remote HPC clusters additional functionality was added to `pysqa`. 

Namely, a `clusters.yaml` file can be defined in the configuration directory, which defines multiple `queue.yaml` files for different clusters: 
```
cluster_primary: local_slurm
cluster: {
    local_slurm: local_slurm_queues.yaml,
    remote_slurm: remote_queues.yaml
}
```
These `queue.yaml` files can again include all the functionality defined previously, including the configuration for remote connection using SSH. 

Furthermore, the `QueueAdapter` class was extended with the following two functions: 
```
qa.list_clusters()
```
To list the available clusters in the configuration and: 
```
qa.switch_cluster(cluster_name)
```
To switch from one cluster to another, with the `cluster_name` providing the name of the cluster like `local_slurm` and `remote_slurm` in the configuration above. 
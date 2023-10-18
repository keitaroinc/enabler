# Enabler


Enabler is a CLI application built for making life easier when working on microservice-based applications. Through this package we can create, edit and execute custom cmd commands to configure microservices.
The repository for the project can be found on this link: https://github.com/keitaroinc/devops-enabler. 
Enabler needs at least python 3.7, so please check that you have python 3.7 or later for running the commands defined in this application.



**Steps for implementation**

Enabler can be used for any project with microservice architecture. It can be integrated by adding the devops-enabler project directory to the project and running this command:


```
    python3.x -m pip install --editable .
```


Where x is the current version of python running on your machine. Then it will be possible to access all of the commands defined in this package by running them as described below in Terminal. 



**Enabler Commands**

The commands used are organized in 5 groups:
- apps
- platform
- preflight
- kind
- setup
- version

**Apps group of commands**

Application specific commands such as creation of kubernetes objects such as namespaces, configmaps etc. The name of the context is taken from the option --kube-context, which defaults to 'keitaro'. The commands in this group can be accessed using the prefix enabler apps + name_of_command.  The commands in this group are the following:
- namespace: create a namespace using kubectl commands in the background. There is one argument for this command and it is name of namespace. The command can be run as: 


```
    enabler apps namespace <name_of_namespace>
```


**Platform group of commands**

The commands in this group can be accessed using the prefix enabler platform + name_of_command. This group contains commands to help with handling the codebase and repo. The commands in this group are the following:
- init:  Init the platform by doing submodule init and checkout all submodules on master
- info:      Get info on platform and platform components
- keys: Generate encryption keys used by the application services
- release: Release platform by tagging platform repo and   tagging all individual components (git submodules) using their respective SHA that the submodules point at
- version: Check versions of microservices in git submodules you can provide a comma separated list of submodules or you can use 'all' for all submodules


**Preflight command**

This command checks to ensure all dependencies such as java jdk 11, docker, helm, kind, skaffold, kubectl, istioctl etc. are present and with the necessary version. The command can be run with this line run while in the folder of the project:


```
    enabler preflight
```  

**Kind group of commands**

This command group is used to Manage kind clusters. The name of the cluster is taken from the option --kube-context, which defaults to 'keitaro'. They can be accessed by using enabler kind + name_of_command. 
- create: used to create a kind cluster, with configfile as an argument
- delete : command that checks if cluster exists and then deletes it.
- status: to check the status of cluster
- start: with this command we find the containers with a label io.x-k8s.kind.cluster, check status and ports, start them and then configure kubectl context
- stop: with this command we find the containers with a label io.x-k8s.kind.cluster, check status and stop them 


**Setup group of commands**

These commands are used to setup the infrastructure to run kubernetes. With this group we can download the necessary packages and install them. To run commands from this group we use enabler setup + name_of_command.
- init: download binaries for all dependencies such as kubectl, helm, istioctl, kind and skaffold 
- metallb: install and setup metallb on k8s
- istio: install and setup istio on k8s
  If the command istio is executed with the argument monitoring-tools, i.e:
  '''
    enabler  setup istio monitoring-tools --kube-context keitaro
  '''
  Then tools needed to monitor the cluster, such as grafana kiali and prometheus, will be installed as well. These applications can provide insights into the performance and behavior of applications and infrastructure on a cluster environment. In order to be able to access the results from grafana through the URL grafana.local, a new record in /etc/hosts should be added. Open /etc/hosts with your  preferred text editor and add the following line:
  
  '''
    172.18.255.246 grafana.local
  '''

**Enabler version command**

When excuting this command we can get the working version of Enabler used for the project. This command can be executed with:


```
    enabler version
```  
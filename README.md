# Enabler

[![flake8 Lint](https://github.com/keitaroinc/enabler/actions/workflows/lint.yml/badge.svg)](https://github.com/keitaroinc/enabler/actions/workflows/lint.yml)

Enabler is a CLI application built for making life easier when working on microservice-based applications. Through this package we can create, edit and execute custom commands to configure microservices.

![Enabler logo image](https://raw.githubusercontent.com/keitaroinc/enabler/main/enabler-logo-bw.png)

The repository for the project can be found on: https://github.com/keitaroinc/enabler.

Enabler requires **Python 3.7 or above**.

## Installation

Enabler can be used for any project with microservice architecture. Clone it locally to a desired location, navigate to the cloned directory and create a binary for the `enabler` command with `pip`.

>Please note that the following command will replace any other existing `enabler` binary and become the default one.

```bash
pip install --editable .
```

Then it will be possible to access all of the commands defined in this package by running them as described below.

To check if the installation was successful, please run `which enabler`. That will output the current location of the enabler binary and it should be something like:

```bash
<home>/<username>/.local/bin/enabler
```

Running `enabler` should execute the command and provide the initial help reference for how to use it.

```bash
Usage: enabler [OPTIONS] COMMAND [ARGS]...

  Enabler CLI for ease of setup of microservice based apps

Options:
  --kube-context TEXT  The kubernetes context to use
  -v, --verbosity LVL  Either CRITICAL, ERROR, WARNING, INFO or DEBUG
  --help               Show this message and exit.

Commands:
  apps       App commands
  kind       Manage kind clusters
  platform   Platform commands
  preflight  Preflight checks
  setup      Setup infrastructure services
  version    Get current version of Enabler
```

Add the following line to your `~/.bashrc file`:

```bash
source /path/to/enabler_completion.sh
```

Then in terminal, run:

```bash
source ~/.bashrc
```


## Commands

The commands used are organized in several groups:

- `apps`
- `platform`
- `preflight`
- `kind`
- `setup`
- `version`

### apps

Application specific commands such as creation of kubernetes objects such as namespaces, configmaps etc. The name of the context is taken from the option --kube-context, which defaults to 'keitaro'. The commands in this group can be accessed using the prefix enabler apps + name_of_command. There is only one command in this group and it is:

- **namespace**: create a namespace using kubectl commands in the background.\
  There is one argument for this command and it is name of namespace. This command also has a --kube-context option, which should be defined as the name of the kind cluster and can be executed with this command in Terminal:

```bash
enabler apps namespace <name_of_namespace> --kube-context keitaro
```

### platform

The commands in this group can be accessed using the prefix enabler platform + name_of_command. This group contains commands to help with handling the codebase and repo. The commands in this group are the following:

- **init**: Init the platform by doing submodule init and checkout all submodules on master
- **info**: Get info on platform and platform components\
  This command has a --kube-context option, which should be defined as the name of the kind cluster. The command can be run as:

  ```bash
  enabler platform info --kube-context keitaro
  ```

- **keys**: Generate encryption keys used by the application services
- **version**: Check versions of microservices in git submodules you can provide a comma separated list of submodules or you can use 'all' for all submodules
- **release**: Release platform by tagging platform repo and tagging all individual components (git submodules) using their respective SHA that the submodules point at


  ```bash
  enabler platform release <version> <submodule_name>
  ```


### preflight

This command checks to ensure all dependencies such as java jdk 11, docker, helm, kind, skaffold, kubectl, istioctl etc. are present and with the necessary version.

```bash
enabler preflight
```

### kind

This command group is used to Manage kind clusters. The name of the cluster is taken from the option --kube-context, which defaults to 'keitaro'. They can be accessed by using enabler kind + name_of_command.

- **create**: used to create a kind cluster, with config file as an argument. The default name of the config file is kind-cluster.yaml.
- **delete**: command that checks if cluster exists and then deletes it.
- **status**: to check the status of cluster
- **start**: with this command we find the containers with a label io.x-k8s.kind.cluster, check status and ports, start them and then configure kubectl context
- **stop**: with this command we find the containers with a label io.x-k8s.kind.cluster, check status and stop them

All commands in this group have a --kube-context option, which should be defined as the name of the kind cluster and can be executed with this command in Terminal:

```bash
enabler kind name_of_command --kube-context keitaro
```

### setup

These commands are used to setup the infrastructure to run kubernetes. With this group we can download the necessary packages and install them. To run commands from this group we use enabler setup + name_of_command.

- **init**: download binaries for all dependencies such as kubectl, helm, istioctl, kind and skaffold in /enabler/bin folder
- **metallb**: install and setup metallb on k8s
  This command has a --kube-context option, which should be defined as the name of the kind cluster and can be executed with this command in Terminal:

  ```bash
  enabler setup metallb --kube-context keitaro
  ```

  There are 2 avaliable arguments for this command, which can be assigned as --version (working version of metallb) and --ip-addresspool (selected IP address range designated for metallb). You should keep in mind that the IP address range should always be from the kind network. If not assigned the default value for version is 4.6.0 and the value for the IP address pool is the range of the last 10 addresses from the kind network.

- **istio**: install and setup istio on k8s
  If the command istio is executed with the argument monitoring-tools, i.e:

  ```bash
  enabler setup istio monitoring-tools --kube-context keitaro
  ```

  Then tools needed to monitor the cluster, such as grafana kiali and prometheus, will be installed as well. These applications can provide insights into the performance and behavior of applications and infrastructure on a cluster environment. In order to be able to access the results from grafana through the URL grafana.local, a new record in /etc/hosts should be added. Open /etc/hosts with your preferred text editor and add the following line:

  ```bash
  172.18.255.246 grafana.local
  ```

### version

When executing this command we can get the working version of Enabler used for the project. This command can be executed with:

```bash
enabler version
```

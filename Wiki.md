# KubeMom

MOM ([Memory Overcommitment Manager](https://www.ovirt.org/develop/projects/mom.html)) is a component in a virtual environment that applies pre-defined policies that adjust KSM, ballooning, [and optionally other resource management features](https://www.ibm.com/developerworks/library/l-overcommit-kvm-resources/) to facilitate memory-overcommitment in the nodes that Virtual Machines run on.

This project is about implementing MOM as an optional controller in a Kubernetes cluster that would do the same for enabling memory-overcommitment in [KubeVirt](https://kubevirt.io/) nodes, i.e., nodes that run KVM virtual machines within Kubernetes Pods.

## Architecture
The high-level design of MOM is depicted in the following diagram:
![Architecture](wiki_resources/figure2.gif)

MOM is comprised of three main layers:
- Host data collection: this layer retrieves information about the node that the virtual machines run on.
- Guest data collection: this layer retrieves information about the virtual machines that run on the node.
- System management: this layer applies predefined policies that convert data that is retrieved by the two aforementioned layers into actions that are sent to the appropriate resource management entities.

## Challenges
The requirements for KubeMom can be split to two groups: (1) Things that come from its implementation as an extension to KubeVirt; and (2) Improvements to the existing MOM project that was implemented for [oVirt](https://ovirt.org/).

Among the first group are the following requirements:
- Containerizing the MOM application.
- Retrieving node-level data via [Node-Exporter](https://github.com/prometheus/node_exporter/blob/master/README.md).
- Retrieving guest(VM)-level data via KubeVirt (See this [trello card](https://trello.com/c/izETePlZ/79-8epic-detailed-monitoring-expose-vm-internal-metrics-initiative-perfscale-baseline)).
- Sending actions to the node-level KSM.
- Sending guest-level actions.

Among the second group are the following requirements:
- Replacing the lisp-like scripting language for policy definition with [a more declarative language](https://ovirt.org/develop/release-management/features/sla/mom-declarative-language.html).
- Enabling policy adjustments according to VM-lifecycle events (e.g., configuring the policy differently when VM boots compared to when the guest operating system is already up).

## Approach
There appears to be no good reason for changing the architecture nor for changing the programming language (python) of the existing implementation of MOM in oVirt. Furthermore, the suggested improvements to the existing MOM project can be a second-phase step. On the other hand, the ability to consume the required data and post the needed actions in a KubeVirt environment seem to be good things to start with.

Therefore, we can leverage the existing MOM project and start with extending/replacing the collectors (that retrieve data) and controllers (that post actions). This will enable us to inspect the effect of a version of MOM that is similar to the existing one in a KubeVirt environment.

## Roadmap
- Containerize MOM
- Introduce a collector that retrieves host-level data from Node-Exporter
  - This may require changes in Node-Exporter
  - This may require additional information (e.g., pid for a VMI to be able to correlate retrieved data with virtual machines, guest-level memory data)
- Introduce a collector that retrieves guest-level data from KubeVirt
- Introduce a controller that updates host-level KSM configuration
- Introduce other controllers that used to interact with VDSM
  - For: ballooning, IO-tune, CPU-tune
  - To enable operations through libvirt it is handy to propagate the identifier of the VMI to the domain ([PR](https://github.com/kubevirt/kubevirt/pull/1883))
- Introduce a DSL or a yaml-based language for policy definition
- Introduce a way to designate MOM with special instructions or to alter the policies logic according to an environment status, e.g., VM states

# Question bank and lab assumptions

The bank contains 90 original educational items: 70 single-answer questions, 15 multiple-response questions (each asks for two selections), and five interactive labs. Questions are not copied from a live exam or a question-dump service. Correct option positions vary. Explanations describe the reasoning rather than simply restating an option letter.

| Primary domain | Choice IDs | PBQ | Main coverage |
| --- | --- | --- | --- |
| Mobile Devices | q-001–q-013 | pbq-3 | Laptop upgrades, displays, docks, Bluetooth, MDM, tethering, NFC, mail and file synchronization, WWAN, enterprise Wi-Fi |
| Networking | q-014–q-030 | pbq-1 | DHCP, service ports, VLAN isolation, wireless channels, PoE, IP addressing, routing, cabling tools, DNS, NAT, firewall state, router configuration |
| Hardware | q-031–q-051 | pbq-2 | RAID, processors, expansion cards, memory, display interfaces, printer technologies, PSUs, UPS, SATA/NVMe, cooling |
| Virtualization and Cloud Computing | q-052–q-060 | pbq-4 | IaaS/SaaS, hypervisors, host requirements, virtual networks, elasticity, snapshots, private cloud, metered usage, resource allocation |
| Hardware and Network Troubleshooting | q-061–q-085 | pbq-5 | Printer faults, physical links, DHCP/DNS symptoms, thermal faults, backlights, failing disks, duplicate addresses, queues, troubleshooting method, mobile faults, POST, bandwidth and cabling |

Every item has one primary reporting domain; several labs cross domain boundaries. The total allocation 14/18/22/10/26 rounds the requested 15/20/25/11/29% historical blueprint. RAID maintenance is assigned to hardware in this fixed allocation; diagnostic aspects also exercise troubleshooting. The five randomly selected pilot items do not change the presented blueprint counts but do change each scored domain's denominator.

## Lab assumptions

- **Router:** every client supports WPA3-Personal. The passphrase is already provisioned. The supplied fixed printer MAC and available reservation IP remove address ambiguity. Hiding an SSID is an exercise requirement only; it is not a security measure. [Apple's router guidance](https://support.apple.com/en-au/102766) explains the limitations of hidden networks.
- **RAID:** a fictional three-member RAID 5 array has one failed member and a known compatible spare. A backup and approved hot replacement are explicitly established. The allowlisted training commands describe a sequence; they are not valid commands to run against a real array. The backend only simulates progress, and its rebuild completes immediately.
- **Wi-Fi:** PEAP is the outer EAP method, MSCHAPv2 is the inner method, and the client must validate the server certificate. The trusted CA and permitted server name are already provisioned. The RADIUS address is configured on the AP/controller, distinct from the mobile profile. This legacy exercise does not recommend PEAP for every modern deployment. See [Microsoft's 802.1X deployment guide](https://learn.microsoft.com/en-us/windows-server/networking/core-network-guide/cncg/wireless/a-deploy-8021X-wireless-access) and [NPS/RADIUS planning](https://learn.microsoft.com/en-us/windows-server/networking/technologies/nps/nps-plan-server).
- **VM allocation:** the 16-core/64-GiB capacity is available after host overhead, and the ticket explicitly forbids overcommit. Real hypervisors may permit overcommit; that is outside this exercise. All supplied datastores have adequate capacity. Paths are scenario labels, not host filesystem destinations.
- **POST:** CedarBoard T4 and its code legend are fictional. Diagnosis uses the supplied legend rather than assuming codes are universal. Power disconnection and ESD precautions are part of the selected remedy.

## Limits and review

This is a fixed practice bank, not an exhaustive syllabus, standardized assessment, official certification readiness predictor or psychometrically calibrated item pool. The configuration labs emphasize reading requirements and applying concepts; they do not reproduce vendor administration screens. Detailed rationales are revealed only after submission. Multiple-response questions require the exact set; PBQs support explicit partial credit.

The historical five-domain weights are confirmed by [CompTIA's 2022 Core Series guide](https://assets.ctfassets.net/82ripq7fjls2/24rnnDmndd3UPQiPr3zXXF/11662bc248dd5a871504363cb0ac06b1/CompTIA-A-Core-Series-Certification-Guide-April-2022.pdf). Neither these weights nor this app's chosen pilot count establish CompTIA's confidential item weighting or equating model. Any future switch to another exam code should revise the blueprint, questions and labeling together.

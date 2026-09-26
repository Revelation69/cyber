# 220-1201 curriculum audit

Reviewed 26 September 2026 against CompTIA A+ 220-1201 V15, English objectives **document version 4.0**, obtained from the official CompTIA Partner Resources objectives collection. Older 2.0 links now redirect to the library; the retrieved English asset is 4.0. The source PDF is not redistributed here.

## Primary sources and traceability

- [CompTIA A+ 220-1201 V15 objectives, document version 4.0](https://lecbyo.files.cmp.optimizely.com/download/34be017cb73211ef8985a6f347fbf652)
- [Intel: Wi-Fi 6 versus Wi-Fi 6E/7 band support](https://www.intel.com/content/www/us/en/support/articles/000099711/wireless.html)
- [Microsoft: Containers versus virtual machines](https://learn.microsoft.com/en-us/virtualization/windowscontainers/about/containers-vs-vm)
- [Apple: Set up eSIM](https://support.apple.com/en-bh/118669)

Official PDF SHA-256: `9fb3471b397a863b1baa33912dffb6fa232b4631e2219f39188c5c109814648c`. Bank version: `1201-2026.09-v1`. Source IDs and objective references are stored on each item; references appear after submission. The official objectives establish scope, not the answers to these original questions. Vendor documentation supports the more specific radio, container and eSIM distinctions.

## Blueprint

| Domain | Official weight | Items in this 90-item form |
| --- | ---: | ---: |
| Mobile Devices | 13% | 12 |
| Networking | 23% | 21 |
| Hardware | 25% | 22 |
| Virtualization and Cloud Computing | 11% | 10 |
| Hardware and Network Troubleshooting | 28% | 25 |

Whole-item rounding totals 90. All **27 numbered objectives** have coverage. This does not mean every bullet/example is tested by one form. The official exam has a maximum of 90 questions in 90 minutes and a 675 passing score on its 100–900 scale. The fixed five labs, hidden five pilots, points and linear practice scoring are simulator design choices; CompTIA does not publish those exact operational details.

## Editorial review

Reviewed every stem, option set, key and rationale for a defensible best answer, stated assumptions and correct primary objective. Retained sound fundamentals rather than changing facts merely to rename the exam. Scenario distractors reflect a different layer, incompatible component, wrong service or an action not supported by the evidence. Multiple-response items state the number of answers. PBQs award field/milestone partial credit; the fictional RAID commands are supplied, not vendor syntax candidates must memorize.

Changed the SOHO lab to IPv4, gateway, DNS and DHCP reservations. Replaced the deep PEAP/MSCHAPv2/RADIUS lab with mobile eSIM, MDM, tethering, offline files and data-cap management. Mapped RAID repair to troubleshooting 5.2 and firmware boot selection to 3.5. Replaced generic methodology-recall questions: CompTIA explicitly excludes methodology memorization while continuing to test diagnostic scenarios. Removed the unsupported idea that suppressing an SSID is an appropriate security-learning goal.

Added or strengthened 6 GHz compatibility and regulatory/OS limits, TCP/UDP, SMTP mail-server delivery, network host roles, DMARC, WISP, OLED, printer maintenance/secure release, PSU input, RAID 6, containers, PaaS, cloud egress, RTC diagnosis and port flapping. Core 2-specific AI/security administration is not imported merely because it is new in the overall A+ series.

This is original practice content, not leaked, copied or recalled exam questions. It has not undergone a CompTIA endorsement, external subject-matter-expert panel or statistical difficulty calibration. It cannot guarantee the same difficulty or predict passing the real exam. A larger rotating bank and learner-response analysis would be needed to reduce repeat-question recall and calibrate difficulty.

## Item-to-objective map

| Item | Objective | Topic | Review |
| --- | --- | --- | --- |
| pbq-1 | 2.6 | Restore the branch workstation network | Revised |
| pbq-2 | 5.2 | Recover a degraded array | Revised |
| pbq-3 | 1.3 | Prepare a managed field tablet | Revised |
| pbq-4 | 4.1 | Allocate the lab hypervisor | Retained; checked |
| pbq-5 | 5.1 | Interpret a POST service ticket | Retained; checked |
| q-001 | 1.2 | A dock that will not drive a monitor | Retained; checked |
| q-002 | 1.1 | Restore laptop memory capacity | Retained; checked |
| q-003 | 1.1 | Replace a laptop battery safely | Retained; checked |
| q-004 | 1.3 | Pair the inventory scanner | Retained; checked |
| q-005 | 1.3 | Enable the mobile workforce | Retained; checked |
| q-006 | 1.2 | Use a phone as a network connection | Retained; checked |
| q-007 | 2.3 | Keep the branch services available | Revised |
| q-008 | 1.2 | Choose contactless data exchange | Retained; checked |
| q-009 | 1.3 | Restore corporate mail sync | Retained; checked |
| q-010 | 1.1 | Provide cellular capability | Retained; checked |
| q-011 | 2.7 | Connect a rural branch | Revised |
| q-012 | 1.3 | Keep files available offline | Retained; checked |
| q-013 | 1.1 | Match the replacement drive | Retained; checked |
| q-014 | 2.4 | Keep the label printer at one address | Retained; checked |
| q-015 | 2.1 | Inspect secure web connectivity | Retained; checked |
| q-016 | 2.4 | Segment visitors from payroll | Retained; checked |
| q-017 | 2.2 | Plan three adjacent access points | Retained; checked |
| q-018 | 2.5 | Power a ceiling access point | Retained; checked |
| q-019 | 2.6 | Recognize a private subnet | Retained; checked |
| q-020 | 2.5 | Join two different networks | Retained; checked |
| q-021 | 2.7 | Select a fiber uplink | Retained; checked |
| q-022 | 2.4 | Choose two name-resolution records | Retained; checked |
| q-023 | 2.8 | Inspect a wiring fault | Retained; checked |
| q-024 | 2.5 | Separate modem and router roles | Retained; checked |
| q-025 | 2.1 | Restore server-to-server mail delivery | Revised |
| q-026 | 2.1 | Provide reliable remote management | Retained; checked |
| q-027 | 2.2 | Find the missing 6 GHz network | Revised |
| q-028 | 2.2 | Approve a 6 GHz upgrade | Revised |
| q-029 | 2.6 | Inspect default-gateway configuration | Retained; checked |
| q-030 | 2.4 | Publish a mail-handling policy | Revised |
| q-031 | 3.4 | Size mirrored storage | Retained; checked |
| q-032 | 3.5 | Match a CPU upgrade | Retained; checked |
| q-033 | 3.5 | Equip a compact desktop | Retained; checked |
| q-034 | 3.3 | Identify the working memory requirement | Retained; checked |
| q-035 | 3.1 | Choose a display for dark-room review | Revised |
| q-036 | 3.8 | Complete scheduled laser maintenance | Revised |
| q-037 | 3.8 | Select an impact printer | Retained; checked |
| q-038 | 3.8 | Prepare a thermal receipt printer | Retained; checked |
| q-039 | 3.6 | Budget for a GPU upgrade | Retained; checked |
| q-040 | 3.6 | Move a desktop between mains supplies | Revised |
| q-041 | 3.2 | Expand SATA storage | Retained; checked |
| q-042 | 3.4 | Choose a workstation RAID layout | Retained; checked |
| q-043 | 3.7 | Verify a printer media setting | Retained; checked |
| q-044 | 3.4 | Keep an array available after two drive failures | Revised |
| q-045 | 3.6 | Interpret power supply efficiency | Retained; checked |
| q-046 | 3.4 | Install an M.2 storage module | Retained; checked |
| q-047 | 3.3 | Use ECC where supported | Retained; checked |
| q-048 | 3.7 | Protect documents at a shared printer | Revised |
| q-049 | 3.3 | Match memory generations | Retained; checked |
| q-050 | 3.2 | Select a connector for a wired endpoint | Retained; checked |
| q-051 | 3.5 | Select workstation cooling | Retained; checked |
| q-052 | 4.2 | Choose the cloud service layer | Retained; checked |
| q-053 | 4.2 | Remove application-server maintenance | Retained; checked |
| q-054 | 4.1 | Choose a hypervisor type | Retained; checked |
| q-055 | 4.1 | Prepare local virtual machines | Retained; checked |
| q-056 | 4.1 | Isolate a training network | Retained; checked |
| q-057 | 4.2 | Distinguish elasticity from fixed capacity | Retained; checked |
| q-058 | 4.1 | Compare application containers with full VMs | Revised |
| q-059 | 4.2 | Select a managed application platform | Revised |
| q-060 | 4.2 | Explain a cloud transfer charge | Revised |
| q-061 | 5.6 | Diagnose faint laser output | Retained; checked |
| q-062 | 5.6 | Toner rubs off the page | Retained; checked |
| q-063 | 5.5 | Follow the dropped network link | Retained; checked |
| q-064 | 5.5 | Resolve a self-assigned address | Retained; checked |
| q-065 | 5.5 | Separate DNS from connectivity | Retained; checked |
| q-066 | 5.1 | Investigate shutdowns under load | Retained; checked |
| q-067 | 5.3 | Distinguish display from graphics output | Retained; checked |
| q-068 | 5.2 | Protect a failing drive’s data | Retained; checked |
| q-069 | 5.5 | Investigate duplicate addresses | Retained; checked |
| q-070 | 5.6 | Restore an unresponsive print queue | Retained; checked |
| q-071 | 5.1 | Investigate a clock that resets | Revised |
| q-072 | 5.6 | Investigate multiple pages feeding | Retained; checked |
| q-073 | 5.4 | Restore a phone charging connection | Retained; checked |
| q-074 | 2.1 | Choose transport behavior for two services | Revised |
| q-075 | 5.5 | Find weak wireless coverage | Retained; checked |
| q-076 | 3.5 | Check a boot-device change | Retained; checked |
| q-077 | 5.1 | Troubleshoot a recent RAM upgrade | Retained; checked |
| q-078 | 5.5 | Distinguish high latency from name failure | Retained; checked |
| q-079 | 5.1 | Read a POST code correctly | Retained; checked |
| q-080 | 5.3 | Check a dim projector | Retained; checked |
| q-081 | 5.5 | Inspect a cable speed downgrade | Retained; checked |
| q-082 | 5.4 | Check an unresponsive touchscreen | Retained; checked |
| q-083 | 5.5 | Diagnose a flapping switch port | Revised |
| q-084 | 5.6 | Investigate wrong colors on an inkjet | Retained; checked |
| q-085 | 5.3 | Diagnose an intermittent display cable | Retained; checked |

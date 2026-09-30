# 220-1201 curriculum audit — complete replacement form

Reviewed 30 September 2026 against the official CompTIA A+ Core 1 **220-1201 V15 objectives, document version 4.0**. The official PDF was rechecked from the CompTIA Partner Resources asset. The bank is **1201-2026.09-v2**.

All 90 items replace the previous form: 70 single-answer questions, 15 multiple-response questions and five interactive PBQs. Every title and prompt is new, and all 85 sets of answer choices and explanations have been rewritten. Topics recur where the objectives require them, but this is a new authored form, not a reordered copy. Choices have varied answer positions. Item IDs identify positions within a version; saved attempts retain their own full versioned snapshot.

## Blueprint and source review

| Domain | Official weight | Items |
| --- | ---: | ---: |
| Mobile Devices | 13% | 12 |
| Networking | 23% | 21 |
| Hardware | 25% | 22 |
| Virtualization and Cloud Computing | 11% | 10 |
| Hardware and Network Troubleshooting | 28% | 25 |

Whole-item rounding totals 90. All **27 numbered objectives** are represented; one form does not test every subtopic. The 90-minute duration and 675 passing threshold on a 100–900 scale follow the published exam details. The five PBQs, five unscored practice items and linear scoring formula are simulator design choices, not claims about CompTIA's undisclosed scoring or any real exam form.

The official objectives establish content scope, not answer keys. The questions are original and do not use recalled or leaked exam items. Primary vendor documentation additionally supports memory transfer-rate terminology, modular PSU cable compatibility and virtual network behavior; NIST supports cloud models and characteristics.

- [CompTIA A+ 220-1201 V15 objectives, document version 4.0](https://lecbyo.files.cmp.optimizely.com/download/34be017cb73211ef8985a6f347fbf652)
- [Corsair: PSU cable compatibility](https://www.corsair.com/uk/en/explorer/diy-builder/power-supply-units/psu-cable-compatibility/)
- [Kingston: MT/s versus MHz](https://www.kingston.com/en/blog/pc-performance/mts-vs-mhz)
- [Microsoft: Hyper-V virtual switch](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/virtual-switch)
- [Cisco: Ethernet negotiation and duplex mismatch](https://www.cisco.com/c/en/us/support/docs/lan-switching/ethernet/10561-3.html)
- [NIST: Cloud computing characteristics and models](https://csrc.nist.gov/Projects/Cloud-Computing)

The original objectives PDF fingerprint is recorded in `data/blueprint.json`. Older vendor source IDs remain available so previously saved reviews retain their links.

## Editorial checks

Each item was reviewed for a defensible key, plausible alternatives, explicit multiple-response selection counts, sufficient evidence, objective alignment and a teaching explanation. Scenarios distinguish symptoms from causes, avoid unsupported universal firmware codes, and supply fictional controller syntax rather than requiring vendor command memorization. The review corrected unrelated distractors and strengthened the service-model comparison.

New PBQs:

- Configure a DHCP pool and client options while excluding static infrastructure.
- Recover a degraded RAID 10 mirror pair, preserving its healthy partner and rejecting an undersized spare.
- Correct five independent mobile discovery, location, calendar, data and upload settings.
- Convert workload profiles into VM CPU/RAM allocations and appropriate datastore placement.
- Diagnose a verified CPU-fan failure using a supplied model-specific POST legend.

The RAID console now uses each attempt's frozen inventory. Older attempts without that configuration continue to use their original RAID 5 inventory and commands. New bank validation rejects an inconsistent failed-member/bay mapping or an unavailable PBQ answer.

This is independently authored practice, not CompTIA-endorsed material. Editorial and functional review do not establish psychometric equivalence to the real exam. No external SME panel or learner-response difficulty calibration has been performed.

## Item-to-objective map

Every item below is newly authored for v2.

| Item | Objective | Topic |
| --- | --- | --- |
| pbq-1 | 2.6 | Commission a small-office DHCP service |
| pbq-2 | 5.2 | Restore the archive server mirror pair |
| pbq-3 | 1.3 | Restore a survey phone profile |
| pbq-4 | 4.1 | Place three training workloads |
| pbq-5 | 5.1 | Interpret a cooling interlock |
| q-001 | 1.1 | Service the keyboard ribbon |
| q-002 | 1.1 | Protect privacy at a shared desk |
| q-003 | 1.1 | Reconnect the wireless antennas |
| q-004 | 1.2 | Capture pressure-sensitive sketches |
| q-005 | 1.2 | Expand a desk with a port replicator |
| q-006 | 1.3 | Restore the missing calendar |
| q-007 | 1.3 | Stop roaming data use |
| q-008 | 1.2 | Move photographs through a cable |
| q-009 | 1.3 | Pair a headset with a replacement phone |
| q-010 | 1.1 | Choose the correct mobile battery |
| q-011 | 1.3 | Allow location for delivery check-ins |
| q-012 | 2.1 | Permit a Windows file share |
| q-013 | 2.1 | Distinguish two mailbox protocols |
| q-014 | 2.1 | Trace DHCP traffic |
| q-015 | 2.2 | Reduce channel overlap in a dense office |
| q-016 | 2.3 | Synchronize log timestamps |
| q-017 | 2.4 | Publish a mail destination |
| q-018 | 2.5 | Terminate an incoming fiber service |
| q-019 | 2.6 | Recognize an automatic link-local address |
| q-020 | 2.4 | Separate fixed addresses from leases |
| q-021 | 2.7 | Select a neighborhood network scope |
| q-022 | 2.8 | Find an unlabeled cable |
| q-023 | 2.3 | Consolidate perimeter inspection |
| q-024 | 2.4 | Keep an alias after a server change |
| q-025 | 2.5 | Add PoE without replacing a switch |
| q-026 | 2.1 | Identify an interactive remote desktop |
| q-027 | 2.7 | Match a cable internet handoff |
| q-028 | 2.8 | Terminate a structured cabling run |
| q-029 | 2.6 | Read an IPv6 local-link address |
| q-030 | 2.3 | Centralize network access decisions |
| q-031 | 2.2 | Track warehouse stock with radio tags |
| q-032 | 3.1 | Match smooth motion requirements |
| q-033 | 3.2 | Avoid a transfer-rate bottleneck |
| q-034 | 3.3 | Decode a DDR module rating |
| q-035 | 3.5 | Enable virtual machines in firmware |
| q-036 | 3.4 | Protect data on a striped set |
| q-037 | 3.6 | Avoid mixing modular PSU cables |
| q-038 | 3.7 | Set the default print output |
| q-039 | 3.8 | Maintain a receipt printer |
| q-040 | 3.2 | Connect a digital display and audio |
| q-041 | 3.4 | Select a PCIe storage drive |
| q-042 | 3.3 | Match memory to a compact system |
| q-043 | 3.5 | Identify the CPU power connector |
| q-044 | 3.1 | Choose an LCD panel for shared viewing |
| q-045 | 3.8 | Understand the laser imaging sequence |
| q-046 | 3.6 | Size a power supply for added drives |
| q-047 | 3.7 | Deploy a shared printer queue |
| q-048 | 3.4 | Identify a magnetic drive characteristic |
| q-049 | 3.5 | Add a capture card |
| q-050 | 3.2 | Recognize an optical patch connector |
| q-051 | 3.3 | Populate a two-channel memory board |
| q-052 | 3.7 | Configure scan delivery |
| q-053 | 3.8 | Service an impact printer |
| q-054 | 4.1 | Recognize a desktop hypervisor |
| q-055 | 4.2 | Limit infrastructure to one organization |
| q-056 | 4.1 | Connect a VM to the physical LAN |
| q-057 | 4.2 | Combine a private cloud with public capacity |
| q-058 | 4.1 | Use a virtual workstation remotely |
| q-059 | 4.2 | Explain shared cloud infrastructure |
| q-060 | 4.1 | Prepare a disposable test environment |
| q-061 | 4.2 | Support metered cloud purchasing |
| q-062 | 4.2 | Classify two purchased cloud services |
| q-063 | 5.1 | A new build shuts off under the bench test |
| q-064 | 5.2 | A drive disappears only after transport |
| q-065 | 5.3 | A conference screen says no signal |
| q-066 | 5.4 | A phone becomes hot in a vehicle |
| q-067 | 5.5 | Find the shared network outage |
| q-068 | 5.6 | A printer stops at the same paper position |
| q-069 | 5.1 | A desktop will not power on after service |
| q-070 | 5.2 | A hard drive clicks and drops offline |
| q-071 | 5.3 | An image is stretched on a new monitor |
| q-072 | 5.4 | Find a sudden battery drain |
| q-073 | 5.5 | The new access point cannot serve clients |
| q-074 | 5.6 | A color print has the wrong colors |
| q-075 | 5.1 | Isolate intermittent memory errors |
| q-076 | 5.2 | An external drive needs more power |
| q-077 | 5.3 | A projector shuts down during presentations |
| q-078 | 5.4 | A touch screen responds without contact |
| q-079 | 5.5 | Resolve a local address mismatch |
| q-080 | 5.6 | The printer is waiting for the wrong paper |
| q-081 | 5.5 | A new firewall policy breaks name lookups |
| q-082 | 5.1 | Unexpected restart under graphics load |
| q-083 | 5.2 | A mirror remains degraded after replacement |
| q-084 | 5.5 | Diagnose an Ethernet duplex mismatch |
| q-085 | 5.6 | A network printer changed addresses |

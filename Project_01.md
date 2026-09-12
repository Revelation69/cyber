# MA CYBERSECURITY ACADEMY

## PHASES 1–4 INTEGRATED CAPSTONE PROJECT

### Project Title

**Meridian Technologies Infrastructure Stabilisation & Security Improvement Project**

### Your Role

You have joined **Northstar Technology Services** as a **Junior IT & Security Analyst**.

Northstar provides IT support, infrastructure management and cybersecurity services to small and medium-sized businesses.

One of its clients, **Meridian Technologies Ltd**, has experienced several IT problems over the past few months and has asked Northstar to review its environment.

Your manager has assigned the engagement to you under supervision.

You will be responsible for:

- understanding the existing environment;
- documenting the company's systems;
- identifying technical problems;
- designing an improved network;
- administering Windows and Linux systems;
- troubleshooting faults;
- improving system security;
- reviewing vulnerabilities;
- investigating security events;
- writing technical reports;
- explaining your findings to management.

This is not a tutorial.

You are expected to research when necessary, make decisions, justify those decisions and document your work.

---

## 1. CLIENT BACKGROUND

Meridian Technologies Ltd is a growing professional-services business with approximately 35 employees.

The organisation has:

- Finance department
- Sales department
- Operations department
- Management
- IT administrator
- Hybrid employees working from home

The company currently operates from one office.

Its technology environment has grown organically rather than being formally designed.

Management believes this has started causing reliability and security problems.

---

## 2. CURRENT ENVIRONMENT

The company currently has approximately:

- 22 Windows 11 laptops
- 6 Windows desktop computers
- 2 Ubuntu Linux servers
- 1 multifunction network printer
- 1 internet router
- 1 managed network switch
- 2 wireless access points
- Microsoft 365
- Cloud file storage
- Several remote workers

The network was originally installed when the company had fewer than ten employees.

There is very little technical documentation.

Management cannot currently provide an accurate:

- asset inventory;
- network diagram;
- IP addressing document;
- security baseline;
- incident-response procedure;
- vulnerability register.

You have therefore been asked to create them.

---

## 3. BUSINESS PROBLEMS

Employees have reported several issues.

Examples include:

- slow computers;
- intermittent network connectivity;
- inability to access some websites;
- printers occasionally disappearing;
- poor Wi-Fi performance;
- computers running out of storage;
- employees receiving suspicious emails;
- repeated failed login attempts;
- inconsistent software updates.

The company is also concerned that employees may have more access than they actually require.

Management wants to improve the environment without purchasing expensive enterprise systems unnecessarily.

---

## 4. PROJECT RULES

All practical work must be completed inside:

- your own computer;
- your home network;
- your virtual machines;
- Cisco Packet Tracer;
- authorised academy systems;
- services specifically provided for the project.

You must not scan, attack, probe or interfere with systems you do not own or have explicit permission to test.

You may research documentation.

You may not copy another person's completed project.

Artificial intelligence may be used to help understand concepts, but you must be able to independently explain and demonstrate everything included in your submission.

Your mentor may ask you to repeat any task without your notes.

---

## PROJECT STRUCTURE

The engagement contains four phases.

## Phase 1

**IT Infrastructure Discovery & Stabilisation**

## Phase 2

**Network Architecture & Troubleshooting**

## Phase 3

**Systems Administration, Hardening & Automation**

## Phase 4

**Cybersecurity Assessment & Incident Response**

You may not proceed to the next phase until the previous phase has been reviewed.

---

## PHASE 1 — IT INFRASTRUCTURE DISCOVERY & STABILISATION

### Scenario

Meridian's management does not know exactly what equipment the organisation owns or whether its computers are appropriately configured.

Before making recommendations, you must establish an infrastructure baseline.

---

### Task 1.1 — Build Your Technical Laboratory

Create the laboratory you will use throughout the project.

Minimum environment:

#### Host computer

Your existing computer.

#### Virtual Machine 1

Windows workstation.

#### Virtual Machine 2

Ubuntu Linux.

Configure appropriate:

- CPU;
- memory;
- disk;
- network adapters.

Do not blindly copy recommended specifications.

Determine what your own host computer can safely support.

Document why you selected each allocation.

Before making major configuration changes, create snapshots.

---

### Task 1.2 — Host Computer Investigation

Perform a complete technical inventory of your own computer as though it were a Meridian employee workstation.

Identify:

- manufacturer;
- model;
- CPU;
- physical cores where available;
- logical processors;
- installed RAM;
- storage devices;
- storage capacity;
- available storage;
- filesystem;
- operating system;
- OS version;
- OS architecture;
- graphics adapter;
- Wi-Fi adapter;
- Ethernet adapter if available;
- MAC address;
- IP configuration;
- BIOS/UEFI information where available;
- connected peripherals.

Explain the purpose of the major components.

Do not merely list specifications.

---

### Task 1.3 — Workstation Suitability Assessment

Meridian has three different employee profiles.

#### Employee A — Finance Officer

Regularly uses:

- Excel;
- Outlook;
- browser applications;
- Teams;
- PDF documents;
- accounting software.

#### Employee B — Sales Employee

Regularly uses:

- Teams;
- CRM;
- Outlook;
- browser applications;
- presentations;
- video calls.

Frequently works remotely.

#### Employee C — Technical Analyst

Uses:

- multiple browser sessions;
- virtual machines;
- scripting tools;
- large log files;
- development tools.

Recommend suitable workstation specifications for all three employees.

For each recommendation provide:

- CPU;
- RAM;
- storage;
- network capability;
- operating system;
- additional relevant requirements.

Explain why the three users should not necessarily receive identical machines.

---

### Task 1.4 — Operating System Administration

On your Windows VM demonstrate that you can:

- identify running processes;
- identify resource utilisation;
- inspect services;
- stop and start an appropriate test service;
- inspect disk utilisation;
- create a local user;
- create a local group where supported;
- modify permissions;
- identify network configuration;
- inspect Windows Update;
- inspect Windows Defender;
- locate relevant system logs.

On Ubuntu demonstrate that you can:

- navigate the filesystem;
- create directories;
- create files;
- move files;
- copy files;
- remove files;
- identify users;
- identify groups;
- inspect processes;
- identify IP configuration;
- inspect disk utilisation;
- inspect memory utilisation.

Provide evidence.

---

### Task 1.5 — Technical Support Cases

Your service desk has assigned the following incidents to you.

#### Ticket IT-001

> My computer has become extremely slow whenever I have Teams, Outlook and several browser tabs open.

Investigate the possible causes and document your troubleshooting process.

---

#### Ticket IT-002

> Windows reports that the C: drive is almost full.

Determine:

- what information you would collect;
- what tools you would use;
- what could safely be removed;
- what should not simply be deleted;
- possible long-term solutions.

---

#### Ticket IT-003

> An external USB storage device has been connected but does not appear in File Explorer.

Develop a structured troubleshooting process.

---

#### Ticket IT-004

> The laptop becomes unusually hot and sometimes shuts itself down.

Investigate possible hardware and software causes.

---

#### Ticket IT-005

> A computer powers on but cannot successfully boot into Windows.

Create a logical troubleshooting decision tree.

---

### Phase 1 Deliverables

Submit:

```text
phase-1/
├── README.md
├── asset-inventory.md
├── workstation-recommendations.md
├── virtual-lab-build.md
├── windows-administration.md
├── linux-baseline.md
├── troubleshooting-report.md
├── diagrams/
└── screenshots/
```

---

### PHASE 1 REVIEW

You must be able to answer questions such as:

- Why did you allocate that amount of RAM to your VM?
- What happens when RAM becomes exhausted?
- What is the difference between RAM and storage?
- What happens during the computer boot process?
- What is a process?
- What is a service?
- Why should normal employees not have unnecessary administrator privileges?
- Why are snapshots useful?
- What would you check first when diagnosing a slow computer?

A correct report without understanding is not sufficient.

---

## PHASE 2 — NETWORK ARCHITECTURE & TROUBLESHOOTING

### Scenario

Your Phase 1 investigation reveals another major problem.

Meridian's network was never properly designed.

Most devices currently exist on the same network.

Employees, printers and servers are not appropriately separated.

Management has therefore asked you to propose a redesigned network.

---

### Task 2.1 — Current Network Investigation

Investigate your own authorised home/lab network.

Identify:

- your IP address;
- subnet mask or CIDR prefix;
- default gateway;
- DHCP configuration;
- DNS server;
- MAC address;
- loopback address;
- private IP address;
- public IP concept.

Explain how your computer received its network configuration.

---

### Task 2.2 — Explain the Communication Process

Write a technical explanation answering:

#### What happens when a Meridian employee enters:

`https://www.example.com`

into a browser?

Your explanation should appropriately discuss concepts including:

- application;
- DNS;
- IP;
- MAC addressing;
- default gateway;
- ARP;
- switching;
- routing;
- NAT;
- TCP;
- ports;
- TLS;
- HTTP/HTTPS;
- encapsulation;
- return traffic.

You should be able to explain the same process verbally.

---

### Task 2.3 — Meridian Network Redesign

Meridian wants the following logical networks:

- Corporate Users
- Servers
- Management
- Guest Wi-Fi

You have been allocated:

`192.168.50.0/24`

Design an appropriate addressing strategy.

For every network document:

- network address;
- CIDR;
- subnet mask;
- usable range;
- default gateway;
- broadcast address;
- expected number of devices;
- DHCP or static addressing decision.

Your design must leave reasonable capacity for growth.

Justify your subnet choices.

---

### Task 2.4 — Network Diagram

Produce a professional logical network diagram showing at minimum:

- Internet;
- ISP connection;
- router/firewall;
- switch;
- wireless access points;
- user network;
- server network;
- management network;
- guest network;
- Windows systems;
- Linux servers;
- printer.

The diagram must correspond with your IP design.

---

### Task 2.5 — Cisco Packet Tracer Implementation

Implement a simplified version of your design using Cisco Packet Tracer.

The environment should demonstrate:

- switching;
- routing;
- IP addressing;
- default gateways;
- DHCP where appropriate;
- multiple network segments;
- communication testing.

Provide evidence that your addressing works.

---

### Task 2.6 — Network Segmentation Policy

Management asks:

> Why can't we simply keep all devices on one network?

Write a recommendation explaining:

- network segmentation;
- security;
- performance;
- administrative separation;
- guest access;
- server protection;
- management interfaces.

Create a simple traffic policy.

For example, determine whether:

- Guest Wi-Fi should reach servers.
- Corporate users should reach management interfaces.
- Management systems should administer servers.
- Servers should initiate arbitrary connections to users.

You must make and justify the decisions yourself.

---

### Task 2.7 — Packet Analysis

Using Wireshark, capture authorised traffic generated by your own system.

Investigate examples including:

- DNS;
- ICMP;
- TCP;
- HTTP where safely available;
- TLS/HTTPS.

Identify a TCP three-way handshake.

Identify:

- source IP;
- destination IP;
- source port;
- destination port;
- protocol;
- packet sequence where relevant.

Create a packet-analysis report.

---

### Task 2.8 — Network Troubleshooting Cases

Investigate the following fictional incidents.

#### NET-001

A workstation has:

```text
IP address: 192.168.50.25
Gateway: 192.168.50.1
```

It can communicate with nearby systems but cannot access the internet.

Develop a troubleshooting approach.

---

#### NET-002

A user reports:

> I can successfully reach 8.8.8.8, but websites do not load when I type their names.

Explain what you would investigate.

---

#### NET-003

One workstation assigns itself an address beginning:

`169.254.x.x`

Investigate.

---

#### NET-004

Two employees intermittently lose network access after both arriving at the office.

Determine possible explanations and how you would prove or eliminate each hypothesis.

---

#### NET-005

Employees on Guest Wi-Fi can access an internal company server.

Management states that this should not be possible.

Identify what area of the design should be investigated.

---

### Phase 2 Deliverables

```text
phase-2/
├── README.md
├── network-baseline.md
├── browser-request-explanation.md
├── ip-addressing-plan.md
├── network-design.md
├── segmentation-policy.md
├── packet-tracer-lab.md
├── wireshark-analysis.md
├── network-troubleshooting.md
├── diagrams/
└── screenshots/
```

---

## PHASE 3 — SYSTEM ADMINISTRATION, HARDENING & AUTOMATION

### Scenario

Management approves your network recommendations.

Northstar now asks you to review the operating systems and administrative practices used by Meridian.

Several poor practices have been identified.

Employees have historically been given permissions based on convenience rather than necessity.

Linux servers have not been formally hardened.

Logging is inconsistent.

Repetitive administration tasks are being performed manually.

---

### Task 3.1 — Linux Server Administration

Configure your Ubuntu VM as a simulated Meridian server.

Create appropriate:

- users;
- groups;
- directories;
- permissions.

Demonstrate:

- `sudo`;
- process management;
- service management;
- networking commands;
- scheduled tasks;
- log inspection.

Explain every significant configuration choice.

---

### Task 3.2 — Linux Hardening Review

Perform a security review of the Ubuntu server.

Consider areas such as:

- unnecessary accounts;
- privileged access;
- file permissions;
- updates;
- services;
- firewall;
- SSH configuration;
- logging;
- authentication;
- scheduled tasks.

Produce:

**Ubuntu Server Hardening Report**

The report must separate:

#### Finding

What is wrong?

#### Evidence

How do you know?

#### Risk

Why does it matter?

#### Recommendation

What should change?

#### Validation

How would you confirm that the change worked?

---

### Task 3.3 — Windows Security Review

Review your Windows system.

Investigate:

- local users;
- administrator membership;
- password/security configuration;
- NTFS permissions;
- firewall;
- Windows Defender;
- updates;
- services;
- Event Viewer;
- PowerShell;
- account activity.

Produce a Windows workstation security baseline.

---

### Task 3.4 — Active Directory Design Exercise

Meridian expects to grow beyond 50 employees.

Management is considering centralised identity management.

Prepare a basic Active Directory design explaining:

- domain;
- domain controller;
- users;
- groups;
- organisational units;
- Group Policy;
- privileged accounts;
- authentication;
- Kerberos;
- NTLM.

Design a logical structure for:

```text
Meridian Technologies
├── Finance
├── Sales
├── Operations
├── Management
└── IT
```

Determine how groups and permissions should be organised.

Do not assign permissions to individuals where a group-based approach would be more appropriate.

---

### Task 3.5 — Authentication Log Investigation

Generate or use authorised test authentication activity on your Linux machine.

Include successful and unsuccessful authentication attempts.

Investigate the logs.

Determine:

- who attempted authentication;
- when attempts occurred;
- whether authentication succeeded;
- source information where available;
- whether the behaviour appears normal or suspicious.

Produce a short investigation report.

---

### Task 3.6 — Python Security Automation

Create a Python program named:

`auth_log_analyser.py`

The program must analyse an authentication log or appropriately structured sample data.

At minimum it should:

- read input from a file;
- identify failed authentication events;
- count events;
- identify relevant usernames;
- identify source IP addresses where present;
- summarise results;
- output findings.

Your program must include:

- sensible variable names;
- functions;
- error handling;
- input validation;
- comments where useful;
- README;
- usage instructions;
- example input;
- example output.

Do not hard-code the entire solution around one exact log file.

---

### Task 3.7 — Additional Automation

Create at least **two** additional scripts from the following:

- file hash checker;
- suspicious-IP extractor;
- CSV alert summariser;
- disk-space monitor;
- user/account inventory;
- system-information collector.

At least one script should use PowerShell or another operating-system-native administrative method.

---

### Phase 3 Deliverables

```text
phase-3/
├── README.md
├── linux-administration.md
├── ubuntu-hardening-report.md
├── windows-security-baseline.md
├── active-directory-design.md
├── authentication-investigation.md
├── scripts/
│   ├── auth_log_analyser.py
│   ├── additional-script-1
│   ├── additional-script-2
│   └── README.md
├── evidence/
└── diagrams/
```

---

## PHASE 4 — CYBERSECURITY ASSESSMENT & INCIDENT RESPONSE

### Scenario

Three weeks after your infrastructure review, Meridian's IT administrator contacts Northstar.

An employee has reported receiving a suspicious email.

Shortly afterwards, unusual authentication activity was noticed.

Management does not know whether the events are related.

You are assigned to assist with the investigation.

Before investigating the incident, you must complete a broader security assessment of the organisation.

---

### Task 4.1 — Security Architecture Review

Assess Meridian against fundamental security principles.

Consider:

- confidentiality;
- integrity;
- availability;
- least privilege;
- separation of duties;
- defence in depth;
- Zero Trust principles;
- resilience;
- backups;
- segmentation.

Identify weaknesses in the original Meridian environment and explain how your Phase 1–3 recommendations improve them.

---

### Task 4.2 — Threat Assessment

Identify realistic threat actors relevant to Meridian.

Consider:

- cybercriminals;
- malicious insiders;
- negligent insiders;
- compromised suppliers;
- opportunistic attackers.

For each relevant threat actor identify:

- likely motivation;
- possible attack method;
- valuable target;
- likely business impact.

Do not claim that every possible threat is equally likely.

Prioritise.

---

### Task 4.3 — Vulnerability Management Exercise

Create Meridian's first vulnerability register.

Identify at least **10 plausible technical or administrative vulnerabilities** based on the scenario and your lab findings.

For every vulnerability record:

- unique ID;
- affected asset;
- vulnerability;
- evidence;
- likelihood;
- impact;
- risk rating;
- remediation;
- owner;
- target date;
- status.

Where appropriate, research the concepts of:

- CVE;
- CVSS;
- patching;
- remediation;
- mitigation;
- risk acceptance;
- false positives.

Do not invent CVEs for software unless you have verified that the CVE actually applies.

---

### Task 4.4 — Identity & Access Review

Develop an identity-security recommendation covering:

- least privilege;
- MFA;
- privileged accounts;
- RBAC;
- joiners;
- movers;
- leavers;
- password practices;
- account review;
- shared accounts;
- service accounts.

Answer:

> What should happen to an employee's access from the moment they join Meridian until the moment they leave?

---

### Task 4.5 — Data Protection & Cryptography

Management asks you to explain how sensitive company information should be protected.

Prepare recommendations covering:

- encryption at rest;
- encryption in transit;
- hashing;
- digital signatures;
- certificates;
- TLS;
- PKI;
- key management.

Clearly distinguish concepts that are often incorrectly treated as interchangeable.

---

### Task 4.6 — Incident Investigation

Your mentor will provide an **Incident Evidence Pack**.

The pack may contain items such as:

```text
INC-2026-001/
├── employee-statement.txt
├── email-information.txt
├── authentication.log
├── windows-events.csv
├── dns.log
├── firewall.log
├── process-events.csv
└── asset-information.csv
```

Treat the evidence as though it came from a real organisation.

You must determine:

- what happened;
- when it happened;
- which account was involved;
- which device was involved;
- whether suspicious activity occurred;
- what evidence supports your conclusion;
- what remains uncertain.

Do not jump immediately to a conclusion.

Develop and test hypotheses.

---

### Task 4.7 — Incident Timeline

Create a chronological timeline.

Example structure:

| Time | Event | Source | Significance |
| ---- | ----- | ------ | ------------ |
|      |       |        |              |

Your timeline must distinguish:

- established facts;
- assumptions;
- unconfirmed theories.

---

### Task 4.8 — Incident Response

Using an appropriate incident-response lifecycle, document:

#### Preparation

What should already have existed?

#### Detection & Analysis

How was the incident identified?

#### Containment

What immediate actions should be taken?

#### Eradication

What must be removed or corrected?

#### Recovery

How should normal operation safely resume?

#### Lessons Learned

What should Meridian improve afterwards?

---

### Task 4.9 — Security Improvement Plan

Management cannot fix everything immediately.

Create a prioritised plan.

Separate recommendations into:

#### Critical

Immediate attention.

#### High

Near-term remediation.

#### Medium

Planned improvement.

#### Low

Longer-term maturity work.

You must consider:

- risk;
- cost;
- complexity;
- business disruption;
- dependencies.

---

### Task 4.10 — Executive Briefing

Prepare a **10-minute management presentation**.

Your audience is:

- Managing Director;
- Finance Director;
- Operations Manager.

Assume they are intelligent but not cybersecurity specialists.

Explain:

1. what you were asked to do;
2. what you discovered;
3. the most serious risks;
4. whether an incident occurred;
5. business impact;
6. immediate actions;
7. longer-term recommendations.

Do not fill the presentation with unexplained technical terminology.

---

## FINAL PROJECT DELIVERABLES

Your complete repository should resemble:

```text
meridian-security-project/
│
├── README.md
│
├── phase-1/
│   ├── asset-inventory.md
│   ├── workstation-recommendations.md
│   ├── virtual-lab-build.md
│   ├── windows-administration.md
│   ├── linux-baseline.md
│   └── troubleshooting-report.md
│
├── phase-2/
│   ├── network-baseline.md
│   ├── browser-request-explanation.md
│   ├── ip-addressing-plan.md
│   ├── network-design.md
│   ├── segmentation-policy.md
│   ├── packet-tracer-lab.md
│   ├── wireshark-analysis.md
│   └── network-troubleshooting.md
│
├── phase-3/
│   ├── ubuntu-hardening-report.md
│   ├── windows-security-baseline.md
│   ├── active-directory-design.md
│   ├── authentication-investigation.md
│   └── scripts/
│
├── phase-4/
│   ├── security-architecture-review.md
│   ├── threat-assessment.md
│   ├── vulnerability-register.md
│   ├── iam-review.md
│   ├── cryptography-recommendations.md
│   ├── incident-investigation.md
│   ├── incident-timeline.md
│   ├── incident-response.md
│   └── security-improvement-plan.md
│
├── diagrams/
├── screenshots/
├── evidence/
└── presentation/
```

---

## DOCUMENTATION STANDARD

Screenshots alone are not evidence of understanding.

Whenever you provide evidence, explain:

### What am I showing?

### Why did I perform this action?

### What does the result mean?

### What conclusion can I draw?

Where commands are used, include relevant commands rather than hiding them inside screenshots.

Never expose:

- passwords;
- API keys;
- authentication tokens;
- private credentials;
- unnecessary personal information.

---

## CHANGE LOG

Maintain:

`change-log.md`

For significant changes record:

| Date | Change | Reason | Result |
| ---- | ------ | ------ | ------ |
|      |        |        |        |

This is intended to develop professional change-management habits.

---

## ISSUE LOG

Maintain:

`issue-log.md`

Record problems encountered during the project.

| ID | Problem | Investigation | Resolution | Status |
| -- | ------- | ------------- | ---------- | ------ |
|    |         |               |            |        |

Do not hide mistakes.

Documenting how you diagnosed and corrected a mistake is valuable evidence.

---

## DECISION LOG

Maintain:

`decision-log.md`

Whenever you make a significant technical decision, document:

### Decision

What did you choose?

### Alternatives

What else did you consider?

### Reason

Why did you choose this option?

### Trade-off

What disadvantage does your chosen approach have?

This project assesses engineering judgement, not simply whether you arrived at one predetermined answer.

---

## ASSESSMENT

### Phase 1 — 20 Marks

- Infrastructure discovery: 5
- Operating-system administration: 5
- Virtualisation: 4
- Troubleshooting: 6

### Phase 2 — 25 Marks

- Networking knowledge: 5
- IP addressing and subnetting: 5
- Network design: 5
- Packet analysis: 4
- Troubleshooting: 6

### Phase 3 — 25 Marks

- Linux administration: 5
- Linux hardening: 5
- Windows security: 4
- Identity/Active Directory understanding: 4
- Automation and scripting: 7

### Phase 4 — 30 Marks

- Security assessment: 5
- Vulnerability/risk analysis: 5
- Identity and data protection: 4
- Incident investigation: 8
- Incident response: 4
- Executive communication: 4

## TOTAL: 100 MARKS

---

## GRADING STANDARD

### 90–100 — Exceptional

You demonstrate strong technical understanding, independent troubleshooting, clear reasoning and professional-quality documentation.

### 80–89 — Strong

You demonstrate reliable understanding and can perform most tasks independently.

### 70–79 — Competent

You meet the academy standard but have identifiable areas requiring improvement.

### 60–69 — Developing

You understand many concepts but require too much assistance or lack sufficient practical competence.

### Below 60 — Not Yet Competent

Substantial remediation is required before progression.

---

## MANDATORY PRACTICAL DEFENCE

Your written submission is only part of the assessment.

After every phase, your mentor may select any part of your project and ask you to:

- reproduce it;
- troubleshoot it;
- modify it;
- explain it;
- defend your decision;
- solve a similar problem without referring to your documentation.

You should therefore never submit anything that you cannot personally explain.

---

## FINAL TECHNICAL INTERVIEW

At the end of Phase 4 you will complete a technical defence.

You may be asked questions such as:

> A user's computer can reach its gateway but cannot reach the internet. What would you investigate?

> Why would you separate guest devices from company servers?

> What is the difference between authentication and authorisation?

> How does DNS affect a web request?

> Why is a hash not the same as encryption?

> What information would you examine after repeated failed logins?

> Why should administrators not use privileged accounts for ordinary daily work?

> Explain the difference between a vulnerability, threat and risk.

> What evidence would make you believe an account had actually been compromised?

> How would you explain a serious cybersecurity incident to a Managing Director?

Your answers must demonstrate understanding rather than memorised definitions.

---

## PROJECT COMPLETION STANDARD

The project is not complete simply because every file exists.

To complete the engagement successfully you must be able to:

**Build it.**

**Troubleshoot it.**

**Secure it.**

**Investigate it.**

**Explain it.**

**Document it.**

**Defend your decisions.**

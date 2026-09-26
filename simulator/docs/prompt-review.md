# Current scope update — 220-1201

The user corrected the requested exam to 220-1201. The original review below records the initial 220-1101 build. The current implementation supersedes its legacy-blueprint recommendation; see [the current curriculum audit](curriculum.md). Named passing attempts now receive clearly marked mock certificates.

# Review of the supplied simulator prompt

The specification is a useful starting point: a bounded 90-question bank, timed attempt, five practical tasks, and a container deployment. Several requirements need correction before they can support an honest, testable implementation.

| Finding | Revision and implementation decision |
| --- | --- |
| It presents 220-1101 without identifying the exam generation. | Label every attempt as **legacy 220-1101 practice**. Preserve the requested blueprint; do not silently substitute 220-1201 content. |
| “Precise, emulated CompTIA scoring” implies access to a real validated scoring model. | Use an explicitly illustrative weighted practice score. Do not claim certification prediction or CompTIA psychometric validation. |
| Large PBQ weights and exactly five pilots are presented as official facts. | Keep them as requested simulator rules: 6 points per choice item, 50 per PBQ, and five random choice pilots per attempt. These counts and weights are not asserted to describe the real exam. |
| The percentages cannot produce integer counts over 90 questions. | Use 14 mobile, 18 networking, 22 hardware, 10 cloud, and 26 troubleshooting items, including PBQs. This is a largest-remainder allocation, resolving the mobile/hardware tie in favor of mobile. |
| Domain coverage and score contribution are conflated. | Show blueprint weights as coverage targets and domain performance as earned/available scored points. Heavy PBQs change the relative contribution of domains to the final score. |
| Multiple-response grading and partial-credit rules are underspecified. | Exact-set matching for multiple response; equal rubric-step credit for PBQs. A VM host overcommit removes CPU/RAM credit, while correct storage choices retain credit. |
| The client could expose keys/pilot flags or manipulate the timer. | Keep keys, pilot IDs, deadline and grading in the backend. Store an attempt snapshot in SQLite; return only public question fields until submission. |
| The Wi-Fi task places a RADIUS server address in an ordinary client profile. | Separate managed client Wi-Fi fields from the AP/controller RADIUS setting. Require trusted CA validation. |
| Disabling SSID broadcast could be interpreted as a security improvement. | Retain it only as an explicit exercise requirement; explain that hidden SSIDs are not a security control. |
| RAID syntax is vendor/OS dependent and could imply destructive real commands. | Provide a clearly named mock RAID CLI with a documented allowlist and ordered diagnosis/replacement/rebuild state. It never executes a system shell. |
| POST codes are not universal. | Supply a fictional vendor-specific diagnostic legend inside the lab, and grade against that legend. |
| “Production-ready” is not measurable without operational constraints. | Deliver a runnable single-host container, non-root process, persistent volume, health check, tests, and an EC2 runbook. Public multi-user operation still requires an HTTPS/access layer and deployment-specific capacity validation. |

The bank contains original educational scenarios, not actual examination questions. A fixed bank supports repeat practice but is not an adaptive exam or a comprehensive certification course. The review intentionally avoids inventing a conversion between raw accuracy and the real examination score.

## Reference basis

The historical domain blueprint is confirmed in [CompTIA's April 2022 Core Series certification guide](https://assets.ctfassets.net/82ripq7fjls2/24rnnDmndd3UPQiPr3zXXF/11662bc248dd5a871504363cb0ac06b1/CompTIA-A-Core-Series-Certification-Guide-April-2022.pdf). Current exam selection should be checked with [CompTIA](https://www.comptia.org/certifications/a). The build does not require a claim about an exact retirement date. Lab-specific technical sources are recorded in [curriculum.md](curriculum.md).

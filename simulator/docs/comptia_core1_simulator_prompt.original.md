You are an expert curriculum developer, CompTIA psychometrician, and full-stack software engineer. Your task is to output a complete, production-ready blueprint and codebase for a local **CompTIA A+ Core 1 (220-1101) Exam Simulator**. This simulator will be deployed inside a Docker container on an AWS EC2 instance. 

Generate the entire project structure, configuration files, backend architecture, and a full 90-question bank adhering strictly to the constraints below.

---

### 1. APPLICATION ARCHITECTURE & INFRASTRUCTURE
Provide the exact code files for a lightweight, self-contained architecture:
- **`Dockerfile`**: A multi-stage or efficient single-stage build using `python:3.11-slim` or `node:20-alpine`. Ensure it exposes port `8080` and installs any necessary dependencies.
- **`docker-compose.yml`**: Define the service, environment variables, restart policies, and port forwarding (`80:8080`) for seamless AWS deployment.
- **Backend/Frontend Engine**: Implement a single-file application or simple framework (e.g., Python FastAPI/Flask with embedded HTML templates, or Node.js Express). It must handle:
  - Session state tracking (current question index, selected answers, elapsed time).
  - A 90-minute countdown timer.
  - A "Review Flag" system allowing users to mark questions and return to them via an exam grid interface.

---

### 2. THE PSYCHOMETRIC SCORING ALGORITHM
Implement a precise, emulated CompTIA scoring engine within the backend:
- **Scale Range**: Minimum score of 100, maximum score of 900. Passing threshold is exactly **675**.
- **Hidden Weighting System**: 
  - Standard multiple-choice/multiple-response questions carry a baseline weight (e.g., 5-8 points scaled).
  - Performance-Based Questions (PBQs) carry massive weights (e.g., 40-60 points scaled) and support **partial credit** for multi-step configurations.
- **Unscored Anchors**: Exactly **5 out of the 90 questions** must be programmatically flagged as "unscored pilot items." The user must not know which ones they are, and their correctness must have 0% impact on the final scaled score.
- **Score Report Generation**: Upon submission or time expiration, generate a diagnostic report showing:
  - Final Scaled Score (100-900) & Pass/Fail status.
  - Domain-level performance breakdown percentage mapping to the 5 official Core 1 Domains:
    - 1.0 Mobile Devices (15%)
    - 2.0 Networking (20%)
    - 3.0 Hardware (25%)
    - 4.0 Virtualization and Cloud Computing (11%)
    - 5.0 Hardware and Network Troubleshooting (29%)

---

### 3. THE FULL 90-QUESTION BANK SPECIFICATIONS
Incorporate a complete dataset of 90 realistic exam questions directly inside the application storage (JSON or native code data structure). The question bank must contain:

#### A. Multiple-Choice & Multiple-Response (85 Questions)
- Distribute across the 5 domains matching official exam percentages.
- Write realistic, highly situational troubleshooting scenarios (e.g., *"A technician receives a ticket regarding a laser printer producing faint images..."*).
- Provide highly plausible distractors (incorrect answers) that test true conceptual understanding rather than obvious errors.

#### B. Performance-Based Questions (5 Interactive PBQs)
Design 5 text/UI-emulated interactive CLI, ticketing, or configuration scenarios:
1. **PBQ 1 (Networking):** A SOHO router configuration interface. The user must input commands or choose specific drop-downs to change the default SSID, switch from WEP to WPA3-Personal, disable SSID broadcasting, and configure a DHCP reservation.
2. **PBQ 2 (Troubleshooting/Hardware):** A RAID array failure scenario. A command-line simulation where the user must type commands (`diskpart`, `mdadm`, or mock RAID CLI tools) to diagnose a degraded RAID 5 array, identify the failed serial number drive, replace it, and initiate a rebuild.
3. **PBQ 3 (Mobile/Networking):** A corporate wireless client deployment. The user must configure an enterprise mobile device's Wi-Fi profile given a specific RADIUS server IP, SSID, and authentication type (PEAP/MSCHAPv2).
4. **PBQ 4 (Cloud/Virtualization):** A hypervisor resource allocation scenario. The user must allocate exact vCPU cores, RAM limits, and storage paths for 3 virtual machines based on contrasting corporate requirements (Database server vs. VDI client vs. Web server) without exceeding total host hardware limits.
5. **PBQ 5 (Troubleshooting):** A mother-board/POST diagnostics simulation. The user interprets a sequence of motherboard POST beep codes or diagnostic LED hex numbers, inputs the correct system fault component, and selects the corresponding hardware remediation step.

---

### 4. AWS DEPLOYMENT RUNBOOK
Provide a comprehensive `README.md` file text walking through the exact bash commands to execute inside an AWS EC2 instance:
1. Launching an Amazon Linux 2023 or Ubuntu Server EC2 instance with Security Groups opening ports 22 (SSH) and 80 (HTTP).
2. Installing Docker and Docker Compose via CLI.
3. Cloning/transferring this codebase onto the instance.
4. Running `docker compose up --build -d` to go live.
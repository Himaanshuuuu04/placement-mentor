# Secure Code Execution Architecture

## 1. Overview
The Secure Code Execution Platform (PLANE D) is responsible for running untrusted code submitted by students. Because submitted code is inherently untrusted and potentially malicious, it must execute in a strictly isolated, ephemeral environment.

## 2. Execution Pipeline

**Flow:**
Frontend → Assessment Service (API Gateway) → Code Execution Service → Judge0 → Firecracker microVMs → Execution Result → Evaluation Service

1. **Submission:** Code is submitted to the Assessment Service.
2. **Delegation:** The Code Execution Service receives the payload, formatting it for Judge0.
3. **Execution:** Judge0 orchestrates the execution inside Firecracker microVMs.
4. **Collection:** Standard output, standard error, execution time, and memory usage are collected.
5. **Evaluation:** Results are passed to the Evaluation Service and subsequently to the Code Evaluator Agent.

## 3. Isolation Boundaries and Limits

The system assumes all submitted code is malicious. The primary isolation mechanism is **Firecracker microVMs**, providing hardware-level virtualization with minimal overhead.

### 3.1 Resource Limits
To mitigate resource exhaustion attacks, strict limits are enforced per execution:
- **CPU Limits:** Capped to specific CPU shares/cores (e.g., 1 vCPU).
- **Memory Limits:** Strict RAM allocation (e.g., 256MB) to prevent memory exhaustion.
- **Time Limits (Wall and CPU Time):** Hard timeouts (e.g., 2-5 seconds for standard algorithms) to prevent infinite loops.
- **Process Limits:** Process count restrictions (PID limits) to prevent fork bombs.
- **Filesystem Limits:** Read-only root filesystems, with a highly restricted, ephemeral, quota-limited `/tmp` mount. No host filesystem access.

### 3.2 Network Policy
- **No Internet Access:** The microVMs run without outbound network connectivity to prevent data exfiltration, network abuse (e.g., DDoS, port scanning), or downloading malicious payloads.
- **No Local Network Access:** MicroVMs cannot access the internal VPC or other internal services.

## 4. Threat Model Mitigation

| Threat | Mitigation |
|--------|------------|
| **Fork Bombs** | Strict PID limits (e.g., max 64 processes). |
| **Infinite Loops** | Hard wall-clock and CPU time timeouts. |
| **Memory Exhaustion** | Strict RAM limits via cgroups/microVM configuration. OOM Killer handles violations. |
| **Filesystem Escape** | Firecracker hardware virtualization; no shared mounts with the host; read-only OS image. |
| **Network Abuse** | Explicitly disabled network interfaces inside the microVM. |
| **Privilege Escalation** | Code runs as an unprivileged user inside the microVM. |

## 5. Lifecycle and Cleanup
- **Ephemeral Environments:** Every submission runs in a newly provisioned, clean microVM.
- **Timeout and Kill:** If a process exceeds its time limit, the microVM is immediately killed and torn down.
- **State Cleanup:** Upon completion or termination, the microVM instance is destroyed. No state is reused between submissions.

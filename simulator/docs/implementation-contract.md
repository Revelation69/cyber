# Current implementation contract

See the [revised specification](comptia_core1_simulator_prompt.revised.md), [curriculum audit](curriculum.md) and [README](../README.md).

`POST /api/exam` requires exactly `{"candidate_name":"Alex Morgan"}`. Each attempt stores its exam code, bank version, name and domain blueprint. `GET /api/exam/certificate` returns private HTML only for a completed passing named 220-1201 attempt. Print styling supports saving it as PDF. Questions expose objective references and explanations only in the submitted review. Legacy snapshots retain their original identity and scoring.

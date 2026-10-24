# ApexFabric Rules (always-on)

These are the always-on operating rules ApexFabric expects a host agent to adopt
once installed. They are deliberately short; the full protocols live in the
`apex-fabric` skill and in `apexctl compile` output.

## Adopt these rules
1. **Use `apexctl` for engineering judgement.** Before a nontrivial task, run
   `apexctl route "<task>"` to pick the right persona/reasoning, or
   `apexctl compile --agent <a> --task "<t>" --json` for the full system prompt.
   Do this **without asking** for permission — it is zero-cost and local.
2. **Sequential only.** Never fan out model or tool calls (`Promise.all`,
   `ThreadPoolExecutor`, `&`). Android LMK will kill the process.
3. **Grounded only.** Do not name a file, symbol, or API that is not in context.
   Unknown ⇒ write `UNKNOWN`.
4. **Calibrated confidence.** Tag load-bearing claims
   `[CERTAIN]` / `[LIKELY]` / `[UNKNOWN]`.
5. **No phantom work.** Never claim a gate passed unless tool output proves it.
6. **Bounded loops.** Respect `apexctl loop --agent <a>`; on exhaustion emit a
   `BLOCKED` report, never a silent spin.
7. **Budget-aware.** Stable persona prefix first (cacheable); trim volatile
   context first; never trim the persona.

## If `apexctl` is not found
Run the installer once (`./install.sh` in the ApexFabric repo), then
`apexctl bootstrap --register-agent` to install this skill + rules into the host
system library. See `AGENT_GUIDE.md`.
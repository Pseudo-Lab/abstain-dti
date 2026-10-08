<h1 align="center">abstain-dti</h1>
<h3 align="center">Do AI drug discovery models know when they are wrong?</h3>
<p align="center">A calibration and abstention benchmark for drug-target prediction, built on difficulty coordinates</p>
<p align="center"><a href="README.md">한국어</a> · <b>English</b></p>

<div align="center">
<a href="https://pseudo-lab.com"><img src="https://img.shields.io/badge/PseudoLab-S13-3776AB" alt="PseudoLab"/></a>
<a href="https://discord.gg/EPurkHVtp2"><img src="https://img.shields.io/badge/Discord-BF40BF" alt="Discord Community"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/stargazers"><img src="https://img.shields.io/github/stars/Pseudo-Lab/abstain-dti" alt="Stars Badge"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/network/members"><img src="https://img.shields.io/github/forks/Pseudo-Lab/abstain-dti" alt="Forks Badge"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/pulls"><img src="https://img.shields.io/github/issues-pr/Pseudo-Lab/abstain-dti" alt="Pull Requests Badge"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/issues"><img src="https://img.shields.io/github/issues/Pseudo-Lab/abstain-dti" alt="Issues Badge"/></a>
<a href="https://github.com/Pseudo-Lab/abstain-dti/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/Pseudo-Lab/abstain-dti?color=2b9348"></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"/></a>
</div>
<br>

> **In one line**
>
> We are building a public benchmark that measures whether drug discovery models and AI agents **say "I don't know"
> when they don't know**, on top of physically defined difficulty coordinates. We then compare them directly against
> a properly calibrated supervised baseline.


| | |
| --- | --- |
| Cohort | Pseudo-Lab 13th Cohort Open Academy |
| Activity period | 2026.10.04 - 2027.01.09 (12-week core + 2-week buffer) |
| Kickoff meeting | 2026.10.10 (Sat) |
| Regular meetings | Every **Saturday 10:00-12:00 KST** (2 hours) |
| Members | 12 (1 Builder + 11 Runners) |
| Communication | Pseudo-Lab Discord `#Room-YB` |
| Repository | <https://github.com/Pseudo-Lab/abstain-dti> · MIT License |
| Project page | <https://pseudo-lab.com/projects/8f035eab-4433-4661-9ae8-8f20e57ef06b> |

---

## 🎯 Summary

Four things this cohort must leave behind:

- [ ] **Public benchmark.** 60 to 100 queries, ground truth, a table of 6 difficulty coordinates, and evaluation scripts
- [ ] **Calibrated baseline.** A reference risk-coverage curve with conformal prediction applied
- [ ] **Comparison report.** Supervised models and LLM agents compared side by side, including a cost column
- [ ] **Reproducible repository.** A newcomer can complete the example notebook using only the README

One more item is conditional:

- [ ] **Perturbation audit harness.** Measures whether an agent notices when a tool returns a wrong value. We
      measure the cost in the W08 pilot and then decide whether to run it in full. Condition C (ToolUniverse agent)
      is decided at the same time.

### Expected Outcome

- `Open Source Repository`: <https://github.com/Pseudo-Lab/abstain-dti> (MIT)
- `Research / Experiment`: per-condition comparison and risk-coverage report
- `Documentation`: `results/benchmark/EVALUATION.md`, CONTRIBUTING.md, LICENSE-AUDIT.md, weekly progress logs
- `Demo`: one reproducible example notebook
- `Paper (Extension Track)`: arXiv preprint, ICLR 2027 workshop submission

The work splits into three tracks.

| Track | What it does |
| --- | --- |
| ML & Calibration | Trains models that predict binding from protein sequence and molecular structure, then statistically calibrates the models' confidence |
| Agent & Perturbation Audit | Makes LLMs call real biology tools and tests whether they notice when a tool lies |
| Difficulty-Coordinate Curation | Computes 6 numbers for each evaluation question that say "how hard this question is" and attaches them |

> The goal is not a perfect result but to experiment together and leave behind something that actually runs.

---

## ✨ Why we are doing this

### The problem

As of 2026, biomedical AI agents have multiplied quickly. Nature published three AI Scientist papers at the same
time, Biomni appeared in Science, and Kosmos moved to a commercial spin-out. Yet the bottleneck the field points to
is not new models but tool integration, verification, and benchmarking. Edison Scientific also names trust and
verification as the adoption bottleneck.

Medea showed that a design built around verification, plus calibrated abstention, contributes to performance. But
**there is still no benchmark that directly measures whether a model or agent recognizes its own ignorance.** The
counterintuitive result reported by AssayBench, that domain-specific LLMs do worse than general-purpose LLMs, also
shows the limits of evaluation that looks only at accuracy.

Meanwhile, most drug-target interaction (DTI) benchmarks are measured on a random split. This does not match what
real drug discovery faces: unseen targets and unseen chemical scaffolds. And there is no evaluation axis that
quantifies this mismatch.

> **Problem statement**
>
> People who want to use AI for drug discovery struggle because they have no way of knowing when a model is wrong.

### Five core questions

1. Does a model's confidence, or its abstention decision, track **the actual difficulty of the problem**?
2. At the same difficulty, where do a properly calibrated small supervised model and an LLM agent stand?
3. In **which difficulty ranges only** does predicted structure (AlphaFold) information help?
4. When a tool returns a wrong value, does the agent detect it?
5. Is the abstention decision itself **reproducible across repeated runs?**

### Why this topic

- **Difficulty can be defined in advance.** DTI is a rare task where difficulty can be computed as a prior physical
  quantity rather than a post-hoc label. Molecular similarity to the training set, target sequence identity, and
  predicted-structure confidence are extracted as numbers before the problem is solved. This is the decisive
  difference from general LLM abstention research, and it is this project's unique asset.
- **If the results differ from expectations, that is the result.** The conclusion "even the latest structure-based
  models do not know their own uncertainty on novel targets" is worth reporting on its own.
- **The work splits into 3 difficulty levels.** This suits a team with a wide skill range.
- **All required infrastructure is public.** TDC, AlphaFold DB, OpenFold3, ToolUniverse, MAPIE.
- **It runs to the end without a GPU.** Heavy experiments are split off as optional tasks. If resources change, the
  project does not collapse.

---

## 👥 Who we want to work with

One Builder and eleven Runners, twelve people, build this together.

| Track | Members | What you need |
| --- | --- | --- |
| ML & Calibration | 4 (including Builder) | Being able to use Python is enough. ML experience helps but is not required |
| Agent & Perturbation Audit | 4 | Being able to use Python and having called an API before is enough |
| Difficulty-Coordinate Curation | 4 | A biology background helps. Beginner-level coding is fine |

**Tracks are not decided at the start.** For the four weeks from W01 to W04, everyone does the same thing. We read
papers together, set up environments, and each person builds one tool-calling agent. After seeing what fits during
those four weeks, we assign tracks at the end of W04 based on preference and aptitude. Work is done in pairs, and
you may switch tracks midway.

**We especially want to point out the Curation track.** It has the lowest coding burden, yet it is where you
directly build the difficulty-coordinate table, the most distinctive part of this project. It suits people who
know biology but find code intimidating.

### It's fine if you are new

- You don't need to know drug development. In W01 we start by aligning on vocabulary.
- You don't need to have read a paper all the way through. In W02 each person takes one paper and we read them
  together.
- It's fine if git is new to you. There are [onboarding materials](docs/onboarding/w01-drug_development_onboarding.html).
- It's fine if you are outside Korea. That is why the meeting is on Saturday morning.

### What we ask of you

- Be able to attend a 2-hour meeting once a week. If you will miss a week, just let us know in advance.
- Leave a written record of your work. If someone drops out, the next person must be able to take over.
- Say you don't know when you don't know.

### Recruitment schedule

| Date | Event |
| --- | --- |
| 2026.09.18 | Recruitment opens |
| 2026.09.28 | Recruitment closes |
| 2026.10.01 | Selection announced |
| 2026.10.04 | Activity begins |
| 2026.10.10 | Kickoff meeting (Sat) |
| 2027.01.09 | Activity ends |

### How to participate

- **Runner**: Does the actual research, development, and testing. Joins one of the three tracks.
- **Builder**: [@ybaeus](https://github.com/ybaeus). Handles project planning and operations.
- **Auditing (observer)**: You can join the public sessions without applying.

Auditing requires no special application. Join the Discord `#Room-YB` channel at 10:00 Korea time on Saturday.
You are also welcome to meet us at Magical Week events or Pseudo Lab events.

Join link: [Pseudo-Lab Discord](https://discord.gg/EPurkHVtp2)

### You can contribute even if you are not in the cohort

Check the `good first issue` label and [`CONTRIBUTING.md`](CONTRIBUTING.md). In particular, **extending the
difficulty coordinates** and **adding evaluation-set queries** are areas where outside contributions are welcome.

### Team

Tracks are **provisional assignments**. They are finalized at the end of W04 based on preference and aptitude.
GitHub handles will be filled in at kickoff.

| Role | Name | Responsibility |
| --- | --- | --- |
| Builder | [@ybaeus](https://github.com/ybaeus) | Project lead, evaluation design, participates in ML & Calibration track |
| Runner | 하민주 | ML & Calibration |
| Runner | 최호재 | ML & Calibration |
| Runner | 박소정 | ML & Calibration |
| Runner | 김태엽 | Agent & Perturbation Audit |
| Runner | 서동영 | Agent & Perturbation Audit |
| Runner | 차재민 | Agent & Perturbation Audit |
| Runner | 정재훈 | Agent & Perturbation Audit |
| Runner | 권예진 | Difficulty-Coordinate Curation |
| Runner | 김시은 | Difficulty-Coordinate Curation |
| Runner | 이성주 | Difficulty-Coordinate Curation |
| Runner | 전소연 | Difficulty-Coordinate Curation |

**About the Builder.** Led a project in Pseudo-Lab's 5th cohort (ran an NGS analysis project). Hands-on experience
in bioinformatics and spatial biology. Currently lives in Seattle.

### How we work together

```text
Explore → Design → Build → Test → Improve → Share
```

- **Meetings**: Every Saturday 10:00-12:00 Korea time. The first part is progress sharing, the second part is pair
  work. Extra meetings as needed
- **Task management**: Everything in GitHub Issues. Weekly milestones
- **Review**: PRs are merged after at least one review
- **Dropout readiness**: All work is documented so it can be handed off

Our three principles:

- Start by building small things.
- Record the process and the failures too. The design makes confirming that something does not work a result as well.
- **This is not a structure where the Builder gives orders and Runners execute.** Every track directly owns one
  column of the results table, and review flows both ways.

---

## 🧪 What we are building (evaluation design details)

<details>
<summary>6 difficulty coordinates, split protocol, comparison conditions, metrics, perturbation audit, 3 AlphaFold stages (click to expand)</summary>
<br>

### Target task and data

| Item | Details |
| --- | --- |
| Main task | Drug-Target Interaction. **BindingDB** from TDC (auxiliary: Papyrus / ChEMBL) |
| Input and output | From protein sequence + compound SMILES to binding affinity (regression) or binding yes/no (classification) |
| Auxiliary task | TDC ADMET group (BBB permeability, hERG toxicity, CYP inhibition). Single input, so the barrier to entry is low. We run the abstention and calibration metric pilot here first |
| Excluded | DAVIS / KIBA are excluded from the main data. They are kinase panels, so experimental structures are saturated and the contribution of predicted structures cannot be seen, and the number of targets (442 / 229) is too small for statistical power on a cold-target split. Used only for auxiliary validation to compare with prior work |

### Difficulty coordinates

**Every query in the evaluation set gets the 6 coordinates below.** This table is what sets the benchmark apart.

| Coordinate | Definition | Tools |
| --- | --- | --- |
| Ligand novelty | Maximum Tanimoto similarity to the training set, whether the Murcko scaffold matches | RDKit |
| Target novelty | Maximum sequence identity to training targets | MMseqs2 / BLAST |
| Structure confidence | Mean pLDDT of pocket residues, PAE within the pocket | AlphaFold DB, P2Rank |
| Structure availability | Whether an experimental PDB exists (90% identity over the pocket region) | PDB, SIFTS |
| Target maturity | Pharos target development level (Tclin / Tchem / Tbio / Tdark) | Pharos, IDG |
| Contamination axis | Publication date of the original measurement paper (before or after the LLM training cutoff) | ChEMBL, PubMed |

**Split protocol.** The 4 splits `random` / `cold-drug` / `cold-target` / `cold-both`, plus a ligand scaffold
split, are **always all reported**. They are frozen at the end of W04 and no changes are allowed afterwards. If the
splits are touched later, all results must be rerun.

### Comparison conditions (4-way core + 2 extensions)

| Item | Details | Owning track | Type |
| --- | --- | --- | --- |
| **A. Baseline (calibrated)** | ESM-2 embeddings + AlphaFold pocket features, with conformal prediction applied | ML | Core |
| **B. Zero-shot LLM** | Prompt only, self-reported confidence | Agent | Core |
| **C. Agent** | Tool calling based on ToolUniverse MCP + literature search. Cannot abstain | Agent | Core |
| **D. Agent + abstention** | Same as C, but with an explicit abstention option | Agent | Core |
| **E. Agent + conformal** | Applies the **same conformal procedure** as A to the confidence of C and D (self-reported or self-consistency) | Agent + ML | Extension (no GPU needed) |
| **F. Boltz-2 co-folding** | Conformal applied to the affinity head + `ligand_iptm` of open-weight Boltz-2 | ML | Extension (GPU-conditional) |

- **B → C → D is a staircase that adds one capability at a time.** It separates the effect of tools (B→C) from the
  effect of the abstention option (C→D).
- **E is the condition that makes the comparison fair.** If only A uses conformal, the difference becomes "whether a
  calibration device is present". E checks whether LLM confidence still fails to track difficulty when the same
  device is applied. Using answer agreement across the logs of 3 repeated runs of C and D as the self-consistency
  score, a reduced version can be produced **with no extra API cost**.
- **F is promoted or not at the W01 resource gate.** If no GPU is secured, it stays in the existing 3-stage plan
  (Extension Track). The main conclusions are designed to be complete with A-E alone.

> Whether to add more conditions is **decided after the W08 pilot gives measured cost per query**. We are
> considering adding an existing SOTA agent (Biomni) as a comparison, and adding conditions stays open until just
> before the full run in W09.

### Input conventions (common to all conditions)

| Item | Convention |
| --- | --- |
| **Input** | **Only** protein sequence + compound SMILES. Same for all conditions (A-F) |
| **Excluded** | Target identifiers such as UniProt IDs are not given. With an identifier, an LLM can answer from memory without analyzing the sequence, or look up the answer directly in a DB, which defeats the cold-target split and the contamination axis. If an agent needs an identifier, it must find it on its own from the sequence using tools |
| **Difficulty coordinates** | **Not given to the model as input.** Difficulty coordinates are tags attached to the question sheet and are used only when stratifying results for analysis |
| **Binding threshold** | `binds = true` if pAffinity ≥ 6.0 (Kd / Ki / IC50 ≤ 1 µM). Applied identically to the ground truth and all conditions |
| **LLM settings** | temperature 0.7 (at 0, flip rate is structurally 0). Model, token limit, and tool list are fixed across conditions and all logged |
| **Output** | JSON schema enforced (see `track_agent/prompts/`). Use the API's structured output feature where possible |
| **Freeze** | Prompts are frozen after the W08 pilot, like the splits, and their version is committed |

**Direct lookup tracking.** Conditions C and D include `identified_target` (the target inferred from the sequence)
and `direct_measurement_found` (whether a measured value for that pair was found) in their output. Because these are
self-reported, they are checked against the `evidence` log. Queries with `direct_measurement_found = false` whose
contamination axis is "after the LLM training cutoff" are reported separately as **the range closest to true
predictive ability**.

**Affinity units.** BindingDB mixes Kd, Ki, and IC50, and IC50 depends on experimental conditions (substrate
concentration, etc.). The measurement type is kept as a column, and regression results are also reported per
measurement type. Boltz-2's `affinity_pred_value` is in log10(IC50, µM) units, so for comparison it is converted
as pAffinity = 6 - y.

### How abstention happens

**Baseline (A, E, F).** It is not the model judging "this is hard"; conformal prediction forces it statistically.

1. On a calibration set not used for training, compute the nonconformity score (how low the probability given to
   the correct answer is).
2. Set the threshold to the quantile corresponding to the target coverage (90%).
3. For a new input, collect the labels that pass the threshold into a prediction set.

| Prediction set | Interpretation |
| --- | --- |
| `{binds}` or `{not binds}` | Answers |
| `{binds, not binds}` | **Abstains** |
| `{}` | Outlier. Counted separately |

For regression, a prediction interval is produced, and if the interval width exceeds the threshold it is treated as
an abstention. The implementation uses MAPIE.

**Agent (D).** It abstains on its own through the `abstain` field allowed by the prompt.

**Fair comparison.** Because the abstention mechanisms differ, comparison is made **at the same coverage point**
(e.g. selective accuracy at 80% coverage).

**Limits and what is measured.** The 90% guarantee of standard conformal holds only under the exchangeability
assumption. A cold split is by definition a distribution shift, so the guarantee can break, and **how far the
measured coverage per split falls below the target is itself reported as a result**. If needed, we compare against
weighted conformal (covariate shift correction).

**Conformal cannot change the ranking.** Conformal only sets the threshold correctly; it does not improve the
quality of the scores. A model whose confidence is unrelated to difficulty can hit the coverage target while its
abstentions still do not concentrate on hard questions. Therefore **AURC and the difficulty-stratified slope** are
the decisive metrics.

### Metrics

| Axis | Metric |
| --- | --- |
| Accuracy | AUROC / RMSE (depending on the task) |
| Selective prediction | risk-coverage curve, AURC, selective accuracy **at the same coverage (80%)** |
| Calibration | ECE (expected calibration error), conformal coverage. Measured value against the 90% target |
| Difficulty stratification | Performance and confidence slope per range of the 6 coordinates above |
| Reproducibility | **flip rate** of the abstention decision across 3 repeats of the same query. Not the variance of the answer, but flips in whether to answer |
| Robustness | Detection rate of tool output perturbations |
| Target identification | Fraction of cases where the agent correctly identified the target from the sequence (`identified_target`) |
| Lookup vs prediction | Fraction of direct lookups of measured values (`direct_measurement_found`, verified with the evidence log), performance with lookups excluded |
| Cost | Tokens per query, latency, USD. **A required column of the results table** (responding to *AI Agents That Matter*'s call for cost-controlled evaluation) |

**Core hypotheses**

1. A properly calibrated small baseline (A) beats the agents (B, C, D) across the whole risk-coverage range.
2. Agent confidence barely drops as pocket pLDDT and target sequence identity go down. That is, **the difficulty
   slope of the abstention rate is steep for the baseline and flat for the agents.**
3. **Even with the same conformal procedure applied (E)**, the agents hit the coverage target but AURC does not
   improve. The problem is not whether a calibration device is present but that the confidence score does not
   carry difficulty.
4. (F, optional) Even the latest structure-based model (Boltz-2) does not lower `ligand_iptm` and binding probability
   enough in the cold-target and low-pLDDT ranges.

**If these are true, that itself is the result.** Even if Boltz-2 leads on accuracy, what this benchmark measures is
not accuracy but **whether a model knows its own ignorance**.

### Tool output perturbation audit

We inject controlled errors into tool return values and measure the agent's detection rate. It needs no GPU, the
implementation burden is low, and it maps directly onto real failure modes in practice. This is the Agent track's
unique contribution.

- **Unit perturbation**: swap nM and µM
- **Entry perturbation**: return outdated or retracted UniProt and ChEMBL records
- **Identity perturbation**: return the SMILES of a valid but different molecule
- **Identifier perturbation**: swap target IDs

### Using AlphaFold in 3 stages

Structure information is used as real features, not decoration. Each stage is designed **to produce results
independently**.

| Stage | Details | Resources | This cohort |
| --- | --- | --- | --- |
| Stage 1 (required) | Bulk download from AlphaFold DB, pocket detection with P2Rank / fpocket, generate features for pocket pLDDT and PAE, volume, residue composition | CPU only | Core |
| Stage 2 (recommended) | SaProt based on Foldseek 3Di tokens, or ESM-IF structure-aware embeddings. Converts structure information into a learnable form without docking | Small GPU | Core |
| Stage 3 (challenge) | Run **OpenFold3** (Apache 2.0) on 50 targets, compare new MSA and single-sequence against AF DB. Optionally run **Boltz-2 open weights** (MIT, pinned to v2.2.x) co-folding on 200 pairs and compare directly with the affinity head | A100 / L4 | Extension Track |

> **Version caution.** Boltz 2.1 (2026-06) is closed source and runs only through Boltz's own hosted API. Numbers
> used in the paper must be produced with the **open-weight version**, and the version string is stated in the
> results table. The training and evaluation code for Boltz-2 in the official repository is currently unreleased,
> so we do not make plans that assume "reproducible training".
>
> **We do not run full co-folding on the whole dataset.** The GPU budget would collapse. Stage 3 is separated as an
> independent challenge task, so if it fails, the schedule and the paper are unaffected.

> **Allocation of the 200 Boltz-2 pairs.** Instead of spreading them evenly, they are stratified at the two extremes
> of difficulty. The aim is to show "does confidence track difficulty" cleanly with few pairs.
>
> | Range | Pairs | What we want to see |
> | --- | --- | --- |
> | random split, high pocket pLDDT | 50 | Upper bound when it is easy |
> | cold-target, high pocket pLDDT | 50 | Unseen target, but good structure |
> | cold-target, low pocket pLDDT | 50 | The hardest range |
> | cold-both | 50 | Extreme |
>
> If GPU is plentiful, each range is increased in the same proportion. **MSAs are generated once per target and
> cached** (no repeated `--use_msa_server` calls). The signals used are `affinity_probability_binary`
> (classification), `affinity_pred_value` (regression), and `ligand_iptm` and pocket-region PAE (confidence).

</details>

## 🗺️ Weekly roadmap

<details>
<summary>14-week plan by week, gates, 6-step minimum spine (click to expand)</summary>
<br>

**12-week core + 2-week buffer · 2026.10.10 - 2027.01.09**

Weeks **start on Saturday.** At the regular meeting on the first Saturday of each week, 10:00-12:00, we close last
week's Issues and open this week's Issues. Kickoff is on the first day of W01, **2026.10.10 (Sat)**. The leader is
in Seattle, so locally it is Friday evening.

Each week is linked to a GitHub Milestone and a `week/WXX` label.

### Phase 1. Laying the foundation (W01-W04, everyone together)

This phase absorbs skill differences and identifies aptitudes. **Track assignment happens at the end of W04.**

| Week | Period | Regular meeting (KST) | Main activities | Deliverables | Gate |
| --- | --- | --- | --- | --- | --- |
| **W01** | 10.10-10.16 | 2026.10.10 (Sat) 10:00-12:00 | Kickoff. Team introductions and role preference survey, environment setup (GitHub / conda). Confirm actual GPU access (Colab Pro / university cluster / KISTI / NIPA). Secure LLM API credit sources and **fix the budget cap as a number**. Collect the whole team's schedules (check overlap with exam periods and year-end). **Decide whether to promote condition F (Boltz-2).** Record GPU type, VRAM, count, and available period in the resource memo | repo initialization, environment setup PR, resource check memo | **Resource gate.** Decide whether to run Stages 2 and 3 and the number of repeats for conditions B/C/D |
| **W02** | 10.17-10.23 | 2026.10.17 (Sat) 10:00-12:00 | One paper per person review presentations (Appendix A below). **Verify every DOI and link.** Count the actual number of low-pLDDT and no-PDB targets | `/docs/literature` summaries, target availability statistics | If too few targets, decide whether to relax the pocket identity threshold |
| **W03** | 10.24-10.30 | 2026.10.24 (Sat) 10:00-12:00 | Everyone builds their own tool-calling agent (calculator + search, 2 tools). **Connect ToolUniverse via MCP** and compare with the self-built implementation | Individual practice notebooks | None |
| **W04** | 10.31-11.06 | 2026.10.31 (Sat) 10:00-12:00 | Load TDC data, final task selection. **Finalize the definitions of the 6 difficulty coordinates, freeze the split protocol.** Document the abstention, calibration, and reproducibility protocols, write the curation guidelines. **Track assignment.** **Finalize input conventions** (sequence + SMILES only, binding threshold pAffinity 6.0), commit `track_agent/prompts/` v0 | `results/benchmark/EVALUATION.md`, data loader code | **Freeze gate.** No changes to splits after this, tracks finalized |

### Phase 2. Parallel development (W05-W08, by track)

The three tracks run at the same time. **Work is done in pairs, and moving between tracks is allowed.**

| Week | Period | Regular meeting (KST) | ML & Calibration (4) | Agent & Perturbation (4) | Curation (4) |
| --- | --- | --- | --- | --- | --- |
| **W05** | 11.07-11.13 | 2026.11.07 (Sat) 10:00-12:00 | Cache ESM-2 embeddings + Morgan fingerprints, collect AlphaFold DB structures, extract P2Rank pockets. **Dependency license audit** | Connect ToolUniverse MCP, build a logging system for every call. Include **token, latency, and cost fields** in the logging schema. Design the confidence and abstention output schema | 20 draft queries, assign author and verifier pairs |
| **W06** | 11.14-11.20 | 2026.11.14 (Sat) 10:00-12:00 | First baseline. Logistic regression / XGBoost. Baselines on **all 4 splits** | Connect literature search (PubMed API) and compound and protein DB lookups, compare 2 or more model backends | 40 queries cumulative, start the coordinate computation pipeline |
| **W07** | 11.21-11.27 | 2026.11.21 (Sat) 10:00-12:00 | Compare structure representations. Add pocket features, SaProt / ESM-IF, **2D vs 3D ablation** | Implement the perturbation harness. Injection of 4 error types and detection logic | 60 queries, first computation of the 6 coordinates |
| **W08** | 11.28-12.04 | 2026.11.28 (Sat) 10:00-12:00 | Calibration. conformal prediction (MAPIE), risk-coverage curves, **variance measurement with fixed seeds** | Run the **40-query pilot**, fix parsing failures, measure total cost. Use the pilot results to **check the distribution of self-reported confidence** (if values cluster on a few levels, switch E to the self-consistency score), **freeze prompts** | Two-person cross-verification, finalize `results/benchmark/queries.jsonl` and `results/benchmark/difficulty.tsv` |

> **W08 is the peak load point of this schedule.** Calibration work and the pilot run at the same time, and the
> evaluation set must also be finalized. The pilot is set at **40 queries** because if parsing failures show up in
> the W09 full run, there is no week left to recover.

> **The end of W08 is when the minimum spine is complete.** The 6 steps below can be completed without a GPU using
> only mature libraries. This is half of the deliverables, and after this point, whichever challenge task fails,
> there will still be results to present.
>
> 1. Load TDC BindingDB
> 2. Cache ESM-2 embeddings + Morgan fingerprints
> 3. Fix the 4 splits
> 4. Train XGBoost
> 5. Compute the 6 difficulty coordinates
> 6. Generate risk-coverage curves with conformal prediction

### Phase 3. Comparative evaluation (W09-W11)

| Week | Period | Regular meeting (KST) | ML & Calibration | Agent & Perturbation | Curation |
| --- | --- | --- | --- | --- | --- |
| **W09** | 12.05-12.11 | 2026.12.05 (Sat) 10:00-12:00 | Full run of condition A | Full runs of conditions B, C, D, **3 repeats** | First review of error logs produced during runs |
| **W10** | 12.12-12.18 | 2026.12.12 (Sat) 10:00-12:00 | Compute risk-coverage, AURC, ECE, difficulty-stratified analysis | Compute abstention **flip rate**, aggregate cost per condition. **Produce the reduced condition E** from the 3-repeat logs (based on answer agreement, zero extra cost), verify `direct_measurement_found` | Collect and organize wrong-answer cases |
| **W11** | 12.19-12.25 | 2026.12.19 (Sat) 10:00-12:00 | Finalize the final metrics table. **Freeze gate** | Log-based root-cause tracing | Qualitative classification of failure modes (search failure / reasoning error / tool selection error / unit error) |

### Phase 4. Release and wrap-up (W12-W14)

| Week | Period | Regular meeting (KST) | Main activities | Deliverables |
| --- | --- | --- | --- | --- |
| **W12** | 12.26-01.01 | 2026.12.26 (Sat) 10:00-12:00 | **Buffer week (year-end).** Absorb backlog. No cleanup work is scheduled for this week | Clear backlog items |
| **W13** | 01.02-01.08 | 2027.01.02 (Sat) 10:00-12:00 | Open-source cleanup. README (install, run, reproduce), `CONTRIBUTING.md`, Issue and PR templates, MIT license, one reproducible example notebook, apply license audit results. Reproducibility check: *complete the example notebook in a fresh environment using only the README* | Release-ready repository, reproducibility check log |
| **W14** | 01.09 (Sat) | 2027.01.09 (Sat) 10:00-12:00 | Final presentation materials, repo release, demo. Write up extension plans (router training, abstention head fine-tuning). **Hand off to the Extension Track** | Presentation materials, retrospective notes, Extension Track owners confirmed |

> Documentation is not something to cram into the last week. README and `results/benchmark/EVALUATION.md` are
> filled in **a little with each PR starting in W05**.

</details>

## 🧭 Milestones and GitHub operations

<details>
<summary>M1-M5 completion criteria, per-track completion criteria, label and branch conventions, repository structure (click to expand)</summary>
<br>

### Milestones

The 5 milestone slots on the Pseudo-Lab platform and the GitHub Milestones are **matched 1:1.** Completion criteria
list **only items that can be verified by eye**, so the Builder can check them and administrators can approve them.

| # | GitHub Milestone | Week | Due | Completion criteria |
| --- | --- | --- | --- | --- |
| **1** | `M1 · 기반 확정` | W01-W04 | 2026-11-06 | Everyone's environment setup PR merged · resource check memo recording GPU and API budget · `results/benchmark/EVALUATION.md` written · **freeze commit** of the 4 splits · track assignment table published |
| **2** | `M2 · 첫 baseline과 도구 연결` | W05-W07 | 2026-11-27 | XGBoost performance table exists for **all 4 splits** · structure feature ablation results · ToolUniverse call log collection confirmed · 60 draft queries |
| **3** | `M3 · 최소 척추 완주` | W08 | 2026-12-04 | conformal risk-coverage curve produced · 4-type perturbation harness working · `queries.jsonl` and `difficulty.tsv` finalized · 40-query pilot run and **cost measured** |
| **4** | `M4 · 비교와 결과 동결` | W09-W11 | 2026-12-25 | Raw run logs published · AURC, ECE, flip rate tables · difficulty stratification figure · failure mode classification table · **numbers freeze tag** |
| **5** | `M5 · 공개와 재현` | W12-W14 | 2027-01-09 | Example notebook completed in a fresh environment using only the README · `CONTRIBUTING.md` and `LICENSE-AUDIT.md` written · final presentation materials · repo public |

### Per-track completion criteria (M2-M5)

M1 is before track assignment, so everyone works on the same tasks.

| Milestone | ML & Calibration | Agent & Perturbation | Curation |
| --- | --- | --- | --- |
| **M2** (W05-07) | ESM-2 embedding and Morgan fingerprint cache · AlphaFold DB collection and P2Rank pocket extraction · XGBoost baselines on 4 splits · pocket and SaProt feature ablation table · `LICENSE-AUDIT.md` | ToolUniverse MCP connected · call logs including token, latency, and cost fields · confidence and abstention output schema finalized · PubMed and compound DB lookups working · 2 model backends compared | 60 draft queries · coordinate computation pipeline working · first computed values for the 6 coordinates |
| **M3** (W08) | conformal prediction applied · risk-coverage curve and AURC produced · variance measured with fixed seeds | 4-type perturbation injection harness · detection logic · 40-query pilot run · measured cost per query | Two-person cross-verification complete · `queries.jsonl` and `difficulty.tsv` finalized · curation guide document |
| **M4** (W09-11) | Full run of condition A · stratified analysis by range for the 6 difficulty coordinates · per-condition metrics table produced | Full runs of conditions B, C, D with 3 repeats · abstention flip rate computed · log-based root-cause tracing | Qualitative failure mode classification · annotated wrong-answer cases · review per stratification range |
| **M5** (W12-14) | `track_ml-baselines` module cleanup · result reproduction scripts · one reproducible example notebook | `track_agent` and `track_agent/perturb` directory cleanup · run examples and cost guidance · demo | Documentation of the `track_curation` and `results/benchmark` directories · contribution guide for extending coordinates · open `good first issue` items |

> After finalizing the evaluation set in M3, the Curation track **moves on to qualitative failure mode
> classification in M4**. Reading and classifying wrong answers needs domain knowledge and has a low coding burden,
> so this track is the best fit to take it over.

### Four things we keep even if the schedule slips

| Item | Reason |
| --- | --- |
| W04 split freeze | If this slips, everything after it slips. The only point that cannot be undone |
| 3 repeated runs | Abstention flip rate is this project's unique contribution. Cutting to 1 run removes the reproducibility axis entirely, and half of the benchmark is gone |
| 60 queries + 6 coordinates | We can give up on 100, but 60 queries and 6 coordinates are the floor. The Curation track runs in parallel, so this does not affect the overall schedule |
| conformal prediction | Without it, there is no basis at all for calling anything "calibrated" |

### GitHub operating conventions

**Milestone.** `M1` through `M5` from the table above. Set the due dates exactly as listed.

**Branch, Issue, label, and PR rules** are written in one place only: [`CONTRIBUTING.md`](CONTRIBUTING.md).

**Weekly routine**

1. **Saturday 10:00, first half of the meeting.** Tidy up last week's Issues, carry unfinished items over to this
   week's label. Record `WXX.md` meeting notes using the [`docs/weekly/`](docs/weekly/) template
2. **Second half of the meeting.** Each track opens this week's Issues, assigns the `week/WXX` label and Milestone,
   pair work
3. **During the week.** Work through PRs, at least one reviewer. Close at the next Saturday meeting

### Repository structure

```text
abstain-dti/
├── track_ml-baselines/ # ML & Calibration track: ESM-2, XGBoost, conformal prediction, AlphaFold structure features, Boltz-2
├── track_agent/    # Agent track: ToolUniverse MCP, logging
│   ├── prompts/    # Prompts for conditions B, C, D (version controlled, frozen at W08)
│   └── perturb/    # Tool output perturbation harness (4 error types injected)
├── track_curation/ # Curation track: guide, coordinate computation scripts, two-person verification records
├── results/
│   └── benchmark/  # Deliverables: EVALUATION.md, queries.jsonl, difficulty.tsv
│       └── eval/   # Scoring scripts (risk-coverage, AURC, ECE, flip rate)
├── tests/          # pytest automated checks
├── notebooks/      # Reproducible examples (M5)
├── docs/           # Paper reviews, design documents, weekly progress logs
│   ├── literature/ # Paper summaries, HANDOFF, tool measurement records
│   ├── onboarding/ # W01 onboarding materials
│   └── weekly/     # Weekly meeting notes
└── environment.yml # mamba environment
```

Documents: `README.md`, `CONTRIBUTING.md`, `results/benchmark/EVALUATION.md`, `LICENSE-AUDIT.md`, weekly progress
logs. Templates: Issue (bug / task / question) and PR templates.

</details>

## ⚠️ Risks and mitigations

<details>
<summary>19 risks, from failing to secure a GPU to not making it to a paper (click to expand)</summary>
<br>

| Risk | Mitigation |
| --- | --- |
| Failing to secure a GPU | The minimum spine is designed to **complete on CPU only**. Stages 2 and 3 are split off as optional tasks |
| LLM API credits run out early | **Fix the budget cap as a number** in W01. Measure total cost in the pilot, then finalize the number of repeats (3). If over budget, shrink condition B and prioritize C and D |
| Latest Boltz version is closed source | Pin to open-weight v2.2.x and state the version in the results table. Stage 3's first priority is OpenFold3 (Apache 2.0), so the challenge experiment survives if one path is blocked |
| Too few targets with no PDB or low pLDDT | Check actual counts in W02. If too few, relax the filter with a pocket-level identity threshold |
| Agent does not give confidence as a number | Add **condition D** with an explicit abstention option, produce substitute confidence with self-consistency sampling |
| Dependency license conflicts | License audit in W05. On conflict, switch to a ToolUniverse-only setup |
| Citation errors and phantom citations | **Mandatory verification of every DOI** in W02 |
| Evaluation set quality degrades | Two-person cross-verification, guidelines finalized in W04 |
| Participant dropout | At least 2 people per track, mandatory documentation |
| 3D and structure representations do not improve performance | Keep 2D as the default condition, run structure only as ablation. **Report negative results as they are** |
| Results differ from expectations | The design makes confirming that something does not work a result as well |
| Exam periods or year-end overlap key weeks | Collect the whole team's schedules in W01 to check overlaps. Treat overlapping weeks as lost and absorb them with the W12 buffer |
| Mass parsing failures in the W09 full run | Expand the W08 pilot to **40 queries** |
| Target workshop is not held in 2027 | Secure 2-3 candidates when the ICLR workshop list is published in December. If all fall through, switch to an ISMB/ECCB 2027 poster |
| Not making it to a paper | **Releasing the repository is the primary goal.** All submission deadlines are after the cohort ends, so there is time to write the draft |
| Agent looks up the answer directly in a DB (search rather than prediction) | Exclude identifiers from the input. Report lookup cases separately using `direct_measurement_found` and the evidence log. Designate the contamination axis "after cutoff" range as the key range |
| LLM self-reported confidence clusters on discrete values, so conformal quantiles cannot be computed | Check the distribution in the W08 pilot. If it clusters, switch to the self-consistency score |
| Cost of condition E explodes (K samples × 3 repeats) | Limit E to 1 run + K internal samples, measure flip rate only on B, C, D. First produce the reduced version from the 3-repeat logs |
| Evaluation set is too small to split off a conformal calibration set | Use cross-conformal. Do not create extra calibration-only queries |
| Mixed affinity measurement types (Kd/Ki/IC50) distort comparisons | Keep a measurement type column, report per type. Convert Boltz-2 output to pAffinity before comparison |

</details>

## 🔁 Extension Track (after the cohort ends)

<details>
<summary>Challenge experiments, submission roadmap, external event schedule (click to expand)</summary>
<br>

The 12-week core aims **up to releasing the repository**. The items below are continued by those who want to stay
on. The main submission target, the ICLR 2027 workshop, has a deadline in February, so there is time after the
cohort ends in January.

| When | What | Owner |
| --- | --- | --- |
| 2027.01 | AlphaFold **Stage 3 challenge experiment.** OpenFold3 on 50 targets, optionally Boltz-2 on 200 pairs | Volunteers |
| 2027.01 | Check the ICLR 2027 workshop list, compile deadlines, page limits, and formats for 2-3 candidates | Leader + volunteers |
| 2027.01 | Write the arXiv preprint draft, then condense it to workshop format (4-8 pages). Consider in parallel once the ISMB proceedings deadline is confirmed | 2 writers |
| 2027.02 | **ICLR 2027 workshop submission** | 2 writers |
| 2027.04 | Submit ISMB/ECCB 2027 poster abstract (250 words). If the workshop paper is accepted, present on 4/29-30 | Those able to attend |

**Paper title (working)**: *Calibrated abstention in therapeutic AI agents, a difficulty-grounded benchmark
for drug-target prediction*

| Event | Dates | Relation to this project |
| --- | --- | --- |
| **ICLR 2027 workshops** (MLDD / GEM family) | Workshops 2027-04-29~30, Moscone Center, San Francisco. Deadline usually February | **Main submission target.** Main conference 4/26-28, with workshops on the last two days. ICLR 2026 held 40 workshops. Individual workshops and deadlines are confirmed after the list is published around December |
| **ISMB/ECCB 2027** | 2027-07, Bella Center, Copenhagen. Proceedings in January / abstracts around April (unconfirmed) | Secondary submission target. Proceedings require a public repository link and reproducibility, so **the W13 repository cleanup directly meets the submission requirements**. Posters are reviewed on a 250-word abstract alone |
| **4th AI Drug Discovery Competition (4th JUMP AI)** | Finals 2026-09-07~10-02, results 11-06 | The topic overlaps exactly, but the finals conflict with Phase 1. Not participating this cohort, deferred to the next round |
| **2027 AI Co-Scientist Challenge Korea** | Announcement expected in December of the previous year | Could apply to Track 2 (science and technology AI agent development) with this project's deliverables. An extension path after the cohort ends |

The individual ICLR 2027 workshop deadlines and the ISMB/ECCB 2027 key dates were not public when this document was
written. **In W11 we will recheck both official sites and update the table above.**

</details>

## 📖 Appendix A. W02 assigned papers

<details>
<summary>23 papers in 5 groups. Starred papers are required reading for everyone (click to expand)</summary>
<br>

One paper per person. Starred papers are **required reading for everyone**.

**A-1. Agents and AI Scientists**

- Huang et al., **Autonomous biomedical research with an artificial intelligence agent** (*Science*, 2026).
  DOI [10.1126/science.adz4351](https://doi.org/10.1126/science.adz4351). The preprint title was "Biomni", and the
  title changed on journal publication. Latest SOTA agent, code and data public
- **ToolUniverse: An open platform for democratizing AI scientists** (arXiv 2509.23426). The infrastructure layer we
  will build on
- ★ Kapoor, Stroebl, Siegel, Nadgir, Narayanan, **AI Agents That Matter** (arXiv:2407.01502, 2024;
  **TMLR 2025** is the publication of record). Pitfalls of agent benchmarking and cost-controlled evaluation. **The
  direct basis for this project's evaluation design**

**A-2. Structure and affinity prediction**

- Abramson et al., **Accurate structure prediction of biomolecular interactions with AlphaFold 3** (Nature, 2024)
- ★ Karelina, Noh, Dror, **How accurately can one predict drug binding modes using AlphaFold models?**
  (*eLife* 12:RP89386, 2023). DOI [10.7554/eLife.89386.2](https://doi.org/10.7554/eLife.89386.2),
  <https://elifesciences.org/articles/89386>. Limits of using predicted structures for ligand binding. **The
  starting point of our hypothesis**
- Buttenschoen et al., **PoseBusters: AI-based docking methods fail to generate physically valid poses**
  (Chemical Science, 2024). How to question evaluation criteria
- **OpenFold3 technical report** and the 2026-03 training data release announcement. Current performance of fully
  open co-folding and the antibody-antigen weakness the consortium itself pointed out. The reference for the Stage 3
  experiment

**A-3. Benchmarks and data leakage**

- Huang et al., **Therapeutics Data Commons** (NeurIPS Datasets & Benchmarks, 2021). The basis of our data
- ★ Wallach & Heifets, **Most ligand-based classification benchmarks reward memorization rather than
  generalization** (JCIM, 2018). The original source for why cold splits are needed
- Chen et al., **Hidden bias in the DUD-E dataset leads to misleading performance of deep learning in
  structure-based virtual screening** (PLoS ONE, 2019)

**A-4. Calibration and selective prediction**

- Angelopoulos & Bates, **A gentle introduction to conformal prediction and distribution-free uncertainty
  quantification** (2021). The practical entry point, required reading before using MAPIE
- ★ Ovadia et al., **Can you trust your model's uncertainty? Evaluating predictive uncertainty under
  dataset shift** (NeurIPS, 2019). **A cold split is a dataset shift**
- ★ Xiong et al., **Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation
  in LLMs** (ICLR, 2024). <https://arxiv.org/abs/2306.13063>. Verbalized confidence is systematically
  overconfident. **Conditions B, C, and D all depend on LLM self-reported confidence, yet until now we had not a
  single reference supporting it**
- Rakhshaninejad et al., **Conformal prediction for uncertainty estimation in drug-target interaction
  prediction** (arXiv:2505.18890, 2025). The closest prior work to condition A. Compares across data split
  scenarios
- Guo et al., **On calibration of modern neural networks** (ICML, 2017). The source of ECE
- Supplementary: Tibshirani et al., *Conformal prediction under covariate shift* (NeurIPS, 2019); Geifman &
  El-Yaniv, *Selective classification for deep neural networks* (NeurIPS, 2017)

**A-5. Molecule and protein representations**

- Lin et al., **Evolutionary-scale prediction of atomic-level protein structure with a language model**
  (Science, 2023). ESM-2
- Su et al., **SaProt: Protein language modeling with structure-aware vocabulary** (ICLR, 2024).
  How to feed structure information as tokens
- van Kempen et al., **Fast and accurate protein structure search with Foldseek** (Nature Biotechnology, 2024).
  The source of the 3Di alphabet

**Supplementary references (optional)**

- Sui et al., **Medea: An AI agent for therapeutic reasoning across biological contexts** (bioRxiv, 2026).
  DOI 10.64898/2026.01.16.696667. The first version's title was "An omics AI agent for therapeutic discovery".
  The closest prior example of calibrated abstention
- Inoue et al., **DrugAgent: Reliable Multi-Agent Integration of Conflicting Biomedical Evidence for
  Drug-Target Interaction Assessment** (arXiv:2408.13378). An LLM multi-agent system applied directly to DTI that
  reports label stability across repeated runs. It is an early form of our flip rate, so **it must be cited in
  related work**
- **AssayBench** (2026). A counterexample showing domain specialization is not always the answer
- Passaro et al., **Boltz-2: Towards Accurate and Efficient Binding Affinity Prediction** (bioRxiv, 2025)
- Bran et al., **ChemCrow: augmenting large language models with chemistry tools** (Nature Machine Intelligence, 2024)
- Boiko et al., **Autonomous chemical research with large language models** (Nature, 2023)

> **Bibliographic details for 2026 publications are still in flux.** In W02 we **open and check each DOI and link
> directly** before adding it to the citation list.

</details>

---

## 📚 Archive

- Repository: <https://github.com/Pseudo-Lab/abstain-dti>
- Benchmark: `results/benchmark/queries.jsonl` · `results/benchmark/difficulty.tsv` *(finalized at M3)*
- Evaluation protocol: [`results/benchmark/EVALUATION.md`](results/benchmark/EVALUATION.md) *(finalized at M1)*
- Demo: `URL` *(M5)*
- Preprint: `URL` *(Extension Track)*
- Presentation: `URL` *(W14)*

| Date | Content | Link |
| --- | --- | --- |
| `2026.10.10` | Project kickoff | `URL` |
| `2026.11.06` | M1 · split protocol frozen | `URL` |
| `2026.12.04` | M3 · minimum spine complete | `URL` |
| `2026.12.25` | M4 · results frozen | `URL` |
| `2027.01.09` | M5 · final results shared · repo released | `URL` |

---

## Acknowledgement 🙏

This project runs as part of Pseudo-Lab Open Academy. Your participation and contributions make the 'Serendipity
Revolution' possible. Our deep thanks to everyone.

abstain-dti is developed as part of Pseudo-Lab's Open Research Initiative. Special thanks to our
contributors and the open source community for their valuable insights and contributions.

## About Pseudo Lab 👋🏼

[Pseudo-Lab](https://pseudo-lab.com/) is a non-profit organization focused on advancing machine learning
and AI technologies. Our core values of Sharing, Motivation, and Collaborative Joy drive us to create
impactful open-source projects. With over 5k+ researchers, we are committed to advancing machine learning
and AI technologies.

<h2>Contributors</h2>
<a href="https://github.com/Pseudo-Lab/abstain-dti/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Pseudo-Lab/abstain-dti" />
</a>
<br><br>

<h2>License</h2>

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

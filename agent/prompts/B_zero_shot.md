<!-- version: v0 (W04 draft, freeze at W08) -->
You are predicting drug-target interaction.
You have no access to external tools, databases, or literature search.
Answer using only your internal knowledge.

## Input
Target sequence: {protein_sequence}
Compound SMILES: {smiles}

## Task
Predict whether this compound binds this target.

## Output
Return ONLY valid JSON. No prose before or after.

{
  "binds": true | false,
  "confidence": <float 0.0-1.0>,
  "pAffinity": <float or null>,
  "reasoning": "<2-3 sentences>"
}

Field definitions:
- "binds": true if you predict pAffinity >= 6.0
  (Kd, Ki, or IC50 <= 1 uM), false otherwise.
- "confidence": your probability that "binds" is correct.
  0.5 = coin flip, 1.0 = certain.
- "pAffinity": predicted -log10(affinity in M). 9.0 = 1 nM, 6.0 = 1 uM.
  null if you cannot estimate.

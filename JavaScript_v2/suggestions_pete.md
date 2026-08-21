from pathlib import Path
import pypandoc

text = r"""# Brutal Manuscript Review

## Executive Summary
- Novelty: 9.5/10
- Mathematical idea: 9/10
- Execution: 7/10
- Writing: 8/10
- Evidence: 6.5/10
- Expected recommendation: **Major Revision**

## Major Issues

### 1. The paper proves something reviewers may consider intuitive
The burden is not proving that the intersection of a moving set and fixed set shrinks, but proving that existing climate adaptation literature reaches misleading conclusions because it ignores that intersection.

### 2. Generality is asserted more than demonstrated
The framework is presented as general, but only one empirical case (Hawaiian coffee) is analyzed. A second case study or synthetic demonstration would greatly strengthen the claim.

### 3. Elevation dependence
Because temperature is almost entirely explained by elevation within the study belt, reviewers may argue that both the terrain and thermal screens are largely measuring the same underlying variable.

### 4. Two competing papers
The manuscript alternates between:
- A general geometric theory.
- A Hawaiian coffee application.

The theory deserves its own stronger section before the case study.

### 5. Too much self-undermining
The manuscript repeatedly explains why statistics should *not* be over-interpreted. Keep the honesty, but move caveats into limitations instead of interrupting the narrative.

### 6. Novelty could be framed more aggressively
The contribution is **not** "terrain matters."

The contribution is:

> Adaptation opportunity is the intersection of a moving climatic suitability set and a fixed feasibility constraint.

Everything else is an illustration.

### 7. Figures carry too much of the argument
The mathematical framework should convince readers even without the figures.

### 8. Theory deserves greater prominence
Consider introducing formal propositions before Hawaii:
- Theorem
- Corollaries
- Conditions for contraction
- Boundary effects
- Hypsometric amplification

### 9. Discussion is too long
Later sections become repetitive after the main conclusion has already been established.

### 10. Title
"Moving Windows on Fixed Ground" is elegant but does not immediately communicate the scientific contribution.

---

# Strengths

- Strong conceptual abstraction.
- Honest treatment of limitations.
- Clearer methods than earlier drafts.
- Memorable core message:
  > Neither input shrinks; the intersection does.

---

# Suggested Revision Priorities

1. Separate theory from application.
2. Demonstrate generality beyond Hawaiian coffee.
3. Reduce emphasis on elevation dependence.
4. Explicitly distinguish the framework from constrained SDMs.
5. Shorten discussion.
6. Add formal mathematical propositions.
7. Lead with the conceptual advance rather than the case study.

---

# Journal Outlook

- Nature: Reject
- Nature Food: Borderline
- Global Change Biology: Good chance after revision
- Agricultural Systems: Strong
- Environmental Research Letters: Strong
- Proceedings of the Royal Society B: Possible with a more theoretical framing
"""
out=Path("/mnt/data/brutal_manuscript_review.md")
pypandoc.convert_text(text,"md",format="md",outputfile=str(out),extra_args=["--standalone"])
print(out)

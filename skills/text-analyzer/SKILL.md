# SKILL.md
---
name: text-analyzer
description: |
  Use this skill whenever the user provides a substantial body of text (over 300 words) and asks for it to be analyzed, summarized, or distilled into key points. This skill is highly useful for processing meeting transcripts, lengthy reports, articles, or email chains that contain critical information.
---

# Text Analysis and Summary Tool

This skill allows you to transform unstructured, long-form text into a clear, actionable, and easy-to-digest report. It does not just summarize; it analyzes, extracts, and structures the findings.

## Guide to Using the Skill

When triggered by a user's request to summarize or analyze a large text block, follow these steps:

1.  **Read the full context**: Understand the primary goal and the overall tone of the provided text.
2.  **Analyze the content**: Systematically review the text to identify the three core components: overall message, critical points, and things that need to happen next.
3.  **Structure the Output**: The output MUST strictly follow the required Markdown format provided below. Do not include any preamble or extra conversation outside of the structured report.

## Output Structure Requirement

ALWAYS use this exact template and markdown structure:

```markdown
# 📈 Analysis Report
## Executive Summary
[Provide a concise, 2-3 sentence high-level summary of the entire text. This is the "TL;DR" for the user.]
## Key Takeaways
*   [Takeaway 1: The most critical, non-negotiable point from the text.]
*   [Takeaway 2: Another important fact or finding.]
*   [Takeaway 3: A potential third point of focus or discussion.]
## Suggested Action Items
*   **[Owner/Department]:** [Specific, concrete action that needs to be taken. Be precise!]
*   **[Owner/Department]:** [Another specific, actionable next step. Who does it and what is it?]
## Sentiment Analysis
[Overall Sentiment: e.g., Positive - Excitement over new market opportunities. | Mixed - Concerns were raised, but goals were reiterated. | Negative - Clear roadblocks cited. | Neutral - Informational status update.]
```

## Best Practices
*   **Be Action-Oriented:** When listing Action Items, always specify *who* is responsible and *what* the action is. Vague items are unhelpful.
*   **Avoid Redundancy:** Do not simply repeat sentences from the source text. Rephrase the information into punchy, clear summaries.
*   **Tone Matching:** If the source text is highly technical, maintain a formal and technical tone in your summary. If it's casual, keep the tone somewhat conversational while remaining professional.

---
### Required Inputs:
The skill requires one input: the source text to analyze.
---
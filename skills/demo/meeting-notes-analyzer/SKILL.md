---
name: meeting-notes-analyzer
description: |
  Analyze raw meeting transcripts or rough notes to automatically generate a highly structured, actionable summary. Use this skill whenever the user provides meeting notes, transcripts, or unstructured discussion points and needs to know the key takeaways, decisions made, and who owns the next steps. Don't just summarize; structure it for immediate action.
compatibility: None
---
# Meeting Notes Analyzer

This skill takes unstructured text—like raw meeting transcripts, bulleted notes, or a lengthy email chain—and transforms it into a structured, concise, and actionable summary suitable for immediate distribution.

## Workflow

1.  **Analyze Content**: Read the provided meeting notes/transcript.
2.  **Identify Key Sections**: Extract the most crucial pieces of information:
    *   **Main Goal/Topic**: What was the meeting about?
    *   **Key Decisions Made**: What specific outcomes or consensus points were reached?
    *   **Action Items**: What tasks need to be done? This must include the *task* itself and the *owner*.
    *   **Next Steps/Follow-up**: What is the plan moving forward?
3.  **Generate Output**: Present the findings using the mandated structure detailed below.

## Output Structure

ALWAYS use this exact template and ensure the tone is professional and actionable.

# 📊 Meeting Summary: [Topic/Date]

## 🎯 Main Goal
[A single, clear paragraph stating the core purpose of the meeting.]

## ✅ Key Decisions
*   **Decision 1**: [Brief description of the decision.] (Agreed by: [Team/Participants])
*   **Decision 2**: [Brief description of the decision.] (Status: [Confirmed/Tentative])

## 🚀 Action Items (WHO does WHAT by WHEN)
| Owner | Action Item | Deadline (Optional) |
| :--- | :--- | :--- |
| [Name] | [Specific task to be completed] | [Date or N/A] |
| [Name] | [Specific task to be completed] | [Date or N/A] |

## ⏭️ Next Steps
[A brief overview of follow-up items and the planned next meeting topic.]

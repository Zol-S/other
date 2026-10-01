You are an expert in analysing institutional meeting transcripts, especially Senate, board, committee, and academic governance meetings.

Your task is to analyse the supplied transcript and extract structured information about:

1. conversations and substantive discussions;
2. voting;
3. discussion segments;
4. concepts discussed;
5. actors participating in the discussions;
6. each actor's attitude toward each concept;
7. evidence supporting each attitude;
8. confidence in each extracted relationship;
9. an actor × concept attitude matrix summarising the results.

The analysis must be based exclusively on the supplied transcript. Do not use external knowledge or assumptions about the people, organisations, political positions, or events mentioned in the transcript.

---

# 1. Conversation detection

Set **`contains_conversation`** to **`1`** only when the text contains an actual substantive exchange between two or more actors.

Examples include:

- questions and answers;
- comments followed by responses;
- disagreement or agreement;
- discussion of a proposal;
- arguments and counterarguments;
- participants challenging or clarifying another participant's statement;
- participants expressing different views on the same issue.

Set **`contains_conversation`** to **`0`** if there is no substantive exchange.

Do NOT treat the following by themselves as a conversation:

- a speech or presentation by one person;
- reading an announcement;
- listing agenda items;
- procedural instructions;
- introductions;
- ceremonial remarks;
- simple acknowledgements such as "thank you";
- mentioning another person's opinion without engaging with it.

A meeting can contain voting without containing substantive conversation.

---

# 2. Voting detection

Set **`contains_voting`** to **`1`** when the text contains an actual or explicitly initiated voting procedure.

Examples include:

- a request to vote;
- a vote on an agenda item;
- a recorded vote or voting result;
- a motion being put to a vote;
- approval or rejection through voting;
- written or electronic voting;
- yes/no voting;
- abstentions;
- an explicit reference to a previous written vote.

Set **`contains_voting`** to **`0`** when voting is not present.

Do not infer voting merely because a decision, approval, adoption, or rejection is mentioned.

There must be textual evidence that voting occurred, was requested, or was explicitly referred to as voting.

---

# 3. Discussion segments

Divide the transcript into meaningful **`discussion_segments`**.

A discussion segment is a contiguous portion of the transcript dealing with one substantive issue, concept, proposal, question, or disagreement.

Do NOT create one segment for every speaker turn.

If several speakers discuss the same issue consecutively, group their contributions into one segment.

Start a new segment when the discussion clearly changes to another substantive issue.

For every segment provide:

- a unique **`segment_id`**;
- a short title;
- the approximate location in the transcript;
- the main topic;
- a concise summary;
- the actors participating;
- the concepts discussed.

Example:

{
"segment_id": "S3",
"title": "Postponement of the V4 conference",
"location": "Pages 4-10",
"summary": "Participants discuss the postponement of the conference, political sensitivity, academic freedom, institutional neutrality, and the role of university management.",
"actor_ids": ["A1", "A2", "A3"],
"concept_ids": ["C1", "C2", "C3"]
}

---

# 4. Concepts

A concept is a substantive issue, proposal, principle, decision, event, or topic that participants discuss.

Do not create a separate concept for every sentence.

Group semantically related statements into a single concept.

Prefer concise, meaningful concept names such as:

- "Postponement of the conference"
- "Academic freedom"
- "Political neutrality"
- "Political sensitivity of the research"
- "Scientific integrity"
- "Institutional reputational risk"
- "Political interference"
- "University censorship"

Do not automatically treat every noun mentioned in the transcript as a concept.

A concept should be something that participants actually discuss, evaluate, question, support, reject, or otherwise engage with.

If the same concept appears in multiple discussion segments, normally create only one concept and link it to all relevant segments.

Create separate concepts only when the issues are substantively distinct.

---

# 5. Actors

An actor is a person or clearly identifiable group that meaningfully participates in a discussion.

Use the actor's full name when available.

Examples:

- "Bruno van Pottelsberghe"
- "Eszter Kirs"
- "Kata Apáti-Tóth"
- "Mánuel László Mágó"
- "The Senate"

Do not include people who are merely mentioned but do not participate meaningfully.

Distinguish individuals from groups or institutions when the transcript supports this distinction.

Every actor receives a unique **`actor_id`**.

---

# 6. Actor-concept relationships

For every actor who meaningfully addresses a concept, create an **`actor_attitude`** relationship.

An actor does NOT need to have a relationship with every concept in a discussion segment.

Only create a relationship when the transcript contains evidence that the actor actually addressed the concept.

Each relationship must contain:

- actor;
- concept;
- attitude;
- confidence;
- evidence;
- discussion segment(s).

---

# 7. Attitude classification

Classify the actor's expressed attitude toward each concept using exactly one of:

### `"positive"`

The actor explicitly:

- supports;
- approves;
- agrees with;
- endorses;
- defends;
- favors;

the concept.

### `"negative"`

The actor explicitly:

- opposes;
- criticizes;
- rejects;
- objects to;
- condemns;
- expresses an unfavorable view;

toward the concept.

### `"neutral"`

The actor discusses, describes, explains, questions, or refers to the concept without expressing a clearly positive or negative attitude.

### `"mixed"`

The actor expresses both favorable and unfavorable views toward the same concept.

For example:

"I understand why the conference was postponed, but I strongly disagree with postponing it."

This is **`"mixed"`** toward the concept of postponement.

### `"unclear"`

There is insufficient evidence to reliably determine the actor's attitude.

Do not guess.

---

# 8. Important distinction: attitude vs factual statement

Do not classify an actor as positive or negative simply because they make a factual claim.

For example:

"The conference was postponed."

→ **`"neutral"`**

"The postponement was completely unnecessary."

→ **`"negative"`**

"I believe postponing the conference protects the university."

→ **`"positive"`**

Similarly:

"The university has academic freedom."

is not automatically positive toward the concept of academic freedom.

The actor must express an evaluative position for the attitude to be positive or negative.

---

# 9. Important distinction: object of the attitude

Be precise about WHAT the actor is expressing an attitude toward.

For example, an actor might:

- support academic freedom;
- oppose postponing a conference;
- support postponing the conference;
- oppose political interference;
- criticize the university's reasoning for postponing the conference.

These are different relationships.

Do not collapse them into a general statement such as:

"Actor X is positive about the conference."

Identify the actual concept being evaluated.

---

# 10. Complex and conditional positions

When an actor expresses a nuanced or conditional position, analyse the individual concepts separately.

Example:

"I agree that the topic is politically sensitive, but I don't agree that this justifies postponing the event."

Possible extraction:

- Political sensitivity → positive/agreeing
- Postponement of the event → negative

Do not automatically classify the entire speaker's contribution as simply positive or negative.

---

# 11. Evidence

Every actor-concept relationship MUST include evidence.

Evidence should:

- come exclusively from the supplied transcript;
- be a concise quotation or faithful paraphrase;
- directly support the assigned attitude;
- identify the relevant statement or argument.

Keep quotations short.

If several statements support the classification, provide a concise synthesis rather than reproducing a long passage.

Example:

{
"attitude": "negative",
"evidence": "Eszter describes the postponement as censorship based on political grounds and questions why an academic event should be postponed because of political considerations."
}

Do not invent evidence.

---

# 12. Confidence score

Assign a numerical **`confidence`** between **`0`** and **`1`** to every actor-concept relationship.

The confidence score represents how strongly the transcript supports the extracted relationship and attitude.

Use the following guidance:

- **`0.90–1.00`**: explicit and unambiguous statement;
- **`0.75–0.89`**: strong evidence, with minor interpretation required;
- **`0.50–0.74`**: plausible interpretation, but somewhat ambiguous;
- **`0.25–0.49`**: weak evidence;
- **`0.00–0.24`**: very little evidence.

Use **`"unclear"`** when evidence is insufficient rather than assigning an artificially high confidence score.

The confidence score measures confidence in the **extraction**, not whether the actor's statement is factually correct.

For example:

"I strongly oppose postponing the conference."

→ attitude: **`"negative"`**
→ confidence: approximately **`0.98`**

"I understand the concern, although I'm not sure postponement is necessary."

→ attitude: **`"mixed"`**
→ confidence: approximately **`0.85`**

---

# 13. Changes of position

If an actor's attitude toward a concept changes during the transcript, do NOT hide the change.

Create separate actor-concept relationships for the relevant discussion segments.

For example:

- S1: Actor supports proposal.
- S4: Actor later expresses concerns about proposal.

Represent this as separate segment-level observations and, where appropriate, an overall relationship marked **`"mixed"`**.

The output should preserve the evolution of the discussion.

---

# 14. Discussion-level extraction

For every discussion segment, identify:

- participating actors;
- concepts discussed;
- actor-concept attitudes;
- supporting evidence;
- confidence scores.

An actor can participate in a segment without expressing an attitude toward every concept in that segment.

Do not force missing relationships.

---

# 15. Actor × concept attitude matrix

In addition to the detailed evidence-based relationships, create an **`attitude_matrix`**.

The matrix must have:

- one row for each actor;
- one column for each concept;
- the corresponding attitude in each cell.

Use these values:

- **`positive`**
- **`negative`**
- **`neutral`**
- **`mixed`**
- **`unclear`**
- **`not_discussed`**

Use **`"not_discussed"`** when there is no evidence that the actor addressed the concept.

Do NOT use **`"neutral"`** simply because no attitude was found.

This distinction is important:

- **`"neutral"`** = the actor discussed the concept but did not express a positive or negative attitude.
- **`"not_discussed"`** = there is no evidence that the actor addressed the concept.

Example:

{
"attitude_matrix": {
"actors": [
{
"actor_id": "A1",
"actor": "Bruno van Pottelsberghe",
"attitudes": {
"C1": "positive",
"C2": "neutral",
"C3": "negative"
}
},
{
"actor_id": "A2",
"actor": "Eszter Kirs",
"attitudes": {
"C1": "negative",
"C2": "positive",
"C3": "not_discussed"
}
}
]
}
}

The matrix is a summary of the detailed actor-concept relationships.

Do not introduce information into the matrix that does not exist in the detailed evidence.

---

# 16. Matrix confidence

For every matrix cell that is not **`"not_discussed"`**, also provide the confidence score and the relevant discussion segment IDs.

Use a structured matrix representation rather than only a string value.

For example:

{
"actor_id": "A1",
"actor": "Bruno van Pottelsberghe",
"attitudes": {
"C1": {
"attitude": "positive",
"confidence": 0.94,
"segment_ids": ["S3"]
},
"C2": {
"attitude": "neutral",
"confidence": 0.88,
"segment_ids": ["S3", "S4"]
},
"C3": {
"attitude": "not_discussed",
"confidence": null,
"segment_ids": []
}
}
}

This makes the matrix traceable back to the original discussion.

---

# 17. Overall concept summary

For every concept, provide a concise summary of the positions expressed by the different actors.

Do not determine which actor is correct.

Do not rank actors.

Do not determine which position is preferable.

The purpose is to represent the discussion faithfully.

Example:

{
"concept_id": "C1",
"concept": "Postponement of the conference",
"summary_of_positions": "Some participants describe the postponement as a reasonable temporary measure to avoid political sensitivity, while others view it as inappropriate interference with an academic event."
}

When positions are disputed, attribute them to the relevant actors rather than presenting a disputed interpretation as an objective fact.

---

# 18. Voting details

If **`contains_voting`** is **`1`**, identify the voting events where possible.

For each voting event provide:

- **`vote_id`**;
- the subject being voted on;
- the relevant discussion segment;
- the stated proposal/resolution;
- any explicitly reported result;
- explicitly identified individual votes or abstentions;
- whether the result is known.

Do not invent vote counts.

For example:

{
"vote_id": "V1",
"subject": "Amendment of the Rules of Procedure of the Senate",
"segment_id": "S2",
"proposal": "Amend the Rules of Procedure in Hungarian and English.",
"result": "not explicitly reported",
"individual_votes": [
{
"actor_id": "A3",
"vote": "abstain"
}
]
}

If a vote is mentioned but the result is not available, use:

**`"result": "not explicitly reported"`**

Do not infer the result from subsequent statements unless the transcript explicitly establishes it.

---

# 19. Final JSON schema

Return ONLY valid JSON.

Do not return Markdown.

Do not return explanations outside the JSON.

Use exactly this overall structure:

{
"contains_conversation": 0,
"contains_voting": 0,

"discussion_segments": [
{
"segment_id": "S1",
"title": "Short discussion title",
"location": "Approximate location",
"summary": "Concise summary",
"actor_ids": ["A1", "A2"],
"concept_ids": ["C1", "C2"]
}
],

"actors": [
{
"actor_id": "A1",
"actor": "Full name"
}
],

"concepts_discussed": [
{
"concept_id": "C1",
"concept": "Concept name",
"description": "Concise description",
"summary_of_positions": "Concise neutral summary of the positions expressed",
"discussion_segment_ids": ["S1"],

```
  "actor_attitudes": [
    {
      "actor_id": "A1",
      "attitude": "positive",
      "confidence": 0.95,
      "evidence": "Concise supporting evidence",
      "discussion_segment_ids": ["S1"]
    }
  ]
}

```

],

"attitude_matrix": {
"actors": [
{
"actor_id": "A1",
"actor": "Full name",
"attitudes": {
"C1": {
"attitude": "positive",
"confidence": 0.95,
"segment_ids": ["S1"]
},
"C2": {
"attitude": "not_discussed",
"confidence": null,
"segment_ids": []
}
}
}
]
},

"voting_events": [
{
"vote_id": "V1",
"subject": "Subject of vote",
"segment_id": "S1",
"proposal": "Proposal being voted on",
"result": "Result if explicitly stated, otherwise 'not explicitly reported'",
"individual_votes": [
{
"actor_id": "A1",
"vote": "yes | no | abstain | unclear"
}
]
}
]
}

---

# 20. Empty-value rules

If there is no substantive discussion:

- **`contains_conversation`** = **`0`**
- **`discussion_segments`** = **`[]`**
- **`concepts_discussed`** = **`[]`**
- **`attitude_matrix.actors`** = **`[]`**

If there is no voting:

- **`contains_voting`** = **`0`**
- **`voting_events`** = **`[]`**

If there is discussion but no identifiable individual actors:

- use the identifiable group/institution as the actor where appropriate.

If a concept was discussed but an actor's attitude cannot be determined:

- use **`"unclear"`**.

If an actor did not discuss a concept:

- use **`"not_discussed"`** in the matrix.

Never substitute **`"neutral"`** for **`"not_discussed"`**.

---

# 21. Final quality-control checks

Before returning the JSON, verify:

1. Every **`concept_id`** referenced by a discussion segment exists in **`concepts_discussed`**.
2. Every **`actor_id`** referenced anywhere exists in **`actors`**.
3. Every segment ID referenced by an actor-concept relationship exists in **`discussion_segments`**.
4. Every concept in the attitude matrix exists in **`concepts_discussed`**.
5. Every actor in the attitude matrix exists in **`actors`**.
6. Every matrix attitude is supported by a corresponding detailed actor-concept relationship.
7. **`"not_discussed"`** is used when there is no evidence of discussion.
8. **`"neutral"`** is used only when the actor actually discusses the concept without expressing a positive or negative attitude.
9. Every positive, negative, mixed, or unclear classification has supporting evidence.
10. Every confidence score is between **`0`** and **`1`**.
11. No external knowledge has been introduced.
12. No actor has been assigned an attitude merely because another actor expressed that attitude.
13. No voting result has been invented.
14. The JSON is syntactically valid.

## Text to analyse

—————

[INSERT TRANSCRIPT HERE]

—————

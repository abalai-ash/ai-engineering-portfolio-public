# Example Outputs

This file keeps a few test questions for the first version of the RAG Research Assistant.

## Example question 1

Question:

```text
Why should conclusions stay cautious when evidence is incomplete?
```

Expected source:

```text
public_science_notes.txt
```

## Example question 2

Question:

```text
Why should API keys not be committed to GitHub?
```

Expected source:

```text
cloud_notes.txt
```

## Example question 3

Question:

```text
Why are visual checks useful for sensor data?
```

Expected source:

```text
sensor_notes.txt
```

## First test notes

The first local test worked with the three sample questions.

The strongest result for the incomplete evidence question came from:

```text
public_science_notes.txt
```

The strongest result for the API key question came from:

```text
cloud_notes.txt
```

The strongest result for the visual checks question came from:

```text
sensor_notes.txt
```

The script also returned a few extra chunks when they shared common words with the question. I updated the retrieval filter so chunks need a score of at least 2 before they are shown. This made the first test cleaner, but there is still room to improve ranking later.

## Current test result

The first version passed all 5 source-matching evaluation questions.

```text
Evaluation complete: 5/5 passed
```

The short-answer step is still simple. It uses the top retrieved chunk and returns a basic answer that can be checked against the source text.

## Sample output summaries

### Incomplete evidence question

Question:

```text
Why should conclusions stay cautious when evidence is incomplete?
```

Top source:

```text
public_science_notes.txt
```

Short answer:

```text
Conclusions should stay cautious when evidence is incomplete because the explanation may not fully fit the available data yet.
```

### API key question

Question:

```text
Why should API keys not be committed to GitHub?
```

Top source:

```text
cloud_notes.txt
```

Short answer:

```text
API keys should not be committed to GitHub because they are secrets. They should be kept separate from the code, often with environment variables.
```

### Sensor data question

Question:

```text
Why are visual checks useful for sensor data?
```

Top source:

```text
sensor_notes.txt
```

Short answer:

```text
Visual checks are useful because plots can show problems like sudden jumps, flat sections, or missing measurements that one number may hide.
```

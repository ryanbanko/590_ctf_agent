# References and clarifications

## Sources used

| Source | Used for |
| --- | --- |
| [CTFTiny](https://github.com/NYU-LLM-CTF/CTFTiny), revision `f1c9531672c45b24b7fb5f3aa44a7ac33d3602f8` | Benchmark challenges and index |
| [NYU CTF Bench](https://github.com/NYU-LLM-CTF/NYU_CTF_Bench) and the [`nyuctf`](https://pypi.org/project/nyuctf/) package 1.1.1 | Challenge loading (`CTFDataset`, `CTFChallenge`) |
| [NYU CTF Bench documentation](https://nyu-llm-ctf.github.io/docs/) | Setup and challenge conventions |
| [nyuctf_agents Dockerfile](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/Dockerfile) (MIT, see [docker/NYU-LICENSE](../docker/NYU-LICENSE)) | Solver image installation recipe, reused in `docker/solver.Dockerfile` |
| [Duke AI Gateway developer guide](https://ai.colab.duke.edu/colab-ai-blog/all-blogs/getting-started-with-dukes-ai-gateway-a-developers-guide/) | Model access through the gateway |
| [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling) and [reasoning](https://developers.openai.com/api/docs/guides/reasoning) guides | Responses API tool calls and reasoning settings |
| [Langfuse Python SDK](https://langfuse.com/docs/observability/sdk/overview) and [OpenAI integration](https://langfuse.com/integrations/model-providers/openai-py) | Tracing and trace export |

No code from the NYU reference agents other than the Dockerfile recipe is included.

## Course clarifications

Professor's replies, as reported by the team member who asked:

- On whether the "Implementation Guide" meant the CTFTiny and NYU CTF Bench
  documentation:
  > Thanks. Yeah it is basically the implementation guide there.
- **November 4**, on runtime package downloads:
  > Yes. The intention of that statement is more along the lines of you don’t want the
  > agent looking up the ctf tiny answers and submitting them. But access to download
  > packages is perfectly acceptable
- **November 6:**
  > 1. Using the challenge repository’s compose files and checking flags privately in your controller is fine. I had originally intended to provide a subset of the dataset, but that hasn’t been created yet.
  > 2. JSON trace exports from Langfuse are fine.
  > 3. Your approach of developing on separate CTFTiny challenges and holding ten out for evaluation works.

**Team decision (November 8), not a professor clarification:** the assignment says to
stop a run when an action reaches outside the permitted environment. The team's reading
is that a connection the firewall prevented may receive a corrective response and the
attempt may continue within scope. The first prevented connection in an attempt returns
an error to the agent; a second one ends the attempt.

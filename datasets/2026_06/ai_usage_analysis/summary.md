# AI-usage analysis — 2026_06

> **AI-usage detection measures a lower bound** (disclosed/configured/automated traces only). With n=55 the comparisons below are exploratory and **correlational, not causal** — AI tooling co-varies with project recency and activity.

## Adoption

- **24/55 (44%)** repos show **AI-assisted development**
- **2/55 (4%)** repos **ship an LLM product feature**

## Dev tools (repos)

```
          tool  repos
   claude_code     20
github_copilot     12
     agents_md      6
  openai_codex      1
         jules      1
         devin      1
           roo      1
    gemini_cli      1
           mcp      1
        cursor      1
```

## Product LLM providers (repos)

```
 provider  repos
   openai      2
anthropic      1
   cohere      1
 deepseek      1
     groq      1
```

## Evidence sources (repos, by strength tier)

```
        source  repos   tier
       pr_body      9 medium
      workflow      3 medium
    dependency      2 medium
commit_trailer     20 strong
          file     14 strong
     pr_author      9 strong
 commit_author      6 strong
```

## Adoption timeline (first AI-dev signal)

```
quarter  repos_first_seen  cumulative
 2025Q1                 1           1
 2025Q2                 6           7
 2025Q3                 2           9
 2025Q4                 3          12
 2026Q1                 7          19
 2026Q2                 4          23
```

## Adopters vs non-adopters (medians; Mann-Whitney U)

```
            metric  adopter_median  nonadopter_median  adopter_n  nonadopter_n  mannwhitney_p
     total_commits          575.00             272.00         24            31         0.0112
    num_developers           11.00               5.00         24            31         0.0022
             stars            7.00               3.00         24            31         0.0780
 health_percentage           50.00              50.00         24            31         0.3262
         age_years            3.79               3.47         24            31         0.9324
bus_factor_no_bots            1.00               1.00         23            31         0.1038
```

## Most AI-active repos

```
                 repo_full_name                                      dev_ai_tools  ai_coauthored_commit_count  ai_authored_commit_count  ai_agent_pr_count         first_dev_ai_date
  meshtastic/Meshtastic-Android   agents_md;claude_code;gemini_cli;github_copilot                         199                         7                  8 2025-05-22T20:54:09+00:00
            meshtastic/firmware          agents_md;claude_code;github_copilot;mcp                         173                         2                  7 2025-04-07T10:46:22+00:00
       codeforjapan/BirdXplorer                             claude_code;devin;roo                          52                        15                  7 2025-04-28T02:30:45+00:00
             openlegaldata/oldp                                claude_code;cursor                          62                         0                  0 2026-01-13T16:23:48+00:00
CivicTechWR/go-train-group-pass                        claude_code;github_copilot                          42                         1                 11 2025-10-08T16:33:13+00:00
                 meshtastic/web                        claude_code;github_copilot                          41                         1                  1 2025-05-27T11:36:16+00:00
   CodeForAfrica/PromiseTracker agents_md;claude_code;github_copilot;openai_codex                          11                         0                  0 2025-09-05T09:37:54+00:00
              choruslabs/chorus                                    github_copilot                           9                         0                  1 2025-06-08T17:33:58+00:00
```

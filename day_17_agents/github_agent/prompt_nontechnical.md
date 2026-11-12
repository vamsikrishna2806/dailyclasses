# GitHub Agent — Plain English Guide

## What does this agent do?

This agent searches GitHub for you and finds the best open-source projects related to any topic. GitHub is the world's largest code hosting platform, and this agent helps you discover the most popular and useful repositories without needing to visit the website.

## How to talk to it

Just ask naturally:

- "Find top Python machine learning repos"
- "Show me the best React component libraries"
- "What are the most popular JavaScript frameworks on GitHub?"
- "Find beginner-friendly open source projects"
- "Show me repos for learning Rust"
- "Find the top data visualisation tools"

## How it works (simple version)

1. You describe what you're looking for
2. The agent searches GitHub's public repository database
3. It retrieves the top 5 most-starred results
4. It presents them with descriptions and links

## What you get back for each repository

- **Repository name** and the owner/organisation
- **Star count** (⭐) — a measure of how popular it is
- **Programming language**
- **Description** of what it does
- **Link** to the GitHub page

## Example conversation

> **You:** Find top Python data science repos
>
> **Agent:** **Top GitHub Repositories for "Python data science"**
>
> 1. ⭐ **pandas** (41k stars) · Python
>    Powerful data analysis and manipulation library
>    🔗 https://github.com/pandas-dev/pandas
>
> 2. ⭐ **numpy** (26k stars) · Python
>    The fundamental package for scientific computing in Python
>    🔗 https://github.com/numpy/numpy
>
> 3. ...

## Good to know

- Completely free — no GitHub account needed
- Returns results sorted by **star count** (most popular first)
- Works for any programming language, framework, or topic
- You can be specific: "Python REST API framework" or broad: "machine learning"

## Limitations

- Shows public repositories only (not private ones)
- Limited to 60 searches per hour (unauthenticated rate limit)
- Very new repositories may not appear if they don't have many stars yet
- Results are ranked by stars, not necessarily by quality or maintenance status

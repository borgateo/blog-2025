---
title: Teaching your AI to remember
description: The system I built with Obsidian to give AI a persistent memory across sessions.
author: Matteo
date: 2026-04-04T10:00:00.000Z
cover: snow-trees.jpg
coverTitle: Cogne, Italy (January 2026)
language: en
tags:
  - AI
  - productivity
  - tools
  - obsidian
---

Every time I open a new AI chat, I start from zero.

No context about the project I'm working on. No memory of last week's decisions. No idea what I prefer or what I've already tried. The model is brilliant, but completely amnesiac.

For one-off questions that's totally fine. But for side projects that stretch over weeks or months, it gets old fast. I was spending the first ten minutes of every session re-explaining myself, and that's before actually getting anything done.

## **The obvious fix**

Paste context manually. "Here's the project. Here's what we've done so far. Here's what I want today." It works! Once. But then you're maintaining a growing text file somewhere, updating it by hand, hoping it's current. It really doesn't scale.

## **The actual fix: Obsidian as a memory layer**

I use [Obsidian](https://obsidian.md) as my personal knowledge base. Markdown files, local-first, no proprietary format. I organize it with the [PARA method](https://fortelabs.com/blog/para/) (Projects, Areas, Resources, Archive), which gives everything a clear home.

At the end of 2025 I started using it as the persistent memory layer between me and my AI assistant, and it's been genuinely great.

**Project notes as context.** Every side project gets a folder. Architecture decisions, open questions, design constraints, relevant links, all in one place. When I start an AI session I load that file and the AI has full context immediately, without me repeating myself.

**Atomic notes as a knowledge base.** Ideas, concepts, things I've learned, I extract them as standalone notes (atoms), each self-contained. Over time they link to each other. When I'm working on something related I pull in exactly what I need.

**Session logs.** At the end of each working session I save a short structured note: what we did, decisions made, open items, next steps. The next session starts by reading it. Zero re-explaining.

## **The `rules/` directory**

Claude Code (the AI I use for coding) reads a `~/.claude/rules/` directory at the start of every session. I keep a few files there:

- `working-style.md` — how I like to work: small focused PRs, front-load context before touching code, specific formatting preferences
- `code-review-preferences.md` — comment weight format, PR title conventions, pre-PR checklist
- one file for whatever project I'm currently focused on

These load automatically. The AI knows my preferences before I type a single word. It's one of those tiny things that saves a surprising amount of friction over time.

## **Skills: teaching the AI new tricks**

Beyond static preferences, you can define reusable workflows as skills. Think of them as slash commands that trigger a specific sequence of actions.

I have a `/dismiss` skill that saves a structured session log at the end of every coding session, a `/summon` skill that loads context from the previous one, and a `/query` skill that answers questions by synthesizing content across multiple vault notes at once. When I type `/dismiss`, the AI knows exactly what to do: write the log, update the right file, note the open items, close the session cleanly.

Once written, skills behave like keyboard shortcuts for complex workflows. You stop explaining the procedure each time and just invoke it.

## **Agents in parallel**

This one surprised me the most.

Claude Code can run multiple agents simultaneously on independent tasks. While one agent is researching a library, another is reviewing recent changes, and a third is running through a checklist. They don't share state, so there's no interference. You get back three completed tasks in roughly the time it would take to finish one.

I use this mostly for pre-PR reviews now: one agent checks code style and project conventions, another hunts for silent failures in error handling, a third checks test coverage. I dispatch all three at once, go make coffee, and come back to a full picture of what needs fixing before I push.

It's a meaningful shift in how you can think about working with AI. Less sequential, more like delegating to a small team.

## **The compounding effect**

This is the part I didn't anticipate when I started.

Every session leaves something behind. A decision that was made, a pattern that was captured, a preference that was noted. The next session starts slightly further ahead than the one before. Not by a lot, but consistently.

After a few months, the difference between "working with AI from scratch" and "working with AI on top of this system" is genuinely noticeable. The system carries context I no longer need to hold in my own head.

Dan Shipper's [Compound Engineering](https://every.to/guides/compound-engineering) framework describes this as the Plan -> Work -> Review -> Compound loop. The Compound step is the one most people skip: extract the insight from what you just did and feed it back into the system so the next session starts further ahead. Obsidian is where that compounding happens for me.

## **One thing worth being explicit about**

This system stores personal workflow patterns, side project context, and things I've learned. It's not a place for proprietary code, team data, or anything that belongs to an employer. That boundary is worth drawing deliberately, and early.

## **How to start**

1. Install Obsidian. Start with PARA: four folders (Projects, Areas, Resources, Archive).
2. Create a folder for each active side project. Keep a running note there: decisions, open questions, what's next.
3. At the end of each AI session, write a short summary. Date it. What was done, what's next.
4. If you use Claude Code, create `~/.claude/rules/` and add a `working-style.md` with your preferences.

That's genuinely all you need to start. No automation, no plugins required. Just the habit of leaving something behind at the end of each session.

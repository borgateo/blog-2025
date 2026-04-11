---
title: The expert always knew more than you. Not anymore.
description: How I used AI to fix two problems at home that the professionals couldn't explain — and what that says about expertise.
author: Matteo
date: 2026-04-11T10:00:00.000Z
cover: gambiarra.webp
coverTitle: Fortaleza, Brazil
language: en
tags:
  - AI
  - diy
  - tools
---

For the past few months I've been using AI to fix things around the house that the professionals couldn't (or wouldn't) figure out. Two examples from real life.

## **The pool that wouldn't come clean**

The guy who maintains my pool has a fixed routine: throw in some aluminum sulfate, wait for the algae to clump and sink to the bottom, vacuum it all up the next day. It works. When I asked him why he does it, he said: “Because everyone does it”.

That was fine until the rainy season hit. Heavy rains dropped the pH of the water, and suddenly the routine stopped working. The pool was green again two days after treatment. Neither of us knew why.

I described the situation to GPT: pool size, what treatments were being used, how much it had been raining. The diagnosis came back quickly: 

> Low pH makes the whole chemical system unstable. Chlorine loses effectiveness, the flocculant doesn't bind properly. Fix the pH first, then everything else will work.

The steps:

1. test the pH;
2. raise it with soda ash until is stable again;
3. do a chlorine shock;
4. apply the aluminum sulfate;

I bought the test kit and the chemicals, followed the steps, and the pool was clear within 48 hours.

I explained it to the pool guy afterward. He was skeptical at first. We went through it together and now he knows how to handle pH drops during rain season. A small knowledge transfer that will probably save him a headache or two with other pools in the block.

<div align="center">❉</div>

## **The circuit breaker that didn't trip**

I've loved taking electronics apart since I was a kid, and I still like tinkering with electrical stuff. One afternoon I trusted my multimeter a bit too much while working on a 110V circuit, got a shock, and the RCD (the safety device that's supposed to cut power immediately) didn't trip.

That was concerning. At 110V it's unpleasant but manageable. At 220V, a failure like that is a different conversation.

I took photos of the electrical panel, the RCD, the house wiring layout, and fed everything to Claude and Gemini in parallel. Both pointed at the same thing: grounding resistance too high. When the ground path has too much resistance, the RCD can't detect the fault properly and doesn't trip.

I called an electrician to measure. Result: 78 ohm. The Brazilian standard (ABNT NBR 5410) requires it to be below 25 ohm.

The reason: I live on a sand dune. Sand has high resistivity, the opposite of what you want for a good electrical ground. The fix was to drive additional copper grounding rods into the soil to reduce resistance. I researched the materials, bought what was needed, planned the whole intervention, then had the electrician execute it. His bill was low because I wasn't paying him to diagnose anything.

That investigation also turned up something else: I'd had electronics frying at home for months. AI explained why:

> Lightning doesn't have to hit your house to damage things. A strike within a few hundred meters sends a voltage spike through the local grid, and that spike is enough to destroy sensitive electronics. The solution is a surge protector at the panel. But you can't install one safely without proper grounding. 

So fixing the ground first wasn't just about the RCD: it was the prerequisite for everything else.

<div align="center">❉</div>

## **The part that actually surprised me**

I talked to four electricians before finding one I trusted. Some showed up without a multimeter. One sent a quote ten times higher than what I ended up paying, with no explanation of what the problem actually was. Another sent a very detailed cost breakdown — looked professional at first glance. I fed it to an LLM and it flagged it immediately: the technical terms were unrelated to the actual problem, strung together to sound credible to someone who didn't know better.

The AI had helped me prepare a list of questions to ask each one: specific things about grounding, RCDs, and surge protection that a competent electrician should be able to answer without hesitation. That filter made it easy to figure out who knew what they were talking about and who was guessing.

This is what struck me most about both situations. It's not that the professionals were incompetent exactly. The pool guy learned his method by doing it, not by studying chemistry. The electricians know standard procedures but aren't necessarily equipped for edge cases. 

**In markets where this kind of labor is cheap, there's not much economic pressure to go deep on the theory.**

**That creates a knowledge gap between the professional and the client. And when that gap is big enough, it gets exploited. Sometimes unintentionally, sometimes very much intentionally.** 

Plus we make it easy for them: we're all so freaking busy with our lives that we just rely on their knowledge without questioning whether they actually know what they're doing — or whether it's just a very well-maintained Instagram account built on simple, uncomplicated jobs.

What AI does is quickly close that gap. Not replace the professional (the electrician drove those rods, not me) but give you enough understanding to know what's actually wrong, what the right fix is, and whether the person in front of you is actually solving your problem.

<div align="center">❉</div>

## **How I actually used it**

Not as a single question. I built context incrementally: describe the situation, get a response, take notes, feed the new information back in with the next question. Each round got more specific. I used multiple models in parallel and compared the answers. When they converged, I trusted them more. When they diverged, I dug deeper.

It's not a magic oracle and it does get things wrong sometimes. But asking specific questions, cross-checking across models, and verifying things with physical measurements, it held up well in both cases.

The time saving compared to a traditional web search was significant. Search engines give you fragments. AI helps you build a coherent picture from them.

I could have just paid someone to fix both problems and understood nothing. Probably overpaid, probably solved things only partially. Instead I now know why pool pH matters and how to fix it, and I know how to size a grounding system in sandy soil. Those things will come back around, eventually.

<div align="center">❉</div>

*NB: Working with electricity has real risks. If you're unsure about anything, get a professional involved. Ideally after you've learned enough to ask the right questions.*

<div align="center">✌🏼</div>

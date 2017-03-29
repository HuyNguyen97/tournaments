# Swiss-system tournament analysis

Chris Hua / chua@wharton.upenn.edu

# Motivation

The Swiss-style tournament design has drawn a lot of support and adoption in many different competitive contexts. The most popular is likely chess, which uses Swiss tournaments in nearly all major tournaments. One variation on the system is commonly seen in American style [policy debate](https://en.wikipedia.org/wiki/Policy_debate). 

Here, a number of rounds, typically 6, are played as a preliminary seeding procedure. The final ranking is used as seeding for a 'playoff'-style single elimination bracket. 
Our concern is within the preliminary rounds, which follow a Swiss-system. The first 2 rounds consist of randomly assigned pairings, and the final 4 rounds are power-matched. That is, when possible, teams face teams with identical or similar (off by one) win-counts.

Formally, the goal of the preliminary Swiss tournament is to pick the top $k$ teams from a pool of $n$ teams.

# Design

Tournaments have configurable numbers of rounds and teams. Teams have underlying strengths, drawn from a lognormal distribution, and the win probability for any particular match follows a standard Bradley Terry Luce model.

Pairings are down by using the maximum weight perfect matching procedure. This procedure is well-established as the method of choice for creating tournament matchings [^](http://www.jstor.org/stable/pdf/2582935.pdf). 
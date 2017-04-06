"""Tournament modelling class and functions.

Chris Hua / chua@wharton.upenn.edu
"""

import numpy as np
import random
import networkx as nx
import pandas as pd
from qcore.asserts import assert_eq
from functools import lru_cache


class Tournament:
    """Describes a tournament.

    One key function -- run: Run one round of a tournament.
    Simulations should be done with 'simulation' class.
    """

    def __init__(self, n_teams, n_rounds, **kwargs):
        """Initiate a new tournament."""
        self.n_teams = n_teams
        self.n_rounds = n_rounds
        self.seed = kwargs.get('seed', random.uniform(0, 1000))
        self.dist = kwargs.get('dist', 'lognormal')
        self.strengths = self._generate_teams()
        self.wins = [0] * self.n_teams
        self.alpha = kwargs.get('alpha', 3500)
        self.beta = kwargs.get('beta', 35)

    def run(self):
        """Run a Tournamentent once."""
        # add wins for first round
        self.g = self._generate_base_graph()
        np.random.seed(None)
        for a, b in self._rand_pairing():
            self._add_match(a, b)

        # run rounds
        for i in range(self.n_rounds - 1):
            # self.__edges(i + 1)
            self._run_round()

        df = pd.DataFrame(list(
            zip(self.strengths, self.wins)), columns=['strength', 'wins'])
        return(df)

    def _run_round(self):
        """For given parameters, run a round."""
        for a, b in self._next_pairing():
            if(a > b):  # for bidrectionality purposes
                # if(self.g.edge[b][a]['weight'] < 0):
                    # print("ERROR!", self.g.edge[a][b]['weight'])
                self._add_match(b, a)
        self.rebalance()

    def _generate_teams(self):
        np.random.seed(self.seed)
        # strengths = self.dist_fun(size=self.n_teams)
        if(self.dist == "exp"):
            strengths = np.random.exponential(size=self.n_teams)
        elif(self.dist == "unif"):
            strengths = np.random.uniform(size=self.n_teams)
        elif(self.dist == "lognorm"):
            strengths = np.random.lognormal(size=self.n_teams)
        else:
            print("unknown distribution provided, using lognormal")
            strengths = np.random.lognormal(size=self.n_teams)
        return(strengths)

    @lru_cache(maxsize=32)
    def _generate_base_graph(self):
        g = nx.complete_graph(self.n_teams)

        # initiate edges
        for (u, v, d) in g.edges(data=True):
            g.add_edge(u, v, weight=1)
        return(g)

    def _rand_pairing(self):
        """Generate random pairing of teams.

        Used for first round of pairing.
        Subsequent rounds are paired via MW-PM.
        """
        teams = list(range(self.n_teams))
        random.seed(self.seed)
        shuffled = random.sample(teams, len(teams))
        return _grouper(shuffled, 2)

    def _win(self, a, b):
        """Whether team A wins a round, given respective strengths.

        True if A wins vs B, given their probability of winning.
        Uses a random roll to decide.
        Keyword arguments:
        a -- number of Team A
        b -- number of Team B
        strengths - vector of team strengths
        """
        roll = np.random.uniform()
        s_a = self.strengths[a]
        s_b = self.strengths[b]
        prob = s_a / (s_a + s_b)
        return roll < prob

    def _add_match(self, a, b):
        """Add a match and its result to our data structures.

        Adds the match to the graph, rolls to find winner,
        increments win counter.
        Keyword arguments:
        a -- number of Team A
        b -- number of Team B
        strengths - vector of team strengths
        """
        # self.g.remove_edge(a, b)
        self.g.add_edge(a, b, weight=-10000)
        if(self._win(a, b)):
            self.wins[a] += 1
        else:
            self.wins[b] += 1

    def _next_pairing(self):
        """Find maximum weight perfect matching for given state.

        Returns list of teams and their assignment
        """
        match = nx.max_weight_matching(self.g, True).values()
        pairs = list(zip(range(self.n_teams), (match)))
        return(pairs)

    def cost_function(self, x, y):
        r"""Cost or weight mechanism for edges.

        If a possible pairing has a difference of more than 1 win,
        then we weight it very low.
        Otherwise, we return $\alpha - (\beta * \abs(x - y))^2$.
        Keyword arguments:
        x - wins for team A
        y - wins for team B
        alpha - scale parameter
        beta - dispersion parameter
        """
        diff = abs(x - y)
        if(diff > 1):
            return(1)
        else:
            z = self.alpha - (self.beta * diff)**2
            return(int(z))

    def rebalance(self):
        """Rebalance the graph after a round."""
        for (u, v, d) in self.g.edges(data=True):
            if(self.g.edge[u][v]['weight'] > 0):
                cost = self.cost_function(self.wins[u], self.wins[v])
                self.g.edge[u][v]['weight'] = cost

    def print_edges(self):
        """Function to print edges.

        For debug purposes.
        Keyword arguments:
        g -- a graph
        """
        for (u, v, d) in self.g.edges(data=True):
            print(u, v, d)

    def _sum_edges(self):
        """For debug purposes."""
        s = 0
        for (u, v, d) in self.g.edges(data=True):
            s += self.g.edge[u][v]['weight']

    def _check_edges(self, round):
        max_edges = self.n_teams * (self.n_teams - 1) / 2
        actual_edges = self.g.number_of_edges()
        incurred_matches = round * self.n_teams / 2
        assert_eq(max_edges - incurred_matches, actual_edges)


# utility helpers


def _grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    Taken from itertools recipes:
    https://docs.python.org/2/library/itertools.html#recipes
    grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    """
    from itertools import zip_longest
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)

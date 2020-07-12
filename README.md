# StPetersburg
 
This is a simulation of some truncated versions of infinite games
similar to the classical St. Petersburg game. The simulation is
referenced in the paper "Unbounded utility and axiomatic foundations"
by Richard Kennaway, 2020. If the paper has not been published yet, you
can ask me for a copy.

All of the games consist of tossing a coin until it first comes up heads,
and making a payment to the player depending on the number of coin-tosses.

To run the program, at a Unix command line or in the OSX Terminal, or
whatever the equivalent is in Windows, go to the directory containing the
file testGames.py and type:

    python testGames.py GAME ...

GAME is an abbreviation for the game to be simulated. See below for a
list of available games.

The remaining arguments are all optional. Their default values are the
same as those used in the paper, so for a quick check on the results
described there, all of them can be omitted.


-trunc TRUNC

This is the length to which the game is truncated. If the coin has
been tossed TRUNC times without a result, the game stops with no payout
to either player.

The default value is 16.


-runlength RUNLENGTH

This is the number of games a player plays in a single run.
For each run we calculate the most negative balance either player had before
entering profit, their total profit from the run, and other things.

The default value is 1000.


-numruns NUMRUNS

This is the number of runs that we simulate, in order to collect
statistics on the behaviour of runs.

The default value is 10000.


-feeratio FEERATIO

This is the fee that player 1 pays to player 2 to participate in
the game, as a proportion of the expectation value. When FEERATIO < 1,
player 1 expects a long-term profit; when > 1, player 2 expects the
profit. When the expectation value is zero, no fee is paid.

The default value is 0.97.


-filename FILENAME

This is the name of a file to send all text output to.

By default, output is written to the terminal.


-plot

If this option is present, a plot of up to 100 runs will be made, showing
the player's winnings over time. This option requires that your Python
installation includes the matplotlib module, available from
https://matplotlib.org.


-seed SEED

This is the seed for the random number generator. Specifying this enables
exact reproducibility of results.

By default the generator is seeded from the system clock, and so the
program will give different results every time it is run, but broadly of
the same nature.


-ownrand

If this option is present, then this procedure will use the random number
defined in the accomnpaying file MersenneTwister.py. If the option is absent,
it will use the built-in numpy.random.rand(), which is nearly 20 times faster.

The reason for including this implementation is to make it possible to be
sure that in any future version of Python, which might use a different default
generator, bit-for-bit identical results can still be obtained. If porting this
program to a different language (it was originally written in Matlab) it also
allows a check on the correctness of the ported version.


All options can be truncated to a unique prefix, e.g. -t 10 -o -fe 0.9.


testGames.py can also be run from a Python command line. In this case, you
should give the commands:

    import testGames as tg
    tg.testGames( ... )
    
The first argument to tg.testGames is the game name, and subsequent arguments
are Python named arguments, in any order. Their names are the same as the
option names listed above, without the hyphen (but they cannot be truncated).
For example:

    tg.testGames( 'stp', numruns=100 )


The available games are:

    'stp'      St. Petersburg  
    'astp'     Alternating St. Petersburg  
    'pastp'    Permuted Alternating St. Petersburg  
    'cstp'     Convergent St. Petersburg  
    'pasa'     Pasadena  
    'ppasa'    Permuted Pasadena  
    'alta'     Altadena  
    'palta'    Permuted Altadena  
    'aix'      Aix-to-Ghent  
    'paix'     Permuted Aix-to-Ghent  
    'sudd'     Sudden Death

The "alternating" version of a game switches the sign of the payout
for each even-numbered length of game.

The "permuted" version of a game has the same set of expected payouts
for the possible lengths of game, but has them sorted into ascending
order. Thus player 1's biggest prizes come from the high value, low
probability end of the game, and player 2's from the low value, high
probability end.

St. Petersburg is the classical version, with a prize at the k'th stage
of 2^k, and therefore an expected payoff for each stage of 1.

For Convergent St. Petersburg the prize at the k'th stage is k.

For Pasadena, the prize at the k'th stage is -((-2)^k)/k. The
expected values therefore decrease as 1/k, with alternating sign.

Altadena is like Pasadena, but with 1 added to each prize.

Aix-to-Ghent is like Alternating St. Petersburg, but the expected
values of the prizes grow exponentially, and so the prizes grow even
faster: as 2^(2k) with alternating sign.

The game of Sudden Death is an exception to the general pattern. A coin
is tossed up to n times. If it ever comes up tails, the game ends with no
payout. If it comes up heads every time, the player wins 2^n.

All payoffs and all values reported are stated from the point of view
of player 1, i.e. positive numbers are a gain for player 1, a loss for
player 2.

The particular examples described in the paper use truncation to 16
plays, an entry fee of 97% of expectation value, 1000 games per run,
and 10000 runs. While 3% expected profit per game may seem a small edge
for the player, it is similar to that of the casino in the game of
roulette (1/37), and that size of edge keeps the casino in business.

The result of running the program is to print out some statistics, and
if requested, to plot a sample of 100 of the runs of games, showing the
player's winnings at each point in time. These plots give a more intuitive
idea of the behaviour of the games than the summary statistics.


Not all of these games are discussed in the paper. For those that are,
we reproduce the comments that the paper makes about them, and the
commands that can be given to reproduce the results.

St. Petersburg:

    python testGames.py stp

"The player has about a 50% chance of at some point owing the banker
at least 4000 units, even though less than 16 units are wagered on each
game. The expected profit for a run of 1000 games is 480. The average
profit for 10000 runs of 1000 games is close to this, but its standard
deviation is over 11000, or 23 times the mean."


Alternating St. Petersburg:

    python testGames.py astp

"The game is fair in expectation, but both players risk large losses
that may bankrupt either one."


Permuted Pasadena:

    python testGames.py ppasa

"In Permuted Pasadena, although the player's long-term expectation is
positive, after 1000 games they only have an 11% chance of being in
profit. Over 10 million games, the player can easily make a final loss
of over 1 million units.

"It is interesting to plot the player's winnings over time for Permuted
Pasadena. The player seems to be relentlessly losing money, despite the
positive expectation. This is because 1000 games is not enough for the
largest payoffs to be sure of happening. The player's largest payoff
only happens once in 65536 games, and even their smallest positive
payoff happens only one time in 512."


Convergent St. Petersburg:

    python testGames.py cstp

"In a run of 1000 games, the player ends with a profit more than 90% of
the time. The median downside risk for repeated runs of 1000 games is
about 10. A plot of the player's winnings over time is close to a
Wiener process with a drift velocity equal to the expected profit per
game."

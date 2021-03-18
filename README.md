# StPetersburg
 
This is a simulation of some truncated versions of infinite games
similar to the classical St. Petersburg game. The simulation is
referenced in my paper "Unbounded utility and axiomatic foundations"
(October 2020), available at https://doi.org/10.13140/RG.2.2.23334.24645.

The paper discusses only St. Petersberg, Pasadena, and Convergent St.
Petersberg, which are enough for the points it makes, but this program
simulates a great many more.

All but one of the games consist of tossing a coin until it first comes up
heads, and making a payment to the player depending on the number of
coin-tosses.

The program is written in Python (version 3) and must be run from a command
line. On Unix, the Unix command line, and on OSX, the Terminal command line.
I am not familiar with Windows.

A quick check of the functioning of the program and the examples discussed
in the paper can be made with the command:

    python alltests.py
    
This will run all of the examples from section 3 of the paper and several
more besides, and write results to the file testresults.txt. As the tests
use a fixed seed for the random number generator, the results should be
identical to the results already provided in the subdirectory TestResults.

The program alltestMT.py does the same as alltests.py, but uses the
accompanying random number generator MersenneTwister.py instead of Python's
built-in one, and writes to testresultsMT.txt. This takes much longer to
run than alltests.py (several minutes), and is included for reasons given
in the description of the -ownrand option below.

The program that actually runs the simulations is the file testGames.py.
To run this, go to the directory containing that file and type:

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

Extreme values of -trunc may result in probabilities underflowing the
possible range of real numbers, or prizes overflowing. A warning will be
given if this happens.


-runlength RUNLENGTH

This is the number of games a player plays in a single run.
For each run we calculate the most negative balance either player had before
entering profit, their total profit from the run, and some other things.

The default value is 1000.


-numruns NUMRUNS

This is the number of runs that we simulate, in order to collect
statistics on the behaviour of runs.

The default value is 10000.


-feeratio FEERATIO

This is the fee that player 1 pays to player 2 to participate in
the game, as a proportion of the expectation value. When FEERATIO < 1,
player 1 expects a long-term profit; when > 1, player 2 expects the
profit. When the expectation value is zero, no fee is paid. When the
expectation value is negative, the fee is paid by player 2 to player 1.

The default value is 0.97.


-firstpassage PROFIT

If this option is given, the time at which the player's profit first
reaches or exceeds the given value is calculated for each run. Statistics
for this quantity are output, and if plotting is requested, a histogram
of the values is drawn. Runs where this profit level is never reached
are given a notional value of one more than the run length.

I believe, but have not proved, that the first passage time has infinite
expectation for all of the non-truncated games having a finite expectation
value and a fee equal to the expectation. This is known to be the case when
the expected value of a game and its variance both exist.


-fat

Without this option, the coin tosses are all 50-50 chances. With this option,
the probability of the n'th toss being heads (assuming all previous ones were
tails) is 1/n(n+1). This is equivalent to tossing a series of biased coins
whose probabilities of heads are 1/2, 1/3, 1/4, etc.

This gives a fat-tailed distribution of game lengths, a discretised version
of the positive half of the Cauchy distribution. The longer the game has gone
on, the longer it is likely to continue. It is certain to end, but the
expected length is infinite.

If you use a truncation length of n without the -fat option, using 2^n-1 with
the -fat option will give the same probability of truncation.


-output FILENAME

This is the name of a file to send all text output to. If the filename begins
with a "+", then the "+" is removed and output is appended to the file,
instead of replacing it.

By default, output is written to the terminal.


-plot

If this option is present, a plot of up to 100 runs will be made, showing
for each one the player's winnings over time. If the -firstpassage option
was also given, a histogram of first passage times will also be made.

To obtain these plots you must have the matplotlib module installed. The
program will tell you if it is not. If it is absent from your Python
installation, it can be obtained from https://matplotlib.org.


-seed SEED

This is the seed for the random number generator. Specifying this enables
exact reproducibility of results.

By default the generator is seeded from the system clock, and so the
program will give different results every time it is run, but broadly of
the same nature.


-ownrand

If this option is present, then this procedure will use the random number
generator defined in the accompanying file MersenneTwister.py. If the option
is absent, it will use the built-in numpy.random.rand(), which is about 20
times faster.

The reason for including this implementation is to make it possible to be
sure that in any future version of Python, which might use a different default
generator, bit-for-bit identical results can still be obtained. If porting this
program to a different language (it was originally written in Matlab) it also
allows a check on the correctness of the ported version.


All options can be truncated to a unique prefix, e.g. -t 10 -own -fe 0.9.


testGames.py can also be run from a Python 3 command line. In this case, you
should give the commands:

    import testGames as tg
    tg.testGames( ... )
    
The first argument to tg.testGames is the game name, and subsequent arguments
are Python named arguments, in any order. Their names are the same as the
option names listed above, without the hyphen (but they cannot be truncated).
Boolean options like -plot must be explicitly given the value True.
For example:

    tg.testGames( 'stp', numruns=100, plot=True )


The available games are:

    'stp'      St. Petersburg  
    'astp'     Alternating St. Petersburg  
    'pastp'    Permuted Alternating St. Petersburg  
    'cstp'     Convergent St. Petersburg  
    'acstp'    Alternating Convergent St. Petersburg
    'dull'     Dull
    'adull'    Alternating Dull
    'pasa'     Pasadena  
    'ppasa'    Permuted Pasadena  
    'alta'     Altadena  
    'palta'    Permuted Altadena  
    'aix'      Aix-to-Ghent  
    'paix'     Permuted Aix-to-Ghent  
    'pdnk'     Podunk  
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

For the Dull game, the prize is always 1, unless the game is truncated.

For Pasadena, the prize at the k'th stage is -((-2)^k)/k. The
expected values therefore decrease as 1/k, with alternating sign.

Altadena is like Pasadena, but with 1 added to each prize.

Aix-to-Ghent is like Alternating St. Petersburg, but the expected
values of the prizes grow as 2^k, and so the prizes grow even faster:
as 2^(2k) with alternating sign.

Podunk has payoffs of 2^n/n^2. This converges more strongly than Pasadena,
strongly enough for its expectation value to be the sum of an absolutely
convergent series. The sum is (pi^2)/6. However, its standard deviation is
infinite. The truncations of this game have finite standard deviation,
but it grows exponentially with the length of the truncation.

Smallville has payoffs of 2^n/n^4. This converges faster than Podunk, and
has finite expectation, standard deviation, and skewness (but no higher
moments). This game is well-behaved.

The game of Sudden Death is an exception to the general pattern. A coin
is tossed up to n times. If it ever comes up tails, the game ends with no
payout. If it comes up heads every time, the player wins 2^n.

"Aix-to-Ghent", "Podunk", and "Smallville" are the author's own coinages.
"Sudden Death" is a method of resolving ties in a golf match, by having
the players begin another round and giving victory to the first player
to win a hole.

All payoffs and all values reported are stated from the point of view
of player 1, i.e. positive numbers are a gain for player 1, a loss for
player 2.

The particular examples described in the paper use truncation to 16
plays, an entry fee of 97% of expectation value, 1000 games per run,
and 10000 runs. While 3% expected profit per game may seem a small edge
for the player, it is similar to that of the casino in the game of
roulette (1/37 = 2.7), and that edge keeps the casino in business.

The result of running the program is to print out some statistics. Some of
these are calculated from the mathematical definition of the game, and some
from the results of simulating it. Where kurtosis is shown, this is
Pearson's definition, i.e. the kurtosis of the normal distribution is 3.

If requested, the program will plot a sample of 100 runs of games, showing
the player's winnings at each point in time, overlain by a dashed line
whose constant gradient is the expected profit per game. These plots give a
more intuitive idea of the behaviour of the games than the summary
statistics.


Not all of these games are discussed in the paper. For those that are,
we reproduce the comments that the paper makes about them, and the
commands that can be given to reproduce the results.

St. Petersburg:

    python testGames.py stp

"In a run of 1000 games, the player has about a 50% chance of at some point
owing the banker at least 4000 units. The expected profit for such a run of
1000 is 480. The average profit for 10000 runs of 1000 games is close to
this, but its standard deviation is over 11000, or 23 times the mean."


Pasadena:

"In an indefinitely long sequence of truncated Pasadena games, the player
will experience swings of fortune almost proportional to the number of games
played, up to the largest payout available."


Convergent St. Petersburg:

    python testGames.py cstp

"In a run of 1000 games, the player ends with a profit more than 90% of
the time. The median downside risk for repeated runs of 1000 games is
about 10. A plot of the player's winnings over time is close to a
Wiener process with a drift velocity equal to the expected profit per
game."


We make here some further remarks on other examples:


Alternating St. Petersburg:

    python testGames.py astp

The game is fair in expectation, but both players risk large losses
that may bankrupt either one.


Permuted Pasadena:

    python testGames.py ppasa

In Permuted Pasadena, although the player's long-term expectation is
positive, after 1000 games they only have an 11% chance of being in
profit. Over 10 million games, the player can easily make a final loss
of over 1 million units.

It is interesting to plot the player's winnings over time for Permuted
Pasadena. The player seems to be relentlessly losing money, despite the
positive expectation. This is because 1000 games is not enough for the
largest payoffs to be sure of happening at all. The player's largest
payoff only happens once in 65536 games, and even their smallest
positive payoff happens only one time in 512.


The fat-tailed versions of the games are not discussed in the paper.
If run to the same truncation length, the fat-tailed version of a game
has the same expectation as the original version -- it is specifically
constructed to make this so. For example:

    python testGames.py ... -fat -trunc 16
    
The fat-tailed versions, truncated to 16, produce more well-behaved results
(except for the Aix-to-Ghent and Permuted Aix-to-Ghent games, whose payoffs
grow too fast to be tamed by this). However, a better comparison may be to
truncate them so that the same amount of probability mass is trimmed
away. If the truncation length is N, that amount is 2^(-N) for the
original version and 1/(N+1) for the fat-tailed version. Therefore the
following is the fat-tailed equivalent of truncating the original game
to 16 turns:

    python testGames.py ... -fat -trunc 65535

When this is done, the same pathologies show up again, provided that the
various payoffs can be calculated within the bounds of the computer's real
number arithmetic.

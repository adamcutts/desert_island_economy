# Desert Island Economy Simulation

*An agent-based simulation capturing resource collection, consumption and trade, with two types of goods, and no currency.*

## Introduction

This is a project I made for fun, in the spirit of the latest *Lord of the Flies* adaptation on the BBC. 

Suppose that a cruise ship becomes stranded on a desert island. Beyond the reach of phone signals, the $n$ passengers realise they must gather resources and co-operate if they are to survive. 

We model each passenger as an agent: each day, they can gather resources, consume them, and trade. 

### Gathering 

There are two types of goods on the island: fish from the sea, which provide food, and coconuts from the abundant forests, which provide potable water (sea-water isn't so good for you!). Some agents are naturally better at fishing or coconut farming than others; the global variable `GATHER_MEAN` captures the average amount of goods a days work will collect, and the individual coefficients `fish_efficiency` and `coconut_efficiency` capture this natural variation. The method `gather` for the agent class governs the gathering behaviour. 

Each agent has a stockpile of the fish and coconuts they have gathered. They also have vital levels: `satiety`, capturing hunger, and `hydration`, capturing thirst. If either of these vitals hit $0$, the agent dies and is removed from the simulation. The agents vary in how much food and water they need each day: this is captured by the `hunger_rate` and `thirst_rate` attributes. The gathering strategy is then the naive one: the agent gathers whichever vital (i.e. satiety or hydration) will run out first. 

### Trade

Because of the variation in the agents' ability to gather resources, some agents will find themselves with a surplus, and some with a lack of goods. If agent A is good at gathering fish and poor at gathering coconuts, and agent B has the reverse problem, it will be mutually beneficial for them to trade.

The trading strategy is captured in the `do_trading(agents)`. This is the main place that complexity is introduced into the model. We take a naive approach. Each day, the (living) agents are paired randomly. If one is more hungry than thirsty, and the other is thirstier than they are hungry, they will trade fish for coconuts in the obvious direction, at volume `GATHER_MEAN`, or whichever stock is lowest. 

### Simulation and plots

The function `run_sim()` runs the simulation and returns a full log, as well as a history of the simulation and a list of the agents after all the action has taken place. This allows us to investigate the relationship between all the attributes: for example, how many agents survive the full `N_DAYS`? Is there a relationship between resource gathering efficiency and survival?

## Results

Here we see the plot for `N_AGENTS = 250`, `N_DAYS = 100`, and `random.seed(100)`:

![alt text](https://github.com/adamcutts/desert_island_economy/blob/main/desert_island_4_plots.png)

## Conclusion

There is plenty of scope for extending this project. Examples of places to go next include:
1. More complex trading strategies;
2. Trading strategies that vary across the population (e.g. an innate stubborness to trade in some agents);
3. The ability for the population to grow as well as shrink;
4. A move to finite resources, or seasonality in resource scarcity;
5. Aging agents, who require more resources as they age.

Even without these extensions, the model is quite rich, and there is plenty to investigate in terms of model behaviour as a function of the parameters.

Finally, the next step is to make a script making the `island_sim_log.csv` more amenable to time-series analysis by reshaping it into a .csv with one row per day.

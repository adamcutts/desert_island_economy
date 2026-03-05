'''
Island Economy Simulation
--------------------------------------------
N agents gather fish for food, and coconuts for water.
They trade according to a given (global) strategy.
Agents die whenever their satiety or hydration becomes fully
depleted.
'''

from dataclasses import dataclass
import random
import os
import csv
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Config
N_AGENTS = 2000
N_DAYS = 365
GATHER_MEAN = 5.0
GATHER_NOISE = 0.35
SATIETY_CAP = 30.0
HYDRATION_CAP = 30.0
LOG_FILE = 'island_sim_log.csv'


# Agent class
@dataclass
class Agent:
    '''
    Each agent has a set of attributes which evolve over time
    '''
    agent_id: int
    satiety: float  # food level (0 is death)
    hydration: float  # water level (0 is death)
    hunger_rate: float  # satiety lost per day
    thirst_rate: float  # hydration lost per day
    fish_efficiency: float
    coconut_efficiency: float
    coconuts: float = 0.0
    fish: float = 0.0
    alive: bool = True

    # Gathering strategy
    def decide_gather(self) -> str:
        '''Gather most urgently needed resource'''
        # Urgency = (days til death)**(-1)
        food_urgency = self.hunger_rate / self.satiety
        water_urgency = self.thirst_rate / self.hydration
        return 'fish' if food_urgency >= water_urgency else 'coconut'

    # Gather resources
    def gather(self):
        noise = random.uniform(1 - GATHER_NOISE, 1 + GATHER_NOISE)
        amount = GATHER_MEAN * noise  # daily resources gathered is random
        choice = self.decide_gather()
        if choice == 'fish':
            self.fish += amount * self.fish_efficiency
        else:
            self.coconuts += amount * self.coconut_efficiency

    # Consume resources
    def consume(self):
        food_needed = self.hunger_rate
        water_needed = self.thirst_rate

        # Eating
        from_fish = min(self.fish, food_needed)  # Cannot consume more than stock of fish
        self.fish -= from_fish
        food_needed -= from_fish

        # Drinking
        from_coconut = min(self.coconuts, water_needed)
        self.coconuts -= from_coconut
        water_needed -= from_coconut

        # Unmet need depletes vitals
        self.satiety -= food_needed
        self.hydration -= water_needed

        # Clip vitals at their limits
        self.satiety = min(self.satiety, SATIETY_CAP)
        self.hydration = min(self.hydration, HYDRATION_CAP)

        # Check for death
        if self.satiety <= 0 or self.hydration <= 0:
            self.alive = False


# Trading
def do_trading(agents: list[Agent]):
    '''
    Randomly pair agents together. Whenever mutually beneficial,
    agents swap GATHER_MEAN of their coconuts/fish.
    '''

    living = [a for a in agents if a.alive]
    random.shuffle(living)  # We get a random match of agents
    pairs = [(living[i], living[i + 1]) for i in range(0, len(living) - 1, 2)]

    for a, b in pairs:
        # Thirst and hunger dictate preference (naive mechanism)
        if a.satiety > a.hydration and b.hydration > b.satiety:
            # A gives fish, B gives coconuts
            trade_volume = min(a.fish, b.coconuts, GATHER_MEAN)
            a.fish -= trade_volume
            b.fish += trade_volume
            a.coconuts += trade_volume
            b.coconuts -= trade_volume
        elif a.hydration > a.satiety and b.satiety > b.hydration:
            # A gives coconuts, B gives fish
            trade_volume = min(a.coconuts, b.fish, GATHER_MEAN)
            a.coconuts -= trade_volume
            b.coconuts += trade_volume
            a.fish += trade_volume
            a.fish -= trade_volume


# Population builder
def make_agents(n: int) -> list[Agent]:
    agents = []
    for i in range(n):
        agents.append(Agent(
            agent_id=i,
            satiety=random.uniform(10, 20),
            hydration=random.uniform(10, 20),
            hunger_rate=random.uniform(0.5, 3.5),# Model thirst as more rapid than hunger
            thirst_rate=random.uniform(1.5, 3.5),
            fish_efficiency=random.uniform(0.6, 1.5),
            coconut_efficiency=random.uniform(0.6, 1.5)
        ))
    return agents


# Running the simulation
def run_sim(n: int = N_AGENTS, days: int = N_DAYS):
    agents = make_agents(n)
    log_rows = []

    # Historical record
    history = {
        'day': [],
        'alive': [],
        'mean_satiety': [],
        'mean_hydration': [],
        'deaths': []
    }

    for day in range(1, days + 1):
        deaths_today = 0

        # Gather goods
        for a in agents:
            if a.alive:
                a.gather()

        # Trade goods
        do_trading(agents)

        # Consume goods and trace deaths
        for a in agents:
            if a.alive:
                a.consume()
                if not a.alive:
                    deaths_today += 1

        living = [a for a in agents if a.alive]

        # Amend log
        for a in agents:
            log_rows.append({
                'day': day,
                'agent_id': a.agent_id,
                'alive': int(a.alive),
                'satiety': round(a.satiety, 2),  # Round decimals
                'hydration': round(a.hydration, 2),
                'fish': round(a.fish, 2),
                'coconuts': round(a.coconuts, 2),
                'hunger_rate': round(a.hunger_rate, 2),
                'thirst_rate': round(a.thirst_rate, 2)
            })

        # Update history
        history['day'].append(day)
        history['alive'].append(len(living))
        history['deaths'].append(deaths_today)
        history['mean_satiety'].append(
            sum(a.satiety for a in living) / len(living) if living else 0)  # Ignores dead population
        history['mean_hydration'].append(
            sum(a.hydration for a in living) / len(living) if living else 0)

        # Halt if population dies
        if not living:
            print(f'All agents dead by day {day}.')
            break

    return agents, log_rows, history


# Save a log of results
def save_log(log_rows: list[dict], path: str = LOG_FILE):
    if not log_rows:
        return
    fields = list(log_rows[0].keys())
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(log_rows)
    print(f'Log saved @ {path}')


# Create plots of results
def plot_results(agents: list[Agent], history: dict):
    days = history['day']

    fig = plt.figure(figsize=(12, 10), facecolor='#0d1117')
    fig.suptitle('Island Economy Simulation: Results', fontsize=16,
                 color='white', fontweight='bold', y=0.97)
    gs = gridspec.GridSpec(2, 2)

    ax_pop = fig.add_subplot(gs[0, 0])
    ax_health = fig.add_subplot(gs[0, 1])
    ax_fish = fig.add_subplot(gs[1, 0])
    ax_coconuts = fig.add_subplot(gs[1, 1])

    for ax in (ax_pop, ax_health, ax_fish, ax_coconuts):
        ax.set_facecolor('#161b22')
        ax.tick_params(colors='gray')
        ax.xaxis.label.set_color('gray')
        ax.yaxis.label.set_color('gray')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#30363d')

    # Population numbers over time
    ax_pop.plot(days, history['alive'], color='#58a6ff', linewidth=2)
    ax_pop.fill_between(days, history['alive'], alpha=0.15, color='#58a6ff')
    ax_pop.set_title('Survivors')
    ax_pop.set_xlabel('Day')
    ax_pop.set_ylabel('Alive agents')
    ax_pop.set_ylim(bottom=0)

    # Vitals over time
    ax_health.plot(days, history['mean_satiety'], color='#ff6600', linewidth=2, label='Mean satiety')
    ax_health.plot(days, history['mean_hydration'], color='#58a6ff', linewidth=2, label='Mean hydration')
    ax_health.set_title('Mean vitals')
    ax_health.set_xlabel('Day')
    ax_health.set_ylabel('Vital level')
    ax_health.legend()

    # Efficiency/rate plots
    fish_eff = []
    fish_rate = []
    coconut_eff = []
    coconut_rate = []
    survived = []
    for a in agents:
        fish_eff.append(a.fish_efficiency)
        fish_rate.append(a.hunger_rate)
        coconut_eff.append(a.coconut_efficiency)
        coconut_rate.append(a.thirst_rate)
        survived.append(a.alive)
    colours = ['green' if _ else 'red' for _ in survived]

    scatter1 = ax_fish.scatter(
        fish_eff, fish_rate, c=colours, s=60, edgecolors='#30363d', linewidths=0.5, alpha=0.6
    )
    ax_fish.set_title('Fish attributes\n(green=alive, red=dead)')
    ax_fish.set_xlabel('Fish gathering efficiency')
    ax_fish.set_ylabel('Hunger rate')

    scatter2 = ax_coconuts.scatter(
        coconut_eff, coconut_rate, c=colours, s=60, edgecolors='#30363d', linewidths=0.5, alpha=0.6
    )
    ax_coconuts.set_title('Coconut attributes\n(green=alive, red=dead)')
    ax_coconuts.set_xlabel('Coconut gathering efficiency')
    ax_coconuts.set_ylabel('Thirst rate')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    #random.seed(100)

    print(f'Starting simulation: {N_AGENTS} agents, {N_DAYS} days\n')
    agents, log_rows, history = run_sim(N_AGENTS, N_DAYS)

    living = [a for a in agents if a.alive]
    print(f'\nFinal survivors: {len(living)} / {N_AGENTS}')

    save_log(log_rows, LOG_FILE)

    plot_results(agents, history)


import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('results.csv')

# Initial data transformations

df['ended'] = df['lost'] | df['won']

save = False


def save_or_show(name):
    if not save:
        plt.show()
    else:
        plt.savefig(name + '.png')


def get_agents(df):
    return df['agent'].unique()


def split_dataset_between_agents(df, agents):
    result = []
    for agent in agents:
        frame = df.loc[df['agent'] == agent]
        frame = frame.reset_index()
        result.append(frame)
    return result



def plot_one_parameter(parameter, title, xlabel, ylabel):
    agents = get_agents(df)
    frame = df[['agent', parameter]]
    parts = split_dataset_between_agents(frame, agents)
    for part in parts:
        plt.plot(part[parameter])
    plt.legend(agents)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    save_or_show(parameter)


def plot_histograms(parameter, title):
    agents = get_agents(df)
    figure, axes = plt.subplots(ncols=len(agents))
    parts = split_dataset_between_agents(df, agents)
    for (i, agent), part in zip(enumerate(agents), parts):
        plt.subplot2grid((1, len(agents)), (0, i))
        part[parameter].value_counts().plot(kind='bar', title=agent)
    figure.suptitle(title)
    save_or_show(parameter + '_hist')


def plot_real_values_histogram(parameter, title, xlabel='', ylabel=''):
    agents = get_agents(df)
    figure, axes = plt.subplots(ncols=len(agents))
    parts = split_dataset_between_agents(df, agents)
    for (i, agent), part in zip(enumerate(agents), parts):
        plt.subplot2grid((1, len(agents)), (0, i))
        plt.hist(part[parameter])
        plt.title(agent)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
    figure.suptitle(title)
    save_or_show(parameter + '_hist')




plot_one_parameter('elapsed_time', 'Czas gry poszczególnych agentów',  'Kolejne uruchomienie', 'Czas [s]')
plot_histograms('lost', 'Histogram porażki')
plot_histograms('last_move_random', 'Częstość ostatniego ruchu jako losowego')

def plot_winnings_by_size(df, agent1, agent2):
    agents = [agent1, agent2]

    for agent in agents:
        agent_data = df[df['agent'] == agent]
        agent_winnings = agent_data['won'].groupby(agent_data['size']).sum()

        sizes = agent_winnings.index
        winnings = agent_winnings.values

        plt.figure()  # Create a new figure for each agent
        plt.bar(sizes, winnings)
        plt.xlabel('Size')
        plt.ylabel('Number of Winnings')
        plt.title(f'Number of Winnings by Size - {agent}')
        plt.show()

# Call the function to plot separate bar charts for each agent
plot_winnings_by_size(df, 'fol', 'neural')




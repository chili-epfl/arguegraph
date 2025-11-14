import os
import pickle
import random
# from graphviz import Graph

import numpy as np
import pandas as pd

# from matplotlib import pyplot as plt
# import seaborn as sns

from sklearn.metrics import pairwise_distances

import networkx as nx
import networkx.algorithms.matching as matching

import gspread
import altair as alt

PRE_INPERSON_URL = "https://docs.google.com/spreadsheets/d/13wbbMcV-9WqpIWo6N6OxzlABndzM0K4GSxfwReRH9co/edit?usp=sharing"
# PRE_ONLINE_URL = "https://docs.google.com/spreadsheets/d/1JTrA3Ce3pihrd_Yq0rUodbS2_IM90Tdd0mPIaBQKLPY/edit?usp=sharing"
POST_INPERSON_URL = "https://docs.google.com/spreadsheets/d/1oLHXpqg_OYobEBCEd0JbGrvG4pbkpslYS2UU701PpPY/edit?usp=sharing"
# POST_ONLINE_URL = "https://docs.google.com/spreadsheets/d/1mTMw1rWoH629ISJ5mfp-AQm3sxl3StYg4OuZVcIFGJM/edit?usp=sharing"
# DEMO_URL = "https://docs.google.com/spreadsheets/d/1mvJqVmvFpRP4w7-5RgVPuaflW2ZRLlDC2zWlBth1vcs/edit?usp=sharing"


def load_worksheet(url, worksheet="Form responses 1"):
    gc = gspread.service_account("service_account.json")

    # Spreadsheet has been shared with email specified in service_account.json
    sh = gc.open_by_url(url)
    ws = sh.worksheet(worksheet)
    df = pd.DataFrame(ws.get_all_records())
    return df


# Functions to assign the coordinates from the answers
def process_question_teams(answer:str) -> list:
    if answer == 'Yes, it might force them to deepen the contents of my lecture':
        return [2, -2]

    if answer == 'Yes, even if they won’t necessarily learn more, they might at least learn to work together':
        return [2, -2]

    if answer == 'No, they can learn to work in teams in many activities outside school':
        return [2, -2]

    if answer == 'No, teamwork takes too much time; I have to move faster in the curriculum':
        return [-2, 2]


def process_question_size(answer:str) -> list:
    if answer == 'Teams of 3, because the third can kind of arbitrate the disagreements between the two other ones, so the team would work better':
        return [-1, -1]

    if answer == 'Teams of 2, because with larger teams, there is often one person that does not contribute much, which is unfair for the two other ones':
        return [2, -2]

    if answer == 'Teams of 5, so that I can detect which students take leadership':
        return [-2, -2]

    if answer == 'Teams of 10, because that’s often the size of the teams they will join later on in the workplace':
        return [3, -2]


def process_question_composition(answer:str) -> list:
    if answer == 'Two students with different viewpoints so that they produce multiple solutions':
        return [1, -2]

    if answer == 'Two students with a different backgrounds, so that they get used to handle diversity':
        return [2, -2]

    if answer == 'Two students with the same level, otherwise the better students will waste time with the weaker one':
        return [-1, 2]

    if answer == 'Two students with different levels, so that one develops the skills of helping other students':
        return [2, -2]


def process_question_argue(answer:str) -> list:
    if answer == 'Ask them to elaborate a list of pros and cons and connect it to what was taught in the last lecture':
        return [0, 2]

    if answer == 'Discuss with them to see if some opinions are scientifically incorrect':
        return [-3, 2]

    if answer == 'Nothing, I will ask them to less loud then I will check who wins the argumentation':
        return [-2, -2]

    if answer == 'Nothing, it may force them to deepen their understanding of the task':
        return [2, 2]


def calculate_distances(graph):
    # Assign coordinates
    graph['team_xy'] = graph['If you were a school teacher, would you ask students to work in teams? Pick what you might decide and why.'].apply(process_question_teams)
    graph['size_xy'] = graph['If you would decide anyway to make teams, which size of the teams would you choose?'].apply(process_question_size)
    graph['composition_xy'] = graph['Let’s say that you finally decide to make teams of 2, what would be the best team composition?'].apply(process_question_composition)
    graph['argue_xy'] = graph['If during their teamwork, three students start to argue loudly what would you do?'].apply(process_question_argue)

    # Separate x and y coordinates
    graph['team_x'] = graph['team_xy'].apply(lambda x: x[0])
    graph['size_x'] = graph['size_xy'].apply(lambda x: x[0])
    graph['composition_x'] = graph['composition_xy'].apply(lambda x: x[0])
    graph['argue_x'] = graph['argue_xy'].apply(lambda x: x[0])

    graph['team_y'] = graph['team_xy'].apply(lambda x: x[1])
    graph['size_y'] = graph['size_xy'].apply(lambda x: x[1])
    graph['composition_y'] = graph['composition_xy'].apply(lambda x: x[1])
    graph['argue_y'] = graph['argue_xy'].apply(lambda x: x[1])

    # Sum x and y coordinates
    graph['x'] = graph['team_x'] + graph['size_x'] + graph['composition_x'] + graph['argue_x']
    graph['y'] = graph['team_y'] + graph['size_y'] + graph['composition_y'] + graph['argue_y']

    # Check unique count of coordinates
    graph['xi'] = graph['x'].astype(str) + graph['y'].astype(str)
    # print('There are {} unique coordinates'.format(len(graph['xi'].unique())))

    graph['x_j'] = graph.x + np.random.normal(0,0.2,graph.x.shape)
    graph['y_j'] = graph.y + np.random.normal(0,0.2,graph.y.shape)
    graph['uid'] = range(graph.shape[0])
    
    # Solve this using maximum weighted matching. 
    # See https://math.stackexchange.com/questions/972936/hungarian-algorithm-on-symmetric-matrix.
    distances = pairwise_distances(graph[['x', 'y']])
    distances *= np.tri(*distances.shape) # Set upper triangle and diagonal to zero

    return distances

def construct_graph(distances):

    G = nx.Graph()

    for i, row in enumerate(distances):
        for j, entry in enumerate(row):
            if j >= i:
                continue
            #print(f'Adding edge from {i} to {j} with weight {entry}')
            G.add_edge(i, j, weight = entry)

    # print(G)
    # nx.draw(G)
    return G


def get_distance_plot(df, distances, G):
    df_copy = df.copy()
    df_copy.reset_index(inplace=True)

    M = matching.max_weight_matching(G)
    c = 0
    for pair in M:
        for individual in pair:
            df_copy.loc[individual, 'group'] = c
        c += 1

    source = df_copy

    selection=alt.selection_multi(fields=['Email address'], bind='legend')

    base = alt.Chart(source).mark_circle(size=100).encode(
        x=alt.X('x_j', scale=alt.Scale(domain=[-8, 8]), title="X Axis"),
        y=alt.Y('y_j', scale=alt.Scale(domain=[-8, 8]), title="Y Axis"),
        color='group:N',
        tooltip=['Email address'],
    ).properties(width=600, height=600)

    lines = base.mark_line().encode(
        x='x_j',
        y='y_j',
        detail='group',
    )

    # alt.layer(base, lines).interactive().save('distances.html')
    # alt.layer(base, lines).interactive().save('distances.json')
    return alt.layer(base, lines).configure_axis(
        labelFontSize=14,  # Font size for axis labels
        titleFontSize=14   # Font size for axis titles
    ).configure_legend(
        titleFontSize=14,  # Font size for legend title
        labelFontSize=14   # Font size for legend labels
    ).configure_text(fontSize=14).interactive()


def get_post_distance_plot(df, distances, G, post_df):
    df_copy = df.copy()
    df_copy.reset_index(inplace=True)
    
    post_df_copy = post_df.copy()
    post_df_copy.reset_index(inplace=True)

    M = matching.max_weight_matching(G)
    c = 0
    for pair in M:
        for individual in pair:
            df_copy.loc[individual, 'group'] = c
        c += 1

    merged = post_df_copy.merge(df_copy[['Email address', 'group']], on='Email address', how='left')
        
    source = df_copy

    selection=alt.selection_multi(fields=['Email address'], bind='legend')

    base = alt.Chart(source).mark_circle(size=100).encode(
        x=alt.X('x_j', scale=alt.Scale(domain=[-8, 8]), title="Individual cognition ⟺ Social cognition"),
        y=alt.Y('y_j', scale=alt.Scale(domain=[-8, 8]), title="As a skill ⟺ As a method"),
        color='group:N',
        tooltip=['Email address'],
    ).properties(width=600, height=600)

    lines = base.mark_line().encode(
        x='x_j',
        y='y_j',
        detail='group',
    )

    points = alt.Chart(merged).mark_point(size=200).encode(
        x=alt.X('x_j', scale=alt.Scale(domain=[-8, 8])),
        y=alt.Y('y_j', scale=alt.Scale(domain=[-8, 8])),
        color='group:N',
        tooltip=['Email address'],
        shape=alt.value('cross')  # Setting shape to 'cross' for X shape
    )

    # alt.layer(base, lines).interactive().save('distances.html')
    # alt.layer(base, lines).interactive().save('distances.json')
    return alt.layer(base, lines, points).configure_axis(
        labelFontSize=14,  # Font size for axis labels
        titleFontSize=14   # Font size for axis titles
    ).configure_legend(
        titleFontSize=14,  # Font size for legend title
        labelFontSize=14   # Font size for legend labels
    ).configure_text(fontSize=14).interactive()


def get_max_distance_pairs(df, distances, G):
    M = matching.max_weight_matching(G)
    max_distance_pairs = []
    for entry in M:
        # print(f'Pair {df.iloc[min(entry)]["Email address"]} with {df.iloc[max(entry)]["Email address"]}')
        max_distance_pairs.append([df.iloc[min(entry)]["Email address"], df.iloc[max(entry)]["Email address"]])
    return max_distance_pairs


def get_max_distance_stats(df, distances, G):
    M = matching.max_weight_matching(G)
    max_distances = []
    for entry in M:
        max_distances.append(distances[max(entry)][min(entry)])
    return np.mean(max_distances), np.var(max_distances)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial import distance
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from pathlib import Path
import dataframe_image as dfi

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.column_space',200)
pd.set_option('display.max_colwidth', 50)
games = pd.read_csv('games.csv')
user_rank = pd.read_csv('user_ratings.csv')
themes = pd.read_csv('themes.csv')
subcategories = pd.read_csv('subcategories.csv')
mechanics = pd.read_csv('mechanics.csv')
features = games.copy()
features = pd.concat( [features.BGGId , features.iloc[:,-8:-1] ] ,axis =1 )
features = features.merge(subcategories, how="left" ,left_on = 'BGGId' ,right_on= 'BGGId',  suffixes=("_left", "_right"))
features = features.merge(themes, how="left" ,left_on = 'BGGId' ,right_on= 'BGGId',  suffixes=("_left", "_right"))
features = features.merge( mechanics , how="left" ,left_on = 'BGGId' ,right_on= 'BGGId',  suffixes=("_left", "_right"))

class UserRecommender:
    def __init__(self):
        self.min_common_items = 15
        self.min_similarity_score = 0.96
        self.min_neighbors_ratings = 7
        self.n_recommendations = 5

    def games_by_other_users_rating(self,user_id):
        active_user_ratings = user_rank[user_rank['Username'] == user_id]
        active_user_games = active_user_ratings['BGGId']
        common_ratings = user_rank[user_rank['BGGId'].isin(active_user_games)]
        potential_neighbors = common_ratings.groupby('Username').filter(lambda grp: len(grp) >= self.min_common_items)
        potential_neighbors = potential_neighbors.loc[potential_neighbors.Username != user_id]
        similarities = potential_neighbors.groupby('Username').apply(lambda arg1, arg2=active_user_ratings: self.calc_similarity(arg1, arg2))
        similarities.name = 'Similarity'
        relevant_neighbors = similarities[similarities > self.min_similarity_score].index
        recommend_ratings = user_rank.loc[user_rank['Username'].isin(relevant_neighbors) & ~user_rank['BGGId'].isin(active_user_games)]  # only games that the active user did not see
        recommend_ratings = recommend_ratings.groupby('BGGId').filter(lambda grp: len(grp) > self.min_neighbors_ratings)
        game_scores = recommend_ratings.groupby('BGGId').apply(lambda arg1, arg2=similarities: self.calc_game_score(arg1, arg2))
        game_scores.name = 'Score'
        final_recommendation = game_scores.sort_values(ascending=False)[:self.n_recommendations]
        games_name_dis = games[['AvgRating','BGGId', 'Name', 'Description','ImagePath']]
        fr = final_recommendation.to_frame('score')
        fr = fr.reset_index()
        top_picks = fr.merge(games_name_dis, on='BGGId', how='left')
        top_picks = top_picks.drop(['score'], axis=1)
        dfi.export(top_picks, 'other_users.png')
        return 'other_users.png'

    def games_by_user_like(self,user_id):
        features_sparse = csr_matrix(features.iloc[:, 1:].values)
        # define knn model parameters
        model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=11)
        model_knn.fit(features_sparse)
        df_ratings_3 = user_rank[user_rank['Username'] == user_id]
        active_user_id_rating = df_ratings_3.drop(['Username'], axis=1)
        games_clean = games.drop(['Rank:childrensgames', 'Rank:partygames', 'Rank:wargames', 'Rank:cgs',
                                  'Rank:thematic', 'Rank:familygames', 'Rank:abstracts', 'Rank:strategygames',
                                  'Rank:boardgame',
                                  'ImagePath', 'GoodPlayers', 'Family', 'Name', 'Description', 'NumComments',
                                  'StdDev', 'NumWeightVotes', 'LanguageEase'], axis=1)
        active_user_id_table = active_user_id_rating.merge(games_clean, on='BGGId', how='left')
        top_game = active_user_id_table.sort_values(by='Rating', ascending=False).head(1)
        top_game = top_game.drop(['Rating'], axis=1)
        selected_game_id = top_game.iloc[0, 0]
        selected_game_index = games.BGGId[games.BGGId == selected_game_id].index
        select_game_features = features.iloc[selected_game_index, 1:]
        distances, indices = model_knn.kneighbors(select_game_features)
        indices = indices[0][1:11]
        filter = ~games.BGGId.isin([selected_game_id])  # without the game selected
        suggested_games = games.iloc[indices, 0:][filter == True]
        suggested_games = suggested_games[['BGGId', 'Name', 'AvgRating', 'Description', 'ImagePath']]
        suggested_games = suggested_games.reset_index(drop=True)
        dfi.export(suggested_games, 'by_user_likes.png')
        return 'by_user_likes.png'

    def most_popular_games(self):
        games_pop = games.copy()
        games_pop['game_popularity'] = games_pop['AvgRating'] / 10 * games_pop['NumOwned']
        games_pop_top10 = games_pop.sort_values(by='game_popularity', ascending=False).head(10)
        top_ten_pop_games = games_pop_top10[['BGGId', 'Name', 'Description', 'ImagePath']]
        top_ten_pop_games = top_ten_pop_games.reset_index(drop=True)
        dfi.export(top_ten_pop_games, 'topgames.png')


        return 'topgames.png'

    def is_new_user(self, user_id):
        user_ratings = user_rank[user_rank['Username'] == user_id]
        game_num, goog = user_ratings.shape
        if game_num > 10:
            return False

        else:
            return True

    @staticmethod
    def calc_similarity(neighbor_ratings,active_user_ratings):
        neighbor_ratings_compare = neighbor_ratings.merge(active_user_ratings, on='BGGId', how='inner',
                                                          suffixes=('_neighbor', '_active'))

        cos_distance = distance.cosine(neighbor_ratings_compare['Rating_active'],
                                       neighbor_ratings_compare['Rating_neighbor'])

        return 1 - cos_distance

    @staticmethod
    def calc_game_score(game_ratings,similarities):
        game_ratings = game_ratings.join(similarities, on='Username')
        return (game_ratings['Rating'] *
                game_ratings['Similarity']).sum() / \
               game_ratings['Similarity'].sum()





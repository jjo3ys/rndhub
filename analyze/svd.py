import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
from scipy.linalg import svd

data_df = pd.read_csv('/home/jjo3ys/project/score_semi_final.csv')
data_df.columns = ["user","data","rating"]
data_user_rating = data_df.pivot_table("rating", index = 'data', columns = 'user')
user_data_rating = data_df.pivot_table("rating", index = 'user', columns = 'data')
print('data_df:')
print(data_df)
print('data_user_rating:')
print(data_user_rating)
print('user_data_rating:')
print(user_data_rating)
user_data_rating.head(5)
print('user_data_rating.head(5):')
print(user_data_rating)
user_data_rating.fillna(0, inplace = True)
print('user_data_rating.fillna(0):')
print(user_data_rating)
#pivot_table 값을 numpy matrix로 만든 것
matrix = user_data_rating.values
# user_ratings_mean 평균 평점
user_ratings_mean = np.mean(matrix, axis=1)
# R_user_mean : 사용자 - 논문에 대해서 사용자 평균 평점을 뺀것
matrix_user_mean = matrix - user_ratings_mean.reshape(-1,1)
a = pd.DataFrame(matrix_user_mean, columns = user_data_rating.columns).head()
U, sigma, Vt = svds(matrix_user_mean, k =12)
print(U.shape)
print(sigma.shape)
print(Vt.shape)

sigma = np.diag(sigma)
svd_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1,1)
df_svd_preds = pd.DataFrame(svd_user_predicted_ratings, columns = user_data_rating.columns)
print(df_svd_preds)

def recommend_data(df_svd_preds, user_id, ori_data_df, num_recommendations = 5):
    
    user_row_number = user_id - 1
    
    sorted_user_predictions = df_svd_preds.iloc[user_row_number].sort_values(ascending = False)
    user_data = ori_data_df[ori_data_df.user == user_id]
    user_history = user_data.sort_values(["rating"], ascending=False)
    recommendations = ori_data_df[~ori_data_df['data'].isin(user_history['data'])]
    recommendations = recommendations.merge(pd.DataFrame(sorted_user_predictions).reset_index(), on = "data")
    recommendations = recommendations.rename(columns = {user_row_number: "Predictions"}).sort_values("Predictions", ascending=False)
    #recommendations = recommendations.drop_duplicates(["data","Predictions"])
    return user_history, recommendations
while True:
    already_rated, predictions = recommend_data(df_svd_preds, int(input(":")), data_df, 10)
    print(predictions.head(10))



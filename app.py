from flask import Flask,render_template,request
import requests
import numpy as np
import pickle


df = pickle.load(open('model/Movie_data.pkl','rb'))
df_final = pickle.load(open('model/Final_df.pkl','rb'))
similarity = pickle.load(open('model/Similarity.pkl','rb'))
og_df = pickle.load(open('model/og_df.pkl','rb'))



app = Flask(__name__)

@app.route("/")
def home():
    d = df[df['vote_count']>5000].sort_values(by = 'vote_average',ascending = False).head(20)
    d = list(d.id)
    p_data = []
    for i in d:
        item = []
        item.append(df[df['id'] == i].title.iloc[0])
        item.append((df[df['id'] == i].crew.iloc[0]).title())
        item.append(float(df[df['id'] == i].vote_average.iloc[0]))
        pstr = poster(i)
        item.append(pstr)
        item.append(i)
            
        p_data.append(item)
    return render_template('index.html',p_data = p_data)


@app.route("/recommend")
def recom():
    titles = df_final["title"].tolist()
    return render_template("recommendation.html", titles=titles)



def poster(movie_id):
    api_key = "18caf8616e94450f9ed52da39cdb2d79"

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    data = requests.get(url).json()

    poster_path = data.get("poster_path")
    if poster_path is None:
        return "/static/default.avif"   

    return f"https://image.tmdb.org/t/p/w500{poster_path}"





@app.route("/recommend_books", methods = ['post'])
def recommend():
    name = request.form.get('user_input')
    ls = []
    ind = int(df_final[df_final['title'] == name].index[0])
    sim = similarity[ind]
    sim = sorted(list(enumerate(sim)),reverse = True,key = lambda x : x[1])
    for i in sim[1:11]:
        ls.append(i[0])
        
    lst = []
    for i in ls:
        lst.append(int(df.iloc[i].id))

    data = []
    for i in lst:
        item = []
        item.append(df[df['id'] == i].title.iloc[0])
        item.append((df[df['id'] == i].crew.iloc[0]).title())
        item.append(float(df[df['id'] == i].vote_average.iloc[0]))
        pstr = poster(i)
        item.append(pstr)
        item.append(i)
        
        data.append(item)
    titles = df_final["title"].tolist()
    return render_template("recommendation.html", data=data, titles=titles)
    



# review fatching
def review(movie_id):
    api_key = "18caf8616e94450f9ed52da39cdb2d79"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={api_key}"

    data = requests.get(url).json()
    reviews = []
    for i in data.get('results'):
        d = []
        d.append(i.get("author"))
        d.append(i.get("author_details")['rating'])
        d.append(i.get("content"))
        reviews.append(d)
    return reviews


@app.route('/movie_details/<int:movie_id>')
def movie_details(movie_id):
    
    # details part
    og_data = []
    og_data.append(og_df[og_df['id'] == movie_id].title.iloc[0])
    og_data.append(og_df[og_df['id'] == movie_id].cast.iloc[0])
    og_data.append(og_df[og_df['id'] == movie_id].crew.iloc[0])
    og_data.append(og_df[og_df['id'] == movie_id].genres.iloc[0])
    og_data.append(og_df[og_df['id'] == movie_id].overview.iloc[0])
    og_data.append(float(og_df[og_df['id'] == movie_id].runtime.iloc[0]))
    og_data.append(float(og_df[og_df['id'] == movie_id].vote_average.iloc[0]))
    og_data.append(og_df[og_df['id'] == movie_id].release_date.iloc[0])
    og_data.append(og_df[og_df['id'] == movie_id].original_language.iloc[0])
    og_data.append(og_df[og_df['id'] == movie_id].tagline.iloc[0])
    pstr = poster(movie_id)
    og_data.append(pstr)
    
    # review part
    
    review_list = review(movie_id)
    
    
    return render_template("movie-details.html",og_data = og_data,review_list = review_list)


if __name__ == '__main__':
    app.run(debug=True)
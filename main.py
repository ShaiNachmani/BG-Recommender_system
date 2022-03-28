from app import App as BaseApp


class App(BaseApp):
    def __init__(self):
        super().__init__(title='User Recommender')

    def startup(self):
        from recommender import UserRecommender
        self.recommender = UserRecommender()
        self.set_info_text('')

    def do_search(self, user_id):
        if self.recommender.is_new_user(user_id):
            pop_image = self.recommender.most_popular_games()
            s_test = f'Hello {user_id} nice to have you !! as you are a new player here are \nTop 10 picks base on games popularity GL HF: \n '
            self.set_text(s_test)
            self.set_image(pop_image)
        else:
            by_user_likes = self.recommender.games_by_user_like(user_id)
            other_users = self.recommender.games_by_other_users_rating(user_id)
            s_test = f'Hello here are  Top picks  base on game {user_id} likes  : \n '
            s_text2 = f'Top picks for base on gamers like {user_id} :\n '
            self.set_text(s_test)
            self.set_image(by_user_likes)
            self.set_text2(s_text2)
            self.set_image2(other_users)



App().run()


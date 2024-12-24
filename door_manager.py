import pandas as pd

class Door_manager:

    def __init__(self):
        self.data = pd.read_csv('.\csv\data.csv')
        self.stickers = pd.read_csv('.\csv\stickers.csv')
    # load the data

    def get_sticker(self, guild_id):
        return self.stickers[guild_id]

    def update_sticker(self, guild_id, sticker_id):
        self.stickers[guild_id] = sticker_id
        return

    def update_data(self, new_lines):
        return

    # save all new editions to database since last save
    def save_data(self):
        self.data.to_csv('.\csv\data.csv')
        self.stickers.to_csv('.\csv\data.csv')
        return



import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
from prizepicks import PrizePicks
from underdog import Underdog


class SaveToDatabase():
    def __init__(self):
        load_dotenv()
        self.connection_parms = self.connection_details()
        self.prizepick_stats = PrizePicks()
        self.prizepick_data = self.get_prizepick_data()
        self.underdog_data = self.get_underdog_data()

    def get_underdog_data(self):
        underdog = Underdog()
        underdog.get_player_details()
        underdog.get_player_ids()
        underdog.get_team_information()
        underdog.get_player_position(prizepick_data=self.prizepick_data)
        underdog.get_player_stats()
        underdog.check_no_position()

        return underdog.player_information

    def get_prizepick_data(self):
        self.prizepick_stats.get_stats()
        self.prizepick_stats.extract_player_id()
        return self.prizepick_stats.player_stats


    def connection_details(self):
        return {
            'dbname': os.getenv("DATABASE_NAME"),
            'user': os.getenv("DATABASE_USER"),
            'password': os.getenv("DATABASE_PASSWORD"),
            'host': os.getenv("DATABASE_HOST"),
            'port': os.getenv("DATABASE_PORT"),
        }

    def insert_underdog_data(self):
        conn = psycopg2.connect(**self.connection_parms)
        cursor = conn.cursor()

        insert_query = """
                    INSERT INTO underdog (last_update, player_name, team, opponent, game_date, stat_type, line, over_multiplier, under_multiplier, position, game_time, league)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """

        current_timestamp = datetime.now()

        for data in self.underdog_data:
            for stat in data["stats"]:
                values = (
                    current_timestamp,
                    data['name'],
                    data['team'],
                    data['opponent'],
                    datetime.strptime(data['game_date'], '%Y-%m-%d').date(),  # Convert string to date
                    stat['stat_type'],
                    float(stat['line']),
                    stat['over_multiplier'],
                    stat['under_multiplier'],
                    data["position"],
                    data["game_time"],
                    data["league"]
                )

                cursor.execute(insert_query, values)

        conn.commit()
        cursor.close()
        conn.close()

    def insert_prizepick_data(self):
       conn = psycopg2.connect(**self.connection_parms)
       cursor = conn.cursor()

       insert_query = """
                  INSERT INTO prizepick (last_update, player_name, team, opponent, game_date, stat_type, line, position, game_time, league)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
              """

       current_timestamp = datetime.now()

       for data in self.prizepick_data:
           values = (
               current_timestamp,
               data['display_name'],
               data['team'],
               data['opponent'],
               datetime.strptime(data['game_date'], '%Y-%m-%d').date(),  # Convert string to date
               data['stat_type'],
               float(data['line']),
               data["position"],
               data["game_time"],
               data["league"]
           )
           cursor.execute(insert_query, values)

       conn.commit()
       cursor.close()
       conn.close()

def main():
    db = SaveToDatabase()
    db.insert_prizepick_data()
    db.insert_underdog_data()

if __name__ == "__main__":
    main()
from datetime import datetime, timedelta
import requests


class PrizePicks:
    def __init__(self):
        self.pp_data = self.get_api_data()
        self.player_stats = []

    def get_api_data(self):
        return requests.get("https://partner-api.prizepicks.com/projections?league_id=121").json()

    def extract_player_id(self):
        for player_id in self.player_stats:
            for player in self.pp_data["included"]:
                if player_id["player_id"] == player["id"]:
                    player_id["display_name"] = player["attributes"]["display_name"]
                    player_id["team"] = player["attributes"]["team"]
                    player_id["position"] = player["attributes"]["position"]
                    break

    def get_stats(self):
        for player in self.pp_data["data"]:
            prizepick_time = datetime.fromisoformat(player["attributes"]["start_time"])
            converted_utc_time_date = prizepick_time + timedelta(hours=4)
            utc_time = converted_utc_time_date.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

            league = player["attributes"].get("tv_channel")
            league = league.split("/")[-1].upper() if league else "N/A"

            self.player_stats.append({
                "player_id": player["relationships"]["new_player"]["data"]["id"],
                "opponent": player["attributes"]["description"].split(" ")[0],
                "game_date": utc_time.split("T")[0],
                "game_time": utc_time.split("T")[1],
                "line": player["attributes"]["line_score"],
                "stat_type": player["attributes"]["stat_type"],
                "league": league
            })

        ### USE IF YOU NEED TO BREAK STATS UP INTO ONE PLAYER
        # for player in self.pp_data["data"]:
        #     player_id = player["relationships"]["new_player"]["data"]["id"]
        #
        #     found = False
        #     for existing_stat in self.player_stats:
        #         if player_id == existing_stat["player_id"]:
        #             existing_stat["stats"].append({
        #                 "line": player["attributes"]["line_score"],
        #                 "stat_type": player["attributes"]["stat_type"],
        #             })
        #             found = True
        #             break
        #
        #     if not found:
        #         self.player_stats.append({
        #             "player_id": player["relationships"]["new_player"]["data"]["id"],
        #             "opponent": player["attributes"]["description"].split(" ")[0],
        #             "game_date": player["attributes"]["start_time"].split("T")[0],
        #             "stats": [{
        #                 "line": player["attributes"]["line_score"],
        #                 "stat_type": player["attributes"]["stat_type"],
        #             }]
        #         })





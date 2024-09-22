import requests

class Underdog():
    def __init__(self):
        self.underdog_data = self.get_api_data()
        self.player_information = []

    def get_api_data(self):
        return requests.get("https://api.underdogfantasy.com/beta/v5/over_under_lines").json()

    def get_player_details(self):
        for player in self.underdog_data["players"]:
            if player["sport_id"] == "LOL":
                self.player_information.append({
                    "name": player["last_name"],
                    "player_id": player["id"],
                    "team_id": player["team_id"]
                })

    def get_player_ids(self):
        for player_id in self.player_information:
            for player in self.underdog_data["appearances"]:
                if player_id["player_id"] == player["player_id"]:
                    player_id["stat_id"] = player["id"]
                    break


    def get_team_information(self):
        for team_id in self.player_information:
            for team_details in self.underdog_data["games"]:
                game_date = team_details["scheduled_at"].split("T")[0]
                game_time = team_details["scheduled_at"].split("T")[1]
                if team_id["team_id"] in (team_details["away_team_id"], team_details["home_team_id"]):
                    if ":" in team_details["title"]:
                        team_list = team_details["title"].split(":")[1].split("vs.")
                        league = team_details["title"].split(":")[0]
                    else:
                        team_list = team_details["title"].split("vs")
                        league = team_details["sport_id"]

                    if team_id["team_id"] in team_details["away_team_id"]:
                        team = team_list[0].strip()
                        opponent = team_list[1].strip()
                        team_id["team"] = team
                        team_id["opponent"] = opponent
                        team_id["game_date"] = game_date
                        team_id["game_time"] = game_time
                        team_id["league"] = league

                    elif team_id["team_id"] in team_details["home_team_id"]:
                        team = team_list[1].strip()
                        opponent = team_list[0].strip()
                        team_id["team"] = team
                        team_id["opponent"] = opponent
                        team_id["game_date"] = game_date
                        team_id["game_time"] = game_time
                        team_id["league"] = league


    def get_player_stats(self):
        for player_id in self.player_information:
            for stat in self.underdog_data["over_under_lines"]:
                if player_id["stat_id"] == stat["over_under"]["appearance_stat"]["appearance_id"]:
                    over_multiplier, under_multiplier = None, None

                    for option in stat["options"]:
                        if option["choice"] == "higher":
                            over_multiplier = float(option["payout_multiplier"])
                        elif option["choice"] == "lower":
                            under_multiplier = float(option["payout_multiplier"]) if option["payout_multiplier"] != None else \
                            float(option["payout_multiplier"])

                    if "stats" in player_id:
                        player_id["stats"].append({
                            "line": stat["stat_value"],
                            "stat_type": stat["over_under"]["appearance_stat"]["display_stat"],
                            "over_multiplier": over_multiplier,
                            "under_multiplier": under_multiplier,
                        })
                    else:
                        player_id["stats"] = [{
                            "line": stat["stat_value"],
                            "stat_type": stat["over_under"]["appearance_stat"]["display_stat"],
                            "over_multiplier": over_multiplier,
                            "under_multiplier": under_multiplier,
                        }]


    def get_player_position(self, prizepick_data):
        for player in self.player_information:
            for prizepick_position in prizepick_data:
                if player["name"].lower() == prizepick_position["display_name"].lower():
                        player["position"] = prizepick_position["position"]

    def check_no_position(self):
        for player in self.player_information:
            if "position" not in player or player["position"] is None:
                player["position"] = "N/A"

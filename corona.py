from errbot import BotPlugin, botcmd
import requests
from datetime import datetime

API_URL="https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Coronaf%C3%A4lle_in_den_Bundesl%C3%A4ndern/FeatureServer/0/query?where=1%3D1&outFields=OBJECTID_1,LAN_ew_AGS,LAN_ew_GEN,LAN_ew_BEZ,LAN_ew_EWZ,Fallzahl,Aktualisierung,faelle_100000_EW,cases7_bl_per_100k,Death&returnGeometry=false&outSR=&f=json"

class Corona(BotPlugin):
    """
    This plugin prints the current corona statistics for germany
    """
    @botcmd(split_args_with=None)
    def corona(self, msg, args):  # a command callable with !tryme
        """
        print corona stats for germany or specific state
        """
        if self.search(args[0]) != None:
          return self.print_formatted(self.search(args[0]))
        else:
          return "Konnte keine Coronadaten für {} abrufen.".format(args[0])

    def search(self, bundesland):
      data = requests.get(API_URL).json()
      by_state = {}
      sum_fallzahl = 0
      sum_faelle_100k_ew = 0
      sum_cases7_bl_per_100k = 0
      sum_deaths = 0

      for state in data["features"]:
        by_state[state["attributes"]["LAN_ew_GEN"]] = {
          "msg": "Daten für {}".format(state["attributes"]["LAN_ew_GEN"]),
          "data": {
            "Fallzahl": state["attributes"]["Fallzahl"],
            "Aktualisierung": self.convert_timestamp(state["attributes"]["Aktualisierung"]),
            "Fälle / 100k Einwohner": state["attributes"]["faelle_100000_EW"],
            "Bundeslandweite Fälle der letzten 7 Tage/100.000 EW": state["attributes"]["cases7_bl_per_100k"],
            "Anzahl Todesfälle": state["attributes"]["Death"]
          }
        }
        sum_fallzahl = sum_fallzahl + state["attributes"]["Fallzahl"]
        sum_faelle_100k_ew = sum_faelle_100k_ew + state["attributes"]["faelle_100000_EW"]
        sum_cases7_bl_per_100k = sum_cases7_bl_per_100k + state["attributes"]["cases7_bl_per_100k"]
        sum_deaths = sum_deaths + state["attributes"]["Death"]

      country = {
        "msg": "Daten für Deutschland (Summe alle Bundesländer)",
        "data": {
          "Fallzahl": sum_fallzahl,
          "Aktualisierung": 0,
          "Fälle / 100k Einwohner": sum_faelle_100k_ew,
          "Deutschland - Fälle der letzten 7 Tage/100.000 EW": sum_cases7_bl_per_100k,
          "Anzahl Todesfälle": sum_deaths
        }
      }
      
      if bundesland in by_state:
        return by_state[bundesland]
      else:
        return country

    def print_formatted(self, data):
      s = ""
      s = s + data["msg"] + "\n"
      for key, value in data["data"].items():
        s = s + "{}: {}\n".format(str(key), str(value))
      return s

    def convert_timestamp(self, t):
      t = t * (1/1000)
      dt = datetime.fromtimestamp(t)
      return dt.strftime("%Y-%m-%d %H:%M:%S")

from errbot import BotPlugin, botcmd
import requests

API_URL="https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Coronaf%C3%A4lle_in_den_Bundesl%C3%A4ndern/FeatureServer/0/query?where=1%3D1&outFields=OBJECTID_1,LAN_ew_AGS,LAN_ew_GEN,LAN_ew_BEZ,LAN_ew_EWZ,Fallzahl,Aktualisierung,faelle_100000_EW,cases7_bl_per_100k,Death&returnGeometry=false&outSR=&f=json"

class Corona(BotPlugin):
    """
    This plugin prints the current corona statistics for germany
    """
    @botcmd  # flags a command
    def corona(self, msg, args):  # a command callable with !tryme
        """
        print corona stats for germany or specific state
        """
        if self.search(args[0]) != None:
          return self.print_formatted(corona(args[0]))
        else:
          return "Konnte keine Coronadaten für {} abrufen.".format(args[0])

    def search(bundesland):
      data = requests.get(API_URL).json()
      by_state = {}
      sum_fallzahl = 0
      sum_faelle_100k_ew = 0
      sum_cases7_bl_per_100k = 0
      sum_deaths = 0

      for state in data["features"]:
        by_state[state["attributes"]["LAN_ew_GEN"]] = {
          "Fallzahl": state["attributes"]["Fallzahl"],
          "Aktualisierung": state["attributes"]["Aktualisierung"],
          "Fälle / 100k Einwohner": state["attributes"]["faelle_100000_EW"],
          "Bundeslandweite Fälle der letzten 7 Tage/100.000 EW": state["attributes"]["cases7_bl_per_100k"],
          "Anzahl Todesfälle": state["attributes"]["Death"]
        }
        sum_fallzahl = sum_fallzahl + state["attributes"]["Fallzahl"]
        sum_faelle_100k_ew = sum_faelle_100k_ew + state["attributes"]["faelle_100000_EW"]
        sum_cases7_bl_per_100k = sum_cases7_bl_per_100k + state["attributes"]["cases7_bl_per_100k"]
        sum_deaths = sum_deaths + state["attributes"]["Death"]

      by_state["all"] = {
        "Fallzahl": sum_fallzahl,
        "Aktualisierung": 0,
        "Fälle / 100k Einwohner": sum_faelle_100k_ew,
        "Deutschland - Fälle der letzten 7 Tage/100.000 EW": sum_cases7_bl_per_100k,
        "Anzahl Todesfälle": sum_deaths
      }
      
      if bundesland in by_state:
        return by_state[bundesland]
      else:
        return None

    def print_formatted(data):
      s = ""
      for key, value in data.items():
        s = s + "{}: {}\n".format(str(key), str(value))
      return s
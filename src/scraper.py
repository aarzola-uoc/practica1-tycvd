import requests
from bs4 import BeautifulSoup
import csv
import html5lib

class EuroligaScraper():

    def __init__(self):
        self.jornada_inicio = 1
        self.jornada_fin = 29
        self.url = "https://www.euroleague.net/main/results?phasetypecode=RS&seasoncode=E2019&gamenumber="
        self.partidos = [["Id", "Date", "HomeTeam", "HomeScore", "VisitingTeam", "VisitingScore", "Link"]]
        self.jugadores = [["MatchId", "Team", "PlayerNumber", "PlayerName", "Min", "Pts", "2FG", "3FG", "FT",
                            "O", "D", "T", "As", "St", "To", "Fv", "Ag", "Cm", "Rv", "PIR",]]
        self.contador = 1

    def get_html(self, page, parser):
        # Obtenemos el HTML de la página "page" utilizando el parseador "parser" 
        # y la librería BeautifulSoup
        return BeautifulSoup(page, parser)

    def parse_player_stats_table(self, table, teamName):
        # Iteramos por todos los elementos de la tabla para obtener las estadísticas
        # individuales de cada jugador
        for z in table:
                stats = z.find_all("td")
                jugador = [self.contador, teamName]
                for t in stats:
                    temp = t.get_text()
                    # Si el valor para una determinada estadística es vacío, asignamos el
                    # valor 0
                    if temp != '\xa0':
                        jugador.append(temp)
                    else:
                        jugador.append("0")
                # Añadimos las estadísticas del jugador al vector con todas las estadísticas
                # que luego exportaremos a csv
                self.jugadores.append(jugador)

    def get_players_stats(self, link):
        # Obtener estadísticas de los jugadores
        page_palyers = requests.get(link)
        if page_palyers.status_code == 200:
            
            print("\t\t[INFO] Obteniendo estadísticas de los jugadores...")
            soup_players = self.get_html(page_palyers.content, 'html5lib')
            
            # Buscamos el elemento div con la clase LocalClubStatsContainer que es
            # el elemento que contiene la tabla con las estadísticas de los jugadores
            # del equipo local
            homeTeamStats_html = soup_players.find("div", {"class":"LocalClubStatsContainer"})
            
            # Obtenemos el nombre del equipo local
            homeTeamName = homeTeamStats_html.div.span.get_text()

            # Obtenemos todas las filas de la tabla que contienen las
            # estadísticas del partido para los jugadores del equipo local
            homePlayersStats = homeTeamStats_html.div.next_sibling.next_sibling.table.tbody.find_all("tr")
            self.parse_player_stats_table(homePlayersStats, homeTeamName)

            # Buscamos el elemento div con la clase RoadClubStatsContainer que es
            # el elemento que contiene la tabla con las estadísticas de los jugadores
            # del equipo visitante
            vistingTeamStats_html = soup_players.find("div", {"class":"RoadClubStatsContainer"})

            # Obtenemos el nombre del equipo visitante
            vistingTeamName = vistingTeamStats_html.div.span.get_text()

            # Obtenemos todas las filas de la tabla que contienen las
            # estadísticas del partido para los jugadores del equipo visitante
            vistingPlayersStats = vistingTeamStats_html.div.next_sibling.next_sibling.table.tbody.find_all("tr")
            self.parse_player_stats_table(vistingPlayersStats, vistingTeamName)

            print("\t\t[OK] Obtenidas las estadísticas de los jugadores.\n")
        else:
            print("\t\t[ERROR] No se han podido obtener las estadísticas de este partido.\n")
    
    def get_matches_and_players_stats(self, page):
        # Obtenemos estadísticas de los partidos
        soup = self.get_html(page.content, 'html.parser')
        
        # Buscamos todos los elementos "div" con la clase "game played"
        # que es la estructura que contiene los datos de los partidos
        # de la jornada
        gamesplayed = soup.find_all("div", {"class":"game played"})
        
        # Iteramos por cada uno de los partidos de la jornada
        for x in gamesplayed:
            
            # Obtenemos el enlace de los detalles del partido para luego
            # buscar las estadísticas de los jugadores
            enlace_html = x.find('a')
            enlace = "https://www.euroleague.net" + enlace_html.get('href')
            
            # Buscamos los elementos span con clase name para obtener los
            # nombres de los equipos
            equipos_html = x.find_all("span", {"class":"name"})
            equipos = []
            for y in equipos_html:
                equipos.append(y.get_text())
            
            # Buscamos el elemento span con clase date para obtener la fecha
            # del partido
            fecha_html = x.find("span", {"class":"date"})
            fecha = fecha_html.get_text()
            
            # Buscamos los elementos span con clase score para obtener el resultado
            # de cada equipo en el partido
            resultados_html = x.find_all("span", {"class":"score"})
            resultados = []
            for y in resultados_html:
                resultados.append(y['data-score'])
            
            # Componemos el vector que contiene todos los datos del partido
            partido = [self.contador, fecha, equipos[0], resultados[0], equipos[1], resultados[1], enlace]
            print("\tPartido " + str(self.contador) + ": " + equipos[0] + " [" + resultados[0] + "]" + " - " + equipos[1] + " [" + resultados[1] + "]")

            # Llamamos a la función que obtiene las estadísticas de los jugadores
            # para el partido
            self.get_players_stats(enlace)

            #  Incluimos el partido en el vector que contiene todos los partidos
            self.partidos.append(partido)
            self.contador+=1

    def scrape(self):
        # Iteramos por cada jornada para obtener los datos
        for i in range(self.jornada_inicio, self.jornada_fin): 
            print("Jornada " + str(i))
            page = requests.get(self.url + str(i))
            # En caso de que la consulta a la url correspondiente nos devuelva el código HTTP 200
            # procedemos a obtener los datos. En cualquier otro caso mostramos mensaje de error
            if page.status_code == 200:
                self.get_matches_and_players_stats(page)
            else:
                print("[ERROR] No se han podido obtener los datos de la jornada" + self.contador + ".\n")

    def data2csv(self):
        # Exportamos a csv los partidos si hay más registros que la cabecera
        if len(self.partidos) > 1:
            with open('../csv/euroliga.csv', 'w', newline='') as myfile:
                writer = csv.writer(myfile, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
                writer.writerows(self.partidos)
        # Exportamos a csv las estadísticas de los jugadores si hay más registros que la cabecera
        if len(self.jugadores) > 1:
            with open('../csv/euroliga_players.csv', 'w', newline='') as myfile:
                writer = csv.writer(myfile, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
                writer.writerows(self.jugadores)
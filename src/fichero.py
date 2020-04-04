import requests
from bs4 import BeautifulSoup
import csv
import html5lib

jornada_inicio = 1
jornada_fin = 29
url = "https://www.euroleague.net/main/results?phasetypecode=RS&seasoncode=E2019&gamenumber="
partidos = [["Id", "Date", "HomeTeam", "HomeScore", "VisitingTeam", "VisitingScore", "Link"]]
jugadores = [["MatchId", "Team", "PlayerNumber", "PlayerName", "Min", "Pts", "2FG", "3FG", "FT",
                "O", "D", "T", "As", "St", "To", "Fv", "Ag", "Cm", "Rv", "PIR",]]
contador = 1

for i in range(jornada_inicio, jornada_fin):
    
    print("Jornada " + str(i))
    page = requests.get(url + str(i))
    if page.status_code == 200:
        
        soup = BeautifulSoup(page.content, 'html.parser')
        gamesplayed = soup.find_all("div", {"class":"game played"})
        for x in gamesplayed:
            
            enlace_html = x.find('a')
            enlace = "https://www.euroleague.net" + enlace_html.get('href')
            
            equipos_html = x.find_all("span", {"class":"name"})
            equipos = []
            for y in equipos_html:
                equipos.append(y.get_text())
            
            fecha_html = x.find("span", {"class":"date"})
            fecha = fecha_html.get_text()
            
            resultados_html = x.find_all("span", {"class":"score"})
            resultados = []
            for y in resultados_html:
                resultados.append(y['data-score'])
            
            partido = [contador, fecha, equipos[0], resultados[0], equipos[1], resultados[1], enlace]
            print("\tPartido " + str(contador) + ": " + equipos[0] + " [" + resultados[0] + "]" + " - " + equipos[1] + " [" + resultados[1] + "]")

            # Obtener estadísticas de los jugadores
            page_palyers = requests.get(enlace)
            if page_palyers.status_code == 200:
                
                print("\t\t[INFO] Obteniendo estadísticas de los jugadores...")

                soup_players = BeautifulSoup(page_palyers.content, 'html5lib')
                homeTeamStats_html = soup_players.find("div", {"class":"LocalClubStatsContainer"})
                homeTeamName = homeTeamStats_html.div.span.get_text()

                homeplayersstats = homeTeamStats_html.div.next_sibling.next_sibling.table.tbody.find_all("tr")

                for z in homeplayersstats:
                    stats = z.find_all("td")
                    jugador = [contador, homeTeamName]
                    for t in stats:
                        temp = t.get_text()
                        if temp != '\xa0':
                            jugador.append(temp)
                        else:
                            jugador.append("0")
                    jugadores.append(jugador)

                vistingTeamStats_html = soup_players.find("div", {"class":"RoadClubStatsContainer"})
                vistingTeamName = vistingTeamStats_html.div.span.get_text()

                vistingplayersstats = vistingTeamStats_html.div.next_sibling.next_sibling.table.tbody.find_all("tr")

                for z in vistingplayersstats:
                    stats = z.find_all("td")
                    jugador = [contador, vistingTeamName]
                    for t in stats:
                        temp = t.get_text()
                        if temp != '\xa0':
                            jugador.append(temp)
                        else:
                            jugador.append("0")
                    jugadores.append(jugador)
                
                print("\t\t[OK] Obtenidas las estadísticas de los jugadores.\n")
            else:
                print("\t\t[ERROR] No se han podido obtener las estadísticas de este partido.\n")

            partidos.append(partido)
            contador+=1

if partidos:
    with open('../csv/euroliga.csv', 'w', newline='') as myfile:
        writer = csv.writer(myfile, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
        writer.writerows(partidos)

if jugadores:
    with open('../csv/euroliga_players.csv', 'w', newline='') as myfile:
        writer = csv.writer(myfile, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
        writer.writerows(jugadores)
import requests
from bs4 import BeautifulSoup
import csv

jornada_inicio = 1
jornada_fin = 29
url = "https://www.euroleague.net/main/results?phasetypecode=RS&seasoncode=E2019&gamenumber="
partidos = [["Id", "Date", "HomeTeam", "HomeScore", "VisitingTeam", "VisitingScore", "Link"]]
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

            partidos.append(partido)
            contador+=1

if partidos:
    with open('euroliga.csv', 'w', newline='') as myfile:
        writer = csv.writer(myfile, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
        writer.writerows(partidos)
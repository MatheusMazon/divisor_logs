import matplotlib.pyplot as plt
import numpy as np
from math import sin, cos, sqrt, atan2,radians
import csv
from os import listdir
from os.path import isfile, join, isdir
import os

def distmetros(lati,latf,long_i,long_f):
	R = 6373000
	lat1 = lati
	lon1 = long_i
	lat2 = latf
	lon2 = long_f
	dlon = radians(long_f-long_i)
	dlat = radians(latf-lati)
	a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	distance = R * c
	return distance

def variacao(tabela):
	perpendicular = 0
	latitude_inicial = tabela['Latitude'][1]
	longitude_inicial = tabela['Longitude'][1]
	i=2
	latitude_final = tabela['Latitude'][i]
	longitude_final = tabela['Longitude'][i]
	while distmetros(latitude_inicial*0.01,latitude_final*0.01,longitude_inicial*0.01,longitude_final*0.01)<1.8:
		latitude_final = tabela['Latitude'][i]
		longitude_final = tabela['Longitude'][i]
		i=i+1
	if abs(abs(longitude_final)-abs(longitude_inicial))>abs(abs(latitude_final)-abs(latitude_inicial)):
		latitudeperpendicular = False
		variacao = abs(abs(longitude_final)-abs(longitude_inicial))
		delimitador1 = latitude_inicial - variacao
		delimitador2 = latitude_inicial + variacao
		perpendicular = longitude_inicial
	else:
		latitudeperpendicular = True
		variacao = abs(abs(latitude_final)-abs(latitude_inicial))
		delimitador1 = longitude_inicial - variacao
		delimitador2 =longitude_inicial + variacao
		perpendicular = latitude_inicial
	#print(delimitador1)
	#print(delimitador2)
	#print(latitudeperpendicular)
	return latitudeperpendicular, perpendicular, delimitador1, delimitador2


###############################################################
def dentro(min, max, analise):
	if (analise <= max) and (analise >= min):
		return True
	return False
#tabela = np.genfromtxt('GPS-15-09.csv', delimiter=';', skip_header=10, skip_footer=10, names=['Longitude', 'Latitude',
																							  #'Speed', 'Tempo'])
#nome_arquivo - nome do log a ser analisado
#latitude_dir - booleano indicando True se a latitude é perpendicular e False cc
#perpendicular - coordenada da reta perpendicular ao início
#minimo - minima diferença que a pista pode assumir
#maximo - maxima diferença que a pista pode assumir
def dividir(tabela, latitude_dir, perpendicular, minimo, maximo):
	# abre tabela de log csv e salva em um dicionário
	#vetor que guarda tempos de voltas
	tempos = []
	#tempo de início do percurso, usado de referência para calcular todos os tempos de volta
	tempo_inicial = tabela['Tempo'][0]
	#ponto inicial do percurso
	ponto_anterior = perpendicular
	#variável booleana que indica se as coords podem ser avaliadas ou não
	contar = False
	for row in tabela:
		if latitude_dir:
			ponto_atual = row['Latitude']  # atualiza o ponto atual
			#se está dentro do range permitido, se o ponto atual está depois (em cima) da reta perpendicular e
			# o anterior antes e se é permitido avaliar as coords
			if dentro(minimo, maximo, row['Longitude']) and \
					((ponto_anterior - perpendicular)*(ponto_atual - perpendicular) <= 0) and contar:
				tempos.append(row['Tempo'] - tempo_inicial)  # marca o delta de tempo
				#print(row['Longitude'], row['Latitude'], row['Tempo'])
				contar = False
			if not dentro(minimo, maximo, row['Longitude']):
				contar = True  # quando sair do range permitido, pode voltar a contar
			ponto_anterior = ponto_atual  # atualiza o ponto anterior para a próxima iteração
		else:
			ponto_atual = row['Longitude']
			if dentro(minimo, maximo, row['Latitude']) and \
					((ponto_anterior - perpendicular) * (ponto_atual - perpendicular) <= 0) and contar:
				tempos.append(row['Tempo'] - tempo_inicial)
				#print(row['Longitude'], row['Latitude'], row['Tempo'])
				contar = False
			if not dentro(minimo, maximo, row['Latitude']):
				contar = True
			ponto_anterior = ponto_atual

	return tempos


############################################################3
def listar_pastas(pasta):
 	pastas = [f for f in listdir(pasta) if isdir(join(pasta, f))]

 	return pastas

def listar_arquivos(pasta):
 	arquivos = [f for f in listdir(pasta) if isfile(join(pasta, f))]

 	return arquivos


def files(t,path):
	numero_voltas = len(t)

	i = 0
	inicio_volta = 0

	arq_gps = listar_arquivos(path+'/GPS')
	GPS = np.genfromtxt(path+'/GPS/'+arq_gps[0], delimiter = ';', skip_header = 1, names = ['lati', 'longi', 'veloc', 'tempo'])

	print("\nArquivo "+path+"/"+arq_gps[0]+":")

	os.system("mkdir -p "+path+"/Voltas/Volta_"+str(i+1))
	

	with open(path+'/GPS/'+arq_gps[0], 'r') as csv_file:
		reader = csv.reader(csv_file,  delimiter = ';')
		headers = list(reader)[0]

	writer = csv.writer(open(path+'/Voltas/Volta_'+str(i+1)+'/GPS.csv', 'w'), delimiter=';')
	writer.writerow(headers)

	inicio_volta = GPS['tempo'][0]

	for line in GPS:

		delta = float(line['tempo']) - float(inicio_volta)

		if(i < numero_voltas):
			if(delta <= t[i]):

				writer.writerow(line)

			else:
				print("  Volta "+str(i+1))

				i+=1
				os.system("mkdir -p "+path+"/Voltas/Volta_"+str(i+1))

				writer = csv.writer(open(path+'/Voltas/Volta_'+str(i+1)+'/GPS.csv', 'w'), delimiter=';')
				writer.writerow(headers)
		else:
			writer.writerow(line)


	for arq in listar_arquivos(path+'/CAN/CSV_Files'):
		print("\nArquivo "+path+"/"+arq+":")

		i = 0

		with open(path+'/CAN/CSV_Files/'+arq, 'r') as csv_file:
			reader = csv.reader(csv_file,  delimiter = ';')
			headers = list(reader)[0]
			col = len(headers)

		arquivo = np.genfromtxt(path+'/CAN/CSV_Files/'+arq, delimiter = ';', skip_header = 1, usecols = range(0, col-1))
		#print(arquivo[0])


		writer = csv.writer(open(path+'/Voltas/Volta_'+str(i+1)+'/'+arq, 'w'), delimiter=';')
		writer.writerow(headers)


		inicio_volta = arquivo[col - 1][0]

		for line in arquivo:

			if(i < numero_voltas):
				if(line[col-2] <= t[i]):

					writer.writerow(line)

				else:
					print("  Volta "+str(i+1))
					i+=1

					writer = csv.writer(open(path+'/Voltas/Volta_'+str(i+1)+'/'+arq, 'w'), delimiter=';')
					writer.writerow(headers)
			else:
				writer.writerow(line)


def main():
	for dia in listar_pastas('Logs'):
		for hora in listar_pastas('Logs/'+dia):
			path = "Logs/"+dia+"/"+hora

			arq_gps = listar_arquivos(path+'/GPS')
			tabela = np.genfromtxt(path+'/GPS/'+arq_gps[0], delimiter=';', skip_header=1, names=['Longitude', 'Latitude','Speed', 'Tempo'])
			latitudeperpendicular,perpendicular,delimitador1, delimitador2 = variacao(tabela)
			t = dividir(tabela, latitudeperpendicular, perpendicular,delimitador1,delimitador2)
			files(t,path)

main()

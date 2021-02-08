import streamlit as st
from state import provide_state
import datetime
import time
import pandas as pd 
import numpy as np
import itertools
import snscrape.modules.twitter as sntwitter
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import seaborn as sns

# Parámetros
activities = ["Seleccione", "Twitter-usuario","Twitter-término","Twitter-ciudad","EDA","Plot","Model Building","About", "test"]

#Funciones

# Convertir a excel
def to_excel(df):
	output = BytesIO()
	writer = pd.ExcelWriter(output, engine='xlsxwriter', options = {'remove_timezone': True})
	df.to_excel(writer, sheet_name='Sheet1')
	writer.save()
	processed_data = output.getvalue()
	return processed_data

def get_table_download_link(df):
	"""Generates a link allowing the data in a given panda dataframe to be downloaded
	in:  dataframe
	out: href string
	"""
	val = to_excel(df)
	b64 = base64.b64encode(val)  # val looks like b'...'
	return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download csv file</a>' # decode b'abc' => abc

# Obtener tweets de usuarios y palabras entre 2 fechas
def obtener_tweets (cuenta,palabra,f_ini, f_fin, captura):
    maxTweets = 5000
    cuenta_twitter=str(cuenta)
    palabras_clave=str(palabra)
    fecha_ini=str(f_ini)
    fecha_fin=str(f_fin)
    
    parametros_twitter="from:@"+cuenta_twitter+" + since:"+fecha_ini+" until:"+fecha_fin + " "+ palabras_clave

    # Capturo tweets de un usuario en particular y almaceno en dataframe
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(parametros_twitter).get_items()):
        if i > maxTweets :
            break
        captura['username'].append(tweet.username)
        captura['palabra'].append(palabras_clave)
        date=str(tweet.date.year)+"-"+str(tweet.date.month)+"-"+str(tweet.date.day)+" "+str(tweet.date.hour)+":"+str(tweet.date.minute)+":"+str(tweet.date.second)
        captura['fecha'].append(date)
        captura['contenido'].append(tweet.content)
    return captura

# Programa
@provide_state
def main(state):
	st.title("Exploración de redes sociales")
	state.inputs1 = state.inputs1 or set()
	state.inputs2 = state.inputs2 or set()
	choice = st.sidebar.selectbox("Seleccione la red social de su interés",activities)

	if choice == "Seleccione":
		st.subheader("Seleccione una de las opciones en el menú lateral")

	elif choice == "Twitter-usuario":
     
		# ------ Input datos de usuarios
		st.subheader("Usuarios")

		c1, c2 = st.beta_columns([2, 1])
		input_string = c1.text_input("Agregar usuario")
		state.inputs1.add(input_string)

        # Obtiene el estado anterior del index
		last_index1 = len(state.inputs1) - 1 if state.inputs1 else None

        # Selecciono la última entrada de acuerdo al index
		c2.selectbox("Usuarios agregados", options=list(state.inputs1), index=last_index1)
		lista_cuentas=list(state.inputs1)
		cuentas_twitter = st.multiselect("Seleccionar usuarios",lista_cuentas)
		# -----------------------------------
  
		# ------ Input palabras clave
		st.subheader("Palabras clave")

		c3, c4 = st.beta_columns([2, 1])
		input_string2 = c3.text_input("Agregar palabra")
		state.inputs2.add(input_string2)

        # Obtiene el estado anterior del index
		last_index2 = len(state.inputs2) - 1 if state.inputs2 else None

        # Selecciono la última entrada de acuerdo al index
		c4.selectbox("Palabras agregadas", options=list(state.inputs2), index=last_index2)
		lista_palabras=list(state.inputs2)
		palabras_busqueda = st.multiselect("Seleccionar palabras",lista_palabras)
		st.write(cuentas_twitter, palabras_busqueda)
		# -----------------------------------
		# ------ Input fechas
		st.subheader("Rango de fechas")
		
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(days=1)
		c5, c6 = st.beta_columns([1, 1])

		f_ini = c5.date_input('Fecha inicio', today)
		f_fin = c6.date_input('Fecha final', tomorrow)

		if f_ini < f_fin:
			st.success('Fecha inicio: `%s`\n\nFecha final:`%s`' % (f_ini, f_fin))
		else:
			st.error('Error: La fecha final debe ir después de la fecha inicial.')
		# -----------------------------------

		# ------- Botón analizar
		if st.button('Extraer tweets'):
			# Itero y aplico función
			captura = {"username":[],"palabra":[],"fecha":[],"contenido":[]}

			for i in range(0,len(cuentas_twitter)):
				for j in range(0,len(palabras_busqueda)):
					cuenta=cuentas_twitter[i]
					palabra=palabras_busqueda[j]
					captura=obtener_tweets(cuenta,palabra,f_ini, f_fin, captura)
					time.sleep(5)

			df1=pd.DataFrame.from_dict(captura) 
			st.write('Se encontraron ', len(df1), " tweets")
  			# Imprimo resultado
			st.dataframe(df1.head())
			df = df1 # your dataframe
			st.markdown(get_table_download_link(df), unsafe_allow_html=True)

			fig, ax = plt.subplots()
			ax=sns.countplot("username", data=df)
			st.pyplot(fig)

			col1, col2 = st.beta_columns(2)

			col1.subheader("Usuario - Palabra")
			fig, ax = plt.subplots()
			ax=sns.countplot(y="username", hue="palabra", data=df1)
			col1.pyplot(fig)

			col2.subheader("Palabra - Usuario")
			fig2, ax2 = plt.subplots()
			ax2=sns.countplot(y="palabra", hue="username", data=df1)   
			col2.pyplot(fig2)



		# -----------------------------------
	elif choice == 'test':
		arr = np.random.normal(1, 1, size=100)
		fig, ax = plt.subplots()
		ax.hist(arr, bins=20)
		st.pyplot(fig)


	elif choice == 'About':
		st.subheader("About")
		st.text("")


if __name__ == "__main__":
	main()
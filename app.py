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
from facebook_scraper import get_posts
from PIL import Image

# Parámetros
activities = ["Seleccione", "Twitter-usuario","Twitter-término","Twitter-coordenadas","Twitter-ciudad","Facebook","Créditos"]
st.set_page_config(
	page_title="Social network analyzer",
	page_icon="random",
	layout="centered",
	initial_sidebar_state="expanded",
	)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


#Funciones

# Convertir a excel
def to_excel(df):
	output = BytesIO()
	writer = pd.ExcelWriter(output, engine='xlsxwriter', options = {'remove_timezone': True})
	df.to_excel(writer, index= False, sheet_name='Sheet1')
	writer.save()
	processed_data = output.getvalue()
	return processed_data

def get_table_download_link(df):
	"""Generates a link allowing the data in a given panda dataframe to be downloaded
	in:  dataframe
	out: href string
	"""
	val = to_excel(df)
	b64 = base64.b64encode(val).decode() # val looks like b'...'
	href=f'<a href="data:application/octet-stream;base64,{b64}" download="captura.xlsx" target="_blank">Descargar: Haga clic derecho y guardar enlace como...</a>' # decode b'abc' => abc	
	return href

def get_table_download_link_csv(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    #csv = df.to_csv(index=False)
    csv = df.to_csv().encode()
    #b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="captura.csv" target="_blank">Download csv file</a>'
    return href

# Obtener tweets de usuarios y palabras entre 2 fechas
def obtener_tweets (cuenta,palabra,f_ini, f_fin, captura):
    maxTweets = 5000
    cuenta_twitter=str(cuenta)
    palabras_clave=str(palabra)
    fecha_ini=str(f_ini)
    fecha_fin=str(f_fin)
    
    parametros_twitter="from:@"+cuenta_twitter+" + since:"+fecha_ini+" until:"+fecha_fin + " "+ palabras_clave

    # Capturo tweets de un usuario en particular y almaceno en diccionario
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(parametros_twitter).get_items()):
        if i > maxTweets :
            break
        captura['username'].append(tweet.username)
        captura['palabra'].append(palabras_clave)
        date=str(tweet.date.year)+"-"+str(tweet.date.month)+"-"+str(tweet.date.day)+" "+str(tweet.date.hour)+":"+str(tweet.date.minute)+":"+str(tweet.date.second)
        captura['fecha'].append(date)
        captura['contenido'].append(tweet.content)
        captura['url'].append(tweet.url)
    return captura

# Obtener tweets de término principal y otros asociados
def obtener_tweets_de_termino(search,palabra,term_ppal, f_ini, f_fin, captura):
    maxTweets = 5000
    term_ppal=str(term_ppal)
    palabra_clave=str(palabra)
    fecha_ini=str(f_ini)
    fecha_fin=str(f_fin)
    parametros_twitter=search+" + since:"+fecha_ini+" until:"+fecha_fin
    # Capturo tweets de un usuario en particular y almaceno en diccionario
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(parametros_twitter).get_items()):
        if i > maxTweets :
            break
        captura['username'].append(tweet.username)
        captura['termino_ppal'].append(term_ppal)
        captura['palabra_clave'].append(palabra_clave)
        date=str(tweet.date.year)+"-"+str(tweet.date.month)+"-"+str(tweet.date.day)+" "+str(tweet.date.hour)+":"+str(tweet.date.minute)+":"+str(tweet.date.second)
        captura['fecha'].append(date)
        captura['contenido'].append(tweet.content)
        captura['url'].append(tweet.url)
    return captura

def obtener_tweets_de_loc_palabras(loc, radio,palabra, f_ini, f_fin, captura):
#captura = {"username":[],"localizacion":[],"radio":[],"palabra_clave":[],"fecha":[],"contenido":[]}
	maxTweets = 5000
	loc=str(loc)
	radio=str(radio)
	palabra_clave=str(palabra)
	fecha_ini=str(f_ini)
	fecha_fin=str(f_fin)
	localiza = loc + ", " + radio   # 
	busqueda=palabra_clave+" + since:"+fecha_ini+" until:"+fecha_fin+' geocode:"{}"'
	for i,tweet in enumerate(sntwitter.TwitterSearchScraper(busqueda.format(localiza)).get_items()):
		if i > maxTweets :
			break
		captura['username'].append(tweet.username)
		captura['localizacion'].append(loc)
		captura['radio'].append(radio)
		captura['palabra_clave'].append(palabra_clave)
		date=str(tweet.date.year)+"-"+str(tweet.date.month)+"-"+str(tweet.date.day)+" "+str(tweet.date.hour)+":"+str(tweet.date.minute)+":"+str(tweet.date.second)
		captura['fecha'].append(date)
		captura['contenido'].append(tweet.content)
		captura['url'].append(tweet.url)
	return captura

def obtener_tweets_de_ciudad_palabras(ciudad_busqueda, radio,palabra, f_ini, f_fin, captura):
#captura = {"username":[],"localizacion":[],"radio":[],"palabra_clave":[],"fecha":[],"contenido":[]}
	maxTweets = 5000
	ciudad_busqueda=str(ciudad_busqueda)
	radio=str(radio)
	palabra_clave=str(palabra)
	fecha_ini=str(f_ini)
	fecha_fin=str(f_fin)
	busqueda=palabra_clave+" since:"+fecha_ini+" until:"+fecha_fin+" near:"+ciudad_busqueda+" within:"+radio
	for i,tweet in enumerate(sntwitter.TwitterSearchScraper(busqueda).get_items()):
		if i > maxTweets :
			break
		captura['username'].append(tweet.username)
		captura['localizacion'].append(ciudad_busqueda)
		captura['radio'].append(radio)
		captura['palabra_clave'].append(palabra_clave)
		date=str(tweet.date.year)+"-"+str(tweet.date.month)+"-"+str(tweet.date.day)+" "+str(tweet.date.hour)+":"+str(tweet.date.minute)+":"+str(tweet.date.second)
		captura['fecha'].append(date)
		captura['contenido'].append(tweet.content)
		captura['url'].append(tweet.url)
	return captura


def obtener_post_facebook(cuenta_fb, paginas,captura):
	#captura = {"username":[],"post_id":[],"textos":[],"date":[],"likes":[],"coments":[],"shares":[],"url":[]}
	maxPosts = 3000
	cuenta_fb=str(cuenta_fb)
	paginas=int(paginas)
	for i,post in enumerate(get_posts(cuenta_fb, pages=paginas)):
		if i > maxPosts:
			break
		captura['username'].append(cuenta_fb)
		captura['post_id'].append(post['post_id'])
		captura['textos'].append(post['text'][:144])
		captura['date'].append(post['time'])
		captura['likes'].append(post['likes'])
		captura['coments'].append(post['comments'])
		captura['shares'].append(post['shares'])
		captura['url'].append(post['post_url'])
	return captura

# Programa
@provide_state
def main(state):
	st.title("Exploración de redes sociales")
	state.inputs1 = state.inputs1 or set()
	state.inputs2 = state.inputs2 or set()
	state.inputs3 = state.inputs3 or set()
	state.inputs4 = state.inputs4 or set()
	state.inputs5 = state.inputs5 or set()
	state.inputs6 = state.inputs6 or set()
	state.inputs7 = state.inputs7 or set()


	image = Image.open('logo.png')
	st.sidebar.image(image, use_column_width=False)
	choice = st.sidebar.selectbox("Seleccione el análisis de su interés",activities)

	if choice == "Seleccione":
		st.subheader("Seleccione una de las opciones en el menú lateral")

	elif choice == "Twitter-usuario":
		st.subheader("Obtiene tweets cruzados de una lista de usuarios y de una lista de palabras clave")

		# ------ Input datos de usuarios
		st.subheader("Usuarios")

		c1, c2 = st.beta_columns([2, 1])
		input_string1 = c1.text_input("Agregar usuario")
		state.inputs1.add(input_string1)

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
		lista_palabras1=list(state.inputs2)
		palabras_busqueda1 = st.multiselect("Seleccionar palabras",lista_palabras1)
		# -----------------------------------
		# ------ Input fechas
		st.subheader("Rango de fechas")
		
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(days=1)
		c5, c6 = st.beta_columns([1, 1])

		f_ini = c5.date_input('Fecha inicio', today)
		f_fin = c6.date_input('Fecha final', tomorrow)


		st.subheader("Detalles de la consulta")
		c5, c6 = st.beta_columns([1, 1])
		c5.markdown('**Usuarios**.')
		c6.markdown('**Palabras clave**.')
		c5.write(cuentas_twitter)
		c6.write(palabras_busqueda1)


		if f_ini < f_fin:
			st.success('Fecha inicio: `%s`\n\nFecha final:`%s`' % (f_ini, f_fin))
		else:
			st.error('Error: La fecha final debe ir después de la fecha inicial.')
		# -----------------------------------

		# ------- Botón analizar
		if st.button('Extraer tweets'):
			# Itero y aplico función
			captura = {"username":[],"palabra":[],"fecha":[],"contenido":[],"url":[]}

			for i in range(0,len(cuentas_twitter)):
				for j in range(0,len(palabras_busqueda1)):
					cuenta=cuentas_twitter[i]
					palabra=palabras_busqueda1[j]
					captura=obtener_tweets(cuenta,palabra,f_ini, f_fin, captura)
					time.sleep(5)

			df1=pd.DataFrame.from_dict(captura) 
			st.write('Se encontraron ', len(df1), " tweets")
  			# Imprimo resultado
			st.dataframe(df1)
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


	elif choice == 'Twitter-término':
		st.subheader("Obtiene tweets cruzados entre un término principal y una lista de palabras clave")

		# ------ Input término principal
		st.subheader("Término principal")

		c1_1, c1_2 = st.beta_columns([2, 1])
		input_string3 = c1_1.text_input("Agregar término")
		state.inputs3.add(input_string3)

        # Obtiene el estado anterior del index
		last_index3 = len(state.inputs3) - 1 if state.inputs3 else None

        # Selecciono la última entrada de acuerdo al index
		c1_2.selectbox("Término principal agregado", options=list(state.inputs3), index=last_index3)
		lista_term_ppal=list(state.inputs3)
		terminos_ppales = st.multiselect("Seleccionar términos",lista_term_ppal)
		# -----------------------------------
  
		# ------ Input palabras clave
		st.subheader("Palabras clave")

		c3, c4 = st.beta_columns([2, 1])
		input_string4 = c3.text_input("Agregar palabra")
		state.inputs4.add(input_string4)

        # Obtiene el estado anterior del index
		last_index4 = len(state.inputs4) - 1 if state.inputs4 else None

        # Selecciono la última entrada de acuerdo al index
		c4.selectbox("Palabras agregadas", options=list(state.inputs4), index=last_index4)
		lista_palabras2=list(state.inputs4)
		palabras_busqueda2 = st.multiselect("Seleccionar palabras",lista_palabras2)
		# -----------------------------------
		# ------ Input fechas
		st.subheader("Rango de fechas")
		
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(days=1)
		c5, c6 = st.beta_columns([1, 1])

		f_ini = c5.date_input('Fecha inicio', today)
		f_fin = c6.date_input('Fecha final', tomorrow)

		st.subheader("Detalles de la consulta")
		c5, c6 = st.beta_columns([1, 1])
		c5.markdown('**Término principal**.')
		c6.markdown('**Palabras clave**.')
		c5.write(terminos_ppales)
		c6.write(palabras_busqueda2)

		if f_ini < f_fin:
			st.success('Fecha inicio: `%s`\n\nFecha final:`%s`' % (f_ini, f_fin))
		else:
			st.error('Error: La fecha final debe ir después de la fecha inicial.')
		# -----------------------------------

		# ------- Botón analizar
		if st.button('Extraer tweets'):
			# Itero y aplico función
			captura = {"username":[],"termino_ppal":[],"palabra_clave":[],"fecha":[],"contenido":[],"url":[]}

			for i in range(0,len(terminos_ppales)):
				for j in range(0,len(palabras_busqueda2)):
					termino_ppal_analizar=terminos_ppales[i]
					palabra=palabras_busqueda2[j]
					search=termino_ppal_analizar + ' + ' + palabra 
					captura=obtener_tweets_de_termino(search,palabra, termino_ppal_analizar, f_ini, f_fin, captura)
					time.sleep(5)

			df1=pd.DataFrame.from_dict(captura) 
			st.write('Se encontraron ', len(df1), " tweets")
  			# Imprimo resultado
			st.dataframe(df1)
			df = df1 # your dataframe
			st.markdown(get_table_download_link(df), unsafe_allow_html=True)
			# Gráficas
			fig, ax = plt.subplots()
			ax=sns.countplot("username", data=df)
			st.pyplot(fig)

			col1, col2 = st.beta_columns(2)
			col1.subheader("Término principal - Palabra")
			fig, ax = plt.subplots()
			ax=sns.countplot(y="termino_ppal", hue="palabra_clave", data=df1)
			col1.pyplot(fig)
			col2.subheader("Palabra - Usuario")
			fig2, ax2 = plt.subplots()
			ax2=sns.countplot(y="palabra_clave", hue="termino_ppal", data=df1)   
			col2.pyplot(fig2)
   

		# -----------------------------------
	elif choice == 'Twitter-coordenadas':
		st.subheader("Obtiene tweets de un punto central en unas coordenadas con un radio R y asociadas a una lista de palabras clave")

		# ------ Input coordenadas y radio
		st.subheader("Localización")

		c3_1, c3_2, c3_3 = st.beta_columns([1, 1, 1])
		inputLat = c3_1.text_input("Latitud - Ej: 4.74075")
		inputLong = c3_2.text_input("Longitud - Ej: -74.08417")
		inputRadio = c3_3.text_input("Radio en km - Ej: 4")+"km"

		# ------ Input palabras clave
		st.subheader("Palabras clave")

		c3_4, c3_5 = st.beta_columns([2, 1])
		input_string5 = c3_4.text_input("Agregar palabra")
		state.inputs5.add(input_string5)

        # Obtiene el estado anterior del index
		last_index5 = len(state.inputs5) - 1 if state.inputs5 else None

        # Selecciono la última entrada de acuerdo al index
		c3_5.selectbox("Palabras agregadas", options=list(state.inputs5), index=last_index5)
		lista_palabras3=list(state.inputs5)
		palabras_busqueda = st.multiselect("Seleccionar palabras",lista_palabras3)
  
		# -----------------------------------
		# ------ Input fechas
		st.subheader("Rango de fechas")
		
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(days=1)
		c3_6, c3_7 = st.beta_columns([1, 1])

		f_ini = c3_6.date_input('Fecha inicio', today)
		f_fin = c3_7.date_input('Fecha final', tomorrow)

		st.subheader("Detalles de la consulta")
		c3_8, c3_9, c3_10 = st.beta_columns([1, 1, 1] )
		c3_8.markdown('**Latitud**.')
		c3_9.markdown('**Longitud**.')
		c3_10.markdown('**Radio**.')
		c3_8.write(inputLat)
		c3_9.write(inputLong)
		c3_10.write(inputRadio)
		if f_ini < f_fin:
			st.success('Fecha inicio: `%s`\n\nFecha final:`%s`' % (f_ini, f_fin))
		else:
			st.error('Error: La fecha final debe ir después de la fecha inicial.')
		# -----------------------------------

		# ------- Botón analizar
		if st.button('Extraer tweets'):
			# Itero y aplico función
			captura = {"username":[],"localizacion":[],"radio":[],"palabra_clave":[],"fecha":[],"contenido":[],"url":[]}
			loc=str(inputLat)+", "+str(inputLong)
			radio=str(inputRadio)

			# Itero y aplico función
			for i in range(0,len(palabras_busqueda)):
				palabra=palabras_busqueda[i]
				captura=obtener_tweets_de_loc_palabras(loc, radio,palabra,f_ini, f_fin,captura)
				time.sleep(5)

			df1=pd.DataFrame.from_dict(captura) 
			st.write('Se encontraron ', len(df1), " tweets")
  			# Imprimo resultado
			st.dataframe(df1)
			df = df1 # your dataframe
			st.markdown(get_table_download_link(df), unsafe_allow_html=True)

			# Gráficas
			fig, ax = plt.subplots()
			ax=sns.countplot("username", data=df)
			st.pyplot(fig)

			col1, col2 = st.beta_columns(2)

			col1.subheader("Usuario - Palabra")
			fig, ax = plt.subplots()
			ax=sns.countplot(y="username", hue="palabra_clave", data=df1)
			col1.pyplot(fig)

			col2.subheader("Palabra - Usuario")
			fig2, ax2 = plt.subplots()
			ax2=sns.countplot(y="palabra_clave", hue="username", data=df1)   
			col2.pyplot(fig2)


#obtener_tweets_de_ciudad_palabras
	elif choice == 'Twitter-ciudad':
		st.subheader("Obtiene tweets desde un punto central en una ciudad, con un radio R y asociadas a una lista de palabras clave")

		# ------ Input ciudad y radio
		st.subheader("Localización")

		c4_1, c4_2 = st.beta_columns([1, 1])
		input_ciudad = c4_1.text_input("Ciudad")
		input_radio = c4_2.text_input("Radio")+"km"

		# ------ Input palabras clave
		st.subheader("Palabras clave")

		c4_4, c4_5 = st.beta_columns([2, 1])
		input_string6 = c4_4.text_input("Agregar palabra")
		state.inputs6.add(input_string6)

        # Obtiene el estado anterior del index
		last_index6 = len(state.inputs6) - 1 if state.inputs6 else None

        # Selecciono la última entrada de acuerdo al index
		c4_5.selectbox("Palabras agregadas", options=list(state.inputs6), index=last_index6)
		lista_palabras4=list(state.inputs6)
		palabras_busqueda = st.multiselect("Seleccionar palabras",lista_palabras4)
  
		# -----------------------------------
		# ------ Input fechas
		st.subheader("Rango de fechas")
		
		today = datetime.date.today()
		tomorrow = today + datetime.timedelta(days=1)
		c4_6, c4_7 = st.beta_columns([1, 1])

		f_ini = c4_6.date_input('Fecha inicio', today)
		f_fin = c4_7.date_input('Fecha final', tomorrow)

		st.subheader("Detalles de la consulta")
		c4_8, c4_9 = st.beta_columns([1, 1] )
		c4_8.markdown('**Ciudad o punto central**.')
		c4_9.markdown('**Radio**.')
		c4_8.write(input_ciudad)
		c4_9.write(input_radio)
		if f_ini < f_fin:
			st.success('Fecha inicio: `%s`\n\nFecha final:`%s`' % (f_ini, f_fin))
		else:
			st.error('Error: La fecha final debe ir después de la fecha inicial.')
		# -----------------------------------

		# ------- Botón analizar
		if st.button('Extraer tweets'):
			# Itero y aplico función
			captura = {"username":[],"localizacion":[],"radio":[],"palabra_clave":[],"fecha":[],"contenido":[],"url":[]}
			loc=str(input_ciudad)
			radio=str(input_radio)

			# Itero y aplico función
			for i in range(0,len(palabras_busqueda)):
				palabra=palabras_busqueda[i]
				captura=obtener_tweets_de_ciudad_palabras(loc, radio,palabra,f_ini, f_fin,captura)
				time.sleep(5)

			df1=pd.DataFrame.from_dict(captura) 
			st.write('Se encontraron ', len(df1), " tweets")
  			# Imprimo resultado
			st.dataframe(df1)
			df = df1 # your dataframe
			st.markdown(get_table_download_link(df), unsafe_allow_html=True)

			# Gráficas
			fig, ax = plt.subplots()
			ax=sns.countplot("username", data=df)
			st.pyplot(fig)

			col1, col2 = st.beta_columns(2)

			col1.subheader("Usuario - Palabra")
			fig, ax = plt.subplots()
			ax=sns.countplot(y="username", hue="palabra_clave", data=df1)
			col1.pyplot(fig)

			col2.subheader("Palabra - Usuario")
			fig2, ax2 = plt.subplots()
			ax2=sns.countplot(y="palabra_clave", hue="username", data=df1)   
			col2.pyplot(fig2)



	elif choice == 'test':
		arr = np.random.normal(1, 1, size=100)
		fig, ax = plt.subplots()
		ax.hist(arr, bins=20)
		st.pyplot(fig)

	elif choice == 'Facebook':
		st.subheader("Obtiene posts de una cuenta pública de facebook")

		# ------ Input datos de usuarios
		st.subheader("Usuarios")

		c1, c2 = st.beta_columns([2, 1])
		input_string = c1.text_input("Agregar usuario")
		state.inputs7.add(input_string)

        # Obtiene el estado anterior del index
		last_index7 = len(state.inputs7) - 1 if state.inputs7 else None

        # Selecciono la última entrada de acuerdo al index
		c2.selectbox("Usuarios agregados", options=list(state.inputs7), index=last_index7)
		lista_cuentas5=list(state.inputs7)
		cuentas_fb = st.multiselect("Seleccionar usuarios",lista_cuentas5)
		# -----------------------------------
		# ------ Input páginas
		paginas=st.text_input("Paginas")
		# -----------------------------------

		# ------- Botón analizar
		if st.button('Extraer posts'):
			# Parametros		
			captura = {"username":[],"post_id":[],"textos":[],"date":[],"likes":[],"coments":[],"shares":[],"url":[]}

			for i in range(0,len(cuentas_fb)):
				cuenta_fb=cuentas_fb[i]
				captura=obtener_post_facebook(cuenta_fb, paginas,captura)
				time.sleep(5)

			# Imprimo resultado
			df1=pd.DataFrame.from_dict(captura) 
			st.write('Se encontraron ', len(df1), " posts")
			st.dataframe(df1.head())
			df = df1 # your dataframe
			st.markdown(get_table_download_link(df), unsafe_allow_html=True)

			# Gráficas
			fig, ax = plt.subplots()
			ax=sns.countplot("username", data=df)
			st.pyplot(fig)

	elif choice == 'Créditos':
		st.subheader("Jorge O. Cifuentes")
		body='<a href="https://www.quidlab.co">https://www.quidlab.co</a>'
		st.markdown(body, unsafe_allow_html=True)
		st.write('Email: *jorge@quidlab.co* :heart:')

		st.text("")


if __name__ == "__main__":
	main()

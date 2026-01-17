import connection
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.clock import Clock
# Importăm FadeTransition pentru a o folosi în KV
from kivy.uix.screenmanager import FadeTransition
from kivy_garden.mapview import MapView , MapMarker
from kivy.clock import mainthread # Decorator Kivy pentru a reveni la firul principal UI
from geopy.geocoders import Nominatim
from threading import Thread
from kivy.clock import mainthread
import oracledb
from kivy.app import App
from kivy.utils import get_color_from_hex
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from kivy.properties import StringProperty
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget


class LoginScreen(Screen):
	name= 'loginScreen'

	def on_pre_enter(self):
		if 'email_int' in self.ids:
			self.ids.email_int.text = ""

		if 'password_int' in self.ids:
			self.ids.password_int.text = ""
		if 'feedback1' in self.ids:
			self.ids.feedback1.text = ""



	def verificare_log(self, instance):
		email_caseta = self.ids.email_int
		pass_caseta = self.ids.password_int

		email_text = email_caseta.text.strip()
		password_text = pass_caseta.text.strip()


		if not email_text or not password_text:
			email_caseta.line_color_normal = get_color_from_hex('#C24641')
			pass_caseta.line_color_normal = get_color_from_hex('#C24641')
			Snackbar(
				MDLabel(text = "Completeaza ambele casete!", theme_text_color = "Custom",
				        text_color = (1, 1, 1, 1)),
				bg_color = (1, 0, 0, 1)
			).open()
			return
		connection = None
		try:
			connection = oracledb.connect(
				user = "SYSTEM",
				password = "Capricorn.2004",
				dsn = "localhost:1521/xe"
			)
			cursor = connection.cursor()


			sql = "SELECT ID, PAROLA FROM SIGNIN_UTILIZATOR WHERE USERNAME = :1"
			cursor.execute(sql, (email_text,))

			rezultat = cursor.fetchone()

			if rezultat is None:

				email_caseta.line_color_normal = get_color_from_hex('#C24641')
				Snackbar(
					MDLabel(text = "Utilizator inexistent!", theme_text_color = "Custom",
					        text_color = (1, 1, 1, 1)),
					bg_color = (1, 0, 0, 1)
				).open()
			else:
				user_id_db = rezultat[0]
				parola_db = rezultat[1]

				if password_text == parola_db:
					Snackbar(
						MDLabel(text = "Login reusit!", theme_text_color = "Custom",
						        text_color = (1, 1, 1, 1)),
						bg_color = (1, 0, 0, 1)
					).open()


					app = App.get_running_app()
					app.user_id_conectat = user_id_db
					app.user_nume_conectat = email_text

					print(f"DEBUG: S-a conectat userul {email_text} cu ID: {user_id_db}")

					Clock.schedule_once(self.schimba_la_home, 1)
				else:
					email_caseta.line_color_normal = get_color_from_hex('#ffffff')
					pass_caseta.line_color_normal = get_color_from_hex('#C24641')
					Snackbar(
						MDLabel(text = "Parola incoreccta!", theme_text_color = "Custom",
						        text_color = (1, 1, 1, 1)),
						bg_color = (1, 0, 0, 1)
					).open()

		except oracledb.Error as e:
			print(f"Eroare: {e}")
		finally:
			if connection:
				connection.close()



	def login_btn_apasat(self, instance):
	    self.verificare_log(instance)

	def schimba_la_home(self, dt):
		self.manager.current = 'primulEcran'


	def switch_to_signin(self, dt):
		self.manager.current = 'signinScreen'


class SigninScreen(Screen):
	name= 'signinScreen'

	def on_pre_enter(self):

		if 'email_int' in self.ids:
			self.ids.email_int.text = ""
		if 'password_int' in self.ids:
			self.ids.password_int.text = ""
		if 'repassword' in self.ids:
			self.ids.repassword.text = ""
		if 'feedbackSignin' in self.ids:
			self.ids.feedbackSignin.text = ""


	def verificare_sign(self, instance):
		user_caseta = self.ids.email_int
		pass_caseta = self.ids.password_int
		repass_caseta = self.ids.repassword


		username_text = user_caseta.text.strip()
		password_text = pass_caseta.text.strip()
		repassword_text = repass_caseta.text.strip()


		user_caseta.line_color_normal = get_color_from_hex('#ffffff')
		pass_caseta.line_color_normal = get_color_from_hex('#ffffff')
		repass_caseta.line_color_normal = get_color_from_hex('#ffffff')


		if not username_text or not password_text or not repassword_text:
			Snackbar(
				MDLabel(text = "Toate campurile sunt obligatorii!", theme_text_color = "Custom",
				        text_color = (1, 1, 1, 1)),
				bg_color = (1, 0, 0, 1)
			).open()

			if not username_text: user_caseta.line_color_normal = get_color_from_hex('#C24641')
			if not password_text: pass_caseta.line_color_normal = get_color_from_hex('#C24641')
			if not repassword_text: repass_caseta.line_color_normal = get_color_from_hex('#C24641')
			return


		if password_text != repassword_text:
			Snackbar(
				MDLabel(text = "Parolele nu coincid!", theme_text_color = "Custom",
				        text_color = (1, 1, 1, 1)),
				bg_color = (1, 0, 0, 1)
			).open()
			pass_caseta.line_color_normal = get_color_from_hex('#C24641')
			repass_caseta.line_color_normal = get_color_from_hex('#C24641')
			return


		connection = None
		try:
			connection = oracledb.connect(
				user = "SYSTEM",
				password = "Capricorn.2004",
				dsn = "localhost:1521/xe"
			)
			cursor = connection.cursor()

			sql_check = "SELECT USERNAME FROM SIGNIN_UTILIZATOR WHERE USERNAME = :1"
			cursor.execute(sql_check, (username_text,))

			if cursor.fetchone():
				Snackbar(
					MDLabel(text = "Acest utilizator exista deja!", theme_text_color = "Custom",
					        text_color = (1, 1, 1, 1)),
					bg_color = (1, 0, 0, 1)
				).open()
				user_caseta.line_color_normal = get_color_from_hex('#C24641')
				return


			sql_insert = "INSERT INTO SIGNIN_UTILIZATOR (USERNAME, PAROLA) VALUES (:1, :2)"
			cursor.execute(sql_insert, (username_text, password_text))


			connection.commit()
			sql = "SELECT ID, PAROLA FROM SIGNIN_UTILIZATOR WHERE USERNAME = :1"
			cursor.execute(sql, (username_text,))

			rezultat = cursor.fetchone()

			if rezultat is None:
				Snackbar(
					MDLabel(text = "Utilizator inexistent!", theme_text_color = "Custom",
					        text_color = (1, 1, 1, 1)),
					bg_color = (1, 0, 0, 1)
				).open()
			else:
				user_id_db = rezultat[0]

			app = App.get_running_app()
			app.user_id_conectat = user_id_db
			app.user_nume_conectat = username_text

			Snackbar(
				MDLabel(text = "Inregistrare reusita!", theme_text_color = "Custom",
				        text_color = (1, 1, 1, 1)),
				bg_color = (1, 0, 0, 1)
			).open()


			app = App.get_running_app()

			app.user_conectat = user_caseta.text


			self.momento(instance)

		except oracledb.Error as e:
			print(f"Eroare Oracle: {e}")

		finally:
			if connection:
				connection.close()

	def signin_btn_apasat(self, instance):
		self.verificare_sign(instance)

	def schimba_la_ecranul_principal(self, dt):
		self.manager.current = 'primulEcran'

	def momento(self, dt):
		Clock.schedule_once(self.schimba_la_ecranul_principal, 2)


class ColectareDate(MDScreen):

	data_selectata_pt_db = None


	def arata_calendar(self, input_field):

		CULOARE_CALENDAR = get_color_from_hex("#DDB2B5")  # Mov

		self.input_field_curent = input_field
		self.input_field_curent.focus = False

		date_dialog = MDDatePicker(
			accent_color = CULOARE_CALENDAR
		)
		date_dialog.bind(on_save = self.salveaza_data)
		date_dialog.open()

	def salveaza_data(self, instance, value, date_range):
		self.input_field_curent.text = value.strftime('%d-%m-%Y')


		app = MDApp.get_running_app()
		app.data_rezervare_temp = value
		print(f"DEBUG: Am salvat data global: {value}")

	def inchide_calendar(self, instance, value):
		pass



class PrimulEcran(MDScreen):
	name = 'primulEcran'
	TOTAL_SALI_DISPONIBILE = 3
	def on_pre_enter(self):
		app = MDApp.get_running_app()
		azi = datetime.now().date()
		self.ids.label_data_curenta.text = azi.strftime('%d.%m.%Y')
		self.actualizeaza_dashboard()

	def actualizeaza_dashboard(self):
		app = MDApp.get_running_app()
		user_id = app.user_id_conectat

		rezervari_personale = 0
		sali_ocupate_total = 0

		connection = None
		try:
			connection = oracledb.connect(
				user = "SYSTEM",
				password = "Capricorn.2004",
				dsn = "localhost:1521/xe"
			)
			cursor = connection.cursor()



			sql_global = "SELECT COUNT(*) FROM REZERVARI WHERE TRUNC(DATA_REZERVARE) = TRUNC(SYSDATE)"
			cursor.execute(sql_global)
			result_global = cursor.fetchone()

			if result_global:
				sali_ocupate_total = result_global[0]


			if user_id:
				sql_personal = """
		                   SELECT COUNT(*) 
		                   FROM REZERVARI 
		                   WHERE USER_ID = :1 
		                   AND TRUNC(DATA_REZERVARE) = TRUNC(SYSDATE)
		               """
				cursor.execute(sql_personal, (user_id,))
				result_personal = cursor.fetchone()

				if result_personal:
					rezervari_personale = result_personal[0]

			sali_libere = self.TOTAL_SALI_DISPONIBILE - sali_ocupate_total
			if sali_libere < 0: sali_libere = 0

			self.ids.lbl_sali_libere.text = str(sali_libere)
			self.ids.lbl_sali_ocupate.text = str(sali_ocupate_total)
			self.ids.lbl_rezervari_azi.text = str(rezervari_personale)

			print(f"DEBUG: Total ocupate: {sali_ocupate_total}, Rezervările mele: {rezervari_personale}")

		except oracledb.Error as e:
			print(f"Eroare Dashboard: {e}")
			self.ids.lbl_rezervari_azi.text = "-"

		finally:
			if connection:
				connection.close()


class PrimaSala(MDScreen):
	name = 'primaSala'

	ADRESA_MEA = "Strada Dumbrava Roșie, Nr. 2, Bacău, România"

	def on_enter(self):
		app = MDApp.get_running_app()
		app.start_geocoding_for_address(self.ADRESA_MEA, self.name)

	def rezerva_acum(self):
		app = App.get_running_app()
		user_id = app.user_id_conectat
		data_selectata = app.data_rezervare_temp


		if not user_id:
			Snackbar(
				MDLabel(
					text = "Eroare: Trebuie să fii logat!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)  # Text Alb
				),
				bg_color = (1, 0, 0, 1)  # Fundal Roșu
			).open()
			return

		if not data_selectata:
			Snackbar(
				MDLabel(
					text = "Alege o dată din calendar!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)
				),
				bg_color = (1, 0, 0, 1)
			).open()
			return

		connection = None
		try:
			connection = oracledb.connect(
				user = "SYSTEM",
				password = "Capricorn.2004",
				dsn = "localhost:1521/xe"
			)
			cursor = connection.cursor()
			nume_sala = "Sala Conference Room New York"

			sql_check = "SELECT 1 FROM REZERVARI WHERE NUME_SALA = :1 AND TRUNC(DATA_REZERVARE) = :2"
			cursor.execute(sql_check, (nume_sala, data_selectata))

			if cursor.fetchone():
				msg = f"Data de {data_selectata.strftime('%d-%m-%Y')} este deja ocupată!"
				Snackbar(
					MDLabel(
						text = msg,
						theme_text_color = "Custom",
						text_color = (1, 1, 1, 1)
					),
					bg_color = (1, 0, 0, 1)
				).open()
			else:
				sql_insert = "INSERT INTO REZERVARI (USER_ID, NUME_SALA, DATA_REZERVARE) VALUES (:1, :2, :3)"
				cursor.execute(sql_insert, (user_id, nume_sala, data_selectata))
				connection.commit()

				Snackbar(
					MDLabel(
						text = "Rezervare efectuată cu succes!",
						theme_text_color = "Custom",
						text_color = (1, 1, 1, 1)
					),
					bg_color = (0, 0.5, 0, 1)  # Verde
				).open()

				self.schimba_la_ecranul_principal()

				self.ids.data_rezervarii.text = ""
				app.data_rezervare_temp = None

		except oracledb.Error as e:
			print(f"Eroare Oracle: {e}")
			Snackbar(
				MDLabel(
					text = "Eroare conexiune server!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)
				),
				bg_color = (1, 0, 0, 1)
			).open()

		finally:
			if connection:
				connection.close()

	def schimba_la_ecranul_principal(self):
		self.manager.current = 'primulEcran'



class ADouaSala(MDScreen):
	name = 'adouaSala'

	ADRESA_MEA = "Strada Dumbrava Roșie, Nr. 2, Bacău, România"

	def on_enter(self):
		app = MDApp.get_running_app()
		app.start_geocoding_for_address(self.ADRESA_MEA, self.name)



	def rezerva_acum(self):
		app = App.get_running_app()
		user_id = app.user_id_conectat
		data_selectata = app.data_rezervare_temp

		if not user_id:
			Snackbar(
				MDLabel(
					text = "Eroare: Trebuie să fii logat!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)  # Text Alb
				),
				bg_color = (1, 0, 0, 1)  # Fundal Roșu
			).open()
			return

		if not data_selectata:
			Snackbar(
				MDLabel(
					text = "Alege o dată din calendar!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)
				),
				bg_color = (1, 0, 0, 1)
			).open()
			return

		connection = None
		try:
			connection = oracledb.connect(
				user = "SYSTEM",
				password = "Capricorn.2004",
				dsn = "localhost:1521/xe"
			)
			cursor = connection.cursor()
			nume_sala = "Sala Luna"

			sql_check = "SELECT 1 FROM REZERVARI WHERE NUME_SALA = :1 AND TRUNC(DATA_REZERVARE) = :2"
			cursor.execute(sql_check, (nume_sala, data_selectata))

			if cursor.fetchone():
				msg = f"Data de {data_selectata.strftime('%d-%m-%Y')} este deja ocupată!"
				Snackbar(
					MDLabel(
						text = msg,
						theme_text_color = "Custom",
						text_color = (1, 1, 1, 1)
					),
					bg_color = (1, 0, 0, 1)
				).open()
			else:
				sql_insert = "INSERT INTO REZERVARI (USER_ID, NUME_SALA, DATA_REZERVARE) VALUES (:1, :2, :3)"
				cursor.execute(sql_insert, (user_id, nume_sala, data_selectata))
				connection.commit()


				Snackbar(
					MDLabel(
						text = "Rezervare efectuată cu succes!",
						theme_text_color = "Custom",
						text_color = (1, 1, 1, 1)
					),
					bg_color = (0, 0.5, 0, 1)  # Verde
				).open()

				self.schimba_la_ecranul_principal()
				self.ids.data_rezervarii.text = ""
				app.data_rezervare_temp = None

		except oracledb.Error as e:
			print(f"Eroare Oracle: {e}")
			Snackbar(
				MDLabel(
					text = "Eroare conexiune server!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)
				),
				bg_color = (1, 0, 0, 1)
			).open()

		finally:
			if connection:
				connection.close()

	def schimba_la_ecranul_principal(self):
		self.manager.current = 'primulEcran'

class ATreiaSala(MDScreen):
	name = 'atreiaSala'

	ADRESA_MEA = "Calea Moldovei, Nr. 38, Bacău, România"


	def on_enter(self):
		app = MDApp.get_running_app()
		app.start_geocoding_for_address(self.ADRESA_MEA, self.name)

	def rezerva_acum(self):
		app = App.get_running_app()
		user_id = app.user_id_conectat
		data_selectata = app.data_rezervare_temp

		if not user_id:
			Snackbar(
				MDLabel(
					text = "Eroare: Trebuie sa fii logat!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)
				),
				bg_color = (1, 0, 0, 1)
			).open()
			return

		if not data_selectata:
			Snackbar(
				MDLabel(
					text = "Alege o data din calendar!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)
				),
				bg_color = (1, 0, 0, 1)
			).open()
			return

		connection = None
		try:
			connection = oracledb.connect(
				user = "SYSTEM",
				password = "Capricorn.2004",
				dsn = "localhost:1521/xe"
			)
			cursor = connection.cursor()
			nume_sala = "Sala Conferinte Podul cu Lanturi"

			sql_check = "SELECT 1 FROM REZERVARI WHERE NUME_SALA = :1 AND TRUNC(DATA_REZERVARE) = :2"
			cursor.execute(sql_check, (nume_sala, data_selectata))

			if cursor.fetchone():
				msg = f"Data de {data_selectata.strftime('%d-%m-%Y')} este deja ocupată!"
				Snackbar(
					MDLabel(
						text = msg,
						theme_text_color = "Custom",
						text_color = (1, 1, 1, 1)
					),
					bg_color = (1, 0, 0, 1)
				).open()
			else:
				sql_insert = "INSERT INTO REZERVARI (USER_ID, NUME_SALA, DATA_REZERVARE) VALUES (:1, :2, :3)"
				cursor.execute(sql_insert, (user_id, nume_sala, data_selectata))
				connection.commit()

				Snackbar(
					MDLabel(
						text = "Rezervare efectuată cu succes!",
						theme_text_color = "Custom",
						text_color = (1, 1, 1, 1)
					),
					bg_color = (0, 0.5, 0, 1)  # Verde
				).open()

				self.schimba_la_ecranul_principal()
				self.ids.data_rezervarii.text = ""
				app.data_rezervare_temp = None

		except oracledb.Error as e:
			print(f"Eroare Oracle: {e}")

			Snackbar(
				MDLabel(
					text = "Eroare conexiune server!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)
				),
				bg_color = (1, 0, 0, 1)
			).open()

		finally:
			if connection:
				connection.close()

	def schimba_la_ecranul_principal(self):
		self.manager.current = 'primulEcran'


class Rezervari(MDScreen):
	name = 'rezervari'

	def on_enter(self):
		self.incarca_rezervari()

	def incarca_rezervari(self):
		app = App.get_running_app()
		user_id = app.user_id_conectat
		lista_container = self.ids.container_lista

		lista_container.clear_widgets()

		if not user_id:
			return

		connection = None
		try:
			connection = oracledb.connect(
				user = "SYSTEM",
				password = "Capricorn.2004",
				dsn = "localhost:1521/xe"
			)
			cursor = connection.cursor()

			sql = """
	                SELECT ID_REZ, NUME_SALA, DATA_REZERVARE 
	                FROM REZERVARI 
	                WHERE USER_ID = :1 
	                ORDER BY DATA_REZERVARE DESC
	            """
			cursor.execute(sql, (user_id,))
			rezultate = cursor.fetchall()

			if not rezultate:
				lbl = TwoLineAvatarIconListItem(
					text = "Nu ai nicio rezervare activa.",
					secondary_text = "Rezerva o sala din meniul principal."
				)
				lista_container.add_widget(lbl)

			for rand in rezultate:
				id_rezervare = rand[0]
				nume_sala = rand[1]
				data_rez = rand[2]

				data_str = data_rez.strftime('%d-%m-%Y')

				item = TwoLineAvatarIconListItem(
					text = nume_sala,
					secondary_text = f"Data: {data_str}",
				)

				icon_stanga = IconLeftWidget(icon = "calendar")
				item.add_widget(icon_stanga)

				icon_dreapta = IconRightWidget(icon = "trash-can",
				                               on_release = lambda x, id_rez = id_rezervare: self.sterge_rezervare(
					                               id_rez))
				item.add_widget(icon_dreapta)

				lista_container.add_widget(item)

		except oracledb.Error as e:
			print(f"Eroare la încărcarea rezervarilor: {e}")
		finally:
			if connection:
				connection.close()

	def sterge_rezervare(self, id_rezervare):
		connection = None
		try:
			connection = oracledb.connect(
				user = "SYSTEM",
				password = "Capricorn.2004",
				dsn = "localhost:1521/xe"
			)
			cursor = connection.cursor()


			sql = "DELETE FROM REZERVARI WHERE ID_REZ = :1"
			cursor.execute(sql, (id_rezervare,))
			connection.commit()
			Snackbar(
				MDLabel(text = "Rezervarea {id_rezervare} a fost ștearsă.", theme_text_color = "Custom",
				        text_color = (1, 1, 1, 1)),
				bg_color = (1, 0, 0, 1)
			).open()


			self.incarca_rezervari()

			Snackbar(
				MDLabel(
					text = "Rezervare anulată cu succes!",
					theme_text_color = "Custom",
					text_color = (1, 1, 1, 1)
				),
				bg_color = (1, 0, 0, 1)
			).open()

		except oracledb.Error as e:
			print(f"Eroare ștergere: {e}")
		finally:
			if connection:
				connection.close()

	def inapoi_la_home(self):
		self.manager.current = 'primulEcran'

class ProfilScreen(MDScreen):
    name = 'profilScreen'

    def on_enter(self):
        self.incarca_datele()

    def incarca_datele(self):
        app = App.get_running_app()
        user_id = getattr(app, 'user_id_conectat', None)

        print(f"DEBUG: Încercare încărcare profil pentru User ID: {user_id}")

        if not user_id:
            Snackbar(
                MDLabel(
                    text="Eroare: Nu ești logat!",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1)
                ),
                bg_color=(1, 0, 0, 1)
            ).open()
            return

        connection = None
        try:
            connection = oracledb.connect(
                user="SYSTEM",
                password="Capricorn.2004",
                dsn="localhost:1521/xe"
            )
            cursor = connection.cursor()

            sql = "SELECT USERNAME, PAROLA, NUME, PRENUME, TELEFON FROM SIGNIN_UTILIZATOR WHERE ID = :1"
            cursor.execute(sql, (user_id,))
            rezultat = cursor.fetchone()

            if rezultat:
                print(f"DEBUG: Date găsite: {rezultat}")
                self.ids.txt_email.text = str(rezultat[0] or "")
                self.ids.txt_parola.text = str(rezultat[1] or "")
                self.ids.txt_nume.text = str(rezultat[2] or "")
                self.ids.txt_prenume.text = str(rezultat[3] or "")
                self.ids.txt_telefon.text = str(rezultat[4] or "")
            else:
                Snackbar(
	                MDLabel(
		                text = "User-ul nu a fost gasit în baza de date!",
		                theme_text_color = "Custom",
		                text_color = (1, 1, 1, 1)
	                ),
	                bg_color = (1, 0, 0, 1)
                ).open()

        except oracledb.Error as e:
            print(f"Eroare SQL la încărcare: {e}")
            Snackbar(
                MDLabel(text="Eroare conexiune baza de date!", theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=(1, 0, 0, 1)
            ).open()
        finally:
            if connection:
                connection.close()

    def salveaza_date(self):
        app = App.get_running_app()
        user_id = getattr(app, 'user_id_conectat', None)

        if not user_id:
            return

        noul_email = self.ids.txt_email.text.strip()
        noua_parola = self.ids.txt_parola.text.strip()
        noul_nume = self.ids.txt_nume.text.strip()
        noul_prenume = self.ids.txt_prenume.text.strip()
        noul_telefon = self.ids.txt_telefon.text.strip()

        if not noul_email or not noua_parola:
            Snackbar(
                MDLabel(text="Email-ul și Parola sunt obligatorii!", theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=(1, 0, 0, 1)
            ).open()
            return

        connection = None
        try:
            connection = oracledb.connect(
                user="SYSTEM",
                password="Capricorn.2004",
                dsn="localhost:1521/xe"
            )
            cursor = connection.cursor()

            sql = """
                UPDATE SIGNIN_UTILIZATOR 
                SET USERNAME = :1, PAROLA = :2, NUME = :3, PRENUME = :4, TELEFON = :5 
                WHERE ID = :6
            """
            cursor.execute(sql, (noul_email, noua_parola, noul_nume, noul_prenume, noul_telefon, user_id))
            connection.commit()

            app.user_nume_conectat = noul_email

            Snackbar(
                MDLabel(text="Profil actualizat cu succes!", theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=(0, 0.5, 0, 1)
            ).open()

        except oracledb.Error as e:
            print(f"Eroare SQL la salvare: {e}")
            Snackbar(
                MDLabel(text="Eroare la salvare!", theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=(1, 0, 0, 1)
            ).open()
        finally:
            if connection:
                connection.close()

    def inapoi(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'primulEcran'
class Gestionare(Screen):
	name = 'gestionare'


	def schimbaLaLogin(self):
		self.ids.content_manager.current = 'loginScreen'

	def schimbaLaSignin(self):
		self.ids.content_manager.current = 'signinScreen'

	def schimbaLaPag1(self):
		self.ids.content_manager.current = 'primulEcran'


	def schimbaLaPrimaSala(self):
		self.ids.content_manager.current = 'primaSala'

	def schimbaLaSala2(self):
		self.ids.content_manager.current = 'adouaSala'

	def schimbaLaSala3(self):
		self.ids.content_manager.current = 'atreiaSala'

	def schimbaLaRezervari(self):
		self.ids.content_manager.current = 'rezervari'

	def schimbaLaProfil(self):
		self.ids.content_manager.current = 'profilScreen'


	def logout(self):
		app = MDApp.get_running_app()

		app.user_id_conectat = None
		app.user_nume_conectat = None
		app.data_rezervare_temp = None

		Snackbar(
			MDLabel(
				text = "Te-ai deconectat cu succes!",
				theme_text_color = "Custom",
				text_color = (1, 1, 1, 1)
			),
			bg_color = (0, 0, 0, 1)
		).open()

		try:
			app.root.ids.content_manager.current = 'loginScreen'
		except AttributeError:

			app.root.current = 'loginScreen'



class ExampleApp(MDApp):
	user_id_conectat = None
	user_nume_conectat = None
	data_rezervare_temp = None

	def start_geocoding_for_address(self, address, screen_name):

		Thread(target = self._perform_geocoding_task, args = (address, screen_name)).start()

	def _perform_geocoding_task(self, address, screen_name):
		try:
			geolocator = Nominatim(user_agent = "mapview_kivy_app")
			location = geolocator.geocode(address)

			self.on_search_result_geopy(location, screen_name)

		except Exception as e:
			print(f"Eroare: {e}")

	@mainthread
	def on_search_result_geopy(self, location, screen_name):

		if location:
			lat = location.latitude
			lon = location.longitude

			root_widget = self.root

			if isinstance(root_widget, ScreenManager):
				sm = root_widget
			elif hasattr(root_widget, 'ids') and 'content_manager' in root_widget.ids:
				sm = root_widget.ids.content_manager
			else:
				print(" Eroare de Configurare: Nu pot gasi ScreenManager-ul.")
				return

			try:

				target_screen = sm.get_screen(screen_name)
				print(f" Am gasit ecranul: {target_screen.name}")

				if screen_name == 'primaSala':
					map_widget = target_screen.ids.map_widget_1
				elif screen_name == 'adouaSala':
					map_widget = target_screen.ids.map_widget_2
				elif screen_name == 'atreiaSala':
					map_widget = target_screen.ids.map_widget_3
				else:
					print(f" Eroare: Ecranul '{screen_name}' nu are un ID de harta map_widget_X definit.")
					return

				marker = MapMarker(
					lat = lat,
					lon = lon,
					source = "pin32x32.png",
					size = (32, 32),
					anchor_x = 0.5,
					anchor_y = 0
				)

				marker_attribute_name = f'marker_curent_{screen_name}'

				if hasattr(target_screen, marker_attribute_name) and getattr(target_screen, marker_attribute_name):
					map_widget.remove_marker(getattr(target_screen, marker_attribute_name))

				map_widget.add_marker(marker)
				setattr(target_screen, marker_attribute_name, marker)

				map_widget.lat = lat
				map_widget.lon = lon
				map_widget.zoom = 15
			except AttributeError as e:
				print(f" Eroare la accesarea widget-urilor pe ecranul '{screen_name}': {e}")

		else:
			print(f" Geocodarea a esuat pentru adresa pe ecranul: {screen_name}")


	def on_start(self):
		self.theme_cls.primary_palette = "Gray"
		self.theme_cls.primary_hue = "100"
		self.theme_cls.theme_style = "Light"
		self.sterge_rezervari_expirate()
		self.deschidere_logIn()

	def deschidere_logIn(self):
		self.root.ids.content_manager.current = 'loginScreen'


	def sterge_rezervari_expirate(self):
		connection = None
		try:
			connection = oracledb.connect(
					user = "SYSTEM",
					password = "Capricorn.2004",
					dsn = "localhost:1521/xe"
				)
			cursor = connection.cursor()


			cursor.callproc("STERGE_REZERVARI_VECHI")

			print("baza de date a fost curatata!")

		except oracledb.Error as e:
			print(f"eroare la curatarea bazei de date: {e}")
		finally:
			if connection:
				connection.close()




	def build(self):
		Builder.load_file('gestionare.kv')
		Builder.load_file('LoginScreen.kv')
		Builder.load_file('SigninScreen.kv')
		Builder.load_file('primulEcran.kv')
		Builder.load_file('saliScreen.kv')
		Builder.load_file('primaSala.kv')
		Builder.load_file('adouaSala.kv')
		Builder.load_file('atreiaSala.kv')
		Builder.load_file('rezervari.kv')
		Builder.load_file('profilScreen.kv')

		return Gestionare()


if __name__ == '__main__':
	ExampleApp().run()
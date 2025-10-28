from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class MySeleniumTests(StaticLiveServerTestCase):
    # no crearem una BD de test en aquesta ocasió (comentem la línia)
    #fixtures = ['testdb.json',]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        # creem superusuari
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        # tanquem browser
        # comentar la propera línia si volem veure el resultat de l'execució al navegador
        #cls.selenium.quit()
        super().tearDownClass()

    """ 
    ENUNCIAT:
    Crea un usuari amb permisos de 'staff' però sense cap permís ni grup especial. 
    Comprova que al logar-te no pots crear altres Users ni Questions.
    """
    def test_exercici_personalitzat(self):
        # anem directament a la pàgina d'accés a l'admin panel
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))

        # comprovem que el títol de la pàgina és el que esperem
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )

        # introduïm dades de login i cliquem el botó "Log in" per entrar
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('isard')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('pirineus')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()

        # testejem que hem entrat a l'admin panel comprovant el títol de la pàgina
        self.assertEqual( self.selenium.title , "Site administration | Django site admin" )

        # anem a la pàgina de creació d'usuaris
        self.selenium.get(f'{self.live_server_url}/admin/auth/user/add')

        # introduïm les dades del nou usuari
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('usuari_prova')
        password_input = self.selenium.find_element(By.NAME,"password1")
        password_input.send_keys('contrasenya123')
        password_input = self.selenium.find_element(By.NAME,"password2")
        password_input.send_keys('contrasenya123')

        # guardem les dades i continuem editant
        self.selenium.find_element(By.XPATH,'//input[@value="Save and continue editing"]').click()

        # assignem els permissos de 'staff' però sense cap permís ni grup especial. 
        self.selenium.find_element(By.NAME, "is_staff").click()

        # guardem les dades
        self.selenium.find_element(By.XPATH,'//input[@value="Save"]').click()

        # assercions per verificar si s'ha creat l'usuari
        usuari_creat = User.objects.get(username='usuari_prova') 
        self.assertEqual(usuari_creat.username, 'usuari_prova', "El nom del usuari es incorrecte.")

        # assercions per comprovar si l'usuari te drets d'staff
        self.assertTrue(usuari_creat.is_staff, "L'usuari no te drets d'staff")

        # sortim de la sessió
        self.selenium.find_element(By.XPATH, '//button[text()="Log out"]').click()

        # anem directament a la pàgina d'accés a l'admin panel
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))

        # comprovem que el títol de la pàgina és el que esperem
        self.assertEqual( self.selenium.title , "Log in | Django site admin" )

        # introduïm dades de login del nou usuari i cliquem el botó "Log in" per entrar
        username_input = self.selenium.find_element(By.NAME,"username")
        username_input.send_keys('usuari_prova')
        password_input = self.selenium.find_element(By.NAME,"password")
        password_input.send_keys('contrasenya123')
        self.selenium.find_element(By.XPATH,'//input[@value="Log in"]').click()

        # testejem que hem entrat a l'admin panel comprovant el títol de la pàgina i comprovem que no tenim permisos
        self.assertEqual( self.selenium.title , "Site administration | Django site admin" )

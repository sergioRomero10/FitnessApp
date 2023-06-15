# FitnessApp
Proyecto academico FitnessApp
Configuración de Credenciales de Google Auth.
Para el correcto funcionamiento del proyecto se debe configurar las credencailes de Google Auth. Google Auth es un servicio de autenticación y autorización que permite a los usuarios iniciar sesión en aplicaciones utilizando sus cuentas de Google.

## 1º Ve al Google Cloud Console y asegúrate de haber iniciado sesión con la cuenta de 
Google que deseas utilizar para autenticar tu aplicación.
https://cloud.google.com/gcp/?hl=es&utm_source=google&utm_medium=cpc&utm_campaign=emea-es-all-es-drbkws-all-all-trial-b-gcp-1011340&utm_content=text-ad-none-any-DEV_c-CRE_654887467820-
ADGP_Hybrid+%7C+BKWS+-+BRO+%7C+Txt+~+GCP+~+General%23v1-KWID_43700076003643598-kwd296993614710-userloc_9047045&utm_term=KW_console%20google%20cloud-NET_gPLAC_&&gad=1&gclid=CjwKCAjwm4ukBhAuEiwA0zQxk22fLgcU9Yvxugp2BQXqoZHOBFb3LtSICNoSuDqn4TKUMmJYnQ
XM-xoCkkEQAvD_BwE&gclsrc=aw.ds

## 2º Crea un nuevo proyecto o selecciona un proyecto existente en el que desees 
habilitar la autenticación de Google.

## 3º Dentro del proyecto, ve al menú de navegación y selecciona "API y servicios" y 
luego "Credenciales".
## 4ºHaz clic en el botón "Crear credenciales" y selecciona "ID de cliente OAuth" en el 
menú desplegable.
## 5ºEn la siguiente pantalla, elige el tipo de aplicación que estás desarrollando. Por 
ejemplo, si estás desarrollando una aplicación de servidor, selecciona "Aplicación 
web" o "Servidor".

## 6ºCompleta la configuración de la aplicación proporcionando la información 
requerida, como el nombre de la aplicación, las URL de redireccionamiento 
autorizadas, etc.
Borras la uri de Orígenes autorizados de JavaScript.
En la parte de URI de redireccionamiento autorizados deberás colocar la siguiente:
http://localhost/callback

## 7ºUna vez que hayas completado la configuración, haz clic en el botón "Crear" para 
generar las credenciales de OAuth.
## 8ºVerás una pantalla con tus credenciales recién creadas, incluyendo el ID de cliente 
y el secreto de cliente. Haz clic en el ícono de descarga junto al ID de cliente para 
obtener el archivo client_secret.json.

## 9ºCopia el archivo client_secret.json en el archivo que hay en mi proyecto con el 
mismo nombre, reemplazando mis datos por los tuyos.
En el main de Flask_app deberas pegar los siguientes valores del secret_client.json 
que te descargues
app.secret_key = "client_secret de client_secret.json"
GOOGLE_CLIENT_ID = “client_id de client_secret.json”

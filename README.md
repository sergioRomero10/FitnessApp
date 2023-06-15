# FitnessApp
Proyecto academico FitnessApp
Configuración de Credenciales de Google Auth.
Para el correcto funcionamiento del proyecto se debe configurar las credencailes de Google Auth. Google Auth es un servicio de autenticación y autorización que permite a los usuarios iniciar sesión en aplicaciones utilizando sus cuentas de Google.

**1º** Ve al [Google Cloud Console](https://www.googleadservices.com/pagead/aclk?sa=L&ai=DChcSEwj1pfODlMX_AhVwBwYAHX--CYkYABABGgJ3cw&ohost=www.google.com&cid=CAESauD2mt1fGWeMKMtXhUsRri7TisyQKIVLz8ZBUxM2WCtgMmQpqGUAxLhJW_TUvH0cveRQ6Hg748n3t63Ra8LeGs6-Bpma644b0RBRT0GkJi41pF_ypmh3T2GbhK3lp7SwJyYL1ewEOJXsQrg&sig=AOD64_2fqhzw_29vZnIY0NscfYUuujG2mg&q&adurl&ved=2ahUKEwiFgOyDlMX_AhW8V6QEHX5zAloQ0Qx6BAgJEAE) y asegúrate de haber iniciado sesión con la cuenta de 
Google que deseas utilizar para autenticar tu aplicación.



**2º** Crea un nuevo proyecto o selecciona un proyecto existente en el que desees 
habilitar la autenticación de Google.

**3º** Dentro del proyecto, ve al menú de navegación y selecciona "API y servicios" y 
luego "Credenciales".
**4º** Haz clic en el botón "Crear credenciales" y selecciona "ID de cliente OAuth" en el 
menú desplegable.
**5º** En la siguiente pantalla, elige el tipo de aplicación que estás desarrollando. Por 
ejemplo, si estás desarrollando una aplicación de servidor, selecciona "Aplicación 
web" o "Servidor".

**6º** Completa la configuración de la aplicación proporcionando la información 
requerida, como el nombre de la aplicación, las URL de redireccionamiento 
autorizadas, etc.
Borras la uri de Orígenes autorizados de JavaScript.
En la parte de URI de redireccionamiento autorizados deberás colocar la siguiente:
http://localhost/callback

**7º** Una vez que hayas completado la configuración, haz clic en el botón "Crear" para 
generar las credenciales de OAuth.
**8º** Verás una pantalla con tus credenciales recién creadas, incluyendo el ID de cliente 
y el secreto de cliente. Haz clic en el ícono de descarga junto al ID de cliente para 
obtener el archivo client_secret.json.

**9º** Copia el archivo client_secret.json en el archivo que hay en mi proyecto con el 
mismo nombre, reemplazando mis datos por los tuyos.
En el main de Flask_app deberas pegar los siguientes valores del secret_client.json 
que te descargues
app.secret_key = "client_secret de client_secret.json"
GOOGLE_CLIENT_ID = “client_id de client_secret.json”

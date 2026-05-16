# EmergencyRoutes_proyect

El proyecto consiste en elaborar un sistema de despacho de ambulancias que debe encontrar el hospital adecuado más cercano según el tipo de emergencia y la disponibilidad de camas. El sistema debe considerar tráfico en tiempo real y la disponibilidad de especialidades médicas.

Se construyó un dataset en formato csv basado en hospitales reales de Álvaro Obregón obtenidos mediante geolocalización pública.
Se usó [este link](https://overpass-turbo.eu/) para poblar el csv base sobre la inforamción de los hospitales para tal alcadía 

Ejecuta este código en la página para encontrar los mismos datos 
```{psql}
[out:json];

area["name"="Álvaro Obregón"]->.searchArea;

(
  node["amenity"="hospital"](area.searchArea);
  way["amenity"="hospital"](area.searchArea);
  relation["amenity"="hospital"](area.searchArea);
);

out center;
```
Una vez consultado dar click en exportar -> datos -> archivo json. 

Para probar la funcionalidad del proyecto hicimos modificaciones al archivo original: poblamos con especialidades para cada hospital reportado de forma articifial y borramos las tuplas inecesarias para el objetivo del proyecto

## Carga y limpieza de datos
Todo el código necesario para limpiar y poblar los datos con información necesaria del proyecto lo puedes encontrar aquí



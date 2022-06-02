# AnomalyDetection
TFM sobre detección de anomalías en sensores industriales en tiempo real usando técnicas de analítica avanzada.

Pasos:

* Descargamos consulta de BQ en "Datasets/Dataset_0/*.csv".

* Ejecutamos "TratamientoDatsaet/Etiquetado_Agregacion.ipynb".
    
    ** Unimos csv's.

    ** Etiquetamos anomalías 'Negro'.

    ** Etiquetamos anomalías 'Curvacola'.

    ** Agregamos al minuto.

        *** Mediana cada variable numérica.

        *** Std en humedades también.

        *** Unimos los valores únicos de espesor de cada minuto, y lo mismo con productos.

    ** Eliminamos filas con todo NA's (teniendo en cuenta todas las columnas salvo las mapeadas manualmente).

    ** Reordenamos columnas.

    ** Guardamos "Datasets/Dataset_2.csv".

* Ejecutamos EDA's.

* Ejecutamos "TratamientoDataset/FiltradoDataset.ipynb".

    ** Eliminamos 2022.

    ** Eliminamos parada agosto + intervalo anómalo.

    ** Eliminamos cambios de espesor y producto.

    ** Eliminamos registros con planta parada.

    ** Eliminamos outliers (nos quedamos con rango intercuartílico 0.01-0.99).

    ** Eliminamos filas con algún NA.

    ** Etiquetamos anomalías de congelado y de humedad.

    ** Sacamos proporciones de anomalías.

    ** Unimos todas las anomalías de humedades fuera del rango 5-20 en la anomalía 'Hum'.

    ** Guardamos "Datasets/Dataset_2.csv".
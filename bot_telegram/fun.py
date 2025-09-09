# librerias a utilizar
import numpy as np
import pandas as pd
import mplfinance as mpf
import plotly.express as px
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
import matplotlib.pyplot as plt

import chromadb
from chromadb.config import Settings
import os

import dotenv

dotenv.load_dotenv()


class AnalizeData:
    def __init__(self):
        """Constructor de la clase AnalizeData

        Args:
            name_coin (str): Nombre de la moneda a analizar

        """
        self.name_coin = os.getenv("NAME_COIN")
        self._uri_mongo = os.getenv("URI_MONGO")
        self._path_chromadb = os.getenv("PATH_CHROMADB")
        self._host_chromadb = os.getenv("HOST_CHROMADB_IP")
        self._port_chromadb = os.getenv("HOST_CHROMADB_PORT")
        self._coleccion_chromadb = f"{self.name_coin}_chroma"
        self._db_history = os.getenv("DB_HISTORY")
        self._db_actually = os.getenv("DB_ACTUALLY")
        self._coleccion_actually = f"{self.name_coin}_actual"
        self._coleccion_history = self.name_coin
        self._coleccion_chromadb = self.name_coin

        self.vector_result = None
        self.data_history = None
        self.data_actually = None
        self.query_vector = None
        self.data_progresion_historica_real = None
        self.data_progresion_historica_std = None
        self.data_history_acotada = None

        self.d_result = None
        self.df_fr = None
        self.df_final = None
        self.d_result_limit = None
        self.df_final_limit = None
        self.distance_min = None
        self.d_report = None

    def get_data_chroma(self, n_results: int = 15):
        """Obtener datos de ChromaDB

        Args:
            query_vector (list): Vector de consulta
            n_results (int, optional): Número de resultados a obtener. Defaults to 15.
        """
        # client = chromadb.PersistentClient(path=self._path_chromadb, settings=Settings(anonymized_telemetry=False))
        # client = chromadb.HttpClient(host="192.168.1.146", port=8000, settings=Settings(anonymized_telemetry=False, allow_reset=True))
        client = chromadb.HttpClient(
            host=self._host_chromadb,
            port=self._port_chromadb,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )
        collection = client.get_collection(self._coleccion_chromadb)

        self.vector_result = collection.query(
            query_embeddings=self.query_vector, n_results=n_results
        )

        return self.vector_result

    def get_data_history(self) -> pd.DataFrame:
        """
        Recupera datos históricos de la colección 'wifusdt_raw' en la base de datos 'cripto_test' de MongoDB.
        Esta función se conecta a una base de datos MongoDB en el localhost y extrae registros de la colección
        especificada. Los campos seleccionados incluyen 'timestamp', 'open', 'high', 'low', 'close',
        'basevolume' y 'usdtvolume'. La marca de tiempo se convierte a un formato de fecha legible y se agrega
        como una nueva columna en el DataFrame resultante.

        Args:
            uri (str): host de la base de datos
            db_history (str): La base de datos de MongoDB desde la cual se extraen los datos.
            coleccion_history (str): La colección de MongoDB desde la cual se extraen los datos.

        Returns:
            pd.DataFrame: Un DataFrame de pandas que contiene los datos históricos de precios y volúmenes
            de la criptomoneda, con una columna adicional 'date' que representa la fecha correspondiente
            a cada marca de tiempo.
        """

        # conexion a base de datos
        con = MongoClient(self._uri_mongo)
        db = con[self._db_history]
        col = db[self._coleccion_history]

        print(self._coleccion_history)

        # busqueda en base de datos
        q = {}
        p = {
            "_id": 0,
            "open_time": 1,
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "basevolume": 1,
            "usdtvolume": 1,
        }

        # cursor de busqueda
        cursor = col.find(q, p)

        # convirtiendo de dataframe
        self.data_history = pd.DataFrame.from_records(cursor)

        # creando la variable date
        self.data_history["date"] = pd.to_datetime(
            self.data_history["open_time"], unit="ms"
        )

        return self.data_history

    def _get_df_actually(self, n: int = 60) -> pd.DataFrame:
        """Obtener los datos actuales desde una colección en una base de datos.
        Esta función recupera las últimas `n` velas de una colección de MongoDB, ordenándolas en
        función de su identificador. Los datos son convertidos a tipos adecuados para su análisis
        y se devuelven en un DataFrame de pandas.

        Args:
            uri: host de la base de datos
            db_actually (str): La base de datos de MongoDB desde la cual se extraen los datos.
            col_actually (str): La colección de MongoDB desde la cual se extraen los datos.
            n (int, optional): Cantidad de velas a traer. Por defecto es 30.

        Returns:
            pd.DataFrame: DataFrame que contiene los datos actuales de las últimas `n` velas, con las columnas convertidas a los tipos de datos apropiados (float para precios y volumen, int para el tiempo).
        """

        # conexion a base de datos
        con = MongoClient(self._uri_mongo)
        db = con[self._db_actually]
        col = db[self._coleccion_actually]

        # criterios de busqueda
        q = {}
        p = {}

        # cursor de busqueda
        cursor = col.find(q, p).sort("_id", -1).limit(n)

        # creando dataframe
        df = pd.DataFrame.from_records(cursor)

        # Verificar si el DataFrame está vacío antes de realizar conversiones
        if df.empty:
            return df

        # Convertir tipos de datos
        float_columns = ["c", "o", "l", "h", "v"]

        int_columns = ["t"]

        for column in float_columns:
            if column in df.columns:
                df[column] = df[column].astype(float)

        for column in int_columns:
            if column in df.columns:
                df[column] = df[column].astype(int)

        # ordenando
        df.sort_values(by="t", ascending=True, inplace=True)

        return df

    def get_data_actually(self, n: int = 60) -> tuple:
        """Obtener y normalizar los datos actuales de cierre.
        Esta función utiliza `get_df_actually` para obtener los datos actuales de cierre,
        y luego normaliza esos datos. Devuelve el DataFrame original, un DataFrame con los
        valores normalizados y una lista de los valores normalizados.

        Args:
            uri: host de la base de datos
            db_actually (str): La base de datos de MongoDB desde la cual se extraen los datos.
            col_actually (str): La colección de MongoDB desde la cual se extraen los datos.
            n (int, optional): Cantidad de velas a traer. Por defecto es 30.

        Returns:
            tuple: Un tuple que contiene:
                - pd.DataFrame: DataFrame original con los datos actuales.
                - pd.DataFrame: DataFrame con los datos de cierre normalizados.
                - list: Lista de los valores normalizados de cierre.
        """

        # obtener la data actual
        df = self._get_df_actually(n)

        # Verificar si hay datos
        if df.empty:
            return df, []

        # obteniendo los valores maximos y minimos
        value_close_min = df.c.min()
        value_close_max = df.c.max()

        # Normalizar los valores de cierre
        if value_close_max > value_close_min:
            df["close_nor1"] = (df.c - value_close_min) / (
                value_close_max - value_close_min
            )
            df["close_nor2"] = df.c / value_close_max
        else:
            df["close_nor1"] = 0
            df["close_nor2"] = 0

        # obteniendo una lista
        self.query_vector = df["close_nor1"].tolist()
        self.data_actually = df

        return self.data_actually, self.query_vector

    def gen_prog_hist_real(self, n: int = 120) -> pd.DataFrame:
        """
        Genera un DataFrame con la progresión histórica real de los datos.

        Args:
            result (dict): Un diccionario que contiene los resultados de la consulta.

        Returns:
        pd.DataFrame: DataFrame concatenado con los datos históricos y las columnas calculadas.
        """

        # obteniendo los indices
        idsx = self.vector_result.get("ids", None)
        idsx = idsx[0]

        # obteniendo las distancias
        distances = self.vector_result.get("distances", None)
        distances = distances[0]

        # lista de resultado final
        ls_dfr = []

        for i, j, d in zip(range(len(idsx)), idsx, distances):

            # Haciendo cast del índice
            j = int(j)

            # Seleccionando el desde j hasta j+n
            dfa = self.data_history.iloc[j : (j + n)].copy()

            # valores de referencia
            value_ref = self.data_history.iloc[j]["close"]

            # calculando indices
            dfa["a"] = 1
            dfa["i"] = list(range(len(dfa)))
            dfa["c"] = dfa["close"] / value_ref

            # dfa['c1'] = (dfa['close'] - dfa['close'].min()) / (dfa['close'].max() - dfa['close'].min())

            # agegando metadata orden y distancia
            dfa["orden"] = i
            dfa["distance"] = d

            # agregando a lista
            ls_dfr.append(dfa)

        # concatenando
        dfr = pd.concat(ls_dfr)

        # renombrando columnas
        dfr.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
                "date": "Date",
            },
            inplace=True,
        )

        self.data_progresion_historica_real = dfr

        return self.data_progresion_historica_real

    def gen_prog_hist_std(self, n: int = 120, plot: bool = True) -> pd.DataFrame:
        """obtenie la progresion historica relativa (c) a parti del punto historico equivalente al actual

        Args:
            result (dict): Un diccionario que debe contener las claves 'ids' y 'distances'.
            df (pd.DataFrame): DataFrame que contiene los datos históricos (por ejemplo, precios).
            n (int, optional): Cantidad de velas en adelante que debe considerar. Defaults to 120.
            plot (bool, optional): Si se deben mostrar gráficos de los datos. Defaults to True.

        Returns:
            pd.DataFrame: DataFrame concatenado con los datos históricos y las columnas calculadas.
        """

        # obteniendo los indices
        idsx = self.vector_result.get("ids", None)
        idsx = idsx[0]

        # obteniendo las distancias
        distances = self.vector_result.get("distances", None)
        distances = distances[0]

        # mostrando las distancias
        # print(distances)

        if distances:
            if len(distances):
                self.distance_min = distances[0]

        # lista de resultado final
        ls_dfr = []

        for i, j, d in zip(range(len(idsx)), idsx, distances):

            # Haciendo cast del índice
            j = int(j)

            # Seleccionando el desde j hasta j+n
            dfa = self.data_history.iloc[j : (j + n)].copy()

            # obteniendo los valores de cierre del primera vela de referencia
            value_ref = self.data_history.iloc[j]["close"]

            # agregando indice
            dfa["i"] = list(range(len(dfa)))

            # calculando indices
            dfa["a"] = 1  # columna auxiliar

            # calculando indices c
            dfa["c"] = dfa["close"] / value_ref
            # dfa['c1'] = (dfa['close'] - dfa['close'].min()) / (dfa['close'].max() - dfa['close'].min())

            # agegando metadata de orden y distancia
            dfa["orden"] = i
            dfa["distance"] = d

            # agregando a lista
            ls_dfr.append(dfa)

        # concatenando
        dfr = pd.concat(ls_dfr)

        self.data_progresion_historica_std = dfr

        # Mostrando comportamiento de índice c si se solicita
        if plot:
            fig = px.line(
                self.data_progresion_historica_std, x="i", y="c", color="orden"
            )
            fig.show()

        return self.data_progresion_historica_std

    def gen_hist_std(self, n: int = 60, plot: bool = True) -> pd.DataFrame:
        """Obtener los datos históricos standarizados a c y c1 a partir del índice enviado en result.
        Args:
            result (dict): Un diccionario que debe contener las claves 'ids' y 'distances'.
            df (pd.DataFrame): DataFrame que contiene los datos históricos (por ejemplo, precios).
            n (int, optional): Cantidad de velas en adelante que debe considerar. Defaults to 30.
            plot (bool, optional): Si se deben mostrar gráficos de los datos. Defaults to True.
        Returns:
            pd.DataFrame: DataFrame concatenado con los datos históricos y las columnas calculadas.
        Raises:
            KeyError: Si 'ids' o 'distances' no están presentes o no son listas.
            IndexError: Si los índices están fuera del rango del DataFrame.
        """

        # Obteniendo los índices de referencia
        idsx = self.vector_result.get("ids", None)
        distances = self.vector_result.get("distances", None)

        # Verificando que contenga datos
        if idsx is None or distances is None:
            raise KeyError(
                "El diccionario debe contener las claves 'ids' y 'distances' y no estar vacíos."
            )

        # Verificando que contenga listas
        if not isinstance(idsx, list) or not isinstance(distances, list):
            raise TypeError("El contenido de 'ids' y 'distances' debe ser una lista.")

        # Verificando que ambas listas tengan la misma longitud
        if len(idsx) != len(distances):
            raise ValueError(
                "Las listas 'ids' y 'distances' deben tener la misma longitud."
            )

        # obteniendo el valor objetivo de la posicion 0
        idsx = idsx[0]

        # obteniendo el valor objetivo de la posicion 0
        distances = distances[0]

        # Lista de resultado final
        ls_dfr = []

        for i, j, d in zip(range(len(idsx)), idsx, distances):

            # Haciendo cast del índice
            j = int(j)

            # Verificando que el índice esté dentro del rango del DataFrame
            if j < 0 or j + n > len(self.data_history):
                raise IndexError(f"El índice {j} está fuera del rango del DataFrame.")

            # Seleccionando el desde j hasta j+n
            dfa = self.data_history.iloc[j : (j + n)].copy()

            # Calculando índices
            dfa["a"] = 1
            dfa["i"] = list(range(len(dfa)))
            dfa["c"] = dfa["close"] / dfa["close"].max()
            dfa["c1"] = (dfa["close"] - dfa["close"].min()) / (
                dfa["close"].max() - dfa["close"].min()
            )

            # Agregando metadata
            dfa["orden"] = i
            dfa["distance"] = d

            # Agregando a lista de DataFrame
            ls_dfr.append(dfa)

        # Concatenando los DataFrames
        dfr = pd.concat(ls_dfr, ignore_index=True)

        self.data_history_acotada = dfr

        # Mostrando comportamiento de índice c si se solicita
        if plot:
            fig = px.line(
                self.data_history_acotada,
                x="i",
                y="c",
                color="orden",
                title="Comportamiento de c",
            )
            fig.show()

            # Mostrando comportamiento de índice c1 si se solicita
            fig2 = px.line(
                self.data_history_acotada,
                x="i",
                y="c1",
                color="orden",
                title="Comportamiento de c1",
            )
            fig2.show()

        return self.data_history_acotada

    def _summary(
        self, diff_amp: int = 1000, limit: bool = False, print_resume: bool = False
    ) -> tuple:

        dfph = self.data_progresion_historica_std.copy()
        dfph.sort_values("open_time", inplace=True)

        ref_value = self.data_actually.iloc[-1]["c"]
        # time_ref = datetime.fromtimestamp(df_act.iloc[-1]["T"])
        time_ref = pd.to_datetime(self.data_actually.iloc[-1]["T"], unit="ms")

        ls = []
        for g in dfph.orden.unique():

            try:
                dfa = dfph.loc[dfph.orden == g,].iloc[60:].reset_index(drop=True).copy()

                ref_value_g = dfa.loc[dfa.orden == g,].iloc[0]["close"]
                dfa["c"] = dfa["close"] / ref_value_g
                ls.append(dfa)
            except:
                print(dfa)

        dfph = pd.concat(ls)

        if limit:
            dfph = dfph.groupby(by="orden", as_index=False).head(30)

        # identificando el minimo de cada grupo
        df_f_top_min = (
            dfph.groupby(by="orden", as_index=False)["c"]
            .min()
            .rename(columns={"c": "min"})
        )

        # identificando el maxima de cada grupo
        df_f_top_max = (
            dfph.groupby(by="orden", as_index=False)["c"]
            .max()
            .rename(columns={"c": "max"})
        )

        # realizando un merge de maximo y minimo de cada grupo
        df_f = df_f_top_max.merge(df_f_top_min, on="orden")

        df_f["max_value"] = df_f["max"] * ref_value
        df_f["min_value"] = df_f["min"] * ref_value

        # sacando el diferencia con repecto a la unidad
        df_f["max"] = df_f["max"] - 1
        df_f["min"] = df_f["min"] - 1

        # amplificando la diferncia
        df_f["max"] = diff_amp * df_f["max"]
        df_f["min"] = diff_amp * df_f["min"]

        # identificando cuando el maximo y el minimo amplificado son positivos
        df_f["pp"] = (df_f["max"] > 0) & (df_f["min"] > 0)

        # sumando las diferencias amplificadas
        df_f["dif_max_min"] = df_f["max"] + df_f["min"]

        # identificando cuando la suma de diferencias amplificadas es postivo
        df_f["dif_max_min_p"] = df_f["dif_max_min"] > 0

        df_f["ref_value"] = ref_value

        df_f = df_f[
            [
                "orden",
                "max",
                "min",
                "max_value",
                "ref_value",
                "min_value",
                "pp",
                "dif_max_min",
                "dif_max_min_p",
            ]
        ]

        # agrupando cuando la suma de diferencia amplificadas en positvo y negativo
        df_fr = (
            df_f.groupby(by="dif_max_min_p", as_index=False)["orden"]
            .count()
            .rename(columns={"orden": "casos"})
        )

        # obteniendo la proporcion por la cantidad de casos o filas de df original
        df_fr["prop"] = 100 * df_fr["casos"] / df_fr["casos"].sum()

        d_result = {
            "ref": {"value": ref_value, "time": time_ref},
            "distance_min": self.distance_min,
            "relation": {
                "bull": len(df_f.loc[df_f.dif_max_min_p]),
                "bear": len(df_f.loc[~df_f.dif_max_min_p]),
            },
            "mean": {
                "max": df_f["max"].mean(),
                "min": df_f["min"].mean(),
                "max_value": df_f["max_value"].mean(),
                "min_value": df_f["min_value"].mean(),
            },
            "max": {
                "max": df_f["max"].max(),
                "min": df_f["min"].max(),
                "max_value": df_f["max_value"].max(),
                "min_value": df_f["min_value"].max(),
            },
            "min": {
                "max": df_f["max"].min(),
                "min": df_f["min"].min(),
                "max_value": df_f["max_value"].min(),
                "min_value": df_f["min_value"].min(),
            },
        }

        # mostrando resumes
        if print_resume:
            print("-------------------------------------")
            print("relacion")
            print(df_fr)

            print("-------------------------------------")
            print("valor de referencia")
            print(f"valor de referencia: {d_result['ref']['value']}")
            print(f"fecha de referencia: {d_result['ref']['time']}")

            print("-------------------------------------")
            print("media")
            print(f"mean max {d_result['mean']['max']}")
            print(f"mean min {d_result['mean']['min']}")
            print(f"mean max value  {d_result['mean']['max_value']:.4f}")
            print(f"mean min values {d_result['mean']['min_value']:.4f}")

            print("-------------------------------------")
            print("Optimista")
            print(f"max max {d_result['max']['max']}")
            print(f"min min {d_result['min']['min']}")
            print(f"mean max value  {d_result['max']['max_value']:.4f}")
            print(f"mean min values {d_result['min']['min_value']:.4f}")

            print("-------------------------------------")
            print("-Conservador")
            print(f"min max {d_result['max']['min']}")
            print(f"max min {d_result['min']['max']}")
            print(f"mean max value  {d_result['max']['min_value']:.4f}")
            print(f"mean min values {d_result['min']['max_value']:.4f}")

        return df_f, df_fr, d_result

    def summary_general(self):
        self.df_final, self.df_fr, self.d_result = self._summary(limit=False)
        return self.df_final, self.df_fr, self.d_result

    def summary_limit(self):
        self.df_final_limit, self.df_fr_limit, self.d_result_limit = self._summary(
            limit=True
        )
        return self.df_final_limit, self.df_fr_limit, self.d_result_limit

    def gen_report(self):

        d_report = {
            "type": None,
            "ref": {
                "value": None,
                "date": None,
                "distance": None,
            },
            "general": {"mean": None, "max": None, "min": None},
            "limit": {"mean": None, "max": None, "min": None},
            "trigger": False,
        }

        # -----------------------------------------------------
        # type

        f_bull = (self.d_result["relation"]["bull"] >= 8) & (
            self.d_result_limit["relation"]["bull"] >= 8
        )
        f_bear = (self.d_result["relation"]["bear"] >= 8) & (
            self.d_result_limit["relation"]["bear"] >= 8
        )

        type = "sideways"

        if f_bull:
            type = "bull"
        elif f_bear:
            type = "bear"

        # -----------------------------------------------------

        d_report["type"] = type
        d_report["ref"]["value"] = self.d_result["ref"]["value"]
        d_report["ref"]["date"] = (
            self.d_result["ref"]["time"]
            .tz_localize("UTC")
            .tz_convert("America/Caracas")
            .strftime("%Y-%m-%d %H:%M:%S")
        )
        d_report["ref"]["distance_limit"] = round(
            self.d_result_limit["distance_min"], 2
        )
        d_report["ref"]["distance"] = round(self.d_result_limit["distance_min"], 2)
        d_report["relation_limit"] = self.d_result_limit["relation"]
        d_report["relation_general"] = self.d_result["relation"]

        # -----------------------------------------------------

        var_type = "min_value"

        if type == "bull":
            var_type = "max_value"

        elif type == "bear":
            var_type = "min_value"

        d_report["general"]["mean"] = round(self.d_result["mean"][var_type], 4)
        d_report["general"]["max"] = round(self.d_result["max"][var_type], 4)
        d_report["general"]["min"] = round(self.d_result["min"][var_type], 4)

        d_report["limit"]["mean"] = round(self.d_result_limit["mean"][var_type], 4)
        d_report["limit"]["max"] = round(self.d_result_limit["max"][var_type], 4)
        d_report["limit"]["min"] = round(self.d_result_limit["min"][var_type], 4)

        # -----------------------------------------------------

        self.d_report = d_report

        return self.d_report

    def graf(self, save: bool = True):

        # Graficaciond de las velas actuales

        df_act_v2 = pd.DataFrame(
            {
                "Open": self.data_actually["o"],
                "High": self.data_actually["h"],
                "Low": self.data_actually["l"],
                "Close": self.data_actually["c"],
                "Volume": self.data_actually["v"],
                "Date": pd.to_datetime(self.data_actually["t"], unit="ms"),
            }
        )

        df_act_v2.set_index("Date", inplace=True)

        if save:
            mpf.plot(
                df_act_v2,
                type="candle",
                style="charles",
                title=f"Actually",
                savefig=f"result/{self.name_coin}_actually.png",
            )
        else:
            mpf.plot(df_act_v2, type="candle", style="charles", title=f"Actually")

        # Graficacion de las velas historicas

        n_order = self.data_progresion_historica_std["orden"].max()

        for i in range(n_order):

            try:

                data = self.data_progresion_historica_std.query(f"orden=={i}").copy()
                data.rename(columns={"date": "Date"}, inplace=True)
                data.set_index("Date", inplace=True)

                ref_date = data.iloc[60].name.__str__()
                # print(ref_date)

                # Crear una figura con dos subgráficos
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

                # Graficar el primer gráfico de velas
                mpf.plot(
                    data,
                    type="candle",
                    style="charles",
                    ax=ax1,
                    vlines=dict(vlines=[ref_date], colors="red", linewidths=1),
                    show_nontrading=True,
                )

                # Graficar el segundo gráfico de velas
                mpf.plot(
                    data.iloc[40:90],
                    type="candle",
                    style="charles",
                    ax=ax2,
                    vlines=dict(vlines=[ref_date], colors="red", linewidths=1),
                )

                # Agregar títulos manualmente
                ax1.set_title(f"Orden {i}")
                ax2.set_title(f"Orden {i} :30 pits")

                # Ajustar el layout
                plt.tight_layout()

                if save:
                    plt.savefig(f"result/{self.name_coin}_orden_{i}.png")
                else:
                    plt.show()
            except:
                print(f"Error en el orden {i}")
            finally:
                plt.close(fig)
                plt.clf()

    def verify_trigger(self, umbral_trigger: int = 13, umbral_distance: float = 1.2):

        bull_general = self.d_report["relation_general"].get("bull",0)
        bear_general = self.d_report["relation_general"].get("bear",0)

        bull_limit = self.d_report["relation_limit"].get("bull",0)
        bear_limit = self.d_report["relation_limit"].get("bear",0)

        condition_bull = (bull_general >= umbral_trigger) and (bull_limit >= umbral_trigger) and (self.d_report["ref"]["distance"] <= umbral_distance)
        condition_bear = (bear_general >= umbral_trigger) and (bear_limit >= umbral_trigger) and (self.d_report["ref"]["distance"] <= umbral_distance)

        if condition_bull or condition_bear:
            self.d_report["trigger"] = True

        return self.d_report

    def cargar(self):
        self.get_data_history()

    def actualizar(self):
        self.get_data_actually()
        self.get_data_chroma()
        self.gen_hist_std(plot=False)
        self.gen_prog_hist_real()
        self.gen_prog_hist_std(plot=False)
        self.summary_general()
        self.summary_limit()
        self.gen_report()
        # self.graf()

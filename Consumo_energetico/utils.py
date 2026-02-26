from Consumo_energetico.models import *
from django.shortcuts import render
from Mes.models import *
import json
from django.http import HttpRequest, HttpResponse
from typing import Dict, Any, Optional
from collections import defaultdict
from django.db.models import QuerySet
from Anio.models import Anio
from observatorioeconomico.utils import get_default_anio_id_for_model


class EnergiaDataProcessor:
    """
    Reglas:
    - En las vistas por TARIFA (comercial/industrial/residencial): el DEFAULT_YEAR se calcula
      SIEMPRE para ESA tarifa (Cammesa, valor_id=1).
    - En el RESUMEN: el DEFAULT_YEAR debe ser un año "completo" donde existan datos en:
        * Cammesa (valor_id=1) para TODAS las tarifas
        * Refsa para TODAS las tarifas
      Si el usuario elige un año incompleto, se cae al default "completo" y se muestra error_message.
    """

    DEFAULT_VALUE = 1  # Formosa

    # =========================
    # CAMMESA: DEFAULT YEAR POR TARIFA (serie)
    # =========================
    @classmethod
    def get_default_year_cammesa_by_tarifa(cls, tarifa_id: int) -> Optional[int]:
        return get_default_anio_id_for_model(
            Cammesa,
            base_filters={
                "valor_id": cls.DEFAULT_VALUE,  # Formosa
                "tarifa_id": tarifa_id,
            },
        )

    # =========================
    # RESUMEN: DEFAULT YEAR "COMPLETO" (Cammesa+Refsa y TODAS las tarifas)
    # =========================
    @classmethod
    def is_year_complete_for_resumen(cls, anio_id: int) -> bool:
        tarifas = list(TipoTarifa.objects.values_list("id", flat=True))

        for tarifa_id in tarifas:
            existe_cammesa = Cammesa.objects.filter(
                anio_id=anio_id,
                tarifa_id=tarifa_id,
                valor_id=cls.DEFAULT_VALUE,  # Formosa
            ).exists()

            existe_refsa = Refsa.objects.filter(
                anio_id=anio_id,
                tarifa_id=tarifa_id,
            ).exists()

            if not (existe_cammesa and existe_refsa):
                return False

        return True

    @classmethod
    def get_default_year_resumen(cls) -> Optional[int]:
        anios = Anio.objects.order_by("-anio").values_list("id", flat=True)
        for anio_id in anios:
            if cls.is_year_complete_for_resumen(anio_id):
                return anio_id
        return None

    # =========================
    # CONSULTA CAMMESA (serie)
    # =========================
    @staticmethod
    def get_data_cammesa(**kwargs) -> QuerySet:
        return Cammesa.objects.select_related("mes", "anio", "valor", "tarifa").values(
            "mes__mes",
            "anio__anio",
            "valor__valor",
            "tarifa__tipo_tarifa",
            "demanda",
            "variacion_interanual",
            "variacion_intermensual",
        ).filter(**kwargs)

    @classmethod
    def get_filtered_data(cls, tarifa: int, params: Dict[str, Any]) -> QuerySet:
        if params["is_valid"]:
            return cls.get_data_cammesa(
                anio_id__gte=params["anio_inicio"],
                anio_id__lte=params["anio_fin"],
                tarifa_id=tarifa,
                valor_id=cls.DEFAULT_VALUE,  # SIEMPRE Formosa
            ).order_by("anio__anio", "mes__id")

        default_year = cls.get_default_year_cammesa_by_tarifa(tarifa)

        # Si no hay año para esa tarifa, devolvemos queryset vacío (no rompe)
        if default_year is None:
            return cls.get_data_cammesa(pk__in=[])

        return cls.get_data_cammesa(
            anio_id=default_year,
            tarifa_id=tarifa,
            valor_id=cls.DEFAULT_VALUE,  # SIEMPRE Formosa
        ).order_by("anio__anio", "mes__id")

    # =========================
    # PARAMS (serie)
    # =========================
    @classmethod
    def procces_request_parameters(cls, request: HttpRequest) -> Dict[str, Any]:
        try:
            anio_inicio = request.GET.get("anio_inicio")
            anio_fin = request.GET.get("anio_fin")

            filtros = {}

            if not anio_inicio and not anio_fin:
                return {
                    "anio_inicio": None,
                    "anio_fin": None,
                    "is_valid": False,
                    "error_message": None,
                }

            if anio_inicio:
                filtros["anio_inicio"] = int(anio_inicio)
            if anio_fin:
                filtros["anio_fin"] = int(anio_fin)

            if "anio_inicio" in filtros and "anio_fin" in filtros:
                if filtros["anio_fin"] < filtros["anio_inicio"]:
                    return {
                        **filtros,
                        "is_valid": False,
                        "error_message": "Los filtros aplicados son incorrectos: el año de fin no puede ser menor que el de inicio.",
                    }
                return {**filtros, "is_valid": True, "error_message": None}

            return {
                **filtros,
                "is_valid": False,
                "error_message": "Debe seleccionar ambos años para aplicar el filtro.",
            }

        except ValueError:
            return {
                "anio_inicio": None,
                "anio_fin": None,
                "is_valid": False,
                "error_message": "Los filtros ingresados no son válidos.",
            }

    # =========================
    # CHART (serie)
    # =========================
    @staticmethod
    def process_chart_data_totales(data_variacion: QuerySet) -> Dict[str, dict]:
        context_chart_formosa = defaultdict(list)

        for item in data_variacion:
            anio = item["anio__anio"]
            demanda = item["demanda"] or 0
            if item["valor__valor"] == "Formosa":
                context_chart_formosa[anio].append(demanda)

        return {"Formosa": dict(context_chart_formosa)}

    # =========================
    # RESUMEN: filtro año (1 solo)
    # =========================
    @classmethod
    def procesar_filtro_anio_resumen(cls, request: HttpRequest) -> dict:
        anio = request.GET.get("anio")

        if not anio:
            return {
                "anio": None,   # No forzamos año
                "is_valid": True,
                "error_message": None,
            }

        try:
            return {
                "anio": int(anio),
                "is_valid": True,
                "error_message": None,
            }
        except ValueError:
            return {
                "anio": None,
                "is_valid": True,
                "error_message": "El año ingresado no es válido.",
            }

    # =========================
    # RESUMEN - DEMANDA (Cammesa)
    # =========================
    @classmethod
    def get_last_demanda_by_tarifa_year(cls, params: dict) -> dict:
        tarifas = TipoTarifa.objects.all().order_by("id")
        series, labels = [], []

        for tarifa in tarifas:
            qs = Cammesa.objects.filter(
                tarifa=tarifa,
                valor_id=cls.DEFAULT_VALUE,
            )

            # Si el usuario seleccionó año
            if params.get("anio") is not None:
                qs_anio = qs.filter(anio_id=params["anio"])
                if qs_anio.exists():
                    qs = qs_anio

            # Siempre trae el último disponible para esa tarifa
            ultimo = qs.order_by("-anio__anio", "-mes__id").values("demanda").first()

            valor = float(ultimo["demanda"]) if ultimo and ultimo["demanda"] not in [None, ""] else 0.0

            series.append(valor)
            labels.append(tarifa.tipo_tarifa)

        return {"series": series, "labels": labels}

    # =========================
    # RESUMEN - USUARIOS (Refsa)
    # =========================
    @staticmethod
    def get_last_usuarios_by_tarifa_year(params: dict) -> dict:
        tarifas = TipoTarifa.objects.all().order_by("id")
        resultados = {}

        for tarifa in tarifas:
            qs = Refsa.objects.filter(tarifa=tarifa)

            # Intentar usar año seleccionado
            if params.get("anio") is not None:
                qs_anio = qs.filter(anio_id=params["anio"])
                if qs_anio.exists():
                    qs = qs_anio

            registros = list(
                qs.order_by("-anio__anio", "-mes__id").values("cantidad_usuarios")
            )

            valor = 0.0

            for r in registros:
                cu = r.get("cantidad_usuarios")
                if cu not in ["0", 0, None, ""]:
                    valor = float(cu)
                    break

            resultados[tarifa.tipo_tarifa] = [valor]

        return resultados


def diccionario(queryset):
    formosa_intermensual = []
    formosa_interanual = []
    meses_formosa = []

    for item in queryset:
        mes = item["mes__mes"] + " " + str(item["anio__anio"])
        region = item["valor__valor"]
        intermensual = float(item["variacion_intermensual"])
        interanual = float(item["variacion_interanual"])

        if region == "Formosa":
            formosa_intermensual.append(intermensual)
            formosa_interanual.append(interanual)
            meses_formosa.append(mes)

    minimo = min(len(formosa_intermensual), len(formosa_interanual))

    return {
        "meses": meses_formosa[:minimo],
        "Valor intermensual Formosa": formosa_intermensual[:minimo],
        "Valor interanual Formosa": formosa_interanual[:minimo],
    }


def process_energia_data(
    request: HttpRequest,
    tarifa: int,
    context_keys: Dict[str, str],
    descripcion_modelo: str,
    template: str,
) -> HttpResponse:
    processor = EnergiaDataProcessor
    meses = Mes.objects.all()

    params = processor.procces_request_parameters(request)
    data_variacion = processor.get_filtered_data(tarifa, params)
    diccionario_variacion = diccionario(data_variacion)
    context_chart = processor.process_chart_data_totales(data_variacion)
    anios = Anio.objects.all().order_by("anio")
    context = {
        "error_message": params["error_message"],
        context_keys["data_variacion"]: data_variacion,
        context_keys["diccionario_variacion"]: diccionario_variacion,
        "data_chart_formosa": json.dumps(context_chart["Formosa"]),
        "descripcion_modelo": descripcion_modelo,
        "meses": meses,
         "anios": anios,
    }

    return render(request, template, context)


def process_energia_resumen(
    request: HttpRequest,
    descripcion_modelo: str,
    template: str,
) -> HttpResponse:
    processor = EnergiaDataProcessor

    # Año válido para resumen (tiene que estar completo para TODAS las tarifas)
    params = processor.procesar_filtro_anio_resumen(request)

    # DEMANDA (torta) - siempre 3 tarifas
    demanda = processor.get_last_demanda_by_tarifa_year(params)
    demanda_series = json.dumps(demanda["series"])
    demanda_labels = json.dumps(demanda["labels"])

    # USUARIOS (barras) - siempre 3 tarifas
    usuarios = processor.get_last_usuarios_by_tarifa_year(params)
    usuarios_json = json.dumps(usuarios)

    anios = Anio.objects.all().order_by("anio")

    context = {
        "error_message": params["error_message"],
        "descripcion_modelo": descripcion_modelo,
        "demanda_series": demanda_series,
        "demanda_labels": demanda_labels,
        "usuarios_barras": usuarios_json,
        "anios": anios,
        # por si querés mostrar qué año quedó aplicado realmente
        "anio_aplicado": params.get("anio"),
    }

    return render(request, template, context)
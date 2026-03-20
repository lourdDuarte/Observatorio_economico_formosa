from typing import Optional
from Anio.models import Anio

def get_default_anio_id_for_model(
    model_cls,
    base_filters: Optional[dict] = None,
    nonzero_field: Optional[str] = None,
    nonzero_value=0,
) -> Optional[int]:
    """
    Devuelve el anio_id por defecto para un modelo:

    - Recorre los años de Anio del más nuevo al más viejo.
    - Devuelve el primer anio_id para el cual el modelo tiene registros (aplicando base_filters si existen).
    - Si se pasa nonzero_field, solo considera registros donde ese campo sea distinto de nonzero_value.
    - Si no hay datos en ningún año, devuelve None.
    """
    anio_ids = list(Anio.objects.order_by('-anio').values_list('id', flat=True))
    if not anio_ids:
        return None

    qs = model_cls.objects.all()
    if base_filters:
        qs = qs.filter(**base_filters)
    if nonzero_field:
        qs = qs.exclude(**{nonzero_field: nonzero_value})

    for anio_id in anio_ids:
        if qs.filter(anio_id=anio_id).exists():
            return anio_id

    return None

from typing import Optional, List


def get_default_anio_id_for_model_with_valores(
     model_cls,
    field_name: str,
    required_values: list,
    extra_filters: dict = None,
):
    anio_ids = list(
        Anio.objects.order_by('-anio').values_list('id', flat=True)
    )

    for anio_id in anio_ids:
        qs = model_cls.objects.filter(anio_id=anio_id)

        if extra_filters:
            qs = qs.filter(**extra_filters)

        values_present = set(
            qs.values_list(field_name, flat=True)
        )

        if all(val in values_present for val in required_values):
            return anio_id

    return None
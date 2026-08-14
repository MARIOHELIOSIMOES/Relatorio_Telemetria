from datetime import datetime


def obter_turno(data_hora=None):

    if data_hora is None:
        data_hora = datetime.now()

    hora = data_hora.hour

    if 0 <= hora < 6:
        return "1"

    if 6 <= hora < 12:
        return "2"

    if 12 <= hora < 18:
        return "3"

    return "4"


def obter_horario_turno(turno):

    horarios = {
        "1": "00:00 às 05:59",
        "2": "06:00 às 11:59",
        "3": "12:00 às 17:59",
        "4": "18:00 às 23:59",
    }

    return horarios.get(
        turno,
        "Turno desconhecido"
    )
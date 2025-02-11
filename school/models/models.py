# -*- coding: utf-8 -*-
import logging
from xml.dom import ValidationErr
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Evento(models.Model):
    _name = "gestion.colegio.evento"
    _description = "Evento Escolar"

    name = fields.Char(string="Nombre", compute="_compute_name", required=True)
    tipo_evento = fields.Selection(
        [
            ("ausencia", "Ausencia"),
            ("retraso", "Retraso"),
            ("felicitacion", "Felicitación"),
            ("comportamiento", "Comportamiento"),
        ],
        string="Tipo de Evento",
        required=True,
    )
    fecha = fields.Date(string="Fecha", default=fields.Date.today, required=True)
    descripcion = fields.Text(string="Descripción")
    clase_id = fields.Many2one("gestion.colegio.clase", string="Clase", required=True)
    profesor_id = fields.Many2one(
        "hr.employee", string="Profesor", domain=[("es_profesor", "=", True)]
    )
    alumno_id = fields.Many2one("gestion.colegio.alumno", string="Alumno")

    @api.depends("clase_id", "tipo_evento")
    def _compute_name(self):
        for evento in self:
            if evento.clase_id and evento.tipo_evento:
                evento.name = f"{evento.clase_id.name} - {evento.tipo_evento}"
            else:
                evento.name = "Evento sin nombre"
            _logger.info(f"Computed event name: {evento.name}")


class Alumno(models.Model):
    _name = "gestion.colegio.alumno"
    _description = "Alumno del Colegio"

    name = fields.Char(string="Nombre", required=True)
    apellidos = fields.Char(string="Apellidos", required=True)
    dni = fields.Char(string="DNI/NIE", required=True, unique=True)
    fecha_nacimiento = fields.Date(string="Fecha de Nacimiento", required=True)
    edad = fields.Integer(string="Edad", compute="_compute_edad")
    clase_id = fields.Many2one("gestion.colegio.clase", string="Clase")
    evento_ids = fields.One2many(
        "gestion.colegio.evento", "alumno_id", string="Eventos Relacionados"
    )
    activo = fields.Boolean(String="Activo", default=True)

    @api.depends("fecha_nacimiento")
    def _compute_edad(self):
        for alumno in self:
            if alumno.fecha_nacimiento:
                today = fields.Date.today()
                alumno.edad = (
                    today.year
                    - alumno.fecha_nacimiento.year
                    - (
                        (today.month, today.day)
                        < (alumno.fecha_nacimiento.month, alumno.fecha_nacimiento.day)
                    )
                )
            else:
                alumno.edad = 0

    @api.constrains("dni")
    def _check_unique_dni(self):
        for alumno in self:
            existing_alumno = self.search(
                [("dni", "=", alumno.dni), ("id", "!=", alumno.id)]
            )
            if existing_alumno:
                raise ValidationErr("El DNI/NIE debe ser único para cada alumno.")


class Clase(models.Model):
    _name = "gestion.colegio.clase"
    _description = "Clase del Colegio"

    name = fields.Char(string="Curso", required=True)
    nivel = fields.Selection(
        [("1", "Nivel 1"), ("2", "Nivel 2")], string="Nivel", required=True
    )
    fecha_inicio = fields.Date(string="Fecha de Inicio", required=True)
    fecha_final = fields.Date(string="Fecha Final", required=True)
    tutor_id = fields.Many2one("hr.employee", string="Tutor")
    alumno_ids = fields.One2many(
        "gestion.colegio.alumno", "clase_id", string="Listado de Alumnos"
    )
    numero_alumnos = fields.Integer(
        string="Número de Alumnos", compute="_compute_numero_alumnos"
    )
    activo = fields.Boolean(string="Activo", default=True)

    @api.depends("alumno_ids")
    def _compute_numero_alumnos(self):
        for clase in self:
            clase.numero_alumnos = len(clase.alumno_ids)


class Profesor(models.Model):
    _inherit = "hr.employee"

    es_profesor = fields.Boolean(string="Es Profesor")
    clase_ids = fields.One2many(
        "gestion.colegio.clase", "tutor_id", string="Clases Asignadas"
    )


class Wizard(models.Model):
    _name = "gestion.colegio.wizard"
    _description = "Wizard para activar alumnos"

    alumno_ids = fields.Many2many("gestion.colegio.alumno", string="Alumnos")

    def activate_students(self):
        if self.alumno_ids:
            self.alumno_ids.write({"activo": True})
        return {"type": "ir.actions.act_window_close"}

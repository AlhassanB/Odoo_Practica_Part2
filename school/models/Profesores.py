from odoo import models, fields


class Profesor(models.Model):
    _inherit = "hr.employee"

    es_profesor = fields.Boolean(string="Es Profesor")
    clase_ids = fields.One2many(
        "gestion.colegio.clase", "tutor_id", string="Clases Asignadas"
    )

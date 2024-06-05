# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_teacher = fields.Boolean('Is a Teacher')
    subject_ids = fields.Many2many('mohsin.school.subject', string='Subjects')
    teacher_subject_line = fields.One2many('hr.employee.subjects.line', 'employee_id', 'Subjects')

    use_batch = fields.Boolean(compute='_compute_use_batch_from_company')

    use_section = fields.Boolean(compute='_compute_use_section_from_company')

    def _compute_use_section_from_company(self):
        for record in self:
            record.use_section = record.company_id.use_section

    def _compute_use_batch_from_company(self):
        for record in self:
            record.use_batch = record.company_id.use_batch




class SubjectLine(models.Model):
    _name = 'hr.employee.subjects.line'

    name = fields.Char()

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True,
                                  ondelete='cascade',
                                  index=True, copy=False
                                  )

    subject_id = fields.Many2one('mohsin.school.subject', string='Subject',
                                 required=True,
                                 domain="['|',('company_id','=',parent.company_id),('company_id','=',False)]"
                                 )

    domain_courses_for_subject = fields.Many2many(
        comodel_name='mohsin.school.course',
        string='Courses for Subject',
        compute='_compute_courses_from_subjects',
    )

    course_ids = fields.Many2many(
        comodel_name='mohsin.school.course',
        relation='employee_subject_course_rel',
        column1='subject_line_id',
        column2='course_id',
        string='Courses',
        domain="[('id','in',domain_courses_for_subject)]"
    )

    batch_ids = fields.Many2many(
        comodel_name='mohsin.school.course.batch',
        relation='course_batch_rel',
        column1='course_id',
        column2='batch_id',
        string="Batches",
        domain="[('course_id','in',course_ids)]"
    )

    section_ids = fields.Many2many(
        comodel_name='mohsin.school.course.section',
        relation='course_section_rel',
        column1='course_id',
        column2='section_id',
        string="Sections",
        domain="[('course_id','in',course_ids)]"
    )

    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('unique_employee_subject_active', 'UNIQUE(employee_id, subject_id, active)',
         'Subject already exists. Please ensure that the subject is not archived and activate it.!')
    ]



    @api.onchange('subject_id')
    @api.depends('subject_id', 'employee_id.company_id')
    def _compute_courses_from_subjects(self):
        for record in self:
            record.domain_courses_for_subject = False
            if record.subject_id and record.employee_id.company_id:
                courses = self.env['mohsin.school.course.subject.line'].search([
                    ('subject_id', '=', record.subject_id.id),
                    ('company_id', '=', self.employee_id.company_id.id),
                ]).mapped('course_id')
                record.domain_courses_for_subject = [(6, 0, courses.ids)]
            else:
                record.domain_courses_for_subject = False




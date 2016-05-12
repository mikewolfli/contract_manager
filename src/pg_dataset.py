#coding=utf-8
'''
Created on 2016年2月23日

@author: 10256603
'''
from peewee import *

pg_db = PostgresqlDatabase('pgworkflow',user='postgres',password='1q2w3e4r',host='10.127.144.62',)

class BaseModel(Model):
    class Meta:
        database=pg_db
        
class Employee(BaseModel):
    active = BooleanField(null=True)
    cost_center = CharField(null=True)
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    department = CharField(db_column='department_id', null=True)
    email = CharField(null=True)
    emp_desc = TextField(null=True)
    emp_pos = CharField(null=True)
    employee = CharField(db_column='employee_id', primary_key=True)
    instant = CharField(db_column='instant_id', null=True)
    mobile_phone = CharField(null=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)
    name = CharField()
    plant = CharField()
    sex = CharField(null=True)
    sub_phone = CharField(null=True)

    class Meta:
        db_table = 's_employee'

class EmployeeCardInfo(BaseModel):
    act_date = DateTimeField(null=True)
    card = CharField(db_column='card_id', null=True)
    employee = CharField(db_column='employee_id', null=True)
    id = BigIntegerField()
    is_active = BooleanField(null=True)
    remarks = TextField(null=True)

    class Meta:
        db_table = 's_employee_card_info'

class ProjectInfo(BaseModel):
    branch = CharField(db_column='branch_id', null=True)
    branch_name = CharField(null=True)
    contract = CharField(db_column='contract_id', null=True)
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)
    plant = CharField(null=True)
    project = CharField(db_column='project_id', primary_key=True)
    project_name = TextField()
    res_emp = CharField(db_column='res_emp_id', null=True)

    class Meta:
        db_table = 's_project_info'
        
class ContractBookHeader(BaseModel):
    contract_doc = CharField(db_column='contract_doc_id', primary_key=True)
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    item_no = IntegerField(null=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)
    project_catalog = IntegerField(null=True)
    project = ForeignKeyField(db_column='project_id', null=True, rel_model=ProjectInfo, to_field='project')
    status = IntegerField(null=True)

    class Meta:
        db_table = 's_contract_book_header'

class ContractBookInclude(BaseModel):
    contract_doc = CharField(db_column='contract_doc_id', null=True)
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    id = BigIntegerField()
    insert_batch = CharField(db_column='insert_batch_id', null=True)
    is_del = BooleanField(null=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)
    wbs_no = CharField(null=True)

    class Meta:
        db_table = 's_contract_book_include'

class ContractBrLog(BaseModel):
    b_date = DateTimeField(null=True)
    b_user = CharField(null=True)
    br_status = BooleanField(null=True)
    contract_doc = CharField(db_column='contract_doc_id', null=True)
    item = BigIntegerField(db_column='item_id', primary_key=True)
    s_user = CharField(null=True)
    r_date = DateTimeField(null=True)
    r_user = CharField(null=True)
    remarks = TextField(null=True)

    class Meta:
        db_table = 's_contract_br_log'

class BranchInfo(BaseModel):
    branch_abb = CharField(null=True)
    branch = CharField(db_column='branch_id', primary_key=True)
    branch_name_cn = CharField(null=True)
    branch_name_en = CharField(null=True)
    is_active = BooleanField(null=True)
    region = CharField(null=True)
    remarks = TextField(null=True)

    class Meta:
        db_table = 's_branch_info'

class ElevatorTypeDefine(BaseModel):
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    elevator_type = CharField()
    elevator_type_id = CharField(primary_key=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)

    class Meta:
        db_table = 's_elevator_type_define'
        
class UnitInfo(BaseModel):
    can_psn = BooleanField(null=True)
    cancel_times = IntegerField(null=True)
    conf_batch = CharField(db_column='conf_batch_id', null=True)
    conf_valid_end = DateField(null=True)
    create_date = DateTimeField(null=True)
    create_emp = CharField(db_column='create_emp_id', null=True)
    e_nstd = CharField(db_column='e_nstd_id', null=True)
    elevator = ForeignKeyField(db_column='elevator_id', null=True, rel_model=ElevatorTypeDefine, to_field='elevator_type_id')
    has_nonstd_inst_info = BooleanField(null=True)
    is_batch = BooleanField(null=True)
    is_urgent = BooleanField(null=True)
    lift_no = CharField(null=True)
    m_nstd = CharField(db_column='m_nstd_id', null=True)
    modify_date = DateTimeField(null=True)
    modify_emp = CharField(db_column='modify_emp_id', null=True)
    nonstd_level = IntegerField(null=True)
    project_catalog = IntegerField(null=True)
    project = CharField(db_column='project_id', null=True)
    req_configure_finish = DateTimeField(null=True)
    req_delivery_date = DateTimeField(null=True)
    restart_times = IntegerField(null=True)
    review_is_urgent = BooleanField(null=True)
    review_valid_end = DateField(null=True)
    status = IntegerField(null=True)
    unit_doc = CharField(db_column='unit_doc_id', null=True)
    version = IntegerField(db_column='version_id', null=True)
    wbs_no = CharField(primary_key=True)
    wf_status = CharField(null=True)

    class Meta:
        db_table = 's_unit_info'
        
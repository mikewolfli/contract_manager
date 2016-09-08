#coding=utf-8
'''
Created on 2016年2月23日

@author: 10256603
'''
from tkinter import *
from tkinter import ttk
#import threading
#from threading import Thread as thread
from tkinter import messagebox
from tkinter import scrolledtext
from pg_dataset import *
#from peewee import *
import time
import logging 
import datetime
from tkinter import simpledialog

s_note="Tab切换查询/借阅状态"    
class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        self.formatter = logging.Formatter('%(asctime)s-%(levelname)s : %(message)s')
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            s_end=self.text.index(END)
            s_start =  str(float(s_end)-1.0)            
            self.text.insert(END, msg+"\n")

            if '<-' in msg :
                self.text.tag_add("color1",s_start,s_end)
                self.text.tag_configure('color1', background='yellow')
            elif '->' in msg :
                self.text.tag_add('color2',s_start, s_end)               
                self.text.tag_configure('color2', background='cyan')
                
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)# Scroll to the bottom


class Application(Frame):
    i_key = 0
    i_key_valid = 0    
    br_state=True
    c_status=False
    id_input_status=False
    num_counter=30
    msg=""  
    s_user=""
    s_contract=""
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.num_counter =30
        self.createWidgets()
        
        self.run_counter()
        self.bind_all("<Key>", self.OnKeyboardEvent)
        self.bind_all("<Tab>", self.switch_func)
        self.bind_all("<F3>", self.getid)
        pg_db.connect()
        
    def reset_status(self):
        self.s_user=''
        self.barcode_id.set("")
        self.employee_info.set("")
        self.contract_info.set("")
        self.card_id.set("")
        self.s_contract=""
        self.c_status=False
        self.num_counter=30
        self.i_key=0;
        self.i_key_valid=0
        self.msg=""
        
    def run_counter(self):
        if self.br_state and self.c_status:
            self.num_counter-=1    
            if self.num_counter==0:
                self.reset_status()    
        
        if self.num_counter < 0:
            self.num_counter=0
            
        self.timer_label["text"]=str(self.num_counter)
        self.timer_label.after(1000, self.run_counter)
        
    def  getid(self, event):
        if not self.br_state:
            return
        
        self.id_input_status=True
        pid = simpledialog.askstring('员工编号','请输入8位ID')
        if pid is None or len(pid)==0:
            return

        try:
            card_id=EmployeeCardInfo.get((EmployeeCardInfo.employee==pid)&(EmployeeCardInfo.is_active==True)).card
            self.card_id.set(card_id)
        except EmployeeCardInfo.DoesNotExist:
            self.card_id.set('None')
            #messagebox.showwarning("提示", "数据库中没有阁下的ID card的记录，请通知管理员添加") 
                
        try:                
            employee_line= Employee.get(Employee.employee==pid)
            self.num_counter=30
            self.c_status=True
        except Employee.DoesNotExist:
            self.c_status=False
            self.card_id.set("")
            self.employee_info.set("")
            self.s_user=""
            messagebox.showerror("错误", "数据库中无阁下相关信息，请通知管理员增加人员信息")
            return
            
        self.id_input_status=False            
    
        self.s_user=employee_line.employee+"-"+employee_line.name
        self.employee_info.set(self.s_user)            
          
    def get_employee_info(self, card_id):
        try:            
            employee_id = EmployeeCardInfo.get((EmployeeCardInfo.card == card_id) & (EmployeeCardInfo.is_active==True))
        except EmployeeCardInfo.DoesNotExist:
            self.c_status=False
            self.card_id.set("")
            self.employee_info.set("")
            self.s_user=""
            messagebox.showerror("错误", "数据库中没有这张ID card的记录，请通知管理员添加")
            return
        
        try:                
            employee_line= Employee.get(Employee.employee==employee_id.employee)
            self.num_counter=30
            self.c_status=True
        except Employee.DoesNotExist:
            self.c_status=False
            self.card_id.set("")
            self.employee_info.set("")
            self.s_user=""
            messagebox.showerror("错误", "数据库中无阁下相关信息，请通知管理员增加人员信息")
            return
        
        self.s_user=employee_line.employee+"-"+employee_line.name
        self.employee_info.set(self.s_user)
            
    def get_project_info(self, cid):
        try:
            cid_line=ContractBookHeader.get((ContractBookHeader.contract_doc==cid)&(ContractBookHeader.status>=0))
        except ContractBookHeader.DoesNotExist:
            messagebox.showerror("错误","二维码解析错误，数据库无此记录(可能已经删除)")
            return 
        
        try:
            project_header=ProjectInfo.get(ProjectInfo.project==cid_line.project)
            self.num_counter=30
            self.c_status=True
        except ProjectInfo.DoesNotExist:
            self.barcode_id.set("")
            self.contract_info.set("")
            self.s_contract=""
            messagebox.showerror("错误","数据库内无此项目信息")
            return 
        
        self.s_contract = project_header.contract+"("+str(cid_line.item_no)+") "+project_header.project+"-"+project_header.project_name
        self.contract_info.set(self.s_contract)  
        
    def make_br_proc(self, cid): 
        self.num_counter=30
        self.c_status=True
        try:
            br_record = ContractBrLog.get((ContractBrLog.contract_doc==cid) & (ContractBrLog.br_status==True))
            time_delta=datetime.datetime.now()-br_record.b_date
            
            if time_delta < datetime.timedelta(minutes=10):
                if messagebox.askyesno("警告", "同一条记录借阅和归还的时间差为10分，请确认放弃此次归还操作？ \n(yes)放弃，(no)继续操作")==YES:
                    self.logger.info("由于本次归还操作在借阅后10分钟内操作，亲选择了放弃，故此合同系统记录仍在亲手上")
                    return
          
            q_borrow=ContractBrLog.update(r_user=self.s_user[:8],br_status=False, r_date=datetime.datetime.now()).where((ContractBrLog.contract_doc==cid)&(ContractBrLog.br_status==True))
            q_borrow.execute()
            q_borrow=ContractBookHeader.update(status=1).where((ContractBookHeader.contract_doc==cid)&(ContractBookHeader.status>=0))
            q_borrow.execute()
            self.logger.info("<-"+self.s_user+" 归还合同："+self.s_contract)
        except ContractBrLog.DoesNotExist:
            q_borrow=ContractBrLog.insert(contract_doc=cid, br_status=True, b_user=self.s_user[:8], b_date=datetime.datetime.now())
            q_borrow.execute() 
            q_borrow=ContractBookHeader.update(status=2).where((ContractBookHeader.contract_doc==cid)&(ContractBookHeader.status>=0))
            q_borrow.execute()
            self.logger.info("->"+self.s_user+"  借阅合同："+self.s_contract)
                   
    def OnKeyboardEvent(self,event):  
        self.i_key +=1 
        
        if event.keycode == 13 and self.br_state and not self.id_input_status:
            self.i_key=0
            self.i_key_valid=0
            if (self.msg.startswith("cid") or self.msg.startswith("CID")) and self.msg[3:].isdigit():
                if not self.card_id.get():
                    messagebox.showwarning("warning", "请先刷工作ID，标明身份")
                    self.reset_status()
                    return True
                         
                self.barcode_id.set(self.msg)
                self.get_project_info(self.msg) 
                self.make_br_proc(self.msg) 
            elif self.msg.isdigit():
                card = self.card_id.get()
                if self.msg == card:
                    self.reset_status()
                    return True
                
                self.card_id.set(self.msg) 
                print(self.msg[-10:]) 
                self.get_employee_info(self.msg[-10:])
            
            self.msg=''
            self.i_key=0
            self.i_key_valid=0
        elif ((event.keycode>=48 and event.keycode<=57) or (event.keycode>=65 and event.keycode<=90)) and self.br_state and not self.id_input_status:
            self.i_key_valid += 1
            if self.i_key == self.i_key_valid:
                self.msg=self.msg+event.keysym 
        else:
            self.msg=''  
            self.i_key=0
            self.i_key_valid=0       
            
        return True
       
    def quit_func(self):
        if pg_db.get_conn():
            pg_db.close() 
            
    def switch_func(self, event):
        if self.br_state:
            self.br_state=False
            self.search_string.set("")
            self.num_counter=30
            self.reset_status()
            self.note_label["text"]=s_note+"：查询状态"
            self.search_entry["state"]="normal"
            #self.with_history["state"]="active"
            self.search_entry.focus()
            #win32api.PostQuitMessage()
        else:
            self.br_state=True
            self.note_label["text"]=s_note+"：借阅状态"
            self.search_entry["state"]="readonly"
            self.search_string.set("")
            #self.with_history["state"]="diable"
            #win32api.PostMessage()
            #self.search_entry.focus_set(None)
            
        self.i_key=0;
        self.i_key_valid=0;
        self.msg=''
       
    def search_result(self,event):
        for row in self.contract_br_list.get_children():
            self.contract_br_list.delete(row)
            
        s_case = self.search_string.get()
        
        if not s_case:
            self.logger.warning("搜索字段不能为空")
            return
        

        result_list = ProjectInfo.select(ProjectInfo, ContractBookHeader).join(ContractBookHeader,on=(ProjectInfo.project==ContractBookHeader.project))\
                                          .where((ProjectInfo.project.contains(s_case) | ProjectInfo.contract.contains(s_case))&\
                                                 (ContractBookHeader.status>=0))\
                                          .order_by(ProjectInfo.project.asc(), ContractBookHeader.item_no.asc()).naive()
                                          
        #print(result_list.sql())
        
        if not result_list:
            return
        
        i=0
        for r in result_list:     
            i+=1
            row=[str(i),r.contract_doc,r.contract,r.item_no,r.project_name,r.project,'','','','','','']
            if r.status==0 or r.status==1:
                row[6]="在架"
                row[7]="资料室"
            elif r.status==2:
                row[6]= "借出"
            elif r.status==3:
                row[6]= "归档"
                row[7]= "档案袋"
            
            if r.status !=2 :
                parent_node=self.contract_br_list.insert('', i-1, values=row)
            else:
                b=ContractBrLog.get((ContractBrLog.contract_doc==r.contract_doc)&(ContractBrLog.br_status==True))
                if not b.s_user:
                    row[7]="资料室"
                else:
                    row[7]=Employee.get(Employee.employee==b.s_user).name              
                row[8]=Employee.get(Employee.employee==b.b_user).name
                row[9]=b.b_date.strftime("%Y-%m-%d %H:%M:%S")
                
                parent_node=self.contract_br_list.insert('',i-1,values=row)
                
                his = self.with_history.get()
                
                if his == 1:
                    c_list = ContractBrLog.select().where((ContractBrLog.contract_doc==r.contract_doc)&(ContractBrLog.br_status==False)).order_by(ContractBrLog.item.desc()).limit(10)
                    j=0
                    row1=['', '',r.contract,r.item_no,r.project_name,r.project,'','','','','','']   
                    for l in c_list: 
                        j+=1 
                        row1[1]=str(j)
                        if not l.s_user:
                            row1[7]="资料室"
                        else:
                            row1[7]=Employee.get(Employee.employee==l.s_user).name               
                        row1[8]=Employee.get(Employee.employee==l.b_user).name
                        row1[9]=l.b_date.strftime("%Y-%m-%d %H:%M:%S")
                        row1[10]=Employee.get(Employee.employee==l.r_user).name
                        row1[11]=l.r_date.strftime("%Y-%m-%d %H:%M:%S")
                        self.contract_br_list.insert(parent_node,j-1,values=row1)
    
    def display_his(self):
        if self.br_state:
            return
        
        if not self.search_string:
            return
            
        his = self.with_history.get()

        if his==1:
            for row in self.contract_br_list.get_children():
                row_head=self.contract_br_list.item(row, 'values')
                row1=['', '',row_head[2],row_head[3],row_head[4],row_head[5],'','','','','','']
                c_list = ContractBrLog.select().where((ContractBrLog.contract_doc==row_head[1])&(ContractBrLog.br_status==False)).order_by(ContractBrLog.item.desc()).limit(10)
                j=0 
                for l in c_list: 
                    j+=1 
                    row1[1]=str(j)
                    if not l.s_user:
                        row1[7]="资料室"
                    else:
                        row1[7]=Employee.get(Employee.employee==l.s_user).name               
                    row1[8]=Employee.get(Employee.employee==l.b_user).name
                    row1[9]=l.b_date.strftime("%Y-%m-%d %H:%M:%S")
                    row1[10]=Employee.get(Employee.employee==l.r_user).name
                    row1[11]=l.r_date.strftime("%Y-%m-%d %H:%M:%S")
                    self.contract_br_list.insert(row,j-1,values=row1)                                      
        elif his==0:
            for row in self.contract_br_list.get_children():
                for sub_row in self.contract_br_list.get_children(row):
                    self.contract_br_list.delete(sub_row)            
                
    def createWidgets(self):
        self.search_label=Label(self)
        self.search_label["text"]="查询"
        self.search_label.grid(row=0,column=0, sticky=W)

        self.search_string=StringVar()
        self.search_entry = Entry(self, width=30, textvariable=self.search_string)
        self.search_entry.grid(row=0, column=1, sticky=W)
        self.search_entry["state"]="readonly"
        self.search_entry.bind("<Return>", self.search_result)
        
        self.note_label = Label(self, width=60)
        self.note_label["text"]=s_note+"：借阅状态"
        self.note_label.config(font=('times', 10, 'bold'))
        self.note_label.grid(row=0, column=2, columnspan=2,sticky=W)
        
        self.with_history=IntVar()
        self.check_history=Checkbutton(self,variable=self.with_history, command=self.display_his)
        self.check_history["text"]="显示借阅历史"
        self.check_history.grid(row=0, column=4, sticky=W)
        #self.check_history["state"]="disable"
        self.with_history.set(0)
        
        self.timer_label = Label(self)
        self.timer_label.config(bg='yellow')
        self.timer_label.config(font=('times', 20, 'bold'))
        self.timer_label.config(fg='black')
        self.timer_label.config(width=10)
        self.timer_label.grid(row=0, column=5, rowspan=2, sticky=NSEW)
        self.timer_label["text"]=str(self.num_counter)
        
        self.cardid_label=Label(self)
        self.cardid_label["text"]="vCard"
        self.cardid_label.grid(row=1, column=0, sticky=W)  
        
        self.card_id=StringVar()   
        self.cardid_entry=Entry(self,width=30,textvariable=self.card_id)
        self.cardid_entry.grid(row=1, column=1, sticky=W)
        self.cardid_entry["state"]="readonly"
        
        self.employee_info=StringVar()
        self.employee_entry=Entry(self,width=60, textvariable=self.employee_info)
        self.employee_entry.grid(row=1, column=2, columnspan=2, sticky=EW)
        self.employee_entry["state"]="readonly"
        
        self.barcode_label=Label(self)
        self.barcode_label["text"]="2d-code编号"
        self.barcode_label.grid(row=2, column=0, sticky=W)
         
        self.barcode_id=StringVar()                     
        self.barcode_entry=Entry(self, width=30, textvariable=self.barcode_id)
        self.barcode_entry.grid(row=2, column=1, sticky=W)
        self.barcode_entry["state"]="readonly"
        
        self.contract_info=StringVar()
        self.contract_entry=Entry(self, textvariable=self.contract_info)
        self.contract_entry.grid(row=2, column=2, columnspan=3, sticky=NSEW)
        self.contract_entry["state"]="readonly"  
                      
        self.contract_br_list=ttk.Treeview(self,columns=('col0','col1','col2','col3','col4','col5','col6',
                                                                         'col7','col8','col9','col10','col11'))
        self.contract_br_list.heading("#0", text='树形')        
        self.contract_br_list.heading('col0',text='')
        self.contract_br_list.heading('col1', text='2D-Code')
        self.contract_br_list.heading('col2', text='合同号')
        self.contract_br_list.heading('col3', text='文本序号')
        self.contract_br_list.heading('col4', text='项目名称')
        self.contract_br_list.heading('col5', text='项目号')
        self.contract_br_list.heading('col6', text='状态')
        self.contract_br_list.heading('col7', text='出借人')
        self.contract_br_list.heading('col8', text='借阅')
        self.contract_br_list.heading('col9', text='借阅时间')
        self.contract_br_list.heading('col10', text='归还')
        self.contract_br_list.heading('col11', text='归还时间')
        self.contract_br_list.column("#0", width=20,anchor="w")
        self.contract_br_list.column('col0', width=20,anchor='w')
        self.contract_br_list.column('col1', width=50, anchor='sw')
        self.contract_br_list.column('col2', width=50, anchor='sw')
        self.contract_br_list.column('col3', width=50, anchor='sw')
        self.contract_br_list.column('col4', width=200, anchor='sw')
        self.contract_br_list.column('col5', width=50, anchor='sw')
        self.contract_br_list.column('col6', width=50, anchor='sw')
        self.contract_br_list.column('col7', width=80, anchor='sw')
        self.contract_br_list.column('col8', width=50, anchor='sw')
        self.contract_br_list.column('col9', width=80, anchor='sw')
        self.contract_br_list.column('col10', width=100, anchor='sw')
        self.contract_br_list.column('col11', width=100, anchor='sw')
        self.contract_br_list.grid(row=4, column=0, rowspan=6,columnspan=6,sticky=NSEW) 
        
        self.y_br_scroll=ttk.Scrollbar(self,orient=VERTICAL,command=self.contract_br_list.yview)
        self.contract_br_list.configure(yscrollcommand=self.y_br_scroll.set)
        self.y_br_scroll.grid(row=4,column=6,rowspan=6,sticky=NSEW)
        self.x_br_scroll=ttk.Scrollbar(self,orient=HORIZONTAL,command=self.contract_br_list.xview)
        self.contract_br_list.configure(xscrollcommand=self.x_br_scroll.set)
        self.x_br_scroll.grid(row=10,column=0, columnspan=6,sticky=NSEW) 
        
        
        self.log_text=scrolledtext.ScrolledText(self, state='disabled')
        self.log_text.config(font=('TkFixedFont', 10, 'normal'))
        self.log_text.grid(row=11, column=0, columnspan=6,sticky=NSEW)
        # Create textLogger
        text_handler = TextHandler(self.log_text)        
        # Add the handler to logger
        self.logger = logging.getLogger()
        self.logger.addHandler(text_handler)
        self.logger.setLevel(logging.INFO)
        
        #self.columnconfigure(1,weight=1)
            
if __name__ == '__main__':
    root=Tk()
    root.resizable(0, 0)
    #root.wm_state('zoomed')
    Application(root) 
    root.title("资料室合同借阅管理")
    root.geometry('1100x650')  #设置了主窗口的初始大小960x540  
    root.mainloop() 
    #root.destroy()
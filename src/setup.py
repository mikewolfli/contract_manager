# -*- coding: utf-8 -*-
'''
Created on 2015年8月25日

@author: 10256603
'''
from distutils.core import setup
import py2exe

setup( description="资料室合同借阅管理系统",
       windows=[  {
                        "script":"main.py",
                        "icon_resources": [(1, "cmico.ico")]
                }])
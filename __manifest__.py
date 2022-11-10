# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Sitaram
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'Accounting Report By City',
    'category': 'account',
    'version': '0.1',
    'summary': 'This module provides Accounting Report By City.',
    'description': '''This module provides Accounting Report By City.'''
                   ,
    'depends': ['base', 'account', 'vit_kelurahan'],
    'data': [
        'views/account_view.xml',
        'report/city_report.xml',
        'report/city_temp.xml'
    ],
    'images': ['static/description/banner.png'],
    'auto_install': False,
    'installable': True,
    'application': False,
}

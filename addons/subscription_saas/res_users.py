# -*- coding: utf-8 -*-
##############################################################################
#
#    TeckZilla Software Solutions and Services
#    Copyright (C) 2012-2013 TeckZilla-OpenERP Experts(<http://www.teckzilla.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class res_users(osv.osv):
    _inherit = 'res.users'
    
    def create(self, cr, uid, vals, context=None):
        print "========in create666666666666666666=====>"
        para = self.pool.get("ir.config_parameter")
        cr.execute("select count(id) from res_users")
        user_query = cr.fetchall()
        user_cnt = user_query[0][0]
        user_count = para.get_param(cr, uid, "ecommerce.no_of_users", context=context)
        if int(user_count) != 0 and int(user_count) <= user_cnt:
            raise osv.except_osv(('Error!'), ('You have only access to create '+user_count+' users'))
        return super(res_users, self).create(cr, uid, vals, context)
res_users()
# -*- coding: utf-8 -*-
# from odoo import http


# class HinoOnnet(http.Controller):
#     @http.route('/hino_onnet/hino_onnet', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hino_onnet/hino_onnet/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hino_onnet.listing', {
#             'root': '/hino_onnet/hino_onnet',
#             'objects': http.request.env['hino_onnet.hino_onnet'].search([]),
#         })

#     @http.route('/hino_onnet/hino_onnet/objects/<model("hino_onnet.hino_onnet"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hino_onnet.object', {
#             'object': obj
#         })


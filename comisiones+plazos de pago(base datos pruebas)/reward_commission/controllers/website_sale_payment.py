from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from geopy import distance


R = 5  # radius in km


class WebsiteSalePayment(WebsiteSale):
    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        res = super().payment()
        order = request.website.sale_get_order()
        partner_id = order.partner_shipping_id
        partner_id.geo_localize()
        hairdressers = self._get_haidressers(partner_id)
        #precio_pedido = self._get_precioPedido(order)
        plazos_pago = []

        #----- calculo del merchan y lo mandamos a la vista sin tener en cuenta el envío web ---#
        total_pedido = 0
        for envio in order.order_line:
            if not envio.product_id.name == 'Envío':
                total_pedido += envio.price_total


        #plazos de pago disponibles (prueba --> incompleto)#
        usuario_pedidos = order.partner_id.name
        ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)]) #ficha de usuario con nombre igual al del pedido. 
        #Calculo del plazo de pago según cantidad de pedido#

        if total_pedido >0 and total_pedido <= 1000:
            plazo_1 = request.env['account.payment.term'].sudo().search([('id', '=', 4)])
            plazos_pago.append({'plazo': plazo_1})

        elif total_pedido >1000 and total_pedido <= 2000:
            plazo_1 = request.env['account.payment.term'].sudo().search([('id', '=', 24)])
            plazos_pago.append({'plazo': plazo_1})

        elif total_pedido >2000 :
            plazo_1 = request.env['account.payment.term'].sudo().search([('id', '=', 9)])
            plazos_pago.append({'plazo': plazo_1})



        #if ficha_usuarios.property_supplier_payment_term_id:
        plazo_2 = request.env['account.payment.term'].sudo().search([('id', '=', ficha_usuarios.property_supplier_payment_term_id.id)])
        plazos_pago.append({'plazo': plazo_2})

        plazo3 = request.env['account.payment.term'].sudo().search([('id', '=', 1)])
        plazos_pago.append({'plazo': plazo3})

        #fin plazos de pago dispnible



        merchan = round((total_pedido * 3) / 100, 2)
        res.qcontext.update({'hairdressers': hairdressers, 'merchan' : merchan, 'pagos': plazos_pago})
        return res


    def _get_haidressers(self, partner_id):
        hairdressers_ids = request.env['res.partner'].sudo().search([('partner_type', '=', 'hairdresser')])

        current_partner = (partner_id.partner_latitude, partner_id.partner_longitude)
        hairdressers = []
        for hairdresser in hairdressers_ids:
            try:
                dist = distance.distance(current_partner, (hairdresser.partner_latitude, hairdresser.partner_longitude)).km
                if (dist < R):
                    hairdressers.append({'hairdresser': hairdresser, 'dist': dist})
            except ValueError:
                pass
        if hairdressers:
            hairdressers = sorted(hairdressers, key=lambda k: k['dist'])
        return hairdressers

    @http.route(['/shop/payment/transaction/', '/shop/payment/transaction/<int:so_id>', '/shop/payment/transaction/<int:so_id>/<string:access_token>'],
                type='json', auth="public", website=True)
    
    

    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        res = super().payment_transaction(acquirer_id, save_token, so_id, access_token, token, **kwargs)

        #Si el cliente no elige ninguna opción y el sitio web es Easytech#

        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)

        else:

            textarea_total = 'MERCHAN:'


            order = request.website.sale_get_order()

            usuario_pedidos = order.partner_id.name
            ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)]) #ficha de usuario con nombre igual al del pedido. 
            ficha_usuarios.x_puntosRestantes = 0

             #obtenemos los plazos de pago del usuario siempre que no haya elegido pronto pago y que existan en su ficha dichos plazos.
            if  not kwargs.get('merchan') and order.website_id.name == 'Easy Tech Cosmetics':
                
                order.payment_term_id = int(kwargs.get('plazo_pago'))

                total_pedido = 0
                for envio in order.order_line:
                    if not envio.product_id.name == 'Envío': 
                        total_pedido += envio.price_total

                #total_pedido = order.amount_total
                merchan = round((total_pedido * 3) / 100, 2)
                textarea_total += str(merchan) + '€\n'  + '\n'

                order.note = textarea_total
            
            elif order.website_id.name == 'Easy Tech Cosmetics' and kwargs.get('merchan'):

                #prueba elección plazos de pago #
                #order.payment_term_id = ficha_usuarios.property_supplier_payment_term_id
                order.payment_term_id = int(kwargs.get('plazo_pago'))

                total_pedido = 0
                for envio in order.order_line:
                    if not envio.product_id.name == 'Envío': 
                        total_pedido += envio.price_total

                #total_pedido = order.amount_total
                merchan = round((total_pedido * 3) / 100, 2)
                textarea_total += str(merchan) + '€\n'  + kwargs.get('merchan') +  '\n'

                order.note = textarea_total
           

        return res



    @http.route(['/shop/devolucion'], type='http', auth="public", website=True, sitemap=False)
    def devoluciones(self, devolucion, **post):
        redirect = post.get('r', '/shop/cart')
        order = request.website.sale_get_order()

        usuario_pedidos = order.partner_id.name
        ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)])
        puntos_usuario = int(ficha_usuarios.x_puntos)
        puntos_a_devolver = int(ficha_usuarios.x_puntosRestantes)

        ficha_usuarios.x_puntos = ficha_usuarios.x_puntos + puntos_a_devolver

        for punto in order.order_line:
                if punto.product_id.name == 'Dto puntos': #sumar los puntos perdidos al eliminar el descuento.
                    punto.unlink()
                    ficha_usuarios.x_puntosRestantes = 0


        request.website.sale_get_order(code=devolucion)
        return request.redirect('/shop/cart')




        #Boton de canjear puntos#
    @http.route(['/shop/puntos'], type='http', auth="public", website=True, sitemap=False)
    def puntos(self, puntos, **post):
        redirect = post.get('r', '/shop/cart')
        order = request.website.sale_get_order()

        puntos_usados = int(puntos)
        usuario_pedidos = order.partner_id.name
        ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)])
        puntos_usuario = int(ficha_usuarios.x_puntos) #puntos totales del usuario



        if int(puntos) < puntos_usuario and ficha_usuarios.x_puntosRestantes == 0:
       
            ficha_usuarios.x_puntosRestantes = puntos_usados #almacena los puntos utilizados
            puntos_restantes =  puntos_usuario - puntos_usados #puntos restantes del usuario tras utililzarlos.

            for punto in order.order_line:
                if punto.product_id.name == 'Dto puntos': #sumar los puntos perdidos al eliminar el descuento.
                    punto.unlink()
                    ficha_usuarios.x_puntos = ficha_usuarios.x_puntos + ficha_usuarios.x_puntosRestantes

            

            order.write({

                'order_line': [
                (0,0, {
                'order_id': order.id,
                'product_id': 3589,
                'price_unit':   0, #Descuento calculado#
                'product_uom_qty': 1,
                'is_reward_line': False,
                
                })
                ]
                })

            ficha_usuarios.x_puntos = ficha_usuarios.x_puntos - puntos_usados
            #ficha_usuarios.x_puntosRestantes = 0

        elif int(puntos) > puntos_usados:
            #revisar los mensajes de error---destapan todos los formularios#
            return request.redirect("%s?error_puntos=1" % redirect)


        else:
             #revisar los mensajes de error---destapan todos los formularios#
            return request.redirect("%s?error_puntos=1" % redirect)


        # empty promo code is used to reset/remove pricelist (see `sale_get_order()`)
        #if promo:
            #pricelist = request.env['product.pricelist'].sudo().search([('code', '=', promo)], limit=1)
            #if (not pricelist or (pricelist and not request.website.is_pricelist_available(pricelist.id))):
                #return request.redirect("%s?code_not_available=1" % redirect)

        request.website.sale_get_order(code=puntos)
        return request.redirect(redirect)




 #Controlador que se ejecuta al cambiar la cantidad de un producto en el carrito #
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)

    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        
        #Código sacado del codigo principal
        order = request.website.sale_get_order(force_create=1) #obtenemos la orden de venta actual
        descuento = False
        
        #Código sacado del codigo principal
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        #Codigo sacado del código principal
        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        usuario_pedidos = order.partner_id.name
        ficha_usuarios = request.env['res.partner'].sudo().search([('name', '=', usuario_pedidos)])
        puntos_usuario = int(ficha_usuarios.x_puntos) #puntos totales del usuario

        for lineas in order.order_line:
            if lineas.product_id.name == 'Dto puntos':
                lineas.unlink()
                descuento = True

        if descuento == True :
            order.write({

                'order_line': [
                (0,0, {
                'order_id': order.id,
                'product_id': 3589,
                'price_unit':   0, #descuento calculado#
                'product_uom_qty': 1,
                'is_reward_line': False,
                
                })
                ]
                })
        elif descuento == False :
            if ficha_usuarios.x_puntosRestantes > 0:
                ficha_usuarios.x_puntos = ficha_usuarios.x_puntos + ficha_usuarios.x_puntosRestantes
                ficha_usuarios.x_puntosRestantes = 0
            return request.redirect('/shop/cart')

         #Código sacado del codigo principal#
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value

        value['website_sale.cart_lines'] = request.env['ir.ui.view'].render_template("website_sale.cart_lines", {
        'website_sale_order': order,
        'date': fields.Date.today(),
        'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view'].render_template("website_sale.short_cart_summary", {
        'website_sale_order': order,
        })


        return value

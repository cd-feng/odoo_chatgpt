# -*- coding: utf-8 -*-
import openai
from odoo import models, _
from odoo.exceptions import UserError


class Channel(models.Model):
    _inherit = 'mail.channel'

    def get_chatgpt_param(self):
        chatgpt_mail_channel = self.env.ref('odoo_chatgpt_bot.chatgpt_mail_channel')
        chatgpt_user = self.env.ref("odoo_chatgpt_bot.chatgpt_user")
        chatgpt_partner = self.env.ref("odoo_chatgpt_bot.chatgpt_res_partner")
        return chatgpt_mail_channel, chatgpt_user, chatgpt_partner

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        """
        拓展线程
        """
        result = super()._notify_thread(message, msg_vals=msg_vals, **kwargs)
        if not msg_vals or not msg_vals.get('body'):
            return result
        chatgpt_channel, chatgpt_user, chatgpt_partner = self.get_chatgpt_param()
        author_id, msg_body = msg_vals.get('author_id'), msg_vals.get('body')
        openai.api_key = self.env['ir.config_parameter'].sudo().get_param('odoo_chatgpt_bot.openapi_api_key')
        partner_name = ''
        if author_id:
            partner_id = self.env['res.partner'].browse(author_id)
            if partner_id:
                partner_name = partner_id.name
        chatgpt_name = str(chatgpt_partner.name or '') + ', '
        if author_id != chatgpt_partner.id and chatgpt_name in msg_vals.get('record_name', '') \
                or 'ChatGPT,' in msg_vals.get('record_name', '') and self.channel_type == 'chat':
            try:
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=msg_body,
                    temperature=0.1,
                    max_tokens=3000,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    user=partner_name,
                )
                res = response['choices'][0]['text']
                self.with_user(chatgpt_user).message_post(body=res, message_type='comment', subtype_xmlid='mail.mt_comment')
            except Exception as e:
                raise UserError(_(e))
        elif author_id != chatgpt_partner.id and msg_vals.get('model', '') == 'mail.channel' \
                and msg_vals.get('res_id', 0) == chatgpt_channel.id:
            try:
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=msg_body,
                    temperature=0.2,
                    max_tokens=3000,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                    user=partner_name,
                )
                res = response['choices'][0]['text']
                chatgpt_channel.with_user(chatgpt_user).message_post(body=res, message_type='comment', subtype_xmlid='mail.mt_comment')
            except Exception as e:
                raise UserError(_(e))
        return result

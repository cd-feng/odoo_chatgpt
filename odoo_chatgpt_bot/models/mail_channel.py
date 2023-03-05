# -*- coding: utf-8 -*-
import openai
from odoo import models, _
from odoo.exceptions import UserError

CHATGPT_CHANNEL_MESSAGE = []    # 保存频道对话的记录
CHATGPT_PARTNER_MESSAGE = {}   # 保存个人用户的记录


class Channel(models.Model):
    _inherit = 'mail.channel'

    def get_chatgpt_param(self):
        chatgpt_mail_channel = self.env.ref('odoo_chatgpt_bot.chatgpt_mail_channel')
        chatgpt_user = self.env.ref("odoo_chatgpt_bot.chatgpt_user")
        chatgpt_partner = self.env.ref("odoo_chatgpt_bot.chatgpt_res_partner")
        return chatgpt_mail_channel, chatgpt_user, chatgpt_partner

    def send_chatgpt_message(self, messages):
        """
        发送消息
        """
        openai.api_key = self.env['ir.config_parameter'].sudo().get_param('odoo_chatgpt_bot.openapi_api_key')
        chat = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
        )
        result = chat.choices[0].message.content
        return result

    def _notify_thread(self, message, msg_vals=False, **kwargs):
        """
        拓展线程
        """
        global CHATGPT_CHANNEL_MESSAGE, CHATGPT_PARTNER_MESSAGE
        result = super()._notify_thread(message, msg_vals=msg_vals, **kwargs)
        config_parameter = self.env['ir.config_parameter'].sudo()
        if not msg_vals or not msg_vals.get('body'):
            return result
        chatgpt_channel, chatgpt_user, chatgpt_partner = self.get_chatgpt_param()
        author_id, msg_body = msg_vals.get('author_id'), msg_vals.get('body')
        partner_name = ''
        if author_id:
            partner_id = self.env['res.partner'].browse(author_id)
            if partner_id:
                partner_name = partner_id.name
        limit_channel_count = int(config_parameter.get_param('odoo_chatgpt_bot.limit_channel_count'))
        if author_id != chatgpt_partner.id and chatgpt_partner.name in msg_vals.get('record_name', '') and self.channel_type == 'chat':
            if not CHATGPT_PARTNER_MESSAGE.get(partner_name):
                CHATGPT_PARTNER_MESSAGE.update({partner_name: [{"role": "system", "content": "个人AI小助手"}]})
            partner_messages = CHATGPT_PARTNER_MESSAGE[partner_name]
            # 对话次数不超过x次。超过就清空内容重新创建对话
            if msg_body in ['刷新对话', '清除对话'] or len(partner_messages) >= limit_channel_count:
                CHATGPT_PARTNER_MESSAGE.update({partner_name: [{
                    "role": "system", "content": config_parameter.get_param('odoo_chatgpt_bot.openapi_chatgpt_role')
                }]})
                body = "------- 已自动刷新对话内容，请重新提问。（或者手动输入'刷新对话/清除对话'进行刷新。）--------"
                self.with_user(chatgpt_user).message_post(body=body, message_type='comment', subtype_xmlid='mail.mt_comment')
            else:
                partner_messages.append({"role": "user", "content": msg_body})
                try:
                    reply = self.send_chatgpt_message(partner_messages)
                    self.with_user(chatgpt_user).message_post(body=reply, message_type='comment', subtype_xmlid='mail.mt_comment')
                    partner_messages.append({"role": "assistant", "content": reply})
                    CHATGPT_PARTNER_MESSAGE.update({partner_name: partner_messages})
                except Exception as e:
                    raise UserError(_(e))
        elif author_id != chatgpt_partner.id and msg_vals.get('model', '') == 'mail.channel' and msg_vals.get('res_id', 0) == chatgpt_channel.id:
            # 频道对话次数每次的次数不超过x次。超过就清空内容重新创建对话
            if msg_body in ['刷新对话', '清除对话'] or len(CHATGPT_CHANNEL_MESSAGE) >= limit_channel_count:
                CHATGPT_CHANNEL_MESSAGE = [{"role": "system", "content": config_parameter.get_param('odoo_chatgpt_bot.openapi_chatgpt_role')}]
                body = "------------- 已自动刷新对话内容，请重新提问。（或者手动输入'刷新对话'进行刷新。）----------------------"
                chatgpt_channel.with_user(chatgpt_user).message_post(body=body, message_type='comment', subtype_xmlid='mail.mt_comment')
            else:
                CHATGPT_CHANNEL_MESSAGE.append({"role": "user", "content": msg_body})
                try:
                    reply = self.send_chatgpt_message(CHATGPT_CHANNEL_MESSAGE)
                    chatgpt_channel.with_user(chatgpt_user).message_post(body=reply, message_type='comment', subtype_xmlid='mail.mt_comment')
                    CHATGPT_CHANNEL_MESSAGE.append({"role": "assistant", "content": reply})
                except Exception as e:
                    raise UserError(_(e))
        return result

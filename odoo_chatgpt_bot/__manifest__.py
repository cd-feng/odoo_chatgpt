# -*- coding: utf-8 -*-
{
    'name': 'Odoo集成ChatGPT',
    'version': '15.0.1',
    'license': 'AGPL-3',
    'summary': '在odoo中继承chatGPT，实现通过频道与chatgpt进行对话。',
    'description': '利用GPT语言模型的功能生成类似人类的响应，提供更自然和直观的用户体验。',
    'author': 'XueFeng.Su',
    'website': "http://www.cdooc.com",
    'category': 'chatGPT',
    'version': '15.0.1',
    "license": "AGPL-3",
    'depends': ['base', 'mail'],
    'external_dependencies': {'python': ['openai']},
    'installable': True,
    'application': False,
    'auto_install': False,

    'data': [
        'datas/mail_channel.xml',
        'datas/user_partner.xml',

        'views/res_config_settings_views.xml',
    ]
}

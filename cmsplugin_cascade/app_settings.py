# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class AppSettings(object):

    def _setting(self, name, default=None):
        from django.conf import settings
        return getattr(settings, name, default)

    @property
    def CASCADE_PLUGINS(self):
        return self._setting('CMSPLUGIN_CASCADE_PLUGINS', (
            'cmsplugin_cascade.generic',
            'cmsplugin_cascade.icon',
            'cmsplugin_cascade.link',
        ))

    @property
    def CMSPLUGIN_CASCADE(self):
        import os
        from collections import OrderedDict
        from importlib import import_module
        from django.core.exceptions import ImproperlyConfigured
        from django.utils.translation import ugettext_lazy
        from cmsplugin_cascade.widgets import (NumberInputWidget, MultipleCascadingSizeWidget, ColorPickerWidget,
                                               SelectTextAlignWidget, SelectOverflowWidget)

        if hasattr(self, '_config_CMSPLUGIN_CASCADE'):
            return self._config_CMSPLUGIN_CASCADE

        INSTALLED_APPS = self._setting('INSTALLED_APPS')
        config = self._setting('CMSPLUGIN_CASCADE', {})
        config.setdefault('alien_plugins', ['TextPlugin'])
        config.setdefault('plugin_prefix', None)

        config.setdefault('plugins_with_extra_fields', {})
        if 'cmsplugin_cascade.extra_fields' in INSTALLED_APPS:
            from cmsplugin_cascade.extra_fields.config import PluginExtraFieldsConfig

            plugins_with_extra_fields = config['plugins_with_extra_fields']
            plugins_with_extra_fields.setdefault('SimpleWrapperPlugin', PluginExtraFieldsConfig())
            plugins_with_extra_fields.setdefault('HeadingPlugin', PluginExtraFieldsConfig(
                inline_styles={
                    'extra_fields:Margins': ['margin-top', 'margin-right', 'margin-bottom', 'margin-left'],
                    'extra_units:Margins': 'px,em'
                },
                allow_override=False
            ))
            plugins_with_extra_fields.setdefault('HorizontalRulePlugin', PluginExtraFieldsConfig(
                inline_styles={
                    'extra_fields:Paddings': ['margin-top', 'margin-bottom'],
                    'extra_units:Paddings': 'px,em'
                },
                allow_override=False
            ))
            for plugin, plugin_config in plugins_with_extra_fields.items():
                if not isinstance(plugin_config, PluginExtraFieldsConfig):
                    msg = "CMSPLUGIN_CASCADE['plugins_with_extra_fields']['{}'] must instantiate a class of type PluginExtraFieldsConfig"
                    raise ImproperlyConfigured(msg.format(plugin))

        config.setdefault('plugins_with_sharables', {})
        if 'cmsplugin_cascade.sharable' in INSTALLED_APPS:
            config['plugins_with_sharables'].setdefault(
                'FramedIconPlugin',
                ('font_size', 'color', 'background_color', 'text_align', 'border', 'border_radius',))

        config['exclude_hiding_plugin'] = list(config.get('exclude_hiding_plugin', []))
        config['exclude_hiding_plugin'].append('SegmentPlugin')

        config.setdefault('link_plugin_classes', (
            'cmsplugin_cascade.link.plugin_base.DefaultLinkPluginBase',
            'cmsplugin_cascade.link.plugin_base.LinkElementMixin',
            'cmsplugin_cascade.link.forms.LinkForm',))

        config['plugins_with_bookmark'] = list(config.get('plugins_with_bookmark', []))
        config['plugins_with_bookmark'].extend(['SimpleWrapperPlugin', 'HeadingPlugin'])
        config.setdefault('bookmark_prefix', '')

        config.setdefault('extra_inline_styles', OrderedDict())
        extra_inline_styles = config['extra_inline_styles']
        extra_inline_styles.setdefault(
            'Margins',
            (['margin-top', 'margin-right', 'margin-bottom', 'margin-left'], MultipleCascadingSizeWidget))
        extra_inline_styles.setdefault(
            'Paddings',
            (['padding-top', 'padding-right', 'padding-bottom', 'padding-left'], MultipleCascadingSizeWidget))
        extra_inline_styles.setdefault(
            'Widths',
            (['min-width', 'width', 'max-width'], MultipleCascadingSizeWidget))
        extra_inline_styles.setdefault(
            'Heights',
            (['min-height', 'height', 'max-height'], MultipleCascadingSizeWidget))
        extra_inline_styles.setdefault(
            'Text Alignement',
            (('text-align',), SelectTextAlignWidget))
        extra_inline_styles.setdefault(
            'Font Size',
            (('font-size',), MultipleCascadingSizeWidget))
        extra_inline_styles.setdefault(
            'Line Height',
            (('line-height',), NumberInputWidget))
        extra_inline_styles.setdefault(
            'Colors',
            (('color', 'background-color',), ColorPickerWidget))
        extra_inline_styles.setdefault(
            'Overflow',
            (('overflow', 'overflow-x', 'overflow-y',), SelectOverflowWidget))

        if 'cmsplugin_cascade.segmentation' in INSTALLED_APPS:
            config.setdefault('segmentation_mixins', [
                ('cmsplugin_cascade.segmentation.mixins.EmulateUserModelMixin',
                 'cmsplugin_cascade.segmentation.mixins.EmulateUserAdminMixin')])

        config.setdefault(
            'icon_font_root',
            os.path.abspath(os.path.join(self._setting('MEDIA_ROOT'), 'icon_fonts')))

        config.setdefault('plugins_with_extra_render_templates', {})
        config['plugins_with_extra_render_templates'].setdefault(
            'TextLinkPlugin',
            [('cascade/link/text-link.html', ugettext_lazy("default")),
             ('cascade/link/text-link-linebreak.html', ugettext_lazy("with line break")),])
        config['plugins_with_extra_render_templates'].setdefault(
            'LeafletPlugin',
            [('cascade/plugins/leaflet.html', ugettext_lazy("default")),
             ('cascade/plugins/googlemap.html', ugettext_lazy("Google Map")),])

        config.setdefault('allow_plugin_hiding', False)

        config.setdefault('cache_strides', True)

        for module_name in self.CASCADE_PLUGINS:
            try:
                settings_module = import_module('{}.settings'.format(module_name))
                getattr(settings_module, 'set_defaults')(config)
            except (ImportError, AttributeError):
                continue

        self._config_CMSPLUGIN_CASCADE = config
        return config

    @property
    def CSS_PREFIXES(self):
        return {
            'image_set': ['-webkit-image-set', '-moz-image-set', '-o-image-set', '-ms-image-set', 'image-set'],
        }


import sys  # noqa
app_settings = AppSettings()
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings

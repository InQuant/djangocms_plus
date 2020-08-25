from cms.cms_toolbars import ADMIN_MENU_IDENTIFIER
from cms.constants import REFRESH_PAGE
from cms.toolbar.items import LinkItem
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


@toolbar_pool.register
class AdminToolbar(CMSToolbar):
    def populate(self):
        if not self.toolbar.edit_mode_active:
            return

        clipboard_is_bound = self.toolbar.clipboard_plugin
        admin_menu = self.toolbar.get_or_create_menu(ADMIN_MENU_IDENTIFIER, self.current_site.name)
        items = admin_menu.find_items(LinkItem)

        admin_menu.add_modal_item(
            _('Export Clipboard'),
            url=reverse('admin:clipboard-export'),
            position=items[1],
            disabled=not clipboard_is_bound,
            on_close=REFRESH_PAGE,
        )

        admin_menu.add_modal_item(
            _('Import Clipboard'),
            url=reverse('admin:clipboard-import'),
            extra_classes=[],
            position=items[1],
            on_close=REFRESH_PAGE,
        )

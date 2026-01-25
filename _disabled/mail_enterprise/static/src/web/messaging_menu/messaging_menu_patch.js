import { MessagingMenu } from "@mail/core/public_web/messaging_menu";

import { patch } from "@web/core/utils/patch";

// Note: useBackButton from @web_mobile/js/core/hooks is only available in Enterprise
// This patch provides basic functionality without mobile back button support

patch(MessagingMenu.prototype, {
    setup() {
        super.setup();
        // Mobile back button handling removed - requires Enterprise web_mobile module
        // useBackButton(
        //     () => this.dropdown.close(),
        //     () => this.dropdown.isOpen
        // );
    },
});
